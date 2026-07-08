# Claims Index

Top-level pointer for the falsifiable-claim registries referenced by
`README.md`, `CITATION.cff`, and `metadata.json`. Each entry names the
canonical file and its ID range so an academic bot honoring the CFF
lands on real files.

| Register | ID range | Location | Format |
|---|---|---|---|
| Automation-scope audit (fab) | C000-C083 | `automation_scope_audit/CLAIM_TABLE.fab.json` | JSON, validated by `automation_scope_audit/validate_fab.py` |
| Automation-scope audit (canonical) | C000-C083 | `automation_scope_audit/CLAIM_TABLE.json` | JSON |
| Substrate accounting | (unified) | `substrate_accounting/CLAIMS_UNIFIED.json` | JSON |
| Ringwoodite / earth coupling | (domain-specific) | `ringwoodite_earth_coupling/CLAIM_TABLE.earth.json` | JSON |
| Accounting layer | (prose narrative) | `accounting/CLAIMS.md` | Markdown |
| Core 13 structural equations | equations-v1 surface | `equations.yaml` | YAML with data-source bindings |

See `CLAIM_TABLE_VERSIONING.md` for the versioning contract, and
`schemas/claim_contract.py` for the machine-checkable claim schema.

## Refutation protocol

Every claim in every register carries a single-sentence falsifier.
The general protocol:

1. Locate the claim by its ID or file path.
2. Produce the measurement that contradicts it.
3. Update the register — do not retune the surrounding modules to
   make the failing claim pass.

See `FALSIFIABILITY_NOTICE.txt` and `PREDICTION_PROTOCOL.md` for the
top-level framing, and `.github/ISSUE_TEMPLATE/falsification_report.md`
to file a refutation.
