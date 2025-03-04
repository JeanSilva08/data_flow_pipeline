import json

class Song:
    def __init__(
        self,
        name,
        main_artist_id,
        producer=None,
        ytmsc_id=None,
        record_label=None,
        type=None,
        release_date=None,
        days_from_release=None,
        spotify_id=None,
        youtube_id=None,
        spotify_url=None,
        youtube_url=None,
        youtube_music_url=None,
        album_id=None,
        featured_artists=None
    ):
        self.name = name
        self.main_artist_id = main_artist_id
        self.producer = producer
        self.ytmsc_id = ytmsc_id
        self.record_label = record_label
        self.type = type
        self.release_date = release_date
        self.days_from_release = days_from_release
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.spotify_url = spotify_url
        self.youtube_url = youtube_url
        self.youtube_music_url = youtube_music_url
        self.album_id = album_id
        self.featured_artists = featured_artists or []  # List of artist IDs or names

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
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
        db_connector.connection.commit()
        print(f"Song {self.name} inserted successfully")

    def update_in_db(self, db_connector, song_id):
        cursor = db_connector.connection.cursor()
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
        db_connector.connection.commit()
        print(f"Song with ID {song_id} updated successfully.")

    @classmethod
    @classmethod
    def get_by_id(cls, db, song_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM songs WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        result = cursor.fetchone()
        if result:
            return cls(
                name=result[1],
                main_artist_id=result[2],
                producer=result[6],
                ytmsc_id=result[5],
                record_label=result[7],
                type=result[8],
                release_date=result[9],
                days_from_release=result[10],
                spotify_id=result[3],
                youtube_id=result[4],
                spotify_url=result[11],
                youtube_url=result[12],
                youtube_music_url=result[13],
                album_id=result[14],
                featured_artists=json.loads(result[15]) if result[15] else []  # Convert JSON to list
            )
        return None

    @classmethod
    def get_all(cls, db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM songs"
        cursor.execute(query)
        results = cursor.fetchall()

        songs = []
        for result in results:
            song = cls(
                name=result[1],
                main_artist_id=result[2],
                producer=result[6],
                ytmsc_id=result[5],
                record_label=result[7],
                type=result[8],
                release_date=result[9],
                spotify_id=result[3],
                youtube_id=result[4],
                spotify_url=result[11],
                youtube_url=result[12],
                youtube_music_url=result[13],
                album_id=result[14],
                featured_artists=json.loads(result[15]) if result[15] else []  # Convert JSON to list
            )
            songs.append(song)

        return songs