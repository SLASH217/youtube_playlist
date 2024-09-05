import csv
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

    def get_playlist_items(self, plist_id):
        """Gets all the videos in a playlist"""
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
    if " - " in title:
        artist, song = title.split("-", 1)  # Split into artist and song
        return artist.strip(), song.strip()  # Remove extra spaces
    else:
        return None, title.strip()


if __name__ == "__main__":
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Replace with your playlist ID
    playlist_manager = PlaylistManager()  # Inherit from YouTubeAPIManager
    playlist_manager.authenticate()  # Authenticate with OAuth

    # Fetch playlist items
    playlistItems = playlist_manager.get_playlist_items(PLAYLIST_ID)

    # Writing to CSV file efficiently
    with open("playlist_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(["Title", "Video ID", "Artist", "Song"])

        for Item in playlistItems:
            Title = Item["snippet"]["title"]
            videoId = Item["contentDetails"]["videoId"]

            # Parse artist and song from title
            Artist, Song = parse_video_title(Title)

            # Write to CSV: include Artist as "Unknown" if it's None
            writer.writerow([Title, videoId, Artist if Artist else "Unknown", Song])

    print("Playlist data written to 'playlist_data.csv' successfully.")
    print(f"Data for {len(playlistItems)} videos saved to 'playlist_data.csv'.")
