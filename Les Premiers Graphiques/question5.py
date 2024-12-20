import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Carregar os dados JSON
with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r') as file:
    data = json.load(file)

# Extrair os anos disponíveis a partir dos dados (baseado em "data['metadata-all']['fr']['year'].keys()")
years = ['all'] + sorted(data["metadata-all"]["fr"]["year"].keys())  # Incluindo 'all' como opção

# Inicializar o app Dash
app = dash.Dash(__name__)

# Layout do Dash
app.layout = html.Div([
    html.H1("Top 10 Palavras-Chave Mais Frequentes"),
    # Dropdown para selecionar o ano
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in years],
        value='all',  # Valor padrão é 'all'
        style={'width': '50%'}
    ),
    # Gráfico para exibir o gráfico de barras
    dcc.Graph(id='keyword-bar-chart')
])

# Função de callback para atualizar o gráfico com base no ano selecionado
@app.callback(
    Output('keyword-bar-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_bar_chart(selected_year):
    # Se 'all' for selecionado, agregamos as palavras-chave de todos os anos
    if selected_year == 'all':
        all_keywords = {}
        # Percorrer todos os anos para agregar as palavras-chave
        for year in years[1:]:  # Excluindo 'all'
            my_dict = data["metadata-all"]["fr"]["year"][year]["kws"]
            for keyword, freq in my_dict.items():
                all_keywords[keyword] = all_keywords.get(keyword, 0) + freq
        
        # Ordenar as palavras-chave por frequência em ordem decrescente
        sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)
    else:
        # Para um ano específico, extrair as palavras-chave desse ano
        my_dict = data["metadata-all"]["fr"]["year"][selected_year]["kws"]
        sorted_keywords = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Selecionar as top 10 palavras-chave
    top_keywords = sorted_keywords[:10]

    # Preparar os dados para o gráfico
    keywords = [keyword for keyword, _ in top_keywords]
    frequencies = [freq for _, freq in top_keywords]

    # Criar o gráfico de barras
    fig = px.bar(x=keywords, y=frequencies, labels={'x': 'Palavra-Chave', 'y': 'Frequência'},
                 title=f'Top 10 Palavras-Chave Mais Usadas em {selected_year}')

    return fig

# Rodar o servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)
