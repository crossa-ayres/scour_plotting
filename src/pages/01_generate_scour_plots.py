import pandas as pd 
import io
import warnings
from PIL import Image
warnings.simplefilter(action='ignore', category=FutureWarning)
import streamlit as st

#from utils.plotting_utils.scour_plotting_utils import recurrence_txt,generate_pier_scour_df, generate_figure, generate_summary_figure
from utils.plotting_utils.plotting_utils import generate_figure

from utils.plotting_utils.data_processing_utils import recurrence_txt,generate_pier_scour_df


if __name__ == "__main__":
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
        st.write("To make changes to the data being plotted, please modifiy the information in the scour worksheet and re-upload the data.")
  
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
        
        pier_data_dict = structure_data[0]
        individual_pier_ids = structure_data[1]
        bridge_low_chord = structure_data[2]
        bridge_high_chord = structure_data[3]
        ground_line = structure_data[4]
        scour_data_df = structure_data[5]
        bank_stations = structure_data[6]
        lateral_stability = structure_data[7]
        wse_data = structure_data[8]
        events = structure_data[9]
        abutment_data = structure_data[10]
        abut_stat = structure_data[11]
        LTD = structure_data[12]
        contraction_scour = structure_data[13]
        pile_data = structure_data[14]
        all_pile_elements = structure_data[15]
        
        
        
        
        

        

        # Display the structure data in a table
        pierdata_df = pd.DataFrame(pier_data_dict).T
        st.divider()
        st.subheader("Structure and Scour Data")
        st.write("The table below shows the structure and scour data that will be used to generate the scour plots. To modify the data, please do so from the scour workbook and re-upload. Data can not be modified within this table.")
        st.dataframe(pierdata_df,use_container_width=True)
        st.divider()
        st.header("Scour Figures by Recurrence Interval")
        st.write("The figures below show the scour data for each recurrence interval. You can download each figure by clicking the download button below each plot.")
        
        # Generate scour plots for each recurrence interval
        i=0
        
        events=events.to_numpy()
     
        for year in events[0]:
            if i == 0:
                recur = 0
                abutment_elevation = abutment_data['SDAB']
                wse_station = wse_data['WSE 100yr Station']
                wse_elev = wse_data['WSE 100yr']
                contract_sta = contraction_scour['CS_Design_Station']
                contract_elev = contraction_scour['CS_Design_Elev']
            else:
                recur = 1
                abutment_elevation = abutment_data['SCAB']
                wse_station = wse_data['WSE 500yr Station']
                wse_elev = wse_data['WSE 500yr']
                contract_sta = contraction_scour['CS_Check_Station']
                contract_elev = contraction_scour['CS_Check_Elev']
            abutment_data_event = [abutment_data['Offset Station'], abutment_elevation]
            figure = generate_figure(pier_data_dict, 
                                individual_pier_ids,
                                bridge_low_chord, 
                                bridge_high_chord, 
                                ground_line,
                                scour_data_df,
                                bank_stations, 
                                lateral_stability,
                                abut_stat,wse_station, wse_elev,
                                year,events[0][i],abutment_data_event,recur,LTD,contract_sta,contract_elev,pile_data,all_pile_elements)
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
        
                            

        



