import logging
from authenticate import YouTubeAPIManager
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomateNew(YouTubeAPIManager):
    """
    Automation of the addition of new songs to my daily playlist:
    - Get playlist items from a popular playlist
    - Add only the new songs (not already in my playlist)
    - Optionally, limit the number of songs to add

    Args:
        YouTubeAPIManager (class): Authenticator class
    """

    def get_playlist_items(self, playlist_id):
        """Fetch all items from a playlist."""
        items = []
        page_token = None
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,  # Max 50 results per request
                    pageToken=page_token,
                )
                response = request.execute()
                items.extend(response.get("items", []))
                page_token = response.get("nextPageToken")

                if not page_token:
                    break

            if not items:
                logger.warning("No items found in playlist %s", playlist_id)
            return items
        except HttpError as e:
            logger.error(
                "Failed to retrieve playlist items for %s : %s ", playlist_id, e
            )
            return []

    def add_song_to_playlist(self, playlist_id, video_id):
        """Add a song to the playlist."""
        try:
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
            logger.info(
                "Successfully added video ID %s to playlist %s", video_id, playlist_id
            )
            return response

        except HttpError as e:
            logger.error(
                "Failed to add video ID %s to playlist %s: %s", video_id, playlist_id, e
            )
            return None

    def add_new_songs(self, from_playlist_id, to_playlist_id, number_of_songs_to_add):
        """Add songs from `from_playlist_id` to `to_playlist_id` if they are not already in the target playlist."""
        from_playlist_items = self.get_playlist_items(from_playlist_id)
        if not from_playlist_items:
            logger.error(
                "Failed to fetch playlist items from %s. Aborting operation. ",
                from_playlist_id,
            )
            return

        to_playlist_items = self.get_playlist_items(to_playlist_id)
        if not to_playlist_items:
            logger.error(
                "Failed to fetch playlist items from %s. Aborting operation.",
                to_playlist_id,
            )
            return

        to_playlist_video_ids = {
            item["contentDetails"]["videoId"] for item in to_playlist_items
        }

        new_songs = [
            item
            for item in from_playlist_items
            if item["contentDetails"]["videoId"] not in to_playlist_video_ids
        ]

        if not new_songs:
            logger.info(
                "No new songs to add. All songs from playlist %s are already in %s.",
                from_playlist_items,
                to_playlist_id,
            )
            return

        songs_to_add = new_songs[:number_of_songs_to_add]

        for item in songs_to_add:
            video_id = item["contentDetails"]["videoId"]
            video_title = item["snippet"]["title"]
            logger.info("Adding '%s' to playlist %s.", video_title, to_playlist_id)
            self.add_song_to_playlist(to_playlist_id, video_id)

        logger.info(
            "Added %s new songs to playlist %s.", len(songs_to_add), to_playlist_id
        )


# Usage example:
def main():
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Your playlist ID
    FROM_PLAYLIST_ID = "PL3-sRm8xAzY9gpXTMGVHJWy_FMD67NBed"  # Famous playlist ID
    NUMBER_OF_SONGS_TO_ADD = 5  # Number of songs to add

    try:
        youtube_manager = AutomateNew()
        youtube_manager.authenticate()

        youtube_manager.add_new_songs(
            FROM_PLAYLIST_ID, PLAYLIST_ID, NUMBER_OF_SONGS_TO_ADD
        )
        logger.info("Songs from the famous playlist added successfully.")

    except Exception as e:
        logger.error("An error occurred during execution: %s", e)


if __name__ == "__main__":
    main()
