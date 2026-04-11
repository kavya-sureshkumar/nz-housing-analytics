# NZ Housing Affordability Analytics Pipeline

An end-to-end ELT data pipeline and interactive dashboard analysing housing affordability across 82 Auckland suburbs from January 2018 to March 2026.

Built as a portfolio project demonstrating data engineering, transformation, and visualisation skills using a modern cloud-native stack.

---

## Dashboard

Built with **Streamlit in Snowflake** — live dashboard querying Snowflake directly with no external BI tooling.

**5 pages:**
- 📈 Affordability Over Time — custom affordability index by suburb, 2018–2026
- 🏘️ Suburb Comparison — price-to-income ratio ranked by suburb
- 📉 Rate Cycle Story — OCR rate vs average sale price dual-axis chart
- 🏫 Schools & Amenity — school quality (EQI) and supermarket access by suburb
- 🏠 Rental Yield — gross rental yield ranked by suburb

---

## Key Finding

Auckland's affordability burden remained elevated through 2023–2024 despite a ~23% price correction from the 2021 peak. Rising 2-year swap rates (reaching 6%) offset the price decline — a buyer in 2024 faced a similar affordability burden to 2021 despite paying less for the house.

This is captured by the **Affordability Index**:

```
Affordability Index = Price-to-Income Ratio × (1 + Swap Rate / 100)

Where:
- Price-to-Income Ratio = avg_sale_price / median_household_income
- Swap Rate = 2-year NZ swap rate (how banks price mortgages)
- Higher value = less affordable
```

A $1M house at 2.2% swap rate has an effective price-to-income-rate burden roughly half that of the same house at 5.66% — even if the price itself has dropped.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Data Sources                         │
│  RBNZ  │  Stats NZ  │  Barfoot  │  AT GTFS  │  LINZ  │ MOE │
└────────────────────────────┬────────────────────────────────┘
                             │ Python ingestion scripts
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Snowflake — RAW.LANDING                        │
│  RBNZ_INTEREST_RATES       │  AT_TRANSIT_STOPS              │
│  STATS_NZ_CENSUS_2023      │  LINZ_SUPERMARKETS             │
│  BARFOOT_SUBURB_PRICES     │  MOE_SCHOOLS                   │
└────────────────────────────┬────────────────────────────────┘
                             │ dbt (6 staging views → 1 mart table)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│           Snowflake — ANALYTICS.MARTS                       │
│           MART_AFFORDABILITY_INDEX                          │
│           ~10,700 rows │ 82 suburbs │ Jan 2018–Mar 2026     │
└────────────────────────────┬────────────────────────────────┘
                             │ Snowpark session
                             ▼
┌─────────────────────────────────────────────────────────────┐
│           Streamlit in Snowflake Dashboard                  │
│           5 pages │ Altair charts │ Browser-based           │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, snowflake-connector-python |
| Orchestration | Apache Airflow (Astronomer) — planned |
| Data Warehouse | Snowflake (Standard, AWS Sydney) |
| Transformation | dbt Core (dbt-snowflake) |
| Dashboard | Streamlit in Snowflake, Altair |

---

## Data Sources

| Table | Rows | Source | Method |
|---|---|---|---|
| RBNZ_INTEREST_RATES | 99 | Reserve Bank of NZ | Manual CSV |
| STATS_NZ_CENSUS_2023 | 5,788 | Stats NZ | Manual CSV |
| BARFOOT_SUBURB_PRICES | 10,898 | Barfoot & Thompson | Web scraper |
| AT_TRANSIT_STOPS | 6,955 | Auckland Transport | GTFS v3 API |
| LINZ_SUPERMARKETS | 192 | LINZ ArcGIS Hub | CSV (Auckland only) |
| MOE_SCHOOLS | 2,577 | data.govt.nz | API |

---

## Project Structure

```
nz-housing-analytics/
├── ingestion/
│   ├── snowflake_client.py       shared Snowflake connection + write utility
│   ├── ingest_rbnz.py
│   ├── ingest_stats_nz.py
│   ├── ingest_barfoot.py
│   ├── ingest_at_stops.py
│   ├── ingest_supermarkets.py
│   └── ingest_schools.py
├── housing_transforms/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_interest_rates.sql
│   │   │   ├── stg_census_income.sql
│   │   │   ├── stg_barfoot_prices.sql
│   │   │   ├── stg_at_stops.sql
│   │   │   ├── stg_supermarkets.sql
│   │   │   └── stg_schools.sql
│   │   └── marts/
│   │       └── mart_affordability_index.sql
│   ├── models/staging/sources.yml
│   ├── tests/affordability_tests.yml
│   └── dbt_project.yml
├── docs/
│   ├── PROJECT_NOTES.md
│   ├── ARCHITECTURE.md
│   ├── PRD.md
│   ├── ISSUES_AND_IMPROVEMENTS.md
│   ├── INTERVIEW_PREP.md
│   └── CONCEPTS.md
├── streamlit_code.py
├── .env.example
└── README.md
```

---

## dbt Transformation Design

### Suburb Name Matching

Stats NZ census data uses granular SA2 sub-areas (e.g. `mount eden north`, `mount eden east`). Barfoot uses broad suburb names (`mount eden`). The staging model uses regex to strip directional suffixes and averages income across sub-areas per parent suburb:

```sql
TRIM(
    REGEXP_REPLACE(
        LOWER(DESCRIPTOR),
        '\\s+(north|south|east|west|central|...)$',
        ''
    )
) AS suburb,
AVG(CAST(VALUE AS FLOAT)) AS median_household_income
```

### Mt → Mount Conversion

Barfoot uses `Mt Albert`, Stats NZ uses `Mount Albert`. Handled in all mart joins:

```sql
REPLACE(LOWER(TRIM(p.suburb)), 'mt ', 'mount ') = c.suburb
```

### Why Swap Rate, Not OCR

Banks price mortgages off 2-year swap rates, not the OCR. Swap rates are forward-looking — they rose in late 2021 before RBNZ had moved the OCR at all. A model using OCR would miss this leading indicator effect.

---

## Data Coverage & Limitations

- **Date range:** January 2018 – March 2026 (monthly)
- **Suburbs:** 82 of 93 Barfoot suburbs with full income data (88% coverage)
- **11 suburbs with no income data:** Auckland average, City Centre, Flat Bush, Mangere, Mangere Bridge, Otahuhu, Otara, Ranui, St Heliers, Te Atatu Peninsula, Te Atatu South — genuine Stats NZ SA2 boundary gap, not fixable without paid concordance data
- **Barfoot market share:** ~40% of Auckland sales — known bias toward premium suburbs, mitigated by data quality flags in staging
- **Low transaction volume:** Premium suburbs like Remuera may have only 2–3 sales in a given month, causing single-month average spikes

---

## Setup

### Prerequisites

- Python 3.9+
- Snowflake account
- dbt Core with dbt-snowflake adapter

### Environment Variables

```
SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=HOUSING_WH
SNOWFLAKE_DATABASE=RAW
SNOWFLAKE_ROLE=PIPELINE_ROLE
AT_API_KEY=your-at-api-key
```

### Run Ingestion

```bash
pip install snowflake-connector-python pandas requests beautifulsoup4 python-dotenv

python ingestion/ingest_rbnz.py
python ingestion/ingest_stats_nz.py
python ingestion/ingest_barfoot.py      # ~90 min (polite 1s delay between requests)
python ingestion/ingest_at_stops.py
python ingestion/ingest_supermarkets.py
python ingestion/ingest_schools.py
```

### Run dbt Transformations

```bash
pip install dbt-snowflake

cd housing_transforms
dbt deps
dbt run
dbt test
```

### Deploy Streamlit Dashboard

1. Log into `app.snowflake.com`
2. Left sidebar → **Streamlit** → **+ Streamlit App**
3. Set warehouse: `HOUSING_WH`, database: `ANALYTICS`, schema: `MARTS`
4. Paste contents of `streamlit_code.py`
5. Click **Run**

Grant permissions if needed:

```sql
USE ROLE ACCOUNTADMIN;
GRANT USAGE ON DATABASE ANALYTICS TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA ANALYTICS.MARTS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON TABLE ANALYTICS.MARTS.MART_AFFORDABILITY_INDEX TO ROLE ACCOUNTADMIN;
```

---

## Mart Schema

`ANALYTICS.MARTS.MART_AFFORDABILITY_INDEX`

| Column | Type | Description |
|---|---|---|
| SUBURB | VARCHAR | Auckland suburb name (lowercase) |
| DISTRICT | VARCHAR | District grouping from Barfoot |
| REPORT_DATE | DATE | First day of the reporting month |
| AVG_SALE_PRICE | FLOAT | Average sale price ($NZD) |
| AVG_WEEKLY_RENT | FLOAT | Average weekly rent ($NZD) |
| GROSS_YIELD_PCT | FLOAT | Gross rental yield (%) |
| MEDIAN_HOUSEHOLD_INCOME | FLOAT | Median annual household income ($NZD, 2023 census) |
| OCR_RATE | FLOAT | RBNZ Official Cash Rate (%) |
| SWAP_RATE_2YR | FLOAT | 2-year swap rate (%) |
| SCHOOL_COUNT | INTEGER | Number of active schools in the suburb (MOE) |
| AVG_EQI_INDEX | FLOAT | Average Education Quality Index across suburb schools |
| SUPERMARKET_COUNT | INTEGER | Number of supermarkets in the suburb (LINZ) |
| PRICE_TO_INCOME_RATIO | FLOAT | avg_sale_price / median_household_income |
| AFFORDABILITY_INDEX | FLOAT | price_to_income_ratio × (1 + swap_rate_2yr / 100) — higher = less affordable |

---

## Acknowledgements

- [Reserve Bank of New Zealand](https://www.rbnz.govt.nz) — interest rate data
- [Stats NZ](https://www.stats.govt.nz) — census income data
- [Barfoot & Thompson](https://www.barfoot.co.nz) — suburb sale price data
- [Auckland Transport](https://at.govt.nz) — GTFS transit stop data
- [LINZ](https://data.linz.govt.nz) — supermarket location data
- [Ministry of Education](https://www.educationcounts.govt.nz) — school data
