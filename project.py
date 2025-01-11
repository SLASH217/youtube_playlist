from Video_stats import YouTubePlaylistManager
from manager import PlaylistManager, parse_video_title
from new_releases import AutomateNew
from collections import Counter
import csv
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"
FROM_PLAYLIST_ID = "PL3-sRm8xAzY9gpXTMGVHJWy_FMD67NBed"
STATS_OUTPUT_CSV = "playlist_stats.csv"
NUMBER_OF_SONGS_TO_ADD = 5
DATA_PLAYLIST_CSV = "clean_playlist_data.csv"


def clean_stats(input_csv, output_csv):
    """
    Cleans up text in the CSV file (e.g., removes certain words).
    """

    def clean_text(text):
        text = text.lower()
        text = re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}", "", text)
        words_to_remove = ["official", "music", "video", "lyrics"]
        text = re.sub(
            r"\b(?:" + "|".join(words_to_remove) + r")\b", "", text, flags=re.IGNORECASE
        )
        return " ".join(text.split())

    with open(input_csv, "r", newline="", encoding="utf-8") as input_file, open(
        output_csv, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        writer.writerow(next(reader))  # Write header

        for row in reader:
            writer.writerow([clean_text(cell) for cell in row])

    logger.info(f"Data cleaning complete. Saved to {output_csv}.")


def clean_playlist_data(
    input_csv="playlist_data.csv", output_csv="clean_playlist_data.csv"
):
    """
    Cleans playlist data using the same method as `clean_stats`.
    """
    clean_stats(input_csv, output_csv)


def common_artists(csv_file, artist_column="Artist", top_n=20):
    """
    Plot the top N most frequent artists.
    """
    artists = []
    with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        try:
            artist_index = header.index(artist_column)
        except ValueError:
            logger.error(f"Column '{artist_column}' not found in the CSV header.")
            return

        for row in reader:
            artists.append(row[artist_index])

    if artists:
        artist_counts = Counter(artists)
        top_artists = artist_counts.most_common(top_n)

        artist_names, counts = zip(*top_artists)
        plt.figure(figsize=(10, 6))
        plt.barh(artist_names, counts, color="skyblue")
        plt.xlabel("Number of Songs")
        plt.ylabel("Artists")
        plt.title(f"Top {top_n} Most Common Artists in Playlist")
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
    else:
        logger.error("No artist data to plot.")


def main():
    """
    Main program to manage playlist and stats.
    """
    youtube_manager = YouTubePlaylistManager()
    playlist_manager = PlaylistManager()
    automate_new = AutomateNew()

    youtube_manager.authenticate()
    playlist_manager.authenticate()
    automate_new.authenticate()

    while True:
        print("\nYouTube Playlist Manager Menu")
        print("1. Fetch new songs from another playlist")
        print("2. Fetch Song data from playlist items")
        print("3. Fetch Video statistics from playlist items")
        print("4. Clean playlist data")
        print("5. Clean playlist statistics")
        print("6. Plot top common artists from playlist data")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == "5":
            try:
                clean_stats(STATS_OUTPUT_CSV, "clean_playlist_stats.csv")
            except Exception as e:
                print(f"Error cleaning stats: {e}")

        elif choice == "4":
            clean_playlist_data()

        elif choice == "6":
            if os.path.exists(DATA_PLAYLIST_CSV):
                common_artists(DATA_PLAYLIST_CSV)
            else:
                logger.error(
                    f"{DATA_PLAYLIST_CSV} does not exist. Clean the playlist data first."
                )

        elif choice == "1":
            try:
                automate_new.add_new_songs(
                    FROM_PLAYLIST_ID, PLAYLIST_ID, NUMBER_OF_SONGS_TO_ADD
                )
                logger.info("Songs added successfully.")
            except Exception as e:
                logger.error(f"An error occurred: {e}")

        elif choice == "3":
            video_stats_df = youtube_manager.collect_playlist_statistics(
                PLAYLIST_ID, STATS_OUTPUT_CSV
            )
            youtube_manager.visualize_statistics(video_stats_df)

        elif choice == "2":
            playlistItems = playlist_manager.get_playlist_items(PLAYLIST_ID)
            data = []
            for item in playlistItems:
                title = item["snippet"]["title"]
                video_id = item["contentDetails"]["videoId"]
                artist, song = parse_video_title(title)
                data.append([title, video_id, artist or "Unknown", song])

            df = pd.DataFrame(data, columns=["Title", "Video ID", "Artist", "Song"])
            file_path = "playlist_data.csv"

            if not os.path.exists(file_path):
                df.to_csv(file_path, index=False, encoding="utf-8")
                logger.info(f"Data saved to {file_path}")
            else:
                logger.info(f"{file_path} already exists.")

        elif choice == "7":
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
