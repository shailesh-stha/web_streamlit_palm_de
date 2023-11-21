import numpy as np
import netCDF4 as nc

# Input NetCDF file
input_file1 = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_base - backup\konstanz_4096x4096_v4_xy_N03.000.nc"
input_file2 = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_test - backup\konstanz_4096x4096_v5_xy_N03.000.nc"
# Output NetCDF file
output_file1 = r"F:\konstanz_4096x4096_v4_xy_N03_reduced.000.nc"
output_file2 = r"F:\konstanz_4096x4096_v5_xy_N03_reduced.000.nc"
output_file3 = r"F:\test.nc"

input = input_file1
output = output_file3

x_tick_interval = 1  # 1 hour
band_sequence = [0]
band_sequence.extend(np.arange(5, 144, 6 * x_tick_interval))

# List of variables to extract
variable_list = ['ta_2m*_xy', 'tsurf*_xy', 'wspeed_10m*_xy', 'rad_net*_xy']

# Read the input NetCDF file as a dataset
with nc.Dataset(input, mode="r") as ds:
    # Create a new NetCDF file for writing
    with nc.Dataset(output, mode="w") as out_file:
        # Copy the dimensions from the original dataset
        for dim_name, dim in ds.dimensions.items():
            # Modify the dimension size for the dimension 'time' to 25 and start from 0
            if dim_name == 'time':
                out_file.createDimension(dim_name, 25)
                out_variable = out_file.createVariable(dim_name, ds[dim_name].dtype, (dim_name,))
                out_variable[:] = np.arange(25)
            else:
                out_file.createDimension(dim_name, len(dim))
                # Copy 'x' and 'y' variables to the output file
                if dim_name == 'x' or dim_name == 'y':
                    out_variable = out_file.createVariable(dim_name, ds[dim_name].dtype, (dim_name,))
                    out_variable[:] = ds[dim_name][:]

        # Copy global attributes from the input file to the output file
        for i, attr_name in enumerate(ds.ncattrs()):
            if attr_name != "VAR_LIST":
                out_file.setncattr(attr_name, ds.getncattr(attr_name))

        # Loop through the list of variables
        for variable_name in variable_list:
            if variable_name in ds.variables:
                # Create a variable in the output file with the same name, data type, and dimensions
                out_variable = out_file.createVariable(variable_name, ds[variable_name].dtype,
                                                       ds[variable_name].dimensions)

                for i, band_index in enumerate(band_sequence):
                    # Extract the subset of data and save it to the output variable
                    band_data = ds[variable_name][band_index, :, :, :]
                    out_variable[i,:,:,:] = band_data
                    
                print(f"Variable data with name '{variable_name}' has been extracted and saved to '{output}'")
            else:
                print(f"Variable '{variable_name}' not found in the input dataset")

        # create and add new variable
        ref_variable = 'ta_2m*_xy'
        new_variable = 'test_xy'
        
        test_variable = out_file.createVariable(new_variable, ds[ref_variable].dtype, ds[ref_variable].dimensions)
        for i, band_index in enumerate(band_sequence):
            # Extract the subset of data and save it to the output variable
            band_data = ds[ref_variable][band_index, :, :, :] * 2
            test_variable[i,:,:,:] = band_data
            