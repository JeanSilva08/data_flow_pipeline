class Artist:
    def __init__(
        self,
        name,
        category=None,
        r_label=None,
        spotify_id=None,
        youtube_id=None,
        Instagram_id=None,
        TikTok_id=None,
        Twitter_id=None,
        Twitch_id=None,
        Spotify_url=None,
        youtube_url=None,
        instagram_url=None,
        tiktok_url=None,
        twitter_url=None,
        twitch_url=None
    ):
        self.name = name
        self.category = category
        self.r_label = r_label
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.Instagram_id = Instagram_id
        self.TikTok_id = TikTok_id
        self.Twitter_id = Twitter_id
        self.Twitch_id = Twitch_id
        self.Spotify_url = Spotify_url
        self.youtube_url = youtube_url
        self.instagram_url = instagram_url
        self.tiktok_url = tiktok_url
        self.twitter_url = twitter_url
        self.twitch_url = twitch_url

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
        query = """
            INSERT INTO artists (
                name, category, r_label, spotify_id, youtube_id, Instagram_id,
                TikTok_id, Twitter_id, Twitch_id, Spotify_url, youtube_url,
                instagram_url, tiktok_url, twitter_url, twitch_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            self.name, self.category, self.r_label, self.spotify_id, self.youtube_id,
            self.Instagram_id, self.TikTok_id, self.Twitter_id, self.Twitch_id,
            self.Spotify_url, self.youtube_url, self.instagram_url, self.tiktok_url,
            self.twitter_url, self.twitch_url
        ))
        db_connector.connection.commit()
        print(f"Artist {self.name} inserted successfully")

    def update_in_db(self, db_connector, artist_id):
        cursor = db_connector.connection.cursor()
        query = """
            UPDATE artists SET
                name = %s, category = %s, r_label = %s, spotify_id = %s, youtube_id = %s,
                Instagram_id = %s, TikTok_id = %s, Twitter_id = %s, Twitch_id = %s,
                Spotify_url = %s, youtube_url = %s, instagram_url = %s, tiktok_url = %s,
                twitter_url = %s, twitch_url = %s
            WHERE artist_id = %s
        """
        cursor.execute(query, (
            self.name, self.category, self.r_label, self.spotify_id, self.youtube_id,
            self.Instagram_id, self.TikTok_id, self.Twitter_id, self.Twitch_id,
            self.Spotify_url, self.youtube_url, self.instagram_url, self.tiktok_url,
            self.twitter_url, self.twitch_url, artist_id
        ))
        db_connector.connection.commit()
        print(f"Artist with ID {artist_id} updated successfully")

    @staticmethod
    def delete_from_db(db_connector, artist_id):
        cursor = db_connector.connection.cursor()
        check_songs_query = "SELECT COUNT(*) FROM songs WHERE main_artist_id = %s"
        cursor.execute(check_songs_query, (artist_id,))
        song_count = cursor.fetchone()[0]
        if song_count > 0:
            print(f"Cannot delete artist with ID {artist_id} because {song_count} songs are associated with them.")
            return
        delete_artist_query = "DELETE FROM artists WHERE artist_id = %s"
        cursor.execute(delete_artist_query, (artist_id,))
        db_connector.connection.commit()
        print(f"Artist with ID {artist_id} deleted successfully")

    @classmethod
    def get_by_id(cls, db, artist_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id,))
        result = cursor.fetchone()
        if result:
            return cls(
                name=result[1],
                category=result[2],
                r_label=result[3],
                spotify_id=result[4],
                youtube_id=result[5],
                Instagram_id=result[6],
                TikTok_id=result[7],
                Twitter_id=result[8],
                Twitch_id=result[9],
                Spotify_url=result[10],
                youtube_url=result[11],
                instagram_url=result[12],
                tiktok_url=result[13],
                twitter_url=result[14],
                twitch_url=result[15]
            )
        return None

    @classmethod
    def get_all(cls, db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM artists"
        cursor.execute(query)
        results = cursor.fetchall()

        artists = []
        for result in results:
            artist = cls(
                name=result[1],
                category=result[2],
                r_label=result[3],
                spotify_id=result[4],
                youtube_id=result[5],
                Instagram_id=result[6],
                TikTok_id=result[7],
                Twitter_id=result[8],
                Twitch_id=result[9],
                Spotify_url=result[10],
                youtube_url=result[11],
                instagram_url=result[12],
                tiktok_url=result[13],
                twitter_url=result[14],
                twitch_url=result[15]
            )
            artists.append(artist)

        return artists