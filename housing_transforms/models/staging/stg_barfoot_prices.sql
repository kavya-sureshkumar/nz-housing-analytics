{{ config(materialized='view') }}

SELECT
    SUBURB,
    DISTRICT,
    TO_DATE(REPORT_DATE, 'YYYY-MM-DD HH24:MI:SS')                    AS report_date,
    DATE_TRUNC('month', TO_DATE(REPORT_DATE, 'YYYY-MM-DD HH24:MI:SS')) AS report_month,
    AVG_SALE_PRICE,
    AVG_WEEKLY_RENT,
    GROSS_YIELD_PCT,
    CASE
        WHEN AVG_SALE_PRICE IS NULL    THEN 'missing_price'
        WHEN AVG_SALE_PRICE < 200000   THEN 'suspect_low'
        WHEN AVG_SALE_PRICE > 5000000  THEN 'suspect_high'
        ELSE 'ok'
    END AS data_quality_flag
FROM {{ source('landing', 'BARFOOT_SUBURB_PRICES') }}