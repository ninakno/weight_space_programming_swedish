# Research note: Training-free weight editing for Swedish subordinate-clause word order

## 1. Introduction

Large language models still struggle with many linguistic problems, especially
in languages that are underrepresented in their training data. Many currently
available LLMs have not seen enough Swedish to handle the language reliably,
even though they can produce Swedish output. With some multilingual models, even a slight
increase in sampling temperature quickly leads to ungrammatical output or to
words from other languages being mixed in.

Retraining or fine-tuning LLMs on large amounts of Swedish data is expensive,
and depends on having enough clean training data. It would therefore be
interesting to see whether an existing model can be improved in terms of
grammaticality and language selection through *weight-space programming*:
"treating the weights as a program to be read and written, instead of leaving
them entirely to an optimizer" (Takehi et al., 2026). In that work, an LLM
directly edited a small fraction of another model's weights, for example
raising Qwen3.5-0.8B's MATH-500 score from 7.9% to 48.1% by editing 0.016% of
its weights, without any training. Such an approach could also sidestep the
problem of messy training data, since it does not require a training corpus at
all.

Grammaticality in general is a broad topic and difficult to evaluate, so I
restrict this study to specific grammatical phenomena that can be tested with
minimal pairs. Two natural candidates are gender
agreement between articles and nouns, and the position of adverbs in
subordinate clauses. Both are covered by the Swedish Benchmark of Linguistic
Minimal Pairs, SwE-BLiMP (Sjons et al., 2026), which makes the experiment
straightforward to set up. The guiding question is: **can weight-space
programming improve a model's ability to distinguish grammatical from
ungrammatical sentences, such as wrong gender agreement or wrong adverb
placement in subordinate clauses?**

In the experiment I focus on adverb placement in subordinate clauses. The
model I chose already scores 0.94–1.00 on the article–noun agreement phenomena,
so there was little room for improvement there. Subordinate-clause word order
(0.85) leaves more room.

**Scope.** A failed experiment would not really challenge the approach,
especially since this study only uses small local models on CPU. Properly
testing it would require a larger investigation with different models and
better test data. The aim here is to get an early indication of whether the
approach works, and to gather other insights into how it behaves.

## 2. Hypothesis

A small Swedish language model's errors on adverb–verb order in subordinate
*att*-clauses can be reduced by a targeted, training-free edit to its weights,
written by an LLM based on an analysis of the model's internals. The edit should
improve accuracy more than a random edit of the same size, without harming
main-clause word order or general Swedish ability.

**The phenomenon, by example.** In a Swedish main clause, the finite verb comes
*before* a sentence adverb such as *ofta* ("often"). In a subordinate clause
introduced by *att* ("that"), the adverb comes *before* the verb:

| | Swedish | Literal English |
|---|---|---|
| Main clause ✅ | Iris **minns ofta** parfymen. | Iris *remembers often* the perfume. |
| Subordinate clause ✅ | Rune påstod att Iris **ofta minns** parfymen. | Rune claimed that Iris *often remembers* the perfume. |
| Subordinate clause ❌ | \*Rune påstod att Iris **minns ofta** parfymen. | \*Rune claimed that Iris *remembers often* the perfume. |

The model has to learn that the same two words switch order depending on the
clause type. The test set consists of 100 pairs like the last two rows, and the
model is counted as correct if it assigns the higher probability to the
grammatical version. (In informal spoken Swedish, the starred order is sometimes
accepted after verbs like *påstod*; see Section 5.)

## 3. Experiment

I tested three arms on `jekunz/smollm-135m-cpt-fineweb-swedish`, a 135M-parameter
SmolLM2 model with continued pretraining on Swedish FineWeb-2 data, chosen because it already
handles Swedish reasonably well. The main test set was the SwE-BLiMP phenomenon
`EMBEDDED V2 AdvP.` (100 minimal pairs), with the other 25 SwE-BLiMP phenomena as
side-effect controls. Each pair was scored without prompting by comparing the
log-probabilities of the two sentences. The arms were: **A**, the unedited
model; **B**, ten random edits matched to C's size and location; and **C**, a
weight edit written by an LLM. The C edit was designed, implemented and selected
by **Claude Opus 5.5 (`claude-opus-5-5`), running in Claude Code (CLI, auto
mode)**, in an interactive session with me. Claude used activation
patching on a synthetic dev set and never saw the test pairs' results while
designing. The final edit doubles the output of three attention heads (13.5,
25.3, 25.4) that carry the complementizer *att* signal to the embedded verb and
subject. It was frozen (hash recorded) before the test evaluation. Everything ran
on CPU, with no training and no API keys. Full details are in `METHODS.md`.

## 4. Results

Accuracy on `EMBEDDED V2 AdvP.` (n = 100; 95% CIs from 10,000 bootstrap samples):

| Arm | Accuracy | 95% CI | Perplexity (Swedish Wikipedia) |
|---|---|---|---|
| A: baseline | 0.85 | [0.78, 0.92] | 6.356 |
| B: random matched edits (10 seeds) | mean 0.836, range 0.80–0.85 | — | 6.377–6.445 |
| C: LLM-authored edit | **0.88** | [0.81, 0.94] | 6.411 |

- **C vs A:** +3 percentage points. The edit fixed 3 pairs and broke none.
  Exact McNemar test p = 0.25; paired bootstrap 95% CI of the difference
  [+0.00, +0.07]. The improvement is not statistically significant.
- **C vs B:** C scored higher than all 10 random edits (best random seed: 0.85),
  giving an empirical p ≈ 0.09. That is the smallest p-value 10 seeds allow.

## 5. Interpretation

**Main reading.** The hypothesis is only weakly supported. The edit targets an
interpretable circuit: attention heads that copy the complementizer *att*
signal to the embedded subject (heads 25.3, 25.4) and to the embedded verb
(head 13.5). It moves the model in the intended direction, and it beats all
random edits of the same size. But a 3-point gain on 100 pairs is too small to
separate from chance, so the result is suggestive, not conclusive.

**Dev vs test gap.** On the synthetic dev pairs not used for selection, the
edit raised embedded-clause accuracy from 0.918 to 0.966, removing about 60% of
errors. On the test set it fixed only 3 of 15 errors. The error analysis
suggests why: dev errors sat close to the decision threshold, so a modest push
flipped them. Many test errors are further away, for reasons the edit does not
address.

**Error analysis highlights** (post hoc, after freezing; 15 pairs wrong under A
and/or C):
- **Consistent but small push.** The edit increased the good-vs-bad score
  difference in 13 of the 15 pairs, but most remain below zero. Four are very
  close to flipping (−0.01 to −0.43); the rest are 1–5 log-prob units short.
- **Rare adverbs.** *vanligtvis, vanligen, stundom, oftast* and *hädanefter*
  are very improbable right after a subject in any clause type. In those pairs,
  word frequency outweighs clause-type knowledge.
- **Semantic oddities.** Several test items are semantically unusual (*hör
  spiken*, *förstör klubban på morgondagen*, *påbörjar tankegången under
  kriget*). In several pairs, the words after the swapped region differ by 2–4
  log-prob units between the two orders, which is noise unrelated to the
  word-order rule.
- **Possible label noise.** All errors involve assertive bridge verbs (*påstod*,
  *menade*, *invände*, …). Many speakers accept embedded V2 after these verbs,
  so some "ungrammatical" sentences may be acceptable. With 96 of the 100 items
  using such verbs, this cannot be tested here.

**Side effects suggest a clause-specific edit.** The edit improved other
subordinate-clause phenomena: relative clauses (`V2 REL. CL.`, 0.87 → 0.93) and
`EMBEDDED V3 OBJ.` (0.29 → 0.36). Random edits did not. It lowered some
main-clause V3 phenomena (`V3 CL.` 0.80 → 0.76, `V3 OBJ.` 0.43 → 0.37).
Accuracy across all 2,600 SwE-BLiMP pairs was unchanged (0.772 → 0.775), and
perplexity rose by 0.9%. This pattern fits an edit that strengthens a general
"subordinate clause" signal rather than one tied to *att* + adverb. Some
main-clause cost remains, even though the main-clause dev pairs were meant to
prevent it.

**Limitations.**
- **Sample size:** with 100 pairs, only gains of about 10 points or more are
  reliably detectable.
- **Random control:** arm B adds Gaussian noise of the same norm, while C
  scales existing heads. A control that scales random heads would be fairer.
  Ten seeds also cap the C-vs-B p-value at about 0.09.
- **Selection rule:** "the mildest edit reaching maximum dev accuracy" was
  chosen after seeing the dev sweep, not pre-registered.
- **Single authoring run:** C comes from one interactive session with one LLM.
  How much the outcome depends on the author (another session, another model)
  is unknown.
- **Imperfect control phenomena:** several SwE-BLiMP `V3*` phenomena contrast
  different adverbs rather than reorder the same words, so they are imperfect
  main-clause controls.

## 6. Discussion: generalization, scaling and risks

**Scaling.** How well does the approach generalize and scale? The evidence so
far comes only from small models. Takehi et al. (2026) report large gains on
Qwen3.5-0.8B, but their edits failed on the even smaller Gemma 3 270M. The
authors attribute that failure not to model size but to the kind of error:
Qwen's failures came from a removable obstacle (looping), while Gemma's were
ordinary reasoning errors with no single component to switch off. In their
words, "editing weights could remove an obstacle that hid an ability, but it
could not add an ability the model lacked." Whether the approach works for
large models is therefore still open. It might work best for smaller models
specialised for narrow tasks, and it might scale better if LLMs were trained to
perform this kind of weight editing.

My results fit that observation. The edit strengthened something the model
already had: attention heads that read the complementizer *att*. It did not
help where the model lacked knowledge, such as rare adverbs it hardly
recognises in the relevant position. This experiment cannot say anything about
scaling, since it used a single 135M-parameter model. Within that model,
however, the edit did generalize beyond the cases it was designed on. Adverbs
held out from the design gained as much as those it was designed on (+4 vs +3
points), and other subordinate-clause constructions such as relative clauses
improved too.

**Catastrophic forgetting.** A known risk with specialising a model is that it
improves on one task and gets worse at everything else. Here the edit was small
and targeted (three attention heads), and the costs were limited. Accuracy
across all 2,600 SwE-BLiMP pairs was unchanged and perplexity rose by 0.9%,
although some main-clause phenomena dropped by 4–6 points. Targeted edits are
not necessarily destructive, but they are not free either.

**Why this matters in practice.** In industry, large models are often used for
many different tasks and languages. A cheap way to specialise an existing
model, for a language, a domain or a specific weakness, without retraining
would be valuable. That is the potential appeal of weight-space programming.

**Opening the black box.** Neural networks are usually treated as black boxes,
so it is fascinating that they can be opened up like this. In this experiment,
the analysis located a few specific attention heads that carry the
"subordinate clause" signal, and the edit acts on exactly those components.

**Risks of a model editing a model.** At the same time, the approach creates a
loop: one model edits another, the edited model is used again, and so on. In
general we do not know what the optimised weights mean or what side effects
they might have. In this case the edit was interpretable: three heads, each
scaled by a factor of 2, with a documented rationale. Edits that are larger,
denser or found through automated search could be much harder to understand and
check. That makes transparency, side-effect evaluation and documented authoring
protocols important if the approach is used more widely.

## 7. Recommendation

**Relevance to SE.LLMA's goal of building strong Swedish language models:**
for now, the evidence that weight-space programming can help is weak.

**What this experiment shows.** It is consistent with LLM-authored weight edits
improving a *small* model on a *specific, narrow* task, but it does not
establish this on its own:
- On the test set the gain was not significant (+3 points, p = 0.25).
- The support comes mainly from three other findings: the larger improvement on
  held-out dev pairs (0.918 → 0.966), the edit outperforming all random edits of
  the same size, and an interpretable mechanism (three attention heads carrying
  the *att* signal).
- The experiment used a single 135M-parameter model and a single grammatical
  phenomenon. It says nothing about larger models or broader tasks.

**What the wider evidence shows.** All evidence so far, including Takehi et al.
(2026), comes from small models (at most 0.8B parameters) and from specific
tasks. That work also shows that edits can fail even on small models when there
is no single obstacle to remove. There is not yet any evidence either way for
large models or broad tasks such as overall Swedish grammaticality.

Taken together, I would not yet treat weight-space programming as a method for
building or substantially improving strong Swedish models.

**The comparison that matters for SE.LLMA.** This experiment excluded training
by design, but SE.LLMA does train models. The practical question is therefore
not only whether an edit helps, but whether it beats cheap alternatives that are
already available:
- a small LoRA or fine-tune on a few hundred targeted examples
- better pretraining or instruction data covering the construction

The editing approach is not free either. Here it took diagnostics, around ten
candidate edits and an interactive authoring session. If a short fine-tune fixes
the same errors at similar cost, editing is mainly of research interest.

**Where it could fit.** Strong models are likely to be at or near ceiling on
single rules like this one. If the approach holds up, its realistic roles for
SE.LLMA are probably:
1. **Diagnosis:** finding *why* a model fails on a specific construction. This
   part worked well here: activation patching located the responsible heads
   quickly.
2. **Cheap targeted fixes:** for small or already deployed models where
   retraining is impractical.

That said, this is an early, small exploratory study, and it may only be the
start. Many more experiments are needed to see where the approach is useful and
where it is not. The most informative next steps would be:

1. **Compare against cheap training:** run the same task with a small LoRA or
   fine-tune on targeted examples, matched for effort and compute. This is the
   most decision-relevant comparison for SE.LLMA.
2. **Compare against other weight-space methods:** for example task-vector
   interpolation with the Swedish continued-pretraining delta, to see whether
   LLM-authored edits add anything beyond existing methods.
3. **Measure better:** larger, cleaner test sets (several hundred pairs,
   controlled for word frequency, semantic plausibility and verb type),
   stronger random controls (scaling random heads, ≥ 50 seeds), and a
   pre-registered selection rule.
4. **Test robustness of the authoring:** several independent authoring runs,
   with different sessions and different LLMs, following the protocol in
   `METHODS.md`.
5. **Test scaling:** check whether similar circuits exist, and whether similar
   edits work, in larger Swedish models and on broader tasks than a single
   word-order rule.

Until such results exist, I see weight-space programming as a promising
research direction for SE.LLMA, most immediately useful as a diagnostic tool
for understanding specific model failures. It is not yet a practical method for
improving Swedish models.

## AI usage

This project was carried out with substantial AI assistance from **Claude Opus 5.5
(`claude-opus-5-5`), running in Claude Code (CLI, auto mode)**.

- **Idea:** the idea for the experiment, testing whether weight-space
  programming can improve an LLM on Swedish subordinate-clause word order, was
  my own.
- **Planning:** I planned the experiment together with Claude. Key decisions
  were mine: the three-arm design (baseline, random edit, LLM edit), the
  constraints (no training, CPU only, no API keys), the model choice and the
  scope.
- **Code and execution:** all code was written by Claude, and Claude ran the
  experiments, diagnostics and analyses.
- **The edit in arm C:** as described in Section 3, the edit was designed and
  selected by Claude. Being written by an LLM is part of what was tested.
- **This note:** Claude drafted the text of each section based on my
  instructions on what to include. I reviewed and revised it.

## References

Sjons, J., Heinat, F., & Kurfalı, M. (2026). The Swedish Benchmark of
Linguistic Minimal Pairs. In *Proceedings of LREC 2026*, pp. 6783–6794.
https://aclanthology.org/2026.lrec-1.540.pdf

Takehi, R., Teoh, J., Zhang, A., & Khattab, O. (2026, November 2). Sparks of
Weight-Space Programming: LLMs can natively read & write neural network
weights. Blog post, MIT CSAIL.
https://rikiyat.github.io/blog/weight-space-programming/

**Resources:** model `jekunz/smollm-135m-cpt-fineweb-swedish`
(https://huggingface.co/jekunz/smollm-135m-cpt-fineweb-swedish); SwE-BLiMP data
(https://github.com/itsup/swe_blimp, commit 4770e27).
