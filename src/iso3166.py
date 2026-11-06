"""ISO 3166-1 alpha-3 reference and cross-source geographic aliasing.

The three sources use slightly different conventions for a handful of
geographies (Kosovo, Taiwan, territories). We keep each source's code intact
in the cleaned data and provide a stable `std_geo_key` used ONLY for joins.
"""

# Official ISO 3166-1 alpha-3 codes + the common non-member territories
# (243 codes). Membership is data-driven-verified: the pipeline flags any
# source code not in this set (or in ISO3_NONISO_ACCEPTED) as an audit
# warning, so a missing code surfaces instead of silently passing.
# Removed from an earlier revision: CCA, CXA, FXY, MYT, MNR, VCU (not valid
# current assignments) and TUV/KNA/ARE/CHE duplicates.
ISO3_OFFICIAL = {
    # Africa
    "DZA", "AGO", "BEN", "BDI", "BFA", "BWA", "CMR", "CAF", "COD", "COG",
    "CIV", "COM", "CPV", "CWG", "DJI", "EGY", "GNQ", "ERI", "ETH", "GAB",
    "GMB", "GHA", "GIN", "GNB", "KEN", "LSO", "LBR", "LBY", "MDG", "MWI",
    "MLI", "MRT", "MAR", "MOZ", "NAM", "NER", "NGA", "RWA", "STP", "SEN",
    "SYC", "SLE", "SOM", "SDN", "SSD", "TZA", "SWZ", "TCD", "TGO", "TUN",
    "UGA", "ZMB", "ZWE", "MUS", "REU", "ZAF",
    # Americas
    "ABW", "AIA", "ARG", "ASM", "ATG", "BHS", "BES", "BLZ", "BOL", "BMU",
    "BRA", "CAN", "CHL", "CCK", "CYM", "COL", "CUW", "CRI", "CUB", "DOM",
    "ECU", "SLV",
    "GLP", "GRD", "GTM", "GUF", "GUM", "GUY", "HTI", "HND", "JAM", "MEX",
    "MTQ", "MSR", "NIC", "PAN", "PRY", "PER", "PRI", "SXM", "TCA", "TTO",
    "VCT", "VEN", "VIR", "VGB", "SUR", "DMA", "BLM", "KNA", "LCA", "SHN",
    "SPM", "URY", "USA", "BRB",
    # Asia
    "AFG", "ALA", "AND", "ARE", "ARM", "AZE", "BGD", "BHR", "BRN", "BTN",
    "YEM",
    "KHM", "CHN", "GEO", "HKG", "IDN", "IND", "IRN", "IRQ", "ISR", "JPN",
    "JOR", "KAZ", "KGZ", "LAO", "LBN", "LKA", "MAC", "MMR", "MNG", "MYS",
    "MDV", "NPL", "PRK", "KOR", "KWT", "OMN", "PAK", "PSE", "PHL", "QAT",
    "SAU", "SGP", "SYR", "TJK", "TKM", "THA", "TLS", "TUR", "TWN", "UZB",
    "VNM",
    # Europe
    "ALB", "AUT", "BLR", "BEL", "BIH", "BGR", "HRV", "CYP", "CZE", "DNK",
    "EST", "FIN", "FRA", "DEU", "GIB", "GRC", "GGY", "HUN", "ISL", "IRL",
    "IMN", "ITA", "JEY", "LVA", "LIE", "LTU", "LUX", "MLT", "MKD", "MDA",
    "MCO", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "RUS", "SMR", "SRB",
    "SVK", "SVN", "SWE", "CHE", "UKR", "VAT", "GBR", "FRO", "GRL", "ESP",
    # Oceania
    "AUS", "COK", "FJI", "FSM", "KIR", "MHL", "MNP", "NCL", "NAU", "NIU",
    "NFK", "NZL", "PLW", "PNG", "PYF", "SLB", "TON", "TKL", "TUV", "VUT",
    "WSM",
    # Antarctica / polar / other territories
    "ATA", "ATF", "BVT", "CXR", "FLK", "HMD", "SGS", "UMI",
}

# Well-known non-ISO codes that energy data vendors legitimately use.
# These are ACCEPTED (not treated as errors) but always flagged in the audit.
ISO3_NONISO_ACCEPTED = {
    "XKS": "Kosovo (ISO user-assigned)",
    "XKO": "Kosovo (UN user-assigned)",
    "XKX": "Kosovo (vendor variant)",
    "TWP": "Taiwan, Province of China (ISO user-assigned)",
    "TWA": "Taiwan (vendor variant)",
    "QAX": "West Bank (vendor variant)",
    "SUN": "Soviet Union (historical; EI vendor code)",
    "ANT": "Netherlands Antilles (retired code; vendor keeps pre-2010 entity)",
    "NRU": "Nauru (legacy vendor code; current official code is NAU)",
}

# Canonical join keys for geographies whose codes differ across sources.
# Keys are lower-case, stable strings; anything not in this map joins on
# iso3 itself.
GEO_ALIAS_TO_KEY = {
    "xks": "kosovo", "xko": "kosovo", "xkx": "kosovo",
    "twn": "taiwan", "twp": "taiwan", "twa": "taiwan",
    "qax": "west-bank", "psx": "west-bank",
}


def std_geo_key(iso3: str) -> str:
    """Stable join key for a geo code (handles non-ISO vendor codes)."""
    if iso3 is None:
        return ""
    code = str(iso3).strip().lower()
    if code in GEO_ALIAS_TO_KEY:
        return GEO_ALIAS_TO_KEY[code]
    return code


def is_known(iso3: str) -> bool:
    return str(iso3).strip().upper() in ISO3_OFFICIAL


def is_accepted_noniso(iso3: str) -> bool:
    return str(iso3).strip().upper() in ISO3_NONISO_ACCEPTED
