# Investment Research Framework — Coal vs. Clean Energy Allocation

> **Historical research framework.** The assignment requires an explicit
> industry allocation judgment. The completed, scoped recommendation is in
> [deliverables/INVESTMENT_THESIS.md](../deliverables/INVESTMENT_THESIS.md).
> Missing valuation data limits security selection and return claims; it does
> not prevent a clearly labelled industry outlook judgment. Unsupported
> grid/causality claims below are addressed in the
> [project audit](../deliverables/PROJECT_AUDIT.md).

**Status:** framework + evidence matrix only. **No rating
(Outperform/Neutral/Underperform) is assigned anywhere in this document,
by design** — none of the three datasets contains valuation, financial, or
policy data, and a rating without that evidence would be fabrication.

The framework converts the verified findings
(`reports/research_findings.md`) into a testable research program:
hypotheses, the evidence that would support or kill each one, the data
still needed, and decision rules.

---

## 1. The decision problem, restated from the evidence

The central question ("replacement vs coexistence") does **not** resolve to
a global binary. Verified structure (findings F1–F7, F15):

- In **share** terms, clean is winning globally (38.8% → 43.8% of matched
  panel generation, 2020→2025); fossil generation peaked 2024, fell 2025.
- In **absolute** terms, coal volumes grew through 2024 and were ~flat in
  2025 (EI panel), carried by China/India coexistence and a US 2025
  power-sector rebound.
- Five distinct country pathways (transition / coexistence / coal_decline /
  mixed / coal_growth) — the portfolio question is therefore
  **market-segmented**, not global.

Consequences for the framework:
1. A single "coal" or "clean" factor bet is the wrong unit of analysis;
   the unit is **market × business model** (e.g. "US coal generation",
   "Asian-export coal", "Chinese utility mix", "global grid capex").
2. Every segment has a different verified trend and a different unknown
   (US: causality of the 2025 rebound; China: how long coexistence lasts;
   Europe: whether the decline accelerates).

## 2. Evidence matrix

Legend — **E**: evidence already in this repository (verified, from
`analysis/output/`); **N**: needed (not in the three datasets); the
"decision rule" states what would change the view.

### 2.1 Coal-exposed segments

| Segment | Verified evidence (E) | Open questions (N) | Decision rule |
|---|---|---|---|
| **US coal producers (domestic power coal)** | Sector-98 consumption 435.8M→373.3M st (2020→2024, −14.4%), then **+11.3% in 2025** to 415.4M; prices flat ($46.45→$45.56/st); industrial coal −6% YoY and declining since 2021 (F4, F12) | Cause of the 2025 rebound (outages? gas prices? load? data-center demand — F5); stockpile levels (state stocks missing); fleet retirement schedule; capex vs maintenance split | If the rebound cause is one-off (outages/inventory) → decline trend resumes → short-term volume risk for producers. If structural (load/gas) → re-rate the decline timeline. **Do not extrapolate either direction until F5 is resolved.** |
| **Asian-export coal producers** (Indonesia, Australia, etc.) | Production decoupled from domestic power demand: Indonesia production +48.2% vs gen +26.3% (2020→24); Brazil +12.4% vs −20.4% (F10); concentration: top-5 producers = 83.6% of world production | Import demand curves for India/China; seaborne prices vs domestic; policy (export taxes, mining royalties); thermal fleet additions in importing countries | Export exposure is a bet on **Asian import demand**, not on domestic retirements. Verify with trade/price data before treating "coal decline" theses as covering exporters. |
| **Coal-fired generators / utilities** | US coal gen 844.3→712.9 TWh (2020→24) then +12.8% in 2025; China 5,836 TWh (57.4% of world) still 54.4% of its own generation in 2025; India 71.2% (F2, F6) | Plant age/margin of coal units vs gas; emission compliance capex; contract structures; policy (IRA 45X, EU ETS costs); whether Chinese coexistence is policy-mandated or market-driven | Same-direction generation ≠ same economics: a generator's cash flow depends on the **merit-order position** of coal vs gas, which this dataset cannot see. |

### 2.2 Clean-energy segments

| Segment | Verified evidence (E) | Open questions (N) | Decision rule |
|---|---|---|---|
| **Wind + solar builders/developers** | Wind+solar generation 2,414→5,421 TWh (+124.5%, matched panel, 2020→25); YoY +18.1% in 2025, the fastest-growing measure; China +46% wind-solar 2024→25 (1,836→2,310 TWh); clean covered 109.9% of 2025 demand growth (F1, F11) | Module/turbine pricing and margins; interconnection queue lengths; supply-chain (polysilicon, neodymium) exposure; utilization/capacity factors (not in data); offtake vs merchant mix | Volume trend is verified and strong; **margin** is the unknown. The allocation case for this segment rests on cost data this project does not have. |
| **Nuclear** | US clean share 39.8→43.0% (2020→25) with coal −15.6% (2020→24) — displacement is not all wind/solar (F4, F6 panels); France clean 94.9% (matched 2024, F11 source table) | New-build pipeline and costs; SMR economics; utilization rates; regulatory cost of the 2025 US rebound if it displaces baseload nuclear | Baseload substitution for coal depends on nuclear availability in high-coal markets; verify US nuclear generation trend (not separately measured here). |
| **Hydro** | Matched-panel renewable growth +8.9% YoY 2025 (F1); S. America clean share 79.0% | Hydrology variability, drought risk — not in data | Treat as stable-but-weather-dependent; not a growth driver on the verified record. |

### 2.3 Adjacent segments the thesis forces us to watch

| Segment | Verified evidence (E) | Open questions (N) | Decision rule |
|---|---|---|---|
| **Grid / T&D** | Demand growth outpaced clean growth in 2021–2024 on the matched panel (clean covered 74–77% of demand growth each year; only 2025 exceeded 100%, F1) | Capex guidance, transmission constraint data, load-forecast revision — not in data | Every year through 2024, demand grew faster than clean; the grid is the bottleneck segment for the *pace* of displacement. Grid capex is the most regime-proof leg of a clean transition portfolio. |
| **Gas** | US total fossil +120.6 TWh (2020→24) while US coal −131.4 TWh (F8 note) — gas took coal's place in US generation | Gas price path; gas-to-coal switch economics in the 2025 rebound; LNG export capacity | The 2025 US coal rebound is economically coherent **only if** gas was unavailable/expensive at the margin — the prime hypothesis to test (F5). If gas prices stay structically higher, coal rebound support is stronger. |
| **Coal-transition-exposed utilities** (high-coal-balance-sheet) | US/India/Indonesia/Russia/China carry 54–74% coal generation (F6, F7) | Leverage, dividend cover, fleet-mix options, cost of capital | These are the "coal decline tail-risk" holders; the allocation risk is their balance sheet, not the generation trend. Needs financials (N). |

## 3. Research hypotheses (testable, with kill criteria)

1. **H-US:** The 2025 US coal rebound is demand-driven (load/gas), not
   one-off (outages/inventory).
   *Test:* EIA weekly generation cause analysis; gas price series
   2024–2025; stockpile data; 2026 monthly coal consumption vs load.
   *Kill:* if 2026 consumption reverts to the 2022–2024 trend line
   (≈ −8%/yr from the 2021 peak) while load keeps growing → one-off.
2. **H-CN:** China coexistence is policy-sustained (dual growth for ≥3 more
   years), not a temporary grid-reliability buffer.
   *Test:* announced 5th/6th 5-year-plan clean targets vs actual
   additions; new coal plant approvals; provincial RPS.
   *Kill:* first calendar year in which Chinese coal *generation* declines
   >5% YoY while demand grows → coexistence ending.
3. **H-GLOBAL:** Global fossil generation has durably peaked (2024/2025).
   *Test:* 2026 Ember full-year + EI revised 2025.
   *Kill:* 2026 matched-panel fossil generation > 16,716 TWh.
   *Caveat:* 2025 is provisional in both sources (F14) — this hypothesis is
   on watch, not decidable, until the next publication cycle.
4. **H-EXPORT:** Export-oriented coal producers' volumes track Asian import
   demand, insulating them from domestic-retirement theses.
   *Test:* seaborne coal price vs Indonesia/Australia production; India
   thermal additions.
   *Kill:* 2026 seaborne price decline >20% despite flat Asian demand
   (oversupply) → the insulation fails.

## 4. Data still needed (explicit list — nothing here is a substitute)

| Category | Items | Suggested sources |
|---|---|---|
| **Valuation** | EV/EBITDA, P/B, price-to-book by segment; index weights; market caps | provider data (not in this repo) |
| **Financials** | capex (growth vs maintenance), FCF, leverage, dividend cover, margins by fuel | 10-K / annual reports |
| **Power economics** | gas price path (Henry Hub, Asian JKM), coal index prices (Newcastle, API2), LCOE by technology, capacity factors, merit-order data | EIA STEO, Argus, IRENA LCOE |
| **Policy** | IRA 45X/45Y parameters, EU ETS price, China 5-year plan, state retirement mandates | government publications |
| **Fleet** | plant ages, retirement/addition pipelines, emission compliance costs | EPRI, national grid reports |
| **Trade** | coal import/export flows by country pair | UN Comtrade, BMI |
| **System** | interconnection queues, grid investment, load forecasts (incl. data centers) | FERC, national TSO reports |

## 5. Decision rules and process

1. **No rating without the evidence matrix row being filled.** A segment
   earns an Outperform/Neutral/Underperform view only when its "N" column
   has been answered by sourced data and the decision rule is evaluated.
   Until then the correct state is "under research", which is itself a
   reportable result.
2. **Market-segmented positions:** any allocation view must name the
   market (US / China / India / rest-of-Asia / Europe / global) and the
   business model (producer / generator / developer / grid). A global
   "long clean, short coal" statement is out of spec — the verified data
   shows the two are not uniformly opposite (F2, F7).
3. **2025-gating:** every view that depends on 2025 figures (the US
   rebound, the global peak) is provisional until the next Ember/EI/EIA
   release (F14). The framework schedules a re-run of `analysis/` at each
   release; the pipeline is deterministic, so numbers are comparable.
4. **Concentration rule:** top-5 producers = 83.6% of world coal
   production (F9). Any coal exposure is, in practice, concentrated
   exposure to 3–5 countries; sizing must reflect that, not a diversified
   "coal industry" assumption.
5. **Causality before trend-extension:** the US 2025 rebound (F4/F5) must
   have a verified cause before any multi-year coal demand path is
   extended from it. Until then, US coal models carry two branches
   (one-off vs structural) with explicit probabilities, not a point
   forecast.

## 6. What this framework deliberately does NOT do

- No machine-learning forecasting (excluded by the engagement brief; the
  2025 data is provisional, so any model trained on it would be fitting
   to noise — and the brief forbids starting ML work tonight regardless).
- No price targets, no ratings, no position sizes.
- No imputation of missing values (e.g. EIA state stocks, 2021 prices) —
  missing stays missing and is flagged.
