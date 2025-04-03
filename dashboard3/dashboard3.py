import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set page config for wide layout
st.set_page_config(layout="wide", page_title="Madrid Housing Analytics")

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
    justify-content: center;
    text-align: center;
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
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* Force Plotly to center its content */
.js-plotly-plot {
    margin: 0 auto !important;
}

/* Center plot titles - very specific selectors */
.js-plotly-plot .plotly .main-svg .g-gtitle {
    text-anchor: middle !important;
}

/* Align axis titles to center */
.xtitle, .ytitle {
    text-anchor: middle !important;
}

/* Hide default streamlit footer */
footer {display: none !important;}
.stApp {height: 100vh !important;}

/* Adjust header margins */
h3 {
    margin-top: 0 !important;
    margin-bottom: 5px !important;
    font-size: 18px !important;
    text-align: center;
}

/* Adjust metrics to be more compact and centered */
[data-testid="stMetric"] {
    padding: 5px !important;
    text-align: center !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
[data-testid="stMetricLabel"] {
    margin-bottom: 0 !important;
    text-align: center !important;
    width: 100%;
    justify-content: center !important;
}
[data-testid="stMetricValue"] {
    margin-bottom: 0 !important;
    text-align: center !important;
    width: 100%;
    justify-content: center !important;
}
[data-testid="stMetricDelta"] {
    margin-top: 0 !important;
    text-align: center !important;
    width: 100%;
    justify-content: center !important;
}

/* Force content to fit in a single slide */
.main .block-container {
    max-height: calc(100vh - 20px) !important;
    overflow: hidden !important;
}

/* Adjust plotly charts to be more compact and centered */
.js-plotly-plot {
    margin-bottom: 0 !important;
}

/* Remove extra padding from markdown and center text */
.stMarkdown p {
    margin-bottom: 0 !important;
    text-align: center;
}

/* KPI grid */
.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 5px;
    text-align: center;
}
.kpi-item {
    padding: 5px;
    text-align: center;
}

/* Radio buttons more compact and centered */
.st-cc {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    text-align: center;
}

/* Tab control more compact */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 3px !important;
    text-align: center;
}

/* Center chart content and annotations */
.plotly .annotation-text {
    text-align: center !important;
}

/* Center the Analysis Insights box */
div[style*="background-color:#f8f9fa"] {
    text-align: center !important;
}
div[style*="background-color:#f8f9fa"] ul {
    display: inline-block;
    text-align: left;
}

/* Center Plotly SVG elements */
.svg-container {
    margin: 0 auto !important;
}

/* Override any specific chart elements to center them */
g.infolayer {
    text-anchor: middle !important;
}

/* Custom formatting for chart column containers */
[data-testid="column"] {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/* Add more space at the top for better title visibility */
div.appview-container {
    margin-top: 15px;
}

/* Selector dropdown styling */
div[data-baseweb="select"] {
    margin-bottom: 10px;
}

/* Add styles for Sankey diagram text - SOLID BLACK */
.js-plotly-plot .sankey .node text {
    fill: black !important;
    font-weight: bold !important;
    font-size: 14px !important;
    text-shadow: none !important; /* Remove text shadow */
}
</style>
""", unsafe_allow_html=True)

# Display the title bar
st.markdown('<div class="title-bar">Analytical Insights: Deep-Dive Financial Analysis</div>', unsafe_allow_html=True)

# Create a placeholder for KPIs to be filled later
kpi_placeholder = st.empty()

# --- Data Preparation ---
# Sankey Diagram Data
sankey_data = {
    'node_labels': ["Total Housing Budget", "Tax Incentives", "Remaining Budget", 
                    "Affordable Housing Programs", "Rental Assistance", "Other Housing Initiatives"],
    'node_colors': ["#3498db", "#e74c3c", "#2980b9", "#27ae60", "#8e44ad", "#f39c12"],
    'link_sources': [0, 0, 2, 2, 2],
    'link_targets': [1, 2, 3, 4, 5],
    'link_values': [27.8, 72.2, 24, 28.2, 20],
    'link_colors': ["rgba(231, 76, 60, 0.4)", "rgba(41, 128, 185, 0.4)", 
                    "rgba(39, 174, 96, 0.4)", "rgba(142, 68, 173, 0.4)", "rgba(243, 156, 18, 0.4)"]
}

# Waterfall Chart Data
waterfall_data = {
    'measures': ['relative', 'relative', 'total'],
    'labels': ['Tax Savings', 'Rent Reduction', 'Net Gain'],
    'text_values': ['€7,313', '−€1,440', '€5,873'],
    'values': [7312.68, -1440, None]
}

# Long-term Projection Data
years = list(range(2025, 2035))
current_property_tax = 500
growth_without = 0.02
growth_with = 0.03
revenue_without = [current_property_tax * (1 + growth_without)**t for t in range(10)]
revenue_with = [current_property_tax * (1 + growth_with)**t for t in range(10)]
revenue_diff = [with_ - without_ for with_, without_ in zip(revenue_with, revenue_without)]
cumulative_diff = sum(revenue_diff)

# Sustainability KPIs data
roi = (cumulative_diff / 27.8) * 100  # ROI percentage
initial_investment = 27.8  # million euros
cumulative_revenue_diff = np.cumsum(revenue_diff)
years_to_payback = np.searchsorted(cumulative_revenue_diff, initial_investment)
if years_to_payback >= len(cumulative_revenue_diff):
    payback_period = 10.0
else:
    if years_to_payback == 0:
        payback_period = initial_investment / cumulative_revenue_diff[0]
    else:
        prev_cumulative = cumulative_revenue_diff[years_to_payback-1] if years_to_payback > 0 else 0
        remaining = initial_investment - prev_cumulative
        year_diff = cumulative_revenue_diff[years_to_payback] - prev_cumulative
        payback_period = years_to_payback + (remaining / year_diff)
revenue_growth = ((revenue_with[-1] / revenue_without[-1]) - 1) * 100  # % increase in final year
social_impact = 25.2  # Average percentage improvement in affordability

# Correlation Analysis Data
np.random.seed(42)
incentive_amounts = np.linspace(0, 10000, 20)
base_participation = 5
noise = np.random.normal(0, 5, 20)
participation_rates = np.clip(base_participation + incentive_amounts * 0.006 + noise, 0, 100)
correlation = np.corrcoef(incentive_amounts, participation_rates)[0, 1]
r_squared = correlation ** 2

# District Analysis Data
districts = [
    "Salamanca", "Centro", "Chamberí", "Chamartín", "Arganzuela",
    "Tetuán", "Retiro", "Moncloa-Aravaca", "Fuencarral-El Pardo", "Usera"
]
affordability_improvement = [30.1, 26.5, 24.3, 23.7, 20.5, 19.8, 22.1, 21.5, 18.7, 17.2]
incentive_cost = [235, 220, 210, 190, 160, 150, 180, 175, 140, 125]
implementation_complexity = [4, 4, 3, 3, 2, 2, 3, 3, 2, 1]
roi_ratio = [a/c * 100 for a, c in zip(affordability_improvement, np.array(incentive_cost)/100)]

district_analysis = pd.DataFrame({
    'District': districts,
    'Affordability Improvement (%)': affordability_improvement,
    'Incentive Cost (€/unit)': incentive_cost,
    'Implementation Complexity': implementation_complexity,
    'ROI Ratio': roi_ratio
})

# Sidebar controls
with st.sidebar:
    st.header("Analysis Controls")
    
    # Incentive budget slider
    incentive_budget = st.slider(
        "Incentive Budget (% of total)",
        min_value=20.0, max_value=40.0, value=27.8, step=0.1,
        help="Percentage of total housing budget allocated to incentives"
    )
    
    # Tax savings slider
    tax_savings = st.slider(
        "Tax Savings per Landlord (€)",
        min_value=5000, max_value=9000, value=7313, step=100,
        help="Average tax savings per participating landlord"
    )
    
    # Growth rate without program
    growth_rate_without = st.slider(
        "Base Growth Rate (%)",
        min_value=1.0, max_value=3.0, value=2.0, step=0.1,
        help="Annual growth rate without program"
    ) / 100
    
    # Growth rate with program
    growth_rate_with = st.slider(
        "Enhanced Growth Rate (%)",
        min_value=growth_rate_without*100 + 0.1, max_value=5.0, 
        value=3.0, step=0.1,
        help="Annual growth rate with program"
    ) / 100
    
    # District selection
    selected_districts = st.multiselect(
        "Select Districts for Analysis",
        districts,
        default=[],
        help="Select specific districts to focus the analysis on"
    )
    
    # Analysis view
    analysis_view = st.radio(
        "District Analysis View",
        ["Quadrant Analysis", "Heatmap Analysis"],
        index=0
    )
    
    st.button("Reset Filters", on_click=lambda: None)

# --- Recalculation of Values based on Sidebar ---
# Recalculate values for Sankey
updated_sankey_values = [incentive_budget, 100-incentive_budget]
remaining_budget = 100 - incentive_budget
updated_remaining_values = [
    remaining_budget * 24/72.2, 
    remaining_budget * 28.2/72.2, 
    remaining_budget * 20/72.2
]

# Recalculate values for waterfall
rent_reduction = -1440  # Keep this fixed for simplicity
updated_net_gain = tax_savings + rent_reduction

# Recalculate long-term projection
updated_revenue_without = [current_property_tax * (1 + growth_rate_without)**t for t in range(10)]
updated_revenue_with = [current_property_tax * (1 + growth_rate_with)**t for t in range(10)]
updated_revenue_diff = [with_ - without_ for with_, without_ in zip(updated_revenue_with, updated_revenue_without)]
updated_cumulative_diff = sum(updated_revenue_diff)

# Recalculate KPIs
updated_roi = (updated_cumulative_diff / incentive_budget) * 100
updated_cumulative_revenue_diff = np.cumsum(updated_revenue_diff)
years_to_payback = np.searchsorted(updated_cumulative_revenue_diff, incentive_budget)
if years_to_payback >= len(updated_cumulative_revenue_diff):
    updated_payback_period = 10.0
else:
    if years_to_payback == 0:
        updated_payback_period = incentive_budget / updated_cumulative_revenue_diff[0]
    else:
        prev_cumulative = updated_cumulative_revenue_diff[years_to_payback-1] if years_to_payback > 0 else 0
        remaining = incentive_budget - prev_cumulative
        year_diff = updated_cumulative_revenue_diff[years_to_payback] - prev_cumulative
        updated_payback_period = years_to_payback + (remaining / year_diff)
updated_revenue_growth = ((updated_revenue_with[-1] / updated_revenue_without[-1]) - 1) * 100

# Filter district data if needed
if selected_districts:
    filtered_district_analysis = district_analysis[district_analysis['District'].isin(selected_districts)]
else:
    filtered_district_analysis = district_analysis

# --- Fill the KPI placeholder we created earlier ---
with kpi_placeholder.container():
    # Use a single full-width row for KPIs
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.metric(
            label="10-Year ROI",
            value=f"{updated_roi:.1f}%",
            delta=f"{updated_roi - 100:.1f}%" if updated_roi > 100 else f"{updated_roi - 100:.1f}%"
        )

    with kpi_cols[1]:
        st.metric(
            label="Payback Period",
            value=f"{updated_payback_period:.1f} years",
            delta=f"{5 - updated_payback_period:.1f} years" if updated_payback_period < 5 else f"{updated_payback_period - 5:.1f} years",
            delta_color="inverse"
        )

    with kpi_cols[2]:
        st.metric(
            label="Revenue Growth",
            value=f"{updated_revenue_growth:.1f}%",
            delta=f"{updated_revenue_growth:.1f}%"
        )

    with kpi_cols[3]:
        st.metric(
            label="Affordability Improvement",
            value=f"{social_impact:.1f}%",
            delta=f"{social_impact - 20:.1f}%"
        )

# --- Layout: Row 1 (2 Charts Side-by-Side taking full width) ---
row1_col1, row1_col2 = st.columns(2)

# 1) Sankey Diagram
with row1_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_sankey = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=1.5),
            label=sankey_data['node_labels'],
            color=sankey_data['node_colors'],
            hoverlabel=dict(
                bgcolor="white",
                bordercolor="black",
                font=dict(size=14, family="Arial", color="black")
            )
        ),
        link=dict(
            source=sankey_data['link_sources'],
            target=sankey_data['link_targets'],
            value=[incentive_budget, remaining_budget, *updated_remaining_values],
            color=sankey_data['link_colors'],
            hovertemplate='%{value:.1f}% from %{source.label}<br>to %{target.label}<extra></extra>'
        )
    )])
    
    fig_sankey.update_layout(
        title=dict(
            text='Housing Budget Flow Analysis (€100M Total)', 
            x=0.5,
            font=dict(size=16),
            xanchor='center',
            yanchor='top'
        ),
        font=dict(size=14),  # Keep global size, remove color override
        height=310,
        margin=dict(l=20, r=20, t=40, b=60),
        paper_bgcolor='white'
    )
    
    # Annotation about budget allocation
    fig_sankey.add_annotation(
        x=0.5, y=-0.15,
        xref='paper', yref='paper',
        text=f'<b>{incentive_budget:.1f}%</b> of the total budget is allocated to tax incentives',
        showarrow=False,
        font=dict(size=14, color='black'),
        align='center',
        bgcolor='rgba(220, 239, 110, 0.8)',
        bordercolor='#3498db',
        borderwidth=1,
        borderpad=8,
        opacity=0.9
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# 2) Waterfall Chart
with row1_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_waterfall = go.Figure(go.Waterfall(
        name='Waterfall',
        orientation='v',
        measure=waterfall_data['measures'],
        x=waterfall_data['labels'],
        textposition='auto',
        text=[f'€{tax_savings:,.0f}', f'−€{abs(rent_reduction):,.0f}', f'€{tax_savings + rent_reduction:,.0f}'],
        y=[tax_savings, rent_reduction, None],
        connector={'line': {'color': 'grey'}},
        decreasing={'marker': {'color': '#d62728'}},  # Red for losses
        increasing={'marker': {'color': '#2ca02c'}},  # Green for gains
        totals={'marker': {'color': '#1f77b4'}}        # Blue for total
    ))
    
    fig_waterfall.update_layout(
        title=dict(
            text='Landlord Financial Impact Analysis (Per Property)', 
            x=0.5,
            font=dict(size=16),
            xanchor='center',
            yanchor='top'
        ),
        xaxis_title='Financial Components',
        yaxis_title='Amount (€)',
        height=310,
        margin=dict(l=30, r=30, t=40, b=30),
        showlegend=False,
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgrey')
    )
    
    # Add annotations for explanation
    fig_waterfall.add_annotation(
        x=0, y=tax_savings * 1.05,
        text='Tax incentive benefit',
        showarrow=False,
        font=dict(size=11),
        yshift=10
    )
    fig_waterfall.add_annotation(
        x=1, y=rent_reduction * 0.5,
        text='Controlled rent impact',
        showarrow=False,
        font=dict(size=11),
        yshift=-10
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- Layout: Row 2 (Combined chart with selector and insights side by side) ---
row2_col1, row2_col2 = st.columns([0.7, 0.3])  # 70/30 split for charts and insights

# Combined chart with selector (left side - 70%)
with row2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Add a selector for the chart type
    chart_type = st.selectbox(
        "Select Chart", 
        ["Long-term Projection", "Correlation Analysis", "District Analysis"],
        index=0
    )
    
    # Create the selected chart based on user choice
    if chart_type == "Long-term Projection":
        # Long-term Revenue Projection
        fig_combined = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_combined.add_trace(go.Scatter(
            x=years, y=updated_revenue_without, name='Without Program',
            line=dict(color='steelblue', width=3),
            hovertemplate='%{y:.1f}M €'
        ), secondary_y=False)
        
        fig_combined.add_trace(go.Scatter(
            x=years, y=updated_revenue_with, name='With Program',
            line=dict(color='green', width=3),
            fill='tonexty', fillcolor='rgba(0,128,0,0.1)',
            hovertemplate='%{y:.1f}M €'
        ), secondary_y=False)
        
        fig_combined.add_trace(go.Bar(
            x=years, y=updated_revenue_diff, name='Annual Gain',
            marker_color='orange',
            text=[f"€{val:.1f}M" for val in updated_revenue_diff],
            textposition='outside',
            textfont=dict(size=9),
            hovertemplate='+%{y:.1f}M €'
        ), secondary_y=True)
        
        fig_combined.update_layout(
            title=dict(
                text='Long-term Property Tax Revenue Projection (2025–2034)', 
                x=0.5,
                y=0.98,
                font=dict(size=16),
                xanchor='center',
                yanchor='top'
            ),
            xaxis_title='Year',
            height=310,
            margin=dict(l=40, r=40, t=60, b=40),  # Increased top margin
            plot_bgcolor='white',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center', 
                x=0.5,
                font=dict(size=10),
                bgcolor='rgba(255,255,255,0.8)'
            )
        )
        fig_combined.update_yaxes(title_text='Tax Revenue (M €)', secondary_y=False, showgrid=True, gridcolor='lightgray')
        fig_combined.update_yaxes(title_text='Extra Gain (M €)', secondary_y=True, range=[0, max(updated_revenue_diff) * 1.6])
        
        # Cumulative gain annotation
        fig_combined.add_annotation(
            x=2030, y=max(updated_revenue_diff) * 1.3,
            text=f"<b>Cumulative 10-Year Gain:</b><br>+€{updated_cumulative_diff:.1f}M",
            showarrow=False,
            font=dict(size=11, color='orange'),
            bgcolor='white', bordercolor='orange',
            borderwidth=1, borderpad=5
        )
        
    elif chart_type == "Correlation Analysis":
        # Correlation Analysis chart
        fig_combined = go.Figure()
        
        # Scatter plot
        fig_combined.add_trace(go.Scatter(
            x=incentive_amounts,
            y=participation_rates,
            mode='markers',
            name='Data Points',
            marker=dict(size=8, color='royalblue', line=dict(width=1, color='black'))
        ))
        
        # Trendline
        trendline = np.poly1d(np.polyfit(incentive_amounts, participation_rates, 1))
        fig_combined.add_trace(go.Scatter(
            x=incentive_amounts,
            y=trendline(incentive_amounts),
            mode='lines',
            name='Trendline',
            line=dict(color='red', width=2)
        ))
        
        # Correlation annotation
        fig_combined.add_annotation(
            x=1000, y=90,
            text=f"<b>Correlation:</b> {correlation:.2f}<br><b>R²:</b> {r_squared:.2f}",
            showarrow=False,
            bgcolor='white',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=11),
            align='left'
        )
        
        # Fixed Annotations
        annotations = {
            0: 'No Incentives',
            3000: 'Partial Incentives',
            7000: 'Full Incentives'
        }
        
        for x_val, label in annotations.items():
            idx = np.abs(incentive_amounts - x_val).argmin()
            y_val = participation_rates[idx]
            fig_combined.add_annotation(
                x=x_val,
                y=y_val,
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor='gray',
                ax=-30,
                ay=-30,
                font=dict(size=10)
            )
        
        # Layout Settings
        fig_combined.update_layout(
            title=dict(
                text='Correlation: Tax Incentives & Landlord Participation', 
                x=0.5,
                font=dict(size=16),
                xanchor='center',
                yanchor='top'
            ),
            xaxis_title='Tax Incentive Amount (€)',
            yaxis_title='Landlord Participation Rate (%)',
            height=310,
            margin=dict(l=40, r=20, t=40, b=40),
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgrey', tickformat=',.0f'),
            yaxis=dict(showgrid=True, gridcolor='lightgrey'),
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.6)', font=dict(size=10))
        )
        
    else:  # District Analysis
        # District Analysis chart - using the analysis_view from sidebar
        if analysis_view == "Quadrant Analysis":
            # Compute averages
            avg_cost = filtered_district_analysis['Incentive Cost (€/unit)'].mean()
            avg_improvement = filtered_district_analysis['Affordability Improvement (%)'].mean()
            x_max = filtered_district_analysis['Incentive Cost (€/unit)'].max() * 1.15
            y_max = filtered_district_analysis['Affordability Improvement (%)'].max() * 1.15
            
            # Base scatter
            fig_combined = px.scatter(
                filtered_district_analysis,
                x='Incentive Cost (€/unit)',
                y='Affordability Improvement (%)',
                size='ROI Ratio',
                color='Implementation Complexity',
                hover_name='District',
                text='District',
                color_continuous_scale='Viridis',
                labels={
                    'Incentive Cost (€/unit)': 'Incentive Cost (€/unit)',
                    'Affordability Improvement (%)': 'Affordability Improvement (%)',
                    'Implementation Complexity': 'Implementation Complexity (1–5)'
                }
            )
            
            # Quadrant lines
            fig_combined.add_shape(
                type="line", x0=avg_cost, y0=0, x1=avg_cost, y1=y_max,
                line=dict(color="gray", width=1, dash="dash")
            )
            fig_combined.add_shape(
                type="line", x0=0, y0=avg_improvement, x1=x_max, y1=avg_improvement,
                line=dict(color="gray", width=1, dash="dash")
            )
            
            # Quadrant labels
            fig_combined.add_annotation(
                x=avg_cost / 2, y=avg_improvement * 1.1,
                text="<b>High Impact<br>Low Cost</b>",
                showarrow=False,
                font=dict(size=10, color="green")
            )
            fig_combined.add_annotation(
                x=avg_cost * 1.25, y=avg_improvement * 1.1,
                text="<b>High Impact<br>High Cost</b>",
                showarrow=False,
                font=dict(size=10, color="blue")
            )
            fig_combined.add_annotation(
                x=avg_cost / 2, y=avg_improvement * 0.4,
                text="<b>Low Impact<br>Low Cost</b>",
                showarrow=False,
                font=dict(size=10, color="orange")
            )
            fig_combined.add_annotation(
                x=avg_cost * 1.25, y=avg_improvement * 0.4,
                text="<b>Low Impact<br>High Cost</b>",
                showarrow=False,
                font=dict(size=10, color="red")
            )
            
            # Layout
            fig_combined.update_layout(
                title=dict(
                    text='District Cost-Effectiveness Analysis', 
                    x=0.5,
                    font=dict(size=16),
                    xanchor='center',
                    yanchor='top'
                ),
                height=310,
                margin=dict(l=40, r=20, t=40, b=40),
                plot_bgcolor='white',
                xaxis=dict(
                    title='Incentive Cost (€/unit)',
                    gridcolor='lightgrey',
                    zeroline=False,
                    range=[0, x_max]
                ),
                yaxis=dict(
                    title='Affordability Improvement (%)',
                    gridcolor='lightgrey',
                    zeroline=False,
                    range=[0, y_max]
                ),
                coloraxis_colorbar=dict(
                    title="Complexity",
                    tickvals=[1, 2, 3, 4],
                    ticktext=["Low", "Medium", "High", "Very High"],
                    lenmode="fraction",
                    len=0.75
                )
            )
            
            # Marker styling
            fig_combined.update_traces(
                textposition='top center',
                marker=dict(
                    line=dict(width=1, color='DarkSlateGrey'),
                    sizemode='area',
                    sizeref=2.*max(filtered_district_analysis['ROI Ratio'])/(30**2),
                    sizemin=5
                ),
                textfont=dict(size=9, color='black')
            )
            
        else:  # Heatmap Analysis
            # Sort by ROI for better visualization
            df_sorted = filtered_district_analysis.sort_values(by='ROI Ratio', ascending=False)
            
            # Heatmap matrix data
            z_data = [
                df_sorted['ROI Ratio'].values,
                df_sorted['Incentive Cost (€/unit)'].values,
                df_sorted['Affordability Improvement (%)'].values,
            ]
            
            # Labels
            y_labels = ['ROI Ratio', 'Incentive Cost (€)', 'Affordability (%)']
            x_labels = df_sorted['District'].tolist()
            
            # Text for display inside cells
            text_data = [
                [f"{val:.2f}" for val in df_sorted['ROI Ratio']],
                [f"€{val:.0f}" for val in df_sorted['Incentive Cost (€/unit)']],
                [f"{val:.1f}%" for val in df_sorted['Affordability Improvement (%)']]
            ]
            
            # Heatmap
            fig_combined = go.Figure(data=go.Heatmap(
                z=z_data,
                x=x_labels,
                y=y_labels,
                text=text_data,
                texttemplate="%{text}",
                textfont=dict(size=10),
                colorscale='RdBu_r',
                reversescale=False,
                colorbar=dict(title='Value', thickness=15, len=0.7)
            ))
            
            # Layout
            fig_combined.update_layout(
                title=dict(
                    text='District-Level Affordability vs. Costs', 
                    x=0.5,
                    font=dict(size=16),
                    xanchor='center',
                    yanchor='top'
                ),
                xaxis=dict(title='District', tickangle=-30),
                yaxis=dict(title='Metric', autorange='reversed'),
                height=310,
                margin=dict(l=40, r=20, t=40, b=50)
            )
    
    # Display the selected chart
    st.plotly_chart(fig_combined, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# Analysis Insights (right side - 30%)
with row2_col2:
    st.markdown("""
    <div style="background-color:#f8f9fa; padding:15px; border-radius:8px; font-size:0.95em; height: 100%; display:flex; flex-direction:column; justify-content:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #eee;">
    <h3 style="text-align: center; color:#333; margin-bottom:15px; border-bottom: 2px solid #dcef6e; padding-bottom:8px; margin-top:0;">Analysis Insights</h3>
    <div style="display: flex; flex-direction: column; justify-content: space-around; flex-grow: 1;">
        <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;">
            <span style="font-weight: bold; color:#2c3e50;">Program Payback:</span><br>
            <span style="font-size: 1.1em; color:#333;">Pays for itself in <b>{updated_payback_period:.1f} years</b></span>
        </div>
        <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;">
            <span style="font-weight: bold; color:#2c3e50;">Revenue Impact:</span><br>
            <span style="font-size: 1.1em; color:#333;">Generates <b>€{updated_cumulative_diff:.1f}M</b> over 10 years</span>
        </div>
        <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;">
            <span style="font-weight: bold; color:#2c3e50;">Budget Allocation:</span><br>
            <span style="font-size: 1.1em; color:#333;">Tax incentives are <b>{incentive_budget:.1f}%</b> of housing budget</span>
        </div>
        <div style="padding: 8px; background-color: rgba(255,255,255,0.6); border-radius: 5px;">
            <span style="font-weight: bold; color:#2c3e50;">Landlord Benefit:</span><br>
            <span style="font-size: 1.1em; color:#333;">Average gain of <b>€{updated_net_gain:.0f}</b> annually</span>
        </div>
    </div>
    </div>
    """.format(
        updated_payback_period=updated_payback_period,
        updated_cumulative_diff=updated_cumulative_diff,
        incentive_budget=incentive_budget,
        updated_net_gain=updated_net_gain
    ), unsafe_allow_html=True)

# Footer with minimal info
st.markdown(f"""
<div style="background-color:#f0f0f0; padding:5px; border-radius:3px; margin-top:5px; font-size:0.6em; text-align:center;">
Data Sources: Madrid Property Tax Revenue Reports, Landlord Survey 2023, District Affordability Analysis | Budget Allocation: {incentive_budget:.1f}% | Growth Rate: {growth_rate_with*100:.1f}%
</div>
""", unsafe_allow_html=True)