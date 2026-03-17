with base as (

    select * 
    from {{ ref('stg_power_plants') }}

),

unpivoted as (

    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2013 as year, generation_gwh_2013 as generation_gwh from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2014, generation_gwh_2014 from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2015, generation_gwh_2015 from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2016, generation_gwh_2016 from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2017, generation_gwh_2017 from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2018, generation_gwh_2018 from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2019, generation_gwh_2019 from base

),

filled as (

    select
        *,
        coalesce(
            generation_gwh,
            avg(generation_gwh) over (
                partition by country_code, primary_fuel
            )
        ) as generation_gwh_filled
    from unpivoted

)

select * from filled