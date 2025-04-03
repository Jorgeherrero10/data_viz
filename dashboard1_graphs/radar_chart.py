import pandas as pd
import plotly.graph_objects as go

# Create the DataFrame using your data (using semicolon as delimiter)
data = """Year;Access to Housing;Unemployment;Political Issues;Job Quality;Immigration;Economic Crisis
2014;5;8;6;7;4;7
2024;9;7;6;7;5;6"""
from io import StringIO
df = pd.read_csv(StringIO(data), delimiter=';')

# Define the categories for the radar chart (all columns except 'Year')
categories = list(df.columns[1:])

# Create the interactive radar chart
fig = go.Figure()

# Loop over each year and add a trace.
for index, row in df.iterrows():
    # We close the loop by repeating the first value at the end.
    values = row[categories].tolist()
    values += values[:1]
    # Also repeat the first category at the end.
    cats = categories + [categories[0]]
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=cats,
        fill='toself',
        name=str(row['Year'])
    ))

# Update layout settings for aesthetics.
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 10]  # Adjust range as needed based on your scale
        )
    ),
    title="Concerns Comparison Between 2014 and 2024",
    showlegend=True
)

# Display the interactive radar chart.
fig.show()
