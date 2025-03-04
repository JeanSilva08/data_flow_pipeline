class ArtistSongs:
    def __init__(self, db):
        self.db = db

    def add_song_for_artist(self, artist_id, song_id):
        """
        Adds a relationship between an artist and a song.
        """
        cursor = self.db.connection.cursor()
        query = "INSERT INTO song_artists (song_id, artist_id) VALUES (%s, %s)"
        cursor.execute(query, (song_id, artist_id))
        self.db.connection.commit()
        print(f"Added artist {artist_id} to song {song_id}")

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