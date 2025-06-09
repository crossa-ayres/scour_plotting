import h5py
import csv
import pandas as pd
import streamlit as st



def write_csv(data, filename):
    with open(filename, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Node", "Value"])
        for key, value in data.items():
            writer.writerow([key, value])

def extract_data(depth_file:str,depth_file_name,velocity_file: str, nodes: list) -> tuple:
    
    """
    Extracts and processes depth and velocity data from HDF5 files for specified nodes.

    Parameters:
        depth_file (str): Path to the HDF5 file containing water depth data.
        velocity_file (str): Path to the HDF5 file containing velocity magnitude data.
        nodes (list): List of node indices for which data is to be extracted.
    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - depth_data_dict (pd.DataFrame): DataFrame with columns "Node" and "Depth", 
                where "Depth" is the maximum water depth for each node.
            - velocity_data_dict (pd.DataFrame): DataFrame with columns "Node" and "Velocity", 
                where "Velocity" is the maximum velocity magnitude for each node.
    """

    depth_data_dict = []
    velocity_data_dict = []
    for index in range(4):
        try:
            file_reference = depth_file_name.split("_")[index]
            with h5py.File(depth_file, 'r') as file:
                a_group_key = list(file.keys())[0]
                # Getting the data  [0]
                data = list(file[a_group_key][file_reference]['Water_Depth_ft']['Values'])
                for j in nodes:
                    depth_array = []
                    for i in range(len(data)):
                        depth_array.append(float(data[i][int(j)-1]))
                    depth_data_dict.append([j,max(depth_array)])
                depth_data_dict = pd.DataFrame(depth_data_dict,columns = ["Node","Depth"])
        except Exception as e:
            pass
        
        
    for index in range(4):
        try:
            file_reference = depth_file_name.split("_")[index]
            with h5py.File(velocity_file, 'r') as file:
                a_group_key = list(file.keys())[0]
                
                # Getting the data  [0]
                data = list(file[a_group_key][file_reference]['Vel_Mag_ft_p_s']['Values'])
            
                for j in nodes:
                    velocity_array = []
                    for i in range(len(data)):
                        velocity_array.append(float(data[i][int(j)-1]))
                    
                    velocity_data_dict.append([j,max(velocity_array)])
                velocity_data_dict = pd.DataFrame(velocity_data_dict,columns = ["Node","Velocity"])
        except Exception as e:
            pass


    return depth_data_dict, velocity_data_dict




