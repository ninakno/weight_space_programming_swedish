"""Arm A: evaluate unedited model(s) on all SwE-BLiMP phenomena.

Only aggregate accuracies are printed/saved, so per-item test errors are not
exposed while the arm-C edit is being designed.

Usage: python -m src.run_baseline [--only-target] [model_name ...]
"""
import json
import sys
import time

import numpy as np

from src.load import DEFAULT_MODEL, ROOT, TARGET_PHENOMENON, load_model, load_swe_blimp
from src.scoring import pair_correct


def bootstrap_ci(correct, n_boot=10_000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(correct, dtype=float)
    means = x[rng.integers(0, len(x), (n_boot, len(x)))].mean(1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def evaluate(model_name: str, only_target: bool = False) -> dict:
    model, tok = load_model(model_name)
    df = load_swe_blimp(TARGET_PHENOMENON if only_target else None)
    t0 = time.time()
    correct = pair_correct(model, tok, df["sentence_good"].tolist(), df["sentence_bad"].tolist())
    df["correct"] = correct
    res = {"model": model_name, "seconds": round(time.time() - t0, 1), "phenomena": {}}
    for ph, g in df.groupby("phenomenon", sort=False):
        lo, hi = bootstrap_ci(g["correct"])
        res["phenomena"][ph] = {"acc": float(g["correct"].mean()), "ci95": [lo, hi], "n": len(g)}
    res["overall_acc"] = float(df["correct"].mean())
    return res


def main():
    args = sys.argv[1:]
    only_target = "--only-target" in args
    names = [a for a in args if not a.startswith("--")] or [DEFAULT_MODEL]
    for name in names:
        res = evaluate(name, only_target)
        suffix = "__target" if only_target else ""
        out = ROOT / "results" / f"baseline__{name.replace('/', '__')}{suffix}.json"
        out.write_text(json.dumps(res, indent=2, ensure_ascii=False))
        t = res["phenomena"][TARGET_PHENOMENON]
        print(f"\n=== {name}  ({res['seconds']}s)  overall={res['overall_acc']:.3f}")
        print(f">>> {TARGET_PHENOMENON}: {t['acc']:.2f}  CI95 [{t['ci95'][0]:.2f}, {t['ci95'][1]:.2f}]")
        for ph, r in res["phenomena"].items():
            print(f"  {ph:28s} {r['acc']:.2f}")


if __name__ == "__main__":
    main()
