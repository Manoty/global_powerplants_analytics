import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="Global Power Plants Dashboard", layout="wide")

# --- DB CONNECTION ---
conn = duckdb.connect("power_plants.duckdb")
conn.execute("SET schema 'main'")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    query = """
        SELECT *
        FROM fct_power_generation
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

# --- KPI SECTION ---
col1, col2, col3 = st.columns(3)

col1.metric("Total Generation (GWh)", int(filtered_df["generation_gwh"].sum()))
col2.metric("Number of Plants", filtered_df["plant_id"].nunique())
col3.metric("Countries", filtered_df["country_name"].nunique())

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

fig2 = px.pie(fuel_df, names="primary_fuel", values="generation_gwh")
st.plotly_chart(fig2, use_container_width=True)

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

# --- CHART 4: Data Quality ---
st.subheader("🧠 Data Quality (Source of Generation Data)")

quality_df = (
    filtered_df
    .groupby("generation_source")
    .size()
    .reset_index(name="count")
)

fig4 = px.bar(quality_df, x="generation_source", y="count")
st.plotly_chart(fig4, use_container_width=True)