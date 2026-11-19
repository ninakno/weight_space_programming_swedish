"""Analyse the final A/B/C test evaluation (results/test_eval/*.csv).

  * target accuracy per arm with bootstrap 95% CI
  * C vs A: exact McNemar test + paired bootstrap CI of the difference
  * C vs B: C's rank within the random-edit seed distribution
  * target breakdowns: adverb seen in dev vs held out; matrix verb class
  * side effects: every phenomenon, A vs C vs mean(B); perplexity

Usage: python -m src.stats   -> prints report, writes results/test_eval/report.md
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from src.devset import SHARED_ADVERBS
from src.load import ROOT, TARGET_PHENOMENON, load_swe_blimp

OUT = ROOT / "results" / "test_eval"
RNG = np.random.default_rng(0)

# Hooper & Thompson (1973)-style coarse split: verbs whose complements resist
# embedded V2 (doubt/deny = class C, factive regret/miss = class D). All other
# matrix verbs in the set are assertive/semi-assertive, where embedded V2 is
# often acceptable in (spoken) Swedish, so the "bad" sentence is less clearly bad.
NON_ASSERTIVE = {"betvivlade", "förnekade", "beklagade", "missade"}


def boot_ci(x, n=10_000):
    x = np.asarray(x, float)
    m = x[RNG.integers(0, len(x), (n, len(x)))].mean(1)
    return np.percentile(m, [2.5, 97.5])


def parse_target():
    d = load_swe_blimp(TARGET_PHENOMENON)
    rows = []
    for g, b in zip(d["sentence_good"], d["sentence_bad"]):
        gw, bw = g.split(), b.split()
        i = 0
        while gw[i] == bw[i]:
            i += 1
        verb = bw[i]
        adv = " ".join(gw[i : gw.index(verb, i)]) if verb in gw[i:] else gw[i]
        rows.append(dict(matrix_verb=gw[1], adverb=adv))
    t = pd.DataFrame(rows)
    t["adverb_group"] = np.where(t["adverb"].isin(SHARED_ADVERBS), "seen in dev", "held out")
    t["verb_class"] = np.where(t["matrix_verb"].isin(NON_ASSERTIVE), "non-assertive", "assertive")
    return t


def main():
    arms = {p.stem: pd.read_csv(p) for p in sorted(OUT.glob("*.csv"))}
    meta = json.loads((OUT / "meta.json").read_text())
    b_names = sorted([a for a in arms if a.startswith("B")], key=lambda s: int(s[1:]))
    tgt = {a: df[df["phenomenon"] == TARGET_PHENOMENON]["correct"].to_numpy() for a, df in arms.items()}
    lines = []
    p = lines.append

    p(f"# Test results: {TARGET_PHENOMENON} (n={len(tgt['A'])})\n")
    p("| Arm | Acc | 95% CI | Perplexity |\n|---|---|---|---|")
    for a in ["A", "C"] + b_names:
        lo, hi = boot_ci(tgt[a])
        p(f"| {a} | {tgt[a].mean():.2f} | [{lo:.2f}, {hi:.2f}] | {meta[a]['ppl']:.3f} |")
    b_acc = np.array([tgt[b].mean() for b in b_names])
    p(f"\nB (random, {len(b_names)} seeds): mean={b_acc.mean():.3f} sd={b_acc.std(ddof=1):.3f} "
      f"min={b_acc.min():.2f} max={b_acc.max():.2f}")

    a, c = tgt["A"].astype(bool), tgt["C"].astype(bool)
    n01, n10 = int((~a & c).sum()), int((a & ~c).sum())
    pval = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    diff = c.astype(float) - a.astype(float)
    lo, hi = boot_ci(diff)
    p(f"\n**C vs A:** {c.mean() - a.mean():+.2f} (paired bootstrap 95% CI [{lo:+.2f}, {hi:+.2f}]); "
      f"fixed {n01}, broke {n10}; exact McNemar p={pval:.4f}")
    rank = (b_acc >= c.mean()).sum()
    p(f"**C vs B:** C={c.mean():.2f}; {rank}/{len(b_names)} random seeds reach >= C "
      f"(empirical p ≈ {(rank + 1) / (len(b_names) + 1):.3f})")

    t = parse_target()
    p("\n## Target breakdown\n")
    for col in ("adverb_group", "verb_class"):
        p(f"| {col} | n | A | C | mean B |\n|---|---|---|---|---|")
        for g, idx in t.groupby(col).groups.items():
            idx = np.array(list(idx))
            p(f"| {g} | {len(idx)} | {tgt['A'][idx].mean():.2f} | {tgt['C'][idx].mean():.2f} | "
              f"{np.mean([tgt[b][idx].mean() for b in b_names]):.2f} |")
        p("")

    p("## All phenomena (side effects)\n")
    p("| Phenomenon | A | C | C−A | mean B |\n|---|---|---|---|---|")
    phen = arms["A"]["phenomenon"].unique()
    for ph in phen:
        acc = {k: v[v["phenomenon"] == ph]["correct"].mean() for k, v in arms.items()}
        mb = np.mean([acc[b] for b in b_names])
        mark = " **(target)**" if ph == TARGET_PHENOMENON else ""
        p(f"| {ph}{mark} | {acc['A']:.2f} | {acc['C']:.2f} | {acc['C'] - acc['A']:+.2f} | {mb:.2f} |")
    ov = {k: v["correct"].mean() for k, v in arms.items()}
    p(f"| **overall (2600)** | {ov['A']:.3f} | {ov['C']:.3f} | {ov['C'] - ov['A']:+.3f} | "
      f"{np.mean([ov[b] for b in b_names]):.3f} |")

    report = "\n".join(lines)
    (OUT / "report.md").write_text(report + "\n")
    print(report)


if __name__ == "__main__":
    main()
