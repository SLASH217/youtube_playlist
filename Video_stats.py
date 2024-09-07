import os
import csv
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
        Only create the file if it doesn't already exist.
        """
        if os.path.exists(output_csv):
            print(f"{output_csv} already exists. Reading from the file.")
            return self.read_csv(output_csv)

        print(f"Creating {output_csv} and saving playlist statistics...")
        videos = self.get_playlist_videos(playlist_id)
        video_stats = []

        with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Views", "Likes"])

            for video in videos:
                stats = self.get_video_statistics(video["video_id"])
                video_stats.append(
                    {
                        "title": video["title"],
                        "views": stats["views"],
                        "likes": stats["likes"],
                    }
                )
                writer.writerow([video["title"], stats["views"], stats["likes"]])

        return video_stats

    def read_csv(self, csv_file):
        """
        Read video statistics from an existing CSV file.
        """
        video_stats = []
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                video_stats.append(
                    {
                        "title": row["Title"],
                        "views": int(row["Views"]),
                        "likes": int(row["Likes"]),
                    }
                )
        return video_stats

    def visualize_statistics(self, video_stats):
        """
        Visualize video statistics using matplotlib.
        - Top 10 highest views, likes
        - Bottom 10 lowest views, likes
        """
        # Sort by views and likes
        video_stats_sorted_by_views = sorted(
            video_stats, key=lambda x: x["views"], reverse=True
        )
        video_stats_sorted_by_likes = sorted(
            video_stats, key=lambda x: x["likes"], reverse=True
        )

        # Get top and bottom 10 videos for views and likes
        highest_views = video_stats_sorted_by_views[:10]
        lowest_views = video_stats_sorted_by_views[-10:]
        highest_likes = video_stats_sorted_by_likes[:10]
        lowest_likes = video_stats_sorted_by_likes[-10:]

        # Create subplots for highest and lowest views/likes
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # Plot highest views
        axs[0, 0].barh(
            [video["title"] for video in highest_views],
            [video["views"] for video in highest_views],
            color="blue",
        )
        axs[0, 0].set_title("Top 10 Highest Views")
        axs[0, 0].set_xlabel("Views")
        axs[0, 0].invert_yaxis()

        # Plot highest likes
        axs[0, 1].barh(
            [video["title"] for video in highest_likes],
            [video["likes"] for video in highest_likes],
            color="green",
        )
        axs[0, 1].set_title("Top 10 Highest Likes")
        axs[0, 1].set_xlabel("Likes")
        axs[0, 1].invert_yaxis()

        # Plot lowest views
        axs[1, 0].barh(
            [video["title"] for video in lowest_views],
            [video["views"] for video in lowest_views],
            color="red",
        )
        axs[1, 0].set_title("Bottom 10 Lowest Views")
        axs[1, 0].set_xlabel("Views")
        axs[1, 0].invert_yaxis()

        # Plot lowest likes
        axs[1, 1].barh(
            [video["title"] for video in lowest_likes],
            [video["likes"] for video in lowest_likes],
            color="orange",
        )
        axs[1, 1].set_title("Bottom 10 Lowest Likes")
        axs[1, 1].set_xlabel("Likes")
        axs[1, 1].invert_yaxis()

        plt.tight_layout()
        plt.show()


# Example usage
if __name__ == "__main__":
    playlist_id = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"  # Replace with your YouTube playlist ID

    # Create a YouTubePlaylistManager instance
    youtube_manager = YouTubePlaylistManager()

    # Authenticate
    youtube_manager.authenticate()

    # Fetch and save playlist statistics to a CSV file (only if it doesn't exist)
    video_stats = youtube_manager.collect_playlist_statistics(playlist_id)

    # Visualize video statistics
    youtube_manager.visualize_statistics(video_stats)
