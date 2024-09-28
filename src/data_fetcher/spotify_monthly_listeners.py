import requests
from bs4 import BeautifulSoup

class MonthlyListeners:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    @staticmethod
    def fetch_listeners(artist_id, spotify_url):
        """Fetch monthly listeners for a given artist from their Spotify page."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(spotify_url, headers=headers)
            response.raise_for_status()

            # Debugging: print the response content to see what you're getting
            print(response.content.decode('utf-8'))  # Print the raw HTML response

            soup = BeautifulSoup(response.content, 'html.parser')
            # Use the correct class to find the monthly listeners
            monthly_listeners_tag = soup.find('span', class_='Ydwa1P5GkCggtLlSvphs')
            if monthly_listeners_tag:
                listeners_text = monthly_listeners_tag.text.strip()

                # Remove commas and dots for conversion
                listeners = int(listeners_text.replace('.', '').replace(' ', ''))
                return listeners
            else:
                print(f"Could not find monthly listeners for {spotify_url}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data from Spotify: {e}")
            return None
        except ValueError as e:
            print(f"Error converting monthly listeners to an integer: {e}")
            return None

    def save_to_db(self, artist_id, listeners):
        """Save the fetched monthly listeners to the database."""
        if isinstance(listeners, int):
            cursor = self.db_connector.connect().cursor()
            query = """
                INSERT INTO monthly_listeners (artist_id, listeners)
                VALUES (%s, %s)
            """
            cursor.execute(query, (artist_id, listeners))
            self.db_connector.connect().commit()
            print(f"Inserted {listeners} listeners for artist with ID {artist_id}")
        else:
            print(f"Invalid data type for listeners: {listeners}, expected int")

    def update_all_artists(self):
        """Fetch and save listeners for all artists in the database."""
        connection = self.db_connector.connect()  # Get the connection once
        cursor = connection.cursor()  # Use the cursor
        cursor.execute("SELECT artist_id, spotify_id FROM artists WHERE spotify_id IS NOT NULL")
        artists = cursor.fetchall()

        for artist_id, spotify_id in artists:
            spotify_url = f"https://open.spotify.com/artist/{spotify_id}"
            listeners = self.fetch_listeners(artist_id, spotify_url)
            if listeners is not None:
                self.save_to_db(artist_id, listeners)

        cursor.close()  # Close the cursor when done
