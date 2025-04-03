import pandas as pd
import numpy as np

def bucket_1(df, district):
    """
    Bucket 1: Compound Annual Growth Rate (CAGR)
    This bucket calculates the CAGR of Rent Price for the selected district (or for all districts if "All" is selected).
    """
    if district == "All":
        df_district = df.copy()
    else:
        df_district = df[df['District'] == district]
    
    if df_district.empty or len(df_district) < 2:
        return "N/A"
    
    # Calculate CAGR using the first and last recorded Rent_Price
    cagr = ((df_district['Rent_Price'].iloc[-1] / df_district['Rent_Price'].iloc[0]) ** 
            (1 / (len(df_district) - 1))) - 1
    return round(cagr * 100, 2)

def bucket_2(df, district):
    """
    Bucket 2: Maximum Rent Price
    This bucket shows the maximum rent price recorded for the selected district (or overall if "All" is selected).
    """
    if district == "All":
        df_district = df.copy()
    else:
        df_district = df[df['District'] == district]
    
    if df_district.empty:
        return "N/A"
    
    max_price = df_district['Rent_Price'].max()
    return round(max_price, 2)

def bucket_3(df, district):
    """
    Bucket 3: Rent Price Ranking
    This bucket returns the ranking (position) of the selected district based on Rent Price.
    If the district is "All" or if there is not enough data, it returns "N/A".
    """
    if district == "All":
        return "N/A"
    else:
        df_district = df[df['District'] == district]
        if df_district.empty:
            return "N/A"
        # Rank all records in the district in descending order
        position = df_district['Rent_Price'].rank(ascending=False).iloc[0]
        # If the ranking result is NaN, return "N/A"
        if pd.isna(position):
            return "N/A"
        return int(position)

def bucket_4(df, district):
    """
    Bucket 4: Average Rent Price
    This bucket calculates the average rent price for the selected district (or overall if "All" is selected).
    """
    if district == "All":
        df_district = df.copy()
    else:
        df_district = df[df['District'] == district]
    
    if df_district.empty:
        return "N/A"
    
    avg_price = df_district['Rent_Price'].mean()
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
    monthly_income = rent_expenditure / 0.4

    return monthly_income