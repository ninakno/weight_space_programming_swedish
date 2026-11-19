"""Arm C — FROZEN edit, authored by the LLM (Claude Code) on the synthetic dev set.

Derivation (see logs/edit_iterations.md and results/diagnostics*.json):
  * Activation patching ("X MV att Y" vs "X MV: Y") showed that the
    subordinate-clause signal lives on the `att` token and is copied forward by
    a few attention heads:
      - head 13.5  -> to the embedded *verb*   (restores 53% of the margin gap
                      at decision 2: ADV vs OBJ after "att Y V")
      - heads 25.3, 25.4 -> to the embedded *subject* (restore 25% + 19% at
                      decision 1: ADV vs V after "att Y")
  * Edit: double the output (o_proj columns) of these three heads.
  * Chosen as the mildest setting reaching max dev-design embedded accuracy
    (0.916 -> 0.974); check split 0.918 -> 0.966; main clauses 0.771 -> 0.800;
    Swedish Wikipedia perplexity 6.356 -> 6.411.

Do not modify after freezing: its sha256 is recorded in results/test_eval/FROZEN.txt.
"""
from src.edits.primitives import Delta, scale_head

HEADS = [(13, 5), (25, 3), (25, 4)]
FACTOR = 2.0


def llm_edit(model) -> list[Delta]:
    return [scale_head(model, layer, head, FACTOR) for layer, head in HEADS]
