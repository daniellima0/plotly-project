import json
import numpy as np
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
from datetime import datetime

# Load the data from JSON files
with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r', encoding='utf-8') as file:
    old_data = json.load(file)

with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r', encoding='utf-8') as file:
    recent_data = json.load(file)

# Function to merge the yearly keyword data
def merge_years(data1, data2):
    combined_years = {}
    all_years = set(data1.keys()).union(data2.keys())
    for year in all_years:
        kws1 = data1.get(year, {}).get("kws", {})
        kws2 = data2.get(year, {}).get("kws", {})
        combined_kws = {**kws1}
        for key, value in kws2.items():
            combined_kws[key] = combined_kws.get(key, 0) + value
        combined_years[year] = {"kws": combined_kws}
    return combined_years

# Combine yearly data
combined_yearly_data = merge_years(old_data["metadata"]["year"], recent_data["metadata"]["year"])

# Aggregate all keywords across all years
def aggregate_all_keywords(yearly_data):
    all_keywords = {}
    for year, details in yearly_data.items():
        kws = details.get("kws", {})
        for keyword, freq in kws.items():
            all_keywords[keyword] = all_keywords.get(keyword, 0) + freq
    return all_keywords



# Prepare data for keyword growth over months graph
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

# Function to extract co-occurrence data for keywords
def extract_cooccurrence(data_tree):
    cooccurrence_counts = defaultdict(int)
    all_keywords = set()

    for year in data_tree:
        for month in data_tree[year]:
            for day in data_tree[year][month]:
                articles = data_tree[year][month][day]
                for article in articles:
                    keywords = set(article["kws"].keys())
                    all_keywords.update(keywords)
                    for kw1 in keywords:
                        for kw2 in keywords:
                            if kw1 != kw2:
                                cooccurrence_counts[(kw1, kw2)] += 1

    return cooccurrence_counts, all_keywords

# Extract co-occurrence data from recent data
cooccurrences, all_keywords = extract_cooccurrence(recent_data["data"])

# Create a list of the top 10 keywords based on co-occurrence
top_cooccurrences = sorted(cooccurrences.items(), key=lambda x: x[1], reverse=True)[:20]
top_keywords = set()
for (kw1, kw2), _ in top_cooccurrences:
    top_keywords.update([kw1, kw2])

# Create a list of top keywords and their correlation matrix
keywords_list = list(top_keywords)
keyword_index = {keyword: idx for idx, keyword in enumerate(keywords_list)}

# Fill the co-occurrence matrix
cooccurrence_matrix = np.zeros((len(keywords_list), len(keywords_list)))
for (kw1, kw2), count in cooccurrences.items():
    if kw1 in keyword_index and kw2 in keyword_index:
        i, j = keyword_index[kw1], keyword_index[kw2]
        cooccurrence_matrix[i, j] = count
        cooccurrence_matrix[j, i] = count  # Symmetric matrix

# Calculate the correlation matrix
correlation_matrix = np.corrcoef(cooccurrence_matrix)

# Create the Dash app
app = Dash()

# Aggregate data for bar chart
combined_keywords = aggregate_all_keywords(combined_yearly_data)
years = ['all'] + sorted(combined_yearly_data.keys())

app.layout = html.Div([
    html.H1("Dashboard Projet Plotly Python - DATA 732"),

    # Dropdown for year selection
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in years],
        value='all',
        style={'width': '50%'}
    ),

    # Bar chart
    html.Div([ 
        dcc.Graph(id='keyword-bar-chart', style={'height': '50vh'}), 
    ]),
    # Line chart showing keyword growth over months
    html.Div([ 
        dcc.Graph(
            id='keyword-growth-graph',
            figure={
                'data': data_for_graph,
                'layout': go.Layout(
                    title="Keyword Growth Over Months (Old and Recent Data)",
                    xaxis={'title': 'Month', 'tickangle': 45},
                    yaxis={'title': 'Keyword Count'},
                    showlegend=True
                )
            },
            style={'height': '50vh'}
        ),
    ]),

    # Heatmap
    html.Div([ 
        dcc.Graph(id='keyword-heatmap', style={'height': '50vh'}),
    ]),
])

# Callback for bar chart
@app.callback(
    Output('keyword-bar-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_bar_chart(selected_year):
    if selected_year == 'all':
        year_keywords = combined_keywords
    else:
        year_keywords = combined_yearly_data.get(selected_year, {}).get("kws", {})
    
    sorted_keywords = sorted(year_keywords.items(), key=lambda x: x[1], reverse=True)
    top_keywords = sorted_keywords[:10]
    keywords = [keyword for keyword, _ in top_keywords]
    frequencies = [freq for _, freq in top_keywords]

    fig = px.bar(x=keywords, y=frequencies, labels={'x': 'Mots Clés', 'y': 'Fréquence'},
                 title=f'Les 10 mots-clés les plus utilisés en {selected_year}')
    return fig

# Callback for heatmap
@app.callback(
    Output('keyword-heatmap', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_heatmap(selected_year):
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=keywords_list,
        y=keywords_list,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Correlation"),
        text=np.round(correlation_matrix, 2),
        texttemplate="%{text}",
        hovertemplate="x: %{x}<br>y: %{y}<br>Correlation: %{z:.2f}<extra></extra>",
    ))

    fig.update_layout(
        title="Pearson Correlation Matrix of Top 10 Keyword Co-occurrences",
        xaxis_title="Keywords",
        yaxis_title="Keywords",
        width=800,
        height=800
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8081)
