"""Temporary: verify the correct way to exclude EI aggregate entities.
Deleted after use."""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import config as C
from src import iso3166 as I

ei = pd.read_csv(C.CLEANED / C.CLEANED_EI)
e24 = ei[ei.Year == 2024]
byiso = e24.drop_duplicates("iso3")
official = set(I.ISO3_OFFICIAL) | set(I.ISO3_NONISO_ACCEPTED)
n_alpha = int(byiso.iso3.str.upper().isin(official).sum())
n_num = int(byiso.iso_num.notna().sum())
like_agg = byiso.country.str.match(r"^(Total|Other|Rest)", case=False, na=False)
n_name = int((~like_agg).sum())
print("distinct iso3 in 2024:", len(byiso))
print("  alpha3 in ISO-official set:", n_alpha)
print("  iso_num not null:", n_num)
print("  name NOT Total/Other/Rest:", n_name)
print("--- entities with numeric ISO but alpha3 NOT in official set (n=%d) ---"
      % len(byiso[byiso.iso_num.notna() & ~byiso.iso3.str.upper().isin(official)]))
for iso, name in byiso[byiso.iso_num.notna() & ~byiso.iso3.str.upper().isin(official)][
        ["iso3", "country"]].values:
    print(f"   {iso}  {name}")
print("--- entities whose name starts Total/Other/Rest (2024) ---")
for iso, name in byiso[like_agg][["iso3", "country"]].values:
    print(f"   {iso}  {name}")


def world_sum(iso_filter):
    w = ei[ei.Year == 2024]
    w = w[w.iso3.isin(iso_filter)]
    out = {}
    for var in ("coalprod_mt", "electbyfuel_coal", "coal_tes_ej"):
        out[var] = round(w[w.variable == var].value.sum(), 1)
    return out, w.country.nunique()


# candidate filters
f_alpha = set(byiso.iso3[byiso.iso3.str.upper().isin(official)])
f_num = set(byiso.iso3[byiso.iso_num.notna()])
f_name = set(byiso.iso3[~like_agg])
for label, f in (("alpha3-official", f_alpha), ("iso_num-notna", f_num),
                 ("name-not-agg", f_name)):
    tot, n = world_sum(f)
    print(f"\n[{label}] n_entities={n}  coalprod={tot['coalprod_mt']} Mt  "
          f"gen={tot['electbyfuel_coal']} TWh  tes={tot['coal_tes_ej']} EJ")

tw = ei[(ei.country == "Total World") & (ei.Year == 2024)]
print("\n--- EI 'Total World' row 2024 (the ground-truth world total) ---")
for _, r in tw[tw.variable.isin(["coalprod_mt", "electbyfuel_coal", "coal_tes_ej"])].iterrows():
    print(f"   {r.variable}: {r.value}")
