import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.database.db_connector import DBConnector  # Import DBConnector
class GoogleSheetsUploader:

    def __init__(self, db: DBConnector, credentials_file="config/service_account.json", sheet_name="Novo Layout do Midia Kit"):
        self.db = db
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.client = self._authenticate_google_sheets()

    def _authenticate_google_sheets(self):
        """
        Authenticate with Google Sheets using OAuth.
        """
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        return gspread.authorize(creds)

    def _fetch_media_kit_data(self):
        """
        Fetch all data from the media_kit_data table with explicit column selection.
        """
        query = """
            SELECT 
                artist_name, category, record_label,
                spotify_song_count, spotify_monthly_listeners,
                spotify_listener_change_30d, spotify_followers,
                spotify_total_streams, spotify_stream_change_30d,
                youtube_subscribers, youtube_views, youtube_music_views,
                youtube_total_views, instagram_followers,
                instagram_impressions, instagram_accounts_reached,
                instagram_content_interaction, instagram_engaged_accounts,
                tiktok_followers, tiktok_likes, twitter_followers,
                twitter_tweets, twitter_tweets_last_30d, twitch_followers
            FROM media_kit_data
        """
        data = self.db.fetch_all(query)
        if data:
            print("Fetched data columns:", data[0].keys())  # Log the columns
        return data

    def upload_to_sheets(self):
        """
        Upload media_kit_data to Google Sheets within the range A5:X42.
        """
        data = self._fetch_media_kit_data()
        if not data:
            print("No data found in media_kit_data.")
            return

        sheet = self.client.open(self.sheet_name).sheet1

        # Clear only the range A5:X42
        sheet.batch_clear(["A5:X42"])

        # Prepare data for upload (only values, no headers)
        values = [list(row.values()) for row in data]

        # Log the data and range for debugging
        print("Data to upload:", values)
        print("Number of rows:", len(values))
        print("Number of columns:", len(values[0]) if values else 0)

        # Upload data to the range A5:X{end_row}
        if values:
            # Calculate the end row based on the number of rows in the data
            end_row = 5 + len(values) - 1
            # Define the range (A5:X{end_row})
            range_name = f"A5:X{end_row}"
            print("Uploading to range:", range_name)
            # Update the range with the data
            sheet.update(range_name, values)
            print(f"Data uploaded to Google Sheets successfully in range {range_name}.")
        else:
            print("No data to upload.")