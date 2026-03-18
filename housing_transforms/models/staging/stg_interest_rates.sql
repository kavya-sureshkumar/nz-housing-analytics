{{ config(materialized='view') }}

SELECT
    TO_DATE(DATE, 'YYYY-MM-DD HH24:MI:SS')  AS rate_date,
    DATE_TRUNC('month', rate_date)           AS rate_month,
    CAST(OCR_RATE AS FLOAT)                  AS ocr_rate,
    CAST(SWAP_RATE_2YR AS FLOAT)             AS swap_rate_2yr,
    CAST(BANK_BILL_90D AS FLOAT)             AS bank_bill_90d,
    CAST(GOVT_BOND_2YR AS FLOAT)             AS govt_bond_2yr
FROM {{ source('landing', 'RBNZ_INTEREST_RATES') }}
WHERE OCR_RATE IS NOT NULL