import pandas as pd 
import io
from io import BytesIO
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import os
import numpy as np
import time
import streamlit as st

from scour_plotting_utils import recurrence_txt,generate_pier_scour_df, generate_figure, generate_summary_figure


if __name__ == "__main__":
    
    
    st.title("Generate Scour Plots")
    st.subheader("This application generates scour plots based on the provided scour data and recurrence intervals.")
    st.write("Please upload the scour data file (scour_data.csv) in CSV format.")
    st.write("*This file is created by the scour worksheet by clicking the 'Generate Scour Data for Plotting' button and is saved in the same folder as the scour workbook.")
    # Set the page configuration
    with st.sidebar:
        st.header("Upload Files")
        st.subheader("Please upload the scour data file.")
        bridge_data = st.file_uploader("Choose a file")
        st.write("To make changes to the data being plotted, please modifiy the information in the scour worksheet and re-upload the data.")

        
   
    # Create a file uploader for the scour data
    # Ensure the user has uploaded a file
   
    # File uploader for scour data
    # The recurrence intervals are expected to be in a text file with one interval per line
  
    

    
    recurrence_data = recurrence_txt()  

    # Generate scour data based on the flags
    if bridge_data is not None:
        bridge_data = pd.read_csv(bridge_data) 
        structure_data = generate_pier_scour_df(bridge_data)

        # Unpack the structure data
        pier_data_dict = structure_data[0]
        individual_pier_ids = structure_data[1]
        bridge_low_chord = structure_data[2]
        bridge_high_chord = structure_data[3]
        ground_line = structure_data[4]
        scour_data_df = structure_data[5]
        bank_stations = structure_data[6]
        lateral_stability = structure_data[7]
        lt_deg = structure_data[8]
        abt_scour_elev = structure_data[9]
        abut_stat = structure_data[10]
        wse_data = structure_data[11]
        pierdata_df = pd.DataFrame(pier_data_dict).T
        st.subheader("Structure and Scour Data")
        st.write("The table below shows the structure and scour data that will be used to generate the scour plots. To modify the data, please do so from the scour workbook and re-upload. Data can not be modified within this table.")
        st.dataframe(pierdata_df,use_container_width=True)

        st.header("Scour Figures by Recurrence Interval")
        st.write("The figures below show the scour data for each recurrence interval. You can download each figure by clicking the download button below each plot.")
        for year in recurrence_data:
            figure = generate_figure(pier_data_dict, 
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
                                year)
            st.pyplot(figure)
            
            #allow user to download the figure
            buf = io.BytesIO()
            figure.savefig(buf, format="png")
            buf.seek(0)
            figure = buf.getvalue()
            st.download_button(label=f"Download {year[-1]} Figure", data=figure, file_name=f"scour_plot_{year[-1]}.png")
            
        st.header("Scour Summary Figure")
        st.write("The figure below shows the scour data for all recurrence intervals in a single plot. You can download this figure by clicking the download button below the plot.")
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
        
                            

        



