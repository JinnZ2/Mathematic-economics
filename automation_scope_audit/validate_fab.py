"""
validate_fab.py — round-trip every claim in CLAIM_TABLE.fab.json through
schemas/claim_contract.Claim.from_dict / to_dict and report any failures.

Run:    python automation_scope_audit/validate_fab.py
Exit 0  every claim is contract-valid.
Exit 1  one or more claims failed validation; failures printed.

License: CC0-1.0
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schemas.claim_contract import Claim, CONTRACT_VERSION    # noqa: E402


FAB_PATH = os.path.join(HERE, "CLAIM_TABLE.fab.json")


def main() -> int:
    with open(FAB_PATH) as f:
        data = json.load(f)

    if data.get("contract_version") != CONTRACT_VERSION:
        print(f"WARNING: fab contract_version={data.get('contract_version')!r} "
              f"differs from schemas/claim_contract.CONTRACT_VERSION={CONTRACT_VERSION!r}")

    claims = data["claims"]
    allocation_enum = set(data.get("allocation_rules_enum", []))
    failures = []
    ok = []

    for cid, payload in claims.items():
        try:
            claim = Claim.from_dict(payload)
            # Round-trip
            roundtrip = Claim.from_dict(claim.to_dict())
            assert roundtrip == claim, f"{cid} round-trip mismatch"
            # Phase 8 Task 8.3: allocation_rule must be present + valid enum value
            if allocation_enum:
                ar = payload.get("allocation_rule")
                assert ar in allocation_enum, \
                    f"{cid} allocation_rule={ar!r} not in {sorted(allocation_enum)}"
            ok.append(cid)
        except Exception as e:
            failures.append((cid, str(e)))

    print(f"contract_version: {CONTRACT_VERSION}")
    print(f"claims validated: {len(ok)} / {len(claims)}")
    for cid in ok:
        print(f"  ok  {cid}")
    for cid, err in failures:
        print(f"  FAIL {cid}: {err}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
