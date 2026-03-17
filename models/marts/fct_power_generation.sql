select
    plant_id,
    plant_name,
    country_code,
    country_name,
    primary_fuel,
    year,

    capacity_mw,
    generation_gwh_filled as generation_gwh

from {{ ref('int_power_generation') }}