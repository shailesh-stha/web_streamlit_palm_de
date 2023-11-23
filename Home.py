# standard library
import os
import time
# third-party library
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
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
    st.header(body="Urbane Hitzeinseln - Planungsvarianten zur Reduktion von Hitzestress", anchor=False)
    st.write("""Entdecken Sie die Möglichkeiten der hochaufgelösten, mikroskaligen Stadtklimasimulation mit der innovativen Software PALM4U!
             """)
    st.subheader(body="Zwei Szenarien - Eine aufschlussreiche Analyse:", anchor=False)
    st.write("""Wir demonstrieren am Beispiel von Konstanz, wie eine nachhaltige und klimagerechte Stadtentwicklung funktionieren kann.
             Dazu haben wir ein PALM-4U Simulationsmodell erstellt und die Auswirkung zweier realistische Klimaanpassungsmaßnahmen untersucht.""")

st.divider()

option_menu_styles = {
    "container": {
        "width": "100%",  # Set the width of the entire menu container
        "max-width": "initial",
        "background": "white",
        "border-radius": "0rem",
        # "border": "0.5px solid #DD0065",
    },
    "nav-link": {
        "width": "95%",
        "color": "black",
        # "background": "#d4d4d4",
        "font-size": "1.0rem",
        "border": "1px solid #DD0065",
        "border-radius": "1rem",
        # "font-family": "Franklin Gothic Demi",
    },
    "nav-link-selected": {
        "background-color": "#DD0065",
        "color": "white",
        "font-size": "1.1rem",
        "border-radius": "1rem",
        # "font-family": "Franklin Gothic Demi",
    },
}

selected_menu = option_menu(
    menu_title = None,
    options=["Szenarien", "3D Visualisierung", "OpenStreetMap", "Flächenrepräsentation", "Info"],
    icons=["house", "globe2", "map", "palette", "info-circle"],
    default_index=0,
    orientation="horizontal",
    styles= option_menu_styles,
    )

# Define initial session states
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if selected_menu == "Szenarien":
    with st.expander("Klimaanpassungsszenario", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            location = st.selectbox(label="Standort:", options=["Augustinerplatz", "Marktstätte"])
            if location == "Augustinerplatz":
                folder_path = r"./data/landing_page/Augustinerplatz/"
            elif location == "Marktstätte":
                folder_path = r"./data/landing_page/Marktstätte/"
        
        # Read images
        image_names = ["before.png", "after.png", "before_heatmap.png", "after_heatmap.png", "before_heatmap_with_text.png", "after_heatmap_with_text.png"]
        image_addresses = [os.path.join(folder_path, image_name) for image_name in image_names]
        
        # Display Images
        columns_main = st.columns((3,3))
        with columns_main[0]:
            st.markdown(f'<p class="centered-text">Ist-Zustand</p>', unsafe_allow_html=True,)
            st.image(image = image_addresses[0])
            st.image(image = image_addresses[2])
        with columns_main[1]:
            st.markdown(f'<p class="centered-text">Variante Nachbegrünung</p>', unsafe_allow_html=True,)
            st.image(image = image_addresses[1])
            st.image(image = image_addresses[3])

elif selected_menu == "Flächenrepräsentation":
    with st.expander(label="Farbige Flächenrepräsentation", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Fetch locations
            simulation_domain = "N03"
            location_list = ["Altstadt", "Augstinerplatz", "Markstätte"] # "Sankt-Stephans-Platz"
            location = st.selectbox(label="Standort:", options=location_list, index=location_list.index(location_list[0]))
        with columns_input[1]:
            # Fetch masked data from the selected variable
            variable_description = st.selectbox(label="Wahl der zu visualisierenden Variable:", options=read_netcdf.variable_list()[3])
            variable_index = read_netcdf.variable_list()[3].index(variable_description)
        with columns_input[2]:
            # Select time of day and equivanlent band_index for plot
            time_index = st.select_slider(label="Wähle die Tageszeit:", options=time_sequence, value="15:00")
            band_index = band_sequence[time_sequence.index(time_index)]
            
        # Read variable name and variable unit from variable dictionary
        variable_name = read_netcdf.variable_list()[0][variable_index]
        variable_unit = read_netcdf.variable_list()[2][variable_index]
        variable_description_de = read_netcdf.variable_list()[3][variable_index]

        # Read data from masked variable data based on variable name
        variable_data_1_masked, variable_data_2_masked, building_id_mask = read_netcdf.variable_data_masked(variable_name)[0:3]
        variable_data_masked_run_1_aoi_1, variable_data_masked_run_1_aoi_2= read_netcdf.variable_data_masked(variable_name)[3:5]
        variable_data_masked_run_2_aoi_1, variable_data_masked_run_2_aoi_2 = read_netcdf.variable_data_masked(variable_name)[5:7]
        data_run_1_stn_1, data_run_1_stn_2, data_run_1_stn_3, data_run_2_stn_1, data_run_2_stn_2, data_run_2_stn_3 = read_netcdf.variable_data_masked(variable_name)[7:13]

        # Assign Default Values
        cmap = "turbo"
        mask_color = "#474747"
        vmin = min(np.nanmin(variable_data_1_masked), np.nanmin(variable_data_2_masked)) // 2.5 * 2.5
        vmax = max(np.nanmax(variable_data_1_masked), np.nanmax(variable_data_2_masked) + 2.5 - 1) // 2.5 * 2.5
        shapefile_color = "#FFFFFF"
        shapefile_url = r"./data/area_of_interest/aoi_sim.shp"
        shapefile_url_2 = r"./data/area_of_interest/aoi_stations.shp" 
        hatch = "//" 

        columns_main = st.columns(2)
        # Plot color maps as per the variables
        with columns_main[0]:
            st.markdown(f'<p class="centered-text">Ist-Zustand</p>', unsafe_allow_html=True,)
            # Plot color map for base simulation
            display_matplots.colormesh(variable_description_de, variable_unit,
                                    variable_data_1_masked, location,
                                    building_id_mask, band_index, cmap, mask_color,
                                    vmin, vmax, shapefile_color, shapefile_url, hatch, shapefile_url_2)
        with columns_main[1]:
            st.markdown(f'<p class="centered-text">Variante Nachbegrünung</p>', unsafe_allow_html=True,)
            # Plot color map for test simulation
            display_matplots.colormesh(variable_description_de, variable_unit,
                                    variable_data_2_masked, location,
                                    building_id_mask, band_index, cmap, mask_color,
                                    vmin, vmax, shapefile_color, shapefile_url, hatch, shapefile_url_2)
    
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
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Fetch locations
            location_list = ["Altstadt", "Augstinerplatz", "Markstätte", "Räumlicher Knoten 1", "Räumlicher Knoten 2", "Räumlicher Knoten 3"]
            location = st.selectbox(label="Standort: ", options=location_list, index=location_list.index(location_list[1]))
        
        columns_main = st.columns(1)
        with columns_main[0]:
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

elif selected_menu == "3D Visualisierung":
    with st.expander("3D Map Viewer", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Select time of the day visualize the image overlay
            time_index_3d = st.select_slider(label="Wähle die Tageszeit:", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
        with columns_input[1]:
            st.markdown(f'<p class="title-text"><strong>Anzeigeoptionen:</strong></p>', unsafe_allow_html=True,)
            # Toggle image overlay
            display_image = st.checkbox(label="Lufttemperatur (2m)", value=True)
            # Toggle added trees
            display_added_trees = st.checkbox(label="Variante Nachbegrünung", value=True)
        
        # Assign Default Values
        opacity_3d = 0.75
        lat = 47.661129
        lon = 9.175209
        zoom = 15.5
        pitch = 50
        bearing = -40 
     
        # Display 3D Map
        columns_main = st.columns(1)
        with columns_main[0]:
            display_map.pydeck_3d_geojson(time_index_3d, opacity_3d, display_image, display_added_trees, lat, lon, zoom, pitch, bearing)

elif selected_menu == "OpenStreetMap":
    with st.expander("Vergleich Ist-Zustand Planungsvariante", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Select time of the day visualize the image overlay
            time_index = st.select_slider(label="Wähle die Tageszeit:", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
        with columns_input[1]:
            st.markdown(f'<p class="title-text"><strong>Anzeigeoptionen:</strong></p>', unsafe_allow_html=True,)
            # Toggle marker display
            display_markers = st.checkbox(label="Position Zielszenario", value=True)

        # Assign Default Values
        opacity_2d = 0.75
        display_shapefile = False
        
        # Columns for header
        columns_header = st.columns((3,3,0.5))
        with columns_header[0]:
            st.markdown(f'<p class="centered-text">Ist-Zustand</p>', unsafe_allow_html=True,)
        with columns_header[1]:
            st.markdown(f'<p class="centered-text">Variante Nachbegrünung</p>', unsafe_allow_html=True,)
        
        # Display dual Map
        columns_main = st.columns((6,0.5))
        # Display folium map with raster overlay
        with columns_main[0]:
            display_map.dual_raster_overlay(time_index, opacity_2d, display_shapefile, display_markers)
        # Add image as scale
        with columns_main[1]:
            image_url = r"./images/scale.png"
            st.image(image_url, width=70)

        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Option to select which domain to visualize
            options=["Gesamtes Stadtgebiet", "Innenstadtbereich", "Zielregion"]
            domain = st.selectbox(label="Wähle den Auswertungsbereich:", options=options, index=2)
            domain_index = options.index(domain) + 1
        # Display single Map
        columns_main = st.columns(1)
        with columns_main[0]:
            display_map.single_raster_overlay(time_index, opacity_2d, display_shapefile, display_markers, domain_index)
            if domain == "Gesamtes Stadtgebiet":
                st.markdown(f'<p class="note-text">Grade: Auswertungsbereich= 4096 x 4096 m², Auflösung=16m</p>', unsafe_allow_html=True,)
            elif domain == "Innenstadtbereich":
                st.markdown(f'<p class="note-text">Grade: Auswertungsbereich= 2048 x 2048 m², Auflösung=8m</p>', unsafe_allow_html=True,)
            elif domain == "Zielregion":
                st.markdown(f'<p class="note-text">Grade: Auswertungsbereich= 512 x 512 m², Auflösung=2m</p>', unsafe_allow_html=True,)

elif selected_menu == "Info":
    # Website Introduction
    with st.expander("Über das Projekt", expanded=True):
        st.header("Technologie:")
        st.write("""Die rasche Verstädterung und die städtischen Wärmeinseln (Urban Heat Islands, UHI) stellen neben der wachsenden Bedrohung durch den Klimawandel eine große Herausforderung für die städtische Nachhaltigkeit und die öffentliche Gesundheit dar.
                 Mikroklimamodellierung und -simulationen, die unter Verwendung verschiedener Szenarien durchgeführt werden, können zur Untersuchung von UHI, ihren Auswirkungen und anschließenden Anpassungsmaßnahmen verwendet werden.
                 Das PALM-System (Parallelized Large-eddy Simulation Model, https://palm.muk.uni-hannover.de), eine hochmoderne Mikroklima-Simulationssoftware, kann erfolgreich zur Simulation und Vorhersage des Mikroklimas in städtischen Gebieten und von UHIs eingesetzt werden.
                 In dieser Studie wird PALM-4U verwendet, um das Mikroklima in Konstanz, Deutschland zu simulieren.
                 Der Schwerpunkt liegt dabei auf der Untersuchung der Auswirkungen städtischer Infrastrukturen.
                """)
        st.write("""
                 Unsere Referenz: Projekt CoKLIMAx - Anwendung von COPERNICUS-Daten für klimaresiliente Stadtplanung. (https://maps.coklimax.net/portal/apps/sites/#/coklimax)
                 """)
        st.write("""
                 >> * Die Fallstudie deckt die Innenstadt von Konstanz (Süddeutschland) ab und zeigt die Möglichkeiten der Mikroklimasimulationsplattform Palm4U. 
                 >> * Die realistische Stadtkonﬁguration umfasst alle typischen Merkmale der städtischen Komplexität, die für eine physikalisch fundierte Stadtklimasimulation erforderlich sind: Unterschiedliche Gebäudehöhen und -grundrisse, Straßenkonﬁgurationen, Bäume und Freiflächen, reale Orografie-Höhen, die Merkmale der Oberflächenbedeckung, Versiegelung und Vegetation, Gewässer (Bodensee) und Bodeneigenschaften.
                 >> * Die Modelldaten werden aus verschiedenen digitalen und analogen Datenquellen wie dem Stadtmodell in LOD2-Qualität, Geoinformationen der Stadtverwaltung Konstanz und punktwolkenbasierten Informationen aus LiDAR-Daten generiert.
                 >> * Die Stadtklimasimulationen werden für statische (Klarhimmel-Approximation) und dynamische Klimabedingungen berechnet, wobei für letztere eine Anbindung an ein regionales numerisches Wettervorhersagemodell (COSMO-DE) des Deutschen Wetterdienstes (DWD) erfolgt.
                 >> * Berechnungsgebiete und Auflösung:
                 >>>> - Gesamtes Stadtgebiet: L=4096m, B=4096m, H=2048 m, Elementgröße: 16m, Auflösung: 256 x 256 x 128
                 >>>> - Innenstadtbereich: L=2048m, B=2048m, H=1024m, Elementgröße: 8m, Auflösung: 256 x 256 x 128
                 >>>> - Zielregion: L=512m, B=512m, H=256m, Elementgröße 2m, Auflösung: 256 x 256 x 128
                 >> * Berechnete Umweltdaten: Lufttemperatur (2m), Oberflächentemperatur, Wassertemperatur, Luftfeuchtigkeit, Windgeschwindigkeit, Nettostrahlung, Thermal Sensation Index
                 """)
        
    with st.expander("Über uns", expanded=True):
        st.header("Wir sind str.ucture…")
        st.write("""…ein Architektur- und Ingenieurbüro mit Sitz in Stuttgart.
                 Als Unternehmen setzen wir uns dafür ein, **eine nachhaltige und CO&#8322;-neutrale gebaute Umwelt zu schaffen**.
                 Unser Fokus liegt dabei auf einem Leichtbauansatz, der die **Minimierung des Materialverbrauchs** sowie den Einsatz von natürlichen und nachhaltigen Materialien in den Vordergrund stellt.
                 **Digitale Werkzeuge und vernetzte Planungstechnologien** helfen uns in interdisziplinären Teams innovative und nachhaltige Lösungen mit unseren Partnern zu entwickeln.
                 **Simulationstechniken** wie die **Strömungs- oder Stadtklimasimulation** ermöglichen uns die Auswirkungen von Gebäuden auf das Mikroklima in Städten zu verstehen und zu minimieren.
                 Dabei setzen wir auch auf **datenbasierte Planung** und Methoden der **künstlichen Intelligenz**.
                 Wir arbeiten in zahlreichen Kooperationen mit Unternehmen und Fachleuten sowie im Kontext von nationalen und internationalen Forschungsprogrammen daran, State-of-the-Art Entwicklungen in die Planungsprozesse einzubinden und weiterzuentwickeln.
                 Wir sind **Ihr Partner** für die **digitale Transformation im Bereich Stadtklima** und stehen Ihnen zur Seite, um städtische Resilienz zu stärken und Klimaanpassungsmaßnahmen effektiv zu gestalten. 
                 """)

        st.write("""**Unsere Leistungen im Überblick:**""")
        st.write("""
                 >> 1. **Digitales Stadtklima Modell (Palm4U):** Erstellung eines digitalen Stadtklima-Modells Ihrer Stadt basierend auf Ihren verfügbaren Daten.
                 >> 1. **Mikroklima-Simulationsdaten:** Bereitstellung von Simulationsdaten für das städtische Mikroklima zu ausgewählten Tages- und Nachtzeiten. Spezielle Auswertung dieser Daten an kritischen Zielgebieten unter Berücksichtigung von Bebauungsstrukturen, Umweltfaktoren und Mikroklimaparametern.
                 >> 1. **Digitale Datenverarbeitung:** Digitalisierung und Aufbereitung der Simulationsdaten in Form von benutzerfreundlichen Webanwendungen und Informationsseiten für Bürger.
                 >> 1. **Integration in GIS-Systeme:** Nahtlose Integration der Simulationsdaten in lokale GIS (Geoinformationssysteme) zur optimalen Nutzung und Verwaltung der Informationen.
                 >> 1. **Visualisierung von Lösungen:** Bereitstellung standortspezifischen Lösungen und Szenarioanalysen, um einfache Applikationen für Bürger zur Verfügung zu stellen und deren Informiertheit zu erhöhen.
                 >> 1. **Kosten-Nutzen-Bewertung:** Evidenzbasierte Bewertung von Resilienz- und Klimaschutzmaßnahmen, die als Werkzeug für eine fundierte Infrastrukturplanung, Überwachung und Berichterstattung in Entscheidungsprozessen dienen.
                 >> 1. **Wettervorhersagemodelle nutzen:** Einbindung globaler und lokaler Klimamodell und Dienste zur Verbesserung der Prognose, Überwachung und Berichterstattung von Klimaereignissen. 
                 """)
        
        st.markdown(f'<p class="custom-text"><strong>Ansprechpartner</strong></p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">Dr.-Ing. Sami Bidier</p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">📞 +49 (0)711 286 937-13</p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">✉️ bidier@str-ucture.com</p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">&#160</p>', unsafe_allow_html=True,)
        
footer_container = st.container()
with footer_container:
    columns_footer = st.columns(4)
    with columns_footer[0]:
        
        
        st.image(image=r"./data/images/structure_logo_RGB.png", width=250,)
        # st.markdown(f'<p class="footer-text"><strong>© str.ucture GmbH</strong></p>', unsafe_allow_html=True,)
        # st.markdown(f'<p class="footer-text">Lightweight Design. Made in Stuttgart.</p>', unsafe_allow_html=True,)
        # st.markdown(f'<p class="footer-text">Lindenspürstr. 32 </p>', unsafe_allow_html=True,)
        # st.markdown(f'<p class="footer-text">70176 Stuttgart</p>', unsafe_allow_html=True,)

end_time = time.time()
# st.write(f"Time taken to load: {end_time - start_time:.2f} seconds")