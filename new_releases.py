import os
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
        scopes=[
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ],
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

    def get_playlist_items(self, playlist_id):
        # Fetch items in the playlist
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=10,  # Adjust as needed, max is 50 per request
        )
        response = request.execute()
        return response["items"]

    def add_song_to_playlist(self, playlist_id, video_id):
        """Add a song to the playlist"""
        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        )
        response = request.execute()
        return response

    def add_playlist_songs_omit(
        self, from_playlist_id, to_playlist_id, omit_indexes=[]
    ):
        """Add songs from one playlist to another, omitting certain indexes"""
        playlist_items = self.get_playlist_items(from_playlist_id)

        for idx, item in enumerate(playlist_items):
            if idx in omit_indexes:
                print(f"Omitting song at index {idx}")
                continue

            video_id = item["contentDetails"]["videoId"]
            video_title = item["snippet"]["title"]
            print(f"Adding {video_title} to your playlist.")
            self.add_song_to_playlist(to_playlist_id, video_id)


# Usage example:
if __name__ == "__main__":
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Your playlist ID
    FROM_PLAYLIST_ID = "PL3-sRm8xAzY9gpXTMGVHJWy_FMD67NBed"  # Famous playlist ID
    youtube_manager = YouTubeAPIManager()
    youtube_manager.authenticate()

    # Step 1: Get the items from the famous playlist
    # playlist_items = youtube_manager.get_playlist_items(FROM_PLAYLIST_ID)

    # Step 2: Add the songs from the famous playlist to your playlist
    # for item in playlist_items:
    #     video_title = item["snippet"]["title"]
    #     video_id = item["contentDetails"]["videoId"]
    #     print(f"Adding {video_title} to your playlist.")
    #     youtube_manager.add_song_to_playlist(PLAYLIST_ID, video_id)

    print("Songs from the famous playlist added successfully.")
    # Add songs from another playlist, omitting certain indexes
    omit_indexes = [0, 1, 2, 3, 4]  # Example indexes to omit
    youtube_manager.add_playlist_songs_omit(FROM_PLAYLIST_ID, PLAYLIST_ID, omit_indexes)
