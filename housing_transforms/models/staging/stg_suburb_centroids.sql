{{ config(enabled=false) }}

/*
  Derives approximate suburb centroid coordinates by averaging
  school lat/lon values per suburb. Schools are well-distributed
  across suburbs and provide a reasonable centroid proxy.

  In production this would be replaced with an official
  Stats NZ or LINZ suburb boundary centroid table.
*/

SELECT
    suburb,
    AVG(lat) AS centroid_lat,
    AVG(lon) AS centroid_lon,
    COUNT(*) AS school_count_for_centroid
FROM {{ ref('stg_schools') }}
WHERE lat  BETWEEN -37.5 AND -36.0
  AND lon  BETWEEN 174.0 AND 175.5
GROUP BY suburb
HAVING COUNT(*) >= 1