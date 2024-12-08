import json
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud

# Carregar os dados dos dois arquivos JSON
with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r') as file:
    old_data = json.load(file)

with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r') as file:
    recent_data = json.load(file)

# Função para combinar os anos com dados sobrepostos
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

# Combinar os dados anuais dos dois arquivos
combined_yearly_data = merge_years(old_data["metadata"]["year"], recent_data["metadata"]["year"])

# Agregar todas as palavras-chave de todos os anos
def aggregate_all_keywords(yearly_data):
    all_keywords = {}
    for year, details in yearly_data.items():
        kws = details.get("kws", {})
        for keyword, freq in kws.items():
            all_keywords[keyword] = all_keywords.get(keyword, 0) + freq
    return all_keywords

# Dados agregados para todos os anos
combined_keywords = aggregate_all_keywords(combined_yearly_data)

# Lista de opções para o dropdown
years = ['all'] + sorted(combined_yearly_data.keys())

# Layout do Dash
app = Dash()

app.layout = html.Div([
    html.H1("Dashboard Projet Plotly Python - DATA 732"),
    
    # Dropdown para selecionar o ano
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in years],
        value='all',  # Valor padrão é 'all'
        style={'width': '50%'}
    ),
    
    # Gráficos
    html.Div([
        dcc.Graph(id='keyword-bar-chart', style={'height': '50vh'}),
        dcc.Graph(id='wordcloud-chart', style={'height': '50vh'}),
        dcc.Graph(id='keyword-trend-chart', style={'height': '50vh'})
    ])
])

# Callback para atualizar o gráfico de barras
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

# Callback para atualizar a nuvem de palavras
@app.callback(
    Output('wordcloud-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_wordcloud(selected_year):
    if selected_year == 'all':
        year_keywords = combined_keywords
    else:
        year_keywords = combined_yearly_data.get(selected_year, {}).get("kws", {})
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(year_keywords)
    fig = px.imshow(wordcloud, title=f'Nuage de mots en {selected_year}')
    fig.update_xaxes(visible=False).update_yaxes(visible=False)
    return fig

# Callback para atualizar o gráfico de tendências
@app.callback(
    Output('keyword-trend-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_trend_chart(selected_year):
    if selected_year == 'all':
        year_keywords = combined_keywords
    else:
        year_keywords = combined_yearly_data.get(selected_year, {}).get("kws", {})
    
    sorted_keywords = sorted(year_keywords.items(), key=lambda x: x[1], reverse=True)
    top_keywords = sorted_keywords[:10]
    keywords = [keyword for keyword, _ in top_keywords]
    frequencies = [freq for _, freq in top_keywords]

    fig = px.line(x=keywords, y=frequencies, labels={'x': 'Mots Clés', 'y': 'Fréquence'},
                  title=f'Les 10 principales tendances en matière de mots-clés {selected_year}')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
