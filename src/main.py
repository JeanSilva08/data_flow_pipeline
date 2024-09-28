from src.database.db_connector import DBConnector
from src.models.artist import Artist
from src.models.song import Song
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    db = DBConnector(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    db.connect()

    while True:
        print("\nChoose an option:")
        print("1: Add an Artist")
        print("2: Edit an Artist")
        print("3: Delete an Artist")
        print("4: Add a Song")
        print("5: Edit a Song")
        print("6: Delete a Song")
        print("7: Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            print("\nEnter artist details:")
            artist_name = input("Artist Name: ")
            spotify_id = input("Spotify ID (optional): ")
            youtube_id = input("YouTube ID (optional): ")

            new_artist = Artist(
                name=artist_name,
                spotify_id=spotify_id or None,
                youtube_id=youtube_id or None
            )
            new_artist.save_to_db(db)

        elif choice == '2':
            artist_id = input("Enter Artist ID to update: ")
            print("\nEnter new artist details:")
            artist_name = input("Artist Name: ")
            spotify_id = input("Spotify ID (optional): ")
            youtube_id = input("YouTube ID (optional): ")

            updated_artist = Artist(
                name=artist_name,
                spotify_id=spotify_id or None,
                youtube_id=youtube_id or None
            )
            updated_artist.update_in_db(db, artist_id)

        elif choice == '3':
            artist_id = input("Enter Artist ID to delete: ")
            Artist.delete_from_db(db, artist_id)

        elif choice == '4':
            print("\nEnter song details:")
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

        elif choice == '5':
            song_id = input("Enter Song ID to update: ")
            print("\nEnter new song details:")
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

        elif choice == '6':
            song_id = input("Enter Song ID to delete: ")
            Song.delete_from_db(db, song_id)

        elif choice == '7':
            print("Exiting...")
            break

        else:
            print("Invalid choice, please try again.")

    db.close()

if __name__ == "__main__":
    main()
