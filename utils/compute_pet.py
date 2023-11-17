import numpy as np
import netCDF4 as nc

# Dictionary of variable, meaning and units
variable_dict = {
    # variable:       variable description, variable unit
    "t*_xy":          ["Near surface characteristic temperature", "K"],
    "ta_2m*_xy":      ["2m air temperature", "°C"],
    "tsurf*_xy":      ["Surface temperature", "K"],
    "theta_2m*_xy":   ["2-m air potential temperature", "K"],
    "wspeed_10m*_xy": ["10-m wind speed", "m/s"],
    "rad_net*_xy":    ["Net radiation flux at the surface", "W/m²"],
    "rad_lw_in*_xy":  ["Incoming longwave radiation flux", "W/m²"],
    "rad_lw_out*_xy": ["Outgoing longwave radiation flux", "W/m²"],
    "rad_sw_in*_xy":  ["Incoming shortwave radiation flux", "W/m²"],
    "rad_sw_out*_xy": ["Outgoing shortwave radiation flux", "W/m²"]
}

# Read PALM output data based on domain (handles upto 3 domains right now)
def read_netcdf(domain = "N01"):
    if domain == "N01":
        file_1 = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_base\konstanz_4096x4096_v4_xy.000.nc"
        file_2 = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_test\konstanz_4096x4096_v5_xy.000.nc"
        file_static = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_static\konstanz_4096x4096_v4_static"
    elif domain == "N02":
        file_1 = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_base\konstanz_4096x4096_v4_xy_N02.000.nc"
        file_2 = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_test\konstanz_4096x4096_v5_xy_N02.000.nc"
        file_static = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_static\konstanz_4096x4096_v4_static_N02"
    elif domain == "N03":
        file_1 = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_base\konstanz_4096x4096_v4_xy_N03.000.nc"
        file_2 = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_test\konstanz_4096x4096_v5_xy_N03.000.nc"
        file_static = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_static\konstanz_4096x4096_v4_static_N03"
   
    # Read netCDF files
    output_nc_dataset_1 = nc.Dataset(file_1, mode='r')
    output_nc_dataset_2 = nc.Dataset(file_2, mode='r')
    static_nc_dataset = nc.Dataset(file_static, mode='r')
    
    return(output_nc_dataset_1, output_nc_dataset_2, static_nc_dataset)

# TS = 1.7 + 0.118 ta+ 0.0019 IH - 0.322 v - 0.0073 ur + 0.0054 ts,ent
# where:
# ta        = air temperature, in ºC;
# IH        = incident solar radiation, in W/m2;
# v         = air speed,in m/s;
# ur        = umidade relative, in %;
# ts,ent    = mean superficial air temperature of the surroundings, in ºC

output_nc_dataset_1, output_nc_dataset_2, static_nc_dataset = read_netcdf(domain = "N03")
tair1 = output_nc_dataset_1["ta_2m*_xy"] # air_temperature
tair2 = output_nc_dataset_2["ta_2m*_xy"]
ih1 = output_nc_dataset_1["rad_sw_in*_xy"] # incident_solar_radiation
ih2 = output_nc_dataset_2["rad_sw_in*_xy"]
v1 = output_nc_dataset_1["wspeed_10m*_xy"] # wind velocity
v2 = output_nc_dataset_2["wspeed_10m*_xy"]
ur = 36 # Relative Humidity
tsurf1 = output_nc_dataset_1["tsurf*_xy"] #surface temperature
tsurf2 = output_nc_dataset_2["tsurf*_xy"]

TS1_overall = np.empty_like(tair1)
TS2_overall = np.empty_like(tair2)
TS1_data_masked = np.empty_like(tair1)
TS2_data_masked = np.empty_like(tair2)

building_id_mask = static_nc_dataset['building_id'][:,:]>0

for band_index in range(0, np.shape(tair1)[0]):
        band_data_1 = tair1[band_index, 0, :, :]
        band_data_2 = tair2[band_index, 0, :, :]
        
        TS1_data = 1.7 + 0.118*tair1[band_index, 0, :, :] + 0.0019*ih1[band_index, 0, :, :] - 0.322*v1[band_index, 0, :, :] - 0.0073*ur +0.0054*tsurf1[band_index, 0, :, :]
        TS2_data = 1.7 + 0.118*tair2[band_index, 0, :, :] + 0.0019*ih2[band_index, 0, :, :] - 0.322*v2[band_index, 0, :, :] - 0.0073*ur +0.0054*tsurf2[band_index, 0, :, :]
        
        TS1_data_masked_temp = np.where(building_id_mask, np.nan, TS1_data)
        TS2_data_masked_temp = np.where(building_id_mask, np.nan, TS2_data)
        
        TS1_overall[band_index, 0, :, :] = TS1_data
        TS2_overall[band_index, 0, :, :] = TS2_data
        
        TS1_data_masked[band_index, 0, :, :] = TS1_data_masked_temp
        TS2_data_masked[band_index, 0, :, :] = TS2_data_masked_temp
  
band_index = 89 #15hr
 
print()
print(np.nanmean(TS1_overall[band_index,0,:,:]))
print(np.nanmean(TS1_data_masked[band_index,0,:,:]))

print()
print(np.nanmean(TS2_overall[band_index,0,:,:]))
print(np.nanmean(TS2_data_masked[band_index,0,:,:]))

def save_netcdf():
    # Create a NetCDF file for TS1_data_masked
    output_file_TS1 = "F:/TS1_data_masked_corrected.nc"
    nc_TS1 = nc.Dataset(output_file_TS1, 'w', format='NETCDF4')

    # Create dimensions in the NetCDF file
    nc_TS1.createDimension('time', np.shape(TS1_data_masked)[0])
    nc_TS1.createDimension('height', np.shape(TS1_data_masked)[2])
    nc_TS1.createDimension('width', np.shape(TS1_data_masked)[3])

    # Create variables in the NetCDF file
    ts1_var = nc_TS1.createVariable('TS1_data_masked', 'f4', ('time', 'height', 'width'))

    # Set variable attributes
    ts1_var.units = "K"
    ts1_var.description = "Surface temperature with masked values"

    # Write data to the NetCDF file
    ts1_var[:, :, :] = TS1_data_masked[:]

    # Close the NetCDF file
    nc_TS1.close()

    # Create a NetCDF file for TS2_data_masked
    output_file_TS2 = "F:/TS2_data_masked_corrected.nc"
    nc_TS2 = nc.Dataset(output_file_TS2, 'w', format='NETCDF4')

    # Create dimensions in the NetCDF file
    nc_TS2.createDimension('time', np.shape(TS2_data_masked)[0])
    nc_TS2.createDimension('height', np.shape(TS2_data_masked)[2])
    nc_TS2.createDimension('width', np.shape(TS2_data_masked)[3])

    # Create variables in the NetCDF file
    ts2_var = nc_TS2.createVariable('TS2_data_masked', 'f4', ('time', 'height', 'width'))

    # Set variable attributes
    ts2_var.units = "K"
    ts2_var.description = "Surface temperature with masked values"

    # Write data to the NetCDF file
    ts2_var[:, :, :] = TS2_data_masked[:]

    # Close the NetCDF file
    nc_TS2.close()
    
save_netcdf()