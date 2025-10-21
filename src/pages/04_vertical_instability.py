
import warnings
from PIL import Image
warnings.simplefilter(action='ignore', category=FutureWarning)
import streamlit as st
import altair as alt


from utils.vert_stab.vert_stab import process_data







if __name__ == "__main__":
    st.set_page_config(layout='wide')
    image = Image.open('./src/Images/peakflow.jpg')
    st.image(image, use_container_width=True)
    
    st.title("Vizualize Vertical Instability")
    st.subheader("This application downloads field measurement data from the USGS and plots the stage height for a given range of flow rates.")
    
    # Set the page configuration
    with st.sidebar:
        st.header("Data Download")
        st.subheader("Please enter the USGS gage ID:")
        usgs_station_id = st.sidebar.text_input("**USGS Station ID**")
        lower_threshold = st.sidebar.number_input("**Enter Lower Flow Threshold (cfs)**", min_value=0, value=50)
        
        upper_threshold = st.sidebar.number_input("**Enter Higher Flow Threshold (cfs)**", min_value=0, value=100)
        
        

    # Generate scour data based on the flags
    if st.sidebar.button("Analyze Stage Measurements"):
        data, mean, std = process_data(usgs_station_id, lower_threshold,upper_threshold)
        with st.expander("See Original Data"):
            st.dataframe(data)
           
        st.subheader("Stage Measurement Data")
        st.write(f"Mean Flow Across Gage Period of Record: {mean:.1f} cfs")
        st.write(f"Standard Deviation of Flow Across Gage Period of Record: {std:.1f} cfs")
        with st.expander("See Subsetted DataFrame"):
            st.dataframe(data)
        #plot the stage vs date as an altair plot
        figure = alt.Chart(data).mark_line().encode(
            x='date:T',
            y='stage:Q'
        ).properties(
            width=800,
            height=600,
            
        )
        points = alt.Chart(data).mark_circle(color='red', size = 100).encode(
            x='date:T',
            y='stage:Q'
        )
        figure = figure + points
        st.altair_chart(figure, use_container_width=True)
        
