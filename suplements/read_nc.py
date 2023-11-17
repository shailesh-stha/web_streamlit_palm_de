import numpy as np
import netCDF4 as nc
import pandas as pd
import geopandas as gpd

file = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_base - backup\konstanz_4096x4096_v4_xy_N03.000.nc"
file = r"F:\Simulation_Comparison\simulation_data\kn_4096x4096_base\konstanz_4096x4096_v4_xy_N03.000.nc"
file = r"F:\Simulation_Comparison\simulation_data\konstanz_4096x4096_v4_static_N03"


# file = r"F:\konstanz_4096x4096_v5_xy_N03.000.nc"
# Read NetCDF file as dataset
ds = nc.Dataset(file, mode="r")
print(ds)

# Read variable from dataset
variable_names = list(ds.variables.keys())
print(variable_names)
for var in variable_names:
    print(var, np.shape(ds[var]))

