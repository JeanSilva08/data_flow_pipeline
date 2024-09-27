class Song:
    def __init__(self, name, main_artist_id, spotify_id=None, youtube_id=None, featured_artists=None):
        self.name = name
        self.main_artist_id = main_artist_id
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.featured_artists = featured_artists or []

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()

        song_query = """
            INSERT INTO songs (name, main_artist_id, spotify_id, youtube_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(song_query, (self.name, self.main_artist_id, self.spotify_id, self.youtube_id))
        song_id = cursor.lastrowid

        if self.featured_artists:
            song_artist_query = "INSERT INTO song_artists (song_id, artist_id) VALUES (%s, %s)"
            for artist_id in self.featured_artists:
                cursor.execute(song_artist_query, (song_id, artist_id))

        db_connector.connection.commit()
        print(f"Song '{self.name}' with ID {song_id} inserted successfully")

    def update_in_db(self, db_connector, song_id):
        cursor = db_connector.connection.cursor()

        song_query = "UPDATE songs SET name = %s, main_artist_id = %s, spotify_id = %s, youtube_id = %s WHERE id = %s"
        cursor.execute(song_query, (self.name, self.main_artist_id, self.spotify_id, self.youtube_id, song_id))

        # Optionally update featured artists if necessary
        db_connector.connection.commit()
        print(f"Song with ID {song_id} updated successfully")

    @staticmethod
    def delete_from_db(db_connector, song_id):
        cursor = db_connector.connection.cursor()
        song_query = "DELETE FROM songs WHERE id = %s"
        cursor.execute(song_query, (song_id,))
        db_connector.connection.commit()
        print(f"Song with ID {song_id} deleted successfully")
