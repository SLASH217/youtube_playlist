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

# Clean and Efficient Program with All Functions Integrated
PLAYLIST_ID = "PLmPwAQy0bOJZ3U_u5BGeFC1fE2FvzZ9Yp"
FROM_PLAYLIST_ID = "PL3-sRm8xAzY9gpXTMGVHJWy_FMD67NBed"
STATS_OUTPUT_CSV = "playlist_stats.csv"
NUMBER_OF_SONGS_TO_ADD = 5  # Number of songs to add
DATA_PLAYLIST_CSV = "cleaned_playlist_data.csv"
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_stats(input_csv, output_csv):
    """
    Cleans the statistics data from an input CSV file and saves it to an output CSV.
    """

    def clean_text(text):
        # Convert text to lowercase
        text = text.lower()
        # Remove text within brackets and the brackets themselves
        text = re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}", "", text)
        # Remove specific words irrespective of case
        words_to_remove = ["official", "music", "video", "lyrics"]
        text = re.sub(
            r"\b(?:" + "|".join(words_to_remove) + r")\b", "", text, flags=re.IGNORECASE
        )
        # Remove extra spaces
        text = " ".join(text.split())
        return text

    # Open input and output CSV files
    with open(input_csv, "r", newline="", encoding="utf-8") as input_file, open(
        output_csv, "w", newline="", encoding="utf-8"
    ) as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        # Write the header
        header = next(reader)
        writer.writerow(header)

        # Process and clean each row
        for row in reader:
            cleaned_row = [clean_text(cell) for cell in row]
            writer.writerow(cleaned_row)

    logger.info("Data cleaning complete. Cleaned data saved to '%s'.", output_csv)


def clean_playlist_data(
    input_csv="playlist_data.csv", output_csv="clean_playlist_data.csv"
):
    """
    Cleans the playlist data from an input CSV file and saves it to an output CSV.
    """
    clean_stats(
        input_csv, output_csv
    )  # Reuse the clean_stats function since the process is the same


def common_arts(csv_file, artist_column="Artist", top_n=20):
    """
    Plots the top N most common artists from the cleaned playlist data.
    """
    # Collect artists from the CSV file
    artists = []
    with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        # Find the index of the artist column
        try:
            artist_index = header.index(artist_column)
        except ValueError:
            logger.error(
                "Error: Column ' %s ' not found in the CSV header.", artist_column
            )
            return

        for row in reader:
            artists.append(row[artist_index])

    # Count artist frequencies
    artist_counts = Counter(artists)
    top_artists = artist_counts.most_common(top_n)

    if not top_artists:
        logger.error("No artist data found to plot.")
        return

    # Split the data into two lists for plotting
    artist_names, counts = zip(*top_artists)

    # Create bar graph
    plt.figure(figsize=(10, 6))  # Adjust the size of the figure
    plt.barh(artist_names, counts, color="skyblue")
    plt.xlabel("Number of Songs")
    plt.ylabel("Artists")
    plt.title(f"Top {top_n} Most Common Artists in Playlist")
    plt.gca().invert_yaxis()  # Invert y-axis to have the most common artist on top
    plt.tight_layout()
    plt.show()


def main():
    """
    Main menu-driven program that incorporates the use of YouTubePlaylistManager,
    PlaylistManager, and AutomateNew.
    """
    # Instantiate objects for each class
    youtube_manager = YouTubePlaylistManager()
    playlist_manager = PlaylistManager()
    automate_new = AutomateNew()

    # Authenticate each manager (assuming they all have authenticate methods)
    youtube_manager.authenticate()
    playlist_manager.authenticate()
    automate_new.authenticate()

    while True:
        print("\nYouTube Playlist Manager Menu")
        print("1. Clean playlist statistics")
        print("2. Clean playlist data")
        print("3. Plot top common artists from playlist data")
        print("4. Fetch new songs from another playlist (AutomateNew)")
        print("5. Fetch Video statistics from playlist items")
        print("6. Fetch Song data from playlist items")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            # Clean statistics data
            try:
                clean_stats("playlist_stats.csv", "clean_playlist_stats.csv")
            except Exception as e:
                print(e)
        elif choice == "2":
            # Clean playlist data
            clean_playlist_data("playlist_data.csv", "cleaned_playlist_data.csv")

        elif choice == "3":
            # Plot top common artists from cleaned playlist data
            if os.path.exists(DATA_PLAYLIST_CSV):
                common_arts(DATA_PLAYLIST_CSV)
            else:
                logger.error(
                    "%s does not exist. Please clean the playlist data first.",
                    DATA_PLAYLIST_CSV,
                )

        elif choice == "4":
            try:
                # Fetch and add new songs
                automate_new.add_new_songs(
                    FROM_PLAYLIST_ID, PLAYLIST_ID, NUMBER_OF_SONGS_TO_ADD
                )
                logger.info("Songs from the famous playlist added successfully.")

            except Exception as e:
                logger.error("An error occurred during execution: %s", e)

        elif choice == "5":
            # Fetch and save playlist statistics to a CSV file if it doesn't exist
            video_stats_df = youtube_manager.collect_playlist_statistics(
                PLAYLIST_ID, STATS_OUTPUT_CSV
            )
            # Visualize video statistics
            youtube_manager.visualize_statistics(video_stats_df)

        elif choice == "6":
            # Fetch song data from playlist items
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
                logger.info("Playlist data written to '%s' successfully.", file_path)
            else:
                logger.info("'%s' already exists. No data was written.", file_path)

        elif choice == "7":
            # Exit the program
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
