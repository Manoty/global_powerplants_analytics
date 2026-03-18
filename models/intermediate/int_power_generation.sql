with base as (

    select * 
    from {{ ref('stg_power_plants') }}

),

unpivoted as (

    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2013 as year,
           generation_gwh_2013 as generation_gwh,
           estimated_generation_gwh_2013 as estimated_generation_gwh
    from base

    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2014,
           generation_gwh_2014,
           estimated_generation_gwh_2014
    from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2015,
           generation_gwh_2015,
           estimated_generation_gwh_2015
    from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2016,
           generation_gwh_2016,
           estimated_generation_gwh_2016
    from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2017,
           generation_gwh_2017,
           estimated_generation_gwh_2017
    from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2018,
           generation_gwh_2018,
           null as estimated_generation_gwh  -- not in source data
    from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, latitude, longitude, 2019,
           generation_gwh_2019,
           null as estimated_generation_gwh  -- not in source data
    from base

),

filled as (

    select
        *,
        coalesce(
            generation_gwh,
            estimated_generation_gwh,
            avg(generation_gwh) over (
                partition by country_code, primary_fuel
            )
        ) as generation_gwh_final

    from unpivoted

)

select * from filled