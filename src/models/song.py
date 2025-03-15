class Song:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.main_artist_id = kwargs.get("main_artist_id")
        self.producer = kwargs.get("producer")
        self.ytmsc_id = kwargs.get("ytmsc_id")
        self.record_label = kwargs.get("record_label")
        self.type = kwargs.get("type")
        self.release_date = kwargs.get("release_date")
        self.days_from_release = kwargs.get("days_from_release")
        self.spotify_id = kwargs.get("spotify_id")
        self.youtube_id = kwargs.get("youtube_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_url = kwargs.get("youtube_music_url")
        self.album_id = kwargs.get("album_id")
        self.featured_artists = kwargs.get("featured_artists", [])

    @classmethod
    def save_to_db(cls, db, **data):
        """
        Save the song to the database.
        """
        try:
            # Debug: Print the data being saved
            print(f"Saving song to database: {data}")

            # Insert the song into the database
            query = """
                INSERT INTO songs (name, main_artist_id, spotify_id, spotify_url, album_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                data.get("name"),
                data.get("main_artist_id"),
                data.get("spotify_id"),
                data.get("spotify_url"),
                data.get("album_id"),
            )
            db.execute_query(query, values)
            print("Song saved successfully!")
        except Exception as e:
            print(f"Error saving song to database: {e}")

    @staticmethod
    def update_in_db(db, song_id, **kwargs):
        """
        Update the song data in the database.
        """
        cursor = db.connection.cursor()
        set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE songs SET {set_clause} WHERE song_id = %s"
        cursor.execute(query, (*kwargs.values(), song_id))
        db.connection.commit()

    @staticmethod
    def delete_from_db(db, song_id):
        cursor = db.connection.cursor()
        query = "DELETE FROM songs WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        db.connection.commit()

    @staticmethod
    def get_by_id(db, song_id):
        """
        Fetch the current song data from the database.
        """
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM songs WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        return cursor.fetchone()

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
        cursor = db.connection.cursor()
        query = "SELECT * FROM songs"
        cursor.execute(query)
        return [Song(**row) for row in cursor.fetchall()]