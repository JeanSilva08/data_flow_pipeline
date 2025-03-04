from src.apis.spotify_api import fetch_and_store_artist_data, fetch_and_store_songs_by_artist
from src.models.album import Album
from src.models.album_songs import AlbumSongs
from src.models.artist import Artist
from src.models.song import Song
from src.models.playlist import Playlist
from src.scapers.spotify_monthly_listeners import MonthlyListeners
from src.database.db_connector import DBConnector
from dotenv import load_dotenv
import sys
import os

# Add the project root to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()


class ETLSystem:
    def __init__(self):
        self.db = DBConnector(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        self.db.connect()

    def close(self):
        self.db.close()

    def add_artist(self):
        artist_name = input("Artist Name: ")
        category = input("Category: ")
        r_label = input("Record Label: ")
        spotify_id = input("Spotify ID (optional): ")
        youtube_id = input("YouTube ID (optional): ")
        Instagram_id = input("Instagram ID (optional): ")
        TikTok_id = input("TikTok ID (optional): ")
        Twitter_id = input("Twitter ID (optional): ")
        Twitch_id = input("Twitch ID (optional): ")
        Spotify_url = input("Spotify URL (optional): ")
        youtube_url = input("YouTube URL (optional): ")
        instagram_url = input("Instagram URL (optional): ")
        tiktok_url = input("TikTok URL (optional): ")
        twitter_url = input("Twitter URL (optional): ")
        twitch_url = input("Twitch URL (optional): ")

        new_artist = Artist(
            name=artist_name,
            category=category,
            r_label=r_label,
            spotify_id=spotify_id or None,
            youtube_id=youtube_id or None,
            Instagram_id=Instagram_id or None,
            TikTok_id=TikTok_id or None,
            Twitter_id=Twitter_id or None,
            Twitch_id=Twitch_id or None,
            Spotify_url=Spotify_url or None,
            youtube_url=youtube_url or None,
            instagram_url=instagram_url or None,
            tiktok_url=tiktok_url or None,
            twitter_url=twitter_url or None,
            twitch_url=twitch_url or None
        )
        new_artist.save_to_db(self.db)
        print(f"Artist {artist_name} added successfully!")

    def edit_artist(self):
        artist_id = input("Enter Artist ID to update: ")
        artist_name = input("Artist Name: ")
        category = input("Category: ")
        r_label = input("Record Label: ")
        spotify_id = input("Spotify ID (optional): ")
        youtube_id = input("YouTube ID (optional): ")
        Instagram_id = input("Instagram ID (optional): ")
        TikTok_id = input("TikTok ID (optional): ")
        Twitter_id = input("Twitter ID (optional): ")
        Twitch_id = input("Twitch ID (optional): ")
        Spotify_url = input("Spotify URL (optional): ")
        youtube_url = input("YouTube URL (optional): ")
        instagram_url = input("Instagram URL (optional): ")
        tiktok_url = input("TikTok URL (optional): ")
        twitter_url = input("Twitter URL (optional): ")
        twitch_url = input("Twitch URL (optional): ")

        updated_artist = Artist(
            name=artist_name,
            category=category,
            r_label=r_label,
            spotify_id=spotify_id or None,
            youtube_id=youtube_id or None,
            Instagram_id=Instagram_id or None,
            TikTok_id=TikTok_id or None,
            Twitter_id=Twitter_id or None,
            Twitch_id=Twitch_id or None,
            Spotify_url=Spotify_url or None,
            youtube_url=youtube_url or None,
            instagram_url=instagram_url or None,
            tiktok_url=tiktok_url or None,
            twitter_url=twitter_url or None,
            twitch_url=twitch_url or None
        )
        updated_artist.update_in_db(self.db, artist_id)
        print(f"Artist {artist_name} updated successfully!")

    def delete_artist(self):
        artist_id = input("Enter Artist ID to delete: ")
        Artist.delete_from_db(self.db, artist_id)
        print(f"Artist {artist_id} deleted successfully!")

    def add_song(self):
        song_name = input("Song Name: ")
        main_artist_id = input("Main Artist ID: ")
        producer = input("Producer: ")
        ytmsc_id = input("YouTube Music ID (optional): ")
        record_label = input("Record Label: ")
        type = input("Type (e.g., Single, Album): ")
        release_date = input("Release Date (DD-MM-YYYY): ")
        spotify_id = input("Spotify ID (optional): ")
        youtube_id = input("YouTube ID (optional): ")
        spotify_url = input("Spotify URL (optional): ")
        youtube_url = input("YouTube URL (optional): ")
        youtube_music_url = input("YouTube Music URL (optional): ")
        album_id = input("Album ID (optional): ")
        featured_artists_input = input(
            "Enter featured artist IDs (comma-separated, or leave blank if none): "
        )
        featured_artists = [int(x.strip()) for x in
                            featured_artists_input.split(',')] if featured_artists_input else []
        new_song = Song(
            name=song_name,
            main_artist_id=main_artist_id,
            producer=producer,
            ytmsc_id=ytmsc_id,
            record_label=record_label,
            type=type,
            release_date=release_date,
            spotify_id=spotify_id or None,
            youtube_id=youtube_id or None,
            spotify_url=spotify_url or None,
            youtube_url=youtube_url or None,
            youtube_music_url=youtube_music_url or None,
            album_id=album_id or None,
            featured_artists=featured_artists
        )
        new_song.save_to_db(self.db)
        print(f"Song {song_name} added successfully!")

    def edit_song(self):
        song_id = input("Enter Song ID to update: ")
        existing_song = Song.get_by_id(self.db, song_id)
        if not existing_song:
            print(f"Song with ID {song_id} not found.")
            return

        # Prompt for updated values
        song_name = input(f"Song Name [{existing_song.name}]: ") or existing_song.name
        main_artist_id = input(f"Main Artist ID [{existing_song.main_artist_id}]: ") or existing_song.main_artist_id
        spotify_id = input(f"Spotify ID [{existing_song.spotify_id}]: ") or existing_song.spotify_id
        youtube_id = input(f"YouTube ID [{existing_song.youtube_id}]: ") or existing_song.youtube_id
        ytmsc_id = input(f"YouTube Music ID [{existing_song.ytmsc_id}]: ") or existing_song.ytmsc_id
        producer = input(f"Producer [{existing_song.producer}]: ") or existing_song.producer
        record_label = input(f"Record Label [{existing_song.record_label}]: ") or existing_song.record_label
        type = input(f"Type (e.g., Single, Album) [{existing_song.type}]: ") or existing_song.type
        release_date = input(
            f"Release Date (DD-MM-YYYY) [{existing_song.release_date}]: ") or existing_song.release_date
        days_from_release = input(
            f"Days from Release [{existing_song.days_from_release}]: ") or existing_song.days_from_release
        spotify_url = input(f"Spotify URL [{existing_song.spotify_url}]: ") or existing_song.spotify_url
        youtube_url = input(f"YouTube URL [{existing_song.youtube_url}]: ") or existing_song.youtube_url
        youtube_music_url = input(
            f"YouTube Music URL [{existing_song.youtube_music_url}]: ") or existing_song.youtube_music_url
        album_id = input(f"Album ID [{existing_song.album_id}]: ") or existing_song.album_id
        featured_artists_input = input(
            f"Enter featured artist IDs (comma-separated, or leave blank to keep current [{existing_song.featured_artists}]): "
        )
        featured_artists = [int(x.strip()) for x in featured_artists_input.split(
            ',')] if featured_artists_input else existing_song.featured_artists

        # Create updated song object
        updated_song = Song(
            name=song_name,
            main_artist_id=main_artist_id,
            producer=producer,
            ytmsc_id=ytmsc_id,
            record_label=record_label,
            type=type,
            release_date=release_date,
            days_from_release=days_from_release,
            spotify_id=spotify_id,
            youtube_id=youtube_id,
            spotify_url=spotify_url,
            youtube_url=youtube_url,
            youtube_music_url=youtube_music_url,
            album_id=album_id,
            featured_artists=featured_artists
        )

        # Update the song in the database
        updated_song.update_in_db(self.db, song_id)
        print(f"Song {song_name} updated successfully!")

    def delete_song(self):
        song_id = input("Enter Song ID to delete: ")
        Song.delete_from_db(self.db, song_id)
        print(f"Song {song_id} deleted successfully!")

    def add_playlist(self):
        playlist_name = input("Playlist Name (leave blank to use Spotify name): ")
        spotify_playlist_id = input("Spotify Playlist ID: ")
        spotify_url = input("Spotify URL (optional): ")
        try:
            Playlist.add_playlist_from_spotify(self.db, spotify_playlist_id, playlist_name)
            print(f"Playlist '{playlist_name}' successfully added!")
        except Exception as e:
            print(f"Error adding playlist: {e}")

    def edit_playlist(self):
        playlist_id = input("Enter Playlist ID to update: ").strip()
        playlist_name = input("Playlist Name: ").strip()
        spotify_playlist_id = input("Spotify Playlist ID (optional): ").strip()
        spotify_url = input("Spotify URL (optional): ").strip()
        song_ids_input = input("Enter updated song IDs for the playlist (comma-separated): ").strip()
        if song_ids_input:
            song_ids = [int(x.strip()) for x in song_ids_input.split(',')]
        else:
            song_ids = []
        updated_playlist = Playlist(
            name=playlist_name,
            spotify_playlist_id=spotify_playlist_id or None,
            spotify_url=spotify_url or None
        )
        updated_playlist.update_in_db(self.db, playlist_id, song_ids)
        print(f"Playlist {playlist_name} updated successfully!")

    def delete_playlist(self):
        playlist_id = input("Enter Playlist ID to delete: ").strip()
        Playlist.delete_from_db(self.db, playlist_id)
        print(f"Playlist {playlist_id} deleted successfully!")

    def add_album(self):
        album_name = input("Album Name: ")
        artist_id = input("Artist ID: ")
        number_related_on_release_position = input("Number Related on Release Position (e.g., 1, 2, 3): ")
        spotify_album_id = input("Spotify Album ID (optional): ")
        spotify_url = input("Spotify URL (optional): ")
        youtube_id = input("YouTube ID (optional): ")
        youtube_url = input("YouTube URL (optional): ")
        youtube_music_id = input("YouTube Music ID (optional): ")
        youtube_music_url = input("YouTube Music URL (optional): ")
        album = Album(
            name=album_name,
            artist_id=artist_id,
            number_related_on_release_position=number_related_on_release_position,
            spotify_album_id=spotify_album_id or None,
            spotify_url=spotify_url or None,
            youtube_id=youtube_id or None,
            youtube_url=youtube_url or None,
            youtube_music_id=youtube_music_id or None,
            youtube_music_url=youtube_music_url or None
        )
        album.save_to_db(self.db)
        print(f"Album {album_name} added successfully!")

    def edit_album(self):
        album_id = input("Enter Album ID to update: ")
        album_name = input("Album Name: ")
        artist_id = input("Artist ID: ")
        number_related_on_release_position = input("Number Related on Release Position (e.g., 1, 2, 3): ")
        spotify_album_id = input("Spotify Album ID (optional): ")
        spotify_url = input("Spotify URL (optional): ")
        youtube_id = input("YouTube ID (optional): ")
        youtube_url = input("YouTube URL (optional): ")
        youtube_music_id = input("YouTube Music ID (optional): ")
        youtube_music_url = input("YouTube Music URL (optional): ")
        album = Album(
            name=album_name,
            artist_id=artist_id,
            number_related_on_release_position=number_related_on_release_position,
            spotify_album_id=spotify_album_id or None,
            spotify_url=spotify_url or None,
            youtube_id=youtube_id or None,
            youtube_url=youtube_url or None,
            youtube_music_id=youtube_music_id or None,
            youtube_music_url=youtube_music_url or None
        )
        album.update_in_db(self.db, album_id)
        print(f"Album {album_name} updated successfully!")

    def delete_album(self):
        album_id = input("Enter Album ID to delete: ")
        album = Album(name="", artist_id=0)
        album.album_id = album_id
        album.delete_from_db(self.db)
        print(f"Album {album_id} deleted successfully!")

    def fetch_monthly_listeners(self):
        print("Fetching monthly listeners for all artists...")
        listeners_fetcher = MonthlyListeners(self.db)
        listeners_fetcher.update_all_artists()
        print("Monthly listeners updated successfully!")

    def fetch_spotify_artist_data(self):
        print("Fetching and storing Spotify artist data...")
        artists = Artist.get_all(self.db)
        for artist in artists:
            if artist.spotify_id:
                try:
                    fetch_and_store_artist_data(self.db, artist.spotify_id)
                    print(f"Data for artist {artist.name} (Spotify ID: {artist.spotify_id}) saved successfully.")
                except Exception as e:
                    print(
                        f"Error fetching and storing data for artist {artist.name} (Spotify ID: {artist.spotify_id}): {e}")
            else:
                print(f"Artist {artist.name} does not have a Spotify ID. Skipping...")

    def fetch_songs_by_artist(self):
        artist_spotify_id = input("Enter the Artist Spotify ID: ").strip()
        try:
            fetch_and_store_songs_by_artist(self.db, artist_spotify_id)
            print(f"Songs for artist with Spotify ID {artist_spotify_id} successfully added!")
        except Exception as e:
            print(f"Error fetching and adding songs: {e}")

    def add_song_to_album(self):
        song_id = input("Enter Song ID: ")
        album_id = input("Enter Album ID: ")

        song = Song.get_by_id(self.db, song_id)  # Fetch song instance
        if song:
            album_songs = AlbumSongs(self.db)
            album_songs.add_song_to_album(album_id, song_id)
            print(f"Song {song_id} added to album {album_id} successfully!")
        else:
            print("Song not found.")

    def remove_song_from_album(self):
        song_id = input("Enter Song ID: ")
        song = Song.get_by_id(self.db, song_id)
        if song:
            album_id = input("Enter Album ID: ")  # Prompt for the album ID
            album_songs = AlbumSongs(self.db)
            album_songs.remove_song_from_album(album_id, song_id)
            print(f"Song {song_id} removed from album {album_id} successfully!")
        else:
            print("Song not found.")

    def display_menu(self):
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

    def run(self):
        while True:
            self.display_menu()
            choice = input("Digite a opção escolhida: ").strip()

            if choice == '1':
                self.add_artist()
            elif choice == '2':
                self.edit_artist()
            elif choice == '3':
                self.delete_artist()
            elif choice == '4':
                self.add_song()
            elif choice == '5':
                self.edit_song()
            elif choice == '6':
                self.delete_song()
            elif choice == '7':
                self.add_playlist()
            elif choice == '8':
                self.edit_playlist()
            elif choice == '9':
                self.delete_playlist()
            elif choice == '10':
                self.add_album()
            elif choice == '11':
                self.edit_album()
            elif choice == '12':
                self.delete_album()
            elif choice == '13':
                self.fetch_monthly_listeners()
            elif choice == '14':
                self.fetch_spotify_artist_data()
            elif choice == '15':
                self.fetch_songs_by_artist()
            elif choice == '16':
                print("Exiting...")
                break
            elif choice == '17':
                self.add_song_to_album()
            elif choice == '18':
                self.remove_song_from_album()
            else:
                print("Invalid choice. Please try again.")

        self.close()


if __name__ == "__main__":
    etl_system = ETLSystem()
    etl_system.run()