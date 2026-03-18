select distinct
    plant_id,
    plant_name,
    country_code,
    country_name,
    primary_fuel,
    capacity_mw,
    latitude,
    longitude,
    owner

from {{ ref('stg_power_plants') }}