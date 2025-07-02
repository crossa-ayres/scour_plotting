import math
import numpy as np
import pandas as pd
import streamlit as st

def calculate_fetch_limited_contidion(X, u, g):
    """
    Calculate the fetch limited condition based on the given parameters. Used to deterime if the fetch length is sufficient to genetate 
    full wave height conditions.

    Parameters:
    X (float): Fetch distance in meters.
    u (float): Wind speed in m/s.
    g (float): Gravitational acceleration in m/s^2.

    Returns:
    float: Fetch limited condition value.
    """
    return 77.23*(X**0.67/(u**0.43*g**0.33))

def calculate_friction_velocity(U_10):
    """
    Calculate the friction velocity (u*) based on the given wind speed at 10 meters (U_10).

    Parameters:
        U_10 (float): Wind speed at 10 meters in m/s.

    Returns:
        float: Friction velocity in m/s.
    """
    drag_coeff = 0.001*(1.1+0.035*U_10)
    return math.sqrt(U_10**2 * drag_coeff)

def calculate_approximate_wave_period(U_10,X,g):
    """
    Calculate the approximate wave period (T) based on the given wind speed at 10 meters (U_10) and gravitational acceleration (g).
    Parameters:
        U_10 (float): Wind speed at 10 meters in m/s.
        g (float): Gravitational acceleration in m/s^2.
    Returns:
        float: Approximate wave period in seconds.
    """
    uf = calculate_friction_velocity(U_10)  # Assuming U_10 is 10 m/s for the calculation
    return ((0.651*((g*X)/(uf**2))**(1/3))*uf)/g

def calulate_wave_length(U_10,X,d,g):
    """
    Calculate the wave length (L) based on the given parameters.

    Parameters:
    d (float): Water depth in meters.
    g (float): Gravitational acceleration in m/s^2.

    Returns:
    float: Wave length in meters.
    """
    T = calculate_approximate_wave_period(U_10,X,g)
    
    return (g*T**2/(2*3.1415))*math.sqrt(math.tanh((4*3.1415**2*d)/(g*T**2)))

def calculate_wave_height(U_10,X, g):
    """
    Calculate the fully developed wave height (H) based on the given wind speed at 10 meters (U_10) and gravitational acceleration (g).

    Parameters:
    U_10 (float): Wind speed at 10 meters in m/s.
    g (float): Gravitational acceleration in m/s^2.

    Returns:
    float: Fully developed wave height in meters.
    """
    uf = calculate_friction_velocity(U_10)
    return ((4.13*10**-2*((g*X)/uf**2)**(1/2))*uf**2)/g

def plot_wave_profile(L_ft, H_ft):
    """
    Plot the wave profile based on the wave length (L) and wave height (H).

    Parameters:
    L (float): Wave length in meters.
    H (float): Wave height in meters.
    """
    sample = int(L_ft *4)
    x = np.linspace(0, L_ft*2, sample)
    y = H_ft * np.sin((2 * np.pi / L_ft) * (x+(L_ft/4)))
    wave_profile_df = pd.DataFrame({'Distance (ft)': x, 'Wave Height (ft)': y})
    st.subheader("Wave Profile")
    st.line_chart(wave_profile_df,x="Distance (ft)",y = "Wave Height (ft)", width=800, height=400, use_container_width=True)

def calculate_regular_wave_scour(U_10,X,d,g):
    """
    Calculate the regular wave scour based on the given wind speed at 10 meters (U_10), water depth (d), and gravitational acceleration (g).
    Parameters:
        U_10 (float): Wind speed at 10 meters in m/s.
        d (float): Water depth in meters.
        g (float): Gravitational acceleration in m/s^2.
    Returns:
        float: Regular wave scour in meters.
    """
    L = calulate_wave_length(U_10,X,d,g)
    H = calculate_wave_height(U_10,X,g)
    k = (2*3.1415)/L
    L_ft = L * 3.28084  # Convert wave length from meters to feet
    H_ft = H * 3.28084  # Convert water depth from meters to feet
    plot_wave_profile(L_ft, H_ft)

    st.write(f"Wave Length (L): {L_ft:.2f} ft")
    st.write(f"Wave Height (H): {H_ft:.2f} ft")
    st.write(f"Maximum Scour Occurs at {L_ft/4:.2f} ft From the Shore")
 
    return (0.4/((math.sinh(k*d))**1.35))*H

