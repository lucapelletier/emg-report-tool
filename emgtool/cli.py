import argparse
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")   # This makes matplotlib run without popping up a window to display the plots.

# Import the functions from my other files.
from .io import read_emg_txt
from .plotting import plot_processed, plot_raw
from .processing import _guess_time_scale, infer_sample_rate, preprocess
from .report import build_pdf_report

def main():
    parser = argparse.ArgumentParser(description="EMG report generator")    # Creates a command reader so the program understands input and output.
    parser.add_argument("--input", required=True, help="Path to EMG TXT file")  # Requre the user to input a file path for the input EMG data.
    parser.add_argument("--out", required=True, help="Path to output PDF report")  # Requre the user to input a file path for the output PDF report.
    args = parser.parse_args()  # Read what was typed in the terminal and stores it in args.

    patient, time, emg = read_emg_txt(args.input) # Read the EMG data and stores a dictionary of patient informatio in patient, a time array in time, and an EMG array in emg.
    fs = infer_sample_rate(time)    # Try to figure out the frequency of EMG data and stores it in fs. If it can't be inferred, it will be None.
    processed = preprocess(emg, fs) # Clean the EMG data and stores a dictionary of 5 different versions of the processed data in processed.

    scale = _guess_time_scale(time) # Guess if the time scale is in microseconds, milliseconds, or seconds. Scale is the conversion ratio to convert the time units to seconds.
    duration_s = None # Initialize duration_s to None.
    if time.size >= 2:  # If we have at least 2 time points...
        duration_s = float((time[-1] - time[0]) * scale)
    elif fs:  # If we have a sample rate...
        duration_s = float(len(emg) / fs)

    # Create a dictionary for information about the EMG data.
    min_value = None
    if emg.size:
        min_value = float(np.nanmin(emg))

    max_value = None
    if emg.size:
        max_value = float(np.nanmax(emg))

    rms_value = None
    if emg.size:
        squared = np.square(emg)
        mean_square = np.nanmean(squared)
        rms_value = float(np.sqrt(mean_square))

    summary = {
        "duration_s": duration_s,
        "fs_hz": fs,
        "min": min_value,
        "max": max_value,
        "rms": rms_value,
    }

    raw_fig = plot_raw(time, emg)   # Plot the raw EMG data graph.
    processed_fig = plot_processed(time, processed)   # Plot the processed EMG data graph.

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)    # Ensures that the folder for the output PDF report exists. If it doesn't, then creates it.
    build_pdf_report(args.out, patient, summary, [raw_fig, processed_fig])  # Create the PDF report with all necessary information.


if __name__ == "__main__":
    main()

