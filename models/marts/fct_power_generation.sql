{{ config(materialized='table') }}

select
    plant_id,
    plant_name,
    country_code,
    country_name,
    primary_fuel,
    latitude,
    longitude,
    year,
    capacity_mw,
    generation_gwh_final as generation_gwh,
    case
        when generation_gwh is not null then 'actual'
        when estimated_generation_gwh is not null then 'estimated'
        else 'imputed_avg'
    end as generation_source
from {{ ref('int_power_generation') }}