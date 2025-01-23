# standard library
import os
import time
# third-party library
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import base64

# local imports
from utils import read_netcdf, display_map, display_matplots, display_plotly, useful_functions

# Start clock to test out site load time
start_time = time.time()

# Define Page layout
st.set_page_config(page_title="Mikroklima-Visualisierung",
                   layout="centered",
                   initial_sidebar_state="collapsed") #collapsed/expanded


# Inside the container, add the title and content
with st.container():
    columns_main = st.columns((3,3,1))
    with columns_main[2]:
        selected_language = st.selectbox(label="Language", options=["DE", "EN"], label_visibility="hidden")  #🌐
    st.markdown("<div class='fixed-header'/>", unsafe_allow_html=True)

         
def load_language_bundle(locale):
    df = pd.read_csv(r"./i18n/text_bundle.csv")
    df = df.query(f"locale == '{locale}'")

    lang_dict = {df.key.to_list()[i]:df.value.to_list()[i] for i in range(len(df.key.to_list()))}
    return lang_dict

lang_dict = load_language_bundle(selected_language)

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
    st.header(body=f"{lang_dict['website_intro_header']}", anchor=False)
    st.subheader(body=f"{lang_dict['website_intro_subheader']}", anchor=False)
    st.write(f"{lang_dict['website_intro_subheader_details']}")
             
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
    options=[f"{lang_dict['option_menu_0']}", f"{lang_dict['option_menu_1']}", f"{lang_dict['option_menu_2']}", f"{lang_dict['option_menu_3']}", f"{lang_dict['option_menu_4']}"],
    icons=["house", "globe2", "map", "palette", "info-circle"],
    default_index=0,
    orientation="horizontal",
    styles= option_menu_styles,
    )

# Scenerio 0
if selected_menu == f"{lang_dict['option_menu_0']}":
    with st.expander(f"{lang_dict['menu_0_title']}", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            location = st.selectbox(label=f"{lang_dict['location']}", options=["Augustinerplatz", "Marktstätte"])
            if location == "Augustinerplatz":
                folder_path = r"./data/landing_page/Augustinerplatz/"
            elif location == "Marktstätte":
                folder_path = r"./data/landing_page/Marktstätte/"
        
        # Read images
        image_names = ["before.png", "after.png", f"before_heatmap_{selected_language}.png", f"after_heatmap_{selected_language}.png"]
        image_addresses = [os.path.join(folder_path, image_name) for image_name in image_names]
        
        # Display Images
        columns_main = st.columns((3,3))
        with columns_main[0]:
            st.markdown(f"<p class='centered-text'>{lang_dict['current_state']}</p>", unsafe_allow_html=True,)
            st.image(image = image_addresses[0])
            st.image(image = image_addresses[2])
        with columns_main[1]:
            st.markdown(f"<p class='centered-text'>{lang_dict['after_change']}</p>", unsafe_allow_html=True,)
            st.image(image = image_addresses[1])
            st.image(image = image_addresses[3])

# 3D Visualization 1
elif selected_menu == f"{lang_dict['option_menu_1']}":
    with st.expander("3D Map Viewer", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Select time of the day visualize the image overlay
            time_index_3d = st.select_slider(label= f"{lang_dict['time_of_day']}", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
        with columns_input[1]:
            st.markdown(f"<p class='title-text'><strong>{lang_dict['layer_options']}</strong></p>", unsafe_allow_html=True,)
            # Toggle image overlay
            display_image = st.checkbox(label=f"{lang_dict['var_air_temp']}", value=True)
            # Toggle added trees
            display_added_trees = st.checkbox(label=f"{lang_dict['after_change']}", value=True)
        
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

# OSM 2
elif selected_menu == f"{lang_dict['option_menu_2']}":
    with st.expander(f"{lang_dict['menu_2_title']}", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Select time of the day visualize the image overlay
            time_index = st.select_slider(label=f"{lang_dict['time_of_day']}", options=["09:00", "12:00", "15:00", "18:00", "21:00"], value="12:00")
        with columns_input[1]:
            st.markdown(f"<p class='title-text'><strong>{lang_dict['layer_options']}</strong></p>", unsafe_allow_html=True,)
            # Toggle marker display
            display_markers = st.checkbox(label=f"{lang_dict['scenario_positions']}", value=True)

        # Assign Default Values
        opacity_2d = 0.75
        display_shapefile = False
        
        # Columns for header
        columns_header = st.columns((3,3,0.5))
        with columns_header[0]:
            st.markdown(f"<p class='centered-text'>{lang_dict['current_state']}</p>", unsafe_allow_html=True,)
        with columns_header[1]:
            st.markdown(f"<p class='centered-text'>{lang_dict['after_change']}</p>", unsafe_allow_html=True,)
        
        # Display dual Map
        columns_main = st.columns(1)
        # Display folium map with raster overlay
        with columns_main[0]:
            display_map.dual_raster_overlay(time_index, opacity_2d, display_shapefile, display_markers)
        # # Add image as scale
        columns_legend = st.columns((2,4,0.5))
        with columns_legend[0]:
            image_url = r"./images/scale_hz.png"
            st.image(image_url, use_column_width='auto', width=120)

        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Option to select which domain to visualize
            options=[f"{lang_dict['area_parent']}", f"{lang_dict['area_child1']}", f"{lang_dict['area_child2']}"]
            domain = st.selectbox(label=f"{lang_dict['analysis_area']}", options=options, index=2)
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

# Color Map 3
elif selected_menu == f"{lang_dict['option_menu_3']}":
    with st.expander(label=f"{lang_dict['menu_3_title']}", expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Fetch locations
            simulation_domain = "N03"
            location_list = ["Altstadt", "Augstinerplatz", "Markstätte"]
            location = st.selectbox(label=f"{lang_dict['location']}", options=location_list, index=location_list.index(location_list[1]))
        with columns_input[1]:
            if selected_language == "DE":
                # Fetch masked data from the selected variable
                variable_description = st.selectbox(label=f"{lang_dict['displayed_variable']}", options=read_netcdf.variable_list()[3])
                variable_index = read_netcdf.variable_list()[3].index(variable_description)
            elif selected_language == "EN":
                variable_description = st.selectbox(label=f"{lang_dict['displayed_variable']}", options=read_netcdf.variable_list()[1])
                variable_index = read_netcdf.variable_list()[1].index(variable_description)
        with columns_input[2]:
            # Select time of day and equivanlent band_index for plot
            time_index = st.select_slider(label=f"{lang_dict['time_of_day']}", options=time_sequence, value="15:00")
            band_index = band_sequence[time_sequence.index(time_index)]
            
        # Read variable name and variable unit from variable dictionary
        variable_name = read_netcdf.variable_list()[0][variable_index]
        variable_unit = read_netcdf.variable_list()[2][variable_index]
        
        if selected_language == "DE":
            variable_description_selected = read_netcdf.variable_list()[3][variable_index]
        elif selected_language == "EN":
            variable_description_selected = read_netcdf.variable_list()[1][variable_index]

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
            st.markdown(f"<p class='centered-text'>{lang_dict['current_state']}</p>", unsafe_allow_html=True,)
            # Plot color map for base simulation
            display_matplots.colormesh(variable_description_selected, variable_unit,
                                    variable_data_1_masked, location,
                                    building_id_mask, band_index, cmap, mask_color,
                                    vmin, vmax, shapefile_color, shapefile_url, hatch, shapefile_url_2)
        with columns_main[1]:
            st.markdown(f"<p class='centered-text'>{lang_dict['after_change']}</p>", unsafe_allow_html=True,)
            # Plot color map for test simulation
            display_matplots.colormesh(variable_description_selected, variable_unit,
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

    expander_name = f"{lang_dict['menu_3_title_2']}: {variable_description_selected}"
    with st.expander(expander_name, expanded=True):
        # User Input
        columns_input = st.columns(4)
        with columns_input[0]:
            # Fetch locations
            location_list = ["Altstadt", "Augstinerplatz", "Markstätte", "Position 1", "Position 2", "Position 3"]
            location = st.selectbox(label=f"{lang_dict['location']}", options=location_list, index=location_list.index(location_list[1]))
        
        columns_main = st.columns(1)
        with columns_main[0]:
            if location == "Altstadt":
                display_plotly.bar_graph(dataframe_run_1, dataframe_run_2, band_sequence, time_sequence, variable_description_selected, variable_unit, lang_dict)
            elif location == "Augstinerplatz":
                display_plotly.bar_graph(dataframe_run_1_aoi_1, dataframe_run_2_aoi_1, band_sequence, time_sequence, variable_description_selected, variable_unit, lang_dict)
            elif location == "Markstätte":
                display_plotly.bar_graph(dataframe_run_1_aoi_2, dataframe_run_2_aoi_2, band_sequence_backup, time_sequence, variable_description_selected, variable_unit, lang_dict)
            elif location == "Position 1":
                display_plotly.bar_graph(dataframe_run_1_stn_1, dataframe_run_2_stn_1, band_sequence, time_sequence, variable_description_selected, variable_unit, lang_dict)
            elif location == "Position 2":
                display_plotly.bar_graph(dataframe_run_1_stn_2, dataframe_run_2_stn_2, band_sequence, time_sequence, variable_description_selected, variable_unit, lang_dict)
            elif location == "Position 3":
                display_plotly.bar_graph(dataframe_run_1_stn_3, dataframe_run_2_stn_3, band_sequence_backup, time_sequence, variable_description_selected, variable_unit, lang_dict)

# Info 4
elif selected_menu == f"{lang_dict['option_menu_4']}":
    # Website Introduction
    with st.expander(f"{lang_dict['menu_4_title']}", expanded=True):
        st.header(f"{lang_dict['about_title_1']}")
        st.write(f"{lang_dict['about_project_content']}")
        st.write(f"{lang_dict['about_project_sections']}")
        
    with st.expander(f"{lang_dict['about_title_2']}", expanded=True):
        st.header(f"{lang_dict['about_us_title']}")
        st.write(f"{lang_dict['about_us_content']}")

        st.write(f"{lang_dict['about_us_header']}")
        st.write(f"{lang_dict['about_us_sections']}")
        
        st.markdown(f"<p class='custom-text'><strong>{lang_dict['contact_person']}</strong></p>", unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">Dr.-Ing. Sami Bidier</p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">📞 <a href="tel:+4971128693713">+49 (0)711 286 937-13</a></p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">✉️ <a href="mailto:bidier@str-ucture.com">bidier@str-ucture.com</a></p>', unsafe_allow_html=True,)
        st.markdown(f'<p class="custom-text">&#160</p>', unsafe_allow_html=True,)
        
footer_container = st.container()
with footer_container:
    columns_footer = st.columns(4)
    with columns_footer[0]:
        st.image(image=r"./data/images/structure_logo_RGB.png", width=250)
        url = "https://www.str-ucture.com/projekte/coklimax"
        st.write("[str.ucture GmbH](%s)" % url)
        
        # # Path to your GIF file
        # gif_path = r"F:\Simulation_Comparison\wind.gif"
        # with open(gif_path, "rb") as gif_file:
        #     gif_url = base64.b64encode(gif_file.read()).decode("utf-8")
        # st.markdown(f'<img src="data:image/gif;base64,{gif_url}" alt="Test GIF">', unsafe_allow_html=True,)

        # st.markdown(f'<p class="footer-text"><strong>© str.ucture GmbH</strong></p>', unsafe_allow_html=True,)
        # st.markdown(f'<p class="footer-text">Lightweight Design. Made in Stuttgart.</p>', unsafe_allow_html=True,)
        # st.markdown(f'<p class="footer-text">Lindenspürstr. 32 </p>', unsafe_allow_html=True,)
        # st.markdown(f'<p class="footer-text">70176 Stuttgart</p>', unsafe_allow_html=True,)

end_time = time.time()
# st.write(f"Time taken to load: {end_time - start_time:.2f} seconds")
