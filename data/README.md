# data/ — Fetch and Compute

Fetches real economic data from public APIs and computes the 13 equations from the Mathematic-economics framework.

## Quick Start

```bash
# Set API keys (FRED required, BLS optional)
export FRED_API_KEY=your_fred_key
export BLS_API_KEY=your_bls_key    # optional — BLS v2 works without it

# Run
python data/fetch_and_compute.py
```

## Getting API Keys

| Source | Sign-up URL | Required? |
|--------|------------|-----------|
| FRED   | https://fred.stlouisfed.org/docs/api/api_key.html | Yes — needed for money supply and wealth data |
| BLS    | https://www.bls.gov/developers/home.htm | No — v2 API works without a key (rate-limited) |

## Data Sources

| Equation | Series / Source | What It Measures |
|----------|----------------|------------------|
| ER (Extraction Rate) | BLS PRS85006173 (labor share index) | Fraction of output not going to labor |
| UFR (Upward Flow Rate) | FRED WFRBST01134, WFRBSB50215 | Relative wealth accumulation: top 1% vs bottom 50% |
| MSI (Money Socialist Index) | FRED M2SL, CURRCIR | Government-origin fraction of money supply |
| MM (Money Multiplier) | FRED MULT | Fractional-reserve amplification factor |
| HHI (Market Concentration) | Published industry estimates | Market share concentration per industry |

Equations without accessible live APIs (VE/VL, SID, RI, DI, LWR, BSC, ISR, SD) use the illustrative values from README.md.

## Dependencies

Only the Python standard library and `requests`-compatible `urllib` (stdlib). No external packages required.
