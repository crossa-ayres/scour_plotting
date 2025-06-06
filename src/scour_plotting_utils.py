import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import os
import numpy as np
import streamlit as st
pd.options.mode.copy_on_write = True


def recurrence_txt():
    """
    Returns a list of flags used to identify the columns in the DataFrame.
    """
    flags_100yr = ['CS + LTD Depth (100-yr)', 'Local Scour Depth (100-yr)', 'Scour Datum Elev.', 'WSE 100yr','abut scour 100','100-Year Scour Design']
    flags_500yr = ['CS + LTD Depth (500-yr)', 'Local Scour Depth (500-yr)', 'Scour Datum Elev.', 'WSE 500yr','abut scour 500','500-Year Scour Check']
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
    bank_stations = bridge_data[['Channel Bank Sta.']]
    lateral_stability = bridge_data[['Laterally Stable Channel?']]
    lt_deg = bridge_data[['Long Term Deg']]
    abt_scour_elev = bridge_data[['abut scour 100', 'abut scour 500']]
    abut_stat = bridge_data[['Abt Toe Left Sta.','Abt Toe Right Sta.']]
    scour_data_df = bridge_data[['Bent ID','CS + LTD Depth (100-yr)','CS + LTD Depth (500-yr)','Scour Datum Elev.']]
    wse = bridge_data[['WSE 100yr','WSE 500yr']]
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
                                 'Local Scour Depth (500-yr)' ]]
    
    bridge_low_chord = bridge_data[['Bent CL Sta','Low Chord Elev']]
    bridge_low_chord = bridge_low_chord.dropna()
    bridge_high_chord = bridge_data[['Bent CL Sta','High Chord Elev']]
    bridge_high_chord = bridge_high_chord.dropna()
    ground_line = bridge_data[['Offset Station', 'Elev']]
    pier_data_df = pier_data_df.dropna()

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
            lt_deg, 
            abt_scour_elev, 
            abut_stat, wse]


def calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year):
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
    cs_ltd = year[0]
    local_scour = year[1]
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
    
    scour_data_array.append([pier_data['Bent CL Sta'] - 2*(scour_data_df[cs_ltd].values[0] - (scour_data_df[cs_ltd].values[0] - pier_data[local_scour])),
                                   left_station['lt_deg'].values[1]])
    
    scour_data_array.append([pier_data['Bent CL Sta'],
                                   (center_station['lt_deg'].values[1] - pier_data[local_scour])- scour_data_df[cs_ltd].values[0]])
    
    scour_data_array.append([pier_data['Bent CL Sta'] + 2*(scour_data_df[cs_ltd].values[0] - (scour_data_df[cs_ltd].values[0] - pier_data[local_scour])),
                                   right_station['lt_deg'].values[1]])
    
    
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

def generate_figure(pier_data_dict, 
                          individual_pier_ids,
                          bridge_low_chord, 
                          bridge_high_chord, 
                          ground_line,
                          scour_data_df,
                          bank_stations, 
                          lateral_stability,
                          lt_deg, 
                          abt_scour_elev, 
                          abut_stat, wse_data, 
                          year
                          ):
    
    """
    Generates a figure for scour data for a specific recurrence interval.
    Args:
        pier_data_dict (dict): Dictionary containing pier data.
        individual_pier_ids (list): List of individual pier IDs.
        bridge_low_chord (DataFrame): DataFrame containing low chord data.
        bridge_high_chord (DataFrame): DataFrame containing high chord data.
        ground_line (DataFrame): DataFrame containing ground line data.
        scour_data_df (DataFrame): DataFrame containing scour data.
        bank_stations (DataFrame): DataFrame containing bank station data.
        lateral_stability (DataFrame): DataFrame containing lateral stability data.
        lt_deg (DataFrame): DataFrame containing long term degradation data.
        abt_scour_elev (DataFrame): DataFrame containing abutment scour elevation data.
        abut_stat (DataFrame): DataFrame containing abutment station data.
        wse_data (DataFrame): DataFrame containing water surface elevation data.
        year (list): List containing recurrence interval data for the year.
    Returns:
        fig (Figure): The generated figure.
    """

    abut_scour_flag = year[4]
    cs_ltd = year[0]
    wse_flag = year[3]
    recurrence_title = year[-1]

    scour_data_array = []
    
    left_station = abut_stat['Abt Toe Left Sta.'].values[0]
    right_station = abut_stat['Abt Toe Right Sta.'].values[0]
    
    
    # Set the channel type based on the bank stations and abutment stations
    ground_line.loc[(ground_line['Offset Station'] > bank_stations['Channel Bank Sta.'].values[0]) & (ground_line['Offset Station'] < bank_stations['Channel Bank Sta.'].values[1]), "channel"] = "Channel"
    ground_line.loc[(ground_line['Offset Station'] < left_station) | (ground_line['Offset Station'] > right_station), "channel"] = "Abutment"
    ground_line = ground_line.assign(lt_deg = 0.0)
    ground_line = ground_line.assign(contract_scour = 0.0)
    ground_line = ground_line.assign(abut_scour = 0.0)

    # Update lt_deg, contract_scour, and abut_scour based on channel type
    # Assign initial values for lt_deg, contract_scour, and abut_scour
    # This is done to ensure that the lt_deg values are updated correctly
    for idx, row in ground_line.iterrows():
        if row['channel'] == "Abutment":
            ground_line.at[idx, 'abut_scour'] = abt_scour_elev[abut_scour_flag].values[0]
            ground_line.at[idx, 'contract_scour'] = np.nan
            ground_line.at[idx, 'lt_deg'] = abt_scour_elev[abut_scour_flag].values[0]
        elif row['channel'] == "Channel":
            
            ground_line.at[idx, 'lt_deg'] = row['Elev'] - lt_deg['Long Term Deg'].values[0] - scour_data_df[cs_ltd].values[0] 
            ground_line.at[idx, 'contract_scour'] = row['Elev'] - scour_data_df[cs_ltd].values[0] 
            ground_line.at[idx, 'abut_scour'] = np.nan
        else:
            ground_line.at[idx, 'lt_deg'] = row['Elev'] - scour_data_df[cs_ltd].values[0] 
            ground_line.at[idx, 'contract_scour'] = row['Elev'] - scour_data_df[cs_ltd].values[0] 
            ground_line.at[idx, 'abut_scour'] = row['Elev'] - scour_data_df[cs_ltd].values[0]
   

    cl_lsd = [[pier_data_dict[individual_pier_ids[0]]['Bent CL Sta'], (scour_data_df['Scour Datum Elev.'].values[0] - scour_data_df[cs_ltd].values[0])],
                    [pier_data_dict[individual_pier_ids[-1]]['Bent CL Sta'], (scour_data_df['Scour Datum Elev.'].values[0] - scour_data_df[cs_ltd].values[0])]]
    
    #local_instable = [[pier_data_dict[individual_pier_ids[0]]['Bent CL Sta'], (abut_scour_flag)],
    #                [pier_data_dict[individual_pier_ids[-1]]['Bent CL Sta'], (abut_scour_flag)]]
    
    contraction_instable = [[pier_data_dict[individual_pier_ids[0]]['Bent CL Sta'], (scour_data_df['Scour Datum Elev.'].values[0] - ground_line["contract_scour"].values[0])],
                    [pier_data_dict[individual_pier_ids[-1]]['Bent CL Sta'], (scour_data_df['Scour Datum Elev.'].values[0] - ground_line["contract_scour"].values[0])]]
    
    wse = [[pier_data_dict[individual_pier_ids[0]]['Bent CL Sta'], wse_data[wse_flag].values[0]],
           [pier_data_dict[individual_pier_ids[-1]]['Bent CL Sta'], wse_data[wse_flag].values[0]]]
                    
    fig, ax = plt.subplots()
    
    i=0
    scour_data_copy = []
    for pier_id in individual_pier_ids:
        # Calculate the plotting data for the pier
        pier_plotting_data_left, pier_plotting_data_right = calculate_pier_data(pier_data_dict,pier_id)
        # Plot the left and right sides of the pier
        ax.plot([x[0] for x in pier_plotting_data_left], [x[1] for x in pier_plotting_data_left], color='black',linewidth=1)
        ax.plot([x[0] for x in pier_plotting_data_right], [x[1] for x in pier_plotting_data_right], color='black',linewidth=1)
        # If the pier is not the first or last pier, calculate and plot the scour data
        if i > 0 and i < len(individual_pier_ids)-1:
            scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)
            scour_data_copy.append(scour_data_array)
        
            if i == 1:
                # Plot the scour data for the first pier (100 year), only add label for last iteration
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle=':',linewidth=2, label = "Local Scour (LS) at Pier")
            else:
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle=':',linewidth=2)
        i+=1
    
    for station in scour_data_copy:
        # Find the closest left and right stations in the ground line to the scour holes plotted at each pier
        # This is done to ensure that the scour holes are plotted at the correct locations on the ground line
        # and that the lt_deg values are updated correctly
        # Find the closest left and right stations in the ground line to the scour holes plotted at each pier
        left = min(ground_line['Offset Station'], key=lambda x: abs(x - station[0][0]))
        right = min(ground_line['Offset Station'], key=lambda x: abs(x - station[2][0]))
        # Get the index of the left and right stations in the ground line
        left_index = ground_line['Offset Station'][ground_line['Offset Station'] == left].index.tolist()
        right_index = ground_line['Offset Station'][ground_line['Offset Station'] == right].index.tolist()
        # Set the lt_deg values to NaN for the range between the left and right stations
        # This is done to ensure that the lt_deg values are updated correctly
        ground_line.loc[left_index[0]:right_index[0], ["contract_scour"]] = np.nan
        ground_line.loc[left_index[0]:right_index[0], ['lt_deg']] = np.nan
        ground_line.loc[left_index[0]:right_index[0], ["abut_scour"]] = np.nan
        # Replace the lt_deg, abutment scour, and contraction scour values at the left and right stations with the values from the scour holes
        ground_line.loc[left_index[0], ["lt_deg"]] = station[0][1]
        ground_line.loc[right_index[0], ["lt_deg"]] = station[2][1]
        ground_line.loc[left_index[0], ["abut_scour"]] = station[0][1]
        ground_line.loc[right_index[0], ["abut_scour"]] = station[2][1]
        ground_line.loc[left_index[0], ["contract_scour"]] = station[0][1]
        ground_line.loc[right_index[0], ["contract_scour"]] = station[2][1]
        
        


    
    if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
        ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300', label='CS + LTD')
        #ax.plot([x[0] for x in local_instable], [x[1] for x in local_instable], color='#0073CF', label='Local Scour')
        ax.plot([x[0] for x in contraction_instable], [x[1] for x in contraction_instable], color='#FCD450', label='Contraction Scour (CS)')
    else:
        ax.plot(ground_line['Offset Station'], ground_line['lt_deg'], color='#E98300', label='Total Scour (LTD + CS + LS)')
        ax.plot(ground_line['Offset Station'], ground_line["abut_scour"], color='#0073CF', label='Abutment Scour (AS)')
        ax.plot(ground_line['Offset Station'], ground_line["contract_scour"], color='#FCD450', label='Contraction Scour (CS)')

    
    ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green', label='Ground Line')
    
    ax.plot(bridge_low_chord['Bent CL Sta'], bridge_low_chord['Low Chord Elev'], color='black' )
    ax.plot(bridge_high_chord['Bent CL Sta'], bridge_high_chord['High Chord Elev'], color='black')
    
    
    
    ax.plot([x[0] for x in wse], [x[1] for x in wse], color='blue',linewidth=2,linestyle=':', label='WSE')
    
    plt.axvline(x=0, color='grey',linewidth=.5)
    y_axis_range = ax.get_ylim()
    y_ticks = range(int(y_axis_range[0]),int(y_axis_range[1]),1)

    # Add horizontal ticks
    for y in y_ticks:
        plt.hlines(y=y,xmin = -5, xmax = 0, color='grey',linewidth=1)
    plt.xlabel('Station [ft]', weight='bold')
    plt.ylabel('Elevation [ft-NAVD88]', weight='bold')    
    plt.title(recurrence_title, weight='bold')
    
    

    loc = plticker.MultipleLocator(base=10)
    loc_major = plticker.MultipleLocator(base=50)
    ax.xaxis.set_minor_locator(loc)
    ax.xaxis.set_major_locator(loc_major)
    plt.grid(axis='x')
    plt.grid(axis='y')
    ax.legend()
    plt.gcf().set_size_inches(17, 11)
    
    return fig
    

def generate_summary_figure(pier_data_dict, 
                          individual_pier_ids,
                          bridge_low_chord, 
                          bridge_high_chord, 
                          ground_line,
                          scour_data_df,
                          bank_stations, 
                          lateral_stability,
                          lt_deg, 
                          abt_scour_elev, 
                          abut_stat, wse_data, 
                          recurrence_data
                         ):
    
    """
    Generates a summary figure for scour data across multiple recurrence intervals.
    Args:
        pier_data_dict (dict): Dictionary containing pier data.
        individual_pier_ids (list): List of individual pier IDs.
        bridge_low_chord (DataFrame): DataFrame containing low chord data.
        bridge_high_chord (DataFrame): DataFrame containing high chord data.
        ground_line (DataFrame): DataFrame containing ground line data.
        scour_data_df (DataFrame): DataFrame containing scour data.
        bank_stations (DataFrame): DataFrame containing bank station data.
        lateral_stability (DataFrame): DataFrame containing lateral stability data.
        lt_deg (DataFrame): DataFrame containing long term degradation data.
        abt_scour_elev (DataFrame): DataFrame containing abutment scour elevation data.
        abut_stat (DataFrame): DataFrame containing abutment station data.
        wse_data (DataFrame): DataFrame containing water surface elevation data.
        recurrence_data (list): List of recurrence data for different years.
    Returns:
        fig (Figure): The generated summary figure.
    """
    fig, ax = plt.subplots()
    iteration = 0
    for year in recurrence_data:
        
        abut_scour_flag = year[4]
        cs_ltd = year[0]
        scour_data_array = []
        
        left_station = abut_stat['Abt Toe Left Sta.'].values[0]
        right_station = abut_stat['Abt Toe Right Sta.'].values[0]

        ground_line.loc[(ground_line['Offset Station'] > bank_stations['Channel Bank Sta.'].values[0]) & (ground_line['Offset Station'] < bank_stations['Channel Bank Sta.'].values[1]), "channel"] = "Channel"
        ground_line.loc[(ground_line['Offset Station'] < left_station) | (ground_line['Offset Station'] > right_station), "channel"] = "Abutment"
        
        # Assign initial values for lt_deg, contract_scour, and abut_scour
        ground_line = ground_line.assign(lt_deg = 0.0)
        ground_line = ground_line.assign(contract_scour = 0.0)
        ground_line = ground_line.assign(abut_scour = 0.0)

        # Update lt_deg, contract_scour, and abut_scour based on channel type
        for idx, row in ground_line.iterrows():
            if row['channel'] == "Abutment":
                ground_line.at[idx, 'abut_scour'] = abt_scour_elev[abut_scour_flag].values[0]
                ground_line.at[idx, 'contract_scour'] = np.nan
                ground_line.at[idx, 'lt_deg'] = abt_scour_elev[abut_scour_flag].values[0]
            elif row['channel'] == "Channel":
                
                ground_line.at[idx, 'lt_deg'] = row['Elev'] - lt_deg['Long Term Deg'].values[0] - scour_data_df[cs_ltd].values[0] 
                ground_line.at[idx, 'contract_scour'] = row['Elev'] - scour_data_df[cs_ltd].values[0] 
                ground_line.at[idx, 'abut_scour'] = np.nan
            else:
                ground_line.at[idx, 'lt_deg'] = row['Elev'] - scour_data_df[cs_ltd].values[0] 
                ground_line.at[idx, 'contract_scour'] = row['Elev'] - scour_data_df[cs_ltd].values[0] 
                ground_line.at[idx, 'abut_scour'] = row['Elev'] - scour_data_df[cs_ltd].values[0]
        

        cl_lsd = [[pier_data_dict[individual_pier_ids[0]]['Bent CL Sta'], (scour_data_df['Scour Datum Elev.'].values[0] - scour_data_df[cs_ltd].values[0])],
                        [pier_data_dict[individual_pier_ids[-1]]['Bent CL Sta'], (scour_data_df['Scour Datum Elev.'].values[0] - scour_data_df[cs_ltd].values[0])]]
        
    
        i=0
        scour_data_copy = []
        
        for pier_id in individual_pier_ids:
            # Calculate the plotting data for the pier
            pier_plotting_data_left, pier_plotting_data_right = calculate_pier_data(pier_data_dict,pier_id)
            scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)
            # Plot the left and right sides of the pier
            ax.plot([x[0] for x in pier_plotting_data_left], [x[1] for x in pier_plotting_data_left], color='black',linewidth=1)
            ax.plot([x[0] for x in pier_plotting_data_right], [x[1] for x in pier_plotting_data_right], color='black',linewidth=1)

            if i > 0 and i < len(individual_pier_ids)-1:
                # Calculate scour data for the pier and append to the list
                # This is done to ensure that the scour holes are plotted at the correct locations on the ground line
                scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)
                scour_data_copy.append(scour_data_array)
            
                if iteration == 0:
                    # Plot the scour data for the first iteration (100 year)
                    ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='grey',linewidth=2)
                else:
                    # Plot the scour data for the second iteration (500 year)
                    ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle=':',linewidth=2)
            i+=1


        for station in scour_data_copy:
            # Find the closest left and right stations in the ground line to the scour holes plotted at each pier
            left = min(ground_line['Offset Station'], key=lambda x: abs(x - station[0][0]))
            right = min(ground_line['Offset Station'], key=lambda x: abs(x - station[2][0]))
            # Get the index of the left and right stations in the ground line
            # This is done to ensure that the scour holes are plotted at the correct locations on the ground line
            # and that the lt_deg values are updated correctly
            left_index = ground_line['Offset Station'][ground_line['Offset Station'] == left].index.tolist()
            right_index = ground_line['Offset Station'][ground_line['Offset Station'] == right].index.tolist()
            # Set the lt_deg values to NaN for the range between the left and right stations
            ground_line.loc[left_index[0]:right_index[0], ['lt_deg']] = np.nan
            # Replace the lt_deg values at the left and right stations with the values from the scour holes
            ground_line.loc[left_index[0], ["lt_deg"]] = station[0][1]
            ground_line.loc[right_index[0], ["lt_deg"]] = station[2][1]
           

        if iteration == 0:
            #plot total scour for 100 year
            ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green', label='Ground Line')
            ax.plot(bridge_low_chord['Bent CL Sta'], bridge_low_chord['Low Chord Elev'], color='black' )
            ax.plot(bridge_high_chord['Bent CL Sta'], bridge_high_chord['High Chord Elev'], color='black')
            
            if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
                ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300')
            else:
                ax.plot(ground_line['Offset Station'], ground_line['lt_deg'],color='grey',linewidth=2, label = "Total Scour - 100YR")
        else:
            #plot total scour for 500 year
            if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
                ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300')
            else:
                ax.plot(ground_line['Offset Station'], ground_line['lt_deg'], color='red',linestyle=':',linewidth=2, label = "Total Scour - 500YR")
              
        iteration += 1


    plt.axvline(x=0, color='grey',linewidth=.5)
    y_axis_range = ax.get_ylim()
    y_ticks = range(int(y_axis_range[0]),int(y_axis_range[1]),1)

    # Add horizontal ticks
    for y in y_ticks:
        plt.hlines(y=y,xmin = -5, xmax = 0, color='grey',linewidth=1)
    plt.xlabel('Station [ft]', weight='bold')
    plt.ylabel('Elevation [ft-NAVD88]', weight='bold')    
    plt.title("Scour Summary", weight='bold')
    
    

    loc = plticker.MultipleLocator(base=10)
    loc_major = plticker.MultipleLocator(base=50)
    ax.xaxis.set_minor_locator(loc)
    ax.xaxis.set_major_locator(loc_major)
    plt.grid(axis='x')
    plt.grid(axis='y')
    ax.legend()
    plt.gcf().set_size_inches(17, 11)

    return fig
    