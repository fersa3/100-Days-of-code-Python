import time
from datetime import timedelta, datetime
from pprint import pprint

class FlightData:
    """
        This class is responsible for:
        1. Search IATA codes.
        2. Specific logic of flights search.
    """
    def __init__(self, amadeus_client):
        # CLASS COMPOSITION: FlightSearch HAS an AmadeusClient
        self.client = amadeus_client

    def search_cheapest_flight_offer(self, destination_iata, destination_city_name):
        """
                Searches for the flight offers in Amadeus API that leave anytime between tomorrow and in 1 month (30 days) time.
                Uses API v2.
                Args:
                   destination_iata (str): Destination IATA code (e.g., "PAR" for Paris)
                   destination_city_name (str): City name for display (e.g., "Paris")
                :return:
                    Cheapest flight data for that city:
                    cheapest_flight_data = {
                        lowest_price: lowest_price,
                        origin: iataOrigin,
                        destination: iataDestination,
                        out_date: out_date,
                        return_date: return_date,
                    }
                """
        tomorrow = datetime.now() + timedelta(days=1)
        one_month_from_today = datetime.now() + timedelta(days=(1 * 30))

        endpoint = "/shopping/flight-offers"
        params = {
            "originLocationCode": "LON",
            "destinationLocationCode": destination_iata,
            "departureDate": tomorrow.strftime("%Y-%m-%d"),
            "returnDate": one_month_from_today.strftime("%Y-%m-%d"),
            "adults": 1,
            # "nonStop": "true", # found some inconsistency in Amadeus API, if I set this value to true, then 'data' is empty...
            "currencyCode": "GBP",
            "max": 10,
        }

        # Use the Client to make the request (use v2):
        data = self.client.make_request(endpoint, params, version="v2")

        # Default structure in case there is no flight data available.
        cheapest_flight_data = {
            "lowest_price": "N/A",
            "origin": "N/A",
            "destination": "N/A",
            "out_date": "N/A",
            "return_date": "N/A",
        }
        
        # List to store all valid flights (non-Stop)
        valid_flights = []

        print(f"Getting flights for {destination_city_name}")

        # Filter data to get only non-stop flights:
        for flight in data['data']:
            time.sleep(0.1)
            try:
                if flight['itineraries'][0]['segments'][1]:
                    # print("Has stopovers")
                    continue
            except IndexError:
                try:
                    trip_departure = flight['itineraries'][0]['segments'][0]['departure']['iataCode']
                    out_date_raw = flight['itineraries'][0]['segments'][0]['departure']['at']
                    out_date = datetime.fromisoformat(out_date_raw.replace('T', ' '))
                    trip_arrival = flight['itineraries'][0]['segments'][0]['arrival']['iataCode']
                    return_departure = flight['itineraries'][1]['segments'][0]['departure']['iataCode']
                    return_date_raw = flight['itineraries'][1]['segments'][0]['departure']['at']
                    return_date = datetime.fromisoformat(return_date_raw.replace('T', ' '))
                    return_arrival = flight['itineraries'][1]['segments'][0]['arrival']['iataCode']
                    price = float(flight['price']['total'])

                    # Store flight data
                    flight_info = {
                        "price": price,
                        "origin": trip_departure,
                        "destination": trip_arrival,
                        "out_date": out_date.strftime("%Y-%m-%d"),
                        "return_date": return_date.strftime("%Y-%m-%d"),
                        "return_origin": return_departure,
                        "return_destination": return_arrival,
                        "full_data": flight, # in case more data is needed later...
                    }
                    valid_flights.append(flight_info)
                except (IndexError, KeyError) as e:
                    print(f"Error while processing flight data: {e}")
                    continue

        # If there are valid flights (non-Stop), then get the cheapest one:
        if valid_flights:
            cheapest_flight = min(valid_flights, key=lambda  x: x['price'])

            cheapest_flight_data = {
                "price": cheapest_flight['price'],
                "origin": cheapest_flight['origin'],
                "destination": cheapest_flight['destination'],
                "out_date": cheapest_flight['out_date'],
                "return_date": cheapest_flight['return_date'],
            }

            print(f"{destination_city_name}: £{cheapest_flight['price']}")
        else:
            print(f"Couldn't find non-Stop flights to {destination_city_name}")

        return cheapest_flight_data
