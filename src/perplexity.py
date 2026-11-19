"""General-ability guard: perplexity on Swedish Wikipedia text (data/ppl/*.txt).

Non-overlapping 256-token windows, first N windows per article.

Usage: python -m src.perplexity [CANDIDATE ...]     (candidates from src.try_edit)
"""
import math
import sys

import torch

from src.edits.primitives import apply, revert
from src.load import ROOT, load_model

WINDOW = 256
MAX_WINDOWS_PER_DOC = 8


def windows(tok):
    out = []
    for f in sorted((ROOT / "data" / "ppl").glob("*.txt")):
        ids = tok(f.read_text(), add_special_tokens=False)["input_ids"]
        for i in range(0, min(len(ids), WINDOW * MAX_WINDOWS_PER_DOC) - WINDOW + 1, WINDOW):
            out.append(ids[i : i + WINDOW])
    return torch.tensor(out)


@torch.no_grad()
def perplexity(model, batch: torch.Tensor, bs: int = 8) -> float:
    nll, n = 0.0, 0
    for i in range(0, len(batch), bs):
        x = batch[i : i + bs]
        logp = torch.log_softmax(model(input_ids=x).logits[:, :-1], -1)
        nll -= logp.gather(-1, x[:, 1:, None]).sum().item()
        n += x[:, 1:].numel()
    return math.exp(nll / n)


def main():
    from src.try_edit import CANDIDATES
    model, tok = load_model()
    batch = windows(tok)
    print(f"{len(batch)} windows x {WINDOW} tokens")
    for name in sys.argv[1:] or ["none"]:
        deltas = CANDIDATES[name](model)
        apply(model, deltas)
        print(f"{name:24s} ppl={perplexity(model, batch):.3f}", flush=True)
        revert(model, deltas)


if __name__ == "__main__":
    main()
