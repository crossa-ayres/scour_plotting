import pandas as pd 
import numpy as np
from .data_processing_utils import calculate_scour_data, adjust_scourCone,clean_contractionScour,clean_LTD,calc_scourCondition_stable,calc_scourCondition_unstable
from scipy.interpolate import make_splrep
pd.options.mode.copy_on_write = True






def generate_figure(pier_data_dict, 
                          ground_line,
                          scour_data_df, 
                          lateral_stability,
                           wse_station, wse_elev, 
                          event,recur,
                          contraction_data,
                          all_pile_elements,
                          pier_scourCone_shift,
                          line_smoothing_coeff,
                          left_tieIn_shift,
                          right_tieIn_shift,
                          left_abut_shift,
                          right_abut_shift,
                          scourCone_elev_shift,
                          left_abut_match,
                          right_abut_match,
                          cs_condition_mc,
                          smooth_gl,
                        
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

 
    main_dict = {}
    scour_data_array = []
    i=0
    scour_data_design = []
    scour_data_check = []
    main_dict[event] = { "scour_data": {}, "ltd": [],"contraction_scour": [], "total_scour": [], "ground_line": [], "wse": (wse_station, wse_elev), "pile_left": [], "pile_right":[] }
    main_dict["gl"] = {"ground_line":[]}

    
    contraction_station = np.linspace(ground_line['Offset Station'].min(), ground_line['Offset Station'].max(), int(len(ground_line['Offset Station'])))
    
    left_idx = np.abs(contraction_station - int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])).argmin()
    
    right_idx = np.abs(contraction_station - int(pier_data_dict[all_pile_elements['Bent ID'][1]]['Bent CL Sta'])).argmin()

    left_ltd_idx = int(pier_data_dict[all_pile_elements['Bent ID'][0]]['Bent CL Sta'])
    right_ltd_idx = int(pier_data_dict[all_pile_elements['Bent ID'][1]]['Bent CL Sta'])
    
    interpolated_elev = make_splrep(contraction_station, ground_line['Elev'], s=line_smoothing_coeff)(contraction_station)

    if not main_dict["gl"]["ground_line"]:
        if smooth_gl == 'Yes':
            main_dict["gl"]["ground_line"].append(([contraction_station, interpolated_elev]))
        else:
            main_dict["gl"]["ground_line"].append(([ground_line['Offset Station'], ground_line['Elev']]))

    for pier_id in all_pile_elements["Bent ID"].tolist():

        scour_data_array = calculate_scour_data(pier_data_dict,pier_id, scour_data_df,ground_line, recur,pier_scourCone_shift,scourCone_elev_shift,lateral_stability)
        main_dict[event]["scour_data"][pier_id]=scour_data_array
        if scour_data_array:
            if recur == 0:
                scour_data_design.append(scour_data_array)
            if recur == 1:
                scour_data_check.append(scour_data_array)
    #try:
    #    interpolated_elev[left_index[0]+left_tieIn_shift:right_index[0]-right_tieIn_shift] = np.nan
    #except Exception as e:
    #    pass
    


    if recur==0:
        if lateral_stability == 'Yes':
            total_scour, contraction_elevation_arr = calc_scourCondition_stable(cs_condition_mc,interpolated_elev,contraction_data,recur)
            try:
                ltd_elev_shift =  interpolated_elev-contraction_data['LTD Depth'].values[0]
                ltd_array_plot = np.array([contraction_station,ltd_elev_shift])
                ltd_array_plot  = clean_LTD(ltd_array_plot,left_idx,right_idx,left_abut_match,right_abut_match)
                main_dict[event]["ltd"].append(([ltd_array_plot[0], ltd_array_plot[1]]))
            except:
                pass
            total_scour = np.array([contraction_station,total_scour])
            total_scour[1][:left_idx+left_abut_match+left_abut_shift] = pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 100yr']
            total_scour[1][right_idx+right_abut_match+right_abut_shift:] =pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 100yr']
            total_scour[0][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[1][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[0][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour[1][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour = total_scour[:, ~np.isnan(total_scour).any(axis=0)]

            
            scour_array_plot = adjust_scourCone(total_scour[0],total_scour[1],scour_data_design,left_tieIn_shift,right_tieIn_shift)
            
            contract_array_plot = adjust_scourCone(contraction_station,contraction_elevation_arr ,scour_data_design,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)

            

            main_dict[event]["total_scour"].append(([scour_array_plot[0],scour_array_plot[1]]))
            main_dict[event]["contraction_scour"].append(([contract_array_plot[0],contract_array_plot[1]]))
            
        
        elif lateral_stability == 'No':
            total_scour_arr = []
            contract_scour_depth = calc_scourCondition_unstable(cs_condition_mc,contraction_data,recur)
           
            contract_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            total_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            
            
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
        
            contract_array_plot = adjust_scourCone(contraction_station,contract_scour_arr,scour_data_design,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)

            main_dict[event]["total_scour"].append((scour_array_plot))
            main_dict[event]["contraction_scour"].append((contract_array_plot))
            try:
                main_dict[event]["ltd"].append(([left_ltd_idx ,right_ltd_idx ], [(contraction_data['Thawleg Elevation'].values[0]-contraction_data['LTD Depth'].values[0]) for i in range(2)]))
            except:
                pass

    elif recur == 1:
       
        if lateral_stability == 'Yes':
            total_scour, contraction_elevation_arr = calc_scourCondition_stable(cs_condition_mc,interpolated_elev,contraction_data,recur)
           
            total_scour = np.array([contraction_station,total_scour])
            total_scour[1][:left_idx+left_abut_match+left_abut_shift] = pier_data_dict[all_pile_elements['Bent ID'][0]]['Scour Elevation 500yr']
            total_scour[1][right_idx+right_abut_match+right_abut_shift:] =pier_data_dict[all_pile_elements['Bent ID'][1]]['Scour Elevation 500yr']
            total_scour[0][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[1][left_idx+left_abut_match:left_idx+left_abut_shift+left_abut_match] = np.nan
            total_scour[0][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour[1][right_idx+right_abut_shift+right_abut_match:right_idx+right_abut_match] = np.nan
            total_scour = total_scour[:, ~np.isnan(total_scour).any(axis=0)]

            
            scour_array_plot = adjust_scourCone(total_scour[0],total_scour[1],scour_data_check,left_tieIn_shift,right_tieIn_shift)

           
            
            contract_array_plot = adjust_scourCone(contraction_station,contraction_elevation_arr ,scour_data_check,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)
        
            try:
                ltd_elev_shift =  interpolated_elev-contraction_data['LTD Depth'].values[0]
                ltd_array_plot = np.array([contraction_station,ltd_elev_shift])
                ltd_array_plot  = clean_LTD(ltd_array_plot,left_idx,right_idx,left_abut_match,right_abut_match)
                main_dict[event]["ltd"].append(([ltd_array_plot[0], ltd_array_plot[1]]))
            except:
                pass

            main_dict[event]["total_scour"].append((scour_array_plot))
            main_dict[event]["contraction_scour"].append((contract_array_plot))
            

        elif lateral_stability == 'No':

            total_scour_arr = []
            contract_scour_depth = calc_scourCondition_unstable(cs_condition_mc,contraction_data,recur)
         
            total_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            contract_scour_arr = [contract_scour_depth for i in range(int(len(ground_line['Offset Station'])))]
            
            
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
        
            contract_array_plot = adjust_scourCone(contraction_station,contract_scour_arr,scour_data_check,left_tieIn_shift,right_tieIn_shift)
            contract_array_plot = clean_contractionScour(contract_array_plot,left_idx,left_abut_shift,right_idx,right_abut_shift,left_abut_match,right_abut_match)
           
            main_dict[event]["total_scour"].append((scour_array_plot))
            main_dict[event]["contraction_scour"].append((contract_array_plot))

            try:
                main_dict[event]["ltd"].append(([left_ltd_idx ,right_ltd_idx ], [(contraction_data['Thawleg Elevation'].values[0]-contraction_data['LTD Depth'].values[0]) for i in range(2)]))
            except:
                pass

    return main_dict
   

