import netCDF4 as nc
import numpy as np
import plotly.figure_factory as ff

file_N03 = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_base - backup\konstanz_4096x4096_v4_3d_N03.000.nc"
fn_N03 = r"F:\Simulation_Comparison\simulation_data\_kn_4096x4096_static - backup\konstanz_4096x4096_v4_static_N03"

domain = "N03"
ds = nc.Dataset(file_N03, mode="r")
ds_topo = nc.Dataset(fn_N03, mode="r")

# Read Variable Data from output data        
variable_name1 = 'wspeed'
variable_name2 = 'wdir'
variable_name3 = 'u'
variable_name4 = 'v'

var1=ds[variable_name1]
var2=ds[variable_name2]
var3=ds[variable_name3]
var4=ds[variable_name4]

#create building mask
bmask = ds_topo['building_id'][:,:]>0

#define grid spacing
dx = ds['x'][1]-ds['x'][0]
dy = ds['y'][1]-ds['y'][0]
#define number of cells
nx = np.shape(ds['x'])[0]
ny = np.shape(ds['y'])[0]

#coordinates of origin in PALM
origin_x, origin_y, origin_z = ds.origin_x, ds.origin_y, ds.origin_z

#vector for coordinate at cell edges
x = np.arange(nx+1)*dx + origin_x
y = np.arange(nx+1)*dy + origin_y
#vector for coordinates at cell centers
xc = np.arange(nx)*dx + origin_x + dx/2
yc = np.arange(nx)*dy + origin_y + dy/2

band_index = [71]
level_index = 4

X, Y = np.meshgrid(xc, yc)

# Extract wind speed and wind direction data
wspeed_data = var1[band_index, level_index, :, :]
wdir_data = var2[band_index, level_index, :, :]
# Convert wind direction from degrees to radians
wdir_rad = np.radians(wdir_data)

u_data = var3[band_index, level_index, :, :]
v_data = var4[band_index, level_index, :, :]
u = u_data
v = v_data

# Create streamline figure
fig = ff.create_streamline(xc, yc, u, v, arrow_scale=.1)
fig.show()