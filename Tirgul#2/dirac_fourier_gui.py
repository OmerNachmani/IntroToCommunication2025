import os
import sys
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend which works well for freezing
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import datetime

# Function to create a standard rectangular pulse in time domain
def rect(t, width):
    """
    Standard rectangular function with height 1 and specified width.
    The rectangle extends from -width/2 to +width/2 with height 1.
    """
    return np.where(np.abs(t) <= width/2, 1.0, 0.0)

# Function to create a scaled rectangular pulse for Dirac delta approximation
def dirac_rect(t, epsilon):
    """
    Rectangular function scaled to approximate Dirac delta.
    Height is 1/epsilon, width is epsilon.
    As epsilon approaches 0, this approaches Dirac delta.
    """
    # Scale height by 1/epsilon to maintain unit area as width decreases
    return (1.0/epsilon) * rect(t, epsilon)

# Function to compute the Fourier transform
def compute_ft(f, epsilon):
    """
    Compute the Fourier transform of the scaled rectangular function.
    For small epsilon, this approaches 1 for all frequencies.
    """
    # Special case for very small epsilon
    if epsilon < 0.005:
        # As epsilon approaches 0, the FT approaches 1 everywhere
        return np.ones_like(f)
    
    # Calculate sinc(pi * f * epsilon)
    x = np.pi * f * epsilon
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.sin(x) / x
    
    # Fix values at singularities
    y[np.isnan(y)] = 1.0
    
    return y

def main():
    # Get current timestamp for window title
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Set up time and frequency domains
    fs = 1000
    time_range = 5
    freq_range = 20
    t = np.linspace(-time_range, time_range, fs*2)
    f = np.linspace(-freq_range, freq_range, fs*2)

    # Width parameter range
    min_width = 0.001
    max_width = 2.0
    init_width = 0.5  # Initial width

    # Create the figure and subplots
    fig = plt.figure(figsize=(14, 8))
    fig.canvas.manager.set_window_title(f'Dirac Delta Function Visualization - {current_time}')
    
    # Add formulas as the title
    fig.suptitle(r'$\delta(t) = \lim_{\varepsilon \to 0} \frac{1}{\varepsilon} \Pi(\frac{t}{\varepsilon})$ and $\mathcal{F}\{\delta(t)\} = \lim_{\varepsilon \to 0} \mathrm{sinc}(\pi f \varepsilon) = 1$', 
                 fontsize=14, y=0.98)

    # Add subplots
    ax_time = plt.subplot2grid((5, 2), (0, 0), rowspan=4)
    ax_freq = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
    ax_slider = plt.subplot2grid((5, 2), (4, 0), colspan=1)
    ax_button = plt.subplot2grid((5, 2), (4, 1), colspan=1)

    # Initialize the plots
    time_plot, = ax_time.plot([], [], 'r-', lw=2)
    freq_plot, = ax_freq.plot([], [], 'b-', lw=2)
    
    # Add a flat line at y=1 for the limiting case
    flat_line, = ax_freq.plot([-freq_range, freq_range], [1, 1], 'b-', lw=2, alpha=0)

    # Set up the axes
    ax_time.set_xlim(-time_range, time_range)
    ax_time.set_ylim(0, 10)  # Initial range, will be adjusted dynamically
    ax_time.set_xlabel('Time (t)', fontsize=12)
    ax_time.set_ylabel('Amplitude', fontsize=12)
    ax_time.set_title(r'Time Domain: $\frac{1}{\varepsilon}\Pi(\frac{t}{\varepsilon})$', fontsize=14)
    ax_time.grid(True)
    ax_time.axvline(x=0, color='k', linestyle='--', alpha=0.5)
    ax_time.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    
    # Updated x-axis ticks for time domain
    ax_time.set_xticks(np.arange(-time_range, time_range+1, 1))

    ax_freq.set_xlim(-freq_range, freq_range)
    ax_freq.set_ylim(-0.2, 1.2)  # Fixed y-limit to show the limiting value of 1
    ax_freq.set_xlabel('Frequency (f)', fontsize=12)
    ax_freq.set_ylabel('Amplitude', fontsize=12)
    ax_freq.set_title(r'Frequency Domain: $\mathcal{F}\{\delta(t)\} = 1$', fontsize=14)
    ax_freq.grid(True)
    ax_freq.axvline(x=0, color='k', linestyle='--', alpha=0.5)
    ax_freq.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Limit: y=1')
    ax_freq.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax_freq.legend(loc='upper right')

    # Function to update the plots based on width
    def update_plots(width):
        # Time domain plot update
        y_time = dirac_rect(t, width)
        time_plot.set_data(t, y_time)
        
        # Adjust y-axis limits for time domain based on height
        max_height = 1.0/width if width > 0 else 1.0  # Height is 1/width
        ax_time.set_ylim(0, max(1.2, max_height * 1.1))
        
        # Frequency domain plot update
        y_freq = compute_ft(f, width)
        freq_plot.set_data(f, y_freq)
        
        # For very small epsilon, fade in the flat line at y=1
        if width < 0.01:
            # Calculate crossfade alpha values
            alpha_val = 1.0 - (width / 0.01)
            flat_line.set_alpha(alpha_val)
            freq_plot.set_alpha(1.0 - alpha_val)
        else:
            flat_line.set_alpha(0)
            freq_plot.set_alpha(1.0)
        
        # Update title
        ax_time.set_title(r'Time Domain: $\frac{1}{\varepsilon}\Pi(\frac{t}{\varepsilon})$ with $\varepsilon=' + str(format(width, '.4e')) + '$')
        
        # Return the artists that have been updated
        return time_plot, freq_plot, flat_line

    # Create the slider widget for width adjustment
    width_slider = Slider(
        ax=ax_slider,
        label='Width (ε)',
        valmin=min_width,
        valmax=max_width,
        valinit=init_width,
        valstep=0.001,
        color='green'
    )

    # Create the play button
    play_button = Button(ax_button, 'Play Animation', color='lightgoldenrodyellow', hovercolor='0.975')

    # Function to handle slider changes
    def slider_update(val):
        width = width_slider.val
        update_plots(width)
        fig.canvas.draw_idle()

    # Variables for animation
    animation_active = False
    animation_timer = None
    animation_frames = None
    current_frame = 0

    # Function to step animation frame
    def step_animation():
        nonlocal current_frame, animation_active, animation_timer
        
        if not animation_active or current_frame >= len(animation_frames):
            # Animation complete
            play_button.label.set_text('Play Animation')
            animation_active = False
            if animation_timer is not None:
                animation_timer.stop()
                animation_timer = None
            return False  # Stop the timer
        
        # Update width from animation frames
        width = animation_frames[current_frame]
        width_slider.set_val(width)  # This calls slider_update
        current_frame += 1
        
        # If this was the last frame, reset
        if current_frame >= len(animation_frames):
            play_button.label.set_text('Play Animation')
            animation_active = False
            if animation_timer is not None:
                animation_timer.stop()
                animation_timer = None
        
        return True  # Continue the timer

    # Function to handle play button click
    def play_clicked(event):
        nonlocal animation_active, animation_timer, animation_frames, current_frame
        
        if animation_active:
            # Stop the animation
            if animation_timer is not None:
                animation_timer.stop()
                animation_timer = None
            play_button.label.set_text('Play Animation')
            animation_active = False
        else:
            # Start a new animation
            play_button.label.set_text('Stop Animation')
            animation_active = True
            current_frame = 0
            
            # Create values from current width to minimum
            current_width = width_slider.val
            
            if current_width <= min_width:
                # If at minimum already, animate from max to min
                animation_frames = np.logspace(np.log10(max_width), np.log10(min_width), 100)
            else:
                # Animate from current to minimum
                animation_frames = np.logspace(np.log10(current_width), np.log10(min_width), 100)
            
            # Define the update function
            def timer_tick():
                step_animation()
                fig.canvas.draw_idle()
            
            # Create and start the timer
            animation_timer = fig.canvas.new_timer(interval=50)
            animation_timer.add_callback(timer_tick)
            animation_timer.start()

    # Connect the callbacks
    width_slider.on_changed(slider_update)
    play_button.on_clicked(play_clicked)

    # Initial plot update
    update_plots(init_width)

    # Add explanatory text on the figure
    fig.text(0.5, 0.01, 
             "Use the slider to adjust the width (ε) of the rectangular pulse.\n" + 
             "Click 'Play Animation' to see the pulse approach the Dirac delta function (ε → 0).",
             ha='center', fontsize=10)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Display error in a GUI window if there's an exception
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"An error occurred: {str(e)}\n\nPlease report this issue.")
        raise e