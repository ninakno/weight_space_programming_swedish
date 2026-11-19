"""Evaluate candidate arm-C edits on the dev set and log every attempt.

Each candidate is a named function model -> list[Delta]. Results are appended
to logs/edit_iterations.md (the audit trail for how the final edit was found).

Usage: python -m src.try_edit CANDIDATE [CANDIDATE ...] [--split design|check]
"""
import sys
import time

from src.edits.primitives import apply, revert, scale_head
from src.eval_dev import evaluate_dev, load_dev, summarize
from src.load import ROOT, load_model

LOG = ROOT / "logs" / "edit_iterations.md"


def heads_25_3_4(f):
    return lambda m: [scale_head(m, 25, 3, f), scale_head(m, 25, 4, f)]


def head(l, h, f):
    return lambda m: [scale_head(m, l, h, f)]


def combo(*fns):
    return lambda m: [d for fn in fns for d in fn(m)]


CANDIDATES = {
    "none": lambda m: [],
    "h25.3+4_x1.5": heads_25_3_4(1.5),
    "h25.3+4_x2": heads_25_3_4(2.0),
    "h25.3+4_x3": heads_25_3_4(3.0),
    # Second decision point (after "att Y V"): head 13.5 carries the clause signal to V.
    "h13.5_x1.5": head(13, 5, 1.5),
    "h13.5_x2": head(13, 5, 2.0),
    "h13.5_x3": head(13, 5, 3.0),
    "h13.5_x2+h25.3+4_x2": combo(head(13, 5, 2.0), heads_25_3_4(2.0)),
    "h13.5_x3+h25.3+4_x2": combo(head(13, 5, 3.0), heads_25_3_4(2.0)),
    "h13.5_x3+h25.3+4_x3": combo(head(13, 5, 3.0), heads_25_3_4(3.0)),
}


def log_result(name, split, deltas, res):
    s = summarize(res)
    by_clause = res.groupby("clause")["correct"].mean()
    with LOG.open("a") as f:
        f.write(f"\n## {time.strftime('%Y-%m-%d %H:%M')}  `{name}`  (split={split})\n\n")
        for d in deltas:
            f.write(f"- {d.footprint()}\n")
        f.write(f"\nembedded acc={by_clause['embedded']:.3f}  main acc={by_clause['main']:.3f}\n\n")
        f.write("```\n" + s.to_string() + "\n```\n")


def main():
    args = sys.argv[1:]
    split = "design"
    if "--split" in args:
        split = args[args.index("--split") + 1]
        args = [a for a in args if a not in ("--split", split)]
    if not LOG.exists():
        LOG.write_text("# Arm C edit iterations\n\nEvery candidate edit evaluated on the dev set, in order.\n")
    model, tok = load_model()
    dev = load_dev(split)
    for name in args:
        deltas = CANDIDATES[name](model)
        apply(model, deltas)
        res = evaluate_dev(model, tok, dev)
        revert(model, deltas)
        log_result(name, split, deltas, res)
        bc = res.groupby("clause")["correct"].mean()
        bm = res.groupby("clause")["margin"].mean()
        print(f"{name:16s} embedded acc={bc['embedded']:.3f} (margin {bm['embedded']:+.2f})   "
              f"main acc={bc['main']:.3f} (margin {bm['main']:+.2f})", flush=True)


if __name__ == "__main__":
    main()
