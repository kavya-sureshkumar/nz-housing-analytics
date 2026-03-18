{{ config(materialized='view') }}

SELECT
    DESCRIPTOR                               AS suburb,
    CAST(VALUE AS FLOAT)                     AS median_household_income
FROM {{ source('landing', 'STATS_NZ_CENSUS_2023') }}
WHERE SECTION_TITLE = 'Median household income'
  AND VALUE_TYPE_DESCRIPTION = 'Median'
  AND VALUE IS NOT NULL