import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
from util import two_opt
import folium
from streamlit_folium import folium_static
import requests

st.title('Visit Paris with your favorite movie!')

# url_tournages = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/lieux-de-tournage-a-paris/exports/geojson?lang=fr&timezone=Europe%2FBerlin'
# tournages_json = folium.GeoJson(url_tournages, name="lieux de tournages")
# st.write(tournages_json.convert_to_feature_collection())


tournages = gpd.read_file("lieux_tournage_paris.shp", encoding='utf-8')

tournages = tournages.drop("geometry", axis=1)

movie_sel = st.sidebar.selectbox('Select a movie', tournages.nom_tourna.unique())

movie_places = tournages[tournages['nom_tourna'] == movie_sel]

#st.dataframe(movie_places)

st.write(f"{movie_sel} is a {movie_places['type_tourn'][0]} registrered by {movie_places['nom_realis'][0]} in {movie_places['annee_tour'][0]}.")

# Create a matrix of places, with each row being a location in 2-space (function works in n-dimensions).
places = movie_places[["coord_x", "coord_y"]].to_numpy()

with st.spinner('Calculating distances...'):
    route = two_opt(places, 0.001)

    new_places_order = np.concatenate((np.array([places[route[i]] for i in range(len(route))]), np.array([places[0]])))
    new_places = pd.DataFrame(new_places_order, columns=['coord_x', 'coord_y'])

    # Create a Folium map object
    m = folium.Map(location=[48.8534, 2.3488],
                   zoom_start=12, control_scale=True)

    # Loop through each row in the dataframe
    tmp_place = new_places.iloc[0]

    distance = 0
    duration = 0

    for i, row in new_places.iterrows():
        # Add each row to the map
        folium.CircleMarker(location=[row['coord_y'], row['coord_x']],
                      popup=None, color='blue', radius=2).add_to(m)

        if i > 0:
            url = f"https://wxs.ign.fr/calcul/geoportail/itineraire/rest/1.0.0/route?resource=bdtopo-osrm&profile=pedestrian&optimization=shortest&timeUnit=hour&distanceUnit=kilometer&getSteps=false&start={tmp_place['coord_x']},{tmp_place['coord_y']}&end={row['coord_x']},{row['coord_y']}"
            response = requests.get(url)
            data = response.json()
            geometry = data['geometry']
            folium.GeoJson(geometry).add_to(m)

            distance += data['distance']
            duration += data['duration']

            tmp_place = row

    # Display the map using folium_static
    st_data = folium_static(m, width=700)

    st.write(f'These {len(movie_places)} filming locations in Paris could be visited by walking {round(distance, 2)} km in {int(duration)}h{int(round((duration % 1) * 60))}.')
