with base as (

    select * 
    from {{ ref('stg_power_plants') }}

),

unpivoted as (

    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2013 as year,
           generation_gwh_2013 as generation_gwh,
           null as estimated_generation_gwh
    from base

    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2014,
           generation_gwh_2014, null from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2015,
           generation_gwh_2015, null from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2016,
           generation_gwh_2016, null from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2017,
           generation_gwh_2017, null from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2018,
           generation_gwh_2018, null from base
    union all
    select plant_id, plant_name, country_code, country_name, primary_fuel, capacity_mw, 2019,
           generation_gwh_2019, null from base

),

-- 🔥 NEW: bring in estimated values
with_estimates as (

    select
        u.*,

        case year
            when 2013 then estimated_generation_gwh_2013
            when 2014 then estimated_generation_gwh_2014
            when 2015 then estimated_generation_gwh_2015
            when 2016 then estimated_generation_gwh_2016
            when 2017 then estimated_generation_gwh_2017
            when 2016 then estimated_generation_gwh_2018
            when 2017 then estimated_generation_gwh_2019

        end as estimated_generation_gwh

    from unpivoted u
    join {{ ref('stg_power_plants') }} b
        using (plant_id)

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

    from with_estimates

)

select * from filled