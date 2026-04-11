{{ config(enabled=false) }}

/*
  Counts AT transit stops within 800m of each suburb centroid.
  800m is used as a walkable distance threshold (approx 10 min walk).

  Uses Snowflake's native HAVERSINE() function which returns
  distance in kilometres between two lat/lon coordinate pairs.
*/

WITH centroids AS (
    SELECT * FROM {{ ref('stg_suburb_centroids') }}
),
stops AS (
    SELECT * FROM {{ ref('stg_at_stops') }}
)

SELECT
    c.suburb,
    COUNT(s.stop_id)                          AS transit_stops_800m,
    -- Normalised score: cap at 50 stops (dense areas), scale 0-10
     LEAST(COUNT(s.stop_id) / 3.0, 10)        AS transit_score     
FROM centroids c
LEFT JOIN stops s
    ON HAVERSINE(c.centroid_lat, c.centroid_lon, s.lat, s.lon) < 0.8
GROUP BY c.suburb