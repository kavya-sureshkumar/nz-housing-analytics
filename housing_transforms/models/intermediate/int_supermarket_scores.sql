{{ config(enabled=false) }}

/*
  Counts supermarkets per suburb as a proxy for general
  amenity and daily convenience access.

  Normalised score: cap at 5 supermarkets, scale 0-10.
  Most Auckland suburbs have 1-3 supermarkets.
  Suburbs with 0 supermarkets score 0 (genuinely low amenity).
*/

WITH supermarkets AS (
    SELECT * FROM {{ ref('stg_supermarkets') }}
)

SELECT
    suburb,
    COUNT(*)                              AS supermarket_count,
    -- Normalised score: 1 supermarket = 2 points, max 10
    LEAST(COUNT(*) * 2.0, 10)             AS amenity_score
FROM supermarkets
GROUP BY suburb