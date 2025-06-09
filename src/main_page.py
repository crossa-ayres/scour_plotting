import streamlit as st



st.title("Welcome to the SRH-2D Model Data Processing App")
st.subheader("This application allows you to extract and visualize maximum depth x velocity (DxV) at bridge piers and plot scour results from SRH-2D model data.")
st.markdown("The applications located in the side bar require specific files to function correctly.")
st.header("The extract pier DxV application requires the following files:")
st.markdown("- SRH-2D geometry file (.srhgeom)")
st.markdown("- - Located in the _models > SRH-2D > ' recurrence interval ' folder ")
st.markdown("- SRH-2D map file (.map)")
st.markdown("- - Located in the _data folder ")
st.markdown("- Water depth data file (Vel_Mag_ft_p_s.h5)")
st.markdown("- - Located in the _data > ds folder ")
st.markdown("- Water velocity data file (Water_Depth_ft.h5)")
st.markdown("- - Located in the _data > ds folder ")
st.write("In addition to the files listed above, the user must also specify the ESPG state plane coordinate system used in the SRH2D Model.") 
st.markdown("Colorado state plane coordinate systems are listed below:")
st.markdown("- EPSG:2233 - Colorado North (ftUS)")
st.markdown("- EPSG:2232 - Colorado Central (ftUS)")
st.markdown("- EPSG:2231 - Colorado South (ftUS)")
st.header("The scour plotting application requires the following files:")

st.markdown("- scour_data (.csv)")


st.sidebar.markdown("# Home")