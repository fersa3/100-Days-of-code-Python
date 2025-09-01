import requests
import random
import time
from pprint import pprint

CLIENT_ID = '18709855a39fa3a65fc4'
CLIENT_SECRET = 'f82031084f77322fd95075bd1f277222'


def get_artsy_token():
    """ Function to request the Artsy API token.
    Returns a json wih the token and expiration. """

    token_url = "https://api.artsy.net/api/tokens/xapp_token"
    payload= {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(token_url, json=payload)
    response.raise_for_status() # Raise an exception if the token request fails
    return response.json()['token']


def get_artist_url(token, artist_name):
    """ Function to retrieve the artist url from the artist name. """
    headers = {
        'X-Xapp-Token': token
    }
    search_url = f"https://api.artsy.net/api/search?q={artist_name}&type=artist"
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()
    try:
        artist_url = response.json()['_embedded']['results'][0]['_links']['self']['href']
        return artist_url
    except IndexError:
        print("Artist info not available. Try with another one. (Display flash message)")

def fetch_artist_data(token, artist_url):
    """ Function to retrieve the artist data from the artist url. """
    headers = {
        'X-Xapp-Token': token
    }
    response = requests.get(artist_url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_artistic_movements(token, size=50):
    """ Function to fetch artistic movements (genes) from the API.
    Returns a list of names. """
    headers = {
        'X-Xapp-Token': token
    }
    api_url = f'https://api.artsy.net/api/genes?size={size}'

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    movements_data = response.json()['_embedded']['genes']
    all_artistic_movements = [(movement['id'], movement['name'])
                              for movement in movements_data
                              if not movement['name'].isdigit() and 'Century' not in movement['name']]
    return all_artistic_movements

def get_movement_data(token, movement_name):
    """ Fetch the artistic movement (gene) data using the gene name. """
    headers = {
        'X-Xapp-Token': token
    }

    movement_name_encoded = requests.utils.quote(movement_name)  # To avoid issues with special characters
    movement_url = f'https://api.artsy.net/api/genes/{movement_name_encoded}'
    response = requests.get(movement_url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_artwork_for_movement(token, movement_id):
    """ Fetch all artworks for a specific movement using the artworks URL. """
    headers = {
        'X-Xapp-Token': token
    }
    artwork_url = f"https://api.artsy.net/api/artworks?gene_id={movement_id}"  # Artworks URL from the movement data
    print(f"Requesting URL: {artwork_url}")  # For debugging
    print(f"Using token: {token}")  # Print token to verify

    response = requests.get(artwork_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")  # Print the full response content for debugging
    if response.status_code == 401:
        print("Authentication failed. Check if the token is correct or expired.")

    response.raise_for_status()
    return response.json()

def get_artwork_info(token, artwork):
    """ Fetch detailed info for a specific artwork. """
    headers = {
        'X-Xapp-Token': token
    }
    artwork_url = artwork['_links']['self']['href']
    response = requests.get(artwork_url, headers=headers)
    response.raise_for_status()
    artwork_data = response.json()

    # Get artist name from the artists link in the artwork data json
    artists_url = artwork['_links']['artists']['href']
    artist_response = requests.get(artists_url, headers=headers)
    artist_response.raise_for_status()
    artist_data = artist_response.json()
    # Extract the name of the artist from the artist_data json:
    artist_list = artist_data['_embedded']['artists']
    artist_name = artist_list[0].get('name', 'Unknown Artist')

    return {
        'title': artwork_data.get('title', 'Untitled'),
        'artist': artist_name,
        'img_url': artwork_data.get('_links', {}).get('image', {}).get('href', None).format(image_version='square'),
        'medium': artwork_data.get('medium', 'No description available.'),
        'date': artwork_data.get('date', 'Unknown date')
    }

def display_movement_info(token, movement_data):
    """ Display movement information and fetch 10 random artworks.
    Returns a tuple of (movement_description, list_of_artwork_details) """
    movement_description = movement_data.get('description', 'No description available.')
    pprint(movement_data)

    movement_id = movement_data['id']
    artworks_data = fetch_artwork_for_movement(token, movement_id) # Fetch all artworks for this movement
    pprint(f"Artworks data: {artworks_data}")
    # artworks = artworks_data.get('_embedded', {}).get('artworks', []) # Get the list of artworks from the response. (All in '_embedded' and 'artworks')
    # pprint(f"Artworks: {artworks}")
    # Select 10 random artworks from artworks list. Or less if there are no 10 available. Seed function ensure that the list of artworks displayed is different each time the function is called.
    # artworks_to_display = random.sample(artworks, min(10, len(artworks)))
    # Fetch detailed info for each of the 10 selected artworks:
    artwork_details = []
    # for artwork in artworks_to_display:
    #     try:
    #         details = get_artwork_info(token, artwork)
    #         artwork_info = {
    #             'title': details['title'],
    #             'artist': details['artist'],
    #             'img_url': details['img_url'],
    #             'medium': details['medium'],
    #             'date': details['date'],
    #         }
    #         artwork_details.append(artwork_info)
    #         #pprint(movement_data)
    #         #pprint(artwork_details)
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error fetching details for artwork: {e}")
    #         continue
    return movement_description, artwork_details
