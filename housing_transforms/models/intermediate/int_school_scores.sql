{{ config(enabled=false) }}

SELECT
    suburb,
    COUNT(*)                     AS school_count,
    ROUND(AVG(eqi_index), 2)     AS avg_eqi_index,

    -- Normalised 0-10 based on observed Auckland EQI range 344-569
    ROUND(
        LEAST(
            GREATEST(AVG(eqi_index) - 344, 0) / 22.5
        , 10)
    , 2)                         AS school_score

FROM {{ ref('stg_schools') }}
GROUP BY suburb