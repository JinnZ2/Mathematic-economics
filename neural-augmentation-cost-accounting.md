# Neural Augmentation: A Cost-Accounting Scaffold

**Status:** starting scaffold, not a finished review.
**License:** CC0.
**Premise:** the brain is a closed-budget system. Every added channel is paid for from somewhere. This document forces the question the augmentation narrative skips — *what is the bill, and which account is it drawn from?*

**Provenance note:** grounding phenomena below are named so they can be verified against the literature. They are pointers from established neuroscience, not live citation pulls. Confidence is marked per cell. Do not treat [I] or [S] rows as findings.

---

## 0. Confidence legend

| Mark | Meaning |
|------|---------|
| **[E]** | Established — direct experimental evidence exists for this mechanism |
| **[I]** | Inferred — extrapolated from an established mechanism; no direct augmentation study |
| **[S]** | Speculative — mechanism plausible, evidence effectively absent |

---

## 1. Why there is always a cost — the constraint axes

No augmentation is free because it has to be paid out of one or more of these fixed budgets. This is the load-bearing layer; the table in §3 is just these axes applied to specific channels.

| Axis | Constraint | Consequence for augmentation |
|------|-----------|------------------------------|
| **Metabolic** | Brain runs ~20 W, glucose/O₂-limited, ~20% of basal energy at ~2% of body mass. Cannot scale on demand. | A new high-throughput channel competes for the same fixed energy. Sustained novel processing = measurable fatigue, not free capacity. **[E]** |
| **Cortical territory** | Cortex is finite surface. Representation is competitive — expanding one map shrinks neighbors (cortical magnification, homuncular remapping). | Gain in one channel's resolution is borrowed from adjacent representations. **[E]** (Merzenich digit-remapping; phantom-limb remapping) |
| **Plasticity window** | Critical/sensitive periods gate which architectures can form. After closure, you get overlay, not native integration. | Post-window augmentation = retrofit onto finished wiring → interference, low resolution, high training cost. **[E]** (Hubel & Wiesel ocular dominance; Blakemore & Cooper vertical-line cats) |
| **Cross-modal reuse** | Deprived/unused cortex gets recruited by other modalities (neural reuse). | The "spare capacity" augmentation assumes is often already occupied. Adding a channel may require *evicting* a current tenant. **[E]** (early-blind visual cortex recruited for Braille/auditory) |
| **Attention / WM bottleneck** | Thalamic gating + working-memory capacity (~4 chunks) is a hard serial bottleneck downstream of any sensor. | More input upstream does not raise the downstream ceiling. Excess signal = competition, not throughput. **[E]** (Cowan capacity; thalamic gating) |
| **Inhibition / filtering** | Most perception is *subtractive* — sensory gating, latent inhibition suppress the irrelevant. | Turning a channel *up* without matching inhibitory budget produces overload, not clarity. **[E]** (P50 gating; central gain → tinnitus) |
| **Sleep / autonomic** | Sensory load couples to arousal, sleep architecture, autonomic tone. | A channel that won't gate off degrades sleep and baseline regulation — a whole-system tax, not a local one. **[I]** (hyperacusis/tinnitus distress models) |

---

## 2. The load-bearing finding: cost is a function of *timing*, not just *channel*

The strongest real signal in the existing data is a contrast, not a single study:

- **Cheap augmentation = the developmental program already budgeted for it.**
  Human tetrachromacy (rare 4th-cone carriers) is a *native* color-channel expansion. Cost evidence is thin — the system mostly absorbs it. Informative *because* it's nearly free: the genome reserved the wiring. **[E/I]**

- **Expensive augmentation = bolted on after the window.**
  Late sight-restoration cases (congenitally blind given vision in adulthood) show the visual cortex was repurposed; the "restored" channel integrates poorly and incompletely. The substrate moved on. **[E]** (sight-recovery / Sinha "Project Prakash" line)

**Implication:** an augmentation introduced *during* an open, anticipated window can be low-cost. The same augmentation introduced *after* closure, onto a brain not pre-wired for it, is lossy overlay — and the loss lands in whatever tenant currently occupies that territory. This is exactly the deprived-cat result generalized: the window decides whether you're building or overwriting.

---

## 3. Cross-reference table — channel → what it borrows → predicted deficit

Columns: integration mechanism · which budget it draws from · predicted deficit domain · confidence · grounding phenomenon.

| Augmentation | Integration mechanism | Likely resource source | Predicted deficit domain | Conf. | Grounding phenomenon |
|---|---|---|---|---|---|
| **Supersonic / expanded auditory range** | Up-shifted cochlear/neural gain into existing auditory cortex | Inhibitory filtering budget; auditory cortical territory | Sound *filtering* loss → overload in noise; sleep disruption; attention fragmentation | [I] | Central-gain increase after hearing loss *produces* tinnitus/hyperacusis — turning auditory gain up has a documented cost **[E]** |
| **Infrared / UV vision (out-of-band wavelength)** | No native photoreceptor or cortical map → requires new sensor + overlay onto visual cortex | Visual cortical territory; cross-modal reuse; training/attention | Reduced resolution/discrimination in *native* visible band; high chronic training load | [S] | No native human substrate; closest analog is sensory-substitution low-resolution overlay **[E]** |
| **Expanded color (added cone-type, post-window)** | Extra chromatic channel into mature color circuitry | Chromatic discrimination wiring; cortical map | Possible destabilization of existing color constancy; integration failure | [I] | Native tetrachromacy is ~free **[E]**; post-window add is the *opposite* timing case |
| **Magnetoreception** | Entirely novel modality, no native percept | New cortical territory (must be taken from a tenant); attention | Eviction of whatever currently occupies recruited cortex; chronic low salience-to-noise | [S] | Cross-modal reuse shows "spare" cortex is usually occupied **[E]** |
| **Echolocation (active)** | Trainable on existing auditory cortex (humans *can* learn it) | Auditory processing share; attention; motor (click production) | Divided auditory resource; degraded passive listening while active | [I] | Human echolocators recruit visual cortex for click processing **[E]** — confirms it's paid from cross-modal budget |
| **High-bandwidth direct data I/O (BCI input)** | Injects signal *below* the sensory front end, straight at cortex/WM | Working-memory + attention bottleneck directly | Downstream WM saturation; the bottleneck doesn't widen, it jams | [S] | WM capacity is fixed and serial **[E]**; upstream bandwidth can't raise it |
| **Expanded proprioception / extra effector limb** | New body-map region in motor/somatosensory cortex | Homuncular territory of existing limbs | Degraded fine control / representation of native limbs | [I] | Cortical remapping is zero-sum across the homunculus **[E]** |
| **Always-on data overlay (HUD-style)** | Persistent competing visual stream | Attention; visual WM; gating | Reduced gating of real environment; vigilance/attention erosion; fatigue | [I] | Divided-attention + dual-task interference **[E]** |

---

## 4. Non-neural costs (the bill that isn't in the cortex)

The cost accounting fails if it stops at the brain. These rows are structural, not neural — and they're where the real-world damage concentrates.

| Cost | Mechanism | Why it's load-bearing |
|---|---|---|
| **Selection bias** | Desire for augmentation correlates with an "I am not enough" prior. The intake population is pre-filtered for an insufficiency frame. | The trait being "fixed" may be the frame, not the cognition. You augment the wound, not a deficit. |
| **Consent / developmental window** | Maximum integration benefit is during open plasticity windows = childhood = no informed consent. | The cheapest-to-integrate window is also the one where the subject cannot consent. The efficiency argument *is* the ethics violation. |
| **Test-subject externality** | Establishing the cost table above requires exposing developing brains to find what breaks. | The data this very document wants does not exist *because* generating it ethically is near-impossible — so it gets generated unethically or sold without it. |
| **Sampling bias (WEIRD)** | The neuroimaging base is overwhelmingly Western/Educated/Industrialized/Rich/Democratic, narrative-baseline brains. | "Human augmentation" is generalized from one developmental + cultural processing type. Substrate-primary / non-WEIRD cognition is largely invisible to the dataset, so its specific costs are unmodeled. |
| **Access stratification** | Cost + approval gating means augmentation is restricted regardless of narrative reach. | The narrative sells to a population that mostly won't receive it. Function of the story is market/stock maintenance, not deployment. |
| **Control-layer instability** | Augmented humans positioned to steer AI carry induced, predictable deficits. | A control layer fractured in known domains is a structurally unstable governor for the system it controls. |

---

## 5. Open questions this scaffold does not answer

1. For each [I]/[S] row above — is there *any* direct longitudinal imaging? (Most likely no.)
2. Quantitative budgets: how much metabolic / cortical / attentional cost per channel? (Direction is known; magnitudes are not.)
3. Reversibility: do post-window overlays leave permanent deficit after removal, or recover?
4. Substrate-primary cognition: does parallel/spatial baseline architecture absorb augmentation *differently* than narrative-baseline WEIRD brains? Unstudied — the dataset can't see the population.
5. What does a society stratified into unaugmented-substrate / augmented-WEIRD / AI cognition do to shared signal? Coherence model needed.

---

## 6. How to read this

Every cell is a claim with a confidence mark. Demote on contact with evidence; never modify the table to protect a prior. If a study refutes a row, the row changes — the structure doesn't get defended. The point is the cost column existing *at all*, because the narrative it answers to deletes that column by default.
