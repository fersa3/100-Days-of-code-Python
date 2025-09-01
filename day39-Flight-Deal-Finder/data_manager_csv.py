import time
import pandas as pd
from flight_search import FlightSearch

class DataManagerCsv:
    """
        This class is responsible for interacting with the CSV file.
    """
    def __init__(self):
        self.sheet_df = pd.read_csv("flight_deals.csv")

    def get_sheet_data(self):
        """ Gets the data from the csv and returns a data frame """
        return self.sheet_df

    def get_cities_without_iata(self):
        """ Gets the list of cities on the CSV without a IATA code, so it does not populate everything everytime the code is run. """
        # Mask is a boolean True/False array that indicates which rows are compliant with a condition.
        iata_code_column = self.sheet_df['IATA Code']
        mask = pd.isna(iata_code_column) | (iata_code_column == '') | (iata_code_column == 'nan')
        cities_without_iata = self.sheet_df[mask]['City'].tolist()
        return cities_without_iata



    def update_iata_code(self, city, iata_code):
        """ Updates the IATA code column on the df for a specific city. """
        self.sheet_df['IATA Code'] = self.sheet_df['IATA Code'].astype('object') # Assing the type of value since the beginning to avoid FutureWarning
        mask = self.sheet_df['City'] == city
        self.sheet_df.loc[mask, 'IATA Code'] = iata_code


    def save_csv(self):
        """ Saves changes in the CSV file. """
        try:
            self.sheet_df.to_csv('flight_deals.csv', index=False)
            print("CSV updated successfully! 😊")
            return True
        except Exception as e:
            print(f"Error reloading CSV: {e}")
            return False
