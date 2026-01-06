import matplotlib.pyplot as plt
import numpy as np

# This function takes in a time array and an EMG array and plots the raw EMG data.
def plot_raw(time, emg):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(time, emg, label="Raw EMG", color="C0")    # Plots the raw EMG data.
    ax.set_title("Raw EMG")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)    # Adds a faint grid to the plot.
    ax.legend()
    fig.tight_layout()
    return fig

# This function takes in a time array and a dictionary of processed EMG data and plots the rectified, filtered, and envelope signals.
def plot_processed(time, processed):
    fig, ax = plt.subplots(figsize=(8, 4))

    # Gets the processed EMG signals from the dictionary.
    filtered = processed.get("filtered")
    if filtered is None:
        filtered = processed.get("demeaned")
    rectified = processed.get("rectified")
    envelope = processed.get("envelope")

    # Plots the processed EMG signals if they exist.
    if filtered is not None:
        ax.plot(time, filtered, label="Filtered", color="C1")
    if rectified is not None:
        ax.plot(time, rectified, label="Rectified", color="C2", alpha=0.6)
    if envelope is not None:
        ax.plot(time, envelope, label="Envelope", color="C3", linewidth=2)

    ax.set_title("Processed EMG")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig

