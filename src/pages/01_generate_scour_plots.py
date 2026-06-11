import pandas as pd 

import io
import warnings
from PIL import Image
import struct

warnings.simplefilter(action='ignore', category=FutureWarning)
import streamlit as st

from utils.plotting_utils.plotting_utils import generate_figure

from utils.plotting_utils.data_processing_utils import create_Mainfigure, generate_pier_scour_df

st.set_page_config(layout='wide')



# Set the title and description of the Streamlit app
#st.set_page_config(page_title="Generate Scour Plots", layout="wide")

st.title("Generate Scour Plots")
st.subheader("This application generates scour plots based on the provided scour data and recurrence intervals.")
st.write("Please upload the scour data file (scour_data.csv) in CSV format.")
st.write("*This file is created by the scour worksheet by clicking the 'Generate Scour Data for Plotting' button and is saved in the same folder as the scour workbook.")
# Set the page configuration
with st.sidebar:
    st.header("File Upload")
    st.subheader("Please upload the scour data file.")
    bridge_data = st.file_uploader("Choose a file")
    #yes no dropdown for lateral stability

    lateral_stability = st.selectbox(
                            "Is the channel laterally stable?",
                            ("Yes", "No")
                            )
    cs_condition_mc = st.selectbox("Apply Clear Water or Live Bed Contraction Scour to Main Channel?", ("LB", "CW"))
    smooth_gl = st.selectbox("Apply smoothing to ground line?", ("Yes", "No"))
    pier_scourCone_shift = st.sidebar.number_input(
                            "Scour Cone Slope Scaler",
                            min_value=0.1,
                            max_value=2.0,
                            value=(0.8),step = 0.05 # default range
                            )
    scourCone_elev_shift = st.sidebar.number_input(
                            "Scour Cone Elevation Shift (ft)",
                            min_value=-30.0,
                            max_value=30.0,
                            value=(0.0),step = 0.25 # default range
                            )
    line_smoothing_coeff = st.sidebar.number_input(
                            "Line Smoothing Coefficient",
                            min_value=0.0,
                            max_value=10.0,
                            value=(0.5),step = 0.1 # default range
                            )
    left_tieIn_shift = st.sidebar.number_input(
                            "Left LS Tie-In Shift (ft)",
                            min_value=-50,
                            max_value=50,
                            value=(0),step = 1 # default range
                            )
    right_tieIn_shift = st.sidebar.number_input(
                            "Right LS Tie-In Shift (ft)",
                            min_value=-50,
                            max_value=50,
                            value=(0),step = 1 # default range
                            )
    left_abut_shift = st.sidebar.number_input(
                            "Left Contraction Scour Tie-In Shift (ft)",
                            min_value=-50,
                            max_value=50,
                            value=(0),step = 1 # default range
                            )
    left_abut_match = st.sidebar.number_input(
                            "Left Abutment Element Tie-In Shift (ft)",
                            min_value=-50,
                            max_value=50,
                            value=(0),step = 1 # default range
                            )
    
    right_abut_shift = st.sidebar.number_input(
                            "Right Contraction Scour Tie-In Shift (ft)",
                            min_value=-50,
                            max_value=50,
                            value=(0),step = 1 # default range
                            )
    right_abut_match = st.sidebar.number_input(
                            "Right Abutment Element Tie-In Shift (ft)",
                            min_value=-50,
                            max_value=50,
                            value=(0),step = 1 # default range
                            )
    fig_width = st.sidebar.number_input(
                            "Figure Width (in)",
                            min_value=-50,
                            max_value=50,
                            value=(15),step = 1 # default range
                            )
    fig_height = st.sidebar.number_input(
                            "Figure Height (in)",
                            min_value=-50,
                            max_value=50,
                            value=(5),step = 1 # default range
                            )
    
def float_to_bytes(value: float, precision: str = 'f', endian: str = '<') -> bytes:
    """
    Convert a float to bytes.
    
    Args:
        value (float): The floating-point number to convert.
        precision (str): 'f' for 32-bit float, 'd' for 64-bit double.
        endian (str): '<' for little-endian, '>' for big-endian.
    
    Returns:
        bytes: The byte representation of the float.
    """
    if not isinstance(value, (float, int)):
        raise TypeError("Value must be a float or int.")
    if precision not in ('f', 'd'):
        raise ValueError("Precision must be 'f' (32-bit) or 'd' (64-bit).")
    if endian not in ('<', '>'):
        raise ValueError("Endian must be '<' (little) or '>' (big).")
    
    return struct.pack(endian + precision, float(value))

#recurrence_data = recurrence_txt()  

# Generate scour data based on the flags
if bridge_data is not None:
    bridge_data = pd.read_csv(bridge_data) 
    structure_data = generate_pier_scour_df(bridge_data)
    

    st.divider()
    st.subheader("Structure and Scour Data")
    
    
    st.divider()
    
    all_pile_elements=  structure_data[9]
    #find the number of rows in the pier data dict and write it to the streamlit app
    #delete all nan values from all_pile_elements and reset the index
    all_pile_elements = all_pile_elements.dropna().reset_index(drop=True)
    
    st.subheader("Bridge Deck Geometry Data:")
    
    bridge_low_chord= pd.DataFrame(structure_data[1])
   
    bridge_high_chord= pd.DataFrame(structure_data[2])
   
    ground_line= structure_data[3].dropna().reset_index(drop=True)
   
    scour_data_df=  structure_data[4].dropna().reset_index(drop=True)
    
   
    
    events= st.data_editor(pd.DataFrame(structure_data[6]).T).T.dropna().reset_index(drop=True)
   
    contraction_data= structure_data[7][:2]
    
    pile_data=  structure_data[8]
    
    
    all_pile_elements= structure_data[9]

    i=0
    st.header("Scour Figures by Recurrence Interval")
    st.write("The figures below show the scour data for each recurrence interval. You can download each figure by clicking the download button below each plot.")
    
    events=events.to_numpy()
    
    offset_shift = st.number_input("Adjust stationing shift for groundline", min_value=-50, max_value=50, value=0, step=1)
    if offset_shift != 0:
        ground_line['Offset Station'] = ground_line['Offset Station'] + offset_shift


    deck_offset_left = st.number_input("Adjust Bridge Deck Left Station", min_value=-50.0, max_value=50.0, value=0.0, step=0.25)
    deck_offset_right = st.number_input("Adjust Bridge Deck Right Station", min_value=-50.0, max_value=50.0, value=0.0, step=0.25)
   
    bridge_low_chord.at[0,'Bent CL Sta'] += deck_offset_left
    bridge_low_chord.loc[bridge_low_chord.tail().index,'Bent CL Sta'] += deck_offset_right
    bridge_high_chord.at[0,'Bent CL Sta'] += deck_offset_left
    bridge_high_chord.loc[bridge_high_chord.tail().index,'Bent CL Sta'] += deck_offset_right
    #make a list of keys in structure_data[0] if key is not nan
    st.write("Use the table below to adjust the structure bent placement if needed. The Bent CL Sta values can be used to shift the piles left or right.")
    pier_data_dict=st.data_editor(pd.DataFrame(structure_data[0]).T).T
    st.subheader("WSE Data:")
    wse_data= st.data_editor(pd.DataFrame(structure_data[5][:2]).T).T.dropna().reset_index(drop=True)
       
       
        

    


    for year in events[0]:
        if i == 0:
            recur = 0
            wse_station = wse_data['WSE 100yr Station']
            wse_elev = wse_data['WSE 100yr']
        else:
            recur = 1
            wse_station = wse_data['WSE 500yr Station']
            wse_elev = wse_data['WSE 500yr']
        event = events[0][i]
       
        main_dict = generate_figure(pier_data_dict, 
                        ground_line,
                        scour_data_df, 
                        lateral_stability,
                        wse_station, 
                        wse_elev, 
                        event,
                        recur,
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
                        )
       
        figure = create_Mainfigure(main_dict, 
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
                                   fig_height)
        st.pyplot(figure)
        
        
        #allow user to download the figure
        buf = io.BytesIO()
        figure.savefig(buf, format="png")
        buf.seek(0)
        figure = buf.getvalue()
        st.download_button(label=f"Download {events[0][i]} Figure", data=figure, file_name=f"scour_plot_{events[0][i]}.png")
        i+=1
     
    st.divider()
    