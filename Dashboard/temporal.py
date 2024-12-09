import json
import dash
from dash import dcc, html
import plotly.graph_objs as go
from collections import defaultdict
from datetime import datetime

# Load the old data JSON
with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r') as file:
    old_data = json.load(file)

# Load the recent data JSON
with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r', encoding='utf-8') as file:
    recent_data = json.load(file)

# List of target keywords
keywords = [
    'pays', 'russie', 'russe', 'afrique', 'président',
    'ukraine', 'ministre', 'état', 'russes', 'militaire'
]

# Prepare a dictionary to hold the keyword counts per month for each year (merged across both datasets)
keyword_counts = defaultdict(lambda: defaultdict(int))  # Using defaultdict to automatically handle missing data

# Merge the data: Combine both old and recent data sources
data_sources = {
    "old_data": old_data,
    "recent_data": recent_data
}

# Process both datasets
for data_source, data in data_sources.items():
    # Extract years and months from the current data
    years = sorted(data["metadata"]["year"].keys())
    
    # Loop through each year and extract the months and keyword data
    for year in years:
        # Get all the months for this year
        months = sorted(data["metadata"]["month"][year].keys())
        
        # Extract keyword counts for each month in the current year
        for month in months:
            month_data = data["metadata"]["month"][year][month]["kws"]
            for keyword in keywords:
                # Add the count for the keyword for the given year and month
                keyword_counts[keyword][f"{year}-{month}"] += month_data.get(keyword, 0)

# Prepare the data for Plotly graph
data_for_graph = []

for keyword in keywords:
    # Sort months (convert 'YYYY-MM' to datetime for correct ordering)
    sorted_months = sorted(keyword_counts[keyword].keys(), key=lambda x: datetime.strptime(x, "%Y-%m"))
    counts = [keyword_counts[keyword][month] for month in sorted_months]
    
    # Create a trace for the keyword
    trace = go.Scatter(
        x=sorted_months,
        y=counts,
        mode='lines+markers',
        name=keyword
    )
    data_for_graph.append(trace)

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Keyword Growth Over Months", style={'text-align': 'center'}),
    
    dcc.Graph(
        id='keyword-growth-graph',
        figure={
            'data': data_for_graph,
            'layout': go.Layout(
                title="Keyword Growth Over Months",
                xaxis={'title': 'Month', 'tickangle': 45},
                yaxis={'title': 'Keyword Count'},
                showlegend=True
            )
        }
    ),
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, port=8082)
