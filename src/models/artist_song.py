class ArtistSongs:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def add_song_for_artist(db, artist_id, song_id):
        query = "INSERT INTO artist_songs (artist_id, song_id) VALUES (%s, %s)"
        db.execute_query(query, (artist_id, song_id))

    def get_songs_by_artist(self, artist_id):
        """
        Retrieves all songs associated with a specific artist.
        """
        cursor = self.db.connection.cursor()
        query = """
            SELECT songs.* FROM songs
            JOIN song_artists ON songs.song_id = song_artists.song_id
            WHERE song_artists.artist_id = %s
        """
        cursor.execute(query, (artist_id,))
        return cursor.fetchall()

    def get_artists_for_song(self, song_id):
        """
        Retrieves all artists associated with a specific song.
        """
        cursor = self.db.connection.cursor()
        query = """
            SELECT artists.* FROM artists
            JOIN song_artists ON artists.artist_id = song_artists.artist_id
            WHERE song_artists.song_id = %s
        """
        cursor.execute(query, (song_id,))
        return cursor.fetchall()

    def remove_song_from_artist(self, artist_id, song_id):
        """
        Removes a relationship between an artist and a song.
        """
        cursor = self.db.connection.cursor()
        query = "DELETE FROM song_artists WHERE artist_id = %s AND song_id = %s"
        cursor.execute(query, (artist_id, song_id))
        self.db.connection.commit()
        print(f"Removed artist {artist_id} from song {song_id}")

    @staticmethod
    def get_all_artist_song_relationships(db):
        """
        Retrieves all artist-song relationships.
        """
        cursor = db.connection.cursor()
        query = "SELECT * FROM song_artists"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def check_song_for_artist(db, artist_id, song_id):
        query = "SELECT * FROM artist_songs WHERE artist_id = %s AND song_id = %s"
        result = db.execute_query(query, (artist_id, song_id))
        return bool(result)