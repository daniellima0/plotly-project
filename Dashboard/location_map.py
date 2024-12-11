import json
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from geopy.geocoders import Nominatim
from tqdm import tqdm
import os
import pickle
from multiprocessing import Pool, cpu_count
from functools import lru_cache

# Configurer le géolocalisateur
geolocator = Nominatim(user_agent="geoapi", timeout=10)

# Créer ou charger le cache pour les normalisations
CACHE_FILE = "location_cache.pkl"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as cache_file:
        location_cache = pickle.load(cache_file)
else:
    location_cache = {}

# Décorateur pour la mise en cache des recherches géographiques
@lru_cache(maxsize=10000)
def normalize_location(location):
    if location in location_cache:
        return location_cache[location]

    try:
        geo_data = geolocator.geocode(location, language="en")
        if geo_data:
            normalized = geo_data.address.split(",")[-1].strip()
            location_cache[location] = normalized
            return normalized
    except Exception as e:
        print(f"Erreur lors de la normalisation de {location}: {e}")
    
    location_cache[location] = location
    return location

# Sauvegarder le cache dans un fichier
def save_cache():
    with open(CACHE_FILE, "wb") as cache_file:
        pickle.dump(location_cache, cache_file)

# Extraire les données de localisation et les normaliser
def extract_location_data(data):
    # Extraire et normaliser les données de localisation
    loc_data = data["metadata"]["year"]
    locations = [(location, year, count)
                 for year, details in loc_data.items()
                 for location, count in details.get("loc", {}).items()]
    
    print("Normalisation des localisations avec multiprocessing...")

    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm(pool.imap(normalize_location, [loc[0] for loc in locations]),
                            total=len(locations), desc="Localisations traitées"))
    
    all_locations = [{"year": loc[1], "location": normalized, "count": loc[2]}
                     for loc, normalized in zip(locations, results)]

    save_cache()
    
    return pd.DataFrame(all_locations)

if __name__ == "__main__":
    # Charger les données
    with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r') as file:
        old_data = json.load(file)

    # Traiter les données
    df = extract_location_data(old_data)

    # Créer l'application Dash
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Carte des Localisations par Année"),
        dcc.Dropdown(
            id='year-filter',
            options=[{'label': year, 'value': year} for year in df['year'].unique()],
            value=df['year'].unique()[0],
            placeholder="Sélectionner l'Année"
        ),
        dcc.Graph(id='location-map')
    ])

    @app.callback(
        Output('location-map', 'figure'),
        [Input('year-filter', 'value')]
    )
    def update_map(selected_year):
        # Filtrer les données et créer la carte pour l'année sélectionnée
        filtered_df = df[df['year'] == selected_year]

        # Créer une carte choroplèthe avec des pays colorés en fonction du nombre
        fig = px.choropleth(
            filtered_df,
            locations="location",  # La colonne des localisations
            locationmode="country names",  # Mode de localisation par nom de pays
            color="count",  # Valeur associée à la couleur
            hover_name="location",  # Nom de la localisation au survol
            color_continuous_scale="Viridis",  # Échelle de couleurs
            title=f"Localisations en {selected_year}",
            labels={"count": "Nombre d'occurrences"}  # Légende pour le nombre
        )
        
        # Ajouter une légende
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
            coloraxis_colorbar=dict(
                title="Nombre d'occurrences",  # Titre de la légende
                tickvals=[filtered_df['count'].min(), filtered_df['count'].max()],
                ticktext=[f"{filtered_df['count'].min()}", f"{filtered_df['count'].max()}"]
            )
        )
        return fig

    app.run_server(debug=True)
