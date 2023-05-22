import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
from util import two_opt
import folium
from streamlit_folium import folium_static

st.title('Visit Paris with your favorite movie!')

tournages = gpd.read_file("lieux_tournage_paris.shp")

tournages = tournages.rename(columns={"coord_x": "lon", "coord_y": "lat"}).drop("geometry", axis=1)

movie_sel = st.sidebar.selectbox('Select a movie', tournages.nom_tourna.unique())

movie_places = tournages[tournages['nom_tourna'] == movie_sel]

st.write(f'{len(movie_places)} places to visit for {movie_sel}')

# Create a matrix of places, with each row being a location in 2-space (function works in n-dimensions).
places = movie_places[["lon", "lat"]].to_numpy()

with st.spinner('Calculating distances...'):
    route = two_opt(places, 0.001)

    new_places_order = np.concatenate((np.array([places[route[i]] for i in range(len(route))]), np.array([places[0]])))
    new_places = pd.DataFrame(new_places_order, columns=['lon', 'lat'])

    # Create a Folium map object
    m = folium.Map(location=[48.8534, 2.3488],
                   zoom_start=12, control_scale=True)

    # Loop through each row in the dataframe
    tmp_place = new_places.iloc[0]
    for i, row in new_places.iterrows():
        # Add each row to the map
        folium.Marker(location=[row['lat'], row['lon']],
                      popup=None).add_to(m)

        if i > 0:
            # Add each polyline to the map
            folium.PolyLine(locations=[[tmp_place['lat'], tmp_place['lon']], [row['lat'], row['lon']]], color='red').add_to(m)
            tmp_place = row


    # Display the map using folium_static
    st_data = folium_static(m, width=700)

