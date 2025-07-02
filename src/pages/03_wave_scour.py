import streamlit as st
from utils.wavescour_utils.wave_scour_utils import calculate_regular_wave_scour



if __name__ == "__main__":
    st.header("Wave Scour Calculator")
    st.subheader("This application calculates the wave scour depth based on the given wind speed, water depth, and fetch length.")
    
    
    st.header("Input Parameters")
    U_10 = st.number_input("Wind Speed at 33 ft (U_10) in mph", min_value=10, value=200, step=1)
    #convert U_10 from miles per hour to meters per second
    U_10 = U_10 * 0.44704  # Convert mph to m/s
    d = st.number_input("Water Depth (d) in feet", min_value=0.0, value=5.0, step=0.1)
    #convert d from feet to meters
    d = d * 0.3048  # Convert feet to meters
    g = 9.82
    #convert g from feet per second squared to meters per second squared
    
    X = st.number_input("Fetch Length (X) in feet", min_value=500.0, value=10000.0, step=1.0)
    #convert X from feet to meters
    X = X * 0.3048  # Convert feet to meters
        
    if st.button("Calculate Wave Scour"):
        scour_depth = calculate_regular_wave_scour(U_10,X,d, g)
        #convert scour depth to feet
        scour_depth_ft = scour_depth * 3.28084
        st.success(f"Calculated Wave Scour Depth: {scour_depth_ft:.2f} feet")