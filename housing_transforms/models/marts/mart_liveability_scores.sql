{{ config(enabled=false) }}

WITH transit AS (
    SELECT * FROM {{ ref('int_transit_scores') }}
),
schools AS (
    SELECT * FROM {{ ref('int_school_scores') }}
),
amenity AS (
    SELECT * FROM {{ ref('int_supermarket_scores') }}
),
centroids AS (
    SELECT * FROM {{ ref('stg_suburb_centroids') }}
)

SELECT
    c.suburb,
    c.centroid_lat,
    c.centroid_lon,

    -- Transit
    t.transit_stops_800m,
    t.transit_score,

    -- Schools
    s.school_count,
    s.avg_eqi_index,
    s.school_score,

    -- Amenity
    a.supermarket_count,
    a.amenity_score,

    -- Composite liveability score (0-10)
    ROUND(
    COALESCE(t.transit_score, 0) * 0.45
  + COALESCE(s.school_score,  0) * 0.40
  + COALESCE(a.amenity_score, 0) * 0.15
, 2) AS liveability_score

FROM centroids c
LEFT JOIN transit t ON t.suburb = c.suburb
LEFT JOIN schools s ON s.suburb = c.suburb
LEFT JOIN amenity a ON a.suburb = c.suburb
