import streamlit as st
import json
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from utils import bucket_1, bucket_2, bucket_3, bucket_4, bucket_5  # Assuming these have been updated as above

# ------------------ Data Loading & Preparation ------------------
# Load GeoJSON for Madrid districts
try:
    with open('../data/DistritosMadrid.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
except FileNotFoundError:
    st.error("GeoJSON file not found. Please check the file path.")
    st.stop()

# Load rental prices data
df_prices = pd.read_csv('../data/prices.csv')
df_prices['Date'] = pd.to_datetime(df_prices['Date'])

# Calculate average rent per district over time for the line chart
df_avg = df_prices.groupby(['Date', 'District'])['Rent_Price'].mean().reset_index()

# Compute overall average rent (used to add an overall mean line)
overall_df = df_prices.groupby('Date')['Rent_Price'].mean().reset_index()

# Calculate average rent per district for the map
district_avgs = df_prices.groupby('District')['Rent_Price'].mean().to_dict()
min_rent = min(district_avgs.values())
max_rent = max(district_avgs.values())

def get_color(val, min_val, max_val):
    """Compute a hex color (red scale) based on the normalized value."""
    norm = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
    red_level = int(norm * 255)
    return f"#{red_level:02x}0000"

# ------------------ Session State for Filters ------------------
if 'selected_districts' not in st.session_state:
    st.session_state.selected_districts = []

def toggle_district(district):
    """Toggle a district in the session state."""
    if district in st.session_state.selected_districts:
        st.session_state.selected_districts.remove(district)
    else:
        st.session_state.selected_districts.append(district)

# ------------------ Page Configuration & Custom CSS ------------------
st.set_page_config(page_title="Dashboard 1", layout="wide")

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

custom_css = """
    <style>
        /* Fixed top bar styling */
        .fixed-top-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            padding: 70px 0 10px 250px;
            background-color: #dcef6e;
            text-align: left;
            z-index: 1100;
            border-bottom: 2px solid #ccc;
        }
        /* Offset body so content doesn't hide behind the fixed bar */
        body {
            margin-top: 100px;
        }
        /* Override the default padding and margins for block containers */
        div.block-container {
            padding: 0rem !important;
            margin: 0 !important;
        }
        /* Optionally, target Streamlit’s column wrapper for further reduction */
        .css-1lcbmhc {
            padding: 0 !important;
            margin: 0 !important;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

font_size = "28px"
st.markdown(f"""
    <div class="fixed-top-bar" style="font-size: {font_size};">
        <b>Strategic Overview:</b> Rent Prices in Madrid represent a serious problem for the youth population.
    </div>
    """, unsafe_allow_html=True)

# ------------------ Sidebar with Filters ------------------
with st.sidebar:
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.header("Filters", anchor="filters")
    district_list = sorted(df_prices['District'].unique())
    selected_districts = st.multiselect(
        "Select Districts",
        options=district_list,
        default=st.session_state.selected_districts,
        help="Select districts to filter the data."
    )
    st.session_state.selected_districts = selected_districts

    # --- New KPI Filter ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("KPI Filter")
    kpi_district = st.selectbox(
        "Select District for KPIs",
        options=["All"] + district_list,
        index=0
    )


# ------------------ Main Dashboard Content ------------------
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    # --- Container 1: Line Chart ---
    with st.container():
        if st.session_state.get("selected_districts"):
            df_line = df_avg[df_avg['District'].isin(st.session_state.selected_districts)]
            line_title = "Average Rent Price by Date - " + ", ".join(st.session_state.selected_districts)
            default_opacity = 1
            overall_opacity = 0.2
        else:
            df_line = df_avg.copy()
            line_title = "Average Rent Price by Date (All Districts)"
            default_opacity = 0.5
            overall_opacity = 1

        fig_line = px.line(df_line, x="Date", y="Rent_Price", color="District", title=line_title)
        fig_line.add_trace(
            go.Scatter(
                x=overall_df['Date'],
                y=overall_df['Rent_Price'],
                mode='lines',
                name='Overall Mean',
                line=dict(dash='dash', color='black'),
                opacity=overall_opacity
            )
        )
        fig_line.update_layout(
            yaxis_title="Rent Price (€ per M²)",
            yaxis_range=[7, 26],
            xaxis_range=[pd.to_datetime('2008-08-01'), df_prices['Date'].max()],
            margin=dict(l=40, r=20, t=50, b=40),
            height=250,
            legend=dict(
                font=dict(size=10)
            )
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
    # --- Container 2: Map ---
    with st.container():
        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)
        m = folium.Map(location=[40.417101, -3.695899], zoom_start=12, tiles="cartodbpositron")
        for feature in geojson_data['features']:
            district_name = feature['properties'].get('NOMBRE', 'Unknown')
            avg_rent = district_avgs.get(district_name, min_rent)
            fill_color = get_color(avg_rent, min_rent, max_rent)
            folium.GeoJson(
                feature,
                style_function=lambda x, fill_color=fill_color: {
                    'fillColor': fill_color,
                    'color': 'gray',
                    'weight': 1,
                    'fillOpacity': 0.6,
                },
                popup=district_name,
                tooltip=folium.GeoJsonTooltip(
                    fields=["NOMBRE"],
                    aliases=["District:"],
                    sticky=False
                ),
                highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.9},
            ).add_to(m)
        legend_html = """
            <div style="position: absolute;
            bottom: 0px; left: 20px; width: 150px; height: 70px; 
            z-index:9999; font-size:12px;
            background-color:white;
            border:1px solid grey;
            padding:0px;">
            <div style="text-align:center"><b>Rent Range</b></div>
            <div style="font-size:12px;">Low &nbsp;&nbsp;<span style="float:right;">High</span></div>
            <div style="width:100%; height:10px; background: linear-gradient(to right, #000000, #ff0000);"></div>
            </div>
            """
        m.get_root().html.add_child(folium.Element(legend_html))
        map_result = st_folium(m, width=700, height=250)
        if map_result and map_result.get("last_object_clicked") is not None:
            clicked = map_result["last_object_clicked"]
            district_clicked = clicked.get("popup")
            if district_clicked:
                toggle_district(district_clicked)
                st.experimental_rerun()
                
    # --- Container 3: Buckets (4 Metrics) ---
    with st.container():
        # A slight negative margin to reduce the gap between the map and the KPIs
        st.markdown("<div style='margin-top: -20px;'></div>", unsafe_allow_html=True)
        
        # Create four equal columns for the KPIs
        bucket1_col, bucket2_col, bucket3_col, bucket4_col = st.columns(4)
        
        with bucket1_col:
            value1 = bucket_1(df_prices, kpi_district)
            st.metric(label="CAGR", value=value1)
            st.caption("Annual growth rate of Rent Price (%)")
            
        with bucket2_col:
            value2 = bucket_2(df_prices, kpi_district)
            st.metric(label="Max Rental", value=value2)
            st.caption("Maximum Rent Price recorded")
            
        with bucket3_col:
            value3 = bucket_3(df_prices, kpi_district)
            st.metric(label="Ranking", value=value3)
            st.caption("Ranking position by Rent Price")
            
        with bucket4_col:
            value4 = bucket_4(df_prices, kpi_district)
            st.metric(label="Average Rent Price", value=value4)
            st.caption("Average Rent Price")

with col2:
    # --- Graph 1: Youth Salary vs Rent Prices ---
    st.markdown("<h3 style='text-align: center;'>Youth Salary vs Rent Prices</h3>", unsafe_allow_html=True)
    
    # Load CSV data for the first graph
    df_youth = pd.read_csv(r"..\data\Youth_Salary_vs_Rent_Prices.csv")
    # Ensure your columns are named appropriately; for example:
    # df_youth.columns = ["Year", "Average_Youth_Salary", "Average_Monthly_Rent"]
    
    import plotly.graph_objects as go
    # Create a figure for the first graph
    fig1 = go.Figure()
    # Add bar traces for each series
    fig1.add_trace(go.Bar(
        x=df_youth["Year"],
        y=df_youth["Average_Youth_Salary"],
        name="Average Youth Salary",
        marker_color="lightgray"
    ))
    fig1.add_trace(go.Bar(
        x=df_youth["Year"],
        y=df_youth["Average_Monthly_Rent"],
        name="Average Monthly Rent",
        marker_color="#dcef6e"
    ))
    # Overlay line traces
    fig1.add_trace(go.Scatter(
        x=df_youth["Year"],
        y=df_youth["Average_Youth_Salary"],
        mode="lines+markers",
        name="Salary Trend",
        line=dict(color="lightgray")
    ))
    fig1.add_trace(go.Scatter(
        x=df_youth["Year"],
        y=df_youth["Average_Monthly_Rent"],
        mode="lines+markers",
        name="Rent Trend",
        line=dict(color="#dcef6e")
    ))
    fig1.update_layout(
        barmode="group",
        xaxis_title="Year",
        yaxis_title="Amount in $",
        title="Average Youth Salary vs Average Monthly Rent Prices",
        xaxis_tickangle=-45,
        yaxis_range=[600, 1200],
        margin=dict(l=40, r=20, t=50, b=40)
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # --- Graph 2: Comparison: Madrid vs Europe (Horizontal Bar Chart) ---
    st.markdown("<h3 style='text-align: center;'>Comparison: Madrid vs Europe</h3>", unsafe_allow_html=True)
    
    import plotly.express as px
    # Create a DataFrame for the horizontal bar chart
    df_bar = pd.DataFrame({
        "Region": ["Madrid", "Europe"],
        "Percentage": [60, 40]
    })
    # Create the horizontal bar chart
    fig2 = px.bar(df_bar, 
                  x="Percentage", 
                  y="Region", 
                  orientation="h", 
                  text="Percentage",
                  labels={"Percentage": "Percentage", "Region": "Region"},
                  title="Comparison: Madrid vs Europe")
    fig2.update_traces(texttemplate='%{text}%', textposition='outside')
    fig2.update_layout(
        xaxis_range=[0, 100],
        yaxis={'categoryorder':'total ascending'},
        margin=dict(l=40, r=20, t=50, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # --- Graph 3: Concerns Comparison Radar Chart ---
    st.markdown("<h3 style='text-align: center;'>Concerns Comparison Between 2014 and 2024</h3>", unsafe_allow_html=True)
    
    # Define the data using a multi-line string and read it into a DataFrame
    from io import StringIO
    data = """Year;Access to Housing;Unemployment;Political Issues;Job Quality;Immigration;Economic Crisis
2014;5;8;6;7;4;7
2024;9;7;6;7;5;6"""
    df_radar = pd.read_csv(StringIO(data), delimiter=';')
    
    # Define the categories for the radar chart (all columns except 'Year')
    categories = list(df_radar.columns[1:])
    
    # Create the radar chart
    fig3 = go.Figure()
    for index, row in df_radar.iterrows():
        # Close the loop by repeating the first value
        values = row[categories].tolist()
        values += values[:1]
        cats = categories + [categories[0]]
        fig3.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill='toself',
            name=str(row['Year'])
        ))
    fig3.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=True,
        margin=dict(l=40, r=20, t=50, b=40)
    )
    st.plotly_chart(fig3, use_container_width=True)



