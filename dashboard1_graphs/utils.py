import pandas as pd
import numpy as np

def bucket_1(df, district):
    """
    Bucket 1: Compound Annual Growth Rate (CAGR)
    This bucket calculates the CAGR of Rent Price for the selected district (or the mean Rent Price across all districts if "All" is selected).
    Data is filtered to start from 2012 to ensure all districts have data.
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'Date', 'District', and 'Rent_Price' columns.
    district (str): Selected district or "All".
    
    Returns:
    str or float: CAGR as a percentage, rounded to 2 decimal places, or "N/A" if calculation is not possible.
    """
    # Validate input DataFrame
    if df.empty or 'Date' not in df.columns or 'Rent_Price' not in df.columns or 'District' not in df.columns:
        return "N/A"
    
    # Ensure Date is in datetime format
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if df['Date'].isna().any():
        return "N/A"
    
    # Filter data to start from 2012
    df = df[df['Date'] >= pd.to_datetime('2012-01-01')]
    if df.empty:
        return "N/A"
    
    # Ensure Rent_Price is numeric and handle NaN values
    df['Rent_Price'] = pd.to_numeric(df['Rent_Price'], errors='coerce')
    if df['Rent_Price'].isna().all():
        return "N/A"
    
    # Filter for the selected district or calculate mean for "All"
    if district == "All":
        # Calculate the mean Rent_Price across all districts for each date
        df_district = df.groupby('Date')['Rent_Price'].mean().reset_index()
    else:
        # Filter for the selected district
        df_district = df[df['District'] == district]
    
    if df_district.empty or len(df_district) < 2:
        return "N/A"
    
    # Sort by date to ensure correct first and last values
    df_district = df_district.sort_values('Date')
    
    # Drop any rows with NaN in Rent_Price after grouping
    df_district = df_district.dropna(subset=['Rent_Price'])
    if len(df_district) < 2:
        return "N/A"
    
    # Get the first and last rent prices
    initial_price = df_district['Rent_Price'].iloc[0]
    final_price = df_district['Rent_Price'].iloc[-1]
    
    # Check for NaN or invalid prices
    if pd.isna(initial_price) or pd.isna(final_price) or initial_price <= 0 or final_price < 0:
        return "N/A"
    
    # Calculate the number of years between the first and last date
    initial_date = df_district['Date'].iloc[0]
    final_date = df_district['Date'].iloc[-1]
    years = (final_date - initial_date).days / 365.25  # Approximate years, accounting for leap years
    
    if years <= 0:  # Avoid division by zero
        return "N/A"
    
    # Calculate CAGR
    cagr = ((final_price / initial_price) ** (1 / years)) - 1
    
    # Check for NaN or invalid CAGR
    if pd.isna(cagr) or not np.isfinite(cagr):
        return "N/A"
    
    return round(cagr * 100, 2)

def bucket_2(df, district):
    """
    Bucket 2: Maximum Rent Price
    This bucket shows the maximum rent price recorded for the selected district (or overall if "All" is selected).
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'Rent_Price' column.
    district (str): Selected district or "All".
    
    Returns:
    str or float: Maximum rent price, rounded to 2 decimal places, or "N/A" if no data is available.
    """
    if district == "All":
        df_district = df.copy()
    else:
        df_district = df[df['District'] == district]
    
    if df_district.empty:
        return "N/A"
    
    max_price = df_district['Rent_Price'].max()
    if pd.isna(max_price) or max_price <= 0:  # Check for invalid max price
        return "N/A"
    return round(max_price, 2)

def bucket_3(df, district):
    """
    Bucket 3: Rent Price Ranking
    This bucket returns the ranking (position) of the selected district based on its average Rent Price
    compared to other districts' averages.
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'District' and 'Rent_Price' columns.
    district (str): Selected district or "All".
    
    Returns:
    str or int: Ranking position (1 is highest), or "N/A" if ranking is not possible.
    """
    if district == "All":
        return "N/A"
    
    # Calculate the average rent price for each district
    district_avgs = df.groupby('District')['Rent_Price'].mean().reset_index()
    
    # Check if the selected district exists in the data
    if district not in district_avgs['District'].values:
        return "N/A"
    
    # Rank districts by average rent price in descending order
    district_avgs['Rank'] = district_avgs['Rent_Price'].rank(ascending=False, method='min')
    
    # Get the rank of the selected district
    rank = district_avgs[district_avgs['District'] == district]['Rank'].iloc[0]
    
    if pd.isna(rank):
        return "N/A"
    return int(rank)

def bucket_4(df, district):
    """
    Bucket 4: Average Rent Price
    This bucket calculates the average rent price for the selected district (or overall if "All" is selected).
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'Rent_Price' column.
    district (str): Selected district or "All".
    
    Returns:
    str or float: Average rent price, rounded to 2 decimal places, or "N/A" if no data is available.
    """
    if district == "All":
        df_district = df.copy()
    else:
        df_district = df[df['District'] == district]
    
    if df_district.empty:
        return "N/A"
    
    avg_price = df_district['Rent_Price'].mean()
    if pd.isna(avg_price) or avg_price <= 0:  # Check for invalid average
        return "N/A"
    return round(avg_price, 2)

def bucket_5(price, surface=100):
    """
    Bucket 5: Required Monthly Income
    This bucket calculates the monthly income needed based on the price per square meter and surface area,
    assuming that 40% of the total income is dedicated to rent.
    """
    rent_expenditure = price * surface
    monthly_income = rent_expenditure / 0.4
    return monthly_income


def bucket_5(price_2m, surface=100):
    """
    Function to calculate the income based on the price per square meter and surface area, assuming that the amount dedicated
    to rent is 30% of the total income.

    Parameters:
    price_2m (float): Price per square meter.
    surface (float): Surface area in square meters. Default is 100.

    Returns:
    float: Monthly income.
    """
    # Calculate the total income based on the price per square meter and surface area
    rent_expenditure = price_2m * surface

    # Calculate the monthly income based on the assumption that 40% of the total income is dedicated to rent
    monthly_income = rent_expenditure / 0.40

    return monthly_income