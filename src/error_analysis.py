"""POST-HOC, EXPLORATORY: inspect target-test errors of arms A and C.

Run only after arm C was frozen and evaluated. For every target pair that A or
C gets wrong, print the per-word log-prob of good vs bad sentence under A and C
and the two decision-point margins:
  d1 = log P(ADV | ..att Y) - log P(V | ..att Y)        (want > 0)
  d2 = log P(OBJ-word | ..att Y V) - log P(ADV | ..att Y V)  (want > 0)

Usage: python -m src.error_analysis  -> results/test_eval/error_analysis.md
"""
import pandas as pd
import torch

from src.edits.llm_edit import llm_edit
from src.edits.primitives import apply, revert
from src.load import ROOT, TARGET_PHENOMENON, load_model, load_swe_blimp
from src.scoring import _prefix_id
from src.stats import parse_target

OUT = ROOT / "results" / "test_eval"


@torch.no_grad()
def word_logprobs(model, tok, sentence):
    ids, spans = [_prefix_id(tok)], []
    for i, w in enumerate(sentence.split()):
        x = tok((" " if i else "") + w, add_special_tokens=False)["input_ids"]
        spans.append((w, len(ids), len(ids) + len(x)))
        ids += x
    lp = torch.log_softmax(model(input_ids=torch.tensor([ids])).logits[0, :-1], -1)
    lp = lp.gather(-1, torch.tensor(ids[1:])[:, None])[:, 0]
    return [(w, lp[a - 1 : b - 1].sum().item()) for w, a, b in spans]


def analyse(model, tok, good, bad):
    g, b = word_logprobs(model, tok, good), word_logprobs(model, tok, bad)
    gw, bw = good.split(), bad.split()
    i = 0
    while gw[i] == bw[i]:
        i += 1
    # good: ... ADV(+) V ;  bad: ... V ADV(+)
    verb = bw[i]
    j = gw.index(verb, i)              # verb position in good
    n_adv = j - i
    d1 = sum(v for _, v in g[i:j]) - b[i][1]                # P(ADV..) vs P(V) after subject
    d2 = 0.0
    # after "att Y V": good continues with the word after the verb, bad with ADV
    obj_good = g[j + 1][1] if j + 1 < len(g) else 0.0
    d2 = obj_good - sum(v for _, v in b[i + 1 : i + 1 + n_adv])
    return dict(total=sum(v for _, v in g) - sum(v for _, v in b), d1=d1, d2=d2, g=g, b=b)


def fmt(ws):
    return " ".join(f"{w}({v:.1f})" for w, v in ws)


def main():
    model, tok = load_model()
    d = load_swe_blimp(TARGET_PHENOMENON)
    t = parse_target()
    A = pd.read_csv(OUT / "A.csv").query("phenomenon == @TARGET_PHENOMENON")["correct"].to_numpy()
    C = pd.read_csv(OUT / "C.csv").query("phenomenon == @TARGET_PHENOMENON")["correct"].to_numpy()
    idx = [k for k in range(len(d)) if not (A[k] and C[k])]
    deltas = llm_edit(model)
    rows, lines = [], ["# Post-hoc error analysis (exploratory)\n",
                       "Target pairs wrong under A and/or C. Margins in log-prob units, positive = prefers good.",
                       "d1 = ADV vs V right after the embedded subject; d2 = next word vs ADV right after the verb.\n"]
    for k in idx:
        good, bad = d.loc[k, "sentence_good"], d.loc[k, "sentence_bad"]
        ra = analyse(model, tok, good, bad)
        apply(model, deltas)
        rc = analyse(model, tok, good, bad)
        revert(model, deltas)
        status = {(False, True): "FIXED by C", (False, False): "wrong in both", (True, False): "BROKEN by C"}[(bool(A[k]), bool(C[k]))]
        rows.append(dict(item=k, status=status, matrix_verb=t.loc[k, "matrix_verb"], adverb=t.loc[k, "adverb"],
                         adverb_group=t.loc[k, "adverb_group"], A_total=ra["total"], C_total=rc["total"],
                         A_d1=ra["d1"], C_d1=rc["d1"], A_d2=ra["d2"], C_d2=rc["d2"]))
        lines += [f"## item {k} — {status}  (matrix verb: {t.loc[k, 'matrix_verb']}, adverb: {t.loc[k, 'adverb']}, {t.loc[k, 'adverb_group']})",
                  f"- A: total {ra['total']:+.2f}  d1 {ra['d1']:+.2f}  d2 {ra['d2']:+.2f}",
                  f"- C: total {rc['total']:+.2f}  d1 {rc['d1']:+.2f}  d2 {rc['d2']:+.2f}",
                  f"- good (A): {fmt(ra['g'])}", f"- bad  (A): {fmt(ra['b'])}", ""]
    df = pd.DataFrame(rows)
    summary = df.round(2).to_string(index=False)
    lines.insert(3, "```\n" + summary + "\n```\n")
    (OUT / "error_analysis.md").write_text("\n".join(lines))
    print(summary)


if __name__ == "__main__":
    main()
