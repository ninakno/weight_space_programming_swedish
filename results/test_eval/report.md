# Test results: EMBEDDED V2 AdvP. (n=100)

| Arm | Acc | 95% CI | Perplexity |
|---|---|---|---|
| A | 0.85 | [0.78, 0.92] | 6.356 |
| C | 0.88 | [0.81, 0.94] | 6.411 |
| B0 | 0.82 | [0.74, 0.89] | 6.445 |
| B1 | 0.84 | [0.77, 0.91] | 6.377 |
| B2 | 0.84 | [0.77, 0.91] | 6.422 |
| B3 | 0.85 | [0.78, 0.92] | 6.423 |
| B4 | 0.83 | [0.75, 0.90] | 6.393 |
| B5 | 0.80 | [0.72, 0.88] | 6.411 |
| B6 | 0.84 | [0.76, 0.91] | 6.412 |
| B7 | 0.84 | [0.77, 0.91] | 6.394 |
| B8 | 0.85 | [0.78, 0.92] | 6.377 |
| B9 | 0.85 | [0.78, 0.92] | 6.387 |

B (random, 10 seeds): mean=0.836 sd=0.016 min=0.80 max=0.85

**C vs A:** +0.03 (paired bootstrap 95% CI [+0.00, +0.07]); fixed 3, broke 0; exact McNemar p=0.2500
**C vs B:** C=0.88; 0/10 random seeds reach >= C (empirical p ≈ 0.091)

## Target breakdown

| adverb_group | n | A | C | mean B |
|---|---|---|---|---|
| held out | 25 | 0.76 | 0.80 | 0.75 |
| seen in dev | 75 | 0.88 | 0.91 | 0.87 |

| verb_class | n | A | C | mean B |
|---|---|---|---|---|
| assertive | 96 | 0.84 | 0.88 | 0.83 |
| non-assertive | 4 | 1.00 | 1.00 | 0.97 |

## All phenomena (side effects)

| Phenomenon | A | C | C−A | mean B |
|---|---|---|---|---|
| ARG. STR. | 0.75 | 0.76 | +0.01 | 0.74 |
| DOUBLE DEF. | 0.96 | 0.95 | -0.01 | 0.96 |
| ART. NOUN AGR. INDEF. | 0.94 | 0.93 | -0.01 | 0.94 |
| ART. NOUN AGR. GEN. | 1.00 | 1.00 | +0.00 | 1.00 |
| ART. NOUN AGR. PL. | 0.98 | 0.98 | +0.00 | 0.98 |
| ART. NOUN AGR. SG. | 1.00 | 1.00 | +0.00 | 1.00 |
| EMBEDDED V2 AdvP. **(target)** | 0.85 | 0.88 | +0.03 | 0.84 |
| EMBEDDED V3 CL. | 0.94 | 0.94 | +0.00 | 0.94 |
| EMBEDDED V3 OBJ. | 0.29 | 0.36 | +0.07 | 0.27 |
| PARTICLE OBJ. ORDER | 0.90 | 0.91 | +0.01 | 0.88 |
| ADJ. NOUN AGR. GEN. | 0.59 | 0.59 | +0.00 | 0.59 |
| ADJ. NOUN AGR. DEF. | 0.56 | 0.56 | +0.00 | 0.56 |
| ADJ. NOUN AGR. INDEF. | 0.53 | 0.53 | +0.00 | 0.53 |
| ADJ. NOUN AGR. NUM. PL. | 0.85 | 0.85 | +0.00 | 0.84 |
| ADJ. NOUN AGR. NUM. SG. | 0.99 | 0.98 | -0.01 | 0.98 |
| NO RESUMPTION | 0.84 | 0.81 | -0.03 | 0.86 |
| RESUMPTION 1 | 0.99 | 0.99 | +0.00 | 0.99 |
| RESUMPTION 2 | 1.00 | 1.00 | +0.00 | 1.00 |
| V3 CL. | 0.80 | 0.76 | -0.04 | 0.79 |
| V3 OBJ. | 0.43 | 0.37 | -0.06 | 0.40 |
| V3 PP | 0.97 | 0.97 | +0.00 | 0.97 |
| V2 REL. CL. | 0.87 | 0.93 | +0.06 | 0.88 |
| V3 COMPLEX NP | 0.74 | 0.77 | +0.03 | 0.73 |
| ELLIPSIS1 | 0.03 | 0.04 | +0.01 | 0.03 |
| V3 | 0.36 | 0.37 | +0.01 | 0.37 |
| ELLIPSIS2 | 0.92 | 0.91 | -0.01 | 0.92 |
| **overall (2600)** | 0.772 | 0.775 | +0.002 | 0.769 |
