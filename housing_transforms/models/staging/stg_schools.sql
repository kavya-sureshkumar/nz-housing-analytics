{{ config(materialized='view') }}

SELECT
    SCHOOL_ID,
    ORG_NAME                              AS school_name,
    ORG_TYPE                              AS school_type,
    AUTHORITY,
    STATISTICAL_AREA_2_CODE               AS sa2_code,
    STATISTICAL_AREA_2_DESCRIPTION        AS sa2_name,
    LOWER(TRIM(ADD1_SUBURB))              AS suburb,
    ADD1_CITY                             AS city,
    TERRITORIAL_AUTHORITY,
    CAST(LATITUDE  AS FLOAT)              AS lat,
    CAST(LONGITUDE AS FLOAT)              AS lon,
    CAST(EQI_INDEX AS FLOAT)              AS eqi_index,
    CAST(TOTAL     AS INTEGER)            AS roll,
    STATUS
FROM {{ source('landing', 'MOE_SCHOOLS') }}
WHERE STATUS != 'Closed'
  AND LATITUDE IS NOT NULL