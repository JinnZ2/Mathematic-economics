# substrate-allocation  (CC0, stdlib-only)

The framing layer under the audit family. Nothing is 'replaceable' or 'a
failure' in the abstract. There is only FIT: which substrate handles a task's
constraint geometry at lowest cost. Misallocation is the shared product of two
narratives that both require the allocation to stay wrong:

```
  "humans easily replaceable"          "automation is a failure"
     keep the human path                  hand general AI the
     handicapped, deny its                chaotic/extrapolative tasks
     parallel-cognition strength          it is worst at, then point

   BOTH REQUIRE MISALLOCATION. Correct allocation collapses both at once.
```

## CAPABILITY AXES (supply, 0..1)

```
                 C1det C2chaos C3interp C3extrap C4drift C5energy
 DEDICATED        1.00  0.10    0.00     0.00     1.00    1.00   committed, no drift
 HUMAN_PARALLEL   0.30  0.95    0.40     0.90     0.90    0.55   extrapolative domain
 GENERAL_AI       0.70  0.40    0.95     0.15     0.20    0.20   interp; hallucinates OOD
```

C3 is SPLIT, and the split is load-bearing:

- C3_interp  INTERPOLATIVE novelty: synthesis inside the data distribution.
  AI's real strength (cross-corpus pattern-finding). Fails OOD by
  hallucinating.
- C3_extrap  EXTRAPOLATIVE novelty: zero-shot physics in genuinely unprecedented
  situations, via proprioceptive force-gradient sensing. The human
  domain. Survives OOD (the fawn computes a force-gradient, not a
  classifier; you feel the kingpin, not a probability).

A single novelty axis let AI win EVERYTHING novel. Split, AI wins combinatorial
novelty and LOSES adaptive/unprecedented novelty -- the boundary you live on.

'Dumb' computing is not dumb. A committed structure spent its potential once and
holds it at ~zero upkeep. Generality is a STANDING TAX paid to hold options open
against entropy -- pay it only where novelty actually lives.

## THREE MODULES

```
substrate_allocation.py   task demand vs substrate supply -> fit, cost,
                          best-fit, misallocation TAX. balanced: each substrate
                          wins its real domain (DEDICATED high-volume determ;
                          HUMAN chaos+extrap+safety; AI interpolative novelty).

misallocation_bias.py     directional-bias detector. random misallocation
                          SCATTERS; motivated misallocation LEANS. Herfindahl
                          concentration vs permutation null. Proven to have
                          power AND restraint: noise->NOISE, underpowered->NOISE,
                          real lean->DIRECTIONAL_STRUCTURE_DETECTED. Names the
                          innocent common-cause to rule out; never asserts intent.

operator_profile.py       per-operator override (drift/stamina/duty-cycle are
                          PARAMETERS you measure on the real node, not constants)
                          + hiring-choice confound detector.
```

## PER-OPERATOR PROFILE (don't inherit the average; don't deny drift)

The fleet-average human vector is a statistical stand-in, not a person. Fatigue,
skill-decay, habituation, stamina are real (Gemini's "humans don't drift" is
false) -- but their RATES are not constants. A high-adapted operator (reduced
sleep need, body-as-machine-extension, machine-as-sensory-extension) runs a
different C4/C5 and a longer duty cycle. Measure your own baseline, the way you
strip equipment aids at the start of an archery session. Profiles ship flagged
`[ASSUMED - measure this]` until clocked.

## THE HIRING-CHOICE CONFOUND

'Automation beats humans' usually varies TWO things at once: substrate type AND
operator quality, then blames substrate. A task whose best-fit FLIPS away from
the human when operator quality drops is COVERAGE for a hiring choice -- and the
detector tracks WHICH substrate covers:

```
  flip HUMAN -> DEDICATED   honest coverage by the correct low-entropy tool
  flip HUMAN -> GENERAL_AI  AI-as-coverage: a DOUBLE error -- coverage for a
                            hiring choice routed to the WRONG substrate, since
                            AI shares the human's weak axes (chaos, extrap,
                            drift, stamina).
```

Structural finding (demo): coverage flips to DEDICATED, never to GENERAL_AI.
The axes a human degrades on are AI's weak axes too -- so honest coverage of a
low-qualified body is a dedicated structure, NOT general AI. Selling AI as that
coverage is a substrate error on top of a hiring error.

THE HONEST FORK:

- hire quality bodies -> they hold the fatiguing chaos/extrap work; keep
  automation out of out-of-scope roles.
- choose lower-qualified bodies -> ADMIT it; cover the deterministic tedium with
  a DEDICATED tool.
- either way: automation/regulation is COVERAGE FOR A HIRING CHOICE, labeled as
  such -- never as a 'machine > human' narrative datapoint.

## RUN

```
python3 substrate_allocation.py   # per-task fit + misallocation tax
python3 misallocation_bias.py     # noise / underpowered / directional regimes
python3 operator_profile.py       # per-operator tax + hiring-confound verdict
```

## TO MAKE IT BITE

Encode a real operation's subtasks with honest constraint-geometry demands and
their actual assignments. Measure YOUR operator profile and pass it in. The tax
says what misallocation costs and who bears it; the bias detector says whether
errors LEAN and toward which substrate; the confound detector says whether the
'automation win' is really coverage for a hiring choice -- and whether it's even
routed to the right covering substrate. Then rule out the innocent common cause.
If you can't, you've found the gradient.

stdlib only. no numpy. no network. runs from a phone.
