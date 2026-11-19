"""Final test evaluation of arms A (baseline), B (random, seeds 0..9), C (LLM edit).

Per-item correctness on all 26 SwE-BLiMP phenomena + Swedish perplexity are
written to results/test_eval/. Analysis is in src/stats.py.

Resumable: arms already in results/test_eval/meta.json (with their CSV) are skipped.

Usage: python -m src.run_eval [--seeds 10]
"""
import hashlib
import json
import sys
import time

import pandas as pd

from src.edits.llm_edit import llm_edit
from src.edits.primitives import apply, revert
from src.edits.random_edit import random_like
from src.load import DEFAULT_MODEL, ROOT, load_model, load_swe_blimp
from src.perplexity import perplexity, windows
from src.scoring import pair_correct

OUT = ROOT / "results" / "test_eval"


def freeze_record():
    src = (ROOT / "src" / "edits" / "llm_edit.py").read_bytes()
    rec = f"llm_edit.py sha256={hashlib.sha256(src).hexdigest()}  model={DEFAULT_MODEL}  frozen={time.strftime('%Y-%m-%d %H:%M')}\n"
    f = OUT / "FROZEN.txt"
    if f.exists():
        prev = f.read_text().split()[1]
        assert prev in rec, f"llm_edit.py changed since freezing! {prev}"
    else:
        f.write_text(rec)
    print(rec.strip())


def main():
    n_seeds = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 10
    OUT.mkdir(parents=True, exist_ok=True)
    freeze_record()
    model, tok = load_model()
    df = load_swe_blimp()
    ppl_batch = windows(tok)
    c_deltas = llm_edit(model)
    arms = [("A", [])] + [("C", c_deltas)] + [(f"B{s}", random_like(model, c_deltas, s)) for s in range(n_seeds)]
    meta_f = OUT / "meta.json"
    meta = json.loads(meta_f.read_text()) if meta_f.exists() else {}
    for name, deltas in arms:
        if name in meta and (OUT / f"{name}.csv").exists():
            print(f"{name:4s} already done, skipping (resume)")
            continue
        t0 = time.time()
        apply(model, deltas)
        correct = pair_correct(model, tok, df["sentence_good"].tolist(), df["sentence_bad"].tolist())
        ppl = perplexity(model, ppl_batch)
        revert(model, deltas)
        pd.DataFrame({"phenomenon": df["phenomenon"], "item": df.groupby("phenomenon").cumcount(),
                      "correct": correct}).to_csv(OUT / f"{name}.csv", index=False)
        tgt = df.assign(c=correct).query("phenomenon == 'EMBEDDED V2 AdvP.'")["c"].mean()
        meta[name] = {"ppl": ppl, "deltas": [d.footprint() for d in deltas]}
        (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
        print(f"{name:4s} target={tgt:.2f} overall={sum(correct)/len(correct):.3f} ppl={ppl:.3f}  ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
