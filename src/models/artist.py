class Artist:
    def __init__(self, name, spotify_id=None, youtube_id=None):
        self.name = name
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
        query = "INSERT INTO artists (name, spotify_id, youtube_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (self.name, self.spotify_id, self.youtube_id))
        db_connector.connection.commit()
        print(f"Artist {self.name} inserted successfully")

    def update_in_db(self, db_connector, artist_id):
        cursor = db_connector.connection.cursor()
        query = "UPDATE artists SET name = %s, spotify_id = %s, youtube_id = %s WHERE artist_id = %s"
        cursor.execute(query, (self.name, self.spotify_id, self.youtube_id, artist_id))
        db_connector.connection.commit()
        print(f"Artist with ID {artist_id} updated successfully")

    @staticmethod
    def delete_from_db(db_connector, artist_id):
        cursor = db_connector.connection.cursor()
        query = "DELETE FROM artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id,))
        db_connector.connection.commit()
        print(f"Artist with ID {artist_id} deleted successfully")
