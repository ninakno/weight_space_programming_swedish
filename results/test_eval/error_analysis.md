# Post-hoc error analysis (exploratory)

Target pairs wrong under A and/or C. Margins in log-prob units, positive = prefers good.
d1 = ADV vs V right after the embedded subject; d2 = next word vs ADV right after the verb.

```
 item        status  matrix_verb     adverb adverb_group  A_total  C_total  A_d1  C_d1  A_d2  C_d2
   11 wrong in both       menade     alltid  seen in dev    -0.68    -0.01  1.31  1.02 -6.46 -5.41
   22    FIXED by C      invände vanligtvis     held out    -0.43     0.45 -5.94 -5.34 -1.29 -0.54
   23 wrong in both   underströk     ibland  seen in dev    -1.53    -0.43 -2.32 -1.34 -5.66 -4.88
   38 wrong in both kommenterade    stundom     held out    -2.94    -1.31 -1.56 -1.50  0.18  0.94
   40    FIXED by C       påstod       ofta  seen in dev    -0.97     0.46 -0.32  0.73 -8.83 -8.09
   44 wrong in both       menade       ofta  seen in dev    -4.30    -4.03 -1.56 -1.22 -4.51 -3.79
   47 wrong in both     föreslog     aldrig  seen in dev    -3.17    -3.16  1.48  1.78 -7.08 -6.35
   59 wrong in both    berättade     oftast  seen in dev    -4.54    -3.02 -2.73 -2.07 -6.40 -5.45
   64 wrong in both tillkännagav   vanligen     held out    -0.05    -0.15 -4.88 -5.11  0.82  1.24
   69 wrong in both    uttryckte hädanefter     held out    -2.03    -1.13 -5.66 -5.01 -6.33 -6.04
   76 wrong in both   förklarade     aldrig  seen in dev    -5.33    -4.80  1.36  2.69  1.34  1.77
   77 wrong in both       påstod     alltid  seen in dev    -2.13    -1.26  2.82  3.81  2.72  3.15
   82 wrong in both       påstod    stundom     held out    -1.02    -0.35 -2.95 -2.50  1.87  1.71
   88 wrong in both      invände vanligtvis     held out    -3.54    -2.28 -8.23 -7.34  0.83  1.26
   98    FIXED by C       påstod     alltid  seen in dev    -0.16     0.02  3.74  4.49 -0.52 -0.83
```

## item 11 — wrong in both  (matrix verb: menade, adverb: alltid, seen in dev)
- A: total -0.68  d1 +1.31  d2 -6.46
- C: total -0.01  d1 +1.02  d2 -5.41
- good (A): Jonas(-24.6) menade(-9.6) att(-0.4) Alf(-10.6) alltid(-9.4) säljer(-10.0) gardinen(-14.2) på(-3.0) kvällen(-5.1)
- bad  (A): Jonas(-24.6) menade(-9.6) att(-0.4) Alf(-10.6) säljer(-10.7) alltid(-7.7) gardinen(-14.4) på(-2.9) kvällen(-5.3)

## item 22 — FIXED by C  (matrix verb: invände, adverb: vanligtvis, held out)
- A: total -0.43  d1 -5.94  d2 -1.29
- C: total +0.45  d1 -5.34  d2 -0.54
- good (A): Ahmed(-17.0) invände(-15.8) att(-1.4) Mats(-11.0) vanligtvis(-15.5) bär(-7.2) kompassen(-11.9) på(-2.5) sommaren(-5.8)
- bad  (A): Ahmed(-17.0) invände(-15.8) att(-1.4) Mats(-11.0) bär(-9.5) vanligtvis(-10.6) kompassen(-13.4) på(-2.3) sommaren(-6.6)

## item 23 — wrong in both  (matrix verb: underströk, adverb: ibland, seen in dev)
- A: total -1.53  d1 -2.32  d2 -5.66
- C: total -0.43  d1 -1.34  d2 -4.88
- good (A): Mats(-17.8) underströk(-15.4) att(-1.5) Eva(-9.7) ibland(-14.1) glömmer(-7.2) nappen(-12.5) på(-2.8) lördagen(-10.5)
- bad  (A): Mats(-17.8) underströk(-15.4) att(-1.5) Eva(-9.7) glömmer(-11.8) ibland(-6.8) nappen(-13.5) på(-3.1) lördagen(-10.3)

## item 38 — wrong in both  (matrix verb: kommenterade, adverb: stundom, held out)
- A: total -2.94  d1 -1.56  d2 +0.18
- C: total -1.31  d1 -1.50  d2 +0.94
- good (A): Kristina(-17.9) kommenterade(-11.9) att(-3.0) Klara(-10.7) stundom(-13.5) lagar(-11.8) motorn(-12.5) i(-2.9) juli(-12.9)
- bad  (A): Kristina(-17.9) kommenterade(-11.9) att(-3.0) Klara(-10.7) lagar(-11.9) stundom(-12.7) motorn(-10.8) i(-3.2) juli(-12.0)

## item 40 — FIXED by C  (matrix verb: påstod, adverb: ofta, seen in dev)
- A: total -0.97  d1 -0.32  d2 -8.83
- C: total +0.46  d1 +0.73  d2 -8.09
- good (A): Olle(-19.2) påstod(-14.2) att(-0.5) Helga(-12.1) ofta(-8.4) hör(-5.7) spiken(-17.1) i(-1.1) september(-11.2)
- bad  (A): Olle(-19.2) påstod(-14.2) att(-0.5) Helga(-12.1) hör(-8.1) ofta(-8.3) spiken(-13.4) i(-0.8) september(-12.0)

## item 44 — wrong in both  (matrix verb: menade, adverb: ofta, seen in dev)
- A: total -4.30  d1 -1.56  d2 -4.51
- C: total -4.03  d1 -1.22  d2 -3.79
- good (A): Alba(-19.6) menade(-10.9) att(-0.4) Rune(-12.5) ofta(-13.1) glömmer(-7.7) kartan(-9.9) på(-3.5) vintern(-7.1)
- bad  (A): Alba(-19.6) menade(-10.9) att(-0.4) Rune(-12.5) glömmer(-11.6) ofta(-5.4) kartan(-9.5) på(-3.5) vintern(-7.0)

## item 47 — wrong in both  (matrix verb: föreslog, adverb: aldrig, seen in dev)
- A: total -3.17  d1 +1.48  d2 -7.08
- C: total -3.16  d1 +1.78  d2 -6.35
- good (A): Vive(-19.6) föreslog(-12.7) att(-1.1) Dick(-10.0) aldrig(-11.8) hatar(-12.1) tunnan(-14.6) på(-4.6) hösten(-8.3)
- bad  (A): Vive(-19.6) föreslog(-12.7) att(-1.1) Dick(-10.0) hatar(-13.3) aldrig(-7.5) tunnan(-15.4) på(-4.4) hösten(-7.6)

## item 59 — wrong in both  (matrix verb: berättade, adverb: oftast, seen in dev)
- A: total -4.54  d1 -2.73  d2 -6.40
- C: total -3.02  d1 -2.07  d2 -5.45
- good (A): Ida(-18.5) berättade(-7.7) att(-1.4) Maj(-9.2) oftast(-17.2) väcker(-9.3) assistenten(-16.5) på(-3.2) natten(-2.9)
- bad  (A): Ida(-18.5) berättade(-7.7) att(-1.4) Maj(-9.2) väcker(-14.4) oftast(-10.1) assistenten(-14.2) på(-3.1) natten(-2.8)

## item 64 — wrong in both  (matrix verb: tillkännagav, adverb: vanligen, held out)
- A: total -0.05  d1 -4.88  d2 +0.82
- C: total -0.15  d1 -5.11  d2 +1.24
- good (A): Erika(-18.4) tillkännagav(-13.7) att(-2.3) Sandra(-10.5) vanligen(-16.4) ringer(-7.3) vännen(-10.6) på(-3.4) kvällen(-4.2)
- bad  (A): Erika(-18.4) tillkännagav(-13.7) att(-2.3) Sandra(-10.5) ringer(-11.5) vanligen(-11.4) vännen(-11.6) på(-3.4) kvällen(-3.9)

## item 69 — wrong in both  (matrix verb: uttryckte, adverb: hädanefter, held out)
- A: total -2.03  d1 -5.66  d2 -6.33
- C: total -1.13  d1 -5.01  d2 -6.04
- good (A): Ingrid(-19.6) uttryckte(-14.0) att(-2.5) Inger(-13.0) hädanefter(-11.4) får(-4.1) saxen(-16.7) på(-3.3) morgonen(-11.0)
- bad  (A): Ingrid(-19.6) uttryckte(-14.0) att(-2.5) Inger(-13.0) får(-5.8) hädanefter(-10.3) saxen(-17.1) på(-3.2) morgonen(-8.0)

## item 76 — wrong in both  (matrix verb: förklarade, adverb: aldrig, seen in dev)
- A: total -5.33  d1 +1.36  d2 +1.34
- C: total -4.80  d1 +2.69  d2 +1.77
- good (A): Adam(-16.8) förklarade(-10.0) att(-0.9) Magdalena(-10.4) aldrig(-12.1) översätter(-15.4) artiklar(-5.9) under(-5.7) vintern(-8.8)
- bad  (A): Adam(-16.8) förklarade(-10.0) att(-0.9) Magdalena(-10.4) översätter(-13.5) aldrig(-7.2) artiklar(-5.2) under(-6.0) vintern(-10.7)

## item 77 — wrong in both  (matrix verb: påstod, adverb: alltid, seen in dev)
- A: total -2.13  d1 +2.82  d2 +2.72
- C: total -1.26  d1 +3.81  d2 +3.15
- good (A): Magdalena(-25.1) påstod(-12.1) att(-0.5) Alice(-9.4) alltid(-7.7) löser(-10.1) problemet(-3.1) under(-6.8) våren(-8.1)
- bad  (A): Magdalena(-25.1) påstod(-12.1) att(-0.5) Alice(-9.4) löser(-10.5) alltid(-5.8) problemet(-2.4) under(-6.6) våren(-8.3)

## item 82 — wrong in both  (matrix verb: påstod, adverb: stundom, held out)
- A: total -1.02  d1 -2.95  d2 +1.87
- C: total -0.35  d1 -2.50  d2 +1.71
- good (A): Ann-Katrin(-27.5) påstod(-13.0) att(-0.5) Anna-Lena(-11.8) stundom(-15.2) påbörjar(-13.2) tankegången(-12.8) under(-4.7) kriget(-9.0)
- bad  (A): Ann-Katrin(-27.5) påstod(-13.0) att(-0.5) Anna-Lena(-11.8) påbörjar(-12.3) stundom(-14.7) tankegången(-13.3) under(-4.7) kriget(-9.0)

## item 88 — wrong in both  (matrix verb: invände, adverb: vanligtvis, held out)
- A: total -3.54  d1 -8.23  d2 +0.83
- C: total -2.28  d1 -7.34  d2 +1.26
- good (A): Tobias(-17.2) invände(-14.1) att(-1.3) Björn(-8.0) vanligtvis(-17.3) förstör(-8.7) klubban(-12.6) på(-2.4) morgondagen(-15.1)
- bad  (A): Tobias(-17.2) invände(-14.1) att(-1.3) Björn(-8.0) förstör(-9.0) vanligtvis(-13.4) klubban(-12.2) på(-2.3) morgondagen(-15.5)

## item 98 — FIXED by C  (matrix verb: påstod, adverb: alltid, seen in dev)
- A: total -0.16  d1 +3.74  d2 -0.52
- C: total +0.02  d1 +4.49  d2 -0.83
- good (A): Saga(-18.4) påstod(-13.9) att(-0.7) Klas(-10.5) alltid(-8.2) vinner(-9.5) priset(-7.0) på(-3.8) våren(-8.7)
- bad  (A): Saga(-18.4) påstod(-13.9) att(-0.7) Klas(-10.5) vinner(-12.0) alltid(-6.5) priset(-6.7) på(-3.4) våren(-8.5)
