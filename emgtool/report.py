import os
import textwrap

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# This function takes in a value and a precision and returns the value formatted to the precision.
def _format_value(value, precision=2):
    if value is None:
        return "n/a"
    if isinstance(value, (float, np.floating)) and np.isnan(value):  # If the value is a float and is NaN then return "n/a".
        return "n/a"
    if isinstance(value, (float, np.floating)):  # If the value is a float then return the value formatted to the precision.
        return f"{value:.{precision}f}"
    return str(value)

# This function takes in several parameters and draws the label and value wrapped to the width.
def _draw_wrapped_line(ax, x, y, label, value, width=80, fontsize=12):
    if value is None:
        value = ""
    wrapped = textwrap.wrap(value, width=width) or [""]    # Wraps the text in value to make it fit within the width, if value is empty then return an empty list.
    ax.text(x, y, f"{label}: {wrapped[0]}", fontsize=fontsize, va="top")    # Draws the first line of the wrapped text without indenting (because of label).
    y -= 0.03
    for cont in wrapped[1:]:    # Draws the rest of the wrapped text with an indent.
        ax.text(x, y, f"    {cont}", fontsize=fontsize, va="top")
        y -= 0.03
    return y

# This functin takes in several parameters and creates a PDF report with a summary page followed by the signal plots.
def build_pdf_report(out_path, patient, summary, figures):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)    # Creates the directory for the output PDF report if it doesn't exist.

    with PdfPages(out_path) as pdf:    # Opens a PDF file to write into it.
        cover = plt.figure(figsize=(8.5, 11))   # First page is standard 8.5x11 inches size.
        ax = cover.add_subplot(111)    # Creates an axis object for drawing area for the first page.
        ax.axis("off")    # Hides the axis lines.

        # Set margins to make sure nothing gets cut off.
        cover.subplots_adjust(left=0.06, right=0.40, top=0.95, bottom=0.05)

        # Draw the title and patient info on the first page.
        y = 0.95
        ax.text(0.06, y, "EMG Report", fontsize=18, fontweight="bold", va="top")
        y -= 0.06

        ax.text(0.06, y, "Patient Info", fontsize=14, fontweight="bold", va="top")
        y -= 0.04

        # Wrap patient information that might be long (like Notes usually).
        for key, value in patient.items():
            y = _draw_wrapped_line(ax, 0.1, y, key, str(value), width=85, fontsize=12)

        y -= 0.02
        ax.text(0.06, y, "Summary", fontsize=14, fontweight="bold", va="top")   # Draw the summary title.
        y -= 0.04

        stats = [
            ("Duration (s)", _format_value(summary.get("duration_s"))),   # Duration of the EMG data in seconds.
            ("Sample rate (Hz)", _format_value(summary.get("fs_hz"))),   # Sample rate of the EMG data in Hz.
            ("Min", _format_value(summary.get("min"))),   # Minimum value of the EMG data.
            ("Max", _format_value(summary.get("max"))),   # Maximum value of the EMG data.
            ("RMS", _format_value(summary.get("rms"))),   # Root mean square of the EMG data.
        ]
        for label, value in stats:
            y = _draw_wrapped_line(ax, 0.1, y, label, value, width=85, fontsize=12)   # Draw the summary information wrapped to the width.

        pdf.savefig(cover)  # Adds the first page to the PDF file.
        plt.close(cover)

        for fig in figures:   # Adds each of the signal plots to the PDF file as new pages.
            pdf.savefig(fig)
            plt.close(fig)