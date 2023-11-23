import numpy as np


x_tick_interval = 1  # 1 hour
band_sequence = [0]
band_sequence.extend(np.arange(5, 144, 6 * x_tick_interval))
print(band_sequence)

band_sequence[15] = band_sequence[15]+1

print(band_sequence)