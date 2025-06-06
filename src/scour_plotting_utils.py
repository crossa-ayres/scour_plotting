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
    cs_ltd = year[0]
    local_scour = year[1]
    scour_data_array = []
    pier_data = pier_data_dict[pier_id]

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
    pier_plotting_data_left = []
    pier_plotting_data_right = []
    pier_data = pier_data_dict[pier_id]
    #x1, y1
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
    
    abut_scour_flag = year[4]
    cs_ltd = year[0]
    wse_flag = year[3]
    recurrence_title = year[-1]



    pier_keys = list(pier_data_dict.keys())

    scour_data_array = []
    
    left_station = abut_stat['Abt Toe Left Sta.'].values[0]
    right_station = abut_stat['Abt Toe Right Sta.'].values[0]
    
    

    ground_line.loc[(ground_line['Offset Station'] > bank_stations['Channel Bank Sta.'].values[0]) & (ground_line['Offset Station'] < bank_stations['Channel Bank Sta.'].values[1]), "channel"] = "Channel"
    ground_line.loc[(ground_line['Offset Station'] < left_station) | (ground_line['Offset Station'] > right_station), "channel"] = "Abutment"
    ground_line = ground_line.assign(lt_deg = 0.0)
    ground_line = ground_line.assign(contract_scour = 0.0)
    ground_line = ground_line.assign(abut_scour = 0.0)

    
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
        
        pier_plotting_data_left, pier_plotting_data_right = calculate_pier_data(pier_data_dict,pier_id)
        

        ax.plot([x[0] for x in pier_plotting_data_left], [x[1] for x in pier_plotting_data_left], color='black',linewidth=1)
        ax.plot([x[0] for x in pier_plotting_data_right], [x[1] for x in pier_plotting_data_right], color='black',linewidth=1)
        if i > 0 and i < len(individual_pier_ids)-1:
            scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)
            scour_data_copy.append(scour_data_array)
        
            if i == 1:
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle=':',linewidth=2, label = "Local Scour (LS) at Pier")
            else:
                ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle=':',linewidth=2)
        i+=1
    
    for station in scour_data_copy:
        
        left = min(ground_line['Offset Station'], key=lambda x: abs(x - station[0][0]))
        
        right = min(ground_line['Offset Station'], key=lambda x: abs(x - station[2][0]))
        left_index = ground_line['Offset Station'][ground_line['Offset Station'] == left].index.tolist()
        
        right_index = ground_line['Offset Station'][ground_line['Offset Station'] == right].index.tolist()

        ground_line.loc[left_index[0]:right_index[0], ["contract_scour"]] = np.nan
        ground_line.loc[left_index[0]:right_index[0], ['lt_deg']] = np.nan
        ground_line.loc[left_index[0]:right_index[0], ["abut_scour"]] = np.nan

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
    

    fig, ax = plt.subplots()
    iteration = 0
    for year in recurrence_data:
        
        abut_scour_flag = year[4]
        cs_ltd = year[0]
        wse_flag = year[3]
        
        



        pier_keys = list(pier_data_dict.keys())

        scour_data_array = []
        
        left_station = abut_stat['Abt Toe Left Sta.'].values[0]
        right_station = abut_stat['Abt Toe Right Sta.'].values[0]
        
        

        ground_line.loc[(ground_line['Offset Station'] > bank_stations['Channel Bank Sta.'].values[0]) & (ground_line['Offset Station'] < bank_stations['Channel Bank Sta.'].values[1]), "channel"] = "Channel"
        ground_line.loc[(ground_line['Offset Station'] < left_station) | (ground_line['Offset Station'] > right_station), "channel"] = "Abutment"
        ground_line = ground_line.assign(lt_deg = 0.0)
        ground_line = ground_line.assign(contract_scour = 0.0)
        ground_line = ground_line.assign(abut_scour = 0.0)

        
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
        
        wse = [[pier_data_dict[individual_pier_ids[0]]['Bent CL Sta'], wse_data[wse_flag].values[0]],
            [pier_data_dict[individual_pier_ids[-1]]['Bent CL Sta'], wse_data[wse_flag].values[0]]]
                        

        
        
        
        
        i=0
        scour_data_copy = []
        for pier_id in individual_pier_ids:
            
            pier_plotting_data_left, pier_plotting_data_right = calculate_pier_data(pier_data_dict,pier_id)
            scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)

            ax.plot([x[0] for x in pier_plotting_data_left], [x[1] for x in pier_plotting_data_left], color='black',linewidth=1)
            ax.plot([x[0] for x in pier_plotting_data_right], [x[1] for x in pier_plotting_data_right], color='black',linewidth=1)
            if i > 0 and i < len(individual_pier_ids)-1:
                scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, year)
                scour_data_copy.append(scour_data_array)
            
                if i == 1 and iteration == 1:
                    ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='red',linestyle=':',linewidth=2, label = "Total Scour - 500YR")
                else:
                    ax.plot([x[0] for x in scour_data_array], [x[1] for x in scour_data_array], color='grey',linewidth=2, label = "Total Scour - 100YR")
            i+=1
        for station in scour_data_copy:
            
            left = min(ground_line['Offset Station'], key=lambda x: abs(x - station[0][0]))
            
            right = min(ground_line['Offset Station'], key=lambda x: abs(x - station[2][0]))
            left_index = ground_line['Offset Station'][ground_line['Offset Station'] == left].index.tolist()
            
            right_index = ground_line['Offset Station'][ground_line['Offset Station'] == right].index.tolist()

            ground_line.loc[left_index[0]:right_index[0], ["contract_scour"]] = np.nan
            ground_line.loc[left_index[0]:right_index[0], ['lt_deg']] = np.nan
            ground_line.loc[left_index[0]:right_index[0], ["abut_scour"]] = np.nan

            ground_line.loc[left_index[0], ["lt_deg"]] = station[0][1]
            ground_line.loc[right_index[0], ["lt_deg"]] = station[2][1]
            ground_line.loc[left_index[0], ["abut_scour"]] = station[0][1]
            ground_line.loc[right_index[0], ["abut_scour"]] = station[2][1]
            ground_line.loc[left_index[0], ["contract_scour"]] = station[0][1]
            ground_line.loc[right_index[0], ["contract_scour"]] = station[2][1]

        if iteration == 0:
            ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green', label='Ground Line')
            ax.plot(bridge_low_chord['Bent CL Sta'], bridge_low_chord['Low Chord Elev'], color='black' )
            ax.plot(bridge_high_chord['Bent CL Sta'], bridge_high_chord['High Chord Elev'], color='black')
            
            if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
                ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300')
            else:
                ax.plot(ground_line['Offset Station'], ground_line['lt_deg'],color='grey',linewidth=2)
            #ax.plot(ground_line['Offset Station'], ground_line["abut_scour"], color='#0073CF', label='Abutment Scour (AS)')
            #ax.plot(ground_line['Offset Station'], ground_line["contract_scour"], color='#FCD450', label='Contraction Scour (CS)')
            #ax.plot([x[0] for x in wse], [x[1] for x in wse], color='blue',linewidth=2,linestyle=':', label='WSE')
        else:
            #ax.plot(ground_line['Offset Station'], ground_line['Elev'], color='green')
                        
            if lateral_stability['Laterally Stable Channel?'].values[0] == 'No':
                ax.plot([x[0] for x in cl_lsd], [x[1] for x in cl_lsd], color='#E98300')
            else:
                ax.plot(ground_line['Offset Station'], ground_line['lt_deg'], color='red',linestyle=':',linewidth=2)
                #ax.plot(ground_line['Offset Station'], ground_line["abut_scour"], color='#0073CF')
                #ax.plot(ground_line['Offset Station'], ground_line["contract_scour"], color='#FCD450')
                ax.plot([x[0] for x in wse], [x[1] for x in wse], color='blue',linewidth=2,linestyle=':')


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
    