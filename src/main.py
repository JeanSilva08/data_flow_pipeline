from src.apis.spotify_api import fetch_and_store_artist_data, fetch_and_store_songs_by_artist
from src.models.album import Album
from src.models.artist import Artist
from src.models.song import Song
from src.models.playlist import Playlist
from dotenv import load_dotenv
from src.scapers.spotify_monthly_listeners import MonthlyListeners
import sys
import os
from src.database.db_connector import DBConnector

# Add the project root to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

def main():
    # Initialize the database connection
    db = DBConnector(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    db.connect()

    while True:
        # Display the menu
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
        print("10: Adicionar Álbum")  # Add Album
        print("11: Editar Álbum")  # Edit Album
        print("12: Deletar Álbum")  # Delete Album
        print("13: Ouvintes Mensais")
        print("14: Spotify Info")
        print("15: Salvar todas as músicas")
        print("16: Sair")

        # Get user input
        choice = input("Enter your choice: ").strip()

        if choice == '1':  # Add Artist
            artist_name = input("Artist Name: ")
            spotify_id = input("Spotify ID (optional): ")
            youtube_id = input("YouTube ID (optional): ")

            new_artist = Artist(
                name=artist_name,
                spotify_id=spotify_id or None,
                youtube_id=youtube_id or None
            )
            new_artist.save_to_db(db)

        elif choice == '2':  # Edit Artist
            artist_id = input("Enter Artist ID to update: ")
            artist_name = input("Artist Name: ")
            spotify_id = input("Spotify ID (optional): ")
            youtube_id = input("YouTube ID (optional): ")

            updated_artist = Artist(
                name=artist_name,
                spotify_id=spotify_id or None,
                youtube_id=youtube_id or None
            )
            updated_artist.update_in_db(db, artist_id)

        elif choice == '3':  # Delete Artist
            artist_id = input("Enter Artist ID to delete: ")
            Artist.delete_from_db(db, artist_id)

        elif choice == '4':  # Add Song
            song_name = input("Song Name: ")
            main_artist_id = input("Main Artist ID: ")
            spotify_song_id = input("Spotify ID (optional): ")
            youtube_song_id = input("YouTube ID (optional): ")

            featured_artists_input = input(
                "Enter featured artist IDs (comma-separated, or leave blank if none): "
            )
            featured_artists = [int(x.strip()) for x in featured_artists_input.split(',')] if featured_artists_input else []

            new_song = Song(
                name=song_name,
                main_artist_id=main_artist_id,
                spotify_id=spotify_song_id or None,
                youtube_id=youtube_song_id or None,
                featured_artists=featured_artists
            )
            new_song.save_to_db(db)

        elif choice == '5':  # Edit Song
            song_id = input("Enter Song ID to update: ")
            song_name = input("Song Name: ")
            main_artist_id = input("Main Artist ID: ")
            spotify_song_id = input("Spotify ID (optional): ")
            youtube_song_id = input("YouTube ID (optional): ")

            updated_song = Song(
                name=song_name,
                main_artist_id=main_artist_id,
                spotify_id=spotify_song_id or None,
                youtube_id=youtube_song_id or None
            )
            updated_song.update_in_db(db, song_id)

        elif choice == '6':  # Delete Song
            song_id = input("Enter Song ID to delete: ")
            Song.delete_from_db(db, song_id)

        elif choice == '7':  # Add Playlist
            playlist_name = input("Playlist Name (leave blank to use Spotify name): ")
            spotify_playlist_id = input("Spotify Playlist ID: ")
            try:
                Playlist.add_playlist_from_spotify(db, spotify_playlist_id, playlist_name)
                print(f"Playlist '{playlist_name}' successfully added!")
            except Exception as e:
                print(f"Error adding playlist: {e}")

        elif choice == '8':  # Edit Playlist
            playlist_id = input("Enter Playlist ID to update: ").strip()
            playlist_name = input("Playlist Name: ").strip()
            spotify_playlist_id = input("Spotify Playlist ID (optional): ").strip()
            song_ids_input = input("Enter updated song IDs for the playlist (comma-separated): ").strip()
            # Verificar se a entrada está vazia
            if song_ids_input:
                song_ids = [int(x.strip()) for x in song_ids_input.split(',')]
            else:
                song_ids = []  # Se vazio, atribuir uma lista vazia
            updated_playlist = Playlist(name=playlist_name, spotify_playlist_id=spotify_playlist_id or None)
            updated_playlist.update_in_db(db, playlist_id, song_ids)

        elif choice == '9':  # Delete Playlist
            playlist_id = input("Enter Playlist ID to delete: ").strip()
            Playlist.delete_from_db(db, playlist_id)  # Certifique-se de passar `db`

        elif choice == '10':  # Add Album
            album_name = input("Album Name: ")
            artist_id = input("Artist ID: ")
            spotify_album_id = input("Spotify Album ID (optional): ")
            songs = []  # Default to an empty list if there are no songs initially
            album = Album(name=album_name, artist_id=artist_id, songs=songs, spotify_album_id=spotify_album_id)
            album.save_to_db(db)


        elif choice == '11':  # Edit Album
            album_id = input("Enter Album ID to update: ")
            album_name = input("Album Name: ")
            artist_id = input("Artist ID: ")
            spotify_album_id = input("Spotify Album ID (optional): ")
            # Use an empty list for songs, or fetch existing songs as needed
            album = Album(name=album_name, artist_id=artist_id, songs=[], spotify_album_id=spotify_album_id)
            album.update_in_db(db, album_id)


        elif choice == '12':  # Delete Album
            album_id = input("Enter Album ID to delete: ")
            album = Album(name="", artist_id=0, songs=[])  # You can create a temporary album instance with the given ID
            album.album_id = album_id  # Set the album_id from user input
            album.delete_from_db(db)

        elif choice == '13':  # Fetch Monthly Listeners
            print("Fetching monthly listeners for all artists...")
            listeners_fetcher = MonthlyListeners(db)  # Pass the db instance
            listeners_fetcher.update_all_artists()

        elif choice == '14':  # Fetch and Store Spotify Artist Data
            print("Fetching and storing Spotify artist data...")
            # Fetch the Spotify ID from the database for all artists
            artists = Artist.get_all(db)  # This will now work
            for artist in artists:
                if artist.spotify_id:  # Check if the artist has a Spotify ID
                    try:
                        # Fetch and store data for this artist using the Spotify ID
                        fetch_and_store_artist_data(db, artist.spotify_id)
                        print(f"Data for artist {artist.name} (Spotify ID: {artist.spotify_id}) saved successfully.")
                    except Exception as e:
                        print(
                            f"Error fetching and storing data for artist {artist.name} (Spotify ID: {artist.spotify_id}): {e}")
                else:
                    print(f"Artist {artist.name} does not have a Spotify ID. Skipping...")

        elif choice == '15':  # Fetch and Add Songs by Artist Spotify ID
            artist_spotify_id = input("Enter the Artist Spotify ID: ").strip()
            try:
                fetch_and_store_songs_by_artist(db, artist_spotify_id)
                print(f"Songs for artist with Spotify ID {artist_spotify_id} successfully added!")
            except Exception as e:
                print(f"Error fetching and adding songs: {e}")

        elif choice == '16':  # Exit
            print("Exiting...")
            break


    # Close the database connection
    db.close()

if __name__ == "__main__":
    main()
