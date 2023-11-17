import streamlit as st
import geopandas as gpd

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker, patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from utils import read_netcdf

def colormesh(variable_description, variable_unit, variable_data, location, building_id_mask, band_index, cmap, mask_color, vmin, vmax, shapefile_color, shapefile_url, hatch, shapefile_url_2):
    # read netcdf Metadata
    x, y, xc, yc, dx, dy = read_netcdf.grid_information()
    
    # Create single plot
    font_size = 14
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='w', edgecolor='k')
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.rcParams.update({'font.size': font_size+2})
    
    # title and labels
    plt.suptitle(f"{variable_description}", fontsize=font_size+2, weight='bold')
    ax.set_title(f"(2023-06-14 UTC+02)", fontsize = font_size)

    # define mask color
    cmap = plt.get_cmap(cmap)
    cmap.set_bad(mask_color)
    
    # Plot band data and building mask
    toplot = np.ma.masked_array(variable_data[band_index, 0, :, :], mask=building_id_mask)
    pcm = ax.pcolormesh(x, y, toplot, cmap=cmap, vmin=vmin, vmax=vmax, alpha=1.0, facecolor='black')
    
    # Plot AOI shapefile in plot
    if shapefile_url is not None:
        gdf = gpd.read_file(shapefile_url)
        gdf.plot(ax=ax, edgecolor=shapefile_color, linewidth=4.5, facecolor='none', hatch=hatch, alpha=0.45)
    # Plot Stations shapefile in plot
    if (shapefile_url_2 is not None) and location == "Overall (Altstadt)":
        gdf = gpd.read_file(shapefile_url_2)
        gdf.plot(ax=ax, edgecolor=['red', 'green', 'blue'], linewidth=4.5, facecolor='none', hatch=None, alpha=1.0)
        # Add labels to the polygons
        labels = ["Stn_1", "Stn_2", "Stn_3"]
        for i, (geometry, label) in enumerate(zip(gdf['geometry'], labels)):
            centroid_x = geometry.centroid.x
            centroid_y = geometry.centroid.y
            ax.text(centroid_x, centroid_y-10, label, fontsize=font_size, ha='center', va='center')
    
    # Define grids and label
    ax.grid(True, linestyle='-.', linewidth=1.25, color='k', alpha=0.75)
    ax.set_xlabel('EASTING', fontsize = font_size, weight="bold")
    ax.set_ylabel('NORTHING', fontsize = font_size, weight="bold")
    ax.set_aspect(1)
   
    # Configure minor tick locators and grid
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_minor_locator(ticker.AutoMinorLocator(n=5))
        axis.grid(which='minor', linestyle='--', linewidth=0.75, color='grey', alpha=0.5)

    ax.tick_params(axis='x', labelsize=font_size)
    ax.tick_params(axis='y', labelrotation=90, labelsize=font_size)
    def format_y_axis_ticks(y, pos):
        formatted_label = f'{y:.0f}'
        return formatted_label
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_y_axis_ticks))
    
    # Defint plot size (extents) based on location
    if location == "Overall (Altstadt)":
        ax.set_xlim(x[0]+0,x[-1]-0)
        ax.set_ylim(y[0]+0,y[-1]-0)
    elif location == "Augstinerplatz":
        ax.set_xlim(x[0]+30,x[-1]-292)
        ax.set_ylim(y[0]+0,y[-1]-322)
    elif location == "Markstätte":
        ax.set_xlim(x[0]+180,x[-1]-62)
        ax.set_ylim(y[0]+20,y[-1]-202)
    
    # Add colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.15)
    cb = fig.colorbar(pcm, cax=cax, extend='both', format='%.2f', spacing='uniform')
    
    # Add °C where unit is K
    if variable_unit == "K":
        tick_positions_kelvin = cb.get_ticks()
        tick_positions_celsius = tick_positions_kelvin - 273.15
        cb.set_ticks(tick_positions_kelvin)
        cb.set_ticklabels(["%.2f" % temp_celsius for temp_celsius in tick_positions_celsius])
        variable_unit = "°C"
    cb.ax.tick_params(labelsize=font_size, rotation=0)
    cb.ax.xaxis.set_ticks_position("top")
    cb.ax.set_ylabel(f"{variable_description} [{variable_unit}]", fontsize=font_size, weight="bold")
    
    # plot
    st.pyplot(fig)
