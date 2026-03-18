import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="Global Power Plants Dashboard", layout="wide")

# --- DB CONNECTION ---
conn = duckdb.connect("dev.duckdb")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    query = """
        SELECT *
        FROM main.fct_power_generation
    """
    return conn.execute(query).df()

df = load_data()

# --- TITLE ---
st.title("⚡ Global Power Generation Dashboard")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Select Country",
    options=df["country_name"].dropna().unique(),
    default=df["country_name"].dropna().unique()[:5]
)

fuels = st.sidebar.multiselect(
    "Select Fuel Type",
    options=df["primary_fuel"].dropna().unique(),
    default=df["primary_fuel"].dropna().unique()
)

filtered_df = df[
    (df["country_name"].isin(countries)) &
    (df["primary_fuel"].isin(fuels))
]

# --- RENEWABLES LIST (define before KPIs) ---
renewables = ["Solar", "Wind", "Hydro", "Geothermal", "Wave and Tidal", "Biomass"]

# --- KPI SECTION ---
renewable_pct = (
    filtered_df[filtered_df["primary_fuel"].isin(renewables)]["generation_gwh"].sum()
    / filtered_df["generation_gwh"].sum() * 100
)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Generation (GWh)", f"{filtered_df['generation_gwh'].sum():,.0f}")
col2.metric("Total Capacity (MW)", f"{filtered_df['capacity_mw'].sum():,.0f}")
col3.metric("Number of Plants", f"{filtered_df['plant_id'].nunique():,}")
col4.metric("Renewable Share", f"{renewable_pct:.1f}%")



# --- CHART 1: Generation Over Time ---
st.subheader("📈 Generation Over Time")

time_df = (
    filtered_df
    .groupby("year")["generation_gwh"]
    .sum()
    .reset_index()
)

fig1 = px.line(time_df, x="year", y="generation_gwh", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# --- CHART 2: Fuel Mix ---
st.subheader("🔥 Energy Mix by Fuel Type")

fuel_df = (
    filtered_df
    .groupby("primary_fuel")["generation_gwh"]
    .sum()
    .reset_index()
)

# --- CHART 3: Generation Trend by Fuel Type ---
st.subheader("🔥 Generation Trend by Fuel Type")

fig2 = px.pie(fuel_df, names="primary_fuel", values="generation_gwh")
st.plotly_chart(fig2, use_container_width=True)

trend_df = filtered_df.groupby(["year", "primary_fuel"])["generation_gwh"].sum().reset_index()
fig_trend = px.line(trend_df, x="year", y="generation_gwh", color="primary_fuel", markers=True,
              title="Generation Trend by Fuel Type")
st.plotly_chart(fig_trend, use_container_width=True)

# --- CHART 3: Top Plants ---
st.subheader("🏭 Top Power Plants")

top_plants = (
    filtered_df
    .groupby("plant_name")["generation_gwh"]
    .sum()
    .reset_index()
    .sort_values(by="generation_gwh", ascending=False)
    .head(10)
)

fig3 = px.bar(top_plants, x="generation_gwh", y="plant_name", orientation="h")
st.plotly_chart(fig3, use_container_width=True)


# --- CHART 4: TCapacity vs Generation scatter ---
st.subheader("🏭 Capacity vs Generation scatter ")

fig_scatter = px.scatter(
    filtered_df,
    x="capacity_mw",
    y="generation_gwh",
    color="primary_fuel",
    hover_name="plant_name",
    opacity=0.6,
    title="Capacity vs Actual Generation"
)
st.plotly_chart(fig_scatter, use_container_width=True)


# --- CHART 5: Top countries by capacity ---
st.subheader("🏭 Top countries by capacity ")

country_capacity = (
    filtered_df.groupby("country_name")["capacity_mw"]
    .sum().reset_index()
    .sort_values("capacity_mw", ascending=False)
    .head(15)
)
fig_cap = px.bar(country_capacity, x="country_name", y="capacity_mw", title="Top Countries by Installed Capacity (MW)")
st.plotly_chart(fig_cap, use_container_width=True)

# --- CHART 6: Renewable vs Non-Renewable ---
st.subheader("🏭 Renewable vs Non-Renewable Generation")

renewables = ["Solar", "Wind", "Hydro", "Geothermal", "Wave and Tidal", "Biomass"]
filtered_df["energy_type"] = filtered_df["primary_fuel"].apply(
    lambda x: "Renewable" if x in renewables else "Non-Renewable"
)
fig_renew = px.pie(filtered_df, names="energy_type", values="generation_gwh",
             title="Renewable vs Non-Renewable Generation")
st.plotly_chart(fig_renew, use_container_width=True)

# --- CHART 7: Capacity Utilization Rate ---
st.subheader("🏭 Capacity Utilization Rate ")

filtered_df["utilization_rate"] = (
    filtered_df["generation_gwh"] / (filtered_df["capacity_mw"] * 8.76)
).clip(0, 1) * 100

fig_util = px.box(filtered_df, x="primary_fuel", y="utilization_rate",
             title="Capacity Utilization by Fuel Type (%)")
st.plotly_chart(fig_util, use_container_width=True)

# --- CHART 8: Data Quality ---
st.subheader("🧠 Data Quality (Source of Generation Data)")

quality_df = (
    filtered_df
    .groupby("generation_source")
    .size()
    .reset_index(name="count")
)

fig4 = px.bar(quality_df, x="generation_source", y="count")
st.plotly_chart(fig4, use_container_width=True)

with st.expander("📄 View Raw Data"):
    st.dataframe(
        filtered_df.sort_values("generation_gwh", ascending=False),
        use_container_width=True,
        column_config={
            "generation_gwh": st.column_config.NumberColumn("Generation (GWh)", format="%.1f"),
            "capacity_mw": st.column_config.NumberColumn("Capacity (MW)", format="%.1f"),
            "utilization_rate": st.column_config.ProgressColumn("Utilization %", min_value=0, max_value=100),
        }
    )