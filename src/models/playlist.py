class Playlist:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.spotify_playlist_id = kwargs.get("spotify_playlist_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.song_ids = kwargs.get("song_ids", [])

    def save_to_db(self, db):
        cursor = db.connection.cursor()
        query = "INSERT INTO playlists (name, spotify_playlist_id, spotify_url) VALUES (%s, %s, %s)"
        cursor.execute(query, (self.name, self.spotify_playlist_id, self.spotify_url))
        playlist_id = cursor.lastrowid
        db.connection.commit()

        # Add songs to the playlist
        for song_id in self.song_ids:
            query = "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)"
            cursor.execute(query, (playlist_id, song_id))
        db.connection.commit()

    def update_in_db(self, db, playlist_id):
        cursor = db.connection.cursor()
        query = "UPDATE playlists SET name = %s, spotify_playlist_id = %s, spotify_url = %s WHERE playlist_id = %s"
        cursor.execute(query, (self.name, self.spotify_playlist_id, self.spotify_url, playlist_id))
        db.connection.commit()

        # Update songs in the playlist
        query = "DELETE FROM playlist_songs WHERE playlist_id = %s"
        cursor.execute(query, (playlist_id,))
        for song_id in self.song_ids:
            query = "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)"
            cursor.execute(query, (playlist_id, song_id))
        db.connection.commit()

    @staticmethod
    def delete_from_db(db, playlist_id):
        cursor = db.connection.cursor()
        query = "DELETE FROM playlists WHERE playlist_id = %s"
        cursor.execute(query, (playlist_id,))
        db.connection.commit()

    @staticmethod
    def get_by_id(db, playlist_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM playlists WHERE playlist_id = %s"
        cursor.execute(query, (playlist_id,))
        result = cursor.fetchone()
        if result:
            return Playlist(**result)
        return None

    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM playlists"
        cursor.execute(query)
        return [Playlist(**row) for row in cursor.fetchall()]