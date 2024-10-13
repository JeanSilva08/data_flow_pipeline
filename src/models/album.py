class Album:
    def __init__(self, name, artist_id, songs, spotify_album_id=None):
        self.name = name
        self.artist_id = artist_id
        self.songs = songs  # Changed from 'song_ids' to 'songs'
        self.spotify_album_id = spotify_album_id

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
        query = "INSERT INTO albums (name, artist_id, spotify_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (self.name, self.artist_id, self.spotify_album_id))  # Changed to spotify_album_id
        db_connector.connection.commit()
        print(f"Album {self.name} saved to DB.")

    def update_in_db(self, db_connector, album_id):
        cursor = db_connector.connection.cursor()
        query = "UPDATE albums SET name = %s, artist_id = %s, spotify_id = %s WHERE album_id = %s"
        cursor.execute(query,
                       (self.name, self.artist_id, self.spotify_album_id, album_id))  # Changed to spotify_album_id
        db_connector.connection.commit()
        print(f"Album {self.name} updated in DB.")

    def delete_from_db(self, db_connector, album_id):
        cursor = db_connector.connection.cursor()
        query = "DELETE FROM albums WHERE album_id = %s"
        cursor.execute(query, (album_id,))
        db_connector.connection.commit()
        print(f"Album {album_id} deleted from DB.")

    def add_song_to_album(self, db_connector, song_id):
        cursor = db_connector.connection.cursor()
        query = "INSERT INTO album_songs (album_id, song_id) VALUES (%s, %s)"
        cursor.execute(query, (self.album_id, song_id))
        db_connector.connection.commit()
        print(f"Song {song_id} added to album {self.album_id}.")

