import json

class Song:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.main_artist_id = kwargs.get("main_artist_id")
        self.producer = kwargs.get("producer")
        self.ytmsc_id = kwargs.get("ytmsc_id")
        self.record_label = kwargs.get("record_label")
        self.type = kwargs.get("type")
        self.release_date = kwargs.get("release_date")
        self.days_from_release = kwargs.get("days_from_release")
        self.spotify_id = kwargs.get("spotify_id")
        self.youtube_id = kwargs.get("youtube_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_url = kwargs.get("youtube_music_url")
        self.album_id = kwargs.get("album_id")
        self.featured_artists = kwargs.get("featured_artists", [])

    def save_to_db(self, db):
        cursor = db.connection.cursor()
        query = """
            INSERT INTO songs (
                name, main_artist_id, producer, ytmsc_id, record_label, type,
                release_date, days_from_release, spotify_id, youtube_id,
                spotify_url, youtube_url, youtube_music_url, album_id, featured_artists
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            self.name, self.main_artist_id, self.producer, self.ytmsc_id,
            self.record_label, self.type, self.release_date, self.days_from_release,
            self.spotify_id, self.youtube_id, self.spotify_url,
            self.youtube_url, self.youtube_music_url, self.album_id,
            json.dumps(self.featured_artists)  # Convert list to JSON
        ))
        db.connection.commit()

    def update_in_db(self, db, song_id):
        cursor = db.connection.cursor()
        query = """
            UPDATE songs SET
                name = %s, main_artist_id = %s, producer = %s, ytmsc_id = %s,
                record_label = %s, type = %s, release_date = %s, days_from_release = %s,
                spotify_id = %s, youtube_id = %s, spotify_url = %s,
                youtube_url = %s, youtube_music_url = %s, album_id = %s,
                featured_artists = %s
            WHERE song_id = %s
        """
        cursor.execute(query, (
            self.name, self.main_artist_id, self.producer, self.ytmsc_id,
            self.record_label, self.type, self.release_date, self.days_from_release,
            self.spotify_id, self.youtube_id, self.spotify_url,
            self.youtube_url, self.youtube_music_url, self.album_id,
            json.dumps(self.featured_artists),  # Convert list to JSON
            song_id
        ))
        db.connection.commit()

    @staticmethod
    def delete_from_db(db, song_id):
        cursor = db.connection.cursor()
        query = "DELETE FROM songs WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        db.connection.commit()

    @staticmethod
    def get_by_id(db, song_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM songs WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        result = cursor.fetchone()
        if result:
            return Song(**result)
        return None

    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM songs"
        cursor.execute(query)
        return [Song(**row) for row in cursor.fetchall()]