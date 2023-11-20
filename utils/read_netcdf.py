import numpy as np
import netCDF4 as nc
import pandas as pd

from utils import useful_functions

# Dictionary of variable, meaning and units
variable_dict = {
    # variable:       variable description, variable unit
    "t*_xy":          ["Near surface characteristic temperature", "K", "NA"],
    "ta_2m*_xy":      ["2m air temperature", "°C", "Lufttemperatur (2m)"],
    "tsurf*_xy":      ["Surface temperature", "K", "Oberflächentemperatur"],
    "theta_2m*_xy":   ["2-m air potential temperature", "K", "NA"],
    "wspeed_10m*_xy": ["10-m wind speed", "m/s", "Windgeschwindigkeit"],
    "rad_net*_xy":    ["Net radiation flux at the surface", "W/m²", "Nettostrahlung"],
    "rad_lw_in*_xy":  ["Incoming longwave radiation flux", "W/m²", "NA"],
    "rad_lw_out*_xy": ["Outgoing longwave radiation flux", "W/m²", "NA"],
    "rad_sw_in*_xy":  ["Incoming shortwave radiation flux", "W/m²", "NA"],
    "rad_sw_out*_xy": ["Outgoing shortwave radiation flux", "W/m²", "NA"]
}

# Read PALM output (base or test) and return list of variables with dimension > 2 and return Metadata
def variable_list():
    file_1 = r"./data/netcdf/konstanz_4096x4096_v4_xy_N03_reduced.000.nc"
    output_nc_dataset = nc.Dataset(file_1, mode='r')
    
    # Create variable_list with dimension > 2
    dim_limit = 2
    variable_names = []
    for i in output_nc_dataset.variables.keys():
        if len(np.shape(output_nc_dataset[i])) > dim_limit:
            variable_names.append(i)
    
    # Create list of variable descriptions and variable units
    variable_descriptions = []
    variable_units = []
    variable_descriptions_de = []
    for variable in variable_names:
        if variable in variable_dict:
            variable_descriptions.append(variable_dict[variable][0])
            variable_units.append(variable_dict[variable][1])
            variable_descriptions_de.append(variable_dict[variable][2])

    return variable_names, variable_descriptions, variable_units, variable_descriptions_de

# Retrun netcdf Metadata
def grid_information():
    file_1 = r"./data/netcdf/konstanz_4096x4096_v4_xy_N03_reduced.000.nc"
    output_nc_dataset = nc.Dataset(file_1, mode='r')
    
    # Define grid spacing
    dx = output_nc_dataset['x'][1]-output_nc_dataset['x'][0]
    dy = output_nc_dataset['y'][1]-output_nc_dataset['y'][0]
    # Define number of cells
    nx = np.shape(output_nc_dataset['x'])[0]
    ny = np.shape(output_nc_dataset['y'])[0]

    # Coordinates of origin in PALM
    origin_x, origin_y, origin_z = output_nc_dataset.origin_x, output_nc_dataset.origin_y, output_nc_dataset.origin_z

    # Vector for coordinate at cell edges
    x = np.arange(nx+1)*dx + origin_x
    y = np.arange(nx+1)*dy + origin_y
    # Vector for coordinates at cell centers
    xc = np.arange(nx)*dx + origin_x + dx/2
    yc = np.arange(nx)*dy + origin_y + dy/2
    
    return x, y, xc, yc, dx, dy

# Read PALM output data based on domain (handles upto 3 domains right now)
def read_netcdf(domain):
    if domain == "N01":
        file_1 = r"./konstanz_4096x4096_v4_xy.000.nc"
        file_2 = r".//konstanz_4096x4096_v5_xy.000.nc"
        file_static = r"./konstanz_4096x4096_v4_static"
    elif domain == "N02":
        file_1 = r"./konstanz_4096x4096_v4_xy_N02.000.nc"
        file_2 = r"./konstanz_4096x4096_v5_xy_N02.000.nc"
        file_static = r"./konstanz_4096x4096_v4_static_N02"
    elif domain == "N03":
        file_1 = r"./konstanz_4096x4096_v4_xy_N03.000.nc"
        file_2 = r"./konstanz_4096x4096_v5_xy_N03.000.nc"
        file_static = r"./konstanz_4096x4096_v4_static_N03"
    elif domain == "N03_reduced":
        file_1 = r"./data/netcdf/konstanz_4096x4096_v4_xy_N03_reduced.000.nc"
        file_2 = r"./data/netcdf/konstanz_4096x4096_v5_xy_N03_reduced.000.nc"
        file_static = r"./data/netcdf/konstanz_4096x4096_v4_static_N03_building_id"
   
    # Read netCDF files
    output_nc_dataset_1 = nc.Dataset(file_1, mode='r')
    output_nc_dataset_2 = nc.Dataset(file_2, mode='r')
    static_nc_dataset = nc.Dataset(file_static, mode='r')
    
    return(output_nc_dataset_1, output_nc_dataset_2, static_nc_dataset)

# Returning masked variables data and building mask
def variable_data_masked(variable_name):
    # Read the necessary netCDF datasets
    output_nc_dataset_1, output_nc_dataset_2, static_nc_dataset = read_netcdf(domain = "N03_reduced")

    # Read variable data for the given variable_name
    variable_data_1 = output_nc_dataset_1[variable_name]
    variable_data_2 = output_nc_dataset_2[variable_name]
    
    # Create empty arrays to store the masked data for both datasets
    variable_data_1_masked = np.empty_like(variable_data_1)
    variable_data_2_masked = np.empty_like(variable_data_2)
    
    # Create a mask for buildings
    building_id_mask = static_nc_dataset['building_id'][:,:]>0
    
    # Iterate over bands and apply the building mask to each band's data
    for band_index in range(0, np.shape(variable_data_1)[0]):
        band_data_1 = variable_data_1[band_index, 0, :, :]
        band_data_2 = variable_data_2[band_index, 0, :, :]
        
        # Apply the building mask to each band's data and store the masked data
        band_data_1_masked = np.where(building_id_mask, np.nan, band_data_1)
        band_data_2_masked = np.where(building_id_mask, np.nan, band_data_2)
        
        variable_data_1_masked[band_index, 0, :, :] = band_data_1_masked
        variable_data_2_masked[band_index, 0, :, :] = band_data_2_masked
     
    """Call grid info functions and define the AOI (Sim) bounds"""
    x, y, xc, yc, dx, dy = grid_information()
    # define bounds for AOI 1(↙), 2(→) and 3 (↑)
    # x1, x2, x3 = int((512960-x[0])/dx), int((513100-x[0])/dx), int((513000-x[0])/dx)
    # y1, y2, y3 = int((5278430-y[0])/dy), int((5278520-y[0])/dy), int((5278690-y[0])/dy)
    # dx1, dx2, dx3 = int(130/dx), int(230/dx), int(90/dx)
    # dy1, dy2, dy3 = int(130/dy), int(80/dy), int(130/dy)
    
    x1, x2, x3 = int((512960-x[0])/dx), int((513120-x[0])/dx), int((513000-x[0])/dx)
    y1, y2, y3 = int((5278430-y[0])/dy), int((5278540-y[0])/dy), int((5278690-y[0])/dy)
    dx1, dx2, dx3 = int(130/dx), int(180/dx), int(90/dx)
    dy1, dy2, dy3 = int(130/dy), int(50/dy), int(130/dy)
    
    # Create a boolean mask for the rectangle (AOI)
    run_1_aoi_1 = np.zeros_like(variable_data_1[0, 0, :, :], dtype=bool)
    run_1_aoi_2 = np.zeros_like(variable_data_1[0, 0, :, :], dtype=bool)
    run_1_aoi_1[y1:y1+dy1, x1:x1+dx1] = True
    run_1_aoi_2[y2:y2+dy2, x2:x2+dx2] = True
    
    run_2_aoi_1 = np.zeros_like(variable_data_2[0, 0, :, :], dtype=bool)
    run_2_aoi_2 = np.zeros_like(variable_data_2[0, 0, :, :], dtype=bool)
    run_2_aoi_1[y1:y1+dy1, x1:x1+dx1] = True
    run_2_aoi_2[y2:y2+dy2, x2:x2+dx2] = True
    
    # Create an empty array to store the masked data
    variable_data_masked_run_1_aoi_1 = np.empty_like(variable_data_1)
    variable_data_masked_run_1_aoi_2 = np.empty_like(variable_data_1)
    variable_data_masked_run_2_aoi_1 = np.empty_like(variable_data_2)
    variable_data_masked_run_2_aoi_2 = np.empty_like(variable_data_2)

    # Crate array to store masked variable data
    for band_index in range(0, np.shape(variable_data_1)[0]):
        band_data_run_1_aoi_1 = variable_data_1_masked[band_index, 0, :, :]
        band_data_run_1_aoi_2 = variable_data_1_masked[band_index, 0, :, :]
        band_data_run_2_aoi_1 = variable_data_2_masked[band_index, 0, :, :]
        band_data_run_2_aoi_2 = variable_data_2_masked[band_index, 0, :, :]
        
        band_data_masked_run_1_aoi_1 = np.where(run_1_aoi_1, band_data_run_1_aoi_1, np.nan)
        band_data_masked_run_1_aoi_2 = np.where(run_1_aoi_2, band_data_run_1_aoi_2, np.nan)
        band_data_masked_run_2_aoi_1 = np.where(run_2_aoi_1, band_data_run_2_aoi_1, np.nan)
        band_data_masked_run_2_aoi_2 = np.where(run_2_aoi_2, band_data_run_2_aoi_2, np.nan)
        
        variable_data_masked_run_1_aoi_1[band_index, 0, :, :] = band_data_masked_run_1_aoi_1
        variable_data_masked_run_1_aoi_2[band_index, 0, :, :] = band_data_masked_run_1_aoi_2
        variable_data_masked_run_2_aoi_1[band_index, 0, :, :] = band_data_masked_run_2_aoi_1
        variable_data_masked_run_2_aoi_2[band_index, 0, :, :] = band_data_masked_run_2_aoi_2
    """Call grid info functions and define the AOI (Sim) bounds"""
    
    """Call grid info functions and define station bounds"""
    x, y, xc, yc, dx, dy = grid_information()
    # define bounds for AOI 1(↙), 2(→) and 3 (↑)
    x1, x2, x3 = int((513010-x[0])/dx), int((513140-x[0])/dx), int((513250-x[0])/dx)
    y1, y2, y3 = int((5278470-y[0])/dy), int((5278560-y[0])/dy), int((5278570-y[0])/dy)
    dx1, dx2, dx3 = int(10/dx), int(10/dx), int(10/dx)
    dy1, dy2, dy3 = int(10/dy), int(10/dy), int(10/dy)
    
    # Create a boolean mask for the rectangle (AOI)
    run_1_stn_1 = np.zeros_like(variable_data_1[0, 0, :, :], dtype=bool)
    run_1_stn_2 = np.zeros_like(variable_data_1[0, 0, :, :], dtype=bool)
    run_1_stn_3 = np.zeros_like(variable_data_1[0, 0, :, :], dtype=bool)
    run_1_stn_1[y1:y1+dy1, x1:x1+dx1] = True
    run_1_stn_2[y2:y2+dy2, x2:x2+dx2] = True
    run_1_stn_3[y3:y3+dy3, x3:x3+dx3] = True

    # Create a boolean mask for the rectangle (AOI)
    run_2_stn_1 = np.zeros_like(variable_data_2[0, 0, :, :], dtype=bool)
    run_2_stn_2 = np.zeros_like(variable_data_2[0, 0, :, :], dtype=bool)
    run_2_stn_3 = np.zeros_like(variable_data_2[0, 0, :, :], dtype=bool)
    run_2_stn_1[y1:y1+dy1, x1:x1+dx1] = True
    run_2_stn_2[y2:y2+dy2, x2:x2+dx2] = True
    run_2_stn_3[y3:y3+dy3, x3:x3+dx3] = True
    
    # Create an empty array to store the masked data
    data_run_1_stn_1 = np.empty_like(variable_data_1)
    data_run_1_stn_2 = np.empty_like(variable_data_1)
    data_run_1_stn_3 = np.empty_like(variable_data_1)
    data_run_2_stn_1 = np.empty_like(variable_data_2)
    data_run_2_stn_2 = np.empty_like(variable_data_2)
    data_run_2_stn_3 = np.empty_like(variable_data_2) 

    # Crate array to store masked variable data
    for band_index in range(0, np.shape(variable_data_1)[0]):
        band_data_run_1_stn_1 = variable_data_1_masked[band_index, 0, :, :]
        band_data_run_1_stn_2 = variable_data_1_masked[band_index, 0, :, :]
        band_data_run_1_stn_3 = variable_data_1_masked[band_index, 0, :, :]
        band_data_run_2_stn_1 = variable_data_2_masked[band_index, 0, :, :]
        band_data_run_2_stn_2 = variable_data_2_masked[band_index, 0, :, :]
        band_data_run_2_stn_3 = variable_data_2_masked[band_index, 0, :, :]
        
        band_data_masked_run_1_stn_1 = np.where(run_1_stn_1, band_data_run_1_stn_1, np.nan)
        band_data_masked_run_1_stn_2 = np.where(run_1_stn_2, band_data_run_1_stn_2, np.nan)
        band_data_masked_run_1_stn_3 = np.where(run_1_stn_3, band_data_run_1_stn_3, np.nan)
        band_data_masked_run_2_stn_1 = np.where(run_2_stn_1, band_data_run_2_stn_1, np.nan)
        band_data_masked_run_2_stn_2 = np.where(run_2_stn_2, band_data_run_2_stn_2, np.nan)
        band_data_masked_run_2_stn_3 = np.where(run_2_stn_3, band_data_run_2_stn_3, np.nan)
        
        data_run_1_stn_1[band_index, 0, :, :] = band_data_masked_run_1_stn_1
        data_run_1_stn_2[band_index, 0, :, :] = band_data_masked_run_1_stn_2
        data_run_1_stn_3[band_index, 0, :, :] = band_data_masked_run_1_stn_3
        data_run_2_stn_1[band_index, 0, :, :] = band_data_masked_run_2_stn_1
        data_run_2_stn_2[band_index, 0, :, :] = band_data_masked_run_2_stn_2
        data_run_2_stn_3[band_index, 0, :, :] = band_data_masked_run_2_stn_3
    """Call grid info functions and define station bounds"""
    
    # Return the masked data for both datasets and the building mask   
    return variable_data_1_masked, variable_data_2_masked, building_id_mask, variable_data_masked_run_1_aoi_1, variable_data_masked_run_1_aoi_2, variable_data_masked_run_2_aoi_1, variable_data_masked_run_2_aoi_2, data_run_1_stn_1, data_run_1_stn_2, data_run_1_stn_3, data_run_2_stn_1, data_run_2_stn_2, data_run_2_stn_3

# Compute statistics for masked variable data
def compute_statistics_2d(variable_data):
    num_bands = np.shape(variable_data)[0]
    statistics = []
    
    for band_index in range(0, num_bands):
        # Extract masked data
        band_data_masked = variable_data[band_index, 0, :, :]
        # Compute statistics
        band_data_masked_mean = np.nanmean(band_data_masked)
        band_data_masked_max = np.nanmax(band_data_masked)
        band_data_masked_min = np.nanmin(band_data_masked)
        
        time = band_index
        
        # Append
        statistics.append([band_index, time,
                           band_data_masked_mean,
                           band_data_masked_max,
                           band_data_masked_min])
    
    column_labels = ["band_index", "time", "mean", "maximum", "minimum"]
    dataframe = pd.DataFrame(statistics, columns=column_labels)
    return dataframe