with source as (

    select * 
    from {{ ref('global_power_plants') }}

),

renamed as (

    select
        -- ids
        cast(id as varchar) as plant_id,
        lower(name) as plant_name,

        -- location
        lower(country) as country,
        lower(country_long) as country_name,
        lower(primary_fuel) as primary_fuel,

        capacity_mw,

        -- generation (messy columns handled later)
        generation_gwh_2013,
        generation_gwh_2014,
        generation_gwh_2015,
        generation_gwh_2016,
        generation_gwh_2017,

        -- metadata
        lower(owner) as owner,
        lower(source) as source

    from source

)

select * from renamed