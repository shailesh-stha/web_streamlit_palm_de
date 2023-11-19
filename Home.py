# standard library
import os
import time
# third-party library
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import folium
import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd


# local imports
from utils import read_netcdf, display_map, display_matplots, display_plotly, useful_functions

# Start clock to test out site load time
start_time = time.time()
# Define Page layout
st.set_page_config(page_title="PALM output Visualization",
                   layout="centered",
                   initial_sidebar_state="collapsed") #collapsed/expanded

# Import CSS style
with open('./css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Define band and time sequence based on the file to be used
simulation_domain = "N03_reduced"
def band_time_sequence():
    if simulation_domain == "N03":
        # Define band sequence and time sequence
        x_tick_interval = 1 # 1 hour
        band_sequence = [0]
        band_sequence.extend(np.arange(5, 144, 6*x_tick_interval))
        time_sequence = []
        for i, band_index in enumerate(band_sequence):
            time = useful_functions.band_index_to_time_hr_min(band_index)
            time_sequence.append(time)
            
        # Update time by few time steps to get better result in graph (temporary solution)
        band_sequence[15] = 90
        band_sequence[13] = 78
        band_sequence_backup = band_sequence.copy()
        band_sequence_backup[13] = 77
        return band_sequence, band_sequence_backup, time_sequence
    
    elif simulation_domain == "N03_reduced":
        band_sequence = list(range(0,25))
        band_sequence_backup = band_sequence.copy()
        time_sequence = ['0:00', '1:00', '2:00', '3:00', '4:00', '5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '24:00']
        return band_sequence, band_sequence_backup, time_sequence
        
band_sequence, band_sequence_backup, time_sequence = band_time_sequence()

# Website Introduction
with st.container():
    st.header("Urbane Hitzeinseln - Planungsvarianten zur Reduktion von Hitzestress")
    st.write("""Entdecken Sie die Möglichkeiten der hochaufgelösten, mikroskaligen Stadtklimasimulation mit der innovativen Software PALM4U!
             Optimieren Sie Ihre Entscheidungsprozesse und gestalten Sie städtische Umgebungen nachhaltiger durch die präzise Analyse verschiedenster Szenarien.
             Erhalten Sie detaillierte Einblicke in die Temperaturverteilung im Außenraum.
             Bewerten Sie den thermischen Komfort und steigern Sie den Komfort für Bewohner.
             Analysieren Sie den Kaltlufthaushalt und urbane Luftleitbahnen.
             Verstehen Sie die Wege, die kühle Luft in der Stadt nimmt, und optimieren Sie die Luftzirkulation für ein angenehmes Stadtklima.
             Analysieren Sie Windmuster, um den Windkomfort zu verbessern und Gefahren im Zusammenhang mit Stürmen zu erkennen.
             Erfassen Sie die Auswirkungen des Klimawandels auf städtische Strukturen und entwickeln Sie zukunftsweisende Anpassungsstrategien.
             """)
    st.subheader("Zwei Szenarien - Eine aufschlussreiche Analyse:")
    st.write("""Wir zeigen Ihnen anhand der Stadt Konstanz, wie eine nachhaltige und klimagerechte Stadtentwicklung in der Lage sein kann, die stadtklimatischen Belange in der Stadtplanung zu berücksichtigen.
            Wir haben hierzu von Konstanz ein PALM4U Simulationsmodelle unter Berücksichtigung der realistische Stadtkonﬁguration erstellt und 2 Szenarien untersucht.
            """)
    st.write("""
            >> 1. **Ausgangslage: Ist-Zustand**
            >> 1. **Planungsvariante: Entsiegelung des Augustinerplatzes und Nachbegründung der Marktstätte**
            """)
    st.write("""Die folgenden Ergebnisse der feinskaligen PALM4U Stadtklimaanalyse vergleichen die Dynamik des Stadtklimas""")
    st.write("""
        >> * **Farbige Flächenrepräsentation:** Die intuitive Visualisierung ermöglicht es Ihnen, auf einen Blick die Unterschiede zwischen den Szenarien zu erfassen.
        >> * **Informativen Diagramme:** Die Diagramme ermöglichen eine qualitative, vergleichende Analyse der Dynamik des Mikroklimas, um Ihnen ein umfassendes Verständnis zu vermitteln.
        >> * **OpenStreet Map Integration:**: Nutzen Sie unsere interaktive OpenStreet Map, um die Mikroklima-2m-Lufttemperatur visuell über Konstanz zu erforschen. Die Kombination von Kartenmaterial und Echtzeitdaten ermöglicht es Ihnen, die Stadt aus einer neuen Perspektive zu betrachten.
        """)
    # https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

selected_menu = option_menu(
    menu_title = None, # or None to hide title
    options=["3D Map Integration", "OSM Single", "OSM Dual", "Farbkarte", "About"],
    # icons=["house", "book", "envelope"],
    # menu_icon=["cast"],
    default_index=2,
    orientation="horizontal",
    )

if selected_menu == "Farbkarte":
    with st.expander(label="Farbige Flächenrepräsentation", expanded=True):
        # Create columns for variable and plots
        columns_main = st.columns((2,4,4), gap="small")
        with columns_main[0]:
            # Fetch locations
            simulation_domain = "N03"
            location_list = ["Overall (Altstadt)", "Augstinerplatz", "Markstätte"] # "Sankt-Stephans-Platz"
            location = st.selectbox(label="Select a Location:", options=location_list, index=location_list.index(location_list[0]))
            
            # Fetch masked data from the selected variable
            variable_description = st.selectbox(label="Select a variable:", options=read_netcdf.variable_list()[1])
            variable_index = read_netcdf.variable_list()[1].index(variable_description)
            
            # Read variable name and variable unit from variable dictionary
            variable_name = read_netcdf.variable_list()[0][variable_index]
            variable_unit = read_netcdf.variable_list()[2][variable_index]

            # Read data from masked variable data based on variable name
            variable_data_1_masked, variable_data_2_masked, building_id_mask = read_netcdf.variable_data_masked(variable_name)[0:3]
            variable_data_masked_run_1_aoi_1, variable_data_masked_run_1_aoi_2= read_netcdf.variable_data_masked(variable_name)[3:5]
            variable_data_masked_run_2_aoi_1, variable_data_masked_run_2_aoi_2 = read_netcdf.variable_data_masked(variable_name)[5:7]
            data_run_1_stn_1, data_run_1_stn_2, data_run_1_stn_3, data_run_2_stn_1, data_run_2_stn_2, data_run_2_stn_3 = read_netcdf.variable_data_masked(variable_name)[7:13]
            
            # Select time of day and equivanlent band_index for plot
            time_index = st.select_slider(label="Select a time of the day:", options=time_sequence, value="15:00")
            band_index = band_sequence[time_sequence.index(time_index)]
            
            # Define Colormap for visualization
            colormap_options = plt.colormaps()
            colormap_options_list = ["turbo", "jet", "viridis", "plasma", "magma", "cividis"]
            cmap = st.selectbox(label="Select a Colormap:", options=colormap_options_list, index=colormap_options_list.index("turbo"))
            
            # Define mask color and limits of ColorBar of the plot
            columns = st.columns((1.25,1,1))
            with columns[0]:
                # Define mask color for visualization
                mask_color = st.color_picker(label="Mask Color", value="#474747")
            with columns[1]:
                min_value = min(np.nanmin(variable_data_1_masked), np.nanmin(variable_data_2_masked)) // 5 * 5
                vmin = st.number_input(label="Cbar Min", value=min_value)
            with columns[2]:
                max_value = max(np.nanmax(variable_data_1_masked), np.nanmax(variable_data_2_masked) + 5 - 1) // 5 * 5
                vmax = st.number_input(label="Cbar Max", value=max_value)
            
            columns = st.columns((1.25,2))
            with columns[0]:
                # Define shapefile color for visualization
                shapefile_color = st.color_picker(label="Shapefile Color", value="#FFFFFF")
            with columns[1]:
                # Read AOI shapefile and toggle plot display
                display_shapefile = st.checkbox(label="Shapefile", value=True)
                display_stations = st.checkbox(label="Stations", value=True)
                shapefile_url = r"./data/area_of_interest/aoi_sim.shp" if display_shapefile else None
                shapefile_url_2 = r"./data/area_of_interest/aoi_stations.shp" if display_stations else None
                display_hatch = st.checkbox(label="Hatch", value=True)
                hatch = "//" if display_hatch else ''
            
            cmap = "turob"
            

        # Plot color maps as per the variables
        with columns_main[1]:
            # Plot color map for base simulation
            display_matplots.colormesh(variable_description, variable_unit,
                                    variable_data_1_masked, location,
                                    building_id_mask,
                                    band_index, cmap, mask_color,
                                    vmin, vmax,
                                    shapefile_color, shapefile_url, hatch, shapefile_url_2)
            st.markdown(f'<p class="centered-text">Base Simulation</p>', unsafe_allow_html=True,)
        with columns_main[2]:
            # Plot color map for test simulation
            display_matplots.colormesh(variable_description, variable_unit,
                                    variable_data_2_masked, location,
                                    building_id_mask, 
                                    band_index, cmap, mask_color,
                                    vmin, vmax,
                                    shapefile_color, shapefile_url, hatch, shapefile_url_2)
            st.markdown(f'<p class="centered-text">Test Simulation</p>', unsafe_allow_html=True,)

    # Use expander and tabs to display graphs
    dataframe_run_1 = read_netcdf.compute_statistics_2d(variable_data_1_masked)
    dataframe_run_2 = read_netcdf.compute_statistics_2d(variable_data_2_masked)

    dataframe_run_1_aoi_1 = read_netcdf.compute_statistics_2d(variable_data_masked_run_1_aoi_1)
    dataframe_run_1_aoi_2 = read_netcdf.compute_statistics_2d(variable_data_masked_run_1_aoi_2)
    dataframe_run_2_aoi_1 = read_netcdf.compute_statistics_2d(variable_data_masked_run_2_aoi_1)
    dataframe_run_2_aoi_2 = read_netcdf.compute_statistics_2d(variable_data_masked_run_2_aoi_2)

    dataframe_run_1_stn_1 = read_netcdf.compute_statistics_2d(data_run_1_stn_1)
    dataframe_run_1_stn_2 = read_netcdf.compute_statistics_2d(data_run_1_stn_2)
    dataframe_run_1_stn_3 = read_netcdf.compute_statistics_2d(data_run_1_stn_3)

    dataframe_run_2_stn_1 = read_netcdf.compute_statistics_2d(data_run_2_stn_1)
    dataframe_run_2_stn_2 = read_netcdf.compute_statistics_2d(data_run_2_stn_2)
    dataframe_run_2_stn_3 = read_netcdf.compute_statistics_2d(data_run_2_stn_3)

    with st.expander("Graphical Representation", expanded=True):
        # Create columns for variable and plots
        columns_main = st.columns((2,8), gap="small")
        with columns_main[0]:
            # Fetch locations
            location_list = ["Overall (Altstadt)", "Augstinerplatz", "Markstätte", "Station 1", "Station 2", "Station 3"] # "Sankt-Stephans-Platz"
            location = st.selectbox(label="Select a Location: ", options=location_list, index=location_list.index(location_list[1]))
            
            # Select time of day and equivanlent band_index for plot
            time_index = st.select_slider(label="Select a time of the day (Histogram):", options=time_sequence, value="15:00")
            band_index = band_sequence[time_sequence.index(time_index)]
            
        with columns_main[1]:
            # Add tabs
            tabs = st.tabs(["Line Plot", "Bar Graph", "Histogram"])
            with tabs[0]:
                if location == "Overall (Altstadt)":
                    display_plotly.line_graph(dataframe_run_1, dataframe_run_2, band_sequence, time_sequence, band_index, variable_description, variable_unit)
                elif location == "Augstinerplatz":
                    display_plotly.line_graph(dataframe_run_1_aoi_1, dataframe_run_2_aoi_1, band_sequence, time_sequence, band_index, variable_description, variable_unit)
                elif location == "Markstätte":
                    display_plotly.line_graph(dataframe_run_1_aoi_2, dataframe_run_2_aoi_2, band_sequence_backup, time_sequence, band_index, variable_description, variable_unit)
                elif location == "Station 1":
                    display_plotly.line_graph(dataframe_run_1_stn_1, dataframe_run_2_stn_1, band_sequence, time_sequence, band_index, variable_description, variable_unit)
                elif location == "Station 2":
                    display_plotly.line_graph(dataframe_run_1_stn_2, dataframe_run_2_stn_2, band_sequence, time_sequence, band_index, variable_description, variable_unit)
                elif location == "Station 3":
                    display_plotly.line_graph(dataframe_run_1_stn_3, dataframe_run_2_stn_3, band_sequence_backup, time_sequence, band_index, variable_description, variable_unit)
            
            with tabs[1]:
                if location == "Overall (Altstadt)":
                    display_plotly.bar_graph(dataframe_run_1, dataframe_run_2, band_sequence, time_sequence, variable_description, variable_unit)
                elif location == "Augstinerplatz":
                    display_plotly.bar_graph(dataframe_run_1_aoi_1, dataframe_run_2_aoi_1, band_sequence, time_sequence, variable_description, variable_unit)
                elif location == "Markstätte":
                    display_plotly.bar_graph(dataframe_run_1_aoi_2, dataframe_run_2_aoi_2, band_sequence_backup, time_sequence, variable_description, variable_unit)
                elif location == "Station 1":
                    display_plotly.bar_graph(dataframe_run_1_stn_1, dataframe_run_2_stn_1, band_sequence, time_sequence, variable_description, variable_unit)
                elif location == "Station 2":
                    display_plotly.bar_graph(dataframe_run_1_stn_2, dataframe_run_2_stn_2, band_sequence, time_sequence, variable_description, variable_unit)
                elif location == "Station 3":
                    display_plotly.bar_graph(dataframe_run_1_stn_3, dataframe_run_2_stn_3, band_sequence_backup, time_sequence, variable_description, variable_unit)
                    
            with tabs[2]:
                # band_index = 90 if band_index == 89 else band_index
                if location == "Overall (Altstadt)":
                    display_plotly.histogram(variable_data_1_masked, variable_data_2_masked, band_index, time_index, variable_description, variable_unit)
                elif location == "Augstinerplatz":
                    display_plotly.histogram(variable_data_masked_run_1_aoi_1, variable_data_masked_run_2_aoi_1, band_index, time_index, variable_description, variable_unit)
                elif location == "Markstätte":
                    display_plotly.histogram(variable_data_masked_run_1_aoi_2, variable_data_masked_run_2_aoi_2, band_sequence_backup, time_index, variable_description, variable_unit)
                elif location == "Station 1":
                    display_plotly.histogram(data_run_1_stn_1, data_run_2_stn_1, band_index, time_index, variable_description, variable_unit)
                elif location == "Station 2":
                    display_plotly.histogram(data_run_1_stn_2, data_run_2_stn_2, band_index, time_index, variable_description, variable_unit)
                elif location == "Station 3":
                    display_plotly.histogram(data_run_1_stn_3, data_run_2_stn_3, band_sequence_backup, time_index, variable_description, variable_unit)

elif selected_menu == "OSM Single":
    with st.expander("2D Map Viewer", expanded=True): 
        # Create columns for variable and maps
        columns_main = st.columns((2,7,1), gap="small")
        with columns_main[0]:
            time_index = st.select_slider(label="Select a time of the day: ", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
            opacity = st.number_input(label="Overlay Opacity", min_value=0.0, max_value=1.0, value=0.9, step=0.1)

            # Option to select which domain to visualize
            options=["Large (Low Resolution)", "Medium (Medium Resolution)", "Small (High Resolution)"]
            domain = st.selectbox(label="Select the domain to visualize:", options=options, index=2)
            domain_index = options.index(domain) + 1

            # Read AOI shapefile and toggle plot display
            display_shapefile = st.checkbox(label="Domain Boundary", value=True)
            shapefile_url = r"./data/area_of_interest/aoi_sim.shp" if display_shapefile else None
            # Toggle marker display
            display_markers = st.checkbox(label="Location Markers ", value=True)
                
        with columns_main[1]:
            display_map.single_raster_overlay(time_index, opacity, display_shapefile, display_markers, domain_index)
        with columns_main[2]:
            # Add image as scale
            image_url = r"./images/scale.png"
            st.image(image_url, width = 85)

elif selected_menu == "OSM Dual":
    # center on Liberty Bell, add marker
    m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)

    # Add OSM layers with overlay set to True to make them selected by default
    folium.TileLayer("openstreetmap", overlay=True).add_to(m)
    folium.TileLayer("opentopomap", overlay=True).add_to(m)

    m.add_child(folium.LayerControl())

    folium.Marker(
        [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
    ).add_to(m)

    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725)

elif selected_menu == "3D Map Integration":
    with st.expander("3D Map Viewer", expanded=True):
        # Create columns for variable and maps
        columns_main = st.columns((2,8), gap="small")
        with columns_main[0]:
            # Select time of the day visualize the image overlay
            time_index_3d = st.select_slider(label="Select a time of the day:  ", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
            
            # Define opacity of overlayed image
            opacity_3d = st.number_input(label="Overlay Opacity", min_value=0.0, max_value=1.0, value=0.9, step=0.1)

            # Take user input for map settings    
            # columns = st.columns((1,1))
            # with columns[0]:
            #     lat = st.number_input("Latitude", value = 47.661129)
            # with columns[1]:
            #     lon = st.number_input("Longitude", value = 9.175209)
            
            # columns = st.columns((1,1,1))
            # with columns[0]:
            #     zoom = st.number_input("Zoom", value = 15.5)
            # with columns[1]:
            #     pitch = st.number_input("Pitch", value = 50)
            # with columns[2]:
            #     bearing = st.number_input("Bearing", value = -40)
            
            lat = 47.661129
            lon = 9.175209
            zoom = 15.5
            pitch = 50
            bearing = -40 
            
            # Toggle image overlay
            display_image = st.checkbox(label="Overlay", value=True)
            # Toggle added trees
            display_added_trees = st.checkbox(label="Test Simulation (Added Trees)", value=True)
            
        with columns_main[1]:
            display_map.pydeck_3d_geojson(time_index_3d, opacity_3d, display_image, display_added_trees, lat, lon, zoom, pitch, bearing)

end_time = time.time()
st.write(f"Time taken to load: {end_time - start_time} seconds")