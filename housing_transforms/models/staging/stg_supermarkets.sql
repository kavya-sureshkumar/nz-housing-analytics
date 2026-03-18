{{ config(materialized='view') }}

SELECT
    ID             AS supermarket_id,
    NAME           AS store_name,
    ADDRESS,
    LOWER(TRIM(SUBURB)) AS suburb,
    TOWN_CITY
FROM {{ source('landing', 'LINZ_SUPERMARKETS') }}