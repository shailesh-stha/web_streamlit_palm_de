# standard library
import os
import time
# third-party library
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit as st
import geopandas as gpd
from PIL import Image


# local imports
from utils import read_netcdf, display_map, display_matplots, display_plotly, display_images, useful_functions

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
        time_sequence = ['0:10', '1:00', '2:00', '3:00', '4:00', '5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '24:00']
        return band_sequence, band_sequence_backup, time_sequence
        
band_sequence, band_sequence_backup, time_sequence = band_time_sequence()

# Website Introduction
with st.container():
    st.header("Urbane Hitzeinseln - Planungsvarianten zur Reduktion von Hitzestress")
    st.write("""Entdecken Sie die Möglichkeiten der hochaufgelösten, mikroskaligen Stadtklimasimulation mit der innovativen Software PALM4U!
             """)
    st.subheader("Zwei Szenarien - Eine aufschlussreiche Analyse:")
    st.write("""Wir demonstrieren am Beispiel von Konstanz, wie eine nachhaltige und klimagerechte Stadtentwicklung funktionieren kann.
             Dazu haben wir ein PALM-4U Simulationsmodell erstellt und die Auswirkung zweier realistische Klimaanpassungsmaßnahmen untersucht.""")

st.divider()

option_menu_styles = {
    "container": {
        "width": "100%",  # Set the width of the entire menu container
        "color": "#DD0065",
        # "border": "1px solid grey",
    },
    "nav-link": {
        "color": "black",
        "padding": "1.5px",
        "font-size": "1.2rem",
        "font-family": "Times New Roman"
    },
    "nav-link-selected": {
        "background-color": "#DD0065",
        "color": "white",
        "font-size": "1.2rem",
        "font-family": "Times New Roman"
    },
}

selected_menu = option_menu(
    menu_title = None, # or None to hide title
    options=["Szenarien", "3D Visualisierung", "OpenStreetMap", "Flächenrepräsentation", "Info"],
    icons=["house", "globe2", "map", "palette", "info-circle" ],
    menu_icon=None,
    default_index=3,
    orientation="horizontal",
    styles= option_menu_styles,
    )

# Define initial session states
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if selected_menu == "Szenarien":
    with st.expander("Klimaanpassungsszenario", expanded=True):
        columns_header = st.columns((1.25,3,3))
        with columns_header[0]:
            st.markdown(f'<p class="centered-text">&#160</p>', unsafe_allow_html=True,)
        with columns_header[1]:
            st.markdown(f'<p class="centered-text">Ist-Zustand</p>', unsafe_allow_html=True,)
        with columns_header[2]:
            st.markdown(f'<p class="centered-text">Variante Nachbegrünung</p>', unsafe_allow_html=True,)
        
        # Read images for folder
        columns = st.columns((1.25,3,3))
        with columns[0]:
            location = st.selectbox(label="Standort:", options=["Augustinerplatz", "Marktstätte"])
            if location == "Augustinerplatz":
                folder_path = r"./data/landing_page/Augustinerplatz/"
            elif location == "Marktstätte":
                folder_path = r"./data/landing_page/Marktstätte/"
        image_names = ["before.png", "after.png", "before_heatmap.png", "after_heatmap.png", "before_heatmap_with_text.png", "after_heatmap_with_text.png"]
        image_addresses = [os.path.join(folder_path, image_name) for image_name in image_names]

        with columns[1]:
            st.image(image = image_addresses[0])
            st.image(image = image_addresses[2])
        with columns[2]:
            st.image(image = image_addresses[1])
            st.image(image = image_addresses[3])

elif selected_menu == "Flächenrepräsentation":
    with st.expander(label="Farbige Flächenrepräsentation", expanded=True):
        columns_header = st.columns((1.25,3,3))
        with columns_header[0]:
            st.markdown(f'<p class="centered-text">&#160</p>', unsafe_allow_html=True,)
        with columns_header[1]:
            st.markdown(f'<p class="centered-text">Ist-Zustand</p>', unsafe_allow_html=True,)
        with columns_header[2]:
            st.markdown(f'<p class="centered-text">Variante Nachbegrünung</p>', unsafe_allow_html=True,)
            
        # Create columns for variable and plots
        columns_main = st.columns((1.25,3,3), gap="small")
        with columns_main[0]:
            # Fetch locations
            simulation_domain = "N03"
            location_list = ["Altstadt", "Augstinerplatz", "Markstätte"] # "Sankt-Stephans-Platz"
            location = st.selectbox(label="Standort:", options=location_list, index=location_list.index(location_list[0]))
            
            # Fetch masked data from the selected variable
            variable_description = st.selectbox(label="Wahl der zu visualisierenden Variable:", options=read_netcdf.variable_list()[3])
            variable_index = read_netcdf.variable_list()[3].index(variable_description)
            
            # Read variable name and variable unit from variable dictionary
            variable_name = read_netcdf.variable_list()[0][variable_index]
            variable_unit = read_netcdf.variable_list()[2][variable_index]
            variable_description_de = read_netcdf.variable_list()[3][variable_index]

            # Read data from masked variable data based on variable name
            variable_data_1_masked, variable_data_2_masked, building_id_mask = read_netcdf.variable_data_masked(variable_name)[0:3]
            variable_data_masked_run_1_aoi_1, variable_data_masked_run_1_aoi_2= read_netcdf.variable_data_masked(variable_name)[3:5]
            variable_data_masked_run_2_aoi_1, variable_data_masked_run_2_aoi_2 = read_netcdf.variable_data_masked(variable_name)[5:7]
            data_run_1_stn_1, data_run_1_stn_2, data_run_1_stn_3, data_run_2_stn_1, data_run_2_stn_2, data_run_2_stn_3 = read_netcdf.variable_data_masked(variable_name)[7:13]
            
            # Select time of day and equivanlent band_index for plot
            time_index = st.select_slider(label="Wähle die Tageszeit:", options=time_sequence, value="15:00")
            band_index = band_sequence[time_sequence.index(time_index)]

            cmap = "turbo"
            mask_color = "#474747"
            vmin = min(np.nanmin(variable_data_1_masked), np.nanmin(variable_data_2_masked)) // 2.5 * 2.5
            vmax = max(np.nanmax(variable_data_1_masked), np.nanmax(variable_data_2_masked) + 2.5 - 1) // 2.5 * 2.5
            shapefile_color = "#FFFFFF"
            display_shapefile = True
            shapefile_url = r"./data/area_of_interest/aoi_sim.shp"
            display_stations = True
            shapefile_url_2 = r"./data/area_of_interest/aoi_stations.shp" 
            display_hatch = True
            hatch = "//" 

        # Plot color maps as per the variables
        with columns_main[1]:
            # Plot color map for base simulation
            display_matplots.colormesh(variable_description_de, variable_unit,
                                    variable_data_1_masked, location,
                                    building_id_mask,
                                    band_index, cmap, mask_color,
                                    vmin, vmax,
                                    shapefile_color, shapefile_url, hatch, shapefile_url_2)
        with columns_main[2]:
            # Plot color map for test simulation
            display_matplots.colormesh(variable_description_de, variable_unit,
                                    variable_data_2_masked, location,
                                    building_id_mask, 
                                    band_index, cmap, mask_color,
                                    vmin, vmax,
                                    shapefile_color, shapefile_url, hatch, shapefile_url_2)

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

    expander_name = f"Grafische Datenauswertung: {variable_description_de}"
    with st.expander(expander_name, expanded=True):
        # Create columns for variable and plots
        columns_main = st.columns((1.25,6))
        with columns_main[0]:
            # Fetch locations
            location_list = ["Altstadt", "Augstinerplatz", "Markstätte", "Räumlicher Knoten 1", "Räumlicher Knoten 2", "Räumlicher Knoten 3"]
            location = st.selectbox(label="Standort: ", options=location_list, index=location_list.index(location_list[1]))
            
        with columns_main[1]:
            if location == "Altstadt":
                display_plotly.bar_graph(dataframe_run_1, dataframe_run_2, band_sequence, time_sequence, variable_description_de, variable_unit)
            elif location == "Augstinerplatz":
                display_plotly.bar_graph(dataframe_run_1_aoi_1, dataframe_run_2_aoi_1, band_sequence, time_sequence, variable_description_de, variable_unit)
            elif location == "Markstätte":
                display_plotly.bar_graph(dataframe_run_1_aoi_2, dataframe_run_2_aoi_2, band_sequence_backup, time_sequence, variable_description_de, variable_unit)
            elif location == "Räumlicher Knoten 1":
                display_plotly.bar_graph(dataframe_run_1_stn_1, dataframe_run_2_stn_1, band_sequence, time_sequence, variable_description_de, variable_unit)
            elif location == "Räumlicher Knoten 2":
                display_plotly.bar_graph(dataframe_run_1_stn_2, dataframe_run_2_stn_2, band_sequence, time_sequence, variable_description_de, variable_unit)
            elif location == "Räumlicher Knoten 3":
                display_plotly.bar_graph(dataframe_run_1_stn_3, dataframe_run_2_stn_3, band_sequence_backup, time_sequence, variable_description_de, variable_unit)

elif selected_menu == "OpenStreetMap":
    with st.expander("Vergleich Ist-Zustand Planungsvariante", expanded=True):
        columns_header = st.columns((1.25,3,3))
        with columns_header[0]:
            st.markdown(f'<p class="centered-text">&#160</p>', unsafe_allow_html=True,)
        with columns_header[1]:
            st.markdown(f'<p class="centered-text">Ist-Zustand</p>', unsafe_allow_html=True,)
        with columns_header[2]:
            st.markdown(f'<p class="centered-text">Variante Nachbegrünung</p>', unsafe_allow_html=True,)
        
        # Create columns for variable and maps
        columns_main = st.columns((1.25,5.5,0.35), gap="small")
        with columns_main[0]:
            time_index = st.select_slider(label="Wähle die Tageszeit:", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
            
            # Option to select which domain to visualize
            options=["Gesamtes Stadtgebiet", "Innenstadtbereich", "Zielregion"]
            domain = st.selectbox(label="Wähle den Auswertungsbereich:", options=options, index=2)
            domain_index = options.index(domain) + 1

            # Toggle marker display
            display_markers = st.checkbox(label="Position Zielszenario", value=True)

            opacity_2d = 0.75
            display_shapefile = False
                                     
        # Display folium map with raster overlay
        with columns_main[1]:
            display_map.dual_raster_overlay(time_index, opacity_2d, display_shapefile, display_markers, domain_index)
            
            display_map.single_raster_overlay(time_index, opacity_2d, display_shapefile, display_markers, domain_index)
            if domain == "Gesamtes Stadtgebiet":
                st.markdown(f'<p class="note-text">Grade: Auswertungsbereich= 4096 x 4096 m², Auflösung=16m</p>', unsafe_allow_html=True,)
            elif domain == "Innenstadtbereich":
                st.markdown(f'<p class="note-text">Grade: Auswertungsbereich= 2048 x 2048 m², Auflösung=8m</p>', unsafe_allow_html=True,)
            elif domain == "Zielregion":
                st.markdown(f'<p class="note-text">Grade: Auswertungsbereich= 512 x 512 m², Auflösung=2m</p>', unsafe_allow_html=True,)
            
            
        # Display scale as image format
        with columns_main[2]:
            # Add image as scale
            image_url = r"./images/scale.png"
            st.image(image_url, use_column_width=True)


elif selected_menu == "3D Visualisierung":
    with st.expander("3D Map Viewer", expanded=True):
        # Create columns for variable and maps
        columns_main = st.columns((1.25,6))
        with columns_main[0]:
            # Select time of the day visualize the image overlay
            time_index_3d = st.select_slider(label="Wähle die Tageszeit:", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")

            opacity_3d = 0.75
            lat = 47.661129
            lon = 9.175209
            zoom = 15.5
            pitch = 50
            bearing = -40 
            
            # Toggle image overlay
            display_image = st.checkbox(label="Flächenrepräsentation", value=True)
            # Toggle added trees
            display_added_trees = st.checkbox(label="Variante Nachbegrünung", value=True)
            
        with columns_main[1]:
            display_map.pydeck_3d_geojson(time_index_3d, opacity_3d, display_image, display_added_trees, lat, lon, zoom, pitch, bearing)

elif selected_menu == "Info":
    # Website Introduction
    with st.expander("About the Project", expanded=True):
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


# --------BACKUP PAGES------------ #
# elif selected_menu == "OSM new":
#     with st.expander("Map Viewer", expanded=True): 
#         # Create columns for variable and maps
#         columns_main = st.columns((2,3.5,3.5,1), gap="small")
#         with columns_main[0]:
#             time_index = st.select_slider(label="Select a time of the day: ", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
#             opacity = st.number_input(label="Overlay Opacity", min_value=0.0, max_value=1.0, value=0.9, step=0.1)

#             # Option to select which domain to visualize
#             options=["Large (Low Resolution)", "Medium (Medium Resolution)", "Small (High Resolution)"]
#             domain = st.selectbox(label="Select the domain to visualize:", options=options, index=2)
#             domain_index = options.index(domain) + 1

#             # Read AOI shapefile and toggle plot display
#             display_shapefile = st.checkbox(label="Domain Boundary", value=True)
#             shapefile_url = r"./data/area_of_interest/aoi_sim.shp" if display_shapefile else None
#             # Toggle marker display
#             display_markers = st.checkbox(label="Location Markers ", value=True)
              
#         with columns_main[1]:
#             simulation_run = "base"
#             display_map.single_raster_overlay(time_index, opacity, display_shapefile, display_markers, domain_index)
        
#         with columns_main[2]:
#             simulation_run = "test"
#             display_map.single_raster_overlay(time_index, opacity, display_shapefile, display_markers, domain_index)

#         # Display scale as image format
#         with columns_main[3]:
#             # Add image as scale
#             image_url = r"./images/scale.png"
#             st.image(image_url, width = 85)

# elif selected_menu == "Image folders":
#     def get_file_name_without_extension(file_path):
#         return os.path.splitext(os.path.basename(file_path))[0]
    
#     def show_next():
#         # Increments the counter to get the next images (Aug: len=5)
#         if st.session_state.counter < len(paths_images)-1:
#             st.session_state.counter += 1
#         else:
#             st.session_state.counter = len(paths_images)-1
#     def show_previous():
#         if st.session_state.counter > 0:
#             st.session_state.counter -= 1
#         else:
#             st.session_state.counter = 0
    
#     # Initialize Streamlit columns
#     columns_main = st.columns((1,4))
    
#     with columns_main[0]:
#         location = st.selectbox(label="Location", options=["Augustinerplatz", "Marktstätte"])
        
#         if location == "Augustinerplatz":
#             folder_path = r"./data/image_reimagined/AugustinerPlatz/"
#         elif location == "Marktstätte":
#             folder_path = r"./data/image_reimagined/Marktstätte/"
            
#         # Get list of images in folder
#         file_names = os.listdir(folder_path)
#         paths_images = []
#         for file_name in file_names:
#             full_path = os.path.join(folder_path, file_name)
#             paths_images.append(full_path)
            
#         # st.write(f"Image Index: {st.session_state.counter}")
        
#         # Define columns for buttons
#         columns = st.columns((1,1))
#         columns[0].button("Prevous", on_click=show_previous)
#         columns[1].button("Next", on_click=show_next)
#         # Show current image   
#     with columns_main[1]:
#         st.image(image=paths_images[st.session_state.counter], use_column_width="always")

end_time = time.time()
st.write(f"Time taken to load: {end_time - start_time:.2f} seconds")