import os
import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static



def download_usgs_data(site_id):
    """
    Downloads the peak flow data from the given URL and returns the file path.
    
    Args:
        url (str): The URL to download the peak flow data from.
        
    Returns:
        str: The path to the downloaded file.
    """
    try:
        
        yesterday = pd.Timestamp.now() - pd.Timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
    
        url = f"https://waterdata.usgs.gov/nwis/measurements?site_no={site_id}&agency_cd=USGS&format=rdb_expanded"

        if not os.path.exists("data/temp"):
            os.makedirs("data/temp")
        file_path = requests.get(url)
        
        #save the file to the temp directory
        with open(os.path.join("data/temp","flow_data.txt"), 'wb') as f:
            f.write(file_path.content)
        

        file_path = os.path.join("data/temp","flow_data.txt")
        
        info_path = download_site_coords(site_id)
        
        return file_path, info_path
    except Exception as e:
        st.error(f"Error downloading peak flow data: {e}")
       
        return None
    

def extract_site_info(info_path):
    """
    Extracts site information from the info file.
    
    Args:
        info_path (str): The path to the info file.
        
    Returns:
        dict: A dictionary containing site information.
    """
    #try:
    with open(info_path, 'r') as f:
        lines = f.readlines()
    site_info = {}
    for line in lines:
        #find lines that contain latitude and longitude
        if "latitude" in line.lower() or "longitude" in line.lower():
            parts = line.strip().split(' ')
            for part in parts:
                if part == "" or part == " ":
                    parts.remove(part)
            
            
            latitude = parts[1]
            latitude = latitude.replace(',', ' ').replace('&#176', ' ').replace(';', ' ').replace("'", ' ').replace('"', ' ')
            
            latitude = latitude.split(" ")
            
            decimal_lat = float(latitude[0]) + (float(latitude[2]) / 60) + (float(latitude[3])/ 3600)
            longitude = parts[4]
            longitude = longitude.replace(',', ' ').replace('&#176', ' ').replace(';', ' ').replace("'", ' ').replace('"', ' ')
            longitude = longitude.split(" ")
            
            decimal_long = float(longitude[0]) + (float(longitude[2]) / 60) + (float(longitude[3])/ 3600)
            location_df = pd.DataFrame({'latitude': [decimal_lat], 'longitude': [decimal_long*-1]})
            return location_df
        

def download_site_coords(site_id):
    """
    Downloads the site coordinates from the USGS website.
    
    Args:
        site_id (str): The USGS site ID.
        
    Returns:
        dict: A dictionary containing the site coordinates.
    """
    information_url = f"https://waterdata.usgs.gov/nwis/inventory/?site_no={site_id}&agency_cd=USGS"
    info_path = requests.get(information_url)
    with open(os.path.join("data/temp","info_data.txt"), 'wb') as f:
        f.write(info_path.content)
    info_path = os.path.join("data/temp","info_data.txt")
    return info_path


def load_flow_data(file_path, min, max):
    """
    Loads the peak flow data from the given file path into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the peak flow data file.
        
    Returns:
        pd.DataFrame: The loaded peak flow data.
    """
    try:
        data_df = pd.DataFrame()
        df = pd.read_csv(file_path, delimiter='\t', on_bad_lines='skip', skiprows=14, header = 0)
        
        #delete the first row of the dataframe df
        df = df.iloc[1:]
        
        data_df['date'] = pd.to_datetime(df['measurement_dt'],format='mixed')
        data_df['stage'] = pd.to_numeric(df['gage_height_va'], errors='coerce')
        data_df['flow'] = pd.to_numeric(df['discharge_va'], errors='coerce', downcast='float')
        data_df = data_df[['date', 'stage', 'flow']]
        
        data_df = data_df.dropna()
        mean_flow = data_df['flow'].mean()
        std_flow = data_df['flow'].std()
       # min_val = float(min)
       # max_val = float(max)
        #make sure the flow is within the min and max range and remove any rows that are not
        data_df = data_df[(data_df['flow'] >= min) & (data_df['flow'] <=  max)]
        
        
        #add column contining just the year
        data_df['year'] = data_df['date'].dt.year
        data_df['month'] = data_df['date'].dt.month
        data_df['day'] = data_df['date'].dt.day
        
        
        
        return data_df, mean_flow, std_flow
    except Exception as e:
        st.error(f"Error loading peak flow data: {e}")
       
        return None
    
def create_location_plot(info_path, site_id):
    location_df = extract_site_info(info_path)
    attr = ('Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>')
    tiles = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}'
    
    m = folium.Map(location=[location_df["latitude"],location_df["longitude"]], tiles=tiles,attr = "Aerial Imagery", zoom_start=16)
    
    folium.Marker(
        [location_df["latitude"], location_df["longitude"]], popup=f"Gage {site_id} location", tooltip=f"Gage {site_id} location"
    ).add_to(m)
    
    #folium.LayerControl().add_to(m)
    st.header(f"Gage {site_id} Location")
    folium_static(m, width=3000, height=500)
            