import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.patches import Polygon
import os
import numpy as np
import streamlit as st
from .data_processing_utils import calculate_pier_data, calculate_scour_data
pd.options.mode.copy_on_write = True






def generate_figure(pier_data_dict, 
                          individual_pier_ids,
                          bridge_low_chord, 
                          bridge_high_chord, 
                          ground_line,
                          scour_data_df,
                          bank_stations, 
                          lateral_stability,
                          abut_stat, wse_station, wse_elev, 
                          year,event,abutment_data,recur,LTD,contract_sta,contract_elev,pile_data,all_pile_elements
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

    #abut_scour_flag = year[4]
    #cs_ltd = year[0]
    #wse_flag = year[3]
    #recurrence_title = year[5]

    scour_data_array = []
    
    #left_station = abut_stat['Abt Toe Left Sta.'].values[0]
    #right_station = abut_stat['Abt Toe Right Sta.'].values[0]
    
    """
    # Set the channel type based on the bank stations and abutment stations
    ground_line.loc[(ground_line['Offset Station'] > bank_stations['Channel Bank Sta.'].values[0]) & (ground_line['Offset Station'] < bank_stations['Channel Bank Sta.'].values[1]), "channel"] = "Channel"
    ground_line.loc[(ground_line['Offset Station'] < left_station) , "channel"] = "Abutment_Left"
    ground_line.loc[(ground_line['Offset Station'] > right_station), "channel"] = "Abutment_Right"
    ground_line = ground_line.assign(lt_deg = 0.0)
    ground_line = ground_line.assign(contract_scour = 0.0)
    ground_line = ground_line.assign(abut_scour = 0.0)

    # Update lt_deg, contract_scour, and abut_scour based on channel type
    # Assign initial values for lt_deg, contract_scour, and abut_scour
    # This is done to ensure that the lt_deg values are updated correctly
    for idx, row in ground_line.iterrows():
        if row['channel'] == "Abutment_Left":
            ground_line.at[idx, 'abut_scour'] = pier_data_dict[individual_pier_ids[0]][year[6]]
            ground_line.at[idx, 'contract_scour'] = np.nan
            ground_line.at[idx, 'lt_deg'] = pier_data_dict[individual_pier_ids[0]][year[6]]
        elif row['channel'] == "Abutment_Right":
            ground_line.at[idx, 'abut_scour'] = pier_data_dict[individual_pier_ids[-1]][year[6]]
            ground_line.at[idx, 'contract_scour'] = np.nan
            ground_line.at[idx, 'lt_deg'] = pier_data_dict[individual_pier_ids[-1]][year[6]]
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
    """         
    fig, ax = plt.subplots()
    
    i=0
    scour_data_copy = []
    label_placement = 50
    
    for pier_id in all_pile_elements["Bent ID"].tolist():
        #find the closes elevation in 
     
        
        try:
            pier_plotting_data_left, pier_plotting_data_right = calculate_pier_data(pier_data_dict,pier_id)
            # Plot the left and right sides of the pier
            ax.plot([x[0] for x in pier_plotting_data_left], [x[1] for x in pier_plotting_data_left], color='black',linewidth=1)
            ax.plot([x[0] for x in pier_plotting_data_right], [x[1] for x in pier_plotting_data_right], color='black',linewidth=1)
            # If the pier is not the first or last pier, calculate and plot the scour data
            #try:
            #if i > 0 and i < len(individual_pier_ids)-1:
            scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)
            
            scour_data_copy.append(scour_data_array)
        
            if i == 2:
                ground_line_elev = ground_line.iloc[(ground_line['Offset Station'] - pier_data_dict[pier_id]['Bent CL Sta']).abs().argsort()[:1]]
                Initial_depth = ground_line_elev["Elev"].values[0] - pier_data_dict[pier_id]["pile_elev_left_l"]
               
                remaining_depth = pier_data_dict[pier_id]["Scour Elevation 500yr"]-pier_data_dict[pier_id]["pile_elev_left_l"]
                
                percent_remaining = np.round((remaining_depth/Initial_depth)*100,0).astype(int)
                
                # Plot the scour data for the first pier (100 year), only add label for last iteration
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle='--',linewidth=1.5, label = "Local Scour (LS) at Pier")
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement, f'{pier_id}', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-6, f'{percent_remaining}%', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-8, 'Remaining', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-10, 'Embedment', ha='center')
            elif i < len(all_pile_elements)-1 and i > 1:
                #find the ground line elevation at the pier center line station
                ground_line_elev = ground_line.iloc[(ground_line['Offset Station'] - pier_data_dict[pier_id]['Bent CL Sta']).abs().argsort()[:1]]
                Initial_depth = ground_line_elev["Elev"].values[0] -pier_data_dict[pier_id]["pile_elev_left_l"]
                remaining_depth = pier_data_dict[pier_id]["Scour Elevation 500yr"]-pier_data_dict[pier_id]["pile_elev_left_l"]
                
                percent_remaining = np.round((remaining_depth/Initial_depth)*100,0).astype(int)
                
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle='--',linewidth=1.5)
                #.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement, f'{pier_id}', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-6, f'{percent_remaining}%', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-8, 'Remaining', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-10, 'Embedment', ha='center')
            #else:
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement, f'{pier_id}', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-6, f'{percent_remaining}%', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-8, 'Remaining', ha='center')
                #ax.text(scour_data_array[1][0], pier_data_dict[pier_id]["Bottom of Footing Elev"]-label_placement-10, 'Embedment', ha='center')
            i+=1
        except Exception as e:
            i+=1
            pass
            
    
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
        
        #use the index values calculated above to set the elevations in abutment_data to nan between the left and right stations
        abutment_data[1][left_index[0]:right_index[0]] = np.nan
        abutment_data[1][left_index[0]] = station[0][1]
        abutment_data[1][right_index[0]] = station[2][1]
    
    ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green', label='Ground Line')
    if recur==0:
       
        gl = ground_line['Offset Station']
        
        ax.plot(gl[:len(abutment_data[1])], abutment_data[1], color='grey', linewidth=1.5,linestyle='--', label=f'Total Scour: {event}')
     
        contract_sta = contract_sta.dropna()
        sta = []
        sta = [float(x) for x in contract_sta]
        contract_elev = contract_elev.dropna()
        elev = []
        elev = [float(x) for x in contract_elev]

       
        #line2, = ax.plot(sta,elev, color='red', linewidth=2, label=f'Contraction Scour - {event}')
        #line2.set_dashes([2, 2, 2, 2,10,2])
        #line2.set_dash_capstyle('round')
    else:
        gl = ground_line['Offset Station']
        ax.plot(gl[:len(abutment_data[1])], abutment_data[1], color='grey', linewidth=1.5,linestyle='--', label=f'Total Scour: {event}')
        
        contract_sta = contract_sta.dropna()
        contract_elev = contract_elev.dropna()
        #line2, = ax.plot([x for x in contract_sta], [x for x in contract_elev], color='red', linewidth=1, label=f'Contraction Scour - {event}')
        #line2.set_dashes([2, 2, 2, 2,2,2,10,2])
        #line2.set_dash_capstyle('round')


    for index, row in pile_data.iterrows():
        ax.plot([row['pile_sta_left_l'], row['pile_sta_left_h']], [row['pile_elev_left_l'], row['pile_elev_left_h']], color='black', linewidth=1.5)
        ax.plot([row['pile_sta_right_l'], row['pile_sta_right_h']], [row['pile_elev_right_l'], row['pile_elev_right_h']], color='black', linewidth=1.5)


    ax.plot( wse_station, wse_elev, color='blue',linewidth=1,linestyle='--', label=f'WSE - {event}')
    station_marker = 50
    #ax.plot(ground_line['Offset Station'][station_marker]+8, wse_elev[0]+1, color='blue', marker = "v", markersize=9)
    #plt.hlines(y=wse_elev[0]-.45,xmin = ground_line['Offset Station'][station_marker]-5, xmax = ground_line['Offset Station'][station_marker]+5, color='blue',linewidth=1)
    #plt.hlines(y=wse_elev[0]-.8,xmin = ground_line['Offset Station'][station_marker]-3, xmax = ground_line['Offset Station'][station_marker]+3, color='blue',linewidth=1)
    #plt.hlines(y=wse_elev[0]-1.15,xmin = ground_line['Offset Station'][station_marker]-1, xmax = ground_line['Offset Station'][station_marker]+1, color='blue',linewidth=1)
    
    line3, = ax.plot(LTD['LTD_Station'], LTD['LTD_Elev'], color='black', linewidth=1, label=f'LTD')
    line3.set_dashes([2, 2,10,2])
    line3.set_dash_capstyle('round')

    
    line1 = list(zip(bridge_low_chord['Bent CL Sta'],bridge_low_chord['Low Chord Elev']))
    line2 = list(zip(bridge_high_chord['Bent CL Sta'],bridge_high_chord['High Chord Elev']))
    polygon_points = line1 + line2[::-1]  # Reverse line2 to close the polygon

    # Create the polygon
    polygon = Polygon(polygon_points, closed=True, edgecolor='black', facecolor='lightgrey', hatch='///', alpha=0.8)
    ax.add_patch(polygon)

    
    
    plt.axvline(x=0, color='grey',linewidth=.5)
    y_axis_range = ax.get_ylim()
    y_ticks = range(int(y_axis_range[0]),int(y_axis_range[1]),1)

    # Add horizontal ticks
    for y in y_ticks:
        if y % 5 == 0:
            plt.hlines(y=y,xmin = -8, xmax = -2, color='black',linewidth=1.2)
        else:
            plt.hlines(y=y,xmin = -5, xmax = -2, color='grey',linewidth=1)
    plt.xlabel('Station [ft]', weight='bold')
    plt.ylabel('Elevation [ft-NAVD88]', weight='bold')    
    plt.title(event, weight='bold')
    
    

    loc = plticker.MultipleLocator(base=10)
    loc_major = plticker.MultipleLocator(base=50)
    ax.xaxis.set_minor_locator(loc)
    ax.xaxis.set_major_locator(loc_major)
    plt.grid(axis='x')
    #minor grid lines on y axis

    
    plt.grid(axis='y')
    ax.legend()
    plt.gcf().set_size_inches(17, 10.5)
    plt.tight_layout()
    
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
        
        #abut_scour_flag = year[4]
        #cs_ltd = year[0]
        scour_data_array = []
        
        #left_station = abut_stat['Abt Toe Left Sta.'].values[0]
        #right_station = abut_stat['Abt Toe Right Sta.'].values[0]
        """
        ground_line.loc[(ground_line['Offset Station'] > bank_stations['Channel Bank Sta.'].values[0]) & (ground_line['Offset Station'] < bank_stations['Channel Bank Sta.'].values[1]), "channel"] = "Channel"
        ground_line.loc[(ground_line['Offset Station'] < left_station) , "channel"] = "Abutment_Left"
        ground_line.loc[(ground_line['Offset Station'] > right_station), "channel"] = "Abutment_Right"
        
        # Assign initial values for lt_deg, contract_scour, and abut_scour
        ground_line = ground_line.assign(lt_deg = 0.0)
        ground_line = ground_line.assign(contract_scour = 0.0)
        ground_line = ground_line.assign(abut_scour = 0.0)

        # Update lt_deg, contract_scour, and abut_scour based on channel type
        for idx, row in ground_line.iterrows():
            if row['channel'] == "Abutment_Left":
                ground_line.at[idx, 'abut_scour'] = pier_data_dict[individual_pier_ids[0]][year[6]]
                ground_line.at[idx, 'contract_scour'] = np.nan
                ground_line.at[idx, 'lt_deg'] = pier_data_dict[individual_pier_ids[0]][year[6]]
            elif row['channel'] == "Abutment_Right":
                ground_line.at[idx, 'abut_scour'] = pier_data_dict[individual_pier_ids[-1]][year[6]]
                ground_line.at[idx, 'contract_scour'] = np.nan
                ground_line.at[idx, 'lt_deg'] = pier_data_dict[individual_pier_ids[-1]][year[6]]
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
        
        """
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
            try:
                # Find the closest left and right stations in the ground line to the scour holes plotted at each pier
                left = min(ground_line['Offset Station'], key=lambda x: abs(x - station[0][0]))
                right = min(ground_line['Offset Station'], key=lambda x: abs(x - station[2][0]))
                # Get the index of the left and right stations in the ground line
                # This is done to ensure that the scour holes are plotted at the correct locations on the ground line
                # and that the lt_deg values are updated correctly
                left_index = ground_line['Offset Station'][ground_line['Offset Station'] == left].index.tolist()
                right_index = ground_line['Offset Station'][ground_line['Offset Station'] == right].index.tolist()
                # Set the lt_deg values to NaN for the range between the left and right stations
                #ground_line.loc[left_index[0]:right_index[0], ['lt_deg']] = np.nan
                # Replace the lt_deg values at the left and right stations with the values from the scour holes
                #ground_line.loc[left_index[0], ["lt_deg"]] = station[0][1]
                #ground_line.loc[right_index[0], ["lt_deg"]] = station[2][1]
            except Exception as e:
                pass
           
        """
        if iteration == 0:
            #plot total scour for 100 year
            ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green', label='Ground Line')
       
            
           # if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
           #     ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300')
           # else:
           #     ax.plot(ground_line['Offset Station'], ground_line['lt_deg'],color='grey',linewidth=2, label = "Total Scour - 100YR")
        else:
            #plot total scour for 500 year
            #if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
            #    ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300')
            #else:
            ax.plot(ground_line['Offset Station'], ground_line['lt_deg'], color='red',linestyle=':',linewidth=2, label = "Total Scour - 500YR")
              
        iteration += 1
        """
    if recur==0:
        st.write(ground_line['Offset Station'])
        st.write(abutment_data[1])
        gl = ground_line['Offset Station']
        
        ax.plot(gl[:len(abutment_data[1])], abutment_data[1], color='#2E3033', linewidth=1,linestyle='-', label=f'Total Scour - {event}')
     
        contract_sta = contract_sta.dropna()
        sta = []
        sta = [float(x) for x in contract_sta]
        contract_elev = contract_elev.dropna()
        elev = []
        elev = [float(x) for x in contract_elev]

        st.write(elev)
        line2, = ax.plot(sta,elev, color='red', linewidth=1, label=f'Contraction Scour - {event}')
        line2.set_dashes([2, 2, 2, 2,10,2])
        line2.set_dash_capstyle('round')
    else:
        gl = ground_line['Offset Station']
        ax.plot(gl[:len(abutment_data[1])], abutment_data[1], color='#2E3033', linewidth=1,linestyle='--', label=f'Total Scour - {event}')
        
        contract_sta = contract_sta.dropna()
        contract_elev = contract_elev.dropna()
        line2, = ax.plot([x for x in contract_sta], [x for x in contract_elev], color='red', linewidth=1, label=f'Contraction Scour - {event}')
        line2.set_dashes([2, 2, 2, 2,2,2,10,2])
        line2.set_dash_capstyle('round')

    ax.plot( wse_station, wse_elev, color='blue',linewidth=2,linestyle=':', label=f'WSE - {event}')
    line3, = ax.plot(LTD['LTD_Station'], LTD['LTD_Elev'], color='black', linewidth=1, label=f'LTD')
    line3.set_dashes([2, 2,10,2])
    line3.set_dash_capstyle('round')

    ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green', label='Ground Line')
    line1 = list(zip(bridge_low_chord['Bent CL Sta'],bridge_low_chord['Low Chord Elev']))
    line2 = list(zip(bridge_high_chord['Bent CL Sta'],bridge_high_chord['High Chord Elev']))
    polygon_points = line1 + line2[::-1]  # Reverse line2 to close the polygon

    # Create the polygon
    polygon = Polygon(polygon_points, closed=True, edgecolor='black', facecolor='lightgrey', hatch='///', alpha=0.8)
    ax.add_patch(polygon)
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
    