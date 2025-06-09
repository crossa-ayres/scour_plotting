import os
from glob import glob
import streamlit as st
import pandas as pd
import rasterio
import numpy as np
from pyproj import Proj, transform, Transformer
import folium
from streamlit_folium import st_folium
from utils.dxv_utils.find_pier_nodes import read_map_file, read_geom_file, find_mesh_points




#This script processes hydrological data to extract peak water depth and velocity at bridge piers.

#required libraries:
#- pandas
#- numpy
#- h5py

#Requirements descrbed in the environment.yml file included in the repository.

#The script performs the following steps:
#1. Reads the SRH-2D map file to obtain pier data and arc-node mapping.
#2. Reads the SRH-2D geometry file to obtain model nodes.
#3. Finds mesh points corresponding to the pier data using the model nodes and arc-node mapping.
#4. Extracts water depth and velocity data from HDF5 files.
#5. Outputs the processed data to a CSV file.

#Inputs:
#- srh2d_map_file: Path to the SRH-2D map file.
#- srh2d_srhgeom_file: Path to the SRH-2D geometry file.
# water_depth_h5_file: Path to the HDF5 file containing water depth data.
#- water_velocity_h5_file: Path to the HDF5 file containing water velocity data.
#- output_path: Path to the output CSV file.
#- search_radius: max distance from the pier centerline nodes to search for max DxV

#Functions:
#- read_map_file: Reads the SRH-2D map file and returns pier data and arc-node mapping.
#- read_geom_file: Reads the SRH-2D geometry file and returns model nodes.
#- find_mesh_points: Finds mesh points for the piers and extracts water depth and velocity data.



if __name__ == "__main__":
    #path to the data folder
    # The data folder should contain the SRH-2D map file, geometry file, and HDF5 files for water depth and velocity.
    #path to the data folder
    st.set_page_config(layout="wide")
    st.header("Extract Maximum Depth x Velocity (DxV) at Piers")
    st.subheader("This application extracts the maximum depth, velocity, and depth x velocity (DxV) at bridge piers from SRH-2D model data. Please upload the required files indicated in the side bar to proceed.")
    st.text("To plot the location of the maximum DxV for each pier the correct ESPG coordinate system must be selected from the the drop down menu in the side bar. This application will convert projected state plane coordinates into WSG84 latitude and longitude used for plotting.")
    with st.sidebar:
        st.header("File Upload")
        st.subheader("Please upload the files specified below.")
        srh2d_srhgeom_file = st.file_uploader("Select .srhgeom file")
        srh2d_map_file = st.file_uploader("Select .map file")
        water_velocity_h5_file = st.file_uploader("Select Vel_Mag_ft_p_s.h5")
        water_depth_h5_file = st.file_uploader("Select Water_Depth_ft.h5")
        crs = st.selectbox("Select Coordinate Reference System (CRS)", ["EPSG:2233","EPSG:2232", "EPSG:2231", "EPSG:26910", "EPSG:26911", "EPSG:26912", "EPSG:26913", "EPSG:26914", "EPSG:26915"])
        if water_depth_h5_file is not None:
            depth_file_name = water_depth_h5_file.name
        
        
        

    #specify the search radius in feet around the pier centerline nodes
    # The search radius is used to find the maximum water depth and velocity within this radius.
    search_radius = 15


    if srh2d_map_file is not None and srh2d_srhgeom_file is not None and water_depth_h5_file is not None and water_velocity_h5_file is not None:
        pier_data, arc_node_mapping = read_map_file(srh2d_map_file, "Bridge Scour")
        model_nodes = read_geom_file(srh2d_srhgeom_file)
        
        max_nodes = find_mesh_points(pier_data, model_nodes,arc_node_mapping,water_depth_h5_file,depth_file_name,water_velocity_h5_file,search_radius )
        max_nodes = pd.DataFrame(max_nodes)
        lat = [model_nodes.loc[model_nodes["Node"] == node, "lat"].values[0] for node in max_nodes["Model Node"]]
        long = [model_nodes.loc[model_nodes["Node"] == node, "long"].values[0] for node in max_nodes["Model Node"]]

        max_nodes["size"] = max_nodes["DxV"] / 20  # Scale size for better visibility on the map
        
        transformer = Transformer.from_crs(crs,"EPSG:4326")

        lat, long =  transformer.transform(lat,long)
        max_nodes["lat"] = lat
        max_nodes["long"] = long
        
        pier_data = pd.merge(max_nodes, pier_data, on="Pier Node", how='outer')
        
        
        

        max_nodes = max_nodes.sort_values("DxV", ascending=False).drop_duplicates("Pier Arc ID").sort_index()
        max_nodes["color"] = np.random.rand(len(max_nodes["DxV"]),3 ).tolist()  # Random color for each point
        st.divider()
        st.subheader("Maximum Depth x Velocity (DxV) at Piers")
        st.dataframe(max_nodes, use_container_width=True)
        st.divider()
        st.subheader("Maximum Depth x Velocity (DxV) at Piers - Summary Statistics")
        st.bar_chart(data=max_nodes, x="Model Node", y="DxV", use_container_width=True)
        st.divider()
        st.subheader("Maximum Depth at Piers") 
        st.bar_chart(data=max_nodes, x="Model Node", y="Depth", use_container_width=True)
        st.divider()
        st.subheader("Maximum Velocity at Piers")
        st.bar_chart(data=max_nodes, x="Model Node", y="Velocity", use_container_width=True)
        st.divider()
        st.subheader("Map of Mesh Point location for Maximum Depth x Velocity (DxV) at Piers")
        pier_line_dict = {}
        for index, row in pier_data.iterrows():
            pier_line_dict[row["Pier Arc ID"]] = [row["lat_x"], row["long_x"]]
        
        
        #folium_map = folium.Map(
        #    location=[max_nodes["lat"].mean(), max_nodes["long"].mean()],
        #    zoom_start=14,
        #    tiles="OpenStreetMap",
        #)
        #folium.PolyLine(
        #        locations=[node for node in pier_line_dict.values()],
        #        color="red",
        #        weight=3,
        #        tooltip="Previous Route",
        #    ).add_to(folium_map)
        
        #folium_map.location(max_nodes, x="long", y="lat") # add the image column to the popup parameter
        #st_folium(folium_map, height=450, use_container_width=True)
        st.divider()
        st.map(data=max_nodes, latitude="lat", longitude="long",size = "size",color = "color", use_container_width=True)

