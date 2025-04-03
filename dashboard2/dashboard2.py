import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config for wide layout
st.set_page_config(layout="wide", page_title="Madrid Housing Dashboard")

# Add custom CSS for the slide-like appearance with improved padding
st.markdown("""
<style>
/* Add padding to the top of the page */
.main {
    padding-top: 50px !important;
}

/* Title bar styling */
.title-bar {
    background-color: #dcef6e;
    padding: 10px 15px;
    border-radius: 5px;
    margin-bottom: 15px;
    margin-top: 20px;
    color: #333;
    font-size: 22px;
    font-weight: bold;
    display: flex;
    align-items: center;
    height: 45px;
}

/* Remove extra padding and margin to maximize space */
.block-container {
    padding-top: 30px !important;
    padding-bottom: 0 !important;
    margin-top: 10px !important;
    margin-bottom: 0 !important;
}
.element-container {margin-bottom: 5px !important;}
[data-testid="stVerticalBlock"] {gap: 0px !important;}

/* Chart containers */
.chart-container {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
    height: calc(100% - 10px);
    margin-bottom: 10px;
}

/* Hide default streamlit footer */
footer {display: none !important;}
.stApp {height: 100vh !important;}

/* Adjust header margins */
h3 {
    margin-top: 0 !important;
    margin-bottom: 5px !important;
    font-size: 18px !important;
}

/* Adjust metrics to be more compact */
[data-testid="stMetric"] {
    padding: 5px !important;
}
[data-testid="stMetricLabel"] {
    margin-bottom: 0 !important;
}
[data-testid="stMetricValue"] {
    margin-bottom: 0 !important;
}
[data-testid="stMetricDelta"] {
    margin-top: 0 !important;
}

/* Force content to fit in a single slide */
.main .block-container {
    max-height: calc(100vh - 20px) !important;
    overflow: hidden !important;
}

/* Adjust plotly charts to be more compact */
.js-plotly-plot {
    margin-bottom: 0 !important;
}

/* Remove extra padding from markdown */
.stMarkdown p {
    margin-bottom: 0 !important;
}

/* KPI grid */
.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 5px;
}
.kpi-item {
    padding: 5px;
}

/* Radio buttons more compact */
.st-cc {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Tab control more compact */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 3px !important;
}
</style>
""", unsafe_allow_html=True)

# Display the title bar
st.markdown('<div class="title-bar">Tactical Decisions: Smart Rent Control Implementation</div>', unsafe_allow_html=True)

# Data preparation
# -------------------------------------------------------------------------
# Districts data with rent prices
districts = [
    "Salamanca", "Centro", "Chamberí", "Chamartín", "Arganzuela",
    "Tetuán", "Retiro", "Moncloa-Aravaca", "Fuencarral-El Pardo", "Usera"
]
before_control = np.array([25, 24, 23, 22, 20, 18, 21, 19, 17, 16])
after_control = np.array([21, 20, 20, 19, 18, 16, 18, 17, 15, 14])
reduction_percent = ((before_control - after_control) / before_control) * 100

# Create DataFrame
scenario_data = pd.DataFrame({
    "District": districts,
    "Before Control (€/m²)": before_control,
    "After Control (€/m²)": after_control,
    "Reduction (%)": reduction_percent
})

# Landlord participation data
incentive_levels = ['No Incentives', 'Partial Incentives', 'Full Incentives']
participation_rates = [10, 40, 70]
rent_increase = [5.0, 3.0, 1.5]
net_benefit = [0, 3000, 5873]

# Affordability data
tenant_categories = ["Low-Income Renters", "Middle-Income Renters", "Young Professionals"]
before_burden = [51.7, 35.4, 41.2]  # % of income spent on rent
after_burden = [39.4, 25.9, 30.9]   # % of income spent on rent
improvement = [(b-a)/b*100 for b, a in zip(before_burden, after_burden)]

# Operational data
operational_data = {
    "District": districts,
    "Current Rent (€/m²)": before_control,
    "Priority Score": [9, 8, 8, 7, 6, 5, 7, 6, 5, 4],
    "Implementation Timeline (months)": [1, 1, 1.5, 2, 3, 3, 2.5, 2, 4, 4],
    "Incentive Level": ["High", "High", "High", "Medium", "Medium", "Low", "Medium", "Medium", "Low", "Low"]
}
ops_df = pd.DataFrame(operational_data)

# District affordability impact
districts_subset = ["Salamanca", "Centro", "Chamberí", "Retiro", "Arganzuela"]
youth_before = [42.5, 39.3, 39.9, 44.4, 41.2]  # % of income for young professionals 
youth_after = [29.7, 29.0, 30.3, 31.6, 30.0]
low_income_before = [54.9, 52.8, 54.6, 52.0, 46.0]
low_income_after = [44.9, 41.4, 41.8, 40.2, 33.6]

# Sidebar controls
with st.sidebar:
    st.header("Implementation Controls")
    
    selected_districts = st.multiselect(
        "Select districts to analyze:",
        districts,
        default=[]
    )
    
    incentive_level = st.select_slider(
        "Incentive level for landlords:",
        options=incentive_levels,
        value="Full Incentives"
    )
    
    implementation_timeline = st.slider(
        "Timeline (months):",
        min_value=1, max_value=12, value=4, step=1
    )
    
    st.subheader("Additional Filters")
    tenant_category = st.multiselect(
        "Tenant categories to analyze:",
        tenant_categories,
        default=["Low-Income Renters", "Young Professionals"]
    )
    
    st.button("Reset All Filters", on_click=st.rerun)

# Update data based on selections
incentive_index = incentive_levels.index(incentive_level)
selected_participation = participation_rates[incentive_index]
selected_rent_increase = rent_increase[incentive_index]
selected_benefit = net_benefit[incentive_index]

if selected_districts:
    scenario_data_filtered = scenario_data[scenario_data['District'].isin(selected_districts)]
    ops_df_filtered = ops_df[ops_df['District'].isin(selected_districts)]
else:
    scenario_data_filtered = scenario_data
    ops_df_filtered = ops_df

# Filter to only include selected districts that are also in the subset for district-specific impact
available_districts = [d for d in selected_districts if d in districts_subset]
if not available_districts:
    available_districts = districts_subset  # Default to all

# Create filtered data for just the selected districts
district_indices = [districts_subset.index(d) for d in available_districts if d in districts_subset]
district_impact = pd.DataFrame({
    "District": [districts_subset[i] for i in district_indices],
    "Youth Before": [youth_before[i] for i in district_indices],
    "Youth After": [youth_after[i] for i in district_indices],
    "Low-Income Before": [low_income_before[i] for i in district_indices],
    "Low-Income After": [low_income_after[i] for i in district_indices]
})

# Main dashboard layout - Create a clear 2x2 grid
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# Top left: KPIs
with row1_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # KPIs without nesting columns - using HTML grid instead
    avg_before = np.mean(before_control)
    avg_after = np.mean(after_control)
    avg_burden_before = np.mean(before_burden)
    avg_burden_after = np.mean(after_burden)
    priority_districts = len([d for d in ops_df_filtered['Priority Score'] if d >= 8])
    
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
    
    # Incentive details
    st.markdown(f"""
    <div style="background-color:#f8f9fa; padding:5px; border-radius:4px; margin-top:5px; font-size:0.8em;">
    <b>Selected: {incentive_level}</b> | Participation: {selected_participation}% | Rent Increase: {selected_rent_increase}% | Benefit: €{selected_benefit:,}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Top right: Rent Price Impact Chart
with row1_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Rent Price Comparison Chart
    fig_comparison = go.Figure()
    
    fig_comparison.add_trace(go.Bar(
        x=scenario_data_filtered["District"],
        y=scenario_data_filtered["Before Control (€/m²)"],
        name="Before Control",
        marker_color='#ff7f0e'
    ))
    
    fig_comparison.add_trace(go.Bar(
        x=scenario_data_filtered["District"],
        y=scenario_data_filtered["After Control (€/m²)"],
        name="After Control",
        marker_color='#2ca02c'
    ))
    
    fig_comparison.add_trace(go.Scatter(
        x=scenario_data_filtered["District"],
        y=scenario_data_filtered["Reduction (%)"],
        mode='lines+markers',
        name='Reduction (%)',
        yaxis='y2',
        line=dict(color='red', width=2),
        marker=dict(size=6)
    ))
    
    fig_comparison.update_layout(
        title=dict(
            text="Rent Price Impact by District",
            y=1,
            x=0.5,
            xanchor='center',
            yanchor='top',
            pad=dict(t=15, b=10)
        ),
        xaxis_title=None,
        yaxis_title="Rent Price (€/m²)",
        yaxis2=dict(
            title="Reduction (%)",
            overlaying="y",
            side="right",
            range=[0, max(reduction_percent) * 1.2]
        ),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=250,
        margin=dict(l=30, r=30, t=60, b=40),
        font=dict(size=10)
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Left: Landlord Incentives Chart
with row2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Landlord Participation & Incentives
    fig_incentives = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_incentives.add_trace(
        go.Bar(
            x=incentive_levels,
            y=participation_rates,
            name="Landlord Participation",
            marker_color='#1f77b4',
            text=[f"{rate}%" for rate in participation_rates],
            textposition='auto',
            textfont=dict(size=9)
        ),
        secondary_y=False
    )
    
    fig_incentives.add_trace(
        go.Scatter(
            x=incentive_levels,
            y=rent_increase,
            name="Rent Increase",
            mode='lines+markers',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    # Highlight selected incentive
    fig_incentives.add_shape(
        type="rect",
        x0=incentive_levels.index(incentive_level) - 0.4,
        x1=incentive_levels.index(incentive_level) + 0.4,
        y0=0,
        y1=participation_rates[incentive_levels.index(incentive_level)] + 5,
        line=dict(color="blue", width=2),
        fillcolor="rgba(0, 123, 255, 0.3)"
    )
    
    for i, level in enumerate(incentive_levels):
        if net_benefit[i] > 0:
            font_size = 12 if level == incentive_level else 10
            font_color = "black" if level == incentive_level else "white"
            bg_color = "rgba(255, 255, 0, 0.7)" if level == incentive_level else None
            
            fig_incentives.add_annotation(
                x=level,
                y=participation_rates[i]/2,
                text=f"€{net_benefit[i]:,}",
                showarrow=False,
                font=dict(size=font_size, color=font_color, family="Arial"),
                bgcolor=bg_color,
                borderpad=2 if level == incentive_level else 0
            )
    
    fig_incentives.update_layout(
        title=dict(
            text="Landlord Participation & Incentives",
            y=1,
            x=0.5,
            xanchor='center',
            yanchor='top',
            pad=dict(t=15, b=10)
        ),
        xaxis_title=None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        ),
        height=250,
        margin=dict(l=30, r=30, t=60, b=30),
        font=dict(size=10)
    )
    
    fig_incentives.update_yaxes(
        title_text="Participation Rate (%)",
        secondary_y=False
    )
    fig_incentives.update_yaxes(
        title_text="Rent Increase (%)",
        secondary_y=True,
        range=[0, 6]
    )
    
    st.plotly_chart(fig_incentives, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Right: Implementation Strategy / Affordability Impact
with row2_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    selected_tab = st.radio("Select View:", ["Implementation Strategy", "General Affordability", "District Affordability"], horizontal=True)
    
    if selected_tab == "Implementation Strategy":
        # Operational Strategy Chart
        fig_ops = px.scatter(
            ops_df_filtered,
            x="Implementation Timeline (months)",
            y="Priority Score",
            size="Current Rent (€/m²)",
            color="Incentive Level",
            hover_name="District",
            text="District",
            size_max=30,
            color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"}
        )
        
        fig_ops.add_shape(
            type="line",
            x0=implementation_timeline,
            y0=0,
            x1=implementation_timeline,
            y1=10,
            line=dict(color="blue", width=2, dash="dot")
        )
        
        fig_ops.add_annotation(
            x=implementation_timeline,
            y=9.5,
            text=f"Target: {implementation_timeline} mo",
            showarrow=True,
            arrowhead=1,
            ax=20,
            ay=-20,
            font=dict(size=10)
        )
        
        fig_ops.update_layout(
            title="Implementation Strategy by District",
            xaxis_title=None,
            yaxis_title="Priority Score",
            legend_title="Incentive Level",
            height=250,
            margin=dict(l=30, r=30, t=40, b=30),
            font=dict(size=10),
            legend=dict(font=dict(size=9))
        )
        
        fig_ops.update_traces(
            textposition='top center',
            marker=dict(opacity=0.8, line=dict(width=1, color='black')),
            textfont=dict(size=8)
        )
        
        st.plotly_chart(fig_ops, use_container_width=True, config={'displayModeBar': False})
    
    elif selected_tab == "General Affordability":
        # Housing Affordability Impact
        affordability_data = pd.DataFrame({
            "Tenant Category": tenant_categories,
            "Before Control (%)": before_burden,
            "After Control (%)": after_burden,
            "Improvement (%)": improvement
        })
        
        affordability_data_filtered = affordability_data[affordability_data["Tenant Category"].isin(tenant_category)] if tenant_category else affordability_data
        
        fig_afford = go.Figure()
        
        fig_afford.add_trace(go.Bar(
            x=affordability_data_filtered["Tenant Category"],
            y=affordability_data_filtered["Before Control (%)"],
            name="Before",
            marker_color="#d62728",
            text=affordability_data_filtered["Before Control (%)"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
            textfont=dict(size=9)
        ))
        
        fig_afford.add_trace(go.Bar(
            x=affordability_data_filtered["Tenant Category"],
            y=affordability_data_filtered["After Control (%)"],
            name="After",
            marker_color="#2ca02c",
            text=affordability_data_filtered["After Control (%)"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
            textfont=dict(size=9)
        ))
        
        for i, cat in enumerate(affordability_data_filtered["Tenant Category"]):
            idx = affordability_data[affordability_data["Tenant Category"] == cat].index[0]
            fig_afford.add_annotation(
                x=cat,
                y=after_burden[idx] - 3,
                text=f"↓{improvement[idx]:.1f}%",
                showarrow=False,
                font=dict(size=9, color="black")
            )
        
        fig_afford.update_layout(
            title="Impact on Housing Affordability",
            xaxis_title=None,
            yaxis_title="% Income on Rent",
            barmode="group",
            yaxis=dict(range=[0, max(before_burden) * 1.1]),
            height=250,
            margin=dict(l=30, r=30, t=40, b=30),
            font=dict(size=10),
            legend=dict(orientation="h", y=1.02, x=1, font=dict(size=9))
        )
        
        st.plotly_chart(fig_afford, use_container_width=True, config={'displayModeBar': False})
    
    else:  # District Affordability tab
        # Filter by tenant categories for district-specific impact
        categories_to_show = []
        if "Young Professionals" in tenant_category:
            categories_to_show.extend([("Youth Before", "#ff9999"), ("Youth After", "#99ff99")])
        if "Low-Income Renters" in tenant_category:
            categories_to_show.extend([("Low-Income Before", "#ffcc99"), ("Low-Income After", "#99ccff")])
        
        if not categories_to_show:
            categories_to_show = [("Youth Before", "#ff9999"), ("Youth After", "#99ff99")]
        
        fig_district = go.Figure()
        
        # Add trace for each category
        for cat, color in categories_to_show:
            if len(district_impact) > 0:  # Make sure we have data
                fig_district.add_trace(go.Bar(
                    x=district_impact["District"],
                    y=district_impact[cat],
                    name=cat,
                    marker_color=color,
                    text=district_impact[cat].apply(lambda x: f"{x:.1f}%"),
                    textposition="auto",
                    textfont=dict(size=9)
                ))
        
        # Update layout
        fig_district.update_layout(
            title="District-Specific Affordability Impact",
            xaxis_title=None,
            yaxis_title="% Income on Rent",
            barmode="group",
            height=250,
            margin=dict(l=30, r=30, t=40, b=30),
            font=dict(size=10),
            legend=dict(
                orientation="h", 
                y=1.02, 
                x=1, 
                font=dict(size=9)
            )
        )
        
        st.plotly_chart(fig_district, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown('</div>', unsafe_allow_html=True)

# Footer with minimal info
st.markdown(f"""
<div style="background-color:#f0f0f0; padding:5px; border-radius:3px; margin-top:5px; font-size:0.6em; text-align:center;">
Data Sources: Madrid Data Portal, CIS Survey 2014, El Confidencial (2024) | Settings: {incentive_level} | Districts: {len(selected_districts) if selected_districts else "All"}
</div>
""", unsafe_allow_html=True)