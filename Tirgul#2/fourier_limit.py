import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.ticker import FuncFormatter, MultipleLocator

###############################################################################
# 1. Define parameters and functions
###############################################################################

T1 = 1.0  # Fixed pulse width (seconds)

def x_periodic_time_domain(t, T):
    """
    Periodic rectangular pulse:
      x(t) = 1 for t mod T in [0, T1)
           = 0 otherwise.
    """
    tm = np.mod(t, T)
    return np.where((tm >= 0) & (tm < T1), 1.0, 0.0)

def compute_fourier_series(T, f_max=10.0):
    """
    Compute the Fourier series coefficients C_n for one period of x(t),
    where x(t)=1 on [0, T1) and 0 on [T1, T).

    We compute for n from -n_max to +n_max, with n_max = floor(f_max * T).

    Fourier series:
      C_n = (1/T) ∫₀^(T) x(t)e^{-j2π(n/T)t} dt

    Returns:
      fn: array of frequencies (n/T) for n in [-n_max, ..., n_max].
      Cn: complex Fourier series coefficients (double-sided).
    """
    N = 10001
    t_int = np.linspace(0, T, N, endpoint=False)
    x_int = np.where(t_int < T1, 1.0, 0.0)
    
    n_max = int(np.floor(f_max * T))
    n_vals = np.arange(-n_max, n_max + 1)
    fn = n_vals / T

    Cn = []
    for n in n_vals:
        exp_term = np.exp(-1j * 2 * np.pi * (n / T) * t_int)
        integral = np.trapz(x_int * exp_term, t_int)
        Cn_val = (1.0 / T) * integral
        Cn.append(Cn_val)
    return fn, np.array(Cn)

def continuous_transform_rect(f):
    """
    Continuous Fourier Transform of a rectangular pulse of width T1
    defined on [0, T1]:
    
      X(f) = ∫₀^(T1) e^{-j2πft} dt = (1 - e^{-j2πfT1})/(j2πf), with X(0)=T1.
    """
    Xf = np.zeros_like(f, dtype=complex)
    idx = f != 0
    Xf[idx] = (1 - np.exp(-1j * 2 * np.pi * f[idx] * T1)) / (1j * 2 * np.pi * f[idx])
    Xf[~idx] = T1
    return Xf

###############################################################################
# 2. Set up the interactive plotting (vertical layout + vertical slider)
###############################################################################

# Create a figure with 3 vertically stacked subplots
fig, (ax_time, ax_mag, ax_phase) = plt.subplots(3, 1, figsize=(8, 10))
plt.subplots_adjust(right=0.88, bottom=0.15, top=0.92, hspace=1.0)

def get_time_axis():
    """Return a fixed time axis from 0 to 20 seconds."""
    return np.linspace(0, 20, 2000)

# Initial period value
T0 = 4.0

# Formatter for the phase y-axis (multiples of π)
def pi_formatter(y, pos):
    if np.isclose(y, 0):
        return "0"
    return f"{y/np.pi:.1f}π"
phase_formatter = FuncFormatter(pi_formatter)

def update_plots(T):
    # Clear subplots
    ax_time.cla()
    ax_mag.cla()
    ax_phase.cla()
    
    # --- Time-Domain Plot ---
    t_plot = get_time_axis()  # Always from 0 to 20 seconds
    x_plot = x_periodic_time_domain(t_plot, T)
    ax_time.plot(t_plot, x_plot, 'b')
    ax_time.set_xlabel("Time [s]")
    ax_time.set_ylabel("x(t)")
    ax_time.grid(True)
    ax_time.set_ylim(-0.1, 1.1)
    # Set x-ticks at 1-second intervals:
    ax_time.xaxis.set_major_locator(MultipleLocator(1))
    ax_time.set_title(f"Time-Domain Signal (0 to 20 s, T = {T:.2f} s)", 
                      loc='left', pad=10, fontsize=11, fontweight='bold')
    ax_time.text(0.02, 0.95,
                 "$x(t)=1$ if $0\\leq (t\\;\\mathrm{mod}\\;T)<T_1$, else $0$ (with $T_1=1$ s)",
                 transform=ax_time.transAxes, ha='left', va='top', fontsize=9,
                 bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))
    
    # --- Fourier Series Computation ---
    f_max = 10.0
    fn, Cn = compute_fourier_series(T, f_max=f_max)
    Cn_mag = np.abs(Cn)
    Cn_phase = np.angle(Cn)
    n_max = int(np.floor(f_max * T))
    num_coeffs = 2 * n_max + 1
    
    # --- Continuous Fourier Transform ---
    f_cont = np.linspace(-f_max, f_max, 2001)
    Xf = continuous_transform_rect(f_cont)
    Xf_mag = np.abs(Xf)
    Xf_phase = np.angle(Xf)
    
    # --- Magnitude Plot (double-sided) ---
    stem_obj = ax_mag.stem(fn, Cn_mag, linefmt='C1-', markerfmt='C1o', basefmt='k-', use_line_collection=True, label="Fourier Series")
    ax_mag.plot(f_cont, Xf_mag / T, 'C0--', label="Fourier Transform (scaled)")
    ax_mag.set_xlabel("Frequency [Hz]")
    ax_mag.set_ylabel("|Cₙ|")
    ax_mag.set_xlim(-f_max, f_max)
    ax_mag.grid(True)
    ax_mag.set_title("Fourier Series Magnitude", loc='left', pad=10, fontsize=11, fontweight='bold')
    ax_mag.text(0.02, 0.92, f"# of coeffs: {num_coeffs}",
                transform=ax_mag.transAxes, ha='left', va='top', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))
    ax_mag.text(0.5, 1.02, 
                "$C_n=\\frac{1}{T}\\int_{0}^{T} x(t)e^{-j2\\pi (n/T)t}dt$\n"
                "$X(f)=\\frac{1-e^{-j2\\pi fT_1}}{j2\\pi f}$",
                transform=ax_mag.transAxes, ha='center', va='bottom', fontsize=9)
    ax_mag.legend(loc="upper right")
    
    # --- Phase Plot (double-sided) ---
    stem_obj_phase = ax_phase.stem(fn, Cn_phase, linefmt='C2-', markerfmt='C2o', basefmt='k-', use_line_collection=True, label="Fourier Series")
    ax_phase.plot(f_cont, Xf_phase, 'C0--', alpha=0.6, label="Fourier Transform Phase")
    ax_phase.set_xlabel("Frequency [Hz]")
    ax_phase.set_ylabel("Phase [rad]")
    ax_phase.set_xlim(-f_max, f_max)
    ax_phase.grid(True)
    ax_phase.set_title("Fourier Series Phase", loc='left', pad=10, fontsize=11, fontweight='bold')
    ax_phase.legend(loc="upper right")
    ax_phase.yaxis.set_major_formatter(phase_formatter)
    ax_phase.text(0.02, 0.92, "$\\angle C_n=\\arg(C_n)$",
                  transform=ax_phase.transAxes, ha='left', va='top', fontsize=9,
                  bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))
    
    fig.canvas.draw_idle()

# Initialize plots
update_plots(T0)

# Create a vertical slider on the right side
ax_slider = fig.add_axes([0.91, 0.15, 0.03, 0.7])
slider = Slider(ax_slider, "T [s]", 1.0, 20.0, valinit=T0, valstep=1.0, orientation="vertical")

def slider_update(val):
    update_plots(slider.val)

slider.on_changed(slider_update)

plt.show()
