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
    generation_gwh,
    -- remove the bare generation_source here, keep only the CASE version below

    case
        when generation_gwh is not null then 'actual'
        when estimated_generation_gwh is not null then 'estimated'
        else 'imputed_avg'
    end as generation_source

from {{ ref('int_power_generation') }}