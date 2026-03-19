{{ config(materialized='table') }}

WITH property AS (
    SELECT * FROM {{ ref('stg_barfoot_prices') }}
    WHERE data_quality_flag = 'ok'
),
census AS (
    SELECT * FROM {{ ref('stg_census_income') }}
),
rates AS (
    SELECT * FROM {{ ref('stg_interest_rates') }}
)

SELECT
    p.suburb,
    p.district,
    p.report_date,
    p.avg_sale_price,
    p.avg_weekly_rent,
    p.gross_yield_pct,
    c.median_household_income,
    r.ocr_rate,
    r.swap_rate_2yr,
    ROUND(p.avg_sale_price / NULLIF(c.median_household_income, 0), 2)
        AS price_to_income_ratio,
    ROUND(
        (p.avg_sale_price / NULLIF(c.median_household_income, 0))
        * (1 + r.swap_rate_2yr / 100),
    2) AS affordability_index
FROM property p

LEFT JOIN census c
    ON REPLACE(LOWER(TRIM(p.suburb)), 'mt ', 'mount ') = c.suburb


LEFT JOIN rates r
    ON r.rate_month = p.report_month