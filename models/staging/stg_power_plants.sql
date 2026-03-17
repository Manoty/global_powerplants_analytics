with source as (

    select * 
    from {{ ref('global_power_plants') }}

),

cleaned as (

    select
        -- ids
        cast(gppd_idnr as varchar) as plant_id,
        lower(name) as plant_name,

        -- location
        lower(country) as country_code,
        lower(country_long) as country_name,

        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,

        -- fuel
        lower(primary_fuel) as primary_fuel,

        -- capacity
        cast(capacity_mw as double) as capacity_mw,

        -- generation
        cast(generation_gwh_2013 as double) as generation_gwh_2013,
        cast(generation_gwh_2014 as double) as generation_gwh_2014,
        cast(generation_gwh_2015 as double) as generation_gwh_2015,
        cast(generation_gwh_2016 as double) as generation_gwh_2016,
        cast(generation_gwh_2017 as double) as generation_gwh_2017,
        cast(generation_gwh_2018 as double) as generation_gwh_2018,
        cast(generation_gwh_2019 as double) as generation_gwh_2019,

        -- metadata
        lower(owner) as owner,
        lower(source) as source

    from source

)

select * from cleaned