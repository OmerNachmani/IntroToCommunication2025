# Dirac Delta and Fourier Transform Visualizations

This repository contains two interactive Python scripts that visualize different aspects of signal processing.

## Scripts

### `dirac_fourier_gui.py`
This script demonstrates how a rectangular pulse can approximate the Dirac delta function in the time domain and its corresponding Fourier transform in the frequency domain.

- **Features:**
  - **Interactive Slider:** Adjust the pulse width (ε).
  - **Animation Button:** Observe the pulse approaching the Dirac delta function as ε → 0.
  - **Dual Plots:** Displays time-domain and frequency-domain plots side by side.
  - **Dynamic Titles:** Includes the current timestamp and formulas in the figure titles.

### `fourier_limit.py`
This script visualizes the Fourier series coefficients and the continuous Fourier transform of a periodic rectangular pulse signal.

- **Features:**
  - **Time-Domain Plot:** Shows a periodic rectangular pulse defined by a fixed pulse width \( T_1 \).
  - **Fourier Series Computation:** Computes and plots the magnitude and phase of the Fourier series coefficients.
  - **Continuous Fourier Transform:** Overlays the scaled continuous Fourier transform for comparison.
  - **Vertical Slider:** Adjust the period \( T \) of the signal interactively.

## Requirements

- Python 3.x
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)

Install the required packages using pip:

pip install numpy matplotlib


# Running the Scripts

## For the Fourier series/transform visualization:
~~~bash
python fourier_limit.py
python dirac_fourier_gui.py
~~~

## In GitHub Codespaces (or Other Headless Environments)

Codespaces typically runs in a headless mode (no GUI display). To run the scripts, consider one of the following options:

### Switch to a Non-Interactive Backend:
Modify the matplotlib backend in the scripts (for example, in `dirac_fourier_gui.py` change:

~~~python
matplotlib.use('TkAgg')
~~~

to:

~~~python
matplotlib.use('Agg')
~~~

This backend allows you to generate and save figures without displaying them. You can then save plots as image files using:

~~~python
plt.savefig("output.png")
~~~

### Use a Virtual Display (Xvfb):
If you need interactive GUI functionality in a headless environment, install Xvfb and run the script with a virtual display:

~~~bash
xvfb-run python dirac_fourier_gui.py
~~~

# Summary

- **dirac_fourier_gui.py:**  
  An interactive GUI that demonstrates the approximation of the Dirac delta function using a rectangular pulse, featuring both time-domain and frequency-domain visualizations along with an animation option.

- **fourier_limit.py:**  
  An interactive tool that visualizes the Fourier series and continuous Fourier transform of a periodic rectangular pulse signal, with adjustable period and clear plots for magnitude and phase.
