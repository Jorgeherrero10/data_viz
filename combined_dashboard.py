import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Imports for Dashboard 1
import json
import folium
from streamlit_folium import st_folium
# import matplotlib.pyplot as plt # Not used directly in provided d1 code
from io import StringIO

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Madrid Housing Analysis")

# --- Initialize Session State ---
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard1' # Start on Dashboard 1
if 'selected_districts' not in st.session_state: # For Dashboard 1 map interaction
    st.session_state.selected_districts = []

# --- Placeholder Utils Functions (Replace with actual imports/definitions) ---
def bucket_1(df, district): return f"{np.random.uniform(1, 5):.1f}%" if district and district != "All" else f"{np.random.uniform(1, 5):.1f}%" # Simulate All
def bucket_2(df, district):
    if district and district != "All":
        # Simulate district-specific max
        return f"€{np.random.uniform(15, 25):.1f}"
    else:
        # Simulate overall max when 'All' or None is selected
        # In reality, you would calculate df['Rent_Price'].max() here
        return f"€{np.random.uniform(20, 26):.1f}"
def bucket_3(df, district): return f"#{np.random.randint(1, 10)}" if district and district != "All" else "N/A" # Ranking N/A for All
def bucket_4(df, district):
    if district and district != "All":
        # Simulate district-specific average
        return f"€{np.random.uniform(10, 20):.1f}"
    else:
        # Simulate overall average
        # In reality, calculate df['Rent_Price'].mean()
        return f"€{np.random.uniform(12, 18):.1f}"
def bucket_5(avg_rent_str, surface=100):
    try:
        rent_val = float(avg_rent_str.replace('€', ''))
        required = (rent_val * surface) / 0.40 # Assuming 40% of income for rent
        return f"{required:,.0f}"
    except:
        return "N/A"

# --- CSS Definitions ---
# CSS specific to Dashboard 1
css_dashboard1 = """
<style>
/* Add padding to the top of the page */
.main { padding-top: 50px !important; }
/* Title bar styling */
.title-bar { background-color: #dcef6e; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; margin-top: 20px; color: #333; font-size: 22px; font-weight: bold; display: flex; align-items: center; height: 45px; }
/* Override padding/margins for block containers */
div.block-container { padding-top: 30px !important; padding-bottom: 0 !important; margin-top: 10px !important; margin-bottom: 0 !important; }
/* Target column wrapper */
.css-1lcbmhc { padding: 0 !important; margin: 0 !important; }
/* Reduce padding/margins for chart/map containers */
.stPlotlyChart, .stFoliumMap, .stMetric { margin: 0 !important; padding: 0 !important; }
/* Pack containers tightly */
div[data-testid="stVerticalBlock"] > div { margin: 0 !important; padding: 0 !important; }
/* Hide default streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
"""

# CSS specific to Dashboard 2
css_dashboard2 = """
<style>
/* Add padding to the top of the page */
.main { padding-top: 50px !important; }
/* Title bar styling */
.title-bar { background-color: #dcef6e; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; margin-top: 20px; color: #333; font-size: 22px; font-weight: bold; display: flex; align-items: center; height: 45px; }
/* Remove extra padding and margin */
.block-container { padding-top: 30px !important; padding-bottom: 0 !important; margin-top: 10px !important; margin-bottom: 0 !important; }
.element-container { margin-bottom: 5px !important; }
[data-testid="stVerticalBlock"] { gap: 0px !important; }
/* Chart containers */
.chart-container { border: 1px solid #ddd; border-radius: 4px; padding: 5px; height: calc(100% - 10px); margin-bottom: 10px; }
/* Hide default streamlit footer */
footer { display: none !important; }
.stApp { height: 100vh !important; }
/* Adjust header margins */
h3 { margin-top: 0 !important; margin-bottom: 5px !important; font-size: 18px !important; }
/* Adjust metrics to be more compact */
[data-testid="stMetric"] { padding: 5px !important; }
[data-testid="stMetricLabel"] { margin-bottom: 0 !important; }
[data-testid="stMetricValue"] { margin-bottom: 0 !important; }
[data-testid="stMetricDelta"] { margin-top: 0 !important; }
/* Force content to fit in a single slide */
.main .block-container { max-height: calc(100vh - 20px) !important; overflow: hidden !important; }
/* Adjust plotly charts to be more compact */
.js-plotly-plot { margin-bottom: 0 !important; }
/* Remove extra padding from markdown */
.stMarkdown p { margin-bottom: 0 !important; }
/* KPI grid */
.kpi-grid { display: grid; grid-template-columns: 1fr 1fr; grid-gap: 5px; }
.kpi-item { padding: 5px; }
/* Radio buttons more compact */
.st-cc { padding-top: 0 !important; padding-bottom: 0 !important; }
/* Tab control more compact */
[data-testid="stHorizontalBlock"] { gap: 0 !important; padding-top: 0 !important; padding-bottom: 3px !important; }
</style>
"""

# CSS specific to Dashboard 3
css_dashboard3 = """
<style>
/* Add padding to the top of the page */
.main { padding-top: 50px !important; }
/* Title bar styling */
.title-bar { background-color: #dcef6e; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; margin-top: 20px; color: #333; font-size: 22px; font-weight: bold; display: flex; align-items: center; justify-content: center; text-align: center; height: 45px; }
/* Remove extra padding and margin */
.block-container { padding-top: 30px !important; padding-bottom: 0 !important; margin-top: 10px !important; margin-bottom: 0 !important; }
.element-container { margin-bottom: 5px !important; }
[data-testid="stVerticalBlock"] { gap: 0px !important; }
/* Chart containers */
.chart-container { border: 1px solid #ddd; border-radius: 4px; padding: 5px; height: calc(100% - 10px); margin-bottom: 10px; text-align: center; display: flex; flex-direction: column; align-items: center; }
/* Force Plotly to center its content */
.js-plotly-plot { margin: 0 auto !important; }
/* Center plot titles */
.js-plotly-plot .plotly .main-svg .g-gtitle { text-anchor: middle !important; }
/* Align axis titles */
.xtitle, .ytitle { text-anchor: middle !important; }
/* Hide default streamlit footer */
footer { display: none !important; }
.stApp { height: 100vh !important; }
/* Adjust header margins */
h3 { margin-top: 0 !important; margin-bottom: 5px !important; font-size: 18px !important; text-align: center; }
/* Adjust metrics to be more compact and centered */
[data-testid="stMetric"] { padding: 5px !important; text-align: center !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }
[data-testid="stMetricLabel"] { margin-bottom: 0 !important; text-align: center !important; width: 100%; justify-content: center !important; }
[data-testid="stMetricValue"] { margin-bottom: 0 !important; text-align: center !important; width: 100%; justify-content: center !important; }
[data-testid="stMetricDelta"] { margin-top: 0 !important; text-align: center !important; width: 100%; justify-content: center !important; }
/* Force content to fit */
.main .block-container { max-height: calc(100vh - 20px) !important; overflow: hidden !important; }
/* Adjust plotly charts */
.js-plotly-plot { margin-bottom: 0 !important; }
/* Remove extra padding from markdown and center */
.stMarkdown p { margin-bottom: 0 !important; text-align: center; }
/* KPI grid */
.kpi-grid { display: grid; grid-template-columns: 1fr 1fr; grid-gap: 5px; text-align: center; }
.kpi-item { padding: 5px; text-align: center; }
/* Radio buttons more compact and centered */
.st-cc { padding-top: 0 !important; padding-bottom: 0 !important; text-align: center; }
/* Tab control more compact */
[data-testid="stHorizontalBlock"] { gap: 0 !important; padding-top: 0 !important; padding-bottom: 3px !important; text-align: center; }
/* Center chart content and annotations */
.plotly .annotation-text { text-align: center !important; }
/* Center Analysis Insights box */
div[style*="background-color:#f8f9fa"] { text-align: center !important; }
div[style*="background-color:#f8f9fa"] ul { display: inline-block; text-align: left; }
/* Center Plotly SVG elements */
.svg-container { margin: 0 auto !important; }
/* Override specific chart elements */
g.infolayer { text-anchor: middle !important; }
/* Custom formatting for chart column containers */
[data-testid="column"] { display: flex; flex-direction: column; align-items: center; justify-content: center; }
/* Add more space at the top */
div.appview-container { margin-top: 15px; }
/* Selector dropdown styling */
div[data-baseweb="select"] { margin-bottom: 10px; }
/* Sankey text styling */
.js-plotly-plot .sankey .node text { fill: black !important; font-weight: bold !important; font-size: 14px !important; text-shadow: none !important; }
</style>
"""

# --- Data Definitions & Loading ---

# Data Loading for Dashboard 1
try:
    with open('data/DistritosMadrid.geojson', 'r', encoding='utf-8') as f:
        geojson_data_d1 = json.load(f)
except FileNotFoundError:
    st.error("GeoJSON file 'data/DistritosMadrid.geojson' not found.")
    geojson_data_d1 = None
except Exception as e:
    st.error(f"Error loading GeoJSON: {e}")
    geojson_data_d1 = None

try:
    df_prices_d1 = pd.read_csv('data/prices.csv')
    df_prices_d1['Date'] = pd.to_datetime(df_prices_d1['Date'])
    df_avg_d1 = df_prices_d1.groupby(['Date', 'District'])['Rent_Price'].mean().reset_index()
    overall_df_d1 = df_prices_d1.groupby('Date')['Rent_Price'].mean().reset_index()
    district_avgs_d1 = df_prices_d1.groupby('District')['Rent_Price'].mean().to_dict()
    min_rent_d1 = min(district_avgs_d1.values()) if district_avgs_d1 else 0
    max_rent_d1 = max(district_avgs_d1.values()) if district_avgs_d1 else 1
except FileNotFoundError:
    st.error("CSV file 'data/prices.csv' not found.")
    df_prices_d1 = pd.DataFrame(columns=['Date', 'District', 'Rent_Price'])
    df_avg_d1 = pd.DataFrame(columns=['Date', 'District', 'Rent_Price'])
    overall_df_d1 = pd.DataFrame(columns=['Date', 'Rent_Price'])
    district_avgs_d1 = {}
    min_rent_d1, max_rent_d1 = 0, 1
except Exception as e:
    st.error(f"Error loading or processing 'prices.csv': {e}")
    df_prices_d1 = pd.DataFrame(columns=['Date', 'District', 'Rent_Price'])
    df_avg_d1 = pd.DataFrame(columns=['Date', 'District', 'Rent_Price'])
    overall_df_d1 = pd.DataFrame(columns=['Date', 'Rent_Price'])
    district_avgs_d1 = {}
    min_rent_d1, max_rent_d1 = 0, 1

try:
    df_youth_d1 = pd.read_csv("data/Youth_Salary_vs_Rent_Prices.csv")
except FileNotFoundError:
    st.error("CSV file 'data/Youth_Salary_vs_Rent_Prices.csv' not found.")
    df_youth_d1 = pd.DataFrame(columns=['Year', 'Average_Youth_Salary', 'Average_Monthly_Rent'])
except Exception as e:
    st.error(f"Error loading 'Youth_Salary_vs_Rent_Prices.csv': {e}")
    df_youth_d1 = pd.DataFrame(columns=['Year', 'Average_Youth_Salary', 'Average_Monthly_Rent'])

data_radar_d1 = """Year;Access to Housing;Unemployment;Political Issues;Job Quality;Immigration;Economic Crisis
2014;5;8;6;7;4;7
2024;9;7;6;7;5;6"""
try:
    df_radar_d1 = pd.read_csv(StringIO(data_radar_d1), delimiter=';')
except Exception as e:
    st.error(f"Error processing radar chart data: {e}")
    df_radar_d1 = pd.DataFrame(columns=['Year', 'Access to Housing', 'Unemployment', 'Political Issues', 'Job Quality', 'Immigration', 'Economic Crisis'])

# Data for Dashboard 2
districts_d2 = [
    "Salamanca", "Centro", "Chamberí", "Chamartín", "Arganzuela",
    "Tetuán", "Retiro", "Moncloa-Aravaca", "Fuencarral-El Pardo", "Usera"
]
before_control_d2 = np.array([25, 24, 23, 22, 20, 18, 21, 19, 17, 16])
after_control_d2 = np.array([21, 20, 20, 19, 18, 16, 18, 17, 15, 14])
reduction_percent_d2 = ((before_control_d2 - after_control_d2) / before_control_d2) * 100
scenario_data_d2 = pd.DataFrame({
    "District": districts_d2,
    "Before Control (€/m²)": before_control_d2,
    "After Control (€/m²)": after_control_d2,
    "Reduction (%)": reduction_percent_d2
})
incentive_levels_d2 = ['No Incentives', 'Partial Incentives', 'Full Incentives']
participation_rates_d2 = [10, 40, 70]
rent_increase_d2 = [5.0, 3.0, 1.5]
net_benefit_d2 = [0, 3000, 5873]
tenant_categories_d2 = ["Low-Income Renters", "Middle-Income Renters", "Young Professionals"]
before_burden_d2 = [51.7, 35.4, 41.2]
after_burden_d2 = [39.4, 25.9, 30.9]
improvement_d2 = [(b-a)/b*100 for b, a in zip(before_burden_d2, after_burden_d2)]
operational_data_d2 = {
    "District": districts_d2,
    "Current Rent (€/m²)": before_control_d2,
    "Priority Score": [9, 8, 8, 7, 6, 5, 7, 6, 5, 4],
    "Implementation Timeline (months)": [1, 1, 1.5, 2, 3, 3, 2.5, 2, 4, 4],
    "Incentive Level": ["High", "High", "High", "Medium", "Medium", "Low", "Medium", "Medium", "Low", "Low"]
}
ops_df_d2 = pd.DataFrame(operational_data_d2)
districts_subset_d2 = ["Salamanca", "Centro", "Chamberí", "Retiro", "Arganzuela"]
youth_before_d2 = [42.5, 39.3, 39.9, 44.4, 41.2]
youth_after_d2 = [29.7, 29.0, 30.3, 31.6, 30.0]
low_income_before_d2 = [54.9, 52.8, 54.6, 52.0, 46.0]
low_income_after_d2 = [44.9, 41.4, 41.8, 40.2, 33.6]

# Data for Dashboard 3
sankey_data_d3 = {
    'node_labels': ["Total Housing Budget", "Tax Incentives", "Remaining Budget",
                    "Affordable Housing Programs", "Rental Assistance", "Other Housing Initiatives"],
    'node_colors': ["#3498db", "#e74c3c", "#2980b9", "#27ae60", "#8e44ad", "#f39c12"],
    'link_sources': [0, 0, 2, 2, 2],
    'link_targets': [1, 2, 3, 4, 5],
    'link_values': [27.8, 72.2, 24, 28.2, 20],
    'link_colors': ["rgba(231, 76, 60, 0.4)", "rgba(41, 128, 185, 0.4)",
                    "rgba(39, 174, 96, 0.4)", "rgba(142, 68, 173, 0.4)", "rgba(243, 156, 18, 0.4)"]
}
waterfall_data_d3 = {
    'measures': ['relative', 'relative', 'total'],
    'labels': ['Tax Savings', 'Rent Reduction', 'Net Gain'],
    'text_values': ['€7,313', '−€1,440', '€5,873'],
    'values': [7312.68, -1440, None]
}
years_d3 = list(range(2025, 2035))
current_property_tax_d3 = 500
social_impact_d3 = 25.2
np.random.seed(42)
incentive_amounts_d3 = np.linspace(0, 10000, 20)
base_participation_d3 = 5
noise_d3 = np.random.normal(0, 5, 20)
participation_rates_d3 = np.clip(base_participation_d3 + incentive_amounts_d3 * 0.006 + noise_d3, 0, 100)
correlation_d3 = np.corrcoef(incentive_amounts_d3, participation_rates_d3)[0, 1]
r_squared_d3 = correlation_d3 ** 2
districts_d3 = [
    "Salamanca", "Centro", "Chamberí", "Chamartín", "Arganzuela",
    "Tetuán", "Retiro", "Moncloa-Aravaca", "Fuencarral-El Pardo", "Usera"
]
affordability_improvement_d3 = [30.1, 26.5, 24.3, 23.7, 20.5, 19.8, 22.1, 21.5, 18.7, 17.2]
incentive_cost_d3 = [235, 220, 210, 190, 160, 150, 180, 175, 140, 125]
implementation_complexity_d3 = [4, 4, 3, 3, 2, 2, 3, 3, 2, 1]
roi_ratio_d3 = [a/c * 100 for a, c in zip(affordability_improvement_d3, np.array(incentive_cost_d3)/100)]
district_analysis_d3 = pd.DataFrame({
    'District': districts_d3,
    'Affordability Improvement (%)': affordability_improvement_d3,
    'Incentive Cost (€/unit)': incentive_cost_d3,
    'Implementation Complexity': implementation_complexity_d3,
    'ROI Ratio': roi_ratio_d3
})

# --- Helper Functions ---
# Helper for Dashboard 1 Map
def get_color_d1(val, min_val, max_val):
    """Compute a hex color (red scale) based on the normalized value."""
    if max_val > min_val:
        norm = (val - min_val) / (max_val - min_val)
    else:
        norm = 0
    red_level = int(norm * 255)
    return f"#{red_level:02x}0000"

def toggle_district_d1(district):
    """Toggle a district in the session state for D1 map interaction."""
    if district in st.session_state.selected_districts:
        st.session_state.selected_districts.remove(district)
    else:
        st.session_state.selected_districts.append(district)

# Reset functions (can be expanded later)
def reset_filters_d1(): pass
def reset_filters_d2(): pass
def reset_filters_d3(): pass

# --- Dashboard 1: Strategic Overview ---
def display_dashboard1_sidebar():
    with st.sidebar:
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.header("Filters", anchor="d1_filters")
        district_list = sorted(df_prices_d1['District'].unique())
        selected_districts = st.multiselect(
            "Select Districts (Map/Line)",
            options=district_list,
            default=st.session_state.selected_districts,
            help="Select districts to filter the line chart and highlight on the map.",
            key="d1_districts_multiselect"
        )
        # Update session state based on multiselect interaction
        st.session_state.selected_districts = selected_districts

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("KPI Filter")
        kpi_district = st.selectbox(
            "Select District for KPIs",
            options=["All"] + district_list,
            index=0,
            key="d1_kpi_district_selectbox"
        )
        # Note: required_income_district filter is moved to main content area in d1
        return kpi_district

def display_dashboard1_content(kpi_district):
    col1, col2 = st.columns(2)

    with col1:
        # --- Container 1: Line Chart ---
        with st.container():
            df_line_d1 = df_avg_d1.copy()
            if st.session_state.selected_districts:
                df_line_d1 = df_avg_d1[df_avg_d1['District'].isin(st.session_state.selected_districts)]
                line_title = "Average Rent Price by Date - " + ", ".join(st.session_state.selected_districts)
                default_opacity = 1
                overall_opacity = 0.2
            else:
                line_title = "Average Rent Price by Date (All Districts)"
                default_opacity = 0.5
                overall_opacity = 1

            fig_line = px.line(df_line_d1, x="Date", y="Rent_Price", color="District", title=line_title)
            if not overall_df_d1.empty:
                fig_line.add_trace(
                    go.Scatter(
                        x=overall_df_d1['Date'], y=overall_df_d1['Rent_Price'], mode='lines',
                        name='Overall Mean', line=dict(dash='dash', color='black'), opacity=overall_opacity
                    )
                )
            fig_line.update_layout(
                yaxis_title="Rent Price (€ per M²)",
                yaxis_range=[7, 26],
                xaxis_range=[pd.to_datetime('2008-08-01'), df_prices_d1['Date'].max() if not df_prices_d1.empty else pd.to_datetime('today')],
                margin=dict(l=40, r=20, t=50, b=10), height=250, legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

        # --- Container 2: Map ---
        with st.container():
            m = folium.Map(location=[40.417101, -3.695899], zoom_start=10, tiles="cartodbpositron")
            if geojson_data_d1:
                for feature in geojson_data_d1['features']:
                    district_name = feature['properties'].get('NOMBRE', 'Unknown')
                    avg_rent = district_avgs_d1.get(district_name, min_rent_d1)
                    fill_color = get_color_d1(avg_rent, min_rent_d1, max_rent_d1)
                    folium.GeoJson(
                        feature,
                        style_function=lambda x, fill_color=fill_color: {
                            'fillColor': fill_color,
                            'color': 'gray', 'weight': 1, 'fillOpacity': 0.6,
                        },
                        popup=district_name,
                        tooltip=folium.GeoJsonTooltip(fields=["NOMBRE"], aliases=["District:"]),
                        highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.9},
                    ).add_to(m)
                legend_html = """
                <div style="position: absolute; bottom: 10px; left: 10px; width: 150px; z-index:9999; font-size:12px; background-color:white; border:1px solid grey; padding:5px;">
                <div style="text-align:center; margin-bottom: 5px;"><b>Avg Rent (€/m²)</b></div>
                <div style="width:100%; height:10px; background: linear-gradient(to right, #000000, #ff0000); margin-bottom: 3px;"></div>
                <div style="font-size:10px;">{min_rent_d1:.1f}<span style="float:right;">{max_rent_d1:.1f}</span></div>
                </div>
                """.format(min_rent_d1=min_rent_d1, max_rent_d1=max_rent_d1)
                m.get_root().html.add_child(folium.Element(legend_html))

            # Use a unique key for the map
            map_result = st_folium(m, key="d1_map", width=700, height=250)
            if map_result and map_result.get("last_object_clicked") is not None:
                clicked = map_result["last_object_clicked"]
                district_clicked = clicked.get("popup")
                if district_clicked:
                    toggle_district_d1(district_clicked)
                    st.rerun() # Use rerun instead of experimental_rerun

        # --- Container 3: Buckets (4 Metrics) ---
        with st.container():
            bucket1_col, bucket2_col, bucket3_col, bucket4_col = st.columns(4)
            # kpi_district_val = kpi_district if kpi_district != "All" else None # REMOVED THIS LINE
            with bucket1_col:
                # Pass kpi_district directly
                value1 = bucket_1(df_prices_d1, kpi_district)
                st.metric(label="CAGR", value=value1)
                st.caption("Annual growth rate (%)")
            with bucket2_col:
                # Pass kpi_district directly
                value2 = bucket_2(df_prices_d1, kpi_district)
                st.metric(label="Max Rental", value=value2)
                st.caption("Max Rent recorded (€/m²)")
            with bucket3_col:
                # Pass kpi_district directly
                value3 = bucket_3(df_prices_d1, kpi_district)
                st.metric(label="Ranking", value=value3)
                st.caption("Rank by Avg Rent Price")
            with bucket4_col:
                # Pass kpi_district directly
                value4 = bucket_4(df_prices_d1, kpi_district)
                st.metric(label="Avg Rent Price", value=value4)
                st.caption("Average Rent Price (€/m²)")

    with col2:
        # --- Graph 1: Youth Salary vs Rent Prices ---
        fig1 = go.Figure()
        if not df_youth_d1.empty:
            fig1.add_trace(go.Bar(x=df_youth_d1["Year"], y=df_youth_d1["Average_Youth_Salary"], name="Avg Youth Salary", marker_color="lightgray"))
            fig1.add_trace(go.Bar(x=df_youth_d1["Year"], y=df_youth_d1["Average_Monthly_Rent"], name="Avg Monthly Rent", marker_color="#dcef6e"))
            fig1.add_trace(go.Scatter(x=df_youth_d1["Year"], y=df_youth_d1["Average_Youth_Salary"], mode="lines+markers", name="Salary Trend", line=dict(color="darkgray")))
            fig1.add_trace(go.Scatter(x=df_youth_d1["Year"], y=df_youth_d1["Average_Monthly_Rent"], mode="lines+markers", name="Rent Trend", line=dict(color="#b0c74a")))
        fig1.update_layout(
            barmode="group", xaxis_title="Year", yaxis_title="Amount in €", title="Average Youth Salary vs Average Monthly Rent Prices",
            xaxis_tickangle=-45, yaxis_range=[600, 1200] if not df_youth_d1.empty else [0,1], margin=dict(l=40, r=20, t=50, b=40), height=250,
            legend=dict(font=dict(size=10))
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        col4, col5 = st.columns([1,2])
        with col4:
            # --- New Filter and Bucket: Required Income --- Moved from sidebar
            with st.container():
                district_list_req = sorted(df_prices_d1['District'].unique())
                required_income_district = st.selectbox(
                    "District for Req. Income",
                    options=["All"] + district_list_req,
                    index=0,
                    key="d1_required_income_district_selectbox"
                )
                # Pass required_income_district directly to bucket_4 for calculation
                avg_rent_price_str = bucket_4(df_prices_d1, required_income_district)
                required_income = bucket_5(avg_rent_price_str, surface=100)
                st.metric(label=f"Req. Income (100m²) - {required_income_district}", value=f"€{required_income}")
                st.caption("Net income (40% rent)")
        with col5:
            # --- Graph 2: Comparison: Madrid vs Europe --- Moved from d1
            df_bar_d1 = pd.DataFrame({"Region": ["Madrid", "Europe"], "Percentage": [60, 40]})
            fig2 = px.bar(df_bar_d1, x="Percentage", y="Region", orientation="h", text="Percentage", title="Rent Burden: Madrid vs Europe")
            fig2.update_traces(texttemplate='%{text}%', textposition='outside')
            fig2.update_layout(xaxis_range=[0, 100], yaxis={'categoryorder':'total ascending'}, margin=dict(l=40, r=20, t=50, b=40), height=150, legend=dict(font=dict(size=10)))
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        # --- Graph 3: Concerns Comparison Radar Chart ---
        st.markdown("<h6>Concerns Comparison (2014 vs 2024)</h6>", unsafe_allow_html=True)
        fig3 = go.Figure()
        if not df_radar_d1.empty:
            categories = list(df_radar_d1.columns[1:])
            for index, row in df_radar_d1.iterrows():
                values = row[categories].tolist()
                values += values[:1]
                cats = categories + [categories[0]]
                fig3.add_trace(go.Scatterpolar(r=values, theta=cats, fill='toself', name=str(row['Year'])))
        fig3.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True, margin=dict(l=40, r=20, t=50, b=40), height=250, legend=dict(font=dict(size=10))
        )
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    # Footer for Dashboard 1 (optional, can be standardized)
    st.markdown(f"""
    <div style="background-color:#f0f0f0; padding:5px; border-radius:3px; margin-top:15px; font-size:0.6em; text-align:center;">
    Data Sources: INE, CIS, Madrid Data Portal | District KPI: {kpi_district} | Map/Line Selection: {len(st.session_state.selected_districts) if st.session_state.selected_districts else 'All'}
    </div>
    """, unsafe_allow_html=True)

# --- Dashboard 2: Tactical Decisions ---
def display_dashboard2_sidebar():
    with st.sidebar:
        st.header("Implementation Controls")
        selected_districts = st.multiselect("Select districts to analyze:", districts_d2, default=[], key="d2_districts")
        incentive_level = st.select_slider("Incentive level for landlords:", options=incentive_levels_d2, value="Full Incentives", key="d2_incentive_level")
        implementation_timeline = st.slider("Timeline (months):", min_value=1, max_value=12, value=4, step=1, key="d2_timeline")
        st.subheader("Additional Filters")
        tenant_category = st.multiselect("Tenant categories to analyze:", tenant_categories_d2, default=["Low-Income Renters", "Young Professionals"], key="d2_tenant_category")
        st.button("Reset All Filters", on_click=reset_filters_d2, key="d2_reset")
        return selected_districts, incentive_level, implementation_timeline, tenant_category

def display_dashboard2_content(selected_districts, incentive_level, implementation_timeline, tenant_category):
    # Update data based on selections
    incentive_index = incentive_levels_d2.index(incentive_level)
    selected_participation = participation_rates_d2[incentive_index]
    selected_rent_increase = rent_increase_d2[incentive_index]
    selected_benefit = net_benefit_d2[incentive_index]

    if selected_districts:
        scenario_data_filtered = scenario_data_d2[scenario_data_d2['District'].isin(selected_districts)]
        ops_df_filtered = ops_df_d2[ops_df_d2['District'].isin(selected_districts)]
    else:
        scenario_data_filtered = scenario_data_d2
        ops_df_filtered = ops_df_d2

    # Filter to only include selected districts that are also in the subset for district-specific impact
    available_districts = [d for d in selected_districts if d in districts_subset_d2]
    if not available_districts and selected_districts: # Only filter if selection is made
        district_impact = pd.DataFrame(columns=["District", "Youth Before", "Youth After", "Low-Income Before", "Low-Income After"]) # Empty DF
    elif not selected_districts: # Show all if no selection
         available_districts = districts_subset_d2
         district_indices = [districts_subset_d2.index(d) for d in available_districts]
         district_impact = pd.DataFrame({
            "District": [districts_subset_d2[i] for i in district_indices],
            "Youth Before": [youth_before_d2[i] for i in district_indices],
            "Youth After": [youth_after_d2[i] for i in district_indices],
            "Low-Income Before": [low_income_before_d2[i] for i in district_indices],
            "Low-Income After": [low_income_after_d2[i] for i in district_indices]
         })
    else: # Filter based on selection
        district_indices = [districts_subset_d2.index(d) for d in available_districts]
        district_impact = pd.DataFrame({
            "District": [districts_subset_d2[i] for i in district_indices],
            "Youth Before": [youth_before_d2[i] for i in district_indices],
            "Youth After": [youth_after_d2[i] for i in district_indices],
            "Low-Income Before": [low_income_before_d2[i] for i in district_indices],
            "Low-Income After": [low_income_after_d2[i] for i in district_indices]
        })


    # Main dashboard layout
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # Top left: KPIs
    with row1_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        avg_before = np.mean(before_control_d2)
        avg_after = np.mean(after_control_d2)
        avg_burden_before = np.mean(before_burden_d2)
        avg_burden_after = np.mean(after_burden_d2)
        priority_districts = len([d for d in ops_df_filtered['Priority Score'] if d >= 8]) if not ops_df_filtered.empty else 0

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-item">
                <h5>Average Rent Price</h5>
                <div style="font-size:1.8em; font-weight:bold;">{avg_after:.1f} €/m²</div>
                <div style="color:green; font-size:0.9em;">-{avg_before - avg_after:.1f} €/m²</div>
            </div>
            <div class="kpi-item">
                <h5>Landlord Participation</h5>
                <div style="font-size:1.8em; font-weight:bold;">{selected_participation}%</div>
                <div style="color:green; font-size:0.9em;">+{selected_participation}%</div>
            </div>
            <div class="kpi-item">
                <h5>Affordability Impact</h5>
                <div style="font-size:1.8em; font-weight:bold;">{avg_burden_after:.1f}%</div>
                <div style="color:green; font-size:0.9em;">-{avg_burden_before - avg_burden_after:.1f}%</div>
            </div>
            <div class="kpi-item">
                <h5>Implementation Priority</h5>
                <div style="font-size:1.8em; font-weight:bold; position: relative; top: -23px;">{priority_districts}</div>
                <div style="font-size:0.9em; position: relative; top: -25px;">High Priority Districts</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background-color:#f8f9fa; padding:5px; border-radius:4px; margin-top:5px; font-size:0.8em;">
        <b>Selected: {incentive_level}</b> | Participation: {selected_participation}% | Rent Increase: {selected_rent_increase}% | Benefit: €{selected_benefit:,}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Top right: Rent Price Impact Chart
    with row1_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_comparison = go.Figure()
        if not scenario_data_filtered.empty:
            fig_comparison.add_trace(go.Bar(
                x=scenario_data_filtered["District"], y=scenario_data_filtered["Before Control (€/m²)"],
                name="Before Control", marker_color='#ff7f0e'
            ))
            fig_comparison.add_trace(go.Bar(
                x=scenario_data_filtered["District"], y=scenario_data_filtered["After Control (€/m²)"],
                name="After Control", marker_color='#2ca02c'
            ))
            fig_comparison.add_trace(go.Scatter(
                x=scenario_data_filtered["District"], y=scenario_data_filtered["Reduction (%)"],
                mode='lines+markers', name='Reduction (%)', yaxis='y2',
                line=dict(color='red', width=2), marker=dict(size=6)
            ))
        fig_comparison.update_layout(
            title=dict(text="Rent Price Impact by District", y=1, x=0.5, xanchor='center', yanchor='top', pad=dict(t=15, b=10)),
            xaxis_title=None, yaxis_title="Rent Price (€/m²)",
            yaxis2=dict(title="Reduction (%)", overlaying="y", side="right", range=[0, max(reduction_percent_d2) * 1.2]),
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=250, margin=dict(l=30, r=30, t=60, b=40), font=dict(size=10)
        )
        st.plotly_chart(fig_comparison, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Left: Landlord Incentives Chart
    with row2_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_incentives = make_subplots(specs=[[{"secondary_y": True}]])
        fig_incentives.add_trace(go.Bar(
            x=incentive_levels_d2, y=participation_rates_d2, name="Landlord Participation",
            marker_color='#1f77b4', text=[f"{rate}%" for rate in participation_rates_d2],
            textposition='auto', textfont=dict(size=9)
        ), secondary_y=False)
        fig_incentives.add_trace(go.Scatter(
            x=incentive_levels_d2, y=rent_increase_d2, name="Rent Increase", mode='lines+markers',
            line=dict(color='red', width=2), marker=dict(size=8)
        ), secondary_y=True)
        fig_incentives.add_shape(
            type="rect", x0=incentive_levels_d2.index(incentive_level) - 0.4, x1=incentive_levels_d2.index(incentive_level) + 0.4,
            y0=0, y1=participation_rates_d2[incentive_levels_d2.index(incentive_level)] + 5,
            line=dict(color="blue", width=2), fillcolor="rgba(0, 123, 255, 0.3)"
        )
        for i, level in enumerate(incentive_levels_d2):
            if net_benefit_d2[i] > 0:
                font_size = 12 if level == incentive_level else 10
                font_color = "black" if level == incentive_level else "white"
                bg_color = "rgba(255, 255, 0, 0.7)" if level == incentive_level else None
                fig_incentives.add_annotation(
                    x=level, y=participation_rates_d2[i]/2, text=f"€{net_benefit_d2[i]:,}", showarrow=False,
                    font=dict(size=font_size, color=font_color, family="Arial"), bgcolor=bg_color,
                    borderpad=2 if level == incentive_level else 0
                )
        fig_incentives.update_layout(
            title=dict(text="Landlord Participation & Incentives", y=1, x=0.5, xanchor='center', yanchor='top', pad=dict(t=15, b=10)),
            xaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
            height=250, margin=dict(l=30, r=30, t=60, b=30), font=dict(size=10)
        )
        fig_incentives.update_yaxes(title_text="Participation Rate (%)", secondary_y=False)
        fig_incentives.update_yaxes(title_text="Rent Increase (%)", secondary_y=True, range=[0, 6])
        st.plotly_chart(fig_incentives, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Right: Implementation Strategy / Affordability Impact
    with row2_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        selected_tab = st.radio("Select View:", ["Implementation Strategy", "General Affordability", "District Affordability"], horizontal=True, key="d2_tab_select")
        if selected_tab == "Implementation Strategy":
            fig_ops = px.scatter(
                ops_df_filtered, x="Implementation Timeline (months)", y="Priority Score",
                size="Current Rent (€/m²)", color="Incentive Level", hover_name="District", text="District",
                size_max=30, color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"}
            ) if not ops_df_filtered.empty else go.Figure()
            if not ops_df_filtered.empty:
                fig_ops.add_shape(type="line", x0=implementation_timeline, y0=0, x1=implementation_timeline, y1=10, line=dict(color="blue", width=2, dash="dot"))
                fig_ops.add_annotation(x=implementation_timeline, y=9.5, text=f"Target: {implementation_timeline} mo", showarrow=True, arrowhead=1, ax=20, ay=-20, font=dict(size=10))
                fig_ops.update_traces(textposition='top center', marker=dict(opacity=0.8, line=dict(width=1, color='black')), textfont=dict(size=8))
            fig_ops.update_layout(title="Implementation Strategy by District", xaxis_title=None, yaxis_title="Priority Score", legend_title="Incentive Level", height=250, margin=dict(l=30, r=30, t=40, b=30), font=dict(size=10), legend=dict(font=dict(size=9)))
            st.plotly_chart(fig_ops, use_container_width=True, config={'displayModeBar': False})
        elif selected_tab == "General Affordability":
            affordability_data = pd.DataFrame({"Tenant Category": tenant_categories_d2, "Before Control (%)": before_burden_d2, "After Control (%)": after_burden_d2, "Improvement (%)": improvement_d2})
            affordability_data_filtered = affordability_data[affordability_data["Tenant Category"].isin(tenant_category)] if tenant_category else affordability_data
            fig_afford = go.Figure()
            if not affordability_data_filtered.empty:
                fig_afford.add_trace(go.Bar(x=affordability_data_filtered["Tenant Category"], y=affordability_data_filtered["Before Control (%)"], name="Before", marker_color="#d62728", text=affordability_data_filtered["Before Control (%)"].apply(lambda x: f"{x:.1f}%"), textposition="auto", textfont=dict(size=9)))
                fig_afford.add_trace(go.Bar(x=affordability_data_filtered["Tenant Category"], y=affordability_data_filtered["After Control (%)"], name="After", marker_color="#2ca02c", text=affordability_data_filtered["After Control (%)"].apply(lambda x: f"{x:.1f}%"), textposition="auto", textfont=dict(size=9)))
                for i, cat in enumerate(affordability_data_filtered["Tenant Category"]):
                    idx = affordability_data[affordability_data["Tenant Category"] == cat].index[0]
                    fig_afford.add_annotation(x=cat, y=after_burden_d2[idx] - 3, text=f"↓{improvement_d2[idx]:.1f}%", showarrow=False, font=dict(size=9, color="black"))
            fig_afford.update_layout(title="Impact on Housing Affordability", xaxis_title=None, yaxis_title="% Income on Rent", barmode="group", yaxis=dict(range=[0, max(before_burden_d2) * 1.1]), height=250, margin=dict(l=30, r=30, t=40, b=30), font=dict(size=10), legend=dict(orientation="h", y=1.02, x=1, font=dict(size=9)))
            st.plotly_chart(fig_afford, use_container_width=True, config={'displayModeBar': False})
        else:
            categories_to_show = []
            if "Young Professionals" in tenant_category: categories_to_show.extend([("Youth Before", "#ff9999"), ("Youth After", "#99ff99")])
            if "Low-Income Renters" in tenant_category: categories_to_show.extend([("Low-Income Before", "#ffcc99"), ("Low-Income After", "#99ccff")])
            if not categories_to_show: categories_to_show = [("Youth Before", "#ff9999"), ("Youth After", "#99ff99"), ("Low-Income Before", "#ffcc99"), ("Low-Income After", "#99ccff")]
            fig_district = go.Figure()
            if not district_impact.empty:
                for cat, color in categories_to_show:
                    if cat in district_impact.columns:
                         fig_district.add_trace(go.Bar(x=district_impact["District"], y=district_impact[cat], name=cat, marker_color=color, text=district_impact[cat].apply(lambda x: f"{x:.1f}%"), textposition="auto", textfont=dict(size=9)))
            fig_district.update_layout(title="District-Specific Affordability Impact", xaxis_title=None, yaxis_title="% Income on Rent", barmode="group", height=250, margin=dict(l=30, r=30, t=40, b=30), font=dict(size=10), legend=dict(orientation="h", y=1.02, x=1, font=dict(size=9)))
            st.plotly_chart(fig_district, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer for Dashboard 2
    st.markdown(f"""
    <div style="background-color:#f0f0f0; padding:5px; border-radius:3px; margin-top:15px; font-size:0.6em; text-align:center;">
    Data Sources: Madrid Data Portal, CIS Survey 2014, El Confidencial (2024) | Settings: {incentive_level} | Districts: {len(selected_districts) if selected_districts else "All"}
    </div>
    """, unsafe_allow_html=True)

# --- Dashboard 3: Analytical Insights ---
def display_dashboard3_sidebar():
    with st.sidebar:
        st.header("Analysis Controls")
        incentive_budget = st.slider("Incentive Budget (% of total)", min_value=20.0, max_value=40.0, value=27.8, step=0.1, help="Percentage of total housing budget allocated to incentives", key="d3_incentive_budget")
        tax_savings = st.slider("Tax Savings per Landlord (€)", min_value=5000, max_value=9000, value=7313, step=100, help="Average tax savings per participating landlord", key="d3_tax_savings")
        growth_rate_without = st.slider("Base Growth Rate (%)", min_value=1.0, max_value=3.0, value=2.0, step=0.1, help="Annual growth rate without program", key="d3_growth_without") / 100
        growth_rate_with = st.slider("Enhanced Growth Rate (%)", min_value=growth_rate_without*100 + 0.1, max_value=5.0, value=3.0, step=0.1, help="Annual growth rate with program", key="d3_growth_with") / 100
        selected_districts = st.multiselect("Select Districts for Analysis", districts_d3, default=[], help="Select specific districts to focus the analysis on", key="d3_districts")
        analysis_view = st.radio("District Analysis View", ["Quadrant Analysis", "Heatmap Analysis"], index=0, key="d3_analysis_view")
        st.button("Reset Filters", on_click=reset_filters_d3, key="d3_reset")
        return incentive_budget, tax_savings, growth_rate_without, growth_rate_with, selected_districts, analysis_view

def display_dashboard3_content(incentive_budget, tax_savings, growth_rate_without, growth_rate_with, selected_districts, analysis_view):
    # --- Recalculation of Values based on Sidebar ---
    remaining_budget = 100 - incentive_budget
    updated_remaining_values = [
        remaining_budget * 24/72.2 if remaining_budget > 0 else 0,
        remaining_budget * 28.2/72.2 if remaining_budget > 0 else 0,
        remaining_budget * 20/72.2 if remaining_budget > 0 else 0
    ]
    rent_reduction = -1440
    updated_net_gain = tax_savings + rent_reduction
    updated_revenue_without = [current_property_tax_d3 * (1 + growth_rate_without)**t for t in range(10)]
    updated_revenue_with = [current_property_tax_d3 * (1 + growth_rate_with)**t for t in range(10)]
    updated_revenue_diff = [with_ - without_ for with_, without_ in zip(updated_revenue_with, updated_revenue_without)]
    updated_cumulative_diff = sum(updated_revenue_diff)
    safe_incentive_budget = incentive_budget if incentive_budget > 0 else 1
    updated_roi = (updated_cumulative_diff / safe_incentive_budget) * 100
    updated_cumulative_revenue_diff = np.cumsum(updated_revenue_diff)
    years_to_payback = np.searchsorted(updated_cumulative_revenue_diff, safe_incentive_budget)
    if years_to_payback >= len(updated_cumulative_revenue_diff):
        updated_payback_period = 10.0 + (safe_incentive_budget - updated_cumulative_revenue_diff[-1]) / (updated_revenue_diff[-1] if updated_revenue_diff[-1] != 0 else 1) if len(updated_cumulative_revenue_diff)>0 else 10.0
        updated_payback_period = max(10.0, updated_payback_period)
    else:
        if years_to_payback == 0:
            updated_payback_period = safe_incentive_budget / updated_cumulative_revenue_diff[0] if updated_cumulative_revenue_diff[0] != 0 else float('inf')
        else:
            prev_cumulative = updated_cumulative_revenue_diff[years_to_payback-1] if years_to_payback > 0 else 0
            remaining = safe_incentive_budget - prev_cumulative
            year_diff = updated_cumulative_revenue_diff[years_to_payback] - prev_cumulative
            updated_payback_period = years_to_payback + (remaining / year_diff) if year_diff != 0 else float('inf')
    updated_payback_period = min(updated_payback_period, 50)

    safe_revenue_without_last = updated_revenue_without[-1] if updated_revenue_without[-1] != 0 else 1
    updated_revenue_growth = ((updated_revenue_with[-1] / safe_revenue_without_last) - 1) * 100

    if selected_districts:
        filtered_district_analysis = district_analysis_d3[district_analysis_d3['District'].isin(selected_districts)]
    else:
        filtered_district_analysis = district_analysis_d3

    # --- KPIs Display ---
    kpi_placeholder = st.empty()
    with kpi_placeholder.container():
        kpi_cols = st.columns(4)
        with kpi_cols[0]: st.metric(label="10-Year ROI", value=f"{updated_roi:.1f}%", delta=f"{updated_roi - 100:.1f}% vs Initial" if updated_roi is not None else "N/A")
        with kpi_cols[1]: st.metric(label="Payback Period", value=f"{updated_payback_period:.1f} years" if updated_payback_period != float('inf') else ">50 years", delta=f"{5 - updated_payback_period:.1f} vs Target" if updated_payback_period != float('inf') else None, delta_color="inverse")
        with kpi_cols[2]: st.metric(label="Revenue Growth", value=f"{updated_revenue_growth:.1f}%", delta=f"{updated_revenue_growth:.1f}% Boost")
        with kpi_cols[3]: st.metric(label="Affordability Improvement", value=f"{social_impact_d3:.1f}%", delta=f"{social_impact_d3 - 20:.1f}% vs Baseline")

    # --- Layout: Row 1 ---
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_sankey = go.Figure(data=[go.Sankey(
            arrangement='snap',
            node=dict(pad=15, thickness=20, line=dict(color="black", width=1.5), label=sankey_data_d3['node_labels'], color=sankey_data_d3['node_colors'], hoverlabel=dict(bgcolor="white", bordercolor="black", font=dict(size=14, family="Arial", color="black"))),
            link=dict(source=sankey_data_d3['link_sources'], target=sankey_data_d3['link_targets'], value=[incentive_budget, remaining_budget, *updated_remaining_values], color=sankey_data_d3['link_colors'], hovertemplate='%{value:.1f}% from %{source.label}<br>to %{target.label}<extra></extra>')
        )])
        fig_sankey.update_layout(
            title=dict(text='Housing Budget Flow Analysis (€100M Total)', x=0.5, font=dict(size=16), xanchor='center', yanchor='top'),
            font=dict(size=14), height=310, margin=dict(l=20, r=20, t=40, b=60), paper_bgcolor='white'
        )
        fig_sankey.add_annotation(
            x=0.5, y=-0.15, xref='paper', yref='paper', text=f'<b>{incentive_budget:.1f}%</b> of total budget allocated', showarrow=False, font=dict(size=14, color='black'), align='center', bgcolor='rgba(220, 239, 110, 0.8)', bordercolor='#3498db', borderwidth=1, borderpad=8, opacity=0.9
        )
        st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with row1_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_waterfall = go.Figure(go.Waterfall(
            name='Waterfall', orientation='v', measure=waterfall_data_d3['measures'], x=waterfall_data_d3['labels'],
            textposition='auto', text=[f'€{tax_savings:,.0f}', f'−€{abs(rent_reduction):,.0f}', f'€{tax_savings + rent_reduction:,.0f}'],
            y=[tax_savings, rent_reduction, None], connector={'line': {'color': 'grey'}},
            decreasing={'marker': {'color': '#d62728'}}, increasing={'marker': {'color': '#2ca02c'}}, totals={'marker': {'color': '#1f77b4'}}
        ))
        fig_waterfall.update_layout(
            title=dict(text='Landlord Financial Impact (Per Property)', x=0.5, font=dict(size=16), xanchor='center', yanchor='top'),
            xaxis_title='Financial Components', yaxis_title='Amount (€)', height=310, margin=dict(l=30, r=30, t=40, b=30),
            showlegend=False, plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='lightgrey')
        )
        fig_waterfall.add_annotation(x=0, y=tax_savings * 1.05, text='Tax incentive benefit', showarrow=False, font=dict(size=11), yshift=10)
        fig_waterfall.add_annotation(x=1, y=rent_reduction * 0.5, text='Controlled rent impact', showarrow=False, font=dict(size=11), yshift=-10)
        st.plotly_chart(fig_waterfall, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Layout: Row 2 ---
    row2_col1, row2_col2 = st.columns([0.7, 0.3])
    with row2_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        chart_type = st.selectbox("Select Chart", ["Long-term Projection", "Correlation Analysis", "District Analysis"], index=0, key="d3_chart_select")
        if chart_type == "Long-term Projection":
            fig_combined = make_subplots(specs=[[{"secondary_y": True}]])
            fig_combined.add_trace(go.Scatter(x=years_d3, y=updated_revenue_without, name='Without Program', line=dict(color='steelblue', width=3), hovertemplate='%{y:.1f}M €'), secondary_y=False)
            fig_combined.add_trace(go.Scatter(x=years_d3, y=updated_revenue_with, name='With Program', line=dict(color='green', width=3), fill='tonexty', fillcolor='rgba(0,128,0,0.1)', hovertemplate='%{y:.1f}M €'), secondary_y=False)
            fig_combined.add_trace(go.Bar(x=years_d3, y=updated_revenue_diff, name='Annual Gain', marker_color='orange', text=[f"€{val:.1f}M" for val in updated_revenue_diff], textposition='outside', textfont=dict(size=9), hovertemplate='+%{y:.1f}M €'), secondary_y=True)
            fig_combined.update_layout(
                title=dict(text='Long-term Property Tax Revenue (2025–2034)', x=0.5, y=0.98, font=dict(size=16), xanchor='center', yanchor='top'),
                xaxis_title='Year', height=310, margin=dict(l=40, r=40, t=60, b=40), plot_bgcolor='white',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(size=10), bgcolor='rgba(255,255,255,0.8)')
            )
            fig_combined.update_yaxes(title_text='Tax Revenue (M €)', secondary_y=False, showgrid=True, gridcolor='lightgray')
            fig_combined.update_yaxes(title_text='Extra Gain (M €)', secondary_y=True, range=[0, max(updated_revenue_diff or [0]) * 1.6])
            fig_combined.add_annotation(
                x=2030, y=max(updated_revenue_diff or [0]) * 1.3, text=f"<b>Cumulative 10Y Gain:</b><br>+€{updated_cumulative_diff:.1f}M", showarrow=False, font=dict(size=11, color='orange'), bgcolor='white', bordercolor='orange', borderwidth=1, borderpad=5
            )
        elif chart_type == "Correlation Analysis":
            fig_combined = go.Figure()
            fig_combined.add_trace(go.Scatter(x=incentive_amounts_d3, y=participation_rates_d3, mode='markers', name='Data Points', marker=dict(size=8, color='royalblue', line=dict(width=1, color='black'))))
            trendline = np.poly1d(np.polyfit(incentive_amounts_d3, participation_rates_d3, 1))
            fig_combined.add_trace(go.Scatter(x=incentive_amounts_d3, y=trendline(incentive_amounts_d3), mode='lines', name='Trendline', line=dict(color='red', width=2)))
            fig_combined.add_annotation(x=1000, y=90, text=f"<b>Correlation:</b> {correlation_d3:.2f}<br><b>R²:</b> {r_squared_d3:.2f}", showarrow=False, bgcolor='white', bordercolor='black', borderwidth=1, font=dict(size=11), align='left')
            annotations = {0: 'No Incentives', 3000: 'Partial Incentives', 7000: 'Full Incentives'}
            for x_val, label in annotations.items():
                idx = np.abs(incentive_amounts_d3 - x_val).argmin()
                y_val = participation_rates_d3[idx]
                fig_combined.add_annotation(x=x_val, y=y_val, text=label, showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor='gray', ax=-30, ay=-30, font=dict(size=10))
            fig_combined.update_layout(
                title=dict(text='Incentives vs. Landlord Participation', x=0.5, font=dict(size=16), xanchor='center', yanchor='top'),
                xaxis_title='Tax Incentive (€)', yaxis_title='Participation Rate (%)', height=310, margin=dict(l=40, r=20, t=40, b=40), plot_bgcolor='white',
                xaxis=dict(showgrid=True, gridcolor='lightgrey', tickformat=',.0f'), yaxis=dict(showgrid=True, gridcolor='lightgrey'),
                legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.6)', font=dict(size=10))
            )
        else:
            if analysis_view == "Quadrant Analysis":
                if not filtered_district_analysis.empty:
                    avg_cost = filtered_district_analysis['Incentive Cost (€/unit)'].mean()
                    avg_improvement = filtered_district_analysis['Affordability Improvement (%)'].mean()
                    x_max = filtered_district_analysis['Incentive Cost (€/unit)'].max() * 1.15
                    y_max = filtered_district_analysis['Affordability Improvement (%)'].max() * 1.15
                    sizeref = 2.*max(filtered_district_analysis['ROI Ratio'])/(30**2) if max(filtered_district_analysis['ROI Ratio']) > 0 else 1
                else:
                    avg_cost, avg_improvement, x_max, y_max, sizeref = 0, 0, 100, 30, 1

                fig_combined = px.scatter(
                    filtered_district_analysis, x='Incentive Cost (€/unit)', y='Affordability Improvement (%)', size='ROI Ratio', color='Implementation Complexity',
                    hover_name='District', text='District', color_continuous_scale='Viridis',
                    labels={'Incentive Cost (€/unit)': 'Cost (€/unit)', 'Affordability Improvement (%)': 'Affordability Improvement (%)', 'Implementation Complexity': 'Complexity'}
                ) if not filtered_district_analysis.empty else go.Figure()

                if not filtered_district_analysis.empty:
                    fig_combined.add_shape(type="line", x0=avg_cost, y0=0, x1=avg_cost, y1=y_max, line=dict(color="gray", width=1, dash="dash"))
                    fig_combined.add_shape(type="line", x0=0, y0=avg_improvement, x1=x_max, y1=avg_improvement, line=dict(color="gray", width=1, dash="dash"))
                    fig_combined.add_annotation(x=avg_cost / 2, y=avg_improvement * 1.1, text="<b>High Impact<br>Low Cost</b>", showarrow=False, font=dict(size=10, color="green"))
                    fig_combined.add_annotation(x=avg_cost * 1.25, y=avg_improvement * 1.1, text="<b>High Impact<br>High Cost</b>", showarrow=False, font=dict(size=10, color="blue"))
                    fig_combined.add_annotation(x=avg_cost / 2, y=avg_improvement * 0.4, text="<b>Low Impact<br>Low Cost</b>", showarrow=False, font=dict(size=10, color="orange"))
                    fig_combined.add_annotation(x=avg_cost * 1.25, y=avg_improvement * 0.4, text="<b>Low Impact<br>High Cost</b>", showarrow=False, font=dict(size=10, color="red"))
                    fig_combined.update_traces(
                        textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey'), sizemode='area', sizeref=sizeref, sizemin=5),
                        textfont=dict(size=9, color='black')
                    )

                fig_combined.update_layout(
                    title=dict(text='District Cost-Effectiveness Analysis', x=0.5, font=dict(size=16), xanchor='center', yanchor='top'),
                    height=310, margin=dict(l=40, r=20, t=40, b=40), plot_bgcolor='white',
                    xaxis=dict(title='Cost (€/unit)', gridcolor='lightgrey', zeroline=False, range=[0, x_max]),
                    yaxis=dict(title='Affordability Improvement (%)', gridcolor='lightgrey', zeroline=False, range=[0, y_max]),
                    coloraxis_colorbar=dict(title="Complexity", tickvals=[1, 2, 3, 4], ticktext=["Low", "Medium", "High", "Very High"], lenmode="fraction", len=0.75)
                )
            else:
                if not filtered_district_analysis.empty:
                    df_sorted = filtered_district_analysis.sort_values(by='ROI Ratio', ascending=False)
                    z_data = [df_sorted['ROI Ratio'].values, df_sorted['Incentive Cost (€/unit)'].values, df_sorted['Affordability Improvement (%)'].values]
                    y_labels = ['ROI Ratio', 'Cost (€)', 'Affordability (%)']
                    x_labels = df_sorted['District'].tolist()
                    text_data = [
                        [f"{val:.2f}" for val in df_sorted['ROI Ratio']], [f"€{val:.0f}" for val in df_sorted['Incentive Cost (€/unit)']],
                        [f"{val:.1f}%" for val in df_sorted['Affordability Improvement (%)']]
                    ]
                    fig_combined = go.Figure(data=go.Heatmap(
                        z=z_data, x=x_labels, y=y_labels, text=text_data, texttemplate="%{text}",
                        textfont=dict(size=10), colorscale='RdBu_r', reversescale=False, colorbar=dict(title='Value', thickness=15, len=0.7)
                    ))
                else:
                    fig_combined = go.Figure()

                fig_combined.update_layout(
                    title=dict(text='District Affordability vs. Costs Heatmap', x=0.5, font=dict(size=16), xanchor='center', yanchor='top'),
                    xaxis=dict(title='District', tickangle=-30), yaxis=dict(title='Metric', autorange='reversed'),
                    height=310, margin=dict(l=40, r=20, t=40, b=50)
                )

        st.plotly_chart(fig_combined, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with row2_col2:
        st.markdown(f"""
        <div style="background-color:#f8f9fa; padding:15px; border-radius:8px; font-size:0.95em; height: 100%; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #eee;">
        <h3 style="text-align: center; color:#333; margin-bottom:15px; border-bottom: 2px solid #dcef6e; padding-bottom:8px; margin-top:0;">Analysis Insights</h3>
        <div style="display: flex; flex-direction: column; justify-content: space-around; flex-grow: 1;">
            <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;"><span style="font-weight: bold; color:#2c3e50;">Program Payback:</span><br><span style="font-size: 1.1em; color:#333;">Pays for itself in <b>{updated_payback_period:.1f} years</b></span></div>
            <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;"><span style="font-weight: bold; color:#2c3e50;">Revenue Impact:</span><br><span style="font-size: 1.1em; color:#333;">Generates <b>€{updated_cumulative_diff:.1f}M</b> over 10 years</span></div>
            <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;"><span style="font-weight: bold; color:#2c3e50;">Budget Allocation:</span><br><span style="font-size: 1.1em; color:#333;">Tax incentives are <b>{incentive_budget:.1f}%</b> of budget</span></div>
            <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;"><span style="font-weight: bold; color:#2c3e50;">Landlord Benefit:</span><br><span style="font-size: 1.1em; color:#333;">Average gain of <b>€{updated_net_gain:,.0f}</b> annually</span></div>
        </div></div>
        """.format(
            updated_payback_period=updated_payback_period if updated_payback_period != float('inf') else '>50',
            updated_cumulative_diff=updated_cumulative_diff,
            incentive_budget=incentive_budget,
            updated_net_gain=updated_net_gain
        ), unsafe_allow_html=True)

    # Footer for Dashboard 3
    st.markdown(f"""
    <div style="background-color:#f0f0f0; padding:5px; border-radius:3px; margin-top:15px; font-size:0.6em; text-align:center;">
    Sources: Madrid Tax Revenue Reports, Landlord Survey 2023 | Budget: {incentive_budget:.1f}% | Growth: {growth_rate_with*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

# --- Main App Logic ---

# Apply CSS, Title, Sidebar and Content based on the current page
if st.session_state.page == 'dashboard1':
    st.markdown(css_dashboard1, unsafe_allow_html=True)
    st.markdown('<div class="title-bar"><b>Strategic Overview:</b> Madrid Rent Price Analysis</div>', unsafe_allow_html=True)
    kpi_district_d1 = display_dashboard1_sidebar()
    display_dashboard1_content(kpi_district_d1)

elif st.session_state.page == 'dashboard2':
    st.markdown(css_dashboard2, unsafe_allow_html=True)
    # Ensure space after colon in the title string
    st.markdown('<div class="title-bar"><b>Tactical Decisions: </b> Smart Rent Control Implementation</div>', unsafe_allow_html=True)
    selected_districts_d2, incentive_level_d2, implementation_timeline_d2, tenant_category_d2 = display_dashboard2_sidebar()
    display_dashboard2_content(selected_districts_d2, incentive_level_d2, implementation_timeline_d2, tenant_category_d2)

elif st.session_state.page == 'dashboard3':
    st.markdown(css_dashboard3, unsafe_allow_html=True)
    st.markdown('<div class="title-bar"><b>Analytical Insights:</b> Deep-Dive Financial Analysis</div>', unsafe_allow_html=True)
    incentive_budget_d3, tax_savings_d3, growth_rate_without_d3, growth_rate_with_d3, selected_districts_d3, analysis_view_d3 = display_dashboard3_sidebar()
    display_dashboard3_content(incentive_budget_d3, tax_savings_d3, growth_rate_without_d3, growth_rate_with_d3, selected_districts_d3, analysis_view_d3)

# --- Navigation Buttons ---
st.divider()
nav_cols = st.columns([1, 1, 5, 1, 1])

with nav_cols[1]: # Previous Button
    is_first_page = (st.session_state.page == 'dashboard1')
    if not is_first_page:
        if st.button("⬅️", key='prev_button'):
            if st.session_state.page == 'dashboard3': st.session_state.page = 'dashboard2'
            elif st.session_state.page == 'dashboard2': st.session_state.page = 'dashboard1'
            st.rerun()
    else:
        st.button("⬅️", key='prev_button_disabled', disabled=True)

with nav_cols[3]: # Next Button
    is_last_page = (st.session_state.page == 'dashboard3')
    if not is_last_page:
        if st.button("➡️", key='next_button'):
            if st.session_state.page == 'dashboard1': st.session_state.page = 'dashboard2'
            elif st.session_state.page == 'dashboard2': st.session_state.page = 'dashboard3'
            st.rerun()
    else:
        st.button("➡️", key='next_button_disabled', disabled=True)

# Add some space at the very bottom
st.markdown("<br>", unsafe_allow_html=True) 