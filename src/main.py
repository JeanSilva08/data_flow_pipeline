from src.models.album_songs import AlbumSongs
from src.models.artist import Artist
from src.models.song import Song
from src.models.album import Album
from src.models.playlist import Playlist
from src.scapers.spotify_monthly_listeners import MonthlyListeners
from src.apis.spotify_api import fetch_and_store_artist_data, fetch_and_store_songs_by_artist, SpotifyAPI
from src.database.db_connector import DBConnector
from dotenv import load_dotenv
import os
import sys

# Add the project root to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()


class ETLSystem:
    def __init__(self):
        """
        Initialize the ETL system with a database connection.
        """
        self.db = DBConnector(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        self.db.connect()
        self.spotify_api = SpotifyAPI()

    def display_menu(self):
        """
        Display the main menu options.
        """
        print("\nEscolha uma opção:")
        print("1: Adicionar Artista")
        print("2: Editar Artista")
        print("3: Deletar Artista")
        print("4: Adicionar Música")
        print("5: Editar Música")
        print("6: Deletar Música")
        print("7: Adicionar Playlist")
        print("8: Editar Playlist")
        print("9: Deletar Playlist")
        print("10: Adicionar Álbum")
        print("11: Editar Álbum")
        print("12: Deletar Álbum")
        print("13: Ouvintes Mensais")
        print("14: Seguidores Spotify")
        print("15: Salvar todas as músicas")
        print("16: Sair")
        print("17: Adicionar música a um álbum")
        print("18: Remover música de um álbum")
        print("19: Buscar todas as informações de um artista")

    def run(self):
        """
        Run the ETL system and handle user input.
        """
        while True:
            self.display_menu()
            choice = input("Digite a opção escolhida: ").strip()

            if choice == '1':
                self._add_artist()
            elif choice == '2':
                self._edit_artist()
            elif choice == '3':
                self._delete_artist()
            elif choice == '4':
                self._add_song()
            elif choice == '5':
                self._edit_song()
            elif choice == '6':
                self._delete_song()
            elif choice == '7':
                self._add_playlist()
            elif choice == '8':
                self._edit_playlist()
            elif choice == '9':
                self._delete_playlist()
            elif choice == '10':
                self._add_album()
            elif choice == '11':
                self._edit_album()
            elif choice == '12':
                self._delete_album()
            elif choice == '13':
                self._fetch_monthly_listeners()
            elif choice == '14':
                self._fetch_spotify_artist_data()
            elif choice == '15':
                self._fetch_songs_by_artist()
            elif choice == '16':
                print("Exiting...")
                break
            elif choice == '17':
                self._add_song_to_album()
            elif choice == '18':
                self._remove_song_from_album()
            elif choice == '19':
                self._fetch_all_artist_info()
            else:
                print("Invalid choice. Please try again.")

        self.close()

    def _add_artist(self):
        """
        Add a new artist to the database.
        """
        artist_data = self._get_artist_input()
        artist = Artist(**artist_data)  # Create an Artist instance with the collected data
        artist.save_to_db(self.db)  # Save the artist to the database
        print("Artist added successfully!")

    def _edit_artist(self):
        """
        Edit an existing artist in the database.
        """
        artist_id = input("Enter Artist ID to update: ").strip()

        # Fetch current artist data
        current_data = Artist.get_by_id(self.db, artist_id)
        if not current_data:
            print("Artist not found.")
            return

        # Display current data as placeholders
        print("\nCurrent Artist Data:")
        for key, value in current_data.items():
            print(f"{key}: {value}")

        # Get updated data from the user
        print("\nEnter new data (leave blank to keep current value):")
        updated_data = {}
        for key, value in current_data.items():
            if key == "artist_id":  # Skip the primary key
                continue
            new_value = input(f"{key} [{value}]: ").strip()
            updated_data[key] = new_value if new_value else value

        # Update the artist in the database
        Artist.update_in_db(self.db, artist_id, **updated_data)
        print("Artist updated successfully!")

    def _delete_artist(self):
        """
        Delete an artist from the database.
        """
        artist_id = input("Enter Artist ID to delete: ")
        Artist.delete_from_db(self.db, artist_id)
        print("Artist deleted successfully!")

    def _add_song(self):
        """
        Add a new song to the database.
        """
        song_data = self._get_song_input()
        Song.save_to_db(self.db, **song_data)
        print("Song added successfully!")

    def _edit_song(self):
        """
        Edit an existing song in the database.
        """
        song_id = input("Enter Song ID to update: ").strip()

        # Fetch current song data
        current_data = Song.get_by_id(self.db, song_id)
        if not current_data:
            print("Song not found.")
            return

        # Display current data as placeholders
        print("\nCurrent Song Data:")
        for key, value in current_data.items():
            print(f"{key}: {value}")

        # Get updated data from the user
        print("\nEnter new data (leave blank to keep current value):")
        updated_data = {}
        for key, value in current_data.items():
            if key == "song_id":  # Skip the primary key
                continue
            new_value = input(f"{key} [{value}]: ").strip()
            updated_data[key] = new_value if new_value else value

        # Update the song in the database
        Song.update_in_db(self.db, song_id, **updated_data)
        print("Song updated successfully!")

    def _delete_song(self):
        """
        Delete a song from the database.
        """
        song_id = input("Enter Song ID to delete: ")
        Song.delete_from_db(self.db, song_id)
        print("Song deleted successfully!")

    def _add_playlist(self):
        """
        Add a new playlist to the database.
        """
        playlist_name = input("Playlist Name (leave blank to use Spotify name): ")
        spotify_playlist_id = input("Spotify Playlist ID: ")
        Playlist.add_playlist_from_spotify(self.db, spotify_playlist_id, playlist_name)
        print("Playlist added successfully!")

    def _edit_playlist(self):
        """
        Edit an existing playlist in the database.
        """
        playlist_id = input("Enter Playlist ID to update: ").strip()

        # Fetch current playlist data
        current_data = Playlist.get_by_id(self.db, playlist_id)
        if not current_data:
            print("Playlist not found.")
            return

        # Display current data as placeholders
        print("\nCurrent Playlist Data:")
        for key, value in current_data.items():
            print(f"{key}: {value}")

        # Get updated data from the user
        print("\nEnter new data (leave blank to keep current value):")
        updated_data = {}
        for key, value in current_data.items():
            if key == "playlist_id":  # Skip the primary key
                continue
            new_value = input(f"{key} [{value}]: ").strip()
            updated_data[key] = new_value if new_value else value

        # Update the playlist in the database
        Playlist.update_in_db(self.db, playlist_id, **updated_data)
        print("Playlist updated successfully!")

    def _delete_playlist(self):
        """
        Delete a playlist from the database.
        """
        playlist_id = input("Enter Playlist ID to delete: ")
        Playlist.delete_from_db(self.db, playlist_id)
        print("Playlist deleted successfully!")

    def _add_album(self):
        """
        Add a new album to the database.
        """
        album_data = self._get_album_input()
        Album.save_to_db(self.db, **album_data)
        print("Album added successfully!")

    def _edit_album(self):
        """
        Edit an existing album in the database.
        """
        album_id = input("Enter Album ID to update: ").strip()

        # Fetch current album data
        current_data = Album.get_by_id(self.db, album_id)
        if not current_data:
            print("Album not found.")
            return

        # Display current data as placeholders
        print("\nCurrent Album Data:")
        for key, value in current_data.items():
            print(f"{key}: {value}")

        # Get updated data from the user
        print("\nEnter new data (leave blank to keep current value):")
        updated_data = {}
        for key, value in current_data.items():
            if key == "album_id":  # Skip the primary key
                continue
            new_value = input(f"{key} [{value}]: ").strip()
            updated_data[key] = new_value if new_value else value

        # Update the album in the database
        Album.update_in_db(self.db, album_id, **updated_data)
        print("Album updated successfully!")

    def _delete_album(self):
        """
        Delete an album from the database.
        """
        album_id = input("Enter Album ID to delete: ")
        Album.delete_from_db(self.db, album_id)
        print("Album deleted successfully!")

    def _fetch_monthly_listeners(self):
        """
        Fetch and update monthly listeners for all artists.
        """
        MonthlyListeners(self.db).update_all_artists()
        print("Monthly listeners updated successfully!")

    def _fetch_spotify_artist_data(self):
        """
        Fetch and store Spotify artist data for all artists.
        """
        artists = Artist.get_all(self.db)
        for artist in artists:
            if artist.spotify_id:
                try:
                    fetch_and_store_artist_data(self.db, artist.spotify_id)
                    print(f"Data for artist {artist.name} saved successfully.")
                except Exception as e:
                    print(f"Error fetching data for artist {artist.name}: {e}")
            else:
                print(f"Artist {artist.name} does not have a Spotify ID. Skipping...")

    def _fetch_songs_by_artist(self):
        """
        Fetch and store songs for a given artist.
        """
        artist_spotify_id = input("Enter the Artist Spotify ID: ").strip()
        try:
            fetch_and_store_songs_by_artist(self.db, artist_spotify_id)
            print("Songs added successfully!")
        except Exception as e:
            print(f"Error fetching songs: {e}")

    def _add_song_to_album(self):
        """
        Add a song to an album.
        """
        song_id = input("Enter Song ID: ")
        album_id = input("Enter Album ID: ")
        AlbumSongs.add_song_to_album(self.db, album_id, song_id)
        print("Song added to album successfully!")

    def _remove_song_from_album(self):
        """
        Remove a song from an album.
        """
        song_id = input("Enter Song ID: ")
        album_id = input("Enter Album ID: ")
        AlbumSongs.remove_song_from_album(self.db, album_id, song_id)
        print("Song removed from album successfully!")

    def _get_artist_input(self):
        """
        Collect artist input from the user.
        """
        return {
            "name": input("Artist Name: "),
            "category": input("Category: "),
            "r_label": input("Record Label: "),
            "spotify_id": input("Spotify ID (optional): ") or None,
            "youtube_id": input("YouTube ID (optional): ") or None,
            "Instagram_id": input("Instagram ID (optional): ") or None,
            "TikTok_id": input("TikTok ID (optional): ") or None,
            "Twitter_id": input("Twitter ID (optional): ") or None,
            "Twitch_id": input("Twitch ID (optional): ") or None,
            "Spotify_url": input("Spotify URL (optional): ") or None,
            "youtube_url": input("YouTube URL (optional): ") or None,
            "instagram_url": input("Instagram URL (optional): ") or None,
            "tiktok_url": input("TikTok URL (optional): ") or None,
            "twitter_url": input("Twitter URL (optional): ") or None,
            "twitch_url": input("Twitch URL (optional): ") or None,
        }

    def _get_song_input(self):
        """
        Collect song input from the user.
        """
        return {
            "name": input("Song Name: "),
            "main_artist_id": input("Main Artist ID: "),
            "producer": input("Producer: "),
            "ytmsc_id": input("YouTube Music ID (optional): ") or None,
            "record_label": input("Record Label: "),
            "type": input("Type (e.g., Single, Album): "),
            "release_date": input("Release Date (DD-MM-YYYY): "),
            "spotify_id": input("Spotify ID (optional): ") or None,
            "youtube_id": input("YouTube ID (optional): ") or None,
            "spotify_url": input("Spotify URL (optional): ") or None,
            "youtube_url": input("YouTube URL (optional): ") or None,
            "youtube_music_url": input("YouTube Music URL (optional): ") or None,
            "album_id": input("Album ID (optional): ") or None,
            "featured_artists": input("Enter featured artist IDs (comma-separated, or leave blank if none): ").strip().split(',') or [],
        }

    def _get_album_input(self):
        """
        Collect album input from the user.
        """
        return {
            "name": input("Album Name: "),
            "artist_id": input("Artist ID: "),
            "number_related_on_release_position": input("Number Related on Release Position (e.g., 1, 2, 3): "),
            "spotify_album_id": input("Spotify Album ID (optional): ") or None,
            "spotify_url": input("Spotify URL (optional): ") or None,
            "youtube_id": input("YouTube ID (optional): ") or None,
            "youtube_url": input("YouTube URL (optional): ") or None,
            "youtube_music_id": input("YouTube Music ID (optional): ") or None,
            "youtube_music_url": input("YouTube Music URL (optional): ") or None,
        }

    def _fetch_all_artist_info(self):
        """
        Fetch all information about an artist from Spotify.
        """
        artist_spotify_id = input("Enter the Artist Spotify ID: ").strip()
        try:
            artist_info = self.spotify_api.fetch_all_artist_info(artist_spotify_id)
            print("Artist Information:")
            print(artist_info)
        except Exception as e:
            print(f"Error fetching artist information: {e}")


if __name__ == "__main__":
    etl_system = ETLSystem()
    etl_system.run()