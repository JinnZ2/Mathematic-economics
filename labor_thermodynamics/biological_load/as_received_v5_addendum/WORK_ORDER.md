WORK ORDER — ADDENDUM to v5, Mathematic-economics, branch biological-load-accounting
Engineered Stability doc, section "Bridge window": add inside BRIDGE, after "fuel_chain".
All figures from memory, NOT OPENED. Every value void until checked.

  "material_dependency": {     # PROPOSED; from memory, volume: thin
    "helium": {
      "use": "coolant, gas-cooled designs (e.g. Xe-100)",
      "chain": "Qatar ~1/3 world supply, ships via Hormuz (NOT OPENED)",
      "status": None,
    },
    "lithium_7": {
      "use": "enriched Li-7 for molten-salt designs (FLiBe)",
      "chain": "China, Russia main producers (NOT OPENED)",
      "status": None,
    },
    "nuclear_graphite": {
      "use": "moderator, TRISO fuel matrix",
      "chain": "China dominates synthetic graphite (NOT OPENED)",
      "status": None,
    },
    "zirconium_hafnium": {"use": "cladding; Zr/Hf separation", "chain": None, "status": None},
    "nickel_alloys": {"use": "high-temp structural, salt-facing", "chain": None, "status": None},
    "boron_10": {"use": "control, shielding", "chain": None, "status": None},
    "rule": "each material: source, share by country, choke point, refill rate, substitute",
    "derived": "new energy still rides old supply chains and the same geopolitics",
  },

CHECKER
- Voids: all status fields + zirconium_hafnium.chain, nickel_alloys.chain, boron_10.chain — void, never zero.
- Outside figures NOT OPENED: helium/Qatar share, Li-7 producers, graphite share.
- Report pass/fail, void count, strings not found in source.
Commit + push, no PR. Observer slots: null.
