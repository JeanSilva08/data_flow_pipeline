class Album:

    def __init__(self, **kwargs):
        self.album_id = kwargs.get("album_id")  # Add this line
        self.name = kwargs.get("name")
        self.artist_id = kwargs.get("artist_id")
        self.number_related_on_release_position = kwargs.get("number_related_on_release_position")
        self.spotify_id = kwargs.get("spotify_id")  # Matches DB column
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_id = kwargs.get("youtube_id")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_id = kwargs.get("youtube_music_id")
        self.youtube_music_url = kwargs.get("youtube_music_url")
        self.spotify_album_id = kwargs.get("spotify_album_id")  # Matches DB column

    def save_to_db(self, db):
        """Save the album to the database and update the album_id"""
        try:
            cursor = db.connection.cursor()
            query = """
                INSERT INTO albums (
                    name, artist_id, number_related_on_release_position,
                    spotify_id, spotify_url, youtube_id, youtube_url,
                    youtube_music_id, youtube_music_url, spotify_album_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                self.name, self.artist_id, self.number_related_on_release_position,
                self.spotify_id, self.spotify_url, self.youtube_id,
                self.youtube_url, self.youtube_music_id, self.youtube_music_url,
                self.spotify_album_id
            ))
            self.album_id = cursor.lastrowid  # Set the auto-incremented ID
            db.connection.commit()
            return True
        except Exception as e:
            db.connection.rollback()
            print(f"Error saving album: {e}")
            return False

    @staticmethod
    def update_in_db(db, album_id, **kwargs):
        """Update album information in the database"""
        try:
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(album_id)

            query = f"""
                UPDATE albums
                SET {set_clause}
                WHERE album_id = %s
            """
            db.execute_query(query, values)
            return True
        except Exception as e:
            print(f"Error updating album: {e}")
            return False

    @staticmethod
    def delete_from_db(db, album_id):
        """Delete an album from the database"""
        try:
            query = "DELETE FROM albums WHERE album_id = %s"
            db.execute_query(query, (album_id,))
            return True
        except Exception as e:
            print(f"Error deleting album: {e}")
            return False

    @staticmethod
    def get_by_id(db, album_id):
        """Fetch an album by its ID"""
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM albums WHERE album_id = %s"
            cursor.execute(query, (album_id,))
            result = cursor.fetchone()
            return Album(**result) if result else None
        except Exception as e:
            print(f"Error fetching album by ID: {e}")
            return None

    @staticmethod
    def get_by_spotify_id(db, spotify_id):
        """Fetch an album by its Spotify ID"""
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM albums WHERE spotify_id = %s"
            cursor.execute(query, (spotify_id,))
            result = cursor.fetchone()
            return Album(**result) if result else None
        except Exception as e:
            print(f"Error fetching album by Spotify ID: {e}")
            return None

    @staticmethod
    def get_all(db, limit=None):
        """Get all albums with optional limit"""
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM albums"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            return [Album(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching all albums: {e}")
            return []

    @staticmethod
    def get_by_artist(db, artist_id):
        """Get all albums by a specific artist"""
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM albums WHERE artist_id = %s"
            cursor.execute(query, (artist_id,))
            return [Album(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching albums by artist: {e}")
            return []

    @staticmethod
    def exists(db, album_id=None, spotify_album_id=None):
        """Check if an album exists by ID or Spotify ID"""
        if not any([album_id, spotify_album_id]):
            return False

        try:
            cursor = db.connection.cursor()
            if album_id:
                query = "SELECT 1 FROM albums WHERE album_id = %s"
                cursor.execute(query, (album_id,))
            else:
                query = "SELECT 1 FROM albums WHERE spotify_album_id = %s"
                cursor.execute(query, (spotify_album_id,))
            return bool(cursor.fetchone())
        except Exception as e:
            logger.error(f"Error checking album existence: {e}")
            return False