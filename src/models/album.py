class Album:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.artist_id = kwargs.get("artist_id")
        self.number_related_on_release_position = kwargs.get("number_related_on_release_position")
        self.spotify_album_id = kwargs.get("spotify_album_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_id = kwargs.get("youtube_id")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_id = kwargs.get("youtube_music_id")
        self.youtube_music_url = kwargs.get("youtube_music_url")

    @staticmethod
    def get_by_id(db, album_id):
        """
        Fetch an album by its ID.
        """
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM albums WHERE album_id = %s"
        cursor.execute(query, (album_id,))
        result = cursor.fetchone()
        if result:
            return Album(**result)
        return None

    @staticmethod
    def get_by_spotify_id(db, spotify_album_id):
        """
        Fetch an album by its Spotify ID.
        """
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM albums WHERE spotify_album_id = %s"
        cursor.execute(query, (spotify_album_id,))
        result = cursor.fetchone()
        if result:
            return Album(**result)
        return None

    def save_to_db(self, db):
        """
        Save the album to the database.
        """
        cursor = db.connection.cursor()
        query = """
            INSERT INTO albums (
                name, artist_id, number_related_on_release_position,
                spotify_album_id, spotify_url, youtube_id, youtube_url,
                youtube_music_id, youtube_music_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            self.name, self.artist_id, self.number_related_on_release_position,
            self.spotify_album_id, self.spotify_url, self.youtube_id,
            self.youtube_url, self.youtube_music_id, self.youtube_music_url
        ))
        db.connection.commit()
        print("Album saved successfully!")

    @staticmethod
    def update_in_db(db, album_id, **kwargs):
        """
        Update an album's information in the database.
        """
        try:
            # Build the SET clause for the SQL query
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(album_id)  # Add album_id for the WHERE clause

            query = f"""
                UPDATE albums
                SET {set_clause}
                WHERE album_id = %s
            """
            db.execute_query(query, values)
            print("Album updated successfully!")
        except Exception as e:
            print(f"Error updating album: {e}")

    @staticmethod
    def delete_from_db(db, album_id):
        """
        Delete an album from the database.
        """
        try:
            query = "DELETE FROM albums WHERE album_id = %s"
            db.execute_query(query, (album_id,))
            print("Album deleted successfully!")
        except Exception as e:
            print(f"Error deleting album: {e}")