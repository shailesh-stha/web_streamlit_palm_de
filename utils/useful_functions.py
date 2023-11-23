# Useful functions

# convert band number to time in (hr:min:sec) or vice-versa
def band_index_to_time(band_index):
    # Calculate the total seconds
    total_seconds = (band_index) * 10 * 60
    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    total_seconds %= 3600
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    # Format the time as "00:00:00"
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_str

def band_index_to_time_hr_min(band_index):
    # Calculate the total seconds
    total_seconds = (band_index+1) * 10 * 60
    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    total_seconds %= 3600
    minutes = total_seconds // 60
    # Format string for return
    time_str = f"{hours:02d}:{minutes:02d}"
    return time_str

def time_to_band_index():
    time_hr_min = input('Please enter the simulation time in hr:min format: ')
    time = time_hr_min.split(':')
    band_index = int(time[0])*6 + int(time[1])//10
    return band_index