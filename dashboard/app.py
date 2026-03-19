import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

# --- CONFIG ---
st.set_page_config(page_title="Global Power Plants Dashboard", layout="wide")

# --- THEME ---
st.markdown("""
    <style>
        .stApp {
            background-color: #0f1117;
        }
        [data-testid="stSidebar"] {
            background-color: #1c1e26;
        }
        [data-testid="stMetric"] {
            background-color: #1c1e26;
            border: 1px solid #00d4aa;
            border-radius: 8px;
            padding: 16px;
        }
        [data-testid="stMetricValue"] {
            color: #00d4aa;
        }
        html, body, [class*="css"] {
            color: #ffffff;
        }
        h1, h2, h3 {
            color: #00d4aa;
        }
    </style>
""", unsafe_allow_html=True)

# --- CHART THEME ---
CHART_THEME = dict(
    paper_bgcolor="#1c1e26",
    plot_bgcolor="#1c1e26",
    font_color="#ffffff",
    font=dict(family="sans serif"),
    xaxis=dict(gridcolor="#2e3348", zerolinecolor="#2e3348"),
    yaxis=dict(gridcolor="#2e3348", zerolinecolor="#2e3348")
)

COLORSCALE = ["#00d4aa", "#4f8ef7", "#f5a623", "#e05c5c", "#a78bfa", "#34d399", "#fb923c"]

# --- DB CONNECTION ---
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "dev.duckdb")
conn = duckdb.connect(DB_PATH, read_only=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        return conn.execute("SELECT * FROM main.fct_power_generation").df()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

df = load_data()

# --- DERIVE COLUMNS EARLY ---
renewables = ["Solar", "Wind", "Hydro", "Geothermal", "Wave and Tidal", "Biomass"]
df["energy_type"] = df["primary_fuel"].apply(
    lambda x: "Renewable" if x in renewables else "Non-Renewable"
)

# --- TITLE ---
st.title("⚡ Global Power Generation Dashboard")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

energy_type = st.sidebar.radio("Energy Type", ["All", "Renewable", "Non-Renewable"])

countries = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["country_name"].dropna().unique()),
    default=sorted(df["country_name"].dropna().unique())[:5]
)

fuels = st.sidebar.multiselect(
    "Select Fuel Type",
    options=sorted(df["primary_fuel"].dropna().unique()),
    default=sorted(df["primary_fuel"].dropna().unique())
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Data: {int(df['year'].min())}–{int(df['year'].max())}")
st.sidebar.caption(f"Total Plants: {df['plant_id'].nunique():,}")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- APPLY FILTERS ---
filtered_df = df[
    (df["country_name"].isin(countries)) &
    (df["primary_fuel"].isin(fuels))
]
if energy_type != "All":
    filtered_df = filtered_df[filtered_df["energy_type"] == energy_type]

# --- GUARD EMPTY RESULTS ---
if filtered_df.empty:
    st.warning("No data matches your current filters. Try adjusting the sidebar.")
    st.stop()

# --- UTILIZATION RATE ---
filtered_df = filtered_df.copy()
filtered_df["utilization_rate"] = filtered_df.apply(
    lambda row: (row["generation_gwh"] / (row["capacity_mw"] * 8.76)) * 100
    if row["capacity_mw"] > 0 else None, axis=1
).clip(0, 100)

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
fig1 = px.line(
    time_df, x="year", y="generation_gwh", markers=True,
    title="Total Generation Over Time",
    labels={"generation_gwh": "Generation (GWh)", "year": "Year"},
    color_discrete_sequence=COLORSCALE
)
fig1.update_layout(**CHART_THEME)
st.plotly_chart(fig1, use_container_width=True)

# --- CHART 2: Energy Mix by Fuel Type ---
st.subheader("🔥 Energy Mix by Fuel Type")
fuel_df = (
    filtered_df
    .groupby("primary_fuel")["generation_gwh"]
    .sum()
    .reset_index()
)
fig2 = px.pie(
    fuel_df, names="primary_fuel", values="generation_gwh",
    title="Energy Mix by Fuel Type",
    color_discrete_sequence=COLORSCALE
)
fig2.update_layout(**CHART_THEME)
st.plotly_chart(fig2, use_container_width=True)

# --- CHART 3: Generation Trend by Fuel Type ---
st.subheader("📊 Generation Trend by Fuel Type")
trend_df = filtered_df.groupby(["year", "primary_fuel"])["generation_gwh"].sum().reset_index()
fig_trend = px.line(
    trend_df, x="year", y="generation_gwh", color="primary_fuel", markers=True,
    title="Generation Trend by Fuel Type",
    labels={"generation_gwh": "Generation (GWh)", "year": "Year", "primary_fuel": "Fuel Type"},
    color_discrete_sequence=COLORSCALE
)
fig_trend.update_layout(**CHART_THEME)
st.plotly_chart(fig_trend, use_container_width=True)

# --- CHART 4: Top Power Plants ---
st.subheader("🏭 Top 10 Power Plants by Generation")
top_plants = (
    filtered_df
    .groupby("plant_name")["generation_gwh"]
    .sum()
    .reset_index()
    .sort_values(by="generation_gwh", ascending=False)
    .head(10)
)
fig3 = px.bar(
    top_plants, x="generation_gwh", y="plant_name", orientation="h",
    title="Top 10 Power Plants by Generation",
    labels={"generation_gwh": "Generation (GWh)", "plant_name": "Plant"},
    color_discrete_sequence=COLORSCALE
)
fig3.update_layout(**CHART_THEME)
st.plotly_chart(fig3, use_container_width=True)

# --- CHART 5: Capacity vs Generation ---
st.subheader("⚡ Capacity vs Actual Generation")
fig_scatter = px.scatter(
    filtered_df,
    x="capacity_mw", y="generation_gwh",
    color="primary_fuel",
    hover_name="plant_name",
    opacity=0.6,
    title="Capacity vs Actual Generation",
    labels={"capacity_mw": "Capacity (MW)", "generation_gwh": "Generation (GWh)", "primary_fuel": "Fuel Type"},
    color_discrete_sequence=COLORSCALE
)
fig_scatter.update_layout(**CHART_THEME)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- CHART 6: Top Countries by Capacity ---
st.subheader("🌍 Top Countries by Installed Capacity")
country_capacity = (
    filtered_df.groupby("country_name")["capacity_mw"]
    .sum().reset_index()
    .sort_values("capacity_mw", ascending=False)
    .head(15)
)
fig_cap = px.bar(
    country_capacity, x="country_name", y="capacity_mw",
    title="Top Countries by Installed Capacity (MW)",
    labels={"capacity_mw": "Capacity (MW)", "country_name": "Country"},
    color_discrete_sequence=COLORSCALE
)
fig_cap.update_layout(**CHART_THEME)
st.plotly_chart(fig_cap, use_container_width=True)

# --- CHART 7: Renewable vs Non-Renewable ---
st.subheader("🌱 Renewable vs Non-Renewable Generation")
fig_renew = px.pie(
    filtered_df, names="energy_type", values="generation_gwh",
    title="Renewable vs Non-Renewable Generation",
    color_discrete_sequence=["#00d4aa", "#e05c5c"]
)
fig_renew.update_layout(**CHART_THEME)
st.plotly_chart(fig_renew, use_container_width=True)

# --- CHART 8: Capacity Utilization Rate ---
st.subheader("📉 Capacity Utilization by Fuel Type")
fig_util = px.box(
    filtered_df, x="primary_fuel", y="utilization_rate",
    title="Capacity Utilization by Fuel Type (%)",
    labels={"utilization_rate": "Utilization Rate (%)", "primary_fuel": "Fuel Type"},
    color_discrete_sequence=COLORSCALE
)
fig_util.update_layout(**CHART_THEME)
st.plotly_chart(fig_util, use_container_width=True)

# --- CHART 9: Data Quality ---
st.subheader("🧠 Data Quality (Source of Generation Data)")
quality_df = (
    filtered_df
    .groupby("generation_source")
    .size()
    .reset_index(name="count")
)
fig4 = px.bar(
    quality_df, x="generation_source", y="count",
    title="Data Quality — Source of Generation Data",
    labels={"generation_source": "Source", "count": "Number of Records"},
    color_discrete_sequence=COLORSCALE
)
fig4.update_layout(**CHART_THEME)
st.plotly_chart(fig4, use_container_width=True)

# --- RAW DATA ---
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