"""Arm B: random edit with the same footprint as a given edit.

For every Delta of the reference edit:
  cols/rows – pick the same number of columns/rows of the *same parameter* at
              random (for a whole attention head: a random head of the same
              layer), fill with Gaussian noise, rescale to the same Frobenius norm.
  rank1     – random unit vectors u, v; same Frobenius norm.
"""
import torch

from src.edits.primitives import Delta, head_cols


def random_like(model, ref: list[Delta], seed: int) -> list[Delta]:
    g = torch.Generator().manual_seed(seed)
    params = dict(model.named_parameters())
    H = model.config.num_attention_heads
    out = []
    for d in ref:
        W = params[d.param]
        t = torch.zeros_like(W)
        if d.kind in ("cols", "rows"):
            axis = 1 if d.kind == "cols" else 0
            size = W.shape[axis]
            is_head = d.kind == "cols" and d.param.endswith("o_proj.weight") and d.index == head_cols(model, d.index[0] // (size // H))
            if is_head:
                idx = head_cols(model, int(torch.randint(H, (1,), generator=g)))
            else:
                idx = torch.randperm(size, generator=g)[: len(d.index)].tolist()
            noise = torch.randn(W.shape[0] if axis == 1 else len(idx),
                                len(idx) if axis == 1 else W.shape[1], generator=g)
            noise *= d.norm / noise.norm()
            if axis == 1:
                t[:, idx] = noise
            else:
                t[idx, :] = noise
        elif d.kind == "rank1":
            u = torch.randn(W.shape[0], generator=g)
            v = torch.randn(W.shape[1], generator=g)
            t = torch.outer(u / u.norm(), v / v.norm()) * d.norm
            idx = []
        else:
            raise ValueError(d.kind)
        out.append(Delta(d.param, d.kind, t, idx, f"random(seed={seed}) matching: {d.note}"))
    return out
