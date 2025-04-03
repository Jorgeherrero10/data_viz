import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- Page Configuration -----------------
st.set_page_config(
    page_title="Strategic? Xx - Housing Dashboard",
    layout="wide"
)

# ----------------- Sidebar Filters -----------------
st.sidebar.header("Filters to adjust graphs")

# 1) District Filter
district_list = ["Arganzuela", "Barajas", "Carabanchel", "Centro", "Chamartin"]
selected_districts = st.sidebar.multiselect(
    "List of Districts (Drop down menu)",
    options=district_list,
    default=["Centro"]
)

# 2) Slider for "Impact of SRC" from 2015 to 2030
impact_year = st.sidebar.slider(
    "Impact of SRC (select a year)",
    min_value=2015,
    max_value=2030,
    value=2020
)

# 3) Any additional filters you need (e.g., date range, etc.)
# For example, a year dropdown for "Historical KPIs"
# selected_year = st.sidebar.selectbox("Select a Year", [2019, 2020, 2021, 2022, 2023])

# -------------- Top Header (Title Bar) --------------
# You can replace the text below as needed
st.markdown("""
<div style="background-color: #dcef6e; padding: 20px; border-bottom: 2px solid #ccc;">
    <h1 style="font-family: Arial; font-weight: bold; font-size: 32px; color: #484848; margin: 0;">
        Strategic? Xx
    </h1>
    <h2 style="font-family: Arial; font-size: 20px; font-weight: normal; color: #484848; margin: 0;">
        Xx
    </h2>
</div>
""", unsafe_allow_html=True)

# (Optional) Toggle button to switch between different dashboards
toggle_dashboard = st.button("Toggle between dashboard")

# -------------- KPI Row --------------
# Example placeholders for your KPIs
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric(label="Average Supply Value", value="1.048 €")
with col_kpi2:
    st.metric(label="Average Monthly Rent", value="1.072 €")
with col_kpi3:
    st.metric(label="Affordability Ratio", value="35%")

# -------------- Main Charts --------------
# We’ll create two columns: left for the main line chart, right for the bar chart
col_left, col_right = st.columns([1, 1])

# --- Left Column: Historical Rental Prices by District ---
with col_left:
    st.subheader("Historical Rental Prices by District")
    
    # Placeholder data
    df_line = pd.DataFrame({
        "Date": pd.date_range("2018-01-01", periods=24, freq="M"),
        "Rent_Price": [x*0.5 + 10 for x in range(24)],
        "District": ["Centro"]*24
    })
    
    # If multiple districts are selected, we might have more rows
    # For demonstration, let's just duplicate the data
    dfs = []
    for dist in selected_districts:
        temp = df_line.copy()
        temp["District"] = dist
        # add some variation per district
        temp["Rent_Price"] += (hash(dist) % 5)  
        dfs.append(temp)
    df_line_all = pd.concat(dfs, ignore_index=True)
    
    fig_line = px.line(
        df_line_all,
        x="Date",
        y="Rent_Price",
        color="District",
        title="Historical Rental Prices by District"
    )
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

# --- Right Column: Affordability Trends (Bar Chart) ---
with col_right:
    st.subheader("Affordability Trends")
    
    # Placeholder data for a bar chart
    df_bar = pd.DataFrame({
        "Category": ["2019", "2020", "2021", "2022", "2023"],
        "Value": [0.8, 0.9, 1.0, 1.05, 1.07]
    })
    
    fig_bar = px.bar(
        df_bar,
        x="Category",
        y="Value",
        title="Average Rent Growth"
    )
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------- Additional Chart: Impact of Smart Rent Control --------------
st.subheader("Impact of Smart Rent Control on Rental Price Trends")

# Placeholder data for line chart comparing uncontrolled vs controlled rent
df_smart_control = pd.DataFrame({
    "Year": range(2015, 2031),
    "Uncontrolled_Rent": [x*0.05 + 1 for x in range(16)],  # simplistic linear growth
    "Controlled_Rent": [x*0.03 + 1 for x in range(16)]     # slightly slower growth
})

fig_smart = px.line(
    df_smart_control,
    x="Year",
    y=["Uncontrolled_Rent", "Controlled_Rent"],
    labels={"value": "Rent (€/m²)", "Year": "Year", "variable": "Rent Scenario"},
    title="Impact of SRC on Rental Price Trends"
)
fig_smart.update_layout(height=400)
st.plotly_chart(fig_smart, use_container_width=True)

# -------------- Historical KPIs by District (Table or Grid) --------------
st.subheader("Historical KPIs by District")

# Placeholder table for CAGR, price variation, etc.
data_kpis = {
    "District": ["Centro", "Arganzuela", "Barajas", "Carabanchel", "Chamartin"],
    "CAGR (from 2015)": ["3.2%", "2.8%", "2.5%", "3.0%", "3.3%"],
    "Price Variation (yoy)": ["+5%", "+4%", "+3%", "+4%", "+5%"],
    "Avg Rent (€/m²)": [12.5, 11.8, 10.5, 11.2, 13.0],
}
df_kpis = pd.DataFrame(data_kpis)

# If you have a year filter in the sidebar, you can filter df_kpis based on it
# e.g., df_kpis_filtered = df_kpis[df_kpis["Year"] == selected_year]

st.dataframe(df_kpis)

# -------------- Footer / Sources --------------
st.markdown("""
<hr>
<div style="text-align: center; font-size: 12px;">
    <p>Source for map or data: <a href="#" target="_blank">[Your Data Source Link]</a></p>
    <p>Additional references or disclaimers go here.</p>
</div>
""", unsafe_allow_html=True)
