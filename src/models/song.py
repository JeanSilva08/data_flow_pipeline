import json
from datetime import datetime


class Song:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.main_artist_id = kwargs.get("main_artist_id")
        self.producer = kwargs.get("producer")
        self.record_label = kwargs.get("record_label")
        self.type = kwargs.get("type")
        self.release_date = kwargs.get("release_date")
        self.days_from_release = kwargs.get("days_from_release")
        self.spotify_id = kwargs.get("spotify_id")
        self.youtube_id = kwargs.get("youtube_id")
        self.ytmsc_id = kwargs.get("ytmsc_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_url = kwargs.get("youtube_music_url")
        self.album_id = kwargs.get("album_id")
        self.featured_artists = kwargs.get("featured_artists", [])

        # Validate required fields
        if not self.name or not self.main_artist_id or not self.spotify_id:
            raise ValueError("Name, main_artist_id, and spotify_id are required fields.")

    @classmethod
    def save_to_db(cls, db, **data):
        try:
            # Convert release_date to the correct format (YYYY-MM-DD) or set to None if not provided
            release_date = data.get("release_date")
            if release_date:
                try:
                    release_date = datetime.strptime(release_date, "%d-%m-%Y").strftime("%Y-%m-%d")
                except ValueError:
                    print("Invalid release_date format. Setting to None.")
                    release_date = None
            else:
                release_date = None

            query = """
                INSERT INTO songs (
                    name, main_artist_id, producer, record_label, type, release_date, 
                    days_from_release, spotify_id, youtube_id, ytmsc_id, spotify_url, 
                    youtube_url, youtube_music_url, album_id, featured_artists
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get("name"),
                data.get("main_artist_id"),
                data.get("producer"),
                data.get("record_label"),
                data.get("type"),
                release_date,  # Use the validated and formatted release_date
                data.get("days_from_release"),
                data.get("spotify_id"),
                data.get("youtube_id"),
                data.get("ytmsc_id"),
                data.get("spotify_url"),
                data.get("youtube_url"),
                data.get("youtube_music_url"),
                data.get("album_id"),
                json.dumps(data.get("featured_artists", [])),  # Convert list to JSON string
            )
            db.execute_query(query, values)
            print("Song saved successfully!")
        except Exception as e:
            print(f"Error saving song to database: {e}")

    @staticmethod
    def update_in_db(db, song_id, **kwargs):
        """
        Update a song's information in the database.
        """
        try:
            # Build the SET clause for the SQL query
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(song_id)  # Add song_id for the WHERE clause

            query = f"""
                    UPDATE songs
                    SET {set_clause}
                    WHERE song_id = %s
                """
            db.execute_query(query, values)
            print("Song updated successfully!")
        except Exception as e:
            print(f"Error updating song: {e}")

    @staticmethod
    def delete_from_db(db, song_id):
        try:
            query = "DELETE FROM songs WHERE song_id = %s"
            db.execute_query(query, (song_id,))
            print("Song deleted successfully!")
        except Exception as e:
            print(f"Error deleting song: {e}")

    @staticmethod
    def get_by_id(db, song_id):
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM songs WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        result = cursor.fetchone()
        if result:
            return Song(**result)
        return None

    @staticmethod
    def get_by_spotify_id(db, spotify_id):
        """
        Fetch a song by its Spotify ID.
        """
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM songs WHERE spotify_id = %s"
        cursor.execute(query, (spotify_id,))
        result = cursor.fetchone()
        if result:
            return Song(**result)
        return None

    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM songs"
        cursor.execute(query)
        return [Song(**row) for row in cursor.fetchall()]