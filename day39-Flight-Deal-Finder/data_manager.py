import requests
from os import environ


class DataManager:
    #This class is responsible for talking to the Google Sheet.
    def __init__(self, sheet_name="prices"):
        """ Inilializes the data manager

        Args:
            endpoint (str): Sheety API base URL
            token (str, optional): Auth token
            sheet_name (str): Name of spreadsheet sheet
            """
        self.endpoint = environ.get("SHEETY_ENDPOINT")
        self.sheet_name = sheet_name
        self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {environ.get("SHEETY_TOKEN")}"
            }

    def get_sheet_data(self):
        """ Gets the data from the sheet and returns a json """
        try:
            response = requests.get(self.endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()['prices']
        except requests.exceptions.RequestException as e:
            print(f"Error while getting the date: {e}")
            return None

    def populate_iata_column(self, sheet_data, iata_code):
        """ Populates IATAcode column with 'TESTING'
        https://api.sheety.co/29f9677156b634049d623e2d120525a7/flightDeals/prices/[Object ID]
        """
        self.sheet_data = sheet_data
        url = f"{self.endpoint}"
        body = {
            "price": {
                "iataCode": iata_code
            }
        }
        for i in range(2, len(sheet_data)+2):
            response = requests.put(f"{url}/{i}", json=body, headers=self.headers)

            if response.status_code == 200:
                response.json()
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
