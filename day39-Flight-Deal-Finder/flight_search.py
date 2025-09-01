class FlightSearch:
    """
        This class is responsible for:
        1. Search IATA codes.
        2. Specific logic of flights search.
    """
    def __init__(self, amadeus_client):
        # CLASS COMPOSITION: FlightSearch HAS an AmadeusClient
        self.client = amadeus_client

    def get_iata_code(self, city_name):
        """
        Searches for the city_name in Amadeus API
        :param city_name: Name of the city to look for an airport.
        :return:
            IATA code of the airport on that city
        """
        endpoint = "/reference-data/locations/cities"
        params = {
            "keyword": city_name,
            "max": 1,
            "include": "AIRPORTS"
        }

        # Use the Client to make the request:
        data = self.client.make_request(endpoint, params)

        # Super make sure data has the expected value
        if data and 'data' in data and len(data['data'])>0:
            try:
                return data['data'][0]['iataCode']
            except KeyError:
                print("No IATA Code data available for that city")
                return None
        return None
