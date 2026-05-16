import pandas as pd 
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.patches import Polygon
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
    try:
        piles = bridge_data[["pile_sta_right_h",	"pile_elev_right_h",	"pile_sta_right_l",	"pile_elev_right_l",	"pile_sta_left_h",	"pile_elev_left_h",	"pile_sta_left_l",	"pile_elev_left_l"]]
    except:
        pass
  
   
    scour_data_df = bridge_data[['Bent ID','Scour Elevation 100yr','Scour Elevation 500yr',"Scour Depth 100yr",	"Scour Depth 500yr", 'Scour Datum Elev.']]
    scour_data_df = scour_data_df[2:]
    
 
    wse = bridge_data[['WSE 100yr Station','WSE 100yr','WSE 500yr Station','WSE 500yr']]
    LTD = bridge_data[['LTD_Station','LTD_Elev','thalweg_elev','CS + LTD Depth (100-yr)','CS + LTD Depth (500-yr)','cs_lb_mc','cs_cw_mc']]
    contraction_scour = bridge_data[['CS_Design_Station','CS_Design_Elev','CS_Check_Station','CS_Check_Elev']]
    
    
    pier_data_df = bridge_data[['Bent ID',
                                 'Abutment Scour Datum',
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
                                'Scour Elevation 500yr',
                                "pile_elev_left_l",
                                "cse"]]
    
    pier_data_df['Bent ID'] = pier_data_df['Bent ID'].drop_duplicates()
    target_row = pier_data_df.iloc[1]
    pier_data_df = pd.concat([pier_data_df.drop(pier_data_df.index[1]), pd.DataFrame([target_row])]).reset_index(drop=True)
    all_pile_elements = bridge_data[['Bent ID']]
    
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
  
    
    

    for index, row in pier_data_df.iterrows():
        pier_data_dict[row['Bent ID']] = row
        individual_pier_ids.append(row['Bent ID'])
    individual_pier_ids = individual_pier_ids[1:10]
    
    individual_pier_ids = [l for l in individual_pier_ids if str(l) != 'nan']
    
    return [pier_data_dict, 
            bridge_low_chord, 
            bridge_high_chord, 
            ground_line, 
            scour_data_df,  
            wse,
            events,
            LTD,
            contraction_scour, 
            piles,
            all_pile_elements]
   

def draw_scourCone_laterallyStable(pier_data, scour_data_df,ground_line, pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation):
    left = pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) - pier_data['Pier Stem Bottom Width']
    right = pier_data['Bent CL Sta'] + pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) + pier_data['Pier Stem Bottom Width']
    
    #center = pier_data['Bent CL Sta']
    left_station = ground_line.iloc[(ground_line['Offset Station']-left).abs().argsort()[:2]]
    right_station = ground_line.iloc[(ground_line['Offset Station']-right).abs().argsort()[:2]]
    

    # Append left, center, and right station-elevation pairs
    scour_data_array.append([pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                left_station['Elev'].values[1]+scourCone_elev_shift])
    scour_data_array.append([pier_data['Bent CL Sta']-pier_data['Footing Cap Width']/2-.2, scour_data_df[recurrance_elevation].values[0]])         
    scour_data_array.append([pier_data['Bent CL Sta']+pier_data['Footing Cap Width']/2+.2, scour_data_df[recurrance_elevation].values[0]])                      
    scour_data_array.append([pier_data['Bent CL Sta'] + pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                right_station['Elev'].values[1]+scourCone_elev_shift])
    return scour_data_array

def draw_scourCone_laterallyUnstable(pier_data, scour_data_df,ground_line, pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation):
    
    left = pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) - pier_data['Pier Stem Bottom Width']
    right = pier_data['Bent CL Sta'] + pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) + pier_data['Pier Stem Bottom Width']
    
   
    left_station = ground_line.iloc[(ground_line['Offset Station']-left).abs().argsort()[:2]]
    right_station = ground_line.iloc[(ground_line['Offset Station']-right).abs().argsort()[:2]]
    

   
    scour_data_array.append([pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                left_station['Elev'].values[1]+scourCone_elev_shift])
    scour_data_array.append([pier_data['Bent CL Sta']-pier_data['Footing Cap Width']/2-.2, scour_data_df[recurrance_elevation].values[0]])         
    scour_data_array.append([pier_data['Bent CL Sta']+pier_data['Footing Cap Width']/2+.2, scour_data_df[recurrance_elevation].values[0]])                      
    scour_data_array.append([pier_data['Bent CL Sta'] + pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                left_station['Elev'].values[1]+scourCone_elev_shift])
    
    return scour_data_array
    

def calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, recur,pier_scourCone_shift,scourCone_elev_shift,lateral_stability):
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
    #try:
    
    scour_data_array = []
    pier_data = pier_data_dict[pier_id]
    scour_data_df = scour_data_df[scour_data_df['Bent ID'] == pier_id]
    if scour_data_df.empty:
        pass
    else:
        if recur == 0:
            if lateral_stability == "Yes":
                recurrance_depth = "Scour Depth 100yr"
                recurrance_elevation = "Scour Elevation 100yr"

                scour_data_array=draw_scourCone_laterallyStable(pier_data, scour_data_df,ground_line,pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation)
            
                return scour_data_array
            elif lateral_stability == "No":
                recurrance_depth = "Scour Depth 100yr"
                recurrance_elevation = "Scour Elevation 100yr"

                scour_data_array=draw_scourCone_laterallyUnstable(pier_data, scour_data_df,ground_line,pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation)
                return scour_data_array
        if recur == 1:
            if lateral_stability == "Yes":
                recurrance_depth = "Scour Depth 500yr"
                recurrance_elevation = "Scour Elevation 500yr"
                scour_data_array=draw_scourCone_laterallyStable(pier_data, scour_data_df,ground_line,pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation)

                return scour_data_array
            
            elif lateral_stability == "No":

                recurrance_depth = "Scour Depth 500yr"
                recurrance_elevation = "Scour Elevation 500yr"

                scour_data_array=draw_scourCone_laterallyUnstable(pier_data, scour_data_df,ground_line, pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation)
            
                return scour_data_array
        
            
def adjust_scourCone(x_new,total_scour_plot,scour_data_copy,left_tieIn_shift,right_tieIn_shift):
    scour_array_plot = np.array([x_new,total_scour_plot])
    for station in scour_data_copy:
        x_new_df = pd.DataFrame(x_new, columns=['Offset Station'])
        left = min(x_new_df['Offset Station'], key=lambda x: abs(x - station[0][0]))
        right = min(x_new_df['Offset Station'], key=lambda x: abs(x - station[3][0]))
        left_index = x_new_df['Offset Station'][x_new_df['Offset Station'] == left].index.tolist()
        right_index = x_new_df['Offset Station'][x_new_df['Offset Station'] == right].index.tolist()
        scour_array_plot[0][left_index[0]+left_tieIn_shift:right_index[0]+right_tieIn_shift] = np.nan
        scour_array_plot[1][left_index[0]+left_tieIn_shift:right_index[0]+right_tieIn_shift] = np.nan
        
    return scour_array_plot


def draw_totalScour(contraction_station,total_scour_arr,left_idx,left_abut_shift,pier_data_dict,all_pile_elements,ground_line,right_idx,right_abut_shift,contract_elev,left_abut_match,right_abut_match,recur,lateral_stability):
    if recur == 0:
        if lateral_stability == "Yes":
            total_scour_plot = np.array([contraction_station,total_scour_arr])
            total_scour_plot[1][:(left_idx+left_abut_shift)] = [pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 100yr'] for i in range(len(ground_line['Offset Station'][:(left_idx+left_abut_shift)]))]
            total_scour_plot[1][(right_idx+right_abut_shift):] =[pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 100yr'] for i in range(len(total_scour_plot[0])-(right_idx+right_abut_shift))]
            total_scour_plot[1][left_idx+left_abut_shift:right_idx+right_abut_shift] = [contract_elev[0] for i in range((right_idx+right_abut_shift)-(left_idx+left_abut_shift))]
            total_scour_plot[1][left_idx+left_abut_match:left_idx+left_abut_shift] = np.nan
            total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift] =np.nan
            
            total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] =np.nan
            total_scour_plot[1][right_idx+right_abut_shift:right_idx+right_abut_match] = np.nan
            total_scour_plot[0][right_idx+right_abut_shift:right_idx+right_abut_match] =np.nan
            total_scour_plot = total_scour_plot[:, ~np.isnan(total_scour_plot).any(axis=0)]
            return total_scour_plot
        elif lateral_stability == "No":
            total_scour_plot = np.array([contraction_station,total_scour_arr])
            total_scour_plot[1][:(left_idx+left_abut_shift)] = [pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 100yr'] for i in range(len(ground_line['Offset Station'][:(left_idx+left_abut_shift)]))]
            total_scour_plot[1][(right_idx+right_abut_shift):] =[pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 100yr'] for i in range(len(total_scour_plot[0])-(right_idx+right_abut_shift))]
            total_scour_plot[1][left_idx+left_abut_shift:right_idx+right_abut_shift] = [contract_elev[0] for i in range((right_idx+right_abut_shift)-(left_idx+left_abut_shift))]
            total_scour_plot[1][left_idx+left_abut_match:left_idx+left_abut_shift] = np.nan
            total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift] =np.nan
       
            total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] =np.nan
            total_scour_plot[1][right_idx+right_abut_shift:right_idx+right_abut_match] = np.nan
            total_scour_plot[0][right_idx+right_abut_shift:right_idx+right_abut_match] =np.nan
            total_scour_plot = total_scour_plot[:, ~np.isnan(total_scour_plot).any(axis=0)]
            return total_scour_plot
    if recur == 1:
        total_scour_plot = np.array([contraction_station,total_scour_arr])
        total_scour_plot[1][:(left_idx+left_abut_shift)] = [pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 500yr'] for i in range(len(ground_line['Offset Station'][:(left_idx+left_abut_shift)]))]
        total_scour_plot[1][(right_idx+right_abut_shift):] =[pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 500yr'] for i in range(len(total_scour_plot[0])-(right_idx+right_abut_shift))]
        total_scour_plot[1][left_idx+left_abut_shift:right_idx+right_abut_shift] = [contract_elev[0] for i in range((right_idx+right_abut_shift)-(left_idx+left_abut_shift))]

        total_scour_plot[1][left_idx+left_abut_match:left_idx+left_abut_shift] = np.nan
        total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift] =np.nan
        total_scour_plot[1][right_idx+right_abut_shift:right_idx+right_abut_match] = np.nan
        total_scour_plot[0][right_idx+right_abut_shift:right_idx+right_abut_match] =np.nan
        total_scour_plot = total_scour_plot[:, ~np.isnan(total_scour_plot).any(axis=0)]
        return total_scour_plot
def clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match):
    contract_array_plot[0][:left_idx+left_abut_shift+left_abut_match] = np.nan
    contract_array_plot[1][:left_idx+left_abut_shift+left_abut_match] = np.nan
    contract_array_plot[0][right_idx+right_abut_match+right_abut_shift:] = np.nan
    contract_array_plot[1][right_idx+right_abut_match+right_abut_shift:] = np.nan

    return contract_array_plot

def clean_LTD(ltd_array_plot,left_idx,right_idx):
    ltd_array_plot[0][:left_idx] = np.nan
    ltd_array_plot[1][:left_idx] = np.nan
    ltd_array_plot[0][right_idx:] = np.nan
    ltd_array_plot[1][right_idx:] = np.nan
    ltd_array_plot = ltd_array_plot[:, ~np.isnan(ltd_array_plot).any(axis=0)]

    return ltd_array_plot

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
    cse_data = []
    
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
    cse_data.append([pier_data['Bent CL Sta'], pier_data['cse']])

    return pier_plotting_data_left, pier_plotting_data_right,cse_data
