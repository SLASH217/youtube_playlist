import pandas as pd
import os
from authenticate import (
    YouTubeAPIManager,
)


class PlaylistManager(YouTubeAPIManager):
    """Has the methods:
    - get_playlist : gets all the videos in a playlist
    - remove deleted or private videos from playlist

    Args:
        YouTubeAPIManager (Class): Takes in all the authenticator data for YouTube API
    """

    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        super().__init__(credentials_file, token_file)

    def get_playlist_items(self, plist_id):
        """Gets all the videos in a playlist SPECIFICALLY FOR MY PLAYLIST"""
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
        """Remove a video from the playlist FUCTION USED IN remove_deleted_videos function"""
        playlist_items = self.get_playlist_items(playlist_id)
        for item in playlist_items:
            if item["contentDetails"]["videoId"] == video_id:
                request = self.youtube.playlistItems().delete(id=item["id"])
                request.execute()
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


def parse_video_title(title):
    """Parse the video title to separate the artist and song name."""
    if "-" in title: 
        artist, song = title.split("-", 1)  # Split into artist and song
        return artist.strip(), song.strip()  # Remove extra spaces
    else:
        return None, title.strip()


def main():
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Replace with your playlist ID
    playlist_manager = PlaylistManager()  # Inherit from YouTubeAPIManager
    playlist_manager.authenticate()  # Authenticate with OAuth

    # Fetch playlist items
    playlistItems = playlist_manager.get_playlist_items(PLAYLIST_ID)

    data = []
    for item in playlistItems:
        title = item["snippet"]["title"]
        video_id = item["contentDetails"]["videoId"]

        # Parse artist and song from title
        artist, song = parse_video_title(title)

        # Append to data list
        data.append([title, video_id, artist if artist else "Unknown", song])

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Title", "Video ID", "Artist", "Song"])

    # File path
    file_path = "playlist_data.csv"

    # Write to CSV file only if it doesn't already exist
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False, encoding="utf-8")
        print(f"Playlist data written to '{file_path}' successfully.")
    else:
        print(f"'{file_path}' already exists. No data was written.")

    print(f"Data for {len(playlistItems)} videos saved to '{file_path}'.")


if __name__ == "__main__":
    main()
