import pandas as pd 
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.patches import Polygon
import os
import numpy as np
import streamlit as st
from .data_processing_utils import calculate_pier_data, calculate_scour_data, adjust_scourCone,clean_contractionScour,clean_LTD
from scipy.interpolate import make_splrep
pd.options.mode.copy_on_write = True






def generate_figure(pier_data_dict, 
                          bridge_low_chord, 
                          bridge_high_chord, 
                          ground_line,
                          scour_data_df, 
                          lateral_stability,
                           wse_station, wse_elev, 
                          event,recur,
                          LTD,contract_elev,
                          pile_data,all_pile_elements,
                          pier_scourCone_shift,line_smoothing_coeff,
                          left_tieIn_shift,right_tieIn_shift,
                          left_abut_shift,right_abut_shift,
                          scourCone_elev_shift,
                          left_abut_match,right_abut_match,lb_cw_mc
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

 

    scour_data_array = []
    fig, ax = plt.subplots()
    i=0
    scour_data_design = []
    scour_data_check = []
    
    for pier_id in all_pile_elements["Bent ID"].tolist():

        pier_plotting_data_left, pier_plotting_data_right,cse_data = calculate_pier_data(pier_data_dict,pier_id)
        #drop nan values from cse data
        cse_data = [x for x in cse_data[0] if not np.isnan(x).any()]
        
        # Plot the left and right sides of the pier
        ax.plot([x[0] for x in pier_plotting_data_left], [x[1] for x in pier_plotting_data_left], color='black',linewidth=1)
        ax.plot([x[0] for x in pier_plotting_data_right], [x[1] for x in pier_plotting_data_right], color='black',linewidth=1)
       
        scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, recur,pier_scourCone_shift,scourCone_elev_shift,lateral_stability)
        
        if scour_data_array:
            if recur == 0:
                scour_data_design.append(scour_data_array)
            if recur == 1:
                scour_data_check.append(scour_data_array)
            if i == 2:
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='black',linestyle='--',linewidth=1, label = "Local Scour (LS) at Pier")
                
            elif i < len(all_pile_elements)-1 and i > 1:
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='black',linestyle='--',linewidth=1)
                
            i+=1
        else:
            i+=1
          
            
        
    x_new = np.linspace(ground_line['Offset Station'].min(), ground_line['Offset Station'].max(), int(len(ground_line['Offset Station'])))
    

    interpolated_elev = make_splrep(ground_line['Offset Station'], ground_line['Elev'], s=line_smoothing_coeff)(x_new)
    #try:
    #    interpolated_elev[left_index[0]+left_tieIn_shift:right_index[0]-right_tieIn_shift] = np.nan
    #except Exception as e:
    #    pass
    ax.plot(x_new,interpolated_elev, color='black', linewidth=0.75,label='Ground Line')
    


    if recur==0:
       
   
        if lateral_stability == 'Yes':

            
            x_new = np.linspace(ground_line['Offset Station'].min(), ground_line['Offset Station'].max(), int(len(ground_line['Offset Station'])))
            interpolated_elev = make_splrep(ground_line['Offset Station'], ground_line['Elev'], s=line_smoothing_coeff)(x_new)
            total_scour = interpolated_elev-pier_data_dict[all_pile_elements['Bent ID'][0]]['Local Scour Depth (100-yr)'] 
            ltd_elev_shift =  interpolated_elev-(LTD['thalweg_elev'].values[0]-LTD['LTD_Elev'].values[0])
            if lb_cw_mc == "LB":
                contraction_elevation_arr = interpolated_elev-LTD['cs_lb_mc'][recur]
            elif lb_cw_mc == "CW":
                contraction_elevation_arr = interpolated_elev-LTD['cs_cw_mc'][recur]
            
            left_idx = np.abs(x_new - int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])).argmin()
            right_idx = np.abs(x_new - int(pier_data_dict[all_pile_elements['Bent ID'][1]]['Bent CL Sta'])).argmin()
            total_scour = np.array([x_new,total_scour])
            total_scour[1][:left_idx+left_abut_match+left_abut_shift] = pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 100yr']
            total_scour[1][right_idx+right_abut_match+right_abut_shift:] =pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 100yr']
            total_scour[0][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[1][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[0][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour[1][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour = total_scour[:, ~np.isnan(total_scour).any(axis=0)]

            
            scour_array_plot = adjust_scourCone(total_scour[0],total_scour[1],scour_data_design,left_tieIn_shift,right_tieIn_shift)
            ax.plot(scour_array_plot[0], scour_array_plot[1], color='grey', linewidth=1,linestyle='--', label=f'Total Scour: {event}')


            contract_array_plot = adjust_scourCone(x_new,contraction_elevation_arr ,scour_data_design,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)
          
            line2, = ax.plot(contract_array_plot[0],contract_array_plot[1], color='red', linewidth=1, label=f'Contraction Scour - {event}')
            line2.set_dashes([2, 2, 2, 2,10,2])
            line2.set_dash_capstyle('round')

            ltd_array_plot = np.array([x_new,ltd_elev_shift])
            ltd_array_plot  = clean_LTD(ltd_array_plot,left_idx,right_idx)
           
            line3, = ax.plot(ltd_array_plot[0],ltd_array_plot[1], color='black', linewidth=1, label=f'LTD')
            line3.set_dashes([2, 2,10,2])
            line3.set_dash_capstyle('round')

        
        elif lateral_stability == 'No':
            total_scour_arr = []
            if lb_cw_mc == "LB":
                contract_scour_depth = LTD['thalweg_elev'].values[0] -LTD['cs_lb_mc'][recur]
                
            elif lb_cw_mc == "CW":
                contract_scour_depth = LTD['thalweg_elev'].values[0] -LTD['cs_cw_mc'][recur]
                
            
            contraction_station = np.linspace(ground_line['Offset Station'].min(), ground_line['Offset Station'].max(), int(len(ground_line['Offset Station'])))
            contract_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            total_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            left_idx = np.abs(contraction_station - int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])).argmin()
            right_idx = np.abs(contraction_station - int(pier_data_dict[all_pile_elements['Bent ID'][1]]['Bent CL Sta'])).argmin()
            
            total_scour_plot = np.array([contraction_station,total_scour_arr])
            total_scour_plot[1][:(left_idx+left_abut_match)] = [pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 100yr'] for i in range(len(ground_line['Offset Station'][:(left_idx+left_abut_match)]))]
            total_scour_plot[1][(right_idx+right_abut_match):] =[pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 100yr'] for i in range(len(total_scour_plot[0])-(right_idx+right_abut_match))]
            total_scour_plot[1][left_idx+left_abut_shift:right_idx+right_abut_shift] = [contract_scour_depth for i in range((right_idx+right_abut_shift)-(left_idx+left_abut_shift))]
            

            total_scour_plot[1][left_idx+left_abut_match:left_idx+left_abut_shift] = np.nan
            total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift] =np.nan
            total_scour_plot[1][right_idx+right_abut_shift:right_idx+right_abut_match] = np.nan
            total_scour_plot[0][right_idx+right_abut_shift:right_idx+right_abut_match] =np.nan
            total_scour_plot = total_scour_plot[:, ~np.isnan(total_scour_plot).any(axis=0)]

            scour_array_plot = adjust_scourCone(total_scour_plot[0],total_scour_plot[1],scour_data_design,left_tieIn_shift,right_tieIn_shift)
            ax.plot(scour_array_plot[0],scour_array_plot[1], color='grey', linewidth=1.5,linestyle='--', label=f'Total Scour: {event}')
        
           
            
            contract_array_plot = adjust_scourCone(contraction_station,contract_scour_arr,scour_data_design,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)
         
            line2, = ax.plot(contract_array_plot[0],contract_array_plot[1], color='red', linewidth=1, label=f'Contraction Scour - {event}')
            line2.set_dashes([2, 2, 2, 2,10,2])
            line2.set_dash_capstyle('round')

            line3, = ax.plot(LTD['LTD_Station'], LTD['LTD_Elev'], color='black', linewidth=1, label=f'LTD')
            line3.set_dashes([2, 2,10,2])
            line3.set_dash_capstyle('round')
    elif recur == 1:
       
        if lateral_stability == 'Yes':

            x_new = np.linspace(ground_line['Offset Station'].min(), ground_line['Offset Station'].max(), int(len(ground_line['Offset Station'])))
            interpolated_elev = make_splrep(ground_line['Offset Station'], ground_line['Elev'], s=line_smoothing_coeff)(x_new)
            
            total_scour = interpolated_elev-pier_data_dict[all_pile_elements['Bent ID'][0]]['Local Scour Depth (500-yr)'] 
            #find the index of the value in x_new closest to int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])
            left_idx = np.abs(x_new - int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])).argmin()
            right_idx = np.abs(x_new - int(pier_data_dict[all_pile_elements['Bent ID'][1]]['Bent CL Sta'])).argmin()
            total_scour = np.array([x_new,total_scour])
            total_scour[1][:left_idx+left_abut_match+left_abut_shift] = pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 500yr']
            total_scour[1][right_idx+right_abut_match+right_abut_shift:] =pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 500yr']
            total_scour[0][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[1][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[0][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour[1][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour = total_scour[:, ~np.isnan(total_scour).any(axis=0)]

            
            scour_array_plot = adjust_scourCone(total_scour[0],total_scour[1],scour_data_check,left_tieIn_shift,right_tieIn_shift)


            ax.plot(scour_array_plot[0], scour_array_plot[1], color='grey', linewidth=1.5,linestyle='--', label=f'Total Scour: {event}')

            ltd_elev_shift =  interpolated_elev-(LTD['thalweg_elev'].values[0]-LTD['LTD_Elev'].values[0])
            
            
            if lb_cw_mc == "LB":
                contraction_elevation_arr = interpolated_elev-LTD['cs_lb_mc'][recur]
                
            elif lb_cw_mc == "CW":
                contraction_elevation_arr = interpolated_elev-LTD['cs_cw_mc'][recur]
            contract_array_plot = adjust_scourCone(x_new,contraction_elevation_arr ,scour_data_check,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)
          
            line2, = ax.plot(contract_array_plot[0],contract_array_plot[1], color='red', linewidth=1, label=f'Contraction Scour - {event}')
            line2.set_dashes([2, 2, 2, 2,10,2])
            line2.set_dash_capstyle('round')

    
            ltd_array_plot = np.array([x_new,ltd_elev_shift])
            ltd_array_plot  = clean_LTD(ltd_array_plot,left_idx,right_idx)
           
            line3, = ax.plot(ltd_array_plot[0],ltd_array_plot[1], color='black', linewidth=1, label=f'LTD')
            line3.set_dashes([2, 2,10,2])
            line3.set_dash_capstyle('round')

        elif lateral_stability == 'No':

            total_scour_arr = []
            if lb_cw_mc == "LB":
                contract_scour_depth = LTD['thalweg_elev'].values[0] -LTD['cs_lb_mc'][recur]
                
            elif lb_cw_mc == "CW":
                contract_scour_depth = LTD['thalweg_elev'].values[0] -LTD['cs_cw_mc'][recur]
            contraction_station = np.linspace(ground_line['Offset Station'].min(), ground_line['Offset Station'].max(), int(len(ground_line['Offset Station'])))
            total_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            contract_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            left_idx = np.abs(contraction_station - int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])).argmin()
            right_idx = np.abs(contraction_station - int(pier_data_dict[all_pile_elements['Bent ID'][1]]['Bent CL Sta'])).argmin()
            
            total_scour_plot = np.array([contraction_station,total_scour_arr])
            total_scour_plot[1][:(left_idx+left_abut_shift)] = [pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 500yr'] for i in range(len(ground_line['Offset Station'][:(left_idx+left_abut_shift)]))]
            total_scour_plot[1][(right_idx+right_abut_shift):] =[pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 500yr'] for i in range(len(total_scour_plot[0])-(right_idx+right_abut_shift))]
            total_scour_plot[1][left_idx+left_abut_shift:right_idx+right_abut_shift] = [contract_scour_depth for i in range((right_idx+right_abut_shift)-(left_idx+left_abut_shift))]
            total_scour_plot[1][left_idx+left_abut_match:left_idx+left_abut_shift] = np.nan
            total_scour_plot[0][left_idx+left_abut_match:left_idx+left_abut_shift] =np.nan
            total_scour_plot[1][right_idx+right_abut_shift:right_idx+right_abut_match] = np.nan
            total_scour_plot[0][right_idx+right_abut_shift:right_idx+right_abut_match] =np.nan
            total_scour_plot = total_scour_plot[:, ~np.isnan(total_scour_plot).any(axis=0)]
            scour_array_plot = adjust_scourCone(total_scour_plot[0],total_scour_plot[1],scour_data_check,left_tieIn_shift,right_tieIn_shift)
            ax.plot(scour_array_plot[0],scour_array_plot[1], color='grey', linewidth=1,linestyle='--', label=f'Total Scour: {event}')
        

        
            contract_array_plot = adjust_scourCone(contraction_station,contract_scour_arr,scour_data_check,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)
           
            line2, = ax.plot(contract_array_plot[0],contract_array_plot[1], color='red', linewidth=1, label=f'Contraction Scour - {event}')
            line2.set_dashes([2, 2, 2, 2,10,2])
            line2.set_dash_capstyle('round')

            line3, = ax.plot(LTD['LTD_Station'], LTD['LTD_Elev'], color='black', linewidth=1, label=f'LTD')
            line3.set_dashes([2, 2,10,2])
            line3.set_dash_capstyle('round')

    for index, row in pile_data.iterrows():
        ax.plot([row['pile_sta_left_l'], row['pile_sta_left_h']], [row['pile_elev_left_l'], row['pile_elev_left_h']], color='black', linewidth=1.5)
        ax.plot([row['pile_sta_right_l'], row['pile_sta_right_h']], [row['pile_elev_right_l'], row['pile_elev_right_h']], color='black', linewidth=1.5)


    ax.plot( wse_station, wse_elev, color='blue',linewidth=1,linestyle='--', label=f'WSE - {event}')
    #find the station in ground_line['Offset Station'] that is closest to the middle of the wse_station range 
    
    station_marker = ground_line['Offset Station'].sub(wse_station.mean()).abs().idxmin()-6
    ax.plot(ground_line['Offset Station'][station_marker], wse_elev[0]+0.5, color='black', marker = "v", markersize=6)
    plt.hlines(y=wse_elev[0]-.25,xmin = ground_line['Offset Station'][station_marker]-2, xmax = ground_line['Offset Station'][station_marker]+2, color='black',linewidth=1)
    plt.hlines(y=wse_elev[0]-.6,xmin = ground_line['Offset Station'][station_marker]-1, xmax = ground_line['Offset Station'][station_marker]+1, color='black',linewidth=1)
    plt.hlines(y=wse_elev[0]-.95,xmin = ground_line['Offset Station'][station_marker]-0.5, xmax = ground_line['Offset Station'][station_marker]+0.5, color='black',linewidth=1)
    
    line1 = list(zip(bridge_low_chord['Bent CL Sta'],bridge_low_chord['Low Chord Elev']))
    line2 = list(zip(bridge_high_chord['Bent CL Sta'],bridge_high_chord['High Chord Elev']))
    polygon_points = line1 + line2[::-1]  # Reverse line2 to close the polygon

    # Create the polygon
    polygon = Polygon(polygon_points, closed=True, edgecolor='black', facecolor='grey', hatch='///', alpha=0.8)
    ax.add_patch(polygon)

    plt.axvline(x=0, color='grey',linewidth=.5)
    y_axis_range = ax.get_ylim()
    y_ticks = range(int(y_axis_range[0]),int(y_axis_range[1]),1)

    # Add horizontal ticks
    for y in y_ticks:
        if y % 5 == 0:
            plt.hlines(y=y,xmin = -3, xmax = -1, color='black',linewidth=1)
        else:
            plt.hlines(y=y,xmin = -2, xmax = -1, color='grey',linewidth=0.5)
    plt.xlabel('Station [ft]')
    plt.ylabel('Elevation [ft-NAVD88]')    
    plt.title(event)
    
    

    loc = plticker.MultipleLocator(base=10)
    loc_major = plticker.MultipleLocator(base=50)
    ax.xaxis.set_minor_locator(loc)
    ax.xaxis.set_major_locator(loc_major)
    plt.grid(axis='x', color='grey', linestyle='-', linewidth=0.5)
    #minor grid lines on y axis

    
    plt.grid(axis='y', color='grey', linestyle=':', linewidth=0.5)
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='gray')
    ax.legend(fancybox=True, framealpha=0.5,loc='lower left')
    plt.gcf().set_size_inches(15, 5)
    plt.tight_layout()
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    return fig
   
@st.cache_resource
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
    