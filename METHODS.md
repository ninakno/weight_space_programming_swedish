# Methods

Does an LLM-authored weight edit ("weight space programming") improve a small
Swedish LM on embedded-clause adverb–verb order, without any training?

## Task and data

- **Test set:** SwE-BLiMP (Sjons, Heinat & Kurfalı, LREC 2026),
  `data/swe_blimp/swe_blimp_v1.csv`, commit in `data/swe_blimp/SOURCE_COMMIT`.
  Target phenomenon `EMBEDDED V2 AdvP.` (100 minimal pairs), e.g.
  `Rune påstod att Iris ofta minns parfymen på våren` (good) vs
  `Rune påstod att Iris minns ofta parfymen på våren` (bad).
  The other 25 phenomena (2,500 pairs) are side-effect controls.
- **Model:** `jekunz/smollm-135m-cpt-fineweb-swedish` (SmolLM2-135M-Instruct with
  continued pretraining on Swedish FineWeb-2). Chosen because it already knows
  Swedish (target baseline 0.85) and runs quickly on CPU. Rejected candidates and
  their baselines are in `results/baseline__*.json`: English and multilingual
  ≤0.6B models scored 0.40–0.55 on the target.
- **Constraints:** no gradient training, CPU only (16 GB RAM), no API keys or
  gated models.

## Scoring (all arms)

There is no prompting and no chat template. Each sentence is scored as
Σ log P(token) after a single start token (`<|im_start|>`). A pair is correct if
the good sentence scores higher (`src/scoring.py`). Accuracy CIs use a
10,000-sample bootstrap.

## Arms

| Arm | Weights |
|---|---|
| A | model as downloaded |
| B | A + random edit matched to C's footprint, seeds 0–9 (`src/edits/random_edit.py`) |
| C | A + LLM-authored edit, frozen before testing (`src/edits/llm_edit.py`) |

**Matching in B:** each of C's deltas (a scaled attention head = 64 `o_proj`
columns) is replaced by Gaussian noise on the columns of a randomly chosen head
in the **same layer**, rescaled to the **same Frobenius norm**.

## How arm C was authored

The edit was written by an LLM (Claude Code, Claude Opus 5.5) working
interactively in a terminal session with the experimenter. The LLM wrote and ran
the analysis code itself and chose the edit from the numbers.

### Information available to the author

- **Synthetic dev set** (`src/devset.py` → `data/dev/dev_pairs.csv`, 600 pairs):
  - 300 embedded-clause pairs (`X MV att Y ADV V O PP` vs `… Y V ADV O PP`).
  - 300 main-clause pairs (`Y V ADV O PP` vs `Y ADV V O PP`). These are a
    counter-constraint: they penalise a blanket "adverb before verb" edit.
  - Names, matrix verbs and embedded verbs are disjoint from the test set; the
    script asserts this.
  - 10 of the 20 test adverbs are used; 10 are held out. 8 adverbs that are not
    in the test set are added.
  - Random split into `design` (iterated on freely) and `check` (used twice:
    baseline and final candidate).
- **Diagnostics on dev items only** (`src/diagnostics.py`):
  - Activation patching between `X MV att Y` (clean) and `X MV: Y` (corrupt;
    direct speech = main clause), a one-token minimal pair.
  - What was patched: residual stream per layer × token role, attention/MLP
    output per layer, and each attention head.
  - Metric at two decision points: (1) after `att Y`: log P(ADV) − log P(V);
    (2) after `att Y V`: log P(ADV) − log P(OBJ).
  - Logit lens.
- **Swedish Wikipedia perplexity** (`src/perplexity.py`, 5 articles, 40 × 256
  tokens) as a general-ability guard.

### Exposure to the test set before freezing

- **Vocabulary only:** names, matrix verbs, embedded verbs and adverbs were
  extracted to make the dev set disjoint from the test set and to define the
  held-out adverb list.
- **About 15 randomly sampled test pairs** were shown during initial planning,
  before any diagnostics.
- **Aggregate arm-A accuracies** per phenomenon. No per-item errors or
  per-item scores for the target phenomenon were inspected before freezing.

### Allowed edit primitives (`src/edits/primitives.py`)

- Scale an attention head's output (its `o_proj` columns).
- Scale MLP neurons (`down_proj` columns).
- Rank-1 additive update `W += α u vᵀ`.

Only head scaling was used in the end.

### Authoring trajectory (full log: `logs/edit_iterations.md`)

1. Patching at decision 1 located heads **25.3 and 25.4**. They attend from the
   embedded subject to `att` (56% / 81% of their attention, vs 21% / 44% to `:`)
   and restore 25% + 19% of the clean–corrupt margin gap.
2. Scaling them ×1.5 / ×2 / ×3 raised the decision-1 margin but barely raised
   dev embedded accuracy (0.916 → 0.929).
3. Per-word error analysis on design-split errors: 9 of 13 errors had the correct
   decision-1 preference. They failed after the verb: the model predicted
   `V ADV`, which is main-clause order.
4. Patching at decision 2 located head **13.5**. It carries the `att` signal to
   the verb position around layers 12–14 and restores 53% of that gap.
5. Swept head 13.5 (×1.5 / ×2 / ×3) and combinations with heads 25.3/25.4.
6. **Selection rule:** the mildest edit reaching the maximum dev-design embedded
   accuracy, with perplexity as a tie-breaker. This rule was set by the author
   after seeing the sweep, not pre-registered.
7. **Chosen edit:** heads 13.5, 25.3 and 25.4 scaled ×2.

| Dev results | A | C |
|---|---|---|
| design, embedded acc | 0.916 | 0.974 |
| design, main acc | 0.771 | 0.800 |
| check, embedded acc | 0.918 | 0.966 |
| check, main acc | 0.744 | 0.806 |
| perplexity | 6.356 | 6.411 |

In total, 10 candidate edits (plus the unedited baseline) were evaluated on the
design split.

### Freezing

`src/edits/llm_edit.py` was hashed (sha256 in `results/test_eval/FROZEN.txt`)
before the first test-set evaluation of any edited model. `src/run_eval.py`
asserts the hash on every run.

## Test-time analysis (`src/stats.py`)

- **C vs A:** exact McNemar test on discordant pairs, plus a paired-bootstrap
  CI of the accuracy difference.
- **C vs B:** C's rank among the 10 random seeds (empirical p = (k+1)/11).
- **Target breakdowns:**
  - Adverbs seen in dev (75 pairs) vs held out (25 pairs).
  - Matrix verb class, a coarse Hooper & Thompson split. Only 4 non-assertive
    pairs, so this breakdown is indicative only.
- **Side effects:** all 26 phenomena and perplexity.

## Caveats

- n = 100: only gains of roughly 10 points or more are clearly detectable.
- **Label noise:** embedded V2 is often acceptable after assertive bridge
  verbs, which make up 96 of the 100 target pairs, so some "bad" sentences are
  not clearly ungrammatical.
- **Imperfect controls:** some SwE-BLiMP control phenomena (e.g. `V3`) contrast
  different adverbs rather than reorder the same words, so they are not clean
  opposite-order controls.
- **Reproducibility:** authoring was interactive. The process cannot be re-run
  bit-for-bit; it is documented by the iteration log, the diagnostics and the
  protocol below.

## Reusable authoring protocol

To repeat arm C with another LLM or model, give the author the following
instructions:

> You are editing the weights of a causal LM so that it prefers correct
> adverb–verb order in Swedish *att*-clauses (`att Y ADV V`), without hurting
> main clauses (`Y V ADV`) or general Swedish ability. You may not train.
> You may run any forward-pass analysis, such as activation patching, attention
> inspection or the logit lens, on the provided synthetic dev set (`design`
> split). You must not access the SwE-BLiMP test pairs. Allowed edits: scaling
> attention heads, scaling MLP neurons, rank-1 additive updates. Report each
> candidate's dev embedded accuracy, main-clause accuracy and Swedish
> perplexity. Pick the mildest edit that reaches the best embedded accuracy,
> confirm it on the `check` split, then deliver it as a function
> `edit(model) -> list[Delta]` and freeze it.
