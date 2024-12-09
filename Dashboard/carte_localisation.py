import json
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from geopy.geocoders import Nominatim

# Configurar o geolocalizador
geolocator = Nominatim(user_agent="geoapi")

# Função para normalizar localizações usando geopy
def normalize_location(location):
    try:
        geo_data = geolocator.geocode(location, language="en")
        if geo_data:
            # Extrai o país da última parte do endereço
            return geo_data.address.split(",")[-1].strip()
    except Exception as e:
        print(f"Erro ao normalizar {location}: {e}")
    return location  # Retorna o original se falhar

# Carregar os dados
with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r') as file:
    old_data = json.load(file)

# Processar os dados para Dash
def extract_location_data(data):
    loc_data = data["metadata"]["year"]
    all_locations = []

    for year, details in loc_data.items():
        if "loc" in details:
            loc_dict = details["loc"]
            for location, count in loc_dict.items():
                # Normalizar localizações
                normalized_location = normalize_location(location)
                all_locations.append({"year": year, "location": normalized_location, "count": count})

    return pd.DataFrame(all_locations)

df = extract_location_data(old_data)

# Criar aplicação Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Mapa de Localizações por Ano"),
    dcc.Dropdown(
        id='year-filter',
        options=[{'label': year, 'value': year} for year in df['year'].unique()],
        value=df['year'].unique()[0],
        placeholder="Selecione o Ano"
    ),
    dcc.Graph(id='location-map')
])

@app.callback(
    Output('location-map', 'figure'),
    [Input('year-filter', 'value')]
)
def update_map(selected_year):
    # Filtrar os dados para o ano selecionado
    filtered_df = df[df['year'] == selected_year]

    # Gerar mapa
    fig = px.scatter_geo(
        filtered_df,
        locations="location",
        locationmode="country names",
        size="count",
        hover_name="location",
        title=f"Localizações em {selected_year}"
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
