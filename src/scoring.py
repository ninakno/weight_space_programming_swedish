"""Sentence log-probabilities and minimal-pair accuracy."""
import torch


def _prefix_id(tok) -> int:
    # Condition the first word on a start token so every token of the sentence is scored.
    for t in (tok.bos_token_id, tok.eos_token_id):
        if t is not None:
            return t
    raise ValueError("tokenizer has neither BOS nor EOS token")


@torch.no_grad()
def sentence_logprobs(model, tok, sentences: list[str], batch_size: int = 32) -> list[float]:
    """Summed log P(sentence) under the model, conditioned on a start token."""
    start = _prefix_id(tok)
    out: list[float] = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i : i + batch_size]
        ids = [[start] + tok(s, add_special_tokens=False)["input_ids"] for s in batch]
        L = max(len(x) for x in ids)
        pad = tok.pad_token_id if tok.pad_token_id is not None else start
        input_ids = torch.full((len(ids), L), pad, dtype=torch.long)
        attn = torch.zeros((len(ids), L), dtype=torch.long)
        for j, x in enumerate(ids):
            input_ids[j, : len(x)] = torch.tensor(x)
            attn[j, : len(x)] = 1
        logits = model(input_ids=input_ids, attention_mask=attn).logits
        logp = torch.log_softmax(logits[:, :-1].float(), dim=-1)
        tgt = input_ids[:, 1:]
        tok_lp = logp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1) * attn[:, 1:]
        out.extend(tok_lp.sum(-1).tolist())
    return out


def pair_correct(model, tok, good: list[str], bad: list[str], batch_size: int = 32) -> list[bool]:
    lp_good = sentence_logprobs(model, tok, good, batch_size)
    lp_bad = sentence_logprobs(model, tok, bad, batch_size)
    return [g > b for g, b in zip(lp_good, lp_bad)]
