import os
import json
import google.auth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

class YouTubeAPIManager:
    def __init__(self, credentials_file='credentials.json', token_file='token.json', scopes=["https://www.googleapis.com/auth/youtube.readonly"]):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        # Authenticate the user with OAuth 2.0
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token:
                self.credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.load(token), self.scopes)
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
            self.credentials = flow.run_local_server(port=0)
            with open(self.token_file, 'w') as token:
                token.write(self.credentials.to_json())

        # Build the YouTube service
        self.youtube = googleapiclient.discovery.build("youtube", "v3", credentials=self.credentials)

    def get_playlist_items(self, playlist_id):
        # Fetch items in the playlist
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50  # Adjust as needed, max is 50 per request
        )
        response = request.execute()
        return response['items']

# Usage example:

if __name__ == "__main__":
    playlist_id = 'PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp'  # Replace with your playlist ID
    youtube_manager = YouTubeAPIManager()
    youtube_manager.authenticate()
    playlist_items = youtube_manager.get_playlist_items(playlist_id)
    
    # Process playlist items as needed
    for item in playlist_items:
        title = item['snippet']['title']
        video_id = item['contentDetails']['videoId']
        print(f"Title: {title}, Video ID: {video_id}")
