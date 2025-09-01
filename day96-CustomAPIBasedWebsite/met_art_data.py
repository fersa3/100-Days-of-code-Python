import requests
import random
from pprint import pprint


class MetAPIClient:
    """Simple client for the Metropolitan Museum of Art API"""
    BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

    def search_artworks(self, artist_name: str, has_images: bool = True, limit: int = 50):
        """
        Search for artworks by a specific artist.
        Randomly sample a limited number of artworks from the result set.
        """
        try:
            # First get object IDs matching the search
            search_url = f"{self.BASE_URL}/search"
            params = {
                'q': artist_name,
                'hasImages': str(has_images).lower()
            }

            response = requests.get(search_url, params=params)
            response.raise_for_status()
            object_ids = response.json().get('objectIDs', [])

            # Check if the total number of object IDs is larger than the limit
            if len(object_ids) > limit:
                # Randomly sample the specified number of object IDs
                sampled_object_ids = random.sample(object_ids, limit)
            else:
                # If there are fewer object IDs than the limit, take all of them
                sampled_object_ids = object_ids

            # Get full details for first 10 artworks from selected artistic movement:
            artworks_to_display = []
            for object_id in sampled_object_ids:
                try:
                    response = requests.get(f"{self.BASE_URL}/objects/{object_id}")
                    response.raise_for_status()
                    artwork_data = response.json()

                    # Only add artwork if it has a non-empty primary image link and matches the artist name
                    if artist_name in artwork_data['artistDisplayName']:
                        artworks_info = {
                            'title': f'{artwork_data['title']}',
                            'artist': f'{artwork_data['artistDisplayName']}',
                            'date': f'{artwork_data['objectDate']}',
                            'medium': f'{artwork_data['medium']}',
                            'img_url': f'{artwork_data['primaryImage']}',
                            'repository': f'{artwork_data['repository']}',
                        }
                        artworks_to_display.append(artworks_info)

                except requests.exceptions.RequestException:
                    continue

            if len(artworks_to_display) > 10:
                artworks_to_display = random.sample(artworks_to_display, 10)

            return artworks_to_display

        except requests.exceptions.RequestException as e:
            print(f"Error fetching artistic movement data: {e}")
            return []
