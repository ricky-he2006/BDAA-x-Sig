# Research Findings — Coal vs. Clean Electricity, 2020–2025

> **Historical research draft — superseded for submission.** Use
> [the audited evidence and corrections](../deliverables/PROJECT_AUDIT.md),
> [claim lineage](../deliverables/tables/claim_evidence.csv), and
> [investment thesis](../deliverables/INVESTMENT_THESIS.md).
> This draft contains inconsistent fuel/panel labels and unsupported causal
> interpretations identified in that audit; do not quote it as the final analysis.

**Central question:** *Is clean electricity replacing coal worldwide, or is
growing electricity demand allowing both to coexist — and what does that
imply for allocating capital between the coal and clean-energy industries?*

Neither answer is assumed. Every finding below is tagged:

- **[verified]** — computed directly from the cleaned/processed tables in
  `data/` by the scripts in `analysis/` (rerunnable; outputs in
  `analysis/output/`).
- **[interpretation]** — a reading of verified numbers; the arithmetic is
  right, the conclusion is mine.
- **[hypothesis]** — a causal or forward-looking claim the data does **not**
  establish; flagged as requiring external evidence.

## Data basis (read first)

| Source | What it provides | 2025 status |
|---|---|---|
| Ember `country_year_electricity_2020_2025.csv` | electricity demand/generation by fuel, 213 countries 2020–2024 | **2025 covers only 91 countries — partial panel, not comparable to 2020–2024 totals** |
| EIA US coal quality series | US state-level coal by sector (base sectors {1,2,3,8,9,10}); aggregates 94/98 separate | preliminary |
| Energy Institute *Statistical Review of World Energy* | country-level coal production (Mt), coal TES (EJ), coal-fired generation (TWh), 109 listed countries + 32 regional aggregates | **estimates, subject to revision** |

Two structural caveats apply to every global number:

1. **The EI "world proxy"** = sum of the 109 *listed* countries. It is a
   **lower bound**: the EI "Other X" aggregates contain countries not listed
   individually. 2024 gap vs EI's own "Total World" row: 1.7%
   (production 8,901.1 vs 9,057.0 Mt; generation 10,167.0 vs 10,569.7 TWh).
   Closing the gap by adding the aggregates back would **double-count**
   (they contain the listed countries) — so the gap is disclosed, not
   closed. (See Finding 16 for the correction that makes this possible.)
2. **Matched vs full panels.** Ember trends use the 91-country *matched*
   sample (present every year 2020–2025) so changes are apples-to-apples;
   the full-panel 2025 row is **not** used for trends.

---

## Findings, ranked by importance to the central question

### 1. Global fossil generation peaked in 2024 and fell in 2025 — on the Ember matched panel. **[verified]**

91-country matched panel (identical country set every year):

| Year | Fossil gen (TWh) | Clean gen (TWh) | Wind+solar (TWh) | YoY fossil | YoY clean |
|---|---|---|---|---|---|
| 2020 | 15,210.06 | 9,661.04 | 2,414.42 | — | — |
| 2024 | **16,715.95 (peak)** | 12,082.85 | 4,591.50 | +1.63% | +8.40% |
| 2025 | **16,619.99** | 12,953.21 | 5,420.83 | **−0.57%** | +7.20% |

In 2025 clean generation grew +7.20% while demand grew +2.75% — clean
covered **109.9% of demand growth**; fossil fell.

*Contradictory evidence:* Finding 3 — the EI country-level panel does **not**
show a 2025 global decline. The two datasets point opposite directions in
2025; see Finding 2 for the resolution.
*Source:* `analysis/output/research_a_global_electricity.md` (matched sample, YoY).

### 2. The 2025 picture is a regional reshuffle: US-led coal rebound, partly offset by China and India declines. **[verified]**

EI country-level coal-fired generation, 2024 → 2025 (TWh):

| Country | 2024 | 2025 | Δ |
|---|---|---|---|
| United States | 712.9 | 804.1 | **+91.2** |
| China | 5,836.4 | 5,755.9 | **−80.5** |
| India | 1,513.5 | 1,464.2 | **−49.3** |
| World (109 listed) | 10,167.0 | 10,125.3 | **−41.8 (−0.4%)** |

The three largest coal generators together net −38.6 TWh, matching the
order of the global change. **The world total barely moved in 2025; the US
rebound (Finding 4) was substantially offset by declines in China and
India.** This is why the two panels (Findings 1 and 3) disagree: the Ember
matched panel (which includes many European decliners) shows the fall; the
EI country panel, dominated by Asia + the US, is nearly flat.
*Source:* `analysis/output/research_d_cross_country.md` (per-market panels);
`analysis/output/research_b_coal_market.md` (world proxy).

### 3. Coal in absolute terms still grew over 2020–2025 worldwide. **[verified]**

EI country-level world proxy (109 listed countries):

| | 2020 | 2024 | 2025 | 2020→2024 |
|---|---|---|---|---|
| Coal-fired generation (TWh) | 9,096.3 | 10,167.0 | 10,125.3 | **+11.8%** |
| Coal production (Mt) | 7,521.1 | 8,901.1 | 8,891.5 | **+18.2%** |
| Coal TES (EJ) | 148.3 | 162.7 | 163.4 | +9.7% |
| Coal share of all generation | 38.50% | 36.95% | 35.78% | −2.7 pp |

So the honest summary is: **coal's share is falling everywhere; coal's
absolute volumes rose through 2024 and were roughly flat in 2025 on the EI
panel / down 0.57% on the Ember matched panel.** "Replacement" is true in
share terms; "coexistence" is true in absolute terms.
*Caveat:* EI 2025 = estimates; the flat 2025 world total is within
estimation noise.
*Source:* `analysis/output/research_b_coal_market.md` (world proxy + ground-truth check).

### 4. US coal: multi-year decline, then a 2025 rebound of +11.3% led by the power sector. **[verified]**

EIA US electric-power (sector 98) coal consumption:
435.8M short tons (2020) → 501.4M (2021) → 472.8M (2022) → 387.2M (2023) →
**373.3M (2024) → 415.4M (2025, +11.29% YoY)**.

Sector decomposition of the rebound (US level, YoY 2024→2025):

| Sector | Δ 2024→2025 |
|---|---|
| 98 electric power | **+11.3%** |
| 94 IPP | +10.8% |
| industrial base (sectors 8,9,10) | **−6.0%** |

**The rebound was power-sector; industrial coal kept declining.**
State attribution (share of the measurable total change): IN +4.06M st
(10%), KS +3.73M (9%), MO +3.72M (9%), IA +2.75M (7%), AR +2.42M (6%),
IL +2.32M (6%); offsets CO −1.51M, ND −1.13M. TX remains the largest state
(48.9M st, 2025). Delivered prices were flat (98: $46.45 → $45.56/st;
94: $38.37 → $38.28/st), so the rebound was volume-led, not price-led.
*Caveat:* EIA state electric-power stocks are all missing (data gap), so
the stockpile channel cannot be checked from this dataset.
*Source:* `analysis/output/research_c_us_coal.md`.

### 5. **Hypothesis** — why the US rebounded. The data shows *that*; not *why*.

Candidate explanations that **require external evidence** (none are in the
three datasets): generator outages/maintenance backlogs, gas price
movements, delayed nuclear or coal retirements, load growth (data centers /
industrial electrification), or weather. Any of these would need to be
checked against grid-operator reports, EIA weekly data, and fuel price
series before it could be treated as verified. *Do not cite the rebound as
evidence of demand-driven coal growth until the cause is established.*

### 6. Coexistence is concentrated in Asia: China and India grew BOTH clean and coal, 2020→2024. **[verified]**

| Country | Clean gen 2020→2024 | Coal gen 2020→2024 | Clean share 2020→2025 | Coal share 2020→2025 |
|---|---|---|---|---|
| China | 2,551.2 → 3,849.7 TWh (+50.9%) | 4,931.0 → 5,836.4 TWh (+18.4%) | 32.8% → 41.6% | 63.4% → 54.4% |
| India | 341.8 → 458.1 TWh (+34.0%) | 1,143.8 → 1,513.5 TWh (+32.3%) | 21.9% → 26.7% | 72.8% → 71.2% |

China adds more clean capacity than anyone while **still adding coal
generation**; India adds coal faster than it adds clean. China alone is
**57.4% of world coal-fired generation and 51.6% of world coal production
(2024)** — the global coexistence question is substantially *the* China
question. China's combustion CO2 still rose in 2025 (11,169.3 → 11,220.4 Mt)
even as its carbon intensity fell (556.3 → 526.2 g/kWh).
*Source:* `analysis/output/research_d_cross_country.md`; `research_b_coal_market.md`.

### 7. The transition is not one story: 16 material countries fall into five different pathways. **[verified]**

2020→2024, countries with a material coal AND clean base in both years
(16 of 213; threshold >5% change):

| Pathway | n | Countries |
|---|---|---|
| transition (clean up, coal down) | 7 (43.8%) | USA, JPN, KOR, POL, THA, AUS, ZAF |
| coexistence (both up) | 5 (31.2%) | CHN, IDN, IND, TUR, VNM |
| coal_decline (coal down, clean not up) | 2 (12.5%) | DEU, TWN |
| mixed | 1 (6.2%) | MYS |
| coal_growth (coal up, clean not up) | 1 (6.2%) | RUS |

The seven named benchmark markets: Australia = coal_falling_clean_rising;
USA = coal_falling; Germany = coal_falling (demand also fell −5%);
Japan = mixed (coal −5%, clean +35% on flat demand); China = coexistence;
India/Indonesia = coal_growing; Russia = coal_growing (clean flat).
*Source:* `analysis/output/d_allcountry_pathway_2020_2024.csv`;
`research_d_cross_country.md` (excluded countries are listed in that CSV,
not silently dropped).

### 8. Who drove the 2020–2024 global fossil mix: a handful of decliners vs. a handful of growers. **[verified]**

Ember matched panel, fossil generation change 2020→2024 (TWh):
declines — Japan −76.6, Germany −45.8, Netherlands −28.4, UK −26.8,
Italy −26.6, Spain −22.0, France −19.7, Australia −18.0;
increases — **China +1,009.3, India +356.8, Russia +121.5, USA +120.6**,
Iran +61.4, Egypt +36.0.
The two biggest increases are in Asia. Note: the US +120.6 TWh is total
*all-fossil* generation on the Ember panel (gas + coal + others); US
*coal-fired* generation **fell** 844.3 → 712.9 TWh (2020→2024, EI basis,
Finding 4) — gas and other fuels displaced part of the coal. Do not
conflate the two measures.
*Source:* `analysis/output/research_a_global_electricity.md`.

### 9. Concentration: top-5 producers hold 83.6% of world coal production; top-5 generators hold 84.5%. **[verified]**

2024, world proxy: China 4,595.7 Mt (51.6%), India 1,085.1 (12.2%),
Indonesia 836.1 (9.4%), US 465.0 (5.2%), Australia 463.5 (5.2%) →
top-5 = 83.6%. Generation: China 5,836.4 TWh (57.4%), India 1,513.5 (14.9%),
US 712.9 (7.0%), Japan 300.6 (3.0%), Indonesia 228.4 (2.2%) → 84.5%.
*Implication (interpretation):* the global coal trajectory is decided by
3–5 countries; a global "coal vs clean" bet is really a bet on China,
India and the US.
*Source:* `analysis/output/research_b_coal_market.md`.

### 10. Exporters decouple production from power demand — Brazil and Indonesia are the clearest cases. **[verified]**

2020→2024: Brazil coal production +12.4% (7.06 → 7.94 Mt) while coal
**generation** −20.4% (17.75 → 14.13 TWh). Indonesia production +48.2%
(563.7 → 836.1 Mt) vs generation +26.3% — production running well ahead of
domestic power use, i.e. export/non-power demand. No material country shows
the reverse (importer) pattern in 2020→2024.
*Implication (interpretation):* for coal-exposed capital, the relevant
demand question differs by business model: export-oriented producers are
exposed to Asian import demand, not domestic power retirements.
*Source:* `analysis/output/research_b_coal_market.md` (divergence tables).

### 11. Carbon intensity and clean share keep improving even where coal volumes grow. **[verified]**

Matched panel carbon intensity: 486.8 (2020) → 490.7 (2021) → 484.7 →
477.9 → 465.5 (2024) → **451.5 gCO2e/kWh (2025)**, −7.2% over the window.
Clean share of generation: 38.84% → 43.80% (2020→2025). By continent
2020→2025: Asia 28.7→36.4%, Africa 16.2→22.6%, Oceania 32.2→45.2%,
Europe 57.9→62.1%, N. America 44.2→45.9%, S. America 73.1→79.0%.
Even in coal-growing countries the mix improves: China 32.8→41.6% clean
(Finding 6). *Interpretation:* "clean share" and "coal volume" are
separable axes; an allocation model should track both, not assume one
implied the other.
*Source:* `analysis/output/research_a_global_electricity.md`;
`research_d_cross_country.md`.

### 12. US prices were flat through the rebound — no price signal yet. **[verified]**

EIA delivered coal price: sector 98 $36.13 (2020) → $46.45 (2024) →
$45.56 (2025); sector 94 $31.92 (2020) → $38.37 (2024) → $38.28 (2025).
2021 prices are missing (not reported — not zero). The 2025 volume rebound
did not move delivered prices; *interpretation:* either the marginal
demand was inventory-elastic or prices were sticky; a sustained demand
shift would be expected to show in prices within a year.
*Caveat:* one year of flatness is not evidence of equilibrium.
*Source:* `analysis/output/research_c_us_coal.md`.

### 13. US receipts vs consumption: inventories moved in 2023 and 2025. **[verified, limited]**

State-level base-sector receipts vs consumption: 2023 receipts exceeded
consumption by +38.4M st (stockpiling year), 2025 receipts trailed by
−25.5M st (drawdown consistent with the consumption rebound). EIA state
electric-power *stocks* are entirely missing, so this is the receipts
proxy only. *Hypothesis:* the 2025 rebound consumed 2023-built stocks —
testable against EIA stockpile data not in this dataset.
*Source:* `analysis/output/research_c_us_coal.md` (receipts table).

### 14. 2025 is provisional in every source — all 2025 findings are conditional. **[verified caveat]**

Ember 2025: 91 of 213 countries (partial panel). EI 2025: Statistical
Review estimates, subject to revision. EIA 2025: preliminary. The 2025
rows in every table are the only year with this status; 2020–2024 are
published final values. **No 2025-dependent conclusion should be treated
as settled until the next publication cycle.**

### 15. **Interpretation** — the central question resolves to a market-level answer, not a global one.

Verified facts: (a) fossil generation peaked globally on the matched
panel (F1); (b) absolute coal volumes grew 2020–2024 and were flat 2025 on
the EI panel (F3); (c) the five pathways cover all 16 material countries
(F7); (d) the rebound/decline offset structure (F2). *Conclusion:* "clean
is replacing coal" is true for ~44% of material countries (transition)
and in *share* terms globally; "coexistence" is true for ~31% and in
*volumes* for the Asia-dominated world. **Capital allocation should
therefore be structured market-by-market (China / India / US / rest-of-Asia
/ Europe) rather than as a single global coal-vs-clean position**, and the
US position needs the Finding 5 causality before any trend extension.

### 16. **Verified data-quality corrections made while producing these findings** (material to every number above).

- **EI aggregate double-counting (fixed at the cleaning stage).**
  `is_aggregate` previously flagged only 7 vendor codes, so 22 EI regional
  aggregates ("Total World", "Total Asia Pacific", "Other Middle East", …)
  leaked into every country-level sum: the world coal production proxy was
  **36,476 Mt instead of the correct ~8,901 Mt (4.1× inflation)**, and
  "Total World" itself appeared *as a top producer* in Research B
  outputs. The flag now marks all `O-*/T-*/WLD/ROW` codes; corrected
  outputs regenerated; regression tests added
  (`tests/test_ei.py::test_aggregates_separated`,
  `test_country_sum_excludes_all_aggregates`).
- **ISO 3166 reference rebuild (fixed at the reference-module stage).**
  `ISO3_OFFICIAL` silently omitted ≥14 real codes (ESP, USA, ZAF, CHL,
  CAN, BRB, YEM, TCD, LKA, SSD, DOM, ASM, BMU, GRD, GLP, GNB, …) and
  contained invalid entries (CCA, CXA, FXY, MYT, MNR, VCU) and duplicates.
  Rebuilt to 243 codes; vendor variants (SUN, ANT, NRU) moved to
  `ISO3_NONISO_ACCEPTED`; the pipeline's residual check now surfaces any
  future unadjudicated code as an audit warning. Tests: `tests/test_iso.py`.
- Both fixes re-ran the full pipeline deterministically; cleaning log now
  0 errors, 248 warnings (all flags, none acted on by dropping);
  0 duplicate cells in any dataset.

---

## What the data does NOT tell us (explicitly out of scope)

1. **Valuation and financials** — no market prices, multiples, capex,
   balance sheets, or dividend data in any of the three sources. Any
   Outperform/Neutral/Underperform call requires data not present here
   (see `reports/investment_research_framework.md`).
2. **Causality of the 2025 US rebound** (Finding 5).
3. **Renewable intermittency / capacity factors / system cost** — the data
   measures generation (TWh), not cost or reliability.
4. **Coal export flows** — inferred from production-vs-generation gaps
   (Finding 10), not from trade data.
5. **Policy** — no policy variables in the data; retirement mandates,
   subsidies, and carbon prices must be sourced externally.

## Contradictions surfaced (flagged, never force-matched)

- **2025 direction:** Ember matched panel fossil −0.57% vs EI country
  panel −0.41% (coal gen only) — same sign, different magnitude; the
  earlier apparent contradiction (Ember down vs "global up") resolves to
  panel composition (F1/F2/F3).
- **US 2020→2024:** Ember total fossil generation for the US **rose**
  (+120.6 TWh) while US coal generation **fell** (−15.6%) — gas/others
  displaced coal; the measures are distinct and both are correct.
- **EIA vs EI for the US:** EIA sector-98 2024→2025 consumption +11.29%
  (short tons) vs EI US coal generation +12.8% (TWh) — consistent
  direction and magnitude, different units; no discrepancy.
