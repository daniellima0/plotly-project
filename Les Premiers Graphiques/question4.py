import json
import plotly.express as px

# Load your JSON data from the file
with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r') as file:
    data = json.load(file)

my_dict = data["metadata-all"]["fr"]["all"]["kws"]

# Sort the keywords by frequency in descending order
sorted_keywords = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)

# Select the top 10 keywords (if there are fewer than 10, this will take all available keywords)
top_keywords = sorted_keywords[:10]

# Prepare the data for plotting
keywords = [keyword for keyword, _ in top_keywords]
frequencies = [freq for _, freq in top_keywords]

# Create the bar chart
fig = px.bar(x=keywords, y=frequencies, labels={'x': 'Keyword', 'y': 'Frequency'},
             title='Top 10 Most Used Keywords')

# Show the figure
fig.show()

# Optionally, save the figure as an HTML file
# fig.write_html("./top_keywords1.html")
