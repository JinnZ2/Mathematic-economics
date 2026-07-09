iam_audit/
├── README.md
├── CLAIM_TABLE.json               # Claims specifically about IAM comparison
├── run.py                         # Entrypoint: --model dice|fund|ours [--scenario]
├── modules/
│   ├── __init__.py
│   ├── iam_smoothness_audit.py    # Merle blow‑up detection vs. DICE damage function
│   ├── iam_cascade_thresholds.py  # HOI reduction + missing cascade coupling
│   ├── iam_scope_collapse.py      # What DICE omits (institutions, governance, care)
│   └── iam_falsifiability_gap.py  # Engineering‑grade validation of IAM internals
├── scenarios/
│   ├── dice_baseline.py           # DICE‑2023R assumptions encoded as auditable dict
│   └── our_model.py               # Your unified model's assumptions (for comparison)
└── examples/
    ├── rcp85_divergence.py        # Works‑case / fails‑case style for a forcing pathway
    └── rcp26_divergence.py


claim mapping:
Claim ID Module IAM audit use
C020 thermodynamic_accounting_audit Re‑compute DICE’s implied energy cost of abatement against full‑stack eROI
C027 economic_energy_grounding_audit Test DICE’s internal coherence against 5‑criterion validity
C028 economic_energy_grounding_audit Measure DICE’s institutional blindness score
C031 engineering_grade_validation_audit DICE fails 3/4 criteria (design margin, failure modes, falsifiability)
C032 engineering_grade_validation_audit AI‑on‑DICE cascade risk when regime shifts
C025 systemic_precondition_audit All 7 preconditions DICE silently assumes
C026 systemic_precondition_audit DICE’s own economic‑stability precondition undercut
C021 scaling_audit DICE’s damage function lacks interior optimum
C043–C048 governance_thermodynamics_audit DICE has no governance layer; costs omitted
C060–C064 substrate_care_audit Care work, authority inversion – invisible in DICE

New IAM‑specific claims (I001‑I0xx) will cover:

· I001: DICE damage function is smooth → fails Merle blow‑up test for d²E/dt² acceleration.
· I002: DICE pairwise coupling only → misses 70% threshold reduction from hypergraph interactions.
· I003: DICE carbon cycle assumes linear exchange coefficients without regime‑shift (AMOC, permafrost).
· I004: DICE’s single‑agent representative consumer erases distributional extraction (ER, UFR, HHI).
· I005: DICE’s social discount rate is a political choice, not a measurement – violates falsifiability.


