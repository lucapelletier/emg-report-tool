import numpy as np

# This function reads the EMG data text file and returns a dictionary of patient info, a time array, and a raw EMG data array.
def read_emg_txt(path):
    patient = {}    # Initializes an empty dictionary for patient info.
    data = []    # Initializes an empty list for the EMG data.

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()   # Reads the file and stores the lines in a list called lines.

    header_done = False
    for line in lines:
        stripped = line.strip()    # Removes extra space and newlines from the line and stores it in stripped.
        if not header_done:
            if stripped == "":   # If the line is empty, that means the header is done (and we can start reading the data). So we set header_done to True and continue to the next line.
                header_done = True
                continue
            if ":" in line:
                key, value = line.split(":", 1)    # Splits the line between the : and stores the key and value accordingly in patient.
                patient[key.strip()] = value.strip()
            continue

        if stripped == "":
            continue

        if "," in stripped:
            parts = stripped.split(",")
        else:
            parts = stripped.split()
        if len(parts) < 2:  # If the line didn't have at least 2 values, then just skip the line. This is to ensure that the line is a valid EMG data line.
            continue
        try:    # Try to convert the EMG value and time value to floats.
            emg_val = float(parts[0].strip())
            time_val = float(parts[1].strip())
        except ValueError:    # If the conversion fails, then just skip the line.
            continue
        data.append((emg_val, time_val))    # Append the EMG value and time value to the end of the list data.

    if not data:    # If the list data is empty, then return the patient info, an empty time array, and an empty EMG array.
        return patient, np.array([], dtype=float), np.array([], dtype=float)

    emg_vals, time_vals = zip(*data)    # Splits the list data into two lists (one for the EMG values and one for the time values).
    emg = np.asarray(emg_vals, dtype=float)    # Converts the list of EMG values to a numpy array.
    time = np.asarray(time_vals, dtype=float)    # Converts the list of time values to a numpy array.
    return patient, time, emg

