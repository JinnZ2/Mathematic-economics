WORK ORDER — Mathematic-economics, branch biological-load-accounting
File as v3 (third delivery). Keep v1 and v2 untouched; keep records_v2.json beside the new records.
Source: two Claude Docs, edited live; text below is authoritative for the changes.

CHANGE 1 — Decision-Exposure Coupling, section "Provenance fields for any input"
Replace the whole PROVENANCE code block with:

PROVENANCE = {
  "lived_firsthand": None,     # bool — the gate: lived it vs wrote about it
  "role_type": None,           # cab / floor / ward / classroom / field, with sub-role
  "conditions": None,          # exposed (real routes/shifts, own needs) | sheltered (family firm, hand-picked loads)
  "compensation_basis": None,  # market pay | family / insider pay
  "current_seat": None,        # floor / cab | office | media | academia
  "recency": None,             # years since exposure
  "learning": None,            # organizing the work; individual — 1 yr for some, 5 for others
  "endurance": None,           # how long sustained at full exposure
  "maintenance": None,         # how well biological needs were kept up over that span
  "diversity": None,           # range of conditions juggled: roles, seasons, regions, incidents
  # time measures different things; no single years threshold
  # years != experience (20 yrs in school != a PhD's work)
  # authority judged per dimension, not as one score
}
# office seat writing about the floor = DERIVED at best, never OBSERVED
# CANONICAL: PROVENANCE and FALSE_DENOMINATOR are defined here; companion docs point here

CHANGE 2 — Biological Load Accounting for Truck Drivers, BUFFER_INTRUSION.false_denominator
Replace:  "fix": "same rules, same conditions, same metrics on both sides before comparing",
With:     "fix": "canonical in Decision-Exposure Coupling",
(definition, status, fix now all point to the coupling doc)

README
- Close open item "v1 PROVENANCE content dropped in v2" — restored in v3 (CHANGE 1).
- Wording note: "exposed (real routes, ...)" became "exposed (real routes/shifts, ...)" to cover all roles.
- Keep open: ROLE vocabulary (11/13 outside four states; 3 compound statuses unmapped),
  responsibility_h mixed types, true_cost NOT_COMPUTABLE, 9 outside figures NOT OPENED.

CHECKER
- Rerun all checks on v3; confirm the 3 truck-doc pointers resolve, voids recount, hashes for v1/v2/v3 hold.
- Report: pass/fail counts, void count, any string in records not found in source text.
Commit + push, no PR. Observer slots: null.
