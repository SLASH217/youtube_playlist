import os
import csv
import json
import google.auth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class YouTubeAPIManager:
    def __init__(
        self,
        credentials_file="credentials.json",
        token_file="token.json",
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        # Authenticate the user with OAuth 2.0
        if os.path.exists(self.token_file):
            with open(self.token_file, "r", encoding="utf-8") as token:
                self.credentials = (
                    google.oauth2.credentials.Credentials.from_authorized_user_info(
                        json.load(token), self.scopes
                    )
                )
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes
            )
            self.credentials = flow.run_local_server(port=0)
            with open(self.token_file, "w", encoding="utf-8") as token:
                token.write(self.credentials.to_json())

        # Build the YouTube service
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

    def get_playlist_items(self, plist_id):
        # Fetch items in the playlist
        items = []
        page_token = None
        while True:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=plist_id,
                maxResults=50,  # Max is 50 per request
                pageToken=page_token,  # Include the page token to get all items
            )
            response = request.execute()
            items.extend(response["items"])
            page_token = response.get("nextPageToken")

            if not page_token:
                break
        return items


# Usage example:

if __name__ == "__main__":
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Replace with your playlist ID
    youtube_manager = YouTubeAPIManager()
    youtube_manager.authenticate()
    playlist_items = youtube_manager.get_playlist_items(PLAYLIST_ID)

    # Writing to CSV file efficiently
    with open("playlist_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Title", "Video ID"])

        for item in playlist_items:
            title = item["snippet"]["title"]
            video_id = item["contentDetails"]["videoId"]
            writer.writerow([title, video_id])

    print(f"Data for {len(playlist_items)} videos saved to 'playlist_data.csv'.")
