import numpy as np
import netCDF4 as nc

# Input NetCDF file
input_file1 = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_base - backup\konstanz_4096x4096_v4_xy_N03.000.nc"
input_file2 = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_test - backup\konstanz_4096x4096_v5_xy_N03.000.nc"
input_file3 = r"F:\Simulation_Comparison\simulation_data\konstanz_4096x4096_v4_static_N03"
# Output NetCDF file
output_file1 = r"F:\konstanz_4096x4096_v4_xy_N03.000.nc"
output_file2 = r"F:\konstanz_4096x4096_v5_xy_N03.000.nc"
output_file3 = r"F:\konstanz_4096x4096_v4_static_N03_building_id"

input = input_file3
output = output_file3

# Read the input NetCDF file as a dataset
with nc.Dataset(input, mode="r") as ds:
    # Define the variables you want to extract and save
    variable_list = ['building_id']

    # Create a new NetCDF file for writing
    with nc.Dataset(output, mode="w") as out_file:
        # Copy the dimensions from the original dataset (assuming you want the same dimensions)
        for dim_name, dim in ds.dimensions.items():
            out_file.createDimension(dim_name, len(dim))

        # Copy global attributes from the input file to the output file
        for i, attr_name in enumerate(ds.ncattrs()):
            if attr_name != "VAR_LIST":
                print(attr_name)
                out_file.setncattr(attr_name, ds.getncattr(attr_name))
        
        # Iterate through the variables in the variable_list and save them to the output file
        for variable_name in variable_list:
            if variable_name in ds.variables:
                # Create a variable in the output file with the same name, data type, and dimensions
                out_variable = out_file.createVariable(variable_name, ds[variable_name].dtype, ds[variable_name].dimensions)
                # Copy the data from the input variable to the output variable
                out_variable[:] = ds[variable_name][:]
                print(f"Variable data with name '{variable_name}")
            else:
                print(f"Variable '{variable_name}' not found in the input dataset")

# The output file is automatically closed when the 'with' block is exited
