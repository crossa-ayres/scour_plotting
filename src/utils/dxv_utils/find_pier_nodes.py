import pandas as pd 
import re
import math
import numpy as np
from pyproj import Proj, transform, Transformer
import streamlit as st
from .read_srh_results import extract_data


def read_map_file(map_file_path:str, scour_run:str) -> tuple:
    """
    Reads a map file and extracts information about pier nodes and arc nodes.
    Args:
        map_file_path (str): The path to the map file.
        scour_run (str): The identifier for the scour run to search for in the file.
    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - pier_nodes: DataFrame with columns ['Node', 'lat', 'long'] containing information about pier nodes.
            - arc_nodes: DataFrame with columns ['Node', 'arcID'] containing information about arc nodes.

    """
    #with open(map_file_path, 'r') as file:
    file = map_file_path.read().decode("utf-8").splitlines()
    
    # Read each line in the file
    i=0
    arc_pier_index = []
    
    node_index = []
    scour_data_index = []
    
    for line in file:
        
        if scour_run in line:
            scour_data_index.append(i)
        if "arcType 5" in line:
            arc_pier_index.append(i)
            
        try:
            if "ID" in line and i > scour_data_index[0]:
                node_index.append(i)
        except:
            pass
            
        i+=1
  
    lines = [line.rstrip() for line in file]
    st.write(f"Found {len(arc_pier_index)} arc pier nodes and {len(node_index)} potential nodes surrounding the piers.")
    arc_nodes = []
    
    for i in arc_pier_index:
        n = re.split(r'\s+', lines[i-1])[1]
        p = re.split(r'\s+', lines[i-1])[2]
        arc_id = re.split(r'\s+', lines[i-3])[1]
        arc_nodes.append([f"ID {n}", f"ArcID {arc_id}"])
        arc_nodes.append([f"ID {p}", f"ArcID {arc_id}"])
    nodes = []
    pier_nodes = []
    arc_nodes = pd.DataFrame(arc_nodes, columns=["Node", "arcID"])
    for j in node_index:
        if lines[j-2] == "NODE" and lines[j] in arc_nodes["Node"].values:
            nodes.append(j)
            elements = re.split(r'\s+', lines[j-1].rstrip())
            arc = re.split(r'\s+', lines[j].rstrip())[1]
            arc_id = f"ID {arc}"
            pier_nodes.append([arc_id,elements[1], elements[2]])
            #xy[lines[j]] = re.split(r'\s+', lines[j-1])
    pier_nodes = pd.DataFrame(pier_nodes, columns=["Pier Node", 'lat', 'long'])
   
    pier_nodes['lat'] = pd.to_numeric(pier_nodes['lat'])
    pier_nodes['long'] = pd.to_numeric(pier_nodes['long'])
    return pier_nodes, arc_nodes

def read_geom_file(srhgeom_file_path:str) -> dict:
    """
    Reads a geometry file and extracts node information.
    Args:
        srhgeom_file_path (str): The path to the geometry file.
    Returns:
        DataFrame: A pandas DataFrame with columns ['Node', 'lat', 'long'] containing information about nodes.
    
    """
    #with open(srhgeom_file_path, 'r') as file:
    file = srhgeom_file_path.read().decode("utf-8").splitlines()
    # Read each line in the file
    node_rows = []
    for line in file:
        if "Node" in line.split():
            data_rows = re.split(r'\s+', line.rstrip())
            node_rows.append([data_rows[1], data_rows[2], data_rows[3]])
    node_xy = pd.DataFrame(node_rows, columns=["Node", 'lat', 'long'])
    node_xy['lat'] = pd.to_numeric(node_xy['lat'])
    node_xy['long'] = pd.to_numeric(node_xy['long'])
       
    return node_xy


def find_mesh_points(pier_data:dict, model_nodes:dict,arc_node_mapping:dict, depth_file:str,depth_file_name, velocity_file:str, search_radius = 8) -> None:
    """
    Finds the mesh points around piers and calculates the Depth x Velocity (DxV) product for each pier.

    Parameters:
        pier_data (dict): A dictionary containing the pier data with latitude and longitude.
        model_nodes (dict): A dictionary containing the model nodes with latitude, longitude, and node information.
        arc_node_mapping (dict): A dictionary mapping arc IDs to node IDs.
        depth_file (str): Path to the file containing depth data.
        velocity_file (str): Path to the file containing velocity data.
        output_path (str): Path to save the output CSV file.
        search_radius (int): max distance from the pier centerline nodes to search for max DxV

    Returns:
        None: The function saves the results to a CSV file specified by output_path.
    

    """
    max_nodes = []
    my_bar = st.progress(0, text="Processing Piers...")
    
    for index, row in pier_data.iterrows():
        my_bar.progress(index, text=f"Processing Pier {row["Pier Node"]}...")
        temp_nodes = []
        for idx, model_row in model_nodes.iterrows():
            distance = math.dist([row["lat"], row["long"]], [model_row["lat"], model_row["long"]])
            if distance <= search_radius:
                temp_nodes.append(model_row["Node"])
        depth, velocity = extract_data(depth_file,depth_file_name, velocity_file, temp_nodes)
        if depth.empty or velocity.empty:
            st.warning(f"No depth or velocity data found for pier {row["Pier Node"]}. Skipping.")
            continue
        else:
            depth = depth[depth["Depth"] > 0]
            velocity = velocity[velocity["Velocity"] > 0]
            if depth.empty or velocity.empty:
                st.warning(f"No valid depth or velocity data found for pier {row["Pier Node"]}. Skipping.")
                continue
            else:
                dv_array = np.array(np.round(depth["Depth"] * velocity["Velocity"],2))
            
                DxV = pd.DataFrame()
                DxV["Node"] = depth["Node"]
                DxV["DxV"] = dv_array
                max_value = DxV["DxV"].idxmax()

                result = arc_node_mapping.map(lambda x: x == row["Pier Node"])
                row_index, col_index = result.stack()[result.stack()].index[0]
                
                
                
                max_nodes.append([arc_node_mapping["arcID"][row_index], 
                                row["Pier Node"], 
                                DxV["Node"][max_value],
                                DxV["DxV"][max_value],
                                np.round(depth["Depth"][max_value],4), 
                                np.round(velocity["Velocity"][max_value],4)])
    my_bar.empty()
        
    max_nodes = pd.DataFrame(max_nodes, columns = ["Pier Arc ID", "Pier Node", "Model Node","DxV","Depth","Velocity"])
    
    return max_nodes



