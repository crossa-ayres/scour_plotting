import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.patches import Polygon
import os
import numpy as np
import streamlit as st
pd.options.mode.copy_on_write = True


def recurrence_txt():
    """
    Returns a list of flags used to identify the columns in the DataFrame.
    """
    flags_100yr = ['CS + LTD Depth (100-yr)', 'Local Scour Depth (100-yr)', 'Scour Datum Elev.', 'WSE 100yr','abut scour 100','100-Year Scour Design', 'Scour Elevation 100yr']
    flags_500yr = ['CS + LTD Depth (500-yr)', 'Local Scour Depth (500-yr)', 'Scour Datum Elev.', 'WSE 500yr','abut scour 500','500-Year Scour Check', 'Scour Elevation 500yr']
    return [flags_100yr, flags_500yr]

def generate_pier_scour_df(bridge_data):
    """
    Generates a dictionary of pier data and other related data from the bridge data DataFrame.
    Args:
        bridge_data (DataFrame): DataFrame containing bridge data.
    Returns:
        list: A list containing the pier data dictionary, 
            individual pier IDs, 
            low chord data, 
            high chord data, 
            ground line data, 
            scour data DataFrame, 
            bank stations, 
            lateral stability, 
            long term degradation, 
            abutment scour elevation, 
            abutment station data, 
            and water surface elevation data.
    """
    
    pier_data_dict = {}
    individual_pier_ids = []
    events = bridge_data[['scour check title',	'scour design interval']]
    events = events.dropna()
    bank_stations = bridge_data[['Channel Bank Sta.']]
    lateral_stability = bridge_data[['Laterally Stable Channel?']]
    #lt_deg = bridge_data[['Long Term Deg']]
    #abt_scour_elev = bridge_data[['abut scour 100', 'abut scour 500']]
    abut_stat = bridge_data[['Abt Toe Left Sta.','Abt Toe Right Sta.']]
    abutment_data = bridge_data[['Offset Station','SDAB','SCAB']]
    abutment_data = abutment_data.dropna()
    scour_data_df = bridge_data[['Bent ID','CS + LTD Depth (100-yr)','CS + LTD Depth (500-yr)','Scour Datum Elev.']]
    #wse = bridge_data[['WSE 100yr','WSE 500yr']]
    wse = bridge_data[['WSE 100yr Station','WSE 100yr','WSE 500yr Station','WSE 500yr']]
    LTD = bridge_data[['LTD_Station','LTD_Elev']]
    contraction_scour = bridge_data[['CS_Design_Station','CS_Design_Elev','CS_Check_Station','CS_Check_Elev']]
    scour_data_df = scour_data_df.dropna()
    pier_data_df = bridge_data[['Bent ID',
                                'Bridge Thickness', 
                                'Pier Stem Top Width', 
                                'Pier Stem Bottom Width',
                                'Footing Cap Width',
                                'Footing Width',
                                'Footing Cap Height',
                                'Footing Height',
                                'Bent CL Sta',
                                'Bottom of Footing Elev',
                                'Low Chord Elev',
                                'High Chord Elev',
                                'Local Scour Depth (100-yr)',
                                'Local Scour Depth (500-yr)',
                                'Scour Elevation 100yr',
                                'Scour Elevation 500yr']]
    pier_data_df['Bent ID'] = pier_data_df['Bent ID'].drop_duplicates()
    target_row = pier_data_df.iloc[1]
    pier_data_df = pd.concat([pier_data_df.drop(pier_data_df.index[1]), pd.DataFrame([target_row])]).reset_index(drop=True)
    
    
    bridge_low_chord = bridge_data[['Bent CL Sta','Low Chord Elev']]
    target_row = bridge_low_chord.iloc[1]
    bridge_low_chord= pd.concat([bridge_low_chord.drop(bridge_low_chord.index[1]), pd.DataFrame([target_row])]).reset_index(drop=True)
    bridge_low_chord = bridge_low_chord.dropna()
    bridge_high_chord = bridge_data[['Bent CL Sta','High Chord Elev']]
    target_row = bridge_high_chord.iloc[1]
    bridge_high_chord= pd.concat([bridge_high_chord.drop(bridge_high_chord.index[1]), pd.DataFrame([target_row])]).reset_index(drop=True)
    
    bridge_high_chord = bridge_high_chord.dropna()
    
    ground_line = bridge_data[['Offset Station', 'Elev']]
    ground_line = ground_line.dropna()
    #pier_data_df = pier_data_df.dropna()
    
    

    for index, row in pier_data_df.iterrows():
        pier_data_dict[row['Bent ID']] = row
        individual_pier_ids.append(row['Bent ID'])
    return [pier_data_dict, 
            individual_pier_ids,
            bridge_low_chord, 
            bridge_high_chord, 
            ground_line, 
            scour_data_df, 
            bank_stations, 
            lateral_stability,
             wse,events,abutment_data,abut_stat,LTD,contraction_scour]

def calculate_scour_data(pier_data_dict, pier_id, scour_data_df,ground_line, year):
    """
    Calculates the scour data for a given pier based on its ID and the year.
    Args:
        pier_data_dict (dict): Dictionary containing pier data.
        pier_id (str): ID of the pier.
        scour_data_df (DataFrame): DataFrame containing scour data.
        ground_line (DataFrame): DataFrame containing ground line data.
        year (list): List containing recurrence interval data for the year.
    Returns:
        list: List containing the calculated scour data for the pier.
    """
    try:
        cs_ltd = year[0] # this is just the "CS + LTD Depth (100-year)" string
        local_scour = year[1] # this is just "Local Scour Dept (100-year) or 500-year" string
        scour_data_array = []
        pier_data = pier_data_dict[pier_id]
        
        # calculate the left, right, and center stations based on the pier data and the local scour data
        # The left and right stations are calculated as 2 times the local scour depth away from the pier center line station
        # The center station is the pier center line station
        # The left and right stations are used to find the closest stations in the ground line to the scour holes plotted at each pier
        left = pier_data['Bent CL Sta'] - 2*(scour_data_df[cs_ltd].values[0] - (scour_data_df[cs_ltd].values[0] - pier_data[local_scour]))
        right = pier_data['Bent CL Sta'] + 2*(scour_data_df[cs_ltd].values[0] - (scour_data_df[cs_ltd].values[0] - pier_data[local_scour]))
        center = pier_data['Bent CL Sta']
        left_station = ground_line.iloc[(ground_line['Offset Station']-left).abs().argsort()[:2]]
        right_station = ground_line.iloc[(ground_line['Offset Station']-right).abs().argsort()[:2]]
        center_station = ground_line.iloc[(ground_line['Offset Station']-center).abs().argsort()[:2]]

        # Append left, center, and right station-elevation pairs
        scour_data_array.append([pier_data['Bent CL Sta'] - 2*(scour_data_df[cs_ltd].values[0] - (scour_data_df[cs_ltd].values[0] - pier_data[local_scour])),
                                    left_station['lt_deg'].values[1]])
        scour_data_array.append([pier_data['Bent CL Sta'], pier_data[year[6]]])                            
        scour_data_array.append([pier_data['Bent CL Sta'] + 2*(scour_data_df[cs_ltd].values[0] - (scour_data_df[cs_ltd].values[0] - pier_data[local_scour])),
                                    right_station['lt_deg'].values[1]])
    except Exception as e:
        pass
    return scour_data_array

def calculate_pier_data(pier_data_dict,pier_id):
    """
    Calculates the plotting data for a pier based on its ID.
    Args:
        pier_data_dict (dict): Dictionary containing pier data.
        pier_id (str): ID of the pier.
    Returns:
        tuple: Two lists containing the plotting data for the left and right sides of the pier.
    """
    # Initialize lists to hold the plotting data for the left and right sides of the pier
    pier_plotting_data_left = []
    pier_plotting_data_right = []
    pier_data = pier_data_dict[pier_id]
    #x1, y1
    # Calculate the plotting data for the left and right sides of the pier by taking the pier data and calculating the coordinates based on the pier stem top width, bottom width, footing cap width, and footing width.
    pier_plotting_data_left.append([pier_data['Bent CL Sta']-(pier_data['Pier Stem Top Width']/2),pier_data['Low Chord Elev']])
    #x2, y2
    pier_plotting_data_left.append([pier_data['Bent CL Sta']-(pier_data['Pier Stem Bottom Width']/2),(pier_data['Bottom of Footing Elev'] + pier_data['Footing Cap Height'] + pier_data['Footing Height'])])
    #x3, y3
    pier_plotting_data_left.append([pier_data['Bent CL Sta']-pier_data['Footing Cap Width']/2,(pier_data['Bottom of Footing Elev'] + pier_data['Footing Cap Height'] + pier_data['Footing Height'])])
    #x4, y4
    pier_plotting_data_left.append([pier_data['Bent CL Sta']-pier_data['Footing Cap Width']/2,(pier_data['Bottom of Footing Elev']+pier_data['Footing Height'])])
    #x5, y5
    pier_plotting_data_left.append([pier_data['Bent CL Sta']-(pier_data['Footing Width']/2),(pier_data['Bottom of Footing Elev']+pier_data['Footing Height'])])
    #x6, y6
    pier_plotting_data_left.append([pier_data['Bent CL Sta']-(pier_data['Footing Width']/2),pier_data['Bottom of Footing Elev']])
    #x7, y7
    pier_plotting_data_left.append([pier_data['Bent CL Sta'],pier_data['Bottom of Footing Elev']])


    #x1, y1
    pier_plotting_data_right.append([pier_data['Bent CL Sta']+(pier_data['Pier Stem Top Width']/2),pier_data['Low Chord Elev']])
    #x2, y2
    pier_plotting_data_right.append([pier_data['Bent CL Sta']+(pier_data['Pier Stem Bottom Width']/2),(pier_data['Bottom of Footing Elev'] + pier_data['Footing Cap Height'] + pier_data['Footing Height'])])
    #x3, y3
    pier_plotting_data_right.append([pier_data['Bent CL Sta']+pier_data['Footing Cap Width']/2,(pier_data['Bottom of Footing Elev'] + pier_data['Footing Cap Height'] + pier_data['Footing Height'])])
    #x4, y4
    pier_plotting_data_right.append([pier_data['Bent CL Sta']+pier_data['Footing Cap Width']/2,(pier_data['Bottom of Footing Elev']+pier_data['Footing Height'])])
    #x5, y5
    pier_plotting_data_right.append([pier_data['Bent CL Sta']+(pier_data['Footing Width']/2),(pier_data['Bottom of Footing Elev']+pier_data['Footing Height'])])
    #x6, y6
    pier_plotting_data_right.append([pier_data['Bent CL Sta']+(pier_data['Footing Width']/2),pier_data['Bottom of Footing Elev']])
    #x7, y7
    pier_plotting_data_right.append([pier_data['Bent CL Sta'],pier_data['Bottom of Footing Elev']])

    return pier_plotting_data_left, pier_plotting_data_right
