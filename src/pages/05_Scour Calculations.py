import streamlit as st
import numpy as np
import pandas as pd


from utils.scour.data_loader import DataLoader
from utils.scour.calculate_contractionScour import contraction_scour

if __name__ == "__main__":
    st.header("Wave Scour Calculator")
    st.subheader("This application calculates the wave scour depth based on the given wind speed, water depth, and fetch length.")
    
    
    st.header("Input Parameters")
    st.set_page_config(page_title="Data Summary", layout="wide")
    # Example usage:
    loader = DataLoader(r'data\100.csv')
    contracted_section_df, approach_section_df, LOB_contraction_df = loader.generate_scour_df()

    st.title("Data Summary")

    #display editable tables in two columns with st.columns
    col1, col2, col3, col4  = st.columns(4)
    with col1:

        st.subheader("Editable Contracted Section Data")
        edited_contracted_section_df = st.data_editor(contracted_section_df.T)
    with col2:

        st.subheader("original Contracted Section Data")
        contracted_section_df = st.dataframe(contracted_section_df.T)
    with col3:
        st.subheader("Editable Approach Section Data")
        edited_approach_section_df = st.data_editor(approach_section_df.T)
    with col4:
        st.subheader("Original Approach Section Data")
        approach_section_df = st.dataframe(approach_section_df.T)


    edaps = edited_approach_section_df.T
    edcs = edited_contracted_section_df.T
    edlobc = LOB_contraction_df.T
    st.divider()
    st.header("Contracted Section Data:")
    st.write(edlobc)
    scour_calculator = contraction_scour(edaps, edcs)
    parameters = loader.assign_parameters(edcs, edaps)
    st.write("Calculated Contraction Scour Depth:", np.round(scour_calculator.calculate_scour(),2))
    st.divider()
    st.header("Pier Scour Calculator")
    st.subheader("This application calculates the pier scour depth based on the given flow velocity, pier width, and flow depth.")
    st.header("Input Parameters for Pier Scour Calculation")
    number_bents = st.number_input("Enter the Number of Bent Groups for the Structure:", min_value=0.0, value=5.0, key="bents")
    pier_df = pd.DataFrame(np.nan, index=range(int(number_bents)), columns=[f"Col{i+1}" for i in range(5)])
    pier_df.columns = ["Bent Group", "Pier Width (ft)", "Flow Depth (ft)", "Flow Velocity (ft/s)", "Scour Type"]
    #set the benbt group as string
    pier_df["Bent Group"] = pier_df["Bent Group"].astype(str)

    edited_pier_df = st.data_editor(pier_df)
    st.write(f"pier width used to calculation for {edited_pier_df["Bent Group"][0]}: {edited_pier_df["Pier Width (ft)"].values[0]}")
    st.divider()
