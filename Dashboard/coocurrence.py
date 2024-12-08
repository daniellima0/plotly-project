import json
from collections import defaultdict
import numpy as np
import plotly.graph_objects as go

# Step 1: Load the data
with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Step 2: Extract co-occurrence data
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

# Get the cooccurrence counts and list of all keywords
cooccurrences, all_keywords = extract_cooccurrence(data["data"])

# Step 3: Identify the 10 most frequent co-occurrences
top_cooccurrences = sorted(cooccurrences.items(), key=lambda x: x[1], reverse=True)[:20]
top_keywords = set()
for (kw1, kw2), _ in top_cooccurrences:
    top_keywords.update([kw1, kw2])

# Create a reduced keyword list and index map
keywords_list = list(top_keywords)
keyword_index = {keyword: idx for idx, keyword in enumerate(keywords_list)}

# Initialize the co-occurrence matrix for top keywords
cooccurrence_matrix = np.zeros((len(keywords_list), len(keywords_list)))

# Fill the reduced co-occurrence matrix
for (kw1, kw2), count in cooccurrences.items():
    if kw1 in keyword_index and kw2 in keyword_index:
        i, j = keyword_index[kw1], keyword_index[kw2]
        cooccurrence_matrix[i, j] = count
        cooccurrence_matrix[j, i] = count  # Symmetric matrix

# Step 4: Calculate the Pearson correlation matrix
correlation_matrix = np.corrcoef(cooccurrence_matrix)

# Step 5: Create a heatmap using Plotly
fig = go.Figure(data=go.Heatmap(
    z=correlation_matrix,
    x=keywords_list,
    y=keywords_list,
    colorscale='RdBu',  # Diverging colorscale for stronger colors at extremes
    zmin=-1,  # Minimum correlation value
    zmax=1,   # Maximum correlation value
    colorbar=dict(title="Correlation"),
    text=np.round(correlation_matrix, 2),  # Round the values for display
    texttemplate="%{text}",  # Display text in each square
    hovertemplate="x: %{x}<br>y: %{y}<br>Correlation: %{z:.2f}<extra></extra>",
))

fig.update_layout(
    title="Pearson Correlation Matrix of Top 10 Keyword Co-occurrences",
    xaxis_title="Keywords",
    yaxis_title="Keywords",
    width=800,
    height=800
)

# Show the plot
fig.show()
