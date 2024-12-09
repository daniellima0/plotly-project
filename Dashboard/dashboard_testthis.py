import json
from collections import defaultdict
import numpy as np
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go

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

# Aggregate data for bar chart
combined_keywords = aggregate_all_keywords(combined_yearly_data)
years = ['all'] + sorted(combined_yearly_data.keys())

# Function to extract co-occurrence data
def extract_cooccurrence(data_tree, selected_year=None):
    cooccurrence_counts = defaultdict(int)
    all_keywords = set()

    for year, months in data_tree.items():
        if selected_year and str(year) != str(selected_year):
            continue
        for month, days in months.items():
            for day, articles in days.items():
                for article in articles:
                    keywords = set(article["kws"].keys())
                    all_keywords.update(keywords)
                    for kw1 in keywords:
                        for kw2 in keywords:
                            if kw1 != kw2:
                                cooccurrence_counts[(kw1, kw2)] += 1

    return cooccurrence_counts, all_keywords

# Create the Dash app
app = Dash()

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

    # Heatmap
    html.Div([
        dcc.Graph(id='keyword-heatmap', style={'height': '50vh'}),
    ])
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
    # Extract filtered co-occurrence data
    cooccurrences, all_keywords = extract_cooccurrence(recent_data["data"], selected_year if selected_year != 'all' else None)
    
    # Top co-occurrences and reduced keyword list
    top_cooccurrences = sorted(cooccurrences.items(), key=lambda x: x[1], reverse=True)[:20]
    top_keywords = set()
    for (kw1, kw2), _ in top_cooccurrences:
        top_keywords.update([kw1, kw2])

    keywords_list = list(top_keywords)
    keyword_index = {keyword: idx for idx, keyword in enumerate(keywords_list)}
    cooccurrence_matrix = np.zeros((len(keywords_list), len(keywords_list)))

    # Fill co-occurrence matrix
    for (kw1, kw2), count in cooccurrences.items():
        if kw1 in keyword_index and kw2 in keyword_index:
            i, j = keyword_index[kw1], keyword_index[kw2]
            cooccurrence_matrix[i, j] = count
            cooccurrence_matrix[j, i] = count  # Symmetric matrix

    # Calculate Pearson correlation matrix
    correlation_matrix = np.corrcoef(cooccurrence_matrix) if len(keywords_list) > 1 else np.array([[1]])

    # Heatmap figure
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
        title=f"Pearson Correlation Matrix of Top 10 Keyword Co-occurrences ({selected_year})",
        xaxis_title="Keywords",
        yaxis_title="Keywords",
        width=800,
        height=800
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
