class Album:
    def __init__(self, name, artist_id, songs, spotify_album_id=None):
        self.name = name
        self.artist_id = artist_id
        self.songs = songs
        self.spotify_album_id = spotify_album_id
        self.album_id = None  # Default to None until set later

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
        query = "INSERT INTO albums (name, artist_id, spotify_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (self.name, self.artist_id, self.spotify_album_id))
        db_connector.connection.commit()
        print(f"Album {self.name} saved to DB.")
        self.album_id = cursor.lastrowid  # Set album_id from the database

    def update_in_db(self, db_connector, album_id):
        cursor = db_connector.connection.cursor()
        query = "UPDATE albums SET name = %s, artist_id = %s, spotify_id = %s WHERE album_id = %s"
        cursor.execute(query, (self.name, self.artist_id, self.spotify_album_id, album_id))
        db_connector.connection.commit()
        print(f"Album {self.name} updated in DB.")

    def delete_from_db(self, db_connector):
        if not self.album_id:
            raise ValueError("Album ID is not set. Cannot delete album.")

        cursor = db_connector.connection.cursor()
        query = "DELETE FROM albums WHERE album_id = %s"
        cursor.execute(query, (self.album_id,))
        db_connector.connection.commit()
        print(f"Album {self.album_id} deleted from DB.")
