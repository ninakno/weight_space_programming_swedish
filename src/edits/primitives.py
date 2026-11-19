"""Weight-edit primitives.

An edit is a list of `Delta`s. Each Delta adds a tensor to one parameter and
records its *kind* and support, so that arm B can build a random edit with the
same footprint (same parameter, same kind, same number of rows/cols touched,
same Frobenius norm) but random indices/directions.

Kinds:
  "cols"  – delta confined to a set of input columns of W   (e.g. one attention
            head = 64 columns of o_proj; one MLP neuron = 1 column of down_proj)
  "rows"  – delta confined to a set of output rows of W     (e.g. one neuron in
            up/gate_proj)
  "rank1" – dense delta  u vᵀ
"""
from dataclasses import dataclass, field

import torch


@dataclass
class Delta:
    param: str                    # e.g. "model.layers.25.self_attn.o_proj.weight"
    kind: str                     # "cols" | "rows" | "rank1"
    tensor: torch.Tensor          # same shape as the parameter
    index: list[int] = field(default_factory=list)  # touched rows/cols (cols/rows kinds)
    note: str = ""

    @property
    def norm(self) -> float:
        return self.tensor.norm().item()

    def footprint(self) -> dict:
        return dict(param=self.param, kind=self.kind, n_index=len(self.index),
                    norm=round(self.norm, 6), note=self.note)


def _param(model, name: str) -> torch.Tensor:
    return dict(model.named_parameters())[name]


def head_cols(model, head: int) -> list[int]:
    hd = model.config.hidden_size // model.config.num_attention_heads
    return list(range(head * hd, (head + 1) * hd))


def scale_head(model, layer: int, head: int, factor: float) -> Delta:
    """Multiply one attention head's contribution to the residual by `factor`."""
    name = f"model.layers.{layer}.self_attn.o_proj.weight"
    W = _param(model, name).detach()
    cols = head_cols(model, head)
    d = torch.zeros_like(W)
    d[:, cols] = (factor - 1.0) * W[:, cols]
    return Delta(name, "cols", d, cols, f"scale head {layer}.{head} x{factor}")


def scale_neurons(model, layer: int, neurons: list[int], factor: float) -> Delta:
    """Multiply MLP neurons' output (columns of down_proj) by `factor`."""
    name = f"model.layers.{layer}.mlp.down_proj.weight"
    W = _param(model, name).detach()
    d = torch.zeros_like(W)
    d[:, neurons] = (factor - 1.0) * W[:, neurons]
    return Delta(name, "cols", d, list(neurons), f"scale neurons L{layer} {neurons} x{factor}")


def rank1(model, param: str, u: torch.Tensor, v: torch.Tensor, alpha: float, note: str = "") -> Delta:
    """W += alpha * u vᵀ   (u: out_features, v: in_features)."""
    W = _param(model, param).detach()
    d = alpha * torch.outer(u.to(W.dtype), v.to(W.dtype))
    assert d.shape == W.shape
    return Delta(param, "rank1", d, [], note)


@torch.no_grad()
def apply(model, deltas: list[Delta], sign: float = 1.0):
    params = dict(model.named_parameters())
    for d in deltas:
        params[d.param].add_(sign * d.tensor)
    return model


def revert(model, deltas: list[Delta]):
    return apply(model, deltas, sign=-1.0)
