import pandas as pd 

import io
import warnings
from PIL import Image
warnings.simplefilter(action='ignore', category=FutureWarning)
import streamlit as st

from utils.plotting_utils.plotting_utils import generate_figure

from utils.plotting_utils.data_processing_utils import recurrence_txt,generate_pier_scour_df

st.set_page_config(layout='wide')
#image = Image.open('./src/Images/peakflow.jpg')
#st.image(image, use_container_width=True)


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
                            max_value=1.0,
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
    


recurrence_data = recurrence_txt()  

# Generate scour data based on the flags
if bridge_data is not None:
    bridge_data = pd.read_csv(bridge_data) 
    structure_data = generate_pier_scour_df(bridge_data)
    

    # Unpack the structure data
    """
    pier_data_dict, 
        individual_pier_ids,
        bridge_low_chord, 
        bridge_high_chord, 
        ground_line, 
        scour_data_df, 
        bank_stations, 
        lateral_stability,
            wse,events,abutment_data
    """
    #pier_data_dict= pd.DataFrame(structure_data[0])
    st.divider()
    st.subheader("Structure and Scour Data")
    st.write("The table below shows the structure and scour data that will be used to generate the scour plots. To modify the data, please do so from the scour workbook and re-upload. Data can not be modified within this table.")
    pier_data_dict=structure_data[0]
    #st.data_editor(pd.DataFrame(structure_data[0]).T,use_container_width=True).T
    st.divider()
    st.header("Scour Figures by Recurrence Interval")
    st.write("The figures below show the scour data for each recurrence interval. You can download each figure by clicking the download button below each plot.")

    bridge_low_chord= structure_data[1]
    st.write("Bridge Low Chord Elevation:", bridge_low_chord)
    bridge_high_chord= structure_data[2]
    st.write("Bridge High Chord Elevation:", bridge_high_chord)
    ground_line= structure_data[3]
    st.write("Ground Line Elevation:", ground_line)
    scour_data_df=  structure_data[4]
    st.write("Scour Data:", scour_data_df)
    wse_data= structure_data[5]
    st.write("Water Surface Elevation (WSE) Data:", wse_data)
    events= structure_data[6]
    st.write("Recurrence Interval Events:", events)
    LTD= structure_data[7]
    st.write("LTD:", LTD)
    contraction_scour= structure_data[8]
    st.write("Contraction Scour Data:", contraction_scour)
    pile_data=  structure_data[9]
    st.write("Pile Data:", pile_data)
    all_pile_elements=  structure_data[10])
    st.write("All Pile Elements:", all_pile_elements)
    
    
    
    
    

    

    # Display the structure data in a table
    
    
    # Generate scour plots for each recurrence interval
    i=0
    
    events=events.to_numpy()
    lb_cw_mc = st.selectbox("Apply Clear Water or Live Bed Contraction Scour to Main Channel?", ("LB", "CW"))
    for year in events[0]:
        if i == 0:
            recur = 0
            wse_station = wse_data['WSE 100yr Station']
            wse_elev = wse_data['WSE 100yr']
            contract_elev = contraction_scour['CS_Design_Elev']
        else:
            recur = 1
            wse_station = wse_data['WSE 500yr Station']
            wse_elev = wse_data['WSE 500yr']
            contract_elev = contraction_scour['CS_Check_Elev']

        event = events[0][i]
        figure = generate_figure(pier_data_dict, 
                        bridge_low_chord, 
                        bridge_high_chord, 
                        ground_line,
                        scour_data_df, 
                        lateral_stability,
                        wse_station, 
                        wse_elev, 
                        event,
                        recur,
                        LTD,
                        contract_elev,
                        pile_data,
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
                        lb_cw_mc)
        st.pyplot(figure)
        
        
        #allow user to download the figure
        buf = io.BytesIO()
        figure.savefig(buf, format="png")
        buf.seek(0)
        figure = buf.getvalue()
        st.download_button(label=f"Download {events[0][i]} Figure", data=figure, file_name=f"scour_plot_{events[0][i]}.png")
        i+=1
    st.divider()
    st.header("Scour Summary Figure")
    st.write("The figure below shows the scour data for all recurrence intervals in a single plot. You can download this figure by clicking the download button below the plot.")
    # Generate the summary figure for all recurrence intervals
    """
    summary_figure = generate_summary_figure(pier_data_dict, 
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
                        recurrence_data)
    st.pyplot(summary_figure)
    
    #allow user to download the summary figure
    summary_figure_buf = io.BytesIO()
    summary_figure.savefig(summary_figure_buf, format="png")
    summary_figure_buf.seek(0)
    summary_figure = summary_figure_buf.getvalue()
    st.download_button(label="Download Summary Figure", data=summary_figure, file_name="scour_summary_plot.png")
    """
    
                        

    



