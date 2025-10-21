import pandas as pd

from utils.data_io.download_stage_data import download_usgs_data, load_flow_data, create_location_plot


def process_data(usgs_station_id, min, max):
    """
    Downloads and processes USGS stage data for a given station ID.
    
    Args:
        usgs_station_id (str): The USGS station ID.
        
    Returns:
        pd.DataFrame: A DataFrame containing the processed stage data.
        dict: A dictionary containing site information.
    """
    # Download the USGS data
    file_path, info_path = download_usgs_data(usgs_station_id)
    data_df = load_flow_data(file_path, min, max)
    
    create_location_plot(info_path, usgs_station_id)

    return data_df
    
    