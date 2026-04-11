-- Asserts that every (suburb, report_date) combination is unique in the mart.
-- Returns rows that are duplicated; test fails if any rows are returned.
SELECT
    suburb,
    report_date,
    COUNT(*) AS row_count
FROM {{ ref('mart_affordability_index') }}
GROUP BY suburb, report_date
HAVING COUNT(*) > 1
