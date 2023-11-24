# Third-party library imports
import folium
from folium import plugins
import geopandas as gpd
from folium.raster_layers import ImageOverlay
import pydeck as pdk
from shapely.geometry import Polygon
import streamlit as st
from streamlit_folium import st_folium

# read and display AOI shapefile
shapefile_child = r"./data/area_of_interest/aoi_512x512.shp"
shapefile_aoi_sim = r"./data/area_of_interest/aoi_sim.shp"
shapefile_buildings = r"./data/shapefiles/buildings.shp"
gdf_child = gpd.read_file(shapefile_child)
gdf_aoi_sim = gpd.read_file(shapefile_aoi_sim)
gdf_buildings = gpd.read_file(shapefile_buildings)

def single_raster_overlay(time_index, opacity, display_shapefile, display_markers, domain_index):
    # Create a Folium map
    latlong = [47.661129, 9.175209]
    
    if domain_index == 1:
        zoom_start = 13
    elif domain_index == 2:
        zoom_start = 14
    elif domain_index == 3:
        zoom_start = 16

    # Add custom basemap to folium
    basemaps = {
    'Google Maps': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Maps', control = True),
    'Google Satellite': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Satellite', control = True),
    'Google Terrain': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Terrain', control = True),
    'Google Satellite Hybrid': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Satellite', control = True),
    'Esri Satellite': folium.TileLayer(tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr = 'Esri', name = 'Esri Satellite', control = True)
    }
    
    m = folium.Map(location=latlong, tiles=basemaps['Google Satellite'], zoom_start=zoom_start, max_zoom=20, scrollWheelZoom=False)
    basemaps['Google Maps'].add_to(m)
    
    # add minimap and mouse position
    plugins.MiniMap(position='bottomleft', height=125, width=125, toggle_display=True).add_to(m)
    plugins.MousePosition(position='bottomright', empty_string=[47.661129, 9.175209]).add_to(m)
    
    # # Insert shapefiles
    # if display_shapefile:
    #     folium.GeoJson(gdf_buildings, name="Gebäude", show=False,
    #                 style_function=lambda feature:{'color': 'white', 'fillColor': 'white', 'fillOpacity': 0.5, 'weight': 2,}
    #                 ).add_to(m)
    #     folium.GeoJson(gdf_child, name="Interessenbereich", show=False,
    #                 style_function=lambda feature:{'color': 'red', 'fillOpacity': 0.0}
    #                 ).add_to(m)
    #     folium.GeoJson(gdf_aoi_sim, name="Area of Interest for Simulation", show=False, 
    #                 style_function=lambda feature:{'color': 'blue', 'fillColor': 'green', 'fillOpacity': 0, 'weight': 2,}
    #                 ).add_to(m)

    # Define image bounds (Next update: Import from shapefile)
    bounds_N01 = [[47.6448635964296443, 9.1511199720516103], [47.6818029139078376, 9.2058007936034869]]
    bounds_N02 = [[47.6519467198030569, 9.1615802814169225], [47.6704156271541351, 9.1889184400719444]]
    bounds_N03 = [[47.6588733206033766, 9.1718298413872255], [47.6634905475628230, 9.1786643808656230]]
    # Overlay saved image
    image_index = time_index.replace(":","")

    if domain_index==1:
        ImageOverlay(name=f"Flächenrepräsentation at {time_index}", image=f"./images/base_simulation/N01/base_{image_index}.png",
                     bounds=bounds_N01, opacity=opacity).add_to(m)
    elif domain_index==2:
        ImageOverlay(name=f"Flächenrepräsentation at {time_index}", image=f"./images/base_simulation/N02/base_{image_index}.png",
                     bounds=bounds_N02, opacity=opacity).add_to(m)
    elif domain_index==3:
        ImageOverlay(name=f"Flächenrepräsentation at {time_index}", image=f"./images/base_simulation/N03/base_{image_index}.png",
                     bounds=bounds_N03, opacity=opacity).add_to(m)

    if display_markers:
        folium.Marker(location=[47.659553,9.173430],popup= "Augstinerplatz")
        folium.Marker(location=[47.660351,9.175822],popup="Markstätte")
        # folium.Marker(location=[47.661975,9.173732],popup="Sankt-Stephans-Platz")
    
    folium.plugins.Fullscreen(
        position="topleft", 
        title="Fullscreen",
        title_cancel="Exit Fullscreen",
        force_separate_button=True,
        ).add_to(m)
    
    # Add a layer control to the map
    folium.LayerControl().add_to(m)
    folium.plugins.ScrollZoomToggler().add_to(m)
    
    # Use streamlit_folium to display the map
    st_folium(m, width='100%', height=500)
    
def dual_raster_overlay(time_index, opacity_2d, display_shapefile, display_markers):
    # Create a Folium map
    latlong = [47.660029, 9.17480]
    zoom_start = 18
        
    # Add custom basemap to folium
    basemaps = {
    'Google Maps': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Maps', control = True),
    'Google Satellite': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Satellite', control = True),
    'Google Terrain': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Terrain', control = True),
    'Google Satellite Hybrid': folium.TileLayer(tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr = 'Google', name = 'Google Satellite', control = True),
    'Esri Satellite': folium.TileLayer(tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr = 'Esri', name = 'Esri Satellite', control = True)
    }

    m = folium.plugins.DualMap(location=latlong, zoom_start=zoom_start, max_zoom=20, scrollWheelZoom=False, layout='horizontal')
    basemaps['Google Satellite'].add_to(m)
    
    # add minimap and mouse position
    plugins.MiniMap(position='bottomleft', height=125, width=125, toggle_display=True, minimized=True).add_to(m.m1)
    plugins.MousePosition(position='bottomright', empty_string=[47.661129, 9.175209]).add_to(m)
    
    # Insert features (shapefiles using FeatureGroup)
    fg_1 = folium.FeatureGroup(name="markers_1").add_to(m.m1)
    fg_2 = folium.FeatureGroup(name="markers_2").add_to(m.m2)
    if display_shapefile:
        folium.GeoJson(gdf_child, name="Area of Interest", show=True,
                       style_function=lambda feature: {'color': 'red', 'fillOpacity': 0.0}).add_to(fg_1)
        folium.GeoJson(gdf_child, name="Area of Interest", show=True,
                       style_function=lambda feature: {'color': 'green', 'fillOpacity': 0.0}).add_to(fg_2)

    # Define image bounds (Next update: Import from shapefile)
    bounds_N01 = [[47.6448635964296443, 9.1511199720516103], [47.6818029139078376, 9.2058007936034869]]
    bounds_N02 = [[47.6519467198030569, 9.1615802814169225], [47.6704156271541351, 9.1889184400719444]]
    bounds_N03 = [[47.6588733206033766, 9.1718298413872255], [47.6634905475628230, 9.1786643808656230]]
    # Overlay saved image
    image_index = time_index.replace(":","")
    ImageOverlay(name=f"Color Map: {time_index} (Base Simulation N03)", image=f"./images/base_simulation/N03/base_{image_index}.png",
                    bounds=bounds_N03, opacity=opacity_2d).add_to(m.m1)
    ImageOverlay(name=f"Color Map: {time_index} (Test Simulation N03)", image=f"./images/test_simulation/N03/test_{image_index}.png",
                    bounds=bounds_N03, opacity=opacity_2d).add_to(m.m2)

    custom_icon = folium.Icon(
        icon='star',
        prefix='fa',
        icon_color='yellow',
        icon_size=(30, 30)  # Adjust the size to 30x30 pixels
        )

    # Insert Location Markers to map
    if display_markers:
        folium.Marker(location=[47.659553,9.173430],popup= "Augstinerplatz").add_to(m)
        folium.Marker(location=[47.660351,9.175822],popup="Markstätte").add_to(m)
        # folium.Marker(location=[47.661975,9.173732],popup="Sankt-Stephans-Platz").add_to(m)
    
        folium.Marker(location=[47.6594934, 9.1732702],popup= "Position 1", icon=folium.Icon(color='green', icon='map-pin', prefix='fa',)).add_to(m)
        folium.Marker(location=[47.6603006, 9.1750043],popup= "Position 2", icon=folium.Icon(color='green', icon='map-pin', prefix='fa',)).add_to(m)
        folium.Marker(location=[47.6603883, 9.1764696],popup= "Position 3", icon=folium.Icon(color='green', icon='map-pin', prefix='fa',)).add_to(m)

    # Display folium map
    st_folium(m, width='100%', height=450)

def pydeck_3d_shapefile(time_index_3d, opacity_3d, display_image, display_added_trees, lat, lon, zoom, pitch, bearing):
    latlong = [47.661129, 9.175209]
    # image layer
    image_index = time_index_3d.replace(":","")
    image_path = f"./images/base_simulation/N03/base_{image_index}.png"
    image_bounds = [[9.1718298413872255, 47.6588733206033766],  # Southwest corner
                    [9.1718298413872255, 47.663490547562823],  # Northwest corner
                    [9.1786643808656230, 47.663490547562823],  # Northeast corner
                    [9.1786643808656230, 47.6588733206033766]   # Southeast corner
                    ]
    image_layer = pdk.Layer("BitmapLayer",
                            image=image_path,
                            bounds=image_bounds,
                            opacity=opacity_3d)
    if display_image is False:
        image_layer = None
    
    # building shapefile layer
    building_shapefile_path = r"F:\Simulation_Comparison\web_streamlit_palm\data\shapefiles\buildings.shp"
    gdf = gpd.read_file(building_shapefile_path)
    gdf = gdf.to_crs(epsg=4326)
    building_layer = pdk.Layer("PolygonLayer",
                            data=gdf,
                            get_polygon="geometry.coordinates",
                            get_fill_color=[250, 250, 250],  # Specify the fill color
                            get_line_color=[50, 50, 50],  # Specify the line color
                            get_line_width=0.5,  # Specify the line width
                            get_elevation='B_hoeh',  # Map the "B_hoeh" column to elevation
                            wireframe=True,
                            extruded=True,
                            pickable=False,)
    
    # tree shapefile layer (for trunk and crown)
    trees_base_crown_path = r"F:\Simulation_Comparison\web_streamlit_palm\data\shapefiles\trees_base_crown.shp"
    trees_base_trunk_path = r"F:\Simulation_Comparison\web_streamlit_palm\data\shapefiles\trees_base_trunk.shp"
    gdf = gpd.read_file(trees_base_crown_path)
    gdf = gdf.to_crs(epsg=4326)
    def update_z(row):
        t_heig = row['T_heig'] * 0.6
        geometry = row['geometry']
        updated_coordinates = [(x, y, t_heig) for x, y in geometry.exterior.coords]
        return Polygon(updated_coordinates)
    # Apply the function to create a new column "geometry_z"
    gdf['geometry'] = gdf.apply(update_z, axis=1)
    tree_base_crown = pdk.Layer("PolygonLayer",
                            data=gdf,
                            get_polygon="geometry.coordinates",
                            get_fill_color=[75, 200, 75],
                            get_line_color=[50, 50, 50],
                            get_line_width=0.5,
                            get_elevation='T_heig',
                            wireframe=True,
                            extruded=True,
                            opacity=0.5,
                            pickable=False,)
    gdf = gpd.read_file(trees_base_trunk_path)
    gdf = gdf.to_crs(epsg=4326)
    tree_base_trunk = pdk.Layer("PolygonLayer",
                                data=gdf,
                                get_polygon="geometry.coordinates",
                                get_fill_color=[150, 75, 0],
                                get_line_color=[50, 50, 50],
                                get_line_width=0.5,
                                get_elevation='T_heig * 0.6',
                                wireframe=True,
                                extruded=True,
                                opacity=0.5,
                                pickable=False,)
    
    # tree shapefile layer (for trunk and crown)
    trees_base_crown_path = r"F:\Simulation_Comparison\web_streamlit_palm\data\shapefiles\added_trees_crown.shp"
    trees_base_trunk_path = r"F:\Simulation_Comparison\web_streamlit_palm\data\shapefiles\added_trees_trunk.shp"
    gdf = gpd.read_file(trees_base_crown_path)
    gdf = gdf.to_crs(epsg=4326)
    def update_z(row):
        t_heig = row['T_heig'] * 0.6
        geometry = row['geometry']
        updated_coordinates = [(x, y, t_heig) for x, y in geometry.exterior.coords]
        return Polygon(updated_coordinates)
    # Apply the function to create a new column "geometry_z"
    gdf['geometry'] = gdf.apply(update_z, axis=1)
    added_tree_base_crown = pdk.Layer("PolygonLayer",
                            data=gdf,
                            get_polygon="geometry.coordinates",
                            get_fill_color=[75, 100, 75],
                            get_line_color=[50, 50, 50],
                            get_line_width=0.5,
                            get_elevation='T_heig',
                            wireframe=True,
                            extruded=True,
                            opacity=0.5,
                            pickable=False,)
    gdf = gpd.read_file(trees_base_trunk_path)
    gdf = gdf.to_crs(epsg=4326)
    added_tree_base_trunk = pdk.Layer("PolygonLayer",
                                data=gdf,
                                get_polygon="geometry.coordinates",
                                get_fill_color=[150, 75, 0],
                                get_line_color=[50, 50, 50],
                                get_line_width=0.5,
                                get_elevation='T_heig * 0.6',
                                wireframe=True,
                                extruded=True,
                                opacity=0.5,
                                pickable=False,)
    
    if display_added_trees == False:
        added_tree_base_crown = added_tree_base_trunk = None
    
    view_state = pdk.ViewState(latitude=lat, longitude=lon,
                               zoom=zoom, pitch=pitch, bearing=bearing)

    layers = [image_layer, building_layer, tree_base_crown, tree_base_trunk, added_tree_base_crown, added_tree_base_trunk]
    
    r = pdk.Deck(layers=layers,
                initial_view_state=view_state,
                map_provider="mapbox",
                map_style=pdk.map_styles.SATELLITE)
    st.pydeck_chart(r)

def pydeck_3d_geojson(time_index_3d, opacity_3d, display_image, display_added_trees, lat, lon, zoom, pitch, bearing):
    # image layer
    image_index = time_index_3d.replace(":","")
    if display_added_trees:
        image_path = f"./images/test_simulation/N03/test_{image_index}.png"
    else:
        image_path = f"./images/base_simulation/N03/base_{image_index}.png"
    image_bounds = [[9.1718298413872255, 47.6588733206033766],  # Southwest corner
                    [9.1718298413872255, 47.663490547562823],  # Northwest corner
                    [9.1786643808656230, 47.663490547562823],  # Northeast corner
                    [9.1786643808656230, 47.6588733206033766]   # Southeast corner
                    ]
    image_layer = pdk.Layer("BitmapLayer",
                            image=image_path,
                            bounds=image_bounds,
                            opacity=opacity_3d,)
    if display_image is False:
        image_layer = None
    
    # building shapefile layer
    building_geojson_path = r"./data/geojson/buildings.geojson"
    gdf = gpd.read_file(building_geojson_path)
    building_layer = pdk.Layer("PolygonLayer",
                            data=gdf,
                            get_polygon="geometry.coordinates",
                            get_fill_color=[250, 250, 250],  # Specify the fill color
                            get_line_color=[50, 50, 50],  # Specify the line color
                            get_line_width=0.5,  # Specify the line width
                            get_elevation='B_hoeh',  # Map the "B_hoeh" column to elevation
                            wireframe=True,
                            extruded=True,
                            pickable=False,)
    
    # tree geojson layer (for trunk and crown (existing trees))
    trees_base_crown_path = r"./data/geojson/trees_base_crown.geojson"
    trees_base_trunk_path = r"./data/geojson/trees_base_trunk.geojson"
    gdf = gpd.read_file(trees_base_crown_path)
    def update_z(row):
        t_heig = row['T_heig'] * 0.6
        geometry = row['geometry']
        updated_coordinates = [(x, y, t_heig) for x, y in geometry.exterior.coords]
        return Polygon(updated_coordinates)
    # Apply the function to create a new column "geometry_z"
    gdf['geometry'] = gdf.apply(update_z, axis=1)
    tree_base_crown = pdk.Layer("PolygonLayer",
                            data=gdf,
                            get_polygon="geometry.coordinates",
                            get_fill_color=[75, 200, 75],
                            get_line_color=[50, 50, 50],
                            get_line_width=0.5,
                            get_elevation='T_heig',
                            wireframe=True,
                            extruded=True,
                            opacity=0.5,
                            pickable=False,)
    gdf = gpd.read_file(trees_base_trunk_path)
    tree_base_trunk = pdk.Layer("PolygonLayer",
                                data=gdf,
                                get_polygon="geometry.coordinates",
                                get_fill_color=[150, 75, 0],
                                get_line_color=[50, 50, 50],
                                get_line_width=0.5,
                                get_elevation='T_heig * 0.6',
                                wireframe=True,
                                extruded=True,
                                opacity=0.5,
                                pickable=False,)
    
    # tree geojson layer (for trunk and crown (added trees))
    added_trees_crown_path = r"./data/geojson/added_trees_crown.geojson"
    added_trees_trunk_path = r"./data/geojson/added_trees_trunk.geojson"
    gdf = gpd.read_file(added_trees_crown_path)
    def update_z(row):
        t_heig = row['T_heig'] * 0.6
        geometry = row['geometry']
        updated_coordinates = [(x, y, t_heig) for x, y in geometry.exterior.coords]
        return Polygon(updated_coordinates)
    # Apply the function to create a new column "geometry_z"
    gdf['geometry'] = gdf.apply(update_z, axis=1)
    added_tree_base_crown = pdk.Layer("PolygonLayer",
                            data=gdf,
                            get_polygon="geometry.coordinates",
                            get_fill_color=[75, 100, 75],
                            get_line_color=[50, 50, 50],
                            get_line_width=0.5,
                            get_elevation='T_heig',
                            wireframe=True,
                            extruded=True,
                            opacity=0.5,
                            pickable=False,)
    gdf = gpd.read_file(added_trees_trunk_path)
    added_tree_base_trunk = pdk.Layer("PolygonLayer",
                                data=gdf,
                                get_polygon="geometry.coordinates",
                                get_fill_color=[150, 75, 0],
                                get_line_color=[50, 50, 50],
                                get_line_width=0.5,
                                get_elevation='T_heig * 0.6',
                                wireframe=True,
                                extruded=True,
                                opacity=0.5,
                                pickable=False,)
    
    # Tottle display of added trees
    if display_added_trees == False:
        added_tree_base_crown = added_tree_base_trunk = None
    
    # Define initial view state of pydeck map
    view_state = pdk.ViewState(latitude=lat, longitude=lon,
                               zoom=zoom, pitch=pitch, bearing=bearing,
                               height=750,)

    # Define layers to visualize in pydeck map
    layers = [image_layer, building_layer, tree_base_crown, tree_base_trunk, added_tree_base_crown, added_tree_base_trunk]
    
    # Display pydeck map
    r = pdk.Deck(layers=layers,
                 initial_view_state=view_state,
                 map_provider="mapbox",
                 map_style=pdk.map_styles.SATELLITE,
                 )
    
    st.pydeck_chart(r)

