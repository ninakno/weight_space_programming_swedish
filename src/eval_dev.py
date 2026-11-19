"""Evaluate a (possibly edited) model on the synthetic dev set.

Reports, per clause type and adverb group:
  acc     – minimal-pair accuracy (summed sentence log-prob)
  margin  – mean decision-point margin: log P(" ADV" | prefix) - log P(" V" | prefix)
            (positive = prefers adverb next; correct sign is + for embedded,
            - for main clauses)

Usage: python -m src.eval_dev [--split design|check|all]
"""
import sys

import pandas as pd
import torch

from src.load import ROOT, load_model
from src.scoring import _prefix_id, pair_correct

DEV_CSV = ROOT / "data" / "dev" / "dev_pairs.csv"


def load_dev(split: str = "design") -> pd.DataFrame:
    df = pd.read_csv(DEV_CSV, keep_default_na=False)
    return df if split == "all" else df[df["split"] == split].reset_index(drop=True)


@torch.no_grad()
def continuation_logprob(model, tok, prefixes: list[str], conts: list[str]) -> list[float]:
    """log P(cont | prefix), cont scored over all its tokens."""
    start = _prefix_id(tok)
    out = []
    for p, c in zip(prefixes, conts):
        p_ids = [start] + tok(p, add_special_tokens=False)["input_ids"]
        full = [start] + tok(p + c, add_special_tokens=False)["input_ids"]
        assert full[: len(p_ids)] == p_ids, (p, c)
        ids = torch.tensor([full])
        logp = torch.log_softmax(model(input_ids=ids).logits[0, :-1], -1)
        tgt = ids[0, 1:]
        lp = logp.gather(-1, tgt[:, None])[:, 0]
        out.append(lp[len(p_ids) - 1 :].sum().item())
    return out


def evaluate_dev(model, tok, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["correct"] = pair_correct(model, tok, df["sentence_good"].tolist(), df["sentence_bad"].tolist())
    lp_adv = continuation_logprob(model, tok, df["prefix"].tolist(), (" " + df["adverb"]).tolist())
    lp_verb = continuation_logprob(model, tok, df["prefix"].tolist(), (" " + df["verb"]).tolist())
    df["margin"] = [a - v for a, v in zip(lp_adv, lp_verb)]
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["clause", "adverb_group"]).agg(
        n=("correct", "size"), acc=("correct", "mean"), margin=("margin", "mean")
    ).round(3)


def main():
    split = "design"
    if "--split" in sys.argv:
        split = sys.argv[sys.argv.index("--split") + 1]
    model, tok = load_model()
    res = evaluate_dev(model, tok, load_dev(split))
    print(summarize(res))
    print(res.groupby("clause")["correct"].mean().round(3).to_string())


if __name__ == "__main__":
    main()
