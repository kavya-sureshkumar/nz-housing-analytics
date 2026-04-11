{{ config(materialized='table') }}

WITH property AS (
    -- Aggregate to suburb+month grain. Some suburbs appear under multiple districts
    -- in the same Barfoot report; averaging gives a truer suburb-level figure.
    SELECT
        suburb,
        report_month,
        MAX(report_date)                    AS report_date,
        ROUND(AVG(avg_sale_price), 0)       AS avg_sale_price,
        ROUND(AVG(avg_weekly_rent), 0)      AS avg_weekly_rent,
        ROUND(AVG(gross_yield_pct), 2)      AS gross_yield_pct,
        MIN(data_quality_flag)              AS data_quality_flag
    FROM {{ ref('stg_barfoot_prices') }}
    WHERE data_quality_flag = 'ok'
    GROUP BY suburb, report_month
),
census AS (
    SELECT * FROM {{ ref('stg_census_income') }}
),
rates AS (
    SELECT * FROM {{ ref('stg_interest_rates') }}
),
schools AS (
    SELECT
        suburb,
        COUNT(*)                 AS school_count,
        ROUND(AVG(eqi_index), 1) AS avg_eqi_index
    FROM {{ ref('stg_schools') }}
    GROUP BY suburb
),
amenity AS (
    SELECT
        suburb,
        COUNT(*) AS supermarket_count
    FROM {{ ref('stg_supermarkets') }}
    GROUP BY suburb
)

SELECT
    p.suburb,
    p.report_date,
    p.avg_sale_price,
    p.avg_weekly_rent,
    p.gross_yield_pct,
    c.median_household_income,
    r.ocr_rate,
    r.swap_rate_2yr,
    sc.school_count,
    sc.avg_eqi_index,
    am.supermarket_count,

    -- Price-to-income ratio (how many years of income to buy the house)
    ROUND(p.avg_sale_price / NULLIF(c.median_household_income, 0), 2)
        AS price_to_income_ratio,

    -- Custom affordability index: price-to-income ratio adjusted for the interest rate environment
    -- Higher value = less affordable
    ROUND(
        (p.avg_sale_price / NULLIF(c.median_household_income, 0))
        * (1 + r.swap_rate_2yr / 100),
    2) AS affordability_index

FROM property p

LEFT JOIN census c
    ON REPLACE(LOWER(TRIM(p.suburb)), 'mt ', 'mount ') = c.suburb

LEFT JOIN rates r
    ON r.rate_month = p.report_month

LEFT JOIN schools sc
    ON REPLACE(LOWER(TRIM(p.suburb)), 'mt ', 'mount ') = sc.suburb

LEFT JOIN amenity am
    ON REPLACE(LOWER(TRIM(p.suburb)), 'mt ', 'mount ') = am.suburb
