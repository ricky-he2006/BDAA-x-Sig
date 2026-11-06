"""Recompute presentation method examples from the audited fixed-panel tables."""
import pandas as pd


def method_examples(out):
    history = pd.read_csv(out / 'tables/matched_2020_2024.csv').set_index('year')
    watch = pd.read_csv(out / 'tables/matched_2020_2025.csv').set_index('year')
    clean0, clean1 = history.loc[[2020, 2024], 'clean_generation_twh']
    fossil0, fossil1 = history.loc[[2020, 2024], 'fossil_generation_twh']
    share0 = clean0 / history.at[2020, 'generation_twh'] * 100
    share1 = clean1 / history.at[2024, 'generation_twh'] * 100
    delta = watch.loc[2025] - watch.loc[2024]
    residual = delta.demand_twh - delta.clean_generation_twh - delta.fossil_generation_twh - delta.net_imports_twh
    assert abs(residual) < .1, 'Demand accounting residual exceeds rounding tolerance'
    result = {
        'clean_cagr_pct': ((clean1 / clean0) ** .25 - 1) * 100,
        'fossil_cagr_pct': ((fossil1 / fossil0) ** .25 - 1) * 100,
        'share_start_pct': share0, 'share_end_pct': share1,
        'share_change_pp': share1 - share0,
        'demand_delta_twh': delta.demand_twh,
        'clean_delta_twh': delta.clean_generation_twh,
        'fossil_delta_twh': delta.fossil_generation_twh,
        'imports_delta_twh': delta.net_imports_twh,
        'accounting_residual_twh': residual,
    }
    pd.DataFrame([{'metric': k, 'value': v} for k, v in result.items()]).to_csv(out / 'tables/method_examples.csv', index=False)
    return result
