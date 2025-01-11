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
        items = []
        page_token = None
        while True:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=plist_id,
                maxResults=50,  # Max is 50 per request
                pageToken=page_token,
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
        artist, song = title.split("-", 1)
        return artist.strip(), song.strip()
    else:
        return None, title.strip()


def main():
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp" #this is my specific playlist ID "change it to your own"
    playlist_manager = PlaylistManager()
    playlist_manager.authenticate()

    playlistItems = playlist_manager.get_playlist_items(PLAYLIST_ID)

    data = []
    for item in playlistItems:
        title = item["snippet"]["title"]
        video_id = item["contentDetails"]["videoId"]

        artist, song = parse_video_title(title)

        data.append([title, video_id, artist if artist else "Unknown", song])

    df = pd.DataFrame(data, columns=["Title", "Video ID", "Artist", "Song"])

    file_path = "playlist_data.csv"

    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False, encoding="utf-8")
        print(f"Playlist data written to '{file_path}' successfully.")
    else:
        print(f"'{file_path}' already exists. No data was written.")

    print(f"Data for {len(playlistItems)} videos saved to '{file_path}'.")


if __name__ == "__main__":
    main()
