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
    events = bridge_data[['scour check title',	
                          'scour design interval']]
    events = events.dropna()
    try:
        piles = bridge_data[["pile_sta_right_h",
                             "pile_elev_right_h",
                             "pile_sta_right_l",
                             "pile_elev_right_l",
                             "pile_sta_left_h",	
                             "pile_elev_left_h",
                             "pile_sta_left_l",	
                             "pile_elev_left_l"]]
    except:
        pass
    scour_data_df = bridge_data[['Bent ID',
                                 'Scour Elevation 100yr',
                                 'Scour Elevation 500yr',
                                 "Scour Depth 100yr",
                                 "Scour Depth 500yr"]]
    
    scour_data_df = scour_data_df[2:]
    wse = bridge_data[['WSE 100yr Station',
                       'WSE 100yr',
                       'WSE 500yr Station',
                       'WSE 500yr']]
    
    contraction_data = bridge_data[['Thawleg Elevation',
                       'LTD Depth',
                       'CS + LTD Depth (100-yr)',
                       'CS + LTD Depth (500-yr)',
                       'CS Live Bed Main Channel - Depth',
                       'CS Clear Water Main Channel - Depth']]
    
    
    
    pier_data_df = bridge_data[['Bent ID',
                                'Bent CL Sta',
                                'Scour Elevation 100yr',
                                'Scour Elevation 500yr',
                                "cse",
                                'Bridge Thickness', 
                                'Pier Stem Top Width', 
                                'Pier Stem Bottom Width',
                                'Footing Cap Width',
                                'Footing Width',
                                'Footing Cap Height',
                                'Footing Height',
                                'Bottom of Footing Elev',
                                'Low Chord Elev',
                                'High Chord Elev',
                                ]]
    
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
       
    
    return [pier_data_dict, 
            bridge_low_chord, 
            bridge_high_chord, 
            ground_line, 
            scour_data_df,  
            wse,
            events,
            contraction_data,
            piles,
            all_pile_elements]



def create_Mainfigure(main_dict, 
                      event,
                      all_pile_elements,
                      pier_data_dict,
                      pile_data,
                      wse_station, 
                      wse_elev,
                      ground_line,
                      bridge_low_chord,
                      bridge_high_chord,
                      contraction_data,
                      fig_width,
                      fig_height):
    fig, ax = plt.subplots()
    i=0
    ground_line_interpolated = main_dict[event]["ground_line"]
    ax.plot(ground_line_interpolated[0][0], ground_line_interpolated[0][1], color='brown', label = "Ground Line")
    #points at the Bent CL Sta for element labels using the bridge high coord elevation as the y
    for pile_id in all_pile_elements["Bent ID"].tolist():
       
        pier_data = pier_data_dict[pile_id]
        
        ax.text(pier_data['Bent CL Sta'], pier_data['High Chord Elev']+1, f'{pile_id}', ha='center', va='bottom', fontsize=10)
    
    cse_data = []
    
    for pier_id in all_pile_elements["Bent ID"].tolist():
        pier_plotting_data_left, pier_plotting_data_right,cse = calculate_pier_data(pier_data_dict, pier_id,cse_data)
        
        ax.plot(*zip(*pier_plotting_data_left), color='black')
        ax.plot(*zip(*pier_plotting_data_right), color='black')
        scour_data_array=main_dict[event]["scour_data"][pier_id]
        
        if pier_id:
            try:
                line, = ax.plot(*zip(*scour_data_array), color='black', linewidth=1.25, label=f'Local Scour (LS) At Pier - {pier_id}')
                line.set_dashes([2, 2, 10, 2])
                line.set_dash_capstyle('round')
            except:
                pass

    #plot cse data as points
  
    
    scour_array_plot = main_dict[event]["total_scour"]
    contract_array_plot = main_dict[event]["contraction_scour"]
    ltd_array_plot = main_dict[event]["ltd"]
    
    
    #plot scour array
    line1, = ax.plot(scour_array_plot[0][0],scour_array_plot[0][1], color='grey', linewidth=1.25, label=f'Total Scour - {event}')
    line1.set_dashes([2, 2, 10, 2])
    line1.set_dash_capstyle('round')


    line2, = ax.plot(contract_array_plot[0][0],contract_array_plot[0][1], color='red', linewidth=1.25, label=f'Contraction Scour - {event}')
    line2.set_dashes([2, 2, 2, 2,10,2])
    line2.set_dash_capstyle('round')
    try:
        if contraction_data['LTD Depth'].values[0] != 0:
            line3, = ax.plot(ltd_array_plot[0][0],ltd_array_plot[0][1], color='black', linewidth=1.25, label=f'LTD')
            line3.set_dashes([2,10,8, 2,10,2])
            line3.set_dash_capstyle('round')
    except:
        pass
        


    for index, row in pile_data.iterrows():
        ax.plot([row['pile_sta_left_l'], row['pile_sta_left_h']], [row['pile_elev_left_l'], row['pile_elev_left_h']], color='black', linewidth=1.5)
        ax.plot([row['pile_sta_right_l'], row['pile_sta_right_h']], [row['pile_elev_right_l'], row['pile_elev_right_h']], color='black', linewidth=1.5)
    
    ax.plot( wse_station, wse_elev, color='blue',linewidth=1,linestyle='--', label=f'WSE - {event}')
    station_marker = ground_line['Offset Station'].sub(wse_station.mean()).abs().idxmin()-6
    ax.plot(ground_line['Offset Station'][station_marker], wse_elev.values[0]+0.5, color='black', marker = "v", markersize=6)
    plt.hlines(y=wse_elev.values[0]-.25,xmin = ground_line['Offset Station'][station_marker]-2, xmax = ground_line['Offset Station'][station_marker]+2, color='black',linewidth=1)
    plt.hlines(y=wse_elev.values[0]-.6,xmin = ground_line['Offset Station'][station_marker]-1, xmax = ground_line['Offset Station'][station_marker]+1, color='black',linewidth=1)
    plt.hlines(y=wse_elev.values[0]-.95,xmin = ground_line['Offset Station'][station_marker]-0.5, xmax = ground_line['Offset Station'][station_marker]+0.5, color='black',linewidth=1)
    
    st.write([x[0] for x in cse_data], [x[1] for x in cse_data])
    ax.scatter([float(x[0]) for x in cse_data],[float(x[1]) for x in cse_data], color='black', marker='o', label=f'CSE')
   
    
 
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
    plt.gcf().set_size_inches(fig_width, fig_height)
    plt.tight_layout()
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    return fig


def calc_scourCondition_stable(cs_condition_mc,interpolated_elev,contraction_data,recur):
    if cs_condition_mc == "LB":

        total_scour = interpolated_elev-contraction_data['CS Live Bed Main Channel - Depth'][recur]

        contraction_elevation_arr = interpolated_elev-contraction_data['CS Live Bed Main Channel - Depth'][recur]

    elif cs_condition_mc == "CW":

        contraction_elevation_arr = interpolated_elev-contraction_data['CS Clear Water Main Channel - Depth'][recur]

        total_scour = interpolated_elev-contraction_data['CS Clear Water Main Channel - Depth'][recur]

    return total_scour, contraction_elevation_arr

def calc_scourCondition_unstable(cs_condition_mc,contraction_data,recur):
    if cs_condition_mc == "LB":
        contract_scour_depth = contraction_data['Thawleg Elevation'].values[0] -contraction_data['CS Live Bed Main Channel - Depth'][recur]
                
    elif cs_condition_mc == "CW":
        contract_scour_depth = contraction_data['Thawleg Elevation'].values[0] -contraction_data['CS Clear Water Main Channel - Depth'][recur]

    return contract_scour_depth

def draw_scourCone_laterallyStable(pier_data, scour_data_df,ground_line, pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation):
    left = pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) - pier_data['Pier Stem Bottom Width']
    right = pier_data['Bent CL Sta'] + pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) + pier_data['Pier Stem Bottom Width']
    
    #center = pier_data['Bent CL Sta']
    left_station = ground_line.iloc[(ground_line['Offset Station']-left).abs().argsort()[:2]]
    right_station = ground_line.iloc[(ground_line['Offset Station']-right).abs().argsort()[:2]]
    
    # Append left, center, and right station-elevation pairs
    scour_data_array.append([pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                left_station['Elev'].values[1]+scourCone_elev_shift])
    
    scour_data_array.append([pier_data['Bent CL Sta']-pier_data['Footing Cap Width']/2-.2,
                              scour_data_df[recurrance_elevation].values[0]])         
    
    scour_data_array.append([pier_data['Bent CL Sta']+pier_data['Footing Cap Width']/2+.2, 
                             scour_data_df[recurrance_elevation].values[0]])          
                
    scour_data_array.append([pier_data['Bent CL Sta'] + pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                right_station['Elev'].values[1]+scourCone_elev_shift])
    return scour_data_array

def draw_scourCone_laterallyUnstable(pier_data, scour_data_df,ground_line, pier_scourCone_shift,scourCone_elev_shift,scour_data_array,recurrance_depth,recurrance_elevation):
    
    left = pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]) - pier_data['Pier Stem Bottom Width']
    
    left_station = ground_line.iloc[(ground_line['Offset Station']-left).abs().argsort()[:2]]
    
    scour_data_array.append([pier_data['Bent CL Sta'] - pier_scourCone_shift*(scour_data_df[recurrance_depth].values[0]),
                                left_station['Elev'].values[1]+scourCone_elev_shift])
    
    scour_data_array.append([pier_data['Bent CL Sta']-pier_data['Footing Cap Width']/2-.2, 
                             scour_data_df[recurrance_elevation].values[0]])    
         
    scour_data_array.append([pier_data['Bent CL Sta']+pier_data['Footing Cap Width']/2+.2, 
                             scour_data_df[recurrance_elevation].values[0]])   
                       
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
        
            
def adjust_scourCone(contraction_station,total_scour_plot,scour_data_copy,left_tieIn_shift,right_tieIn_shift):
    scour_array_plot = np.array([contraction_station,total_scour_plot])
    for station in scour_data_copy:
        contraction_station_df = pd.DataFrame(contraction_station, columns=['Offset Station'])
        left = min(contraction_station_df['Offset Station'], key=lambda x: abs(x - station[0][0]))
        right = min(contraction_station_df['Offset Station'], key=lambda x: abs(x - station[3][0]))
        left_index = contraction_station_df['Offset Station'][contraction_station_df['Offset Station'] == left].index.tolist()
        right_index = contraction_station_df['Offset Station'][contraction_station_df['Offset Station'] == right].index.tolist()
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

def clean_LTD(ltd_array_plot,left_idx,right_idx,left_abut_match,right_abut_match):
    
    ltd_array_plot[0][:left_idx+left_abut_match] = np.nan
    ltd_array_plot[1][:left_idx+left_abut_match] = np.nan
    ltd_array_plot[0][right_idx+right_abut_match:] = np.nan
    ltd_array_plot[1][right_idx+right_abut_match:] = np.nan
    #ltd_array_plot = ltd_array_plot[:, ~np.isnan(ltd_array_plot).any(axis=0)]

    return ltd_array_plot

def calculate_pier_data(pier_data_dict,pier_id,cse_data):
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
    cse_data 
    
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
