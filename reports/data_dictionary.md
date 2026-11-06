# Data Dictionary

Units and definitions for every variable in the cleaned and processed tables. `source` identifies the upstream dataset. Flags use `available_*` (1/0 or bool) to mark structural missingness; absence of a row means *not reported*.

## Ember `ember_country_year.csv` (grain: country x year)

| variable | unit | definition |
|---|---|---|
| country / iso3 / continent | - | Ember country name, ISO3 code, continent |
| year | year | calendar year 2020-2025 |
| generation_twh | TWh | total electricity generation |
| demand_twh | TWh | generation + net imports (identical by construction) |
| clean_generation_twh | TWh | renewable + nuclear |
| fossil_generation_twh | TWh | coal + gas + oil (no coal sub-split) |
| renewable_generation_twh | TWh | all renewables incl. hydro |
| wind_solar_generation_twh | TWh | wind + solar |
| clean_share_pct / wind_solar_share_pct | % | share of generation |
| net_imports_twh | TWh | may be negative (net export) |
| demand_per_capita_mwh | MWh | per person |
| power_emissions_mtco2e | MtCO2e | sector emissions, 2-decimal rounding |
| carbon_intensity_gco2e_kwh | gCO2e/kWh | emissions per kWh generated |
| has_previous_year | 0/1 | prior-year observation present in this file |
| demand_change_twh / clean_change_twh / fossil_change_twh | TWh | YoY delta |
| clean_share_change_pp | percentage points | YoY |
| clean_growth_surplus_twh | TWh | clean change - demand change |
| clean_growth_coverage_pct | % | surplus / demand change; missing when demand did not grow |
| growth_status | category | demand_not_growing / clean_growth_below_demand_growth / clean_growth_met_or_exceeded_demand_growth |
| net_import_share_pct | % | net imports / demand |
| carbon_intensity_precision_limited | bool | emissions rounding limits CI precision |
| zero_generation_flag | bool | domestic generation = 0 (import-only) |
| clean_growth_coverage_pct_available | bool | completeness flag |

## EIA `eia_us_coal.csv` (grain: year x location x sector)

| variable | unit | definition |
|---|---|---|
| year | year | 2020-2025 |
| location / location_name | code / name | state (2-letter), region (NEW/MAT/...), '90' Pacific, 'US' total, PR |
| location_type | enum | state / census_region / pacific_region / us_total |
| is_geographic_aggregate | bool | True for region/US/pacific rows |
| sector / sectorDescription | code / name | see EIA_SECTORS |
| consumption | short tons | coal consumed |
| receipts | short tons | coal received |
| stocks | short tons | year-end inventory (structurally unreported for most power rows) |
| price | $/short ton | delivered coal price (structurally unreported for most rows) |
| ash_pct / sulfur_pct | % | average ash / sulfur by weight |
| heat_content_raw | mixed | Btu/lb for industrial sectors; GJ/tonne-scale for power sectors (unit not stated in source; see report 5.1) |
| heat_content_unit_inferred | enum | Btu_per_lb / GJ_per_tonne_scale_ASSUMED / zero_activity / missing |
| heat_content_btu_lb | Btu/lb | normalized; power-sector values are ASSUMED conversions |
| heat_content_normalized_is_assumed | bool | True when conversion assumed |
| available_* | bool | per-column completeness flags |

**Sector overlap (double-counting rule).** Sector 94 = 2+3 and 98 = 1+2+3 hold exactly. Use ONLY base sectors {1,2,3,8,9,10} for state-level sums, or ONLY {94,98,8,9,10} for totals - never mix.

## Energy Institute `energy_institute_global_energy.csv` (grain: entity x year x variable; 1965-2025)

| column | unit | definition |
|---|---|---|
| country / iso3 / iso_num | - | entity name; ISO3 code; numeric ISO (null for aggregates) |
| is_aggregate | bool | True for ALL EI regional aggregates: O-*/T-* codes, WLD (Total World), ROW. Country-level sums must exclude these; 'Other X' residual entities keep their listed countries out of such sums |
| Region / SubRegion | - | SRWE region fields (null for aggregates) |
| OPEC/EU/OECD/CIS | 0/1 | membership flags |
| Year | year | 1965-2025 |
| variable | code | see variable unit registry below |
| value | per-variable | numeric observation |
| variable_unit | text | unit from the registry |

### Variable registry (90 variables)

| variable | unit |
|---|---|
| `biodiesel_cons_kboed` | thousand barrels of oil equivalent/day (kboed) |
| `biodiesel_prod_kboed` | kboed |
| `biodiesel_prod_pj` | petajoules (PJ) |
| `biodiesel_tes_pj` | PJ |
| `biofuels_cons_kbd` | thousand barrels/day (kbd) |
| `biofuels_cons_kboed` | kboed |
| `biofuels_prod_kbd` | kbd |
| `biofuels_prod_kboed` | kboed |
| `biofuels_prod_pj` | PJ |
| `biofuels_tes_ej` | exajoules (EJ) |
| `biofuels_tes_pj` | PJ |
| `biogeo_tes_ej` | EJ |
| `biogeo_twh` | terawatt-hours (TWh) |
| `biogeo_twh_net` | TWh |
| `co2_combust_mtco2` | megatonnes CO2 (MtCO2) |
| `co2_combust_pc` | tonnes CO2/capita |
| `co2_combust_per_tes_ej` | MtCO2/EJ |
| `co2_mtco2` | MtCO2 |
| `coal_tes_ej` | EJ |
| `coalprod_ej` | EJ |
| `coalprod_mt` | million tonnes (Mt) |
| `cobalt_kt` | thousand tonnes (kt) |
| `cobaltres_kt` | kt |
| `diesel_gasoil_cons_kbd` | kbd |
| `elect_twh` | TWh |
| `electbyfuel_coal` | TWh |
| `electbyfuel_gas` | TWh |
| `electbyfuel_hydro` | TWh |
| `electbyfuel_nuclear` | TWh |
| `electbyfuel_oil` | TWh |
| `electbyfuel_other` | TWh |
| `electbyfuel_ren_power` | TWh |
| `electbyfuel_total` | TWh |
| `ethanol_cons_kboed` | kboed |
| `ethanol_prod_kboed` | kboed |
| `ethanol_prod_pj` | PJ |
| `ethanol_tes_pj` | PJ |
| `fuel_oil_cons_kbd` | kbd |
| `gas_tes_ej` | EJ |
| `gascons_bcfd` | billion cubic feet/day |
| `gascons_bcm` | billion cubic metres |
| `gasflared_bcm` | bcm |
| `gasflared_mtco2` | MtCO2 |
| `gasoline_cons_kbd` | kbd |
| `gasprod_bcfd` | bcfd |
| `gasprod_bcm` | bcm |
| `gasprod_ej` | EJ |
| `graphite_kt` | kt |
| `graphiteres_kt` | kt |
| `hydro_tes_ej` | EJ |
| `hydro_twh` | TWh |
| `hydro_twh_net` | TWh |
| `kerosene_cons_kbd` | kbd |
| `light_dist_cons_kbd` | kbd |
| `liqcons_kbd` | kbd |
| `lithium_kt` | kt |
| `lithiumres_kt` | kt |
| `lpg_cons_kbd` | kbd |
| `methane_process_mtco2` | MtCO2 |
| `middle_dist_cons_kbd` | kbd |
| `naphtha_cons_kbd` | kbd |
| `nuclear_tes_ej` | EJ |
| `nuclear_twh` | TWh |
| `nuclear_twh_net` | TWh |
| `oil_tes_ej` | EJ |
| `oilcons_kbd` | kbd |
| `oilcons_mt` | million tonnes |
| `oilprod_crudecond_kbd` | kbd |
| `oilprod_kbd` | kbd |
| `oilprod_mt` | million tonnes |
| `oilprod_ngl_kbd` | kbd |
| `other_oil_cons_kbd` | kbd |
| `pop` | millions |
| `rareearths_kt` | kt |
| `rareearthsres_kt` | kt |
| `refcap_kbd` | kbd |
| `refcaputil_pct` | percent |
| `refthru_kbd` | kbd |
| `ren_power_tes_ej` | EJ |
| `ren_power_twh` | TWh |
| `ren_power_twh_net` | TWh |
| `renewables_tes_ej` | EJ |
| `solar_tes_ej` | EJ |
| `solar_twh` | TWh |
| `solar_twh_net` | TWh |
| `tes_ej` | EJ |
| `tes_gj_pc` | GJ/capita |
| `wind_tes_ej` | EJ |
| `wind_twh` | TWh |
| `wind_twh_net` | TWh |

## Processed tables

### `analysis_country_year.csv` (grain: iso3 x year)

Ember columns (renamed none) + EI columns (prefix `ei_`, see registry above) left-joined on (std_geo_key, year). `coal_share_of_generation_pct` = ei_coal_generation / ei_elect_twh. `ei_variables_present` = at least one EI column non-null. Ember flags `zero_generation_flag` and `carbon_intensity_precision_limited` are carried through verbatim.

### `us_state_year_sector.csv` (grain: state x year x base-sector)

State-level EIA rows, base sectors only (1,2,3,8,9,10). Variables: coal_consumption_short_tons, coal_receipts_short_tons, coal_stocks_short_tons, delivered_price_usd_per_short_ton, heat_content_btu_per_lb, ash_content_pct, sulfur_content_pct + unit flags.

### `eia_us_aggregates.csv` (grain: location x year x agg-sector)

US-total/region rows with aggregate sectors 94/98 only - the complement of the state table; never combined with it.

### `coverage_calendar.csv`

Presence cells: (dataset, geo_key, year) with is_aggregate flag - used for coverage analysis and tests.

