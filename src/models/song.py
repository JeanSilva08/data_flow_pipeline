from datetime import datetime, date

class Song:
    def __init__(
        self,
        name,
        main_artist_id,
        producer=None,
        beatmaker=None,
        record_label=None,
        type=None,
        release_date=None,
        days_from_release=None,
        spotify_id=None,
        youtube_id=None,
        youtube_music_id=None,
        spotify_url=None,
        youtube_url=None,
        youtube_music_url=None,
        album_id=None,
        featured_artists=None
    ):
        self.name = name
        self.main_artist_id = main_artist_id
        self.producer = producer
        self.beatmaker = beatmaker
        self.record_label = record_label
        self.type = type
        self.release_date = release_date
        self.days_from_release = days_from_release
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.youtube_music_id = youtube_music_id
        self.spotify_url = spotify_url
        self.youtube_url = youtube_url
        self.youtube_music_url = youtube_music_url
        self.album_id = album_id
        self.featured_artists = featured_artists or []

    def calculate_days_from_release(self):
        if self.release_date:
            # Parse the release_date string in dd-mm-yyyy format into a date object
            release_date = datetime.strptime(self.release_date, "%d-%m-%Y").date()
            # Calculate the difference between today and the release date
            today = date.today()
            self.days_from_release = (today - release_date).days
        else:
            self.days_from_release = None

    def format_release_date_for_db(self):
        if self.release_date:
            # Parse the release_date string in dd-mm-yyyy format into a date object
            release_date = datetime.strptime(self.release_date, "%d-%m-%Y").date()
            # Format it back to yyyy-mm-dd for the database
            return release_date.strftime("%Y-%m-%d")
        return None

    def save_to_db(self, db_connector):
        # Calculate days_from_release before saving
        self.calculate_days_from_release()

        # Format release_date for the database
        formatted_release_date = self.format_release_date_for_db()

        cursor = db_connector.connection.cursor()

        song_query = """
            INSERT INTO songs (
                name, main_artist_id, producer, beatmaker, record_label, type,
                release_date, days_from_release, spotify_id, youtube_id,
                youtube_music_id, spotify_url, youtube_url, youtube_music_url, album_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(song_query, (
            self.name, self.main_artist_id, self.producer, self.beatmaker, self.record_label,
            self.type, formatted_release_date, self.days_from_release, self.spotify_id, self.youtube_id,
            self.youtube_music_id, self.spotify_url, self.youtube_url, self.youtube_music_url, self.album_id
        ))
        song_id = cursor.lastrowid

        if self.featured_artists:
            song_artist_query = "INSERT INTO song_artists (song_id, artist_id) VALUES (%s, %s)"
            for artist_id in self.featured_artists:
                cursor.execute(song_artist_query, (song_id, artist_id))

        db_connector.connection.commit()
        print(f"Song '{self.name}' with ID {song_id} inserted successfully")

    def update_in_db(self, db_connector, song_id):
        # Calculate days_from_release before updating
        self.calculate_days_from_release()

        # Format release_date for the database
        formatted_release_date = self.format_release_date_for_db()

        cursor = db_connector.connection.cursor()

        song_query = """
            UPDATE songs SET
                name = %s, main_artist_id = %s, producer = %s, beatmaker = %s,
                record_label = %s, type = %s, release_date = %s, days_from_release = %s,
                spotify_id = %s, youtube_id = %s, youtube_music_id = %s,
                spotify_url = %s, youtube_url = %s, youtube_music_url = %s, album_id = %s
            WHERE song_id = %s
        """
        cursor.execute(song_query, (
            self.name, self.main_artist_id, self.producer, self.beatmaker, self.record_label,
            self.type, formatted_release_date, self.days_from_release, self.spotify_id, self.youtube_id,
            self.youtube_music_id, self.spotify_url, self.youtube_url, self.youtube_music_url, self.album_id, song_id
        ))

        # Optionally update featured artists if necessary
        db_connector.connection.commit()
        print(f"Song with ID {song_id} updated successfully")