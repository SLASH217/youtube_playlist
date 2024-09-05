import os
import json
import google.auth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class YouTubeAPIManager:
    def __init__(
        self, credentials_file="credentials.json", token_file="token.json", scopes=None
    ):
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/youtube"]
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = None
        self.youtube = None

    def authenticate(self):
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

        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

    def get_playlist_items(self, playlist_id):
        """Fetch items in the playlist"""
        items = []
        page_token = None
        while True:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=page_token,
            )
            response = request.execute()
            items.extend(response["items"])
            page_token = response.get("nextPageToken")

            if not page_token:
                break
        return items

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

    def check_duplicates(self, playlist_id):
        """Check for duplicate videos in the playlist"""
        playlist_items = self.get_playlist_items(playlist_id)
        seen_videos = set()
        duplicates = []
        for item in playlist_items:
            video_id = item["contentDetails"]["videoId"]
            if video_id in seen_videos:
                duplicates.append(video_id)
            else:
                seen_videos.add(video_id)
        return duplicates

    def remove_duplicates(self, playlist_id):
        """Remove duplicate videos from the playlist"""
        duplicates = self.check_duplicates(playlist_id)
        for video_id in duplicates:
            self.remove_video_from_playlist(playlist_id, video_id)
            print(f"Removed duplicate video with ID: {video_id}")

    def remove_video_from_playlist(self, playlist_id, video_id):
        """Remove a video from the playlist"""
        playlist_items = self.get_playlist_items(playlist_id)
        for item in playlist_items:
            if item["contentDetails"]["videoId"] == video_id:
                request = self.youtube.playlistItems().delete(id=item["id"])
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

    # Remove deleted videos
    youtube_manager.remove_deleted_videos(PLAYLIST_ID)

    # Check and remove duplicates
    youtube_manager.remove_duplicates(PLAYLIST_ID)

    # Add songs from another playlist, omitting certain indexes
    omit_indexes = [0, 3, 5]  # Example indexes to omit
    youtube_manager.add_playlist_songs_omit(FROM_PLAYLIST_ID, PLAYLIST_ID, omit_indexes)
