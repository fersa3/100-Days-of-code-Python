# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.
# I used a local csv instead of Sheety API because I exceeded the max free calls in a month and I would've had to wait or pay... lol
import time
from pprint import pprint
from os import environ

import pandas as pd
from dotenv import load_dotenv
from data_manager_csv import DataManagerCsv
from amadeus_client import AmadeusClient
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager

def populate_missing_iata_codes(flight_search, data_manager):
    """
        Populates the missing IATA codes if any.
        1. Check if there are any empty spaces in the IATA column in the CSV.
        2. Run flight_search.get_iata_code() only for the empty cities.
        3. Save changes in the .csv file.
    """

    cities_without_iata = data_manager.get_cities_without_iata()

    if not cities_without_iata:
        print("All cities in the CSV have IATA codes 😊")
        return # STOP and not continue with the rest of the function (equivalent to an if-else)

    for city in cities_without_iata:
        iata_code = flight_search.get_iata_code(city)
        if iata_code:
            data_manager.update_iata_code(city, iata_code)

    data_manager.save_csv()

def search_all_destinations_cheapest_flight(flight_data, data_manager):
    """ Searches for the cheapest flights in all destinations on CSV. """

    sheet_data_df = data_manager.get_sheet_data()
    print(f"Searching flights for {len(sheet_data_df)} destinations from London...")

    all_cities_cheapest_flights = {}

    for _, row in sheet_data_df.iterrows():
        city_name = row['City']
        iata_code = row['IATA Code']

        cheapest_flight_data_to_current_city = flight_data.search_cheapest_flight_offer(destination_iata=iata_code, destination_city_name=city_name)
        all_cities_cheapest_flights[city_name] = cheapest_flight_data_to_current_city

    return all_cities_cheapest_flights

def is_cheapest_price_lower_than_sheet(data_manager, flights):
    """ Compares the prices from the flight search against the typical cheap flight price.  """
    sheet_data_df = data_manager.get_sheet_data()

    # Convert flights to DataFrame
    flights_df = pd.DataFrame([
        {'city_name': city, **details}
        for city, details in flights.items()
    ])

    comparison_df = sheet_data_df.merge(flights_df, left_on='City', right_on="city_name", how='right')

    for _, flight in comparison_df.iterrows():
        if flight['price'] < flight['Lowest Price']:
            text = f"Cheap flight alert! 🌍✈️. Only £{flight['price']} to fly from {flight['origin']} to {flight['destination']}, {flight['city_name']}, on {flight['out_date']} until {flight['return_date']}"
            return text


if __name__ == "__main__":
    load_dotenv()

    # Initiate all objects, just once:
    amadeus_client = AmadeusClient()
    flight_search = FlightSearch(amadeus_client)
    flight_data = FlightData(amadeus_client)
    data_manager = DataManagerCsv()
    notifiquier = NotificationManager()

    try:
        populate_missing_iata_codes(flight_search, data_manager)
        all_cheap_flights = search_all_destinations_cheapest_flight(flight_data, data_manager)
        text_customer = is_cheapest_price_lower_than_sheet(data_manager, all_cheap_flights)
        notifiquier.send_sms_to_customer(text_customer)

    except Exception as e:
        print(f"Fatal error while running main process 💀: {e}")



    # TODO 6: Create a sharable Form linked to your sheet... supongo que tendré que hacerlo con Microsoft para tener un excel en mi versión.
    # TODO 7: Destinations without direct flights.
    # TODO 8: Retrieve your customer emails.
    # TODO 9: Email all your customers.





