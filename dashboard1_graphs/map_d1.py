# dash_app.py
import dash
from dash import dcc, html, Input, Output, callback_context, dash_table
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

# Load your data (adjust paths as needed)
with open('data/DistritosMadrid.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

df_prices = pd.read_csv('data/prices.csv')
df_prices['Date'] = pd.to_datetime(df_prices['Date'])
df_avg = df_prices.groupby(['Date', 'District'])['Rent_Price'].mean().reset_index()

district_avgs = df_prices.groupby('District')['Rent_Price'].mean().to_dict()
min_rent = min(district_avgs.values())
max_rent = max(district_avgs.values())

def get_color(val, min_val, max_val):
    norm = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
    red_level = int(norm * 255)
    return f"#{red_level:02x}0000"

# Create district polygons
polygons = []
district_names = []
for feature in geojson_data['features']:
    positions = feature['geometry']['coordinates'][0]
    swapped_positions = [[coord[1], coord[0]] for coord in positions]
    district_name = feature['properties'].get('NOMBRE', 'Unknown')
    district_names.append(district_name)
    avg_rent = district_avgs.get(district_name, min_rent)
    fill_color = get_color(avg_rent, min_rent, max_rent)
    polygon = dl.Polygon(
        positions=swapped_positions,
        id={'type': 'district-polygon', 'index': district_name},
        color='Gray',
        fill=True,
        fillOpacity=0.6,
        fillColor=fill_color,
        n_clicks=0
    )
    polygons.append(polygon)

# Build the map container
map_component = dl.Map(
    center=[40.38, -3.68],
    zoom=10,
    children=[dl.TileLayer()] + polygons,
    style={'width': '100%', 'height': '100%'},
    id='map'
)
map_container = html.Div([
    map_component,
    html.Div([
        html.Div([
            html.Span("Low", style={'float': 'left', 'fontSize': '12px'}),
            html.Span("High", style={'float': 'right', 'fontSize': '12px'}),
            html.Div(style={'clear': 'both'})
        ]),
        html.Div(
            style={
                'height': '10px',
                'width': '150px',
                'background': 'linear-gradient(to right, #000000, #ff0000)'
            }
        )
    ],
    style={
        'position': 'absolute',
        'bottom': '10px',
        'right': '10px',
        'backgroundColor': 'white',
        'padding': '5px',
        'border': '1px solid gray',
        'fontFamily': 'Arial',
        'zIndex': '1000'
    })
], style={'position': 'relative', 'width': '100%', 'height': '45vh'})

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    html.H1("Madrid Housing Market"),
    html.Div([
        dcc.Graph(id='rent-graph', style={'height': '45vh'}),
        html.Div(map_container, style={'marginTop': '20px'})
    ])
])

@app.callback(
    Output('rent-graph', 'figure'),
    Input({'type': 'district-polygon', 'index': dash.ALL}, 'n_clicks')
)
def update_graph(n_clicks_list):
    ctx = callback_context
    selected_districts = []
    if n_clicks_list is not None:
        for i, n in enumerate(n_clicks_list):
            if n is not None and n % 2 == 1:
                selected_districts.append(district_names[i])
    
    if not selected_districts:
        filtered_df = df_avg.copy()
        title = "Average Rent Price by Date (All Districts)"
        default_opacity = 0.5
        overall_opacity = 1
    else:
        filtered_df = df_avg[df_avg['District'].isin(selected_districts)]
        title = "Average Rent Price by Date - " + ", ".join(selected_districts)
        default_opacity = 1
        overall_opacity = 0.2

    fig = px.line(filtered_df, x='Date', y='Rent_Price', color='District', title=title)
    for trace in fig.data:
        if trace.name != "Overall Mean":
            trace.opacity = default_opacity

    overall_df = df_prices.groupby('Date')['Rent_Price'].mean().reset_index()
    overall_trace = go.Scatter(
        x=overall_df['Date'],
        y=overall_df['Rent_Price'],
        mode='lines',
        name='Overall Mean',
        line=dict(dash='dash', color='black'),
        opacity=overall_opacity
    )
    fig.add_trace(overall_trace)
    fig.update_layout(
        yaxis_title="Rent Price (€ per M²)",
        xaxis_title="Date",
        margin=dict(l=80, r=40, t=60, b=40),
    )
    return fig

if __name__ == '__main__':
    # Run the Dash app on a dedicated port
    app.run(debug=True, port=8050)
