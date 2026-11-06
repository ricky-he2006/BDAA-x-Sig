# research_b_coal_market

## World-proxy coal series (sum of country-level entities; excludes ALL EI regional aggregates O-*/T-*/WLD/ROW to avoid double counting)

```
variable  electbyfuel_coal  coalprod_mt  coal_tes_ej  n_countries  coal_gen_share_pct
Year                                                                                 
2020               9096.28      7521.13       148.33          109               38.50
2021               9830.99      7925.15       156.93          109               39.33
2022               9923.33      8531.29       158.75          109               38.75
2023              10077.33      8791.22       161.26          109               38.30
2024              10167.04      8901.11       162.72          109               36.95
2025              10125.27      8891.52       163.36          109               35.78
```

n_countries: 2024=109, 2025=109 2025 figures are EI estimates.

## Ground-truth check: EI 'Total World' row vs sum of listed countries (world proxy is a lower bound)

```
        variable  year  ei_total_world  sum_of_listed_countries  gap_pct_of_truth
     coalprod_mt  2020          7653.3                   7521.1              1.73
     coalprod_mt  2021          8056.0                   7925.1              1.62
     coalprod_mt  2022          8682.5                   8531.3              1.74
     coalprod_mt  2023          8947.6                   8791.2              1.75
     coalprod_mt  2024          9057.0                   8901.1              1.72
     coalprod_mt  2025          9052.7                   8891.5              1.78
electbyfuel_coal  2020          9502.1                   9096.3              4.27
electbyfuel_coal  2021         10243.5                   9831.0              4.03
electbyfuel_coal  2022         10335.6                   9923.3              3.99
electbyfuel_coal  2023         10472.8                  10077.3              3.78
electbyfuel_coal  2024         10569.7                  10167.0              3.81
electbyfuel_coal  2025         10511.0                  10125.3              3.67
     coal_tes_ej  2020           150.7                    148.3              1.58
     coal_tes_ej  2021           159.2                    156.9              1.44
     coal_tes_ej  2022           161.1                    158.7              1.45
     coal_tes_ej  2023           163.8                    161.3              1.55
     coal_tes_ej  2024           165.4                    162.7              1.59
     coal_tes_ej  2025           166.0                    163.4              1.61
```

The gap is the 'Other X' residual: countries the Statistical Review folds into regional 'Other' aggregates rather than listing individually. It must not be closed by adding those aggregates back (that would double-count the countries they contain).

## Top coal producers, 2024 (Mt; share of world proxy)

```
           country  coalprod_mt  coal_tes_ej  share_pct
             China       4595.7         92.2       51.6
             India       1085.1         23.0       12.2
         Indonesia        836.1          4.7        9.4
                US        465.0          7.9        5.2
         Australia        463.5          1.5        5.2
Russian Federation        427.2          3.7        4.8
      South Africa        236.0          3.7        2.7
        Kazakhstan        113.0          1.5        1.3
          Mongolia        106.5          NaN        1.2
           Germany         91.9          1.6        1.0
            Poland         85.2          1.3        1.0
           Turkiye         81.5          1.8        0.9
```

## Top coal producers, 2025 (Mt; share of world proxy)

```
           country  coalprod_mt  coal_tes_ej  share_pct
             China       4663.0         92.2       52.4
             India       1084.2         23.1       12.2
         Indonesia        790.0          5.2        8.9
                US        483.6          8.7        5.4
         Australia        431.4          1.5        4.9
Russian Federation        429.2          3.6        4.8
      South Africa        235.5          3.6        2.6
        Kazakhstan        120.5          1.6        1.4
          Mongolia        105.5          NaN        1.2
           Germany         86.4          1.5        1.0
            Poland         80.6          1.3        0.9
           Turkiye         75.4          1.8        0.8
```

## Top coal-fired generators, 2024 (TWh)

```
           country  electbyfuel_coal  share_pct
             China            5836.4       57.4
             India            1513.5       14.9
                US             712.9        7.0
             Japan             300.6        3.0
         Indonesia             228.4        2.2
Russian Federation             207.0        2.0
      South Africa             191.3        1.9
       South Korea             184.0        1.8
           Vietnam             152.8        1.5
         Australia             127.8        1.3
           Turkiye             123.0        1.2
            Taiwan             113.3        1.1
```

## Concentration: top-5 production share 2024

top-5 = 83.6% of world-proxy production

## Concentration: top-5 generation share 2024

top-5 = 84.5% of world-proxy generation

## Production up while domestic coal generation down, 2020->2024 (exporters / non-power demand)

```
country  coalprod_mt_2020  coalprod_mt_2024  prod_chg_pct  electbyfuel_coal_2020  electbyfuel_coal_2024  gen_chg_pct
 Brazil              7.06              7.94          0.12                  17.75                  14.13         -0.2
```

## Generation up while production down, 2020->2024 (importers)

```
Empty DataFrame
Columns: [country, prod_chg_pct, gen_chg_pct, coalprod_mt_2020, coalprod_mt_2024]
Index: []
```

## Countries where BOTH clean and coal-fired generation grew, 2020->2024 (TWh; >5% change on a non-zero base, material sizes only)

```
  country iso3  clean_2020  clean_2024  coal_2020  coal_2024  clean_chg_pct  coal_chg_pct
    China  CHN     2551.21     3849.68    4930.98    5836.35           0.51          0.18
    India  IND      341.77      458.09    1143.78    1513.52           0.34          0.32
Indonesia  IDN       52.89       67.21     180.87     228.43           0.27          0.26
 Viet Nam  VNM       84.95      128.36     122.53     152.78           0.51          0.25
   Turkey  TUR      127.33      155.65     105.81     123.00           0.22          0.16
```

## Countries where clean grew but coal-fired generation fell 2020->2024

```
                 country iso3  clean_chg_pct  coal_2020  coal_2024  coal_chg_pct
United States of America  USA           0.14     844.31     712.90         -0.16
                   Japan  JPN           0.35     316.89     300.58         -0.05
            South Africa  ZAF           0.54     207.82     191.31         -0.08
             South Korea  KOR           0.24     205.92     183.96         -0.11
               Australia  AUS           0.54     142.93     127.80         -0.11
                  Poland  POL           0.90     109.37      95.44         -0.13
              Kazakhstan  KAZ           0.51      73.65      69.40         -0.06
                  Brazil  BRA           0.24      17.75      14.13         -0.20
                   Italy  ITA           0.15      15.08       4.79         -0.68
                   Spain  ESP           0.25       6.15       3.47         -0.44
                  France  FRA           0.11       1.40       0.74         -0.47
```

