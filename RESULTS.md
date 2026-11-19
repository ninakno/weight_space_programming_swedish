# Results (small exploratory experiment, 2026-11-19)

Model `jekunz/smollm-135m-cpt-fineweb-swedish`; arms and procedure in `METHODS.md`.
Full tables: `results/test_eval/report.md`; post-hoc error analysis:
`results/test_eval/error_analysis.md`.

## Main result: `EMBEDDED V2 AdvP.` (n = 100)

| Arm | Acc | 95% CI | Perplexity |
|---|---|---|---|
| A: baseline | 0.85 | [0.78, 0.92] | 6.356 |
| C: LLM edit (heads 13.5, 25.3, 25.4 scaled ×2) | **0.88** | [0.81, 0.94] | 6.411 |
| B: random matched edits, 10 seeds | mean 0.836 (0.80–0.85) | | 6.38–6.45 |

- **C vs A:** +3 points. C fixed 3 pairs and broke 0. Exact McNemar p = 0.25;
  paired bootstrap CI [+0.00, +0.07]. **Not significant.**
- **C vs B:** C is above all 10 random seeds (empirical p ≈ 0.09, the
  smallest value 10 seeds allow).
- **Held-out vs seen adverbs:** the gain is similar (+4 vs +3 points), which
  fits a mechanism keyed to `att` rather than to particular adverbs.
- **Dev-set effect was much larger:** check split 0.918 → 0.966.
- **Side effects:**
  - Other subordinate-clause phenomena improve: `V2 REL. CL.` +0.06,
    `EMBEDDED V3 OBJ.` +0.07.
  - Some main-clause V3 phenomena drop: `V3 CL.` −0.04, `V3 OBJ.` −0.06.
  - Overall accuracy is unchanged (0.772 → 0.775).

**Conclusion:** the authored edit targets an interpretable circuit (heads that
copy the complementizer signal to the subject and the verb). It moves the model
in the intended direction on the test set and on related subordinate-clause
phenomena, and it beats matched random edits. But the effect on the 100 target
pairs is too small to establish with this sample size.

## Post-hoc error analysis (exploratory, after freezing)

The analysis covers the 15 target pairs wrong under A and/or C.

1. **C helps almost everywhere, but not enough to flip most pairs.**
   - The good−bad score difference rises in 13 of 15 pairs, is flat in 1 and
     falls in 1.
   - Four pairs that are still wrong end up close to zero (−0.01, −0.15,
     −0.35, −0.43).
   - The others are 1–5 log-prob units short.
   - On this test set the edit adds a fairly uniform, modest push. On the dev
     set the same push was enough to flip most errors, because dev errors were
     close to zero.
2. **Rare adverbs:** *vanligtvis, vanligen, stundom, oftast, hädanefter*
   (mostly held out from dev) are very unlikely right after the subject
   (−13 to −17), regardless of clause type. Sentence-initial adverb rarity, not
   clause-type knowledge, dominates these pairs. The decision-1 margin there is
   −3 to −8, far beyond what the edit shifts.
3. **Odd semantics in test items:** examples include *hör spiken*,
   *förstör klubban på morgondagen* and *påbörjar tankegången under kriget*.
   In several pairs, the words *after* the reordered region (object, time PP)
   differ by 2–4 units between the two orders. That is noise unrelated to the
   word-order rule.
4. **Possible label noise:** every error has an assertive bridge verb
   (*påstod* ×4, *menade* ×2, *invände* ×2, …), but so do 96% of items, so
   this can't be separated with this test set. For such verbs, embedded V2
   (`att Iris minns ofta …`) is acceptable to many speakers.

## Ideas for a future experiment (not run)

### Measurement
- **More test items.** Build a larger independent embedded-clause test set,
  several hundred pairs, ideally checked by native speakers. With n = 100 only
  gains of about 10 points or more are detectable.
- **Control the confounds the error analysis found:**
  - adverb frequency (balance adverbs, or use frequency-normalised scores
    such as SLOR)
  - lexical and semantic plausibility of objects and PPs
  - bridge vs non-bridge matrix verbs, as a balanced factor, to separate
    model errors from genuine embedded-V2 acceptability
- **A clean main-clause test set:** same words, reversed order. Several
  SwE-BLiMP `V3*` phenomena contrast different adverbs, so they are imperfect
  controls.

### Controls
- **A structured random control.** Add a B′ arm that scales 3 random heads ×2
  in the same layers. B currently adds Gaussian noise of the same norm, which
  is a different kind of perturbation from scaling.
- **More random seeds** (≥ 50), so the C-vs-B comparison can go below p ≈ 0.09.

### Authoring protocol
- **Pre-register** the edit budget, the allowed primitives and the selection
  rule before authoring.
- **Several independent authoring runs** (different sessions or LLMs) using the
  protocol in `METHODS.md`, to estimate how much the outcome depends on the
  author.
- **Hold a second dev split** strictly back until freezing. The `check` split
  was used twice here.

### Edits and models
- Edits that also dampen components opposing the subordinate signal
  (L16 attention, heads 16.6–16.8, 13.3).
- Rank-1 edits on the MLPs that read it (L18, L22).
- A non-authored weight-space baseline: interpolate the Swedish continued-
  pretraining task vector from the base `SmolLM2-135M-Instruct`.
- Test whether the same circuit (a complementizer-reading head feeding the verb
  around layers 12–14, and one feeding the subject in a late layer) exists in
  the 360M Swedish model. If so, check whether the same kind of edit transfers.
