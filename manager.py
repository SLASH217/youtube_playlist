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
        scopes=["https://www.googleapis.com/auth/youtube"],
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
    def remove_video_from_playlist(self, playlist_id, video_id):
        """Remove a video from the playlist"""
        playlist_items = self.get_playlist_items(playlist_id)
        for item in playlist_items:
            if item["contentDetails"]["videoId"] == video_id:
                request = self.youtube.playlistItems().delete(
                    id=item["id"]
                )
                response = request.execute()
                print(f"Removed video {video_id} from playlist.")
    
    def remove_deleted_videos(self, playlist_id):
        """Remove deleted or private videos from the playlist"""
        playlist_items = self.get_playlist_items(playlist_id)
        for item in playlist_items:
            title = item["snippet"]["title"]
            if title in ["Deleted video", "Private video"]:
                video_id = item["contentDetails"]["videoId"]
                self.remove_video_from_playlist(playlist_id, video_id)
                print(f"Removed {title} from playlist.")


# Usage example:
def parse_video_title(title):
    """Parse the video title to separate the artist and song name."""
    if " - " in title:
        artist, song = title.split(" - ", 1)  # Split into artist and song
        return artist.strip(), song.strip()   # Remove extra spaces
    else:
        return None, title.strip()        
if __name__ == "__main__":
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Replace with your playlist ID
    youtube_manager = YouTubeAPIManager()
    youtube_manager.authenticate()
    youtube_manager.remove_deleted_videos(PLAYLIST_ID)
    playlist_items = youtube_manager.get_playlist_items(PLAYLIST_ID)

    # Writing to CSV file efficiently
    with open("playlist_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(["Title", "Video ID", "Artist", "Song"])

        for item in playlist_items:
            title = item["snippet"]["title"]
            video_id = item["contentDetails"]["videoId"]
            
            # Parse artist and song from title
            artist, song = parse_video_title(title)
            
            # Write to CSV: include artist as "Unknown" if it's None
            writer.writerow([title, video_id, artist if artist else "Unknown", song])

print("Playlist data written to 'playlist_data.csv' successfully.")
print(f"Data for {len(playlist_items)} videos saved to 'playlist_data.csv'.")
