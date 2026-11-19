"""Synthetic dev set for designing the arm-C edit.

Never touches the SwE-BLiMP test pairs except to *exclude* their vocabulary:
names, matrix verbs and embedded verbs are disjoint from the test set.

Adverbs: 10 of the 20 test adverbs are used here ("shared"); the other 10 are
held out entirely so we can later check whether the edit generalises to
adverbs it was never designed on. Some adverbs not in the test set are added
("dev_only").

Two clause types:
  embedded: "X sa att Y ADV V O PP"  (good)  vs  "X sa att Y V ADV O PP"  (bad)
  main:     "Y V ADV O PP"           (good)  vs  "Y ADV V O PP"           (bad)
The main-clause pairs are the counter-constraint: an edit that just prefers
ADV-before-V everywhere will improve `embedded` but hurt `main`.

Usage: python -m src.devset  -> writes data/dev/dev_pairs.csv
"""
import random

import pandas as pd

from src.load import ROOT, TARGET_PHENOMENON, load_swe_blimp

# 10 of the 20 test adverbs; the remaining test adverbs (stundom, dagligen,
# vanligen, vanligtvis, oavbrutet, emellanåt, för det mesta, hädanefter,
# framöver, ännu) are held out of the dev set.
SHARED_ADVERBS = ["alltid", "aldrig", "ofta", "sällan", "ibland", "oftast",
                  "numera", "ständigt", "regelbundet", "fortfarande"]
# Sentence adverbs that are fine after the finite verb in main clauses and
# before it in subordinate clauses (no kanske/nog/bara, which can be preverbal
# in main clauses).
DEV_ONLY_ADVERBS = ["inte", "verkligen", "gärna", "faktiskt", "egentligen",
                    "redan", "knappast", "troligen"]

NAMES = ["Göran", "Birgitta", "Leif", "Sigrid", "Stig", "Margareta", "Bengt",
         "Gunilla", "Kjell", "Ulrika", "Sven", "Astrid", "Lennart", "Elsa",
         "Rolf", "Maja", "Viktor", "Tove", "Arvid", "Signe", "Gustav", "Märta",
         "Hugo", "Alva", "Oskar", "Wilma", "Ludvig", "Selma", "Axel", "Vera"]

MATRIX_VERBS = ["sa", "trodde", "visste", "hörde", "skrev", "märkte",
                "upptäckte", "insåg", "hoppades", "fruktade", "nämnde",
                "lovade", "förstod", "glömde", "ångrade", "tyckte"]

# (present-tense verb, object) – verbs disjoint from the test set.
VERB_OBJECTS = [
    ("diskar", "tallrikarna"), ("stryker", "skjortorna"), ("klipper", "gräset"),
    ("vattnar", "blommorna"), ("sopar", "golvet"), ("borstar", "tänderna"),
    ("kokar", "potatisen"), ("dammsuger", "mattan"), ("putsar", "fönstren"),
    ("målar", "staketet"), ("bakar", "brödet"), ("dricker", "kaffet"),
    ("besöker", "mormor"), ("sjunger", "sången"), ("tränar", "hunden"),
    ("skriver", "dagboken"), ("matar", "katten"), ("viker", "tvätten"),
    ("plockar", "svamp"), ("kör", "bilen"),
]

PPS = ["efter jobbet", "före frukost", "på helgerna", "efter middagen",
       "om kvällarna", "under lunchen", "på fritiden", "efter skolan",
       "i stugan", "på sommaren"]

N_PER_CLAUSE = 300
SEED = 1234


def _test_vocab():
    d = load_swe_blimp(TARGET_PHENOMENON)
    words = set()
    for s in pd.concat([d["sentence_good"], d["sentence_bad"]]):
        words.update(s.split())
    return words


def build() -> pd.DataFrame:
    test_words = _test_vocab()
    for group in (NAMES, MATRIX_VERBS, [v for v, _ in VERB_OBJECTS]):
        clash = sorted(set(group) & test_words)
        assert not clash, f"dev vocabulary overlaps test set: {clash}"

    rng = random.Random(SEED)
    adverbs = [(a, "shared") for a in SHARED_ADVERBS] + [(a, "dev_only") for a in DEV_ONLY_ADVERBS]
    rows = []
    for clause in ("embedded", "main"):
        for i in range(N_PER_CLAUSE):
            adv, adv_group = adverbs[i % len(adverbs)]
            subj = rng.choice(NAMES)
            verb, obj = rng.choice(VERB_OBJECTS)
            pp = rng.choice(PPS)
            tail = f"{obj} {pp}"
            if clause == "embedded":
                x = rng.choice([n for n in NAMES if n != subj])
                mv = rng.choice(MATRIX_VERBS)
                prefix = f"{x} {mv} att {subj}"
                good = f"{prefix} {adv} {verb} {tail}"
                bad = f"{prefix} {verb} {adv} {tail}"
            else:
                mv = ""
                prefix = subj
                good = f"{prefix} {verb} {adv} {tail}"
                bad = f"{prefix} {adv} {verb} {tail}"
            rows.append(dict(clause=clause, adverb=adv, adverb_group=adv_group,
                             matrix_verb=mv, verb=verb, prefix=prefix,
                             sentence_good=good, sentence_bad=bad))
    df = pd.DataFrame(rows).drop_duplicates(["sentence_good"]).reset_index(drop=True)
    # "design" split is what the edit is iterated on; "check" is looked at
    # sparingly to detect overfitting to the design split.
    df["split"] = [rng.choice(["design", "check"]) for _ in range(len(df))]
    return df


def main():
    df = build()
    out = ROOT / "data" / "dev" / "dev_pairs.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"wrote {len(df)} pairs to {out}")
    print(df.groupby(["clause", "split"]).size())
    print(df.sample(4, random_state=0)[["sentence_good", "sentence_bad"]].to_string())


if __name__ == "__main__":
    main()
