{{ config(materialized='view') }}

SELECT
    STOP_ID,
    STOP_CODE,
    STOP_NAME,
    CAST(STOP_LAT AS FLOAT)        AS lat,
    CAST(STOP_LON AS FLOAT)        AS lon,
    CAST(LOCATION_TYPE AS INTEGER) AS location_type,
    CASE LOCATION_TYPE
        WHEN 0 THEN 'stop'
        WHEN 1 THEN 'station'
        WHEN 2 THEN 'entrance'
        ELSE 'other'
    END                            AS stop_type,
    PARENT_STATION
FROM {{ source('landing', 'AT_TRANSIT_STOPS') }}
WHERE STOP_LAT IS NOT NULL
  AND STOP_LON IS NOT NULL