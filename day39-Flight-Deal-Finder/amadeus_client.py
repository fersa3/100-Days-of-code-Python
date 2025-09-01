from os import environ
from dotenv import load_dotenv
import requests

class AmadeusClient:
    """
        This class is responsible for:
        1. Authenticate with Amadeus API.
        2. Make HTTP requests.
        3. Handle conexion errors.
    """
    def __init__(self):
        load_dotenv()
        self._api_key = environ.get("AMADEUS_API_KEY")
        self._api_secret = environ.get("AMADEUS_API_SECRET")
        self.token_endpoint = environ.get("AMADEUS_AUTH_SERVER")

        self._token = None
        self.base_url = "https://test.api.amadeus.com"

    def _get_new_token(self) -> object:
        """
        Generates the authentication token used for accessing the Amadeus API.
        :return:
            str: The new access token obtained from the API response.
        """
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }
        response = requests.post(url=self.token_endpoint, headers=header, data=body)

        if response.status_code == 200:
            # print(f"Your token is {response.json()['access_token']}")
            # print(f"Your token expires in {response.json()['expires_in']}")
            self._token = response.json()['access_token']
            return self._token
        else:
            print(f"Error while getting token: {response.status_code}")
            print(response.text)
            return None

    def get_token(self):
        """
        Function to get current token and get a new one ONLY if necessary.
        :return:
            str: Current token if exists, if not generates it.
        """
        if self._token is None:
            self._token = self._get_new_token()
        return self._token

    def make_request(self, endpoint, params=None, version="v1"):
        """
        Generic function with the base to make requests to Amadeus API.
        Args:
            endpoint (str): to complete the base url of the API.
            params (dict): Optional params required for the desired request.
            version (str): API version ("v1", "v2", etc...)
        :return:
            if response:
                returns response JSON
            else:
                returns None and prints error
        """
        url = f"{self.base_url}/{version}{endpoint}"
        headers = {
            "accept": "application/vnd.amadeus+json",
            "Authorization": f"Bearer {self.get_token()}"
        }

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error in API request: {response.status_code}")
            print(response.text)
            return None
