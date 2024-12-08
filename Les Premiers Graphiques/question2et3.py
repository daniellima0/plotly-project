import json
import plotly.express as px

# Load your JSON data from the file
with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r') as file:
    data = json.load(file)

# Prepare the data to count the articles by month
articles_by_month = {}

# Iterate through the years, months, and days to count the articles
for year in data["data-all"]:
    for month in data["data-all"][year]:
        # Count the number of articles for each day in the month
        num_articles = sum(1 for _ in data["data-all"][year][month].values())
        if f"{year}-{month}" not in articles_by_month:
            articles_by_month[f"{year}-{month}"] = 0
        articles_by_month[f"{year}-{month}"] += num_articles

# Prepare the data for plotting
months = list(articles_by_month.keys())
article_counts = list(articles_by_month.values())

# Create the bar chart
fig = px.bar(x=months, y=article_counts, labels={'x': 'Month', 'y': 'Number of Articles'},
             title='Number of Articles by Month')

# Show the figure
fig.show()

fig.write_html("./question3.html")

print(data["data-all"]["2019"]["10"]["9"][0])