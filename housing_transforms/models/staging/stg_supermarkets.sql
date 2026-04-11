{{ config(materialized='view') }}

SELECT
    objectid AS supermarket_id,
    LOWER(TRIM(name)) AS supermarket_name,
    CASE LOWER(TRIM(suburb))
        -- mt → mount
        WHEN 'mt albert'        THEN 'mount albert'
        WHEN 'mt roskill'       THEN 'mount roskill'
        WHEN 'mt wellington'    THEN 'mount wellington'
        WHEN 'mt eden'          THEN 'mount eden'
        -- known name differences
        WHEN 'auckland cbd'     THEN 'city centre'
        WHEN 'manukau city'     THEN 'manukau'
        WHEN 'manukau central'  THEN 'manukau'
        WHEN 'mangere central'  THEN 'mangere'
        WHEN 'botany downs'     THEN 'botany'
        WHEN 'takapuna north'   THEN 'takapuna'
        WHEN 'te atatu'         THEN 'te atatu peninsula'
        WHEN 'te atatu north'   THEN 'te atatu peninsula'
        WHEN 'murrays bay'      THEN 'murrays bay'
        WHEN 'the gardens'      THEN 'flat bush'
        WHEN 'dannemora'        THEN 'east tamaki'
        WHEN 'oteha'            THEN 'albany'
        WHEN 'pinehill'         THEN 'albany'
        WHEN 'clendon'          THEN 'manurewa'
        WHEN 'randwick park'    THEN 'manurewa'
        WHEN 'wattle downs'     THEN 'manurewa'
        ELSE LOWER(TRIM(suburb))
    END AS suburb
FROM {{ source('landing', 'LINZ_SUPERMARKETS') }}
WHERE suburb IS NOT NULL