class ArtistSongs:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def add_song_for_artist(self, artist_id, song_id):
        cursor = self.db_connector.connection.cursor()
        query = "INSERT INTO song_artists (song_id, artist_id) VALUES (%s, %s)"
        cursor.execute(query, (song_id, artist_id))
        self.db_connector.connection.commit()
        print(f"Added artist {artist_id} to song {song_id}")

    def get_songs_by_artist(self, artist_id):
        cursor = self.db_connector.connection.cursor()
        query = """
            SELECT songs.* FROM songs
            JOIN song_artists ON songs.song_id = song_artists.song_id
            WHERE song_artists.artist_id = %s
        """
        cursor.execute(query, (artist_id,))
        return cursor.fetchall()

    def get_artists_for_song(self, song_id):
        cursor = self.db_connector.connection.cursor()
        query = """
            SELECT artists.* FROM artists
            JOIN song_artists ON artists.artist_id = song_artists.artist_id
            WHERE song_artists.song_id = %s
        """
        cursor.execute(query, (song_id,))
        return cursor.fetchall()
