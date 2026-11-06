"""Write the investment memo from the same audited metrics as the pitch."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "submission"


def build_memo(m):
    clean = m['clean_growth_2020_2024_pct']
    fossil = m['fossil_growth_2020_2024_pct']
    decline = abs(m['us_coal_2020_2024_pct'])
    rebound = m['us_coal_2025_yoy_pct']
    thesis = f"""# Investment thesis: own clean growth; keep the coal call regional

**Decision date: 6 November 2026 · Horizon: November 2026–November 2029**

## Recommendation to the investment committee

**Overweight clean energy, expressed through diversified low-carbon generation owners. Underweight coal, with the strongest expression in U.S. domestic thermal-coal producers.** These are relative industry preferences against neutral policy weights within an energy allocation. The evidence supports greater conviction in the direction of clean-generation growth than in the timing of coal's decline. It does not establish expected stock returns or justify numerical position sizes.

Our central argument is that clean growth and coal resilience can coexist. On the fixed {m['panel24_n']}-country Ember panel, clean generation rose **{clean:.1f}%** in 2020–2024 while all-fossil generation rose **{fossil:.1f}%**. A clean-energy allocation therefore need not depend on an imminent worldwide coal collapse. The coal underweight rests on a narrower observation: U.S. power-sector coal consumption fell **{decline:.1f}%** through 2024. Its **{rebound:.1f}% rebound in 2025** is a material challenge to that judgment, and limits conviction. [E01–E05]

The portfolio implication is selective exposure to generation growth, accompanied by explicit tests of investment economics and coal-demand persistence. A growing industry is the starting point for diligence; valuation, cash flow and financing must determine which securities deserve capital.

## 1. What the underlying data establishes

| Observation | Evidence | Investment interpretation |
|---|---|---|
| Clean output grew faster than all fossil | Fixed Ember panel, 2020–2024: +{clean:.1f}% versus +{fossil:.1f}%; clean share {m['clean_share_2020_pct']:.1f}% → {m['clean_share_2024_pct']:.1f}%. [E01–E02] | Supports a preference for participation in clean-generation growth. Does not demonstrate equity outperformance. |
| Coal remained resilient during that expansion | EI's own world-total coal generation rose {m['ei_world_coal_growth_2020_2024_pct']:.1f}% over 2020–2024. [E03] | Reject a thesis that requires broad, immediate coal displacement. |
| U.S. coal demand declined, then recovered | EIA national electric-power sector 98: −{decline:.1f}% in 2020–2024; +{rebound:.1f}% in 2025. [E04–E05] | Supports a cautious domestic thermal view, with a significant persistence risk. |
| The latest clean signal improved | Separate {m['panel25_n']}-country Ember panel: 2025 clean additions were {m['matched_2025_clean_vs_demand_additions_pct']:.1f}% of demand additions; all-fossil output fell {abs(m['matched_2025_fossil_yoy_pct']):.2f}%. [E06; matched table] | Encouraging update; one year and partial coverage do not prove a lasting world peak. |
| Coal's latest direction differed by market | EI observations show 2025 coal generation falling in China and India and rising in the U.S. [E11] | Geography must remain part of the exposure decision. |

**Baseline check.** Excluding pandemic-affected 2020, the same historical panel's clean output rose {m['clean_growth_2021_2024_pct']:.1f}% versus {m['fossil_growth_2021_2024_pct']:.1f}% for all fossil in 2021–2024. The direction survives this alternative baseline; the endpoint rates remain historical observations, not annual forecasts. [E10]

## 2. Why the recommendation follows

### Clean energy: favor participation in generation growth

Clean generation expanded faster than fossil generation and increased its share of the observed electricity mix. That combination is the empirical foundation of the overweight. The industry preference is to own participation in clean output, rather than make the entire investment case depend on coal contraction. [E01–E03]

We express that preference through diversified low-carbon generation owners as a portfolio construction judgment. The data aggregates clean output; it does not identify the best technology, prove a diversification benefit, or show which business model retains the profit. Equipment manufacturers, early-stage developers and operating-asset owners cannot be treated as interchangeable merely because they serve the same transition.

The required bridge from output to investment return is explicit: **generation → realized revenue → operating cash flow → cash available after investment and financing → value at the purchase price.** The supplied files establish the generation trend. The remaining links need company and project evidence before security selection. Contract terms, realized prices, operating costs, required capital expenditure, leverage and valuation are diligence questions, not findings from these datasets.

### Coal: focus the underweight where the consumption evidence applies

The U.S. historical consumption decline supports caution toward producers dependent on domestic thermal-power demand. Yet the 2025 recovery means that a straight-line decline would be an unjustified forecast. Our underweight is a forward-looking interpretation of an uneven historical record, not a measured prediction of falling coal-company earnings. [E04–E05]

The recommendation also has a deliberate boundary. EI's rising world coal generation through 2024 and divergent 2025 country observations do not support applying the U.S. consumption signal uniformly to global miners. Exporters and metallurgical-coal producers require separate work on product mix, destination demand, realized prices and costs. Their outlook remains unassessed by this memo rather than implicitly covered by the domestic thermal call. [E03; E11]

## 3. Use geography to test the argument

Three examples are sufficient for the pitch. China grew both clean and coal generation through 2024, showing that coexistence is possible. The U.S. grew clean output while coal generation fell, illustrating a different pathway. Germany's clean output, coal generation and demand all fell, showing why a coal decline alone cannot establish clean substitution. These observations describe outcomes; they do not establish policy, weather or price causality. [E08–E09; country review table]

The detailed country research remains available for diligence. It is not a claim that these examples represent every market or that the selected material markets provide an unbiased frequency estimate.

## 4. Give the strongest counterargument a fair hearing

**The strongest objection is that coal demand can recover while clean output expands—and that a growing clean industry can still be a poor investment.** Both concerns matter. Fossil output increased in the historical Ember panel, world coal generation increased through 2024, and U.S. coal consumption rebounded in 2025. The analysis contains no valuation or investable return model. [E01–E05]

Our response is to narrow the claim and make it testable. Retain the clean industry preference, but require financial evidence before choosing securities. Keep the coal underweight focused on U.S. domestic thermal exposure, and reduce it if the recovery persists. A broad global-coal short or a blanket purchase of clean-energy equities would exceed the evidence.

## 5. Implementation and stakeholder implications

| Exposure or stakeholder | Proposed action | Required next check |
|---|---|---|
| Diversified low-carbon generation owners | Overweight industry preference | Verify fleet mix, contract economics, asset cash flows, capital needs, financing and entry valuation. |
| U.S. domestic thermal-coal producers | Underweight industry preference | Verify dependence on domestic power customers, mine economics, customer contracts and whether recovery persists. |
| Export-facing and metallurgical coal | Separate exposure review | Establish product mix and actual trade exposure before extending the recommendation. |
| Utilities, developers and equipment suppliers | Assess individually within industry research | Determine how the business earns returns; generation trends alone do not establish its profitability. |
| Power consumers and policymakers | Use country demand and mix as context | These files do not establish affordability, reliability or the causal effect of policy. |

No security list, allocation percentage, price target or expected return is assigned. Those decisions require financial inputs beyond the supplied evidence. The November 2026 decision also relies on observations ending in 2025; comparable newer information must be checked before live implementation.

## 6. What would change our view?

These are analyst monitoring rules, not statistical thresholds, fitted probabilities or observed future outcomes. Recalculate on comparable definitions and fixed panels after each annual release.

| Monitor | Reconsideration condition | Response |
|---|---|---|
| U.S. power-sector coal consumption | Consumption stays above the 2024 level for two further annual releases after 2025 | Reduce the domestic thermal-coal underweight and reassess the durability of recovery. |
| Clean share and all-fossil output | Two comparable years with no clean-share gain and rising fossil output | Reassess the clean-energy overweight. |
| Generation owners' investment economics | Financial diligence shows weak project returns, financing pressure or an unattractive entry valuation | Review security selection; do not treat output growth as a sufficient investment case. |
| Composition of the available coal basket | Export or non-power exposure dominates | Rebuild the exposure assessment using the relevant end-market data. |
| Source revisions and coverage | Updated releases change the historical comparison or panel membership | Rerun the evidence before reaffirming the call. |

**Conditional paths.** If clean gains continue and U.S. coal weakens again, the directional preferences are reinforced. If clean and U.S. coal both grow, retain the clean preference only if supported by economics and reassess coal under the persistence rule. If clean momentum stalls and project economics weaken, the overweight warrants review even if coal remains weak. These paths explain decisions; they carry no assigned likelihood or return estimate.

## 7. Evidence quality and limits

- **Coverage:** the historical Ember comparison uses {m['panel24_n']} fixed countries; the latest watch uses a separate {m['panel25_n']}-country panel. The latter represents {m['panel25_share_observed_2024_generation_pct']:.1f}% of generation observed in the 2024 extract, **not {m['panel25_share_observed_2024_generation_pct']:.1f}% of world electricity**. Missing observations are not zeros.
- **Definitions:** Ember all-fossil output is not coal output. EI coal generation, EIA coal consumption and coal production measure different things; we compare their directions without subtracting their levels. Clean includes renewables and nuclear.
- **Prices and quality:** delivered EIA prices are fuel costs, not producer realizations or margins. Unresolved heat-content units prevent a defensible power-sector quality-adjusted fuel-price claim.
- **Third-source provenance:** the local EI file is hash-pinned and the official catalogue was checked. The exact original local edition and download date remain unverified. EI and Ember are not assumed to be wholly independent measurements. See SOURCES.md.
- **Inference:** observed output changes do not identify causes, establish a durable global peak, measure future stock returns or prove that one clean technology captures the value.

## Evidence map and supporting materials

All paths below are relative to this deliverables folder. Claim IDs refer to [claim_evidence.csv](tables/claim_evidence.csv).

| Question | Reproducible source |
|---|---|
| Historical clean versus fossil growth | [Fixed 2020–2024 panel](tables/matched_2020_2024.csv), E01–E02 |
| World coal context | [EI world totals](tables/ei_world_totals.csv), E03 |
| U.S. consumption decline and rebound | [EIA national power-sector series](tables/us_electric_power_coal.csv), E04–E05 |
| Latest clean and coal signals | [2025 matched panel](tables/matched_2020_2025.csv), E06; [coal watch](tables/2025_watch_evidence.csv), E11 |
| Geographic examples | [Country review table](tables/country_review_all.csv), E08–E09 |
| Alternative baseline | [2021 baseline sensitivity](tables/baseline_sensitivity.csv), E10 |

[Executive summary](EXECUTIVE_SUMMARY.md) · [Source limitations](SOURCES.md) · [Project audit](PROJECT_AUDIT.md) · [Country research](COUNTRY_REVIEW.md) · [Slide evidence map](PITCH_SLIDE_MAP.md)
"""
    (OUT / "INVESTMENT_THESIS.md").write_text(thesis)
    summary = f"""# Investment committee brief

**6 November 2026 · Three-year horizon: November 2026–November 2029**

## Decision

**Overweight clean energy through diversified low-carbon generation owners. Underweight coal, focused on U.S. domestic thermal producers.** These are relative industry preferences within an energy allocation. Position sizes and security selection remain conditional on financial diligence.

## Why this view

The transition can support clean growth while coal remains resilient. On the fixed {m['panel24_n']}-country Ember panel, clean generation rose **{clean:.1f}%** versus **{fossil:.1f}%** for all fossil in 2020–2024. Clean share rose from {m['clean_share_2020_pct']:.1f}% to {m['clean_share_2024_pct']:.1f}%. EI's world coal generation nevertheless increased {m['ei_world_coal_growth_2020_2024_pct']:.1f}% over that period. The clean preference does not require an immediate global coal collapse. [E01–E03]

The coal underweight has a narrower foundation: U.S. power-sector coal consumption fell **{decline:.1f}%** through 2024, before rebounding **{rebound:.1f}% in 2025**. That recovery is the strongest counterargument and lowers conviction. Export and metallurgical exposures need separate evidence. [E04–E05]

## Latest update

In the separate {m['panel25_n']}-country 2025 Ember panel, clean additions equalled {m['matched_2025_clean_vs_demand_additions_pct']:.1f}% of demand additions and all-fossil output fell {abs(m['matched_2025_fossil_yoy_pct']):.2f}%. EI coal observations fell in China and India and rose in the U.S. The watch panel covers {m['panel25_share_observed_2024_generation_pct']:.1f}% of **observed 2024 extract generation**, not world electricity. These are encouraging clean signals and divergent coal outcomes, not proof of a durable global peak. [E06; E11]

## How to act and when to reconsider

| Exposure | Action | What changes the view |
|---|---|---|
| Diversified low-carbon generation | Overweight industry preference; verify valuation, asset cash flows and financing | Two comparable years without clean-share gains while fossil output rises; or unattractive investment economics. |
| U.S. domestic thermal coal | Underweight industry preference; verify actual customer and product exposure | Consumption remains above 2024 for two further annual releases after 2025. |

The thresholds are analyst rules, not forecasts. Generation growth alone cannot demonstrate attractive equity returns. The exact original EI local-file edition/download date is also unresolved; preserve that limitation when presenting the third dataset.

**Committee takeaway:** participate selectively in clean-generation growth; keep the coal call geographically precise and open to reversal.

[Full thesis and evidence map](INVESTMENT_THESIS.md) · [Claim calculations](tables/claim_evidence.csv) · [Sources and provenance](SOURCES.md)
"""
    (OUT / "EXECUTIVE_SUMMARY.md").write_text(summary)
