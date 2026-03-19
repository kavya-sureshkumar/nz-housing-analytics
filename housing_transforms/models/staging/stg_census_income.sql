{{ config(materialized='view') }}

SELECT
    -- Strip directional suffix to get parent suburb name
    -- e.g. 'mount eden north' → 'mount eden', 'ponsonby east' → 'ponsonby'
    TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                LOWER(DESCRIPTOR),
                '\\s*\\([^)]*\\)$', ''   -- remove (auckland), (christchurch city) etc.
            ),
            '\\s+(central|north|south|east|west|central-north|central-south|north east|south east|north west|south west|central east|central north|central south|nirvana|konini|rosier|woodglen|larnoch|keegan|red hills|seabrook|tuff crater|royal road west|valley park|abbotts park|waiata|waiatarua|waitaramoa|rosebank|eastridge|amaru|oranga|ferndale|hamlin|heights east|heights north west|heights south west|mclennan|massey park|hospital|eastburn|south crossing|hill east|hill west|parrs park|industrial)$',
            ''
        )
    )                                    AS suburb,
    ROUND(AVG(CAST(VALUE AS FLOAT)),0)      AS median_household_income
FROM {{ source('landing', 'STATS_NZ_CENSUS_2023') }}
WHERE SECTION_TITLE = 'Median household income'
  AND VALUE_TYPE_DESCRIPTION = 'Median'
  AND VALUE IS NOT NULL
GROUP BY 1