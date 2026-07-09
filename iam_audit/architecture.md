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
