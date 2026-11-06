# research_a_global_electricity

## Global series - full panel (each year sums the countries reported that year)

```
 year  n_countries  demand_twh  generation_twh  clean_generation_twh  fossil_generation_twh  renewable_generation_twh  wind_solar_generation_twh  power_emissions_mtco2e  clean_share_pct  carbon_intensity_gco2e_kwh
 2020          213    26701.18        26707.38              10121.53               16585.85                   7472.76                    2444.82                13147.53            37.90                      492.28
 2021          213    28237.64        28235.15              10690.94               17544.21                   7929.98                    2910.05                13979.38            37.86                      495.11
 2022          213    28877.35        28886.66              11151.89               17734.77                   8511.96                    3438.62                14144.98            38.61                      489.67
 2023          212    29518.07        29528.55              11612.07               17916.48                   8963.39                    3974.35                14294.23            39.32                      484.08
 2024          196    30797.89        30793.66              12571.13               18222.53                   9845.30                    4643.59                14544.70            40.82                      472.33
 2025           91    29595.63        29573.20              12953.21               16619.99                  10234.33                    5420.83                13353.33            43.80                      451.53
```

2025 row = PARTIAL panel: Ember 2025 covers only 91 countries, so it is NOT comparable to the 2020-2024 totals above. Use the matched sample below for trends.

## Global series - matched sample (present in all years 2020-2025)

```
      n_countries  demand_twh  generation_twh  clean_generation_twh  fossil_generation_twh  renewable_generation_twh  wind_solar_generation_twh  power_emissions_mtco2e  clean_share_pct  carbon_intensity_gco2e_kwh
year                                                                                                                                                                                                                
2020           91    24856.64        24871.10               9661.04               15210.06                   7090.10                    2414.42                12107.42            38.84                      486.81
2021           91    26300.12        26305.22              10174.26               16130.96                   7510.06                    2873.15                12907.45            38.68                      490.68
2022           91    26913.24        26916.64              10627.29               16289.35                   8069.64                    3399.22                13047.07            39.48                      484.72
2023           91    27583.65        27594.68              11146.15               16448.53                   8531.91                    3930.76                13187.08            40.39                      477.88
2024           91    28803.80        28798.80              12082.85               16715.95                   9397.65                    4591.50                13407.03            41.96                      465.54
2025           91    29595.63        29573.20              12953.21               16619.99                  10234.33                    5420.83                13353.33            43.80                      451.53
```

Matched sample = 91 countries; every row covers the identical country set, so changes are apples-to-apples.

## Year-over-year % (matched sample)

```
      demand_twh  generation_twh  clean_generation_twh  fossil_generation_twh  renewable_generation_twh  wind_solar_generation_twh
year                                                                                                                              
2020         NaN             NaN                   NaN                    NaN                       NaN                        NaN
2021        5.81            5.77                  5.31                   6.05                      5.92                      19.00
2022        2.33            2.32                  4.45                   0.98                      7.45                      18.31
2023        2.49            2.52                  4.88                   0.98                      5.73                      15.64
2024        4.42            4.36                  8.40                   1.63                     10.15                      16.81
2025        2.75            2.69                  7.20                  -0.57                      8.90                      18.06
```

## Clean growth as % of demand growth (matched; blank = demand fell)

```
 year  clean_demand_coverage_pct
 2020                        NaN
 2021                       35.6
 2022                       73.9
 2023                       77.4
 2024                       76.8
 2025                      109.9
```

## Clean share by continent, % (matched sample)

```
continent  Africa  Asia  Europe  North America  Oceania  South America
year                                                                  
2020         16.2  28.7    57.9           44.2     32.2           73.1
2021         17.2  29.2    57.0           44.0     36.3           69.9
2022         18.0  30.8    55.2           44.6     39.5           76.7
2023         18.9  31.3    59.8           44.3     42.2           78.5
2024         19.7  33.5    62.1           44.9     42.0           78.1
2025         22.6  36.4    62.1           45.9     45.2           79.0
```

## Largest clean generators, 2024 (matched sample)

```
                 country  clean_generation_twh  demand_twh  clean_share_pct
                   China                3849.7     10069.9             38.2
United States of America                1838.5      4404.8             41.9
                  Brazil                 667.0       757.3             89.4
                  France                 533.3       472.0             94.9
                  Canada                 494.8       624.4             77.7
                   India                 458.1      2034.2             22.5
Russian Federation (the)                 434.6      1192.9             35.9
                   Japan                 318.0      1016.4             31.3
                 Germany                 290.9       522.3             58.6
             South Korea                 249.5       625.4             39.9
                   Spain                 215.6       270.7             76.8
          United Kingdom                 184.5       317.4             64.9
                  Sweden                 170.1       138.7             98.8
                  Turkey                 155.6       340.2             45.6
                  Norway                 154.9       138.7             98.6
```

## Largest wind+solar generators, 2024

```
                 country  wind_solar_generation_twh
                   China                     1836.1
United States of America                      755.6
                   India                      224.6
                 Germany                      215.7
                  Brazil                      179.8
                   Spain                      120.5
                   Japan                      108.2
          United Kingdom                       98.1
               Australia                       83.0
                  France                       70.5
                  Turkey                       62.2
                   Italy                       58.2
                  Canada                       56.2
             Netherlands                       55.3
                  Mexico                       45.5
```

## Fossil generation change 2020->2024, TWh: biggest declines

```
       country iso3  delta_twh
         Japan  JPN      -76.6
       Germany  DEU      -45.8
   Netherlands  NLD      -28.4
United Kingdom  GBR      -26.8
         Italy  ITA      -26.6
         Spain  ESP      -22.0
        France  FRA      -19.7
     Australia  AUS      -18.0
         Chile  CHL      -16.5
      Pakistan  PAK      -16.4
      Portugal  PRT      -14.3
        Brazil  BRA      -13.1
       Belgium  BEL      -12.4
        Poland  POL      -10.4
       Czechia  CZE       -8.9
```

## Fossil generation change 2020->2024, TWh: biggest increases

```
                   country iso3  delta_twh
                     China  CHN     1009.3
                     India  IND      356.8
  Russian Federation (the)  RUS      121.5
  United States of America  USA      120.6
Iran (Islamic Republic of)  IRN       61.4
                     Egypt  EGY       36.0
                    Mexico  MEX       22.7
                    Canada  CAN       20.4
         Philippines (the)  PHL       18.6
                  Thailand  THA       18.5
                  Viet Nam  VNM       16.2
                    Kuwait  KWT       15.9
                Bangladesh  BGD       15.6
                  Malaysia  MYS       14.4
                    Turkey  TUR       10.9
```

## Global carbon intensity (matched sample)

```
 year  carbon_intensity_gco2e_kwh
 2020                       486.8
 2021                       490.7
 2022                       484.7
 2023                       477.9
 2024                       465.5
 2025                       451.5
```

