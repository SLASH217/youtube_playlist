from authenticate import YouTubeAPIManager


class AutomateNew(YouTubeAPIManager):
    """Automation of the addtion of new songs to my daily playlist:
    - get playlist items from popular playlist
    - add the songs to my playlist
    - optionally: target or omit certain indexes of songs

    Args:
        YouTubeAPIManager (class): authenticator class
    """

    def get_playlist_items(self, playlist_id):
        """Get the items of a playlist"""
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
        self, from_playlist_id, to_playlist_id, omit_indexes=None
    ):
        """Add songs from one playlist to another, omitting certain indexes"""
        if omit_indexes is None:
            omit_indexes = []  # Initialize an empty list if none is provided
        playlist_items = self.get_playlist_items(from_playlist_id)

        for idx, item in enumerate(playlist_items):
            if idx in omit_indexes:
                print(f"Omitting song at index {idx}")
                continue

            video_id = item["contentDetails"]["videoId"]
            video_title = item["snippet"]["title"]
            print(f"Adding {video_title} to your playlist.")
            self.add_song_to_playlist(to_playlist_id, video_id)

    def add_playlist_songs_target(
        self, from_playlist_id, to_playlist_id, target_indexes=None
    ):
        """
        Add songs from one playlist to another, only targeting certain indexes.
        """
        if target_indexes is None:
            target_indexes = []  # Initialize an empty list if none is provided
        playlist_items = self.get_playlist_items(from_playlist_id)

        for idx, item in enumerate(playlist_items):
            if idx not in target_indexes:
                print(f"Skipping song at index {idx}")
                continue

            video_id = item["contentDetails"]["videoId"]
            video_title = item["snippet"]["title"]
            print(f"Adding {video_title} from index {idx} to your playlist.")
            self.add_song_to_playlist(to_playlist_id, video_id)


# Usage example:
if __name__ == "__main__":
    PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Your playlist ID
    FROM_PLAYLIST_ID = "PL3-sRm8xAzY9gpXTMGVHJWy_FMD67NBed"  # Famous playlist ID
    youtube_manager = AutomateNew()
    youtube_manager.authenticate()

    # Step 1: Get the items from the famous playlist
    playlistItems = youtube_manager.get_playlist_items(FROM_PLAYLIST_ID)

    # Step 2: Add the songs from the famous playlist to your playlist
    for Item in playlistItems:
        videoTitle = Item["snippet"]["title"]
        videoId = Item["contentDetails"]["videoId"]
        print(f"Adding {videoTitle} to your playlist.")
        youtube_manager.add_song_to_playlist(PLAYLIST_ID, videoId)

    # # Add songs from another playlist, omitting certain indexes
    # omitIndexes = [0, 1, 2, 3, 4]  # Example indexes to omit
    # youtube_manager.add_playlist_songs_omit(FROM_PLAYLIST_ID, PLAYLIST_ID, omitIndexes)
    # print("Songs from the famous playlist added successfully.")
    # # Define your target indexes
    # targetIndexes = [1, 3, 5]

    # # Add songs from one playlist to another, only from the specified target indexes
    # youtube_manager.add_playlist_songs_target(
    #     FROM_PLAYLIST_ID, PLAYLIST_ID, targetIndexes
    # )
