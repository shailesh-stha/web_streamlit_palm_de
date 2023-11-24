import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase

# Create a sample data array for demonstration
data = np.random.uniform(low=15, high=37.5, size=(10, 10))

# Set up the plot
fig, ax = plt.subplots()

# Plot the data using the 'turbo' colormap and specified range
im = ax.imshow(data, cmap='turbo', vmin=15, vmax=37.5)

# Create a horizontal colorbar legend
cbar = ColorbarBase(ax=ax, cmap='turbo', norm=Normalize(vmin=15, vmax=37.5),
                    orientation='horizontal', label='2m Air Temperature')

# Show the plot
plt.show()
