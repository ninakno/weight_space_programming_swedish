"""Locate where the model encodes "inside an att-clause" (no training).

Contrast (one-token minimal pair, positions align):
  clean    : "X MV att Y"   -> model prefers ADV next (correct for embedded)
  corrupt  : "X MV: Y"      -> direct speech = main clause, ADV preference lower
Metric: margin = log P(" ADV" | prefix) - log P(" V" | prefix)  (whole words).

Activation patching: run the corrupt prefix, overwrite one component's output
with its value from the clean run, and measure how much of the clean-corrupt
margin gap is restored:  restored = (m_patched - m_corrupt) / (m_clean - m_corrupt).

Analyses:
  resid  – residual stream after each layer, patched per token role
           (X, MV, COMP = att/:, Y = embedded subject)
  comp   – attention output / MLP output per layer at the last prefix position
  heads  – each attention head (slice of o_proj input) at the last position
  lens   – logit lens margin per layer at the last position, clean vs corrupt

Decision 2 (--decision 2): prefix extended with the embedded verb; metric is
log P(" ADV") - log P(" OBJ") after "... att Y V" (should be low/negative in
the att-clause, higher after a colon).

Usage: python -m src.diagnostics [--n 40] [--only resid,comp,heads,lens] [--head-from LAYER] [--decision 1|2]
Writes results/diagnostics.json.
"""
import json
import sys
from contextlib import contextmanager

import numpy as np
import torch

from src.eval_dev import load_dev
from src.load import ROOT, load_model
from src.scoring import _prefix_id

ROLES = ["X", "MV", "COMP", "Y", "V"]


def build_items(tok, n: int, decision: int = 1):
    d = load_dev("design")
    d = d[d["clause"] == "embedded"].head(n)
    start = _prefix_id(tok)
    items = []
    for _, r in d.iterrows():
        x, y = r["prefix"].split(" att ")
        name_x, mv = x.split(" ", 1)
        # Tokenise role by role so spans are exact.
        parts_clean = [(f"{name_x}", "X"), (f" {mv}", "MV"), (" att", "COMP"), (f" {y}", "Y")]
        parts_corr = [(f"{name_x}", "X"), (f" {mv}", "MV"), (":", "COMP"), (f" {y}", "Y")]
        ids_c, ids_k, roles = [start], [start], ["BOS"]
        for (pc, role), (pk, _) in zip(parts_clean, parts_corr):
            tc = tok(pc, add_special_tokens=False)["input_ids"]
            tk = tok(pk, add_special_tokens=False)["input_ids"]
            if len(tc) != len(tk):
                break
            ids_c += tc
            ids_k += tk
            roles += [role] * len(tc)
        else:
            adv = tok(" " + r["adverb"], add_special_tokens=False)["input_ids"]
            verb = tok(" " + r["verb"], add_special_tokens=False)["input_ids"]
            if decision == 2:
                # Second decision point: after "... att Y V", is ADV or OBJ next?
                # (embedded: OBJ correct; main clause/colon: ADV fine.)
                obj = r["sentence_good"].split(r["verb"] + " ", 1)[1].split()[0]
                ids_c, ids_k, roles = ids_c + verb, ids_k + verb, roles + ["V"] * len(verb)
                verb = tok(" " + obj, add_special_tokens=False)["input_ids"]
            items.append(dict(clean=ids_c, corrupt=ids_k, roles=roles, adv=adv, verb=verb))
    return items


def cont_logprob(model, prefix_ids, cont_ids) -> float:
    ids = torch.tensor([prefix_ids + cont_ids])
    logp = torch.log_softmax(model(input_ids=ids).logits[0, :-1], -1)
    tgt = ids[0, 1:]
    lp = logp.gather(-1, tgt[:, None])[:, 0]
    return lp[len(prefix_ids) - 1 :].sum().item()


def margin(model, prefix_ids, item) -> float:
    return cont_logprob(model, prefix_ids, item["adv"]) - cont_logprob(model, prefix_ids, item["verb"])


# ---------- hooks ----------

def _replace(out, positions, value):
    t = out[0] if isinstance(out, tuple) else out
    t = t.clone()
    t[0, positions] = value[positions]
    return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t


@contextmanager
def capture(modules: dict):
    """Record outputs (first element if tuple) of named modules, batch index 0."""
    store, handles = {}, []
    for name, mod in modules.items():
        def hook(m, inp, out, name=name):
            store[name] = (out[0] if isinstance(out, tuple) else out)[0].detach().clone()
        handles.append(mod.register_forward_hook(hook))
    try:
        yield store
    finally:
        for h in handles:
            h.remove()


@contextmanager
def patch_output(module, positions, value):
    h = module.register_forward_hook(lambda m, i, o: _replace(o, positions, value))
    try:
        yield
    finally:
        h.remove()


@contextmanager
def patch_head(o_proj, head, head_dim, position, value):
    """value: o_proj input from the clean run, shape [T, hidden]."""
    sl = slice(head * head_dim, (head + 1) * head_dim)

    def pre(m, args):
        x = args[0].clone()
        x[0, position, sl] = value[position, sl]
        return (x,) + args[1:]

    h = o_proj.register_forward_pre_hook(pre)
    try:
        yield
    finally:
        h.remove()


@contextmanager
def capture_o_proj_inputs(layers):
    store, handles = {}, []
    for i, layer in enumerate(layers):
        def pre(m, args, i=i):
            store[i] = args[0][0].detach().clone()
        handles.append(layer.self_attn.o_proj.register_forward_pre_hook(pre))
    try:
        yield store
    finally:
        for h in handles:
            h.remove()


# ---------- analyses ----------

@torch.no_grad()
def run(n: int, only: set[str], head_from: int = 0, decision: int = 1):
    model, tok = load_model()
    layers = model.model.layers
    L = len(layers)
    head_dim = model.config.hidden_size // model.config.num_attention_heads
    H = model.config.num_attention_heads
    items = build_items(tok, n, decision)
    print(f"{len(items)} items with aligned tokenisation")

    m_clean = np.array([margin(model, it["clean"], it) for it in items])
    m_corr = np.array([margin(model, it["corrupt"], it) for it in items])
    gap = m_clean - m_corr
    print(f"margin clean={m_clean.mean():+.2f} corrupt={m_corr.mean():+.2f} gap={gap.mean():+.2f}")
    res = {"n": len(items), "margin_clean": m_clean.mean(), "margin_corrupt": m_corr.mean()}

    # Cache clean activations (prefix only; causal so continuation does not matter).
    caches = []
    mods = {f"resid{l}": layers[l] for l in range(L)}
    mods |= {f"attn{l}": layers[l].self_attn for l in range(L)}
    mods |= {f"mlp{l}": layers[l].mlp for l in range(L)}
    for it in items:
        with capture(mods) as st, capture_o_proj_inputs(layers) as oin:
            model(input_ids=torch.tensor([it["clean"]]))
        caches.append((dict(st), dict(oin)))

    def restored(patched):
        return float(np.mean((np.array(patched) - m_corr) / gap))

    if "resid" in only:
        tab = {}
        for l in range(L):
            for role in ROLES:
                if role not in items[0]["roles"]:
                    continue
                vals = []
                for it, (st, _) in zip(items, caches):
                    pos = [i for i, r in enumerate(it["roles"]) if r == role]
                    with patch_output(layers[l], pos, st[f"resid{l}"]):
                        vals.append(margin(model, it["corrupt"], it))
                tab[f"{l}:{role}"] = restored(vals)
            print("resid L%-2d " % l + "  ".join(f"{r}={tab[f'{l}:{r}']:+.2f}" for r in ROLES if f"{l}:{r}" in tab), flush=True)
        res["resid"] = tab

    if "comp" in only:
        tab = {}
        for l in range(L):
            for kind, mod in (("attn", layers[l].self_attn), ("mlp", layers[l].mlp)):
                vals = []
                for it, (st, _) in zip(items, caches):
                    last = [len(it["corrupt"]) - 1]
                    with patch_output(mod, last, st[f"{kind}{l}"]):
                        vals.append(margin(model, it["corrupt"], it))
                tab[f"{l}:{kind}"] = restored(vals)
            print(f"comp  L{l:<2d} attn={tab[f'{l}:attn']:+.3f}  mlp={tab[f'{l}:mlp']:+.3f}", flush=True)
        res["comp"] = tab

    if "heads" in only:
        tab = {}
        for l in range(head_from, L):
            for h in range(H):
                vals = []
                for it, (_, oin) in zip(items, caches):
                    last = len(it["corrupt"]) - 1
                    with patch_head(layers[l].self_attn.o_proj, h, head_dim, last, oin[l]):
                        vals.append(margin(model, it["corrupt"], it))
                tab[f"{l}.{h}"] = restored(vals)
            print(f"heads L{l:<2d} " + " ".join(f"{tab[f'{l}.{h}']:+.2f}" for h in range(H)), flush=True)
        res["heads"] = tab

    if "lens" in only:
        # Logit lens on the first token of ADV vs VERB at the last prefix position.
        tab = {"clean": [], "corrupt": []}
        W = model.lm_head.weight
        for kind in ("clean", "corrupt"):
            per_layer = np.zeros(L)
            for it in items:
                with capture({f"r{l}": layers[l] for l in range(L)}) as st:
                    model(input_ids=torch.tensor([it[kind]]))
                for l in range(L):
                    h = model.model.norm(st[f"r{l}"][-1])
                    lg = W @ h
                    per_layer[l] += (lg[it["adv"][0]] - lg[it["verb"][0]]).item()
            tab[kind] = (per_layer / len(items)).tolist()
        for l in range(L):
            print(f"lens  L{l:<2d} clean={tab['clean'][l]:+.2f} corrupt={tab['corrupt'][l]:+.2f}")
        res["lens"] = tab

    out = ROOT / "results" / ("diagnostics.json" if decision == 1 else f"diagnostics_d{decision}.json")
    old = json.loads(out.read_text()) if out.exists() else {}
    out.write_text(json.dumps(old | res, indent=1))
    print(f"wrote {out}")


def main():
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 40
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else {"resid", "comp", "heads", "lens"}
    head_from = int(sys.argv[sys.argv.index("--head-from") + 1]) if "--head-from" in sys.argv else 0
    decision = int(sys.argv[sys.argv.index("--decision") + 1]) if "--decision" in sys.argv else 1
    run(n, only, head_from, decision)


if __name__ == "__main__":
    main()
