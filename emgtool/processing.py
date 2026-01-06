import numpy as np

from scipy import signal


# This function takes in a time array and guesses the time scale of the EMG data and returns a conversion ratio (to convert the time units into seconds).
def _guess_time_scale(time):
    if time is None:
        return 1.0
    time = np.asarray(time, dtype=float)    # Convert time array into numpy array so numpy functions can be used on it.
    if time.size < 2:    # If there is only one time point then return 1.0 (cannot measure time steps).
        return 1.0

    diffs = np.diff(time)   # diffs is a numpy array of the differences between consecutive time points.
    diffs = diffs[np.isfinite(diffs)]   # Remove any infinite values (or other garbage values) from the diffs array.
    if diffs.size == 0:   # If the diffs array is empty, then return 1.0 (cannot measure time steps).
        return 1.0

    median_dt = float(np.median(np.abs(diffs)))   # Find the average of the absolute values of the differences between consecutive time points.
    if median_dt <= 0:
        return 1.0

    if median_dt >= 1000:
        return 1e-6  # microseconds to seconds
    if 1 <= median_dt < 1000:
        return 1e-3  # milliseconds to seconds
    return 1.0  # assume already in seconds

# This function takes in a time array and tries to figure out the frequency of the EMG data and returns it in Hz.
def infer_sample_rate(time):
    time = np.asarray(time, dtype=float)    # Convert time array into numpy array so numpy functions can be used on it.
    if time.size < 2:
        return None

    diffs = np.diff(time)
    diffs = diffs[np.isfinite(diffs)]
    if diffs.size == 0:
        return None

    if np.any(diffs <= 0):  # If any difference is zero or negativve, then time is not increasing so return None.
        return None

    median_dt = float(np.median(diffs))   # Find the average of the differences between consecutive time points.
    if median_dt <= 0:   # If the average is zero or negative, then return None.
        return None

    spread = np.std(diffs)
    if median_dt == 0 or (spread / median_dt) > 0.1: # If the standard deviation / average time step is greater than 10%, steps are too inconsistent so return None.
        return None

    scale = _guess_time_scale(time)
    dt_seconds = median_dt * scale  # Convert the average time step into units of seconds (Since Hz is 1/seconds).
    if dt_seconds <= 0:
        return None

    return 1.0 / dt_seconds

# This function takes in a data array, a numerator coefficients array, and a denominator coefficients array and return the filtered data if the signal is long enough.
def _safe_filter(data, b, a):
    padlen = 3 * (max(len(a), len(b)) - 1)  # Calculate minimum length of the signal to be filtered.
    if data.size <= padlen:
        return data
    try:
        return signal.filtfilt(b, a, data)   # Filter the data using the parameters b and a.
    except ValueError:
        return data

# This function takes in raw EMG data and a sample rate (Hz) and return a dictionary of 5 different versions of the processed data.
def preprocess(emg, fs=None):
    emg = np.asarray(emg, dtype=float)    # Convert emg array into numpy array so numpy functions can be used on it.
    raw = emg.copy()    # Make a copy of the emg array and store it in raw.

    if emg.size:
        mean_value = np.nanmean(emg)    # Find the average of the emg array and store it in mean_value.
    else:
        mean_value = 0.0
    demeaned = emg - mean_value    # Subtract the average from the emg array and store it in demeaned (essentially removing the DC offset and centering the signal around 0).

    filtered = demeaned.copy()
    if fs is not None and np.isfinite(fs) and fs > 0:   # If we have a sample rate and the sample rate is finite and positive:
        nyquist = 0.5 * fs  # By definition, Nyquist frequency is half of the sample rate.
        if nyquist > 20:    # If nyquist is greater than 20 Hz, apply high pass filter to remove the low frequencies.
            b_hp, a_hp = signal.butter(4, 20.0 / nyquist, btype="highpass")     # Calculates the numerator and denominator coefficients for a high pass filter with filter order 4 and cutoff frequency of 20 Hz.
            filtered = _safe_filter(demeaned, b_hp, a_hp)   # Filters the data using the high pass filter.

    rectified = np.abs(filtered)

    envelope = rectified.copy()
    if fs is not None and np.isfinite(fs) and fs > 0:
        nyquist = 0.5 * fs
        if nyquist > 5:  # If nyquist is greater than 5 Hz, apply low pass filter to remove the high frequencies.
            b_lp, a_lp = signal.butter(4, 5.0 / nyquist, btype="lowpass")
            envelope = _safe_filter(rectified, b_lp, a_lp)

    return {
        "raw": raw,
        "demeaned": demeaned,
        "filtered": filtered,
        "rectified": rectified,
        "envelope": envelope,
    }
