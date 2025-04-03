import pandas as pd
import numpy as np



def income_calculator(price_2m, surface=100):
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

# Example usage
price_2m = 27.5  # Example price per square meter
surface = 100  # Example surface area in square meters
monthly_income = income_calculator(price_2m, surface)
print("Monthly income:", monthly_income)