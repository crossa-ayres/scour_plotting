import pandas as pd
import streamlit as st

class DataLoader:
    """A class to load and process data from CSV files."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self) -> pd.DataFrame:
        """Load data from the CSV file."""
        return pd.read_csv(self.file_path)

    def generate_scour_df(self) -> pd.DataFrame:
        """Generate summary statistics of the data."""
        data = self.load_data()
        contracted_sections = data[data.iloc[:, 0].str.contains("Contracted section", na=False)]
        contracted_section_headers = [line.split(" ")[0:-1] for line in contracted_sections.iloc[:, 0]]
        contracted_section_headers = [" ".join(header) for header in contracted_section_headers]
        contracted_section_data = [line.split(" ")[-1] for line in contracted_sections.iloc[:, 0]]

        mask = data.iloc[:, 0].str.contains("Left overbank", na=False)
        LOB = data.iloc[:][mask]
        mask = data.iloc[:, 0].str.contains("Right overbank", na=False)
        ROB = data.iloc[:][mask]
        "Left overbank (approach; Used for overbank contraction scour calculations):"
        
        #find the index in LOB that contains "Left overbank (contracted; Used for overbank contraction scour calculations):" amd make new dataframe using the rows below
        #mask_contracted = LOB.iloc[:, 0].str.contains("Left overbank (contracted; Used for overbank contraction scour calculations):", na=False)
        #contracted_sections_index = LOB[mask_contracted:].index[0]
        
        LOB_approach = []
        LOB_contracted = []
        ROB_approach = []
        ROB_contracted = []
        for i, val in enumerate(LOB.values):
            LOB_approach.append(val[0])
            if "Left overbank (contracted; Used for overbank contraction scour calculations):" in val[0]:
                break
        start = False
        for i, val in enumerate(LOB.values):
            if "Left overbank (contracted; Used for overbank contraction scour calculations):" in val[0]:
                start = True
            if start:
                LOB_contracted.append(val[0])
        for i, val in enumerate(ROB.values):
            ROB_approach.append(val[0])
            if "Right overbank (contracted; Used for overbank contraction scour calculations):" in val[0]:
                break
        
        start = False
        for i, val in enumerate(ROB.values):
            if "Right overbank (contracted; Used for overbank contraction scour calculations):" in val[0]:
                start = True
            if start:
                ROB_contracted.append(val[0])

        LOB_approach = LOB_approach[1:-1]
        LOB_contracted = pd.DataFrame(LOB_contracted[1:])
        ROB_approach = ROB_approach[1:-1]
        ROB_contracted = ROB_contracted[1:]

        
        LOB_contraction_headers = [line.split(" ")[0:-1] for line in LOB_contracted.iloc[:, 0]]
        LOB_contraction_headers = [" ".join(header) for header in LOB_contraction_headers]
        LOB_contraction_data = [line.split(" ")[-1] for line in LOB_contracted.iloc[:, 0]]
        contracted_section_df = pd.DataFrame([contracted_section_data], columns=contracted_section_headers)
        LOB_contraction_df = pd.DataFrame([LOB_contraction_data], columns=LOB_contraction_headers)

        approach_sections = data[data.iloc[:, 0].str.contains("Approach section", na=False)]
        approach_section_headers = [line.split(" ")[0:-1] for line in approach_sections.iloc[:, 0]]
        approach_section_headers = [" ".join(header) for header in approach_section_headers]
        approach_section_data = [line.split(" ")[-1] for line in approach_sections.iloc[:, 0]]
        approach_section_df = pd.DataFrame([approach_section_data], columns=approach_section_headers)
        
        return contracted_section_df, approach_section_df, LOB_contraction_df
    def assign_parameters(self, contracted_section_df, approach_section_df) -> None:
        """Assign parameters to the data loader."""
        contracted_parameters = {}
        approach_parameters = {}
        #for key, value in contracted_section_df.items():
        #    st.write(key, value.values[0])
        
    






