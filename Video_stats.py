import os
import pandas as pd
import matplotlib.pyplot as plt
from authenticate import YouTubeAPIManager


class YouTubePlaylistManager(YouTubeAPIManager):
    """
    A class that inherits YouTubeAPIManager to manage YouTube playlist operations.
    """

    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        super().__init__(credentials_file, token_file)

    def get_playlist_videos(self, playlist_id):
        """
        Fetch all videos from a YouTube playlist.
        """
        videos = []
        request = self.youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50
        )

        while request:
            response = request.execute()
            for item in response["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                title = item["snippet"]["title"]
                videos.append({"video_id": video_id, "title": title})

            request = self.youtube.playlistItems().list_next(request, response)

        return videos

    def get_video_statistics(self, video_id):
        """
        Fetch statistics for a YouTube video.
        """
        request = self.youtube.videos().list(part="statistics", id=video_id)
        response = request.execute()

        for item in response["items"]:
            return {
                "views": int(item["statistics"]["viewCount"]),
                "likes": int(item["statistics"].get("likeCount", 0)),
            }

    def collect_playlist_statistics(
        self, playlist_id, output_csv="playlist_statistics.csv"
    ):
        """
        Collect statistics for all videos in a playlist and save them to a CSV file.
        """
        if os.path.exists(output_csv):
            print(f"{output_csv} already exists. Reading from the file.")
            return pd.read_csv(output_csv)

        print(f"Creating {output_csv} and saving playlist statistics...")
        videos = self.get_playlist_videos(playlist_id)
        video_stats = []

        # Collect statistics in a list of dictionaries
        for video in videos:
            stats = self.get_video_statistics(video["video_id"])
            video_stats.append(
                {
                    "Title": video["title"],
                    "Views": stats["views"],
                    "Likes": stats["likes"],
                }
            )

        # Create a DataFrame and save it as CSV
        df = pd.DataFrame(video_stats)
        df.to_csv(output_csv, index=False)

        return df

    def visualize_statistics(self, df):
        """
        Visualize video statistics using matplotlib.
        - Top 10 highest views, likes
        - Bottom 10 lowest views, likes
        """
        # Sort by views and likes
        highest_views = df.nlargest(10, "Views")
        lowest_views = df.nsmallest(10, "Views")
        highest_likes = df.nlargest(10, "Likes")
        lowest_likes = df.nsmallest(10, "Likes")

        # Create subplots for highest and lowest views/likes
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # Plot highest views
        axs[0, 0].barh(highest_views["Title"], highest_views["Views"], color="blue")
        axs[0, 0].set_title("Top 10 Highest Views")
        axs[0, 0].set_xlabel("Views")
        axs[0, 0].invert_yaxis()

        # Plot highest likes
        axs[0, 1].barh(highest_likes["Title"], highest_likes["Likes"], color="green")
        axs[0, 1].set_title("Top 10 Highest Likes")
        axs[0, 1].set_xlabel("Likes")
        axs[0, 1].invert_yaxis()

        # Plot lowest views
        axs[1, 0].barh(lowest_views["Title"], lowest_views["Views"], color="red")
        axs[1, 0].set_title("Bottom 10 Lowest Views")
        axs[1, 0].set_xlabel("Views")
        axs[1, 0].invert_yaxis()

        # Plot lowest likes
        axs[1, 1].barh(lowest_likes["Title"], lowest_likes["Likes"], color="orange")
        axs[1, 1].set_title("Bottom 10 Lowest Likes")
        axs[1, 1].set_xlabel("Likes")
        axs[1, 1].invert_yaxis()

        plt.tight_layout()
        plt.show()


# Example usage
def main():
    playlist_id = (
        "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Replace with your YouTube playlist ID
    )

    # Create a YouTubePlaylistManager instance
    youtube_manager = YouTubePlaylistManager()

    # Authenticate
    youtube_manager.authenticate()

    # Fetch and save playlist statistics to a CSV file (only if it doesn't exist)
    video_stats_df = youtube_manager.collect_playlist_statistics(playlist_id)

    # Visualize video statistics
    youtube_manager.visualize_statistics(video_stats_df)


if __name__ == "__main__":
    main()
