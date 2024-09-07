import csv
from collections import Counter
import matplotlib.pyplot as plt

# Read CSV file and collect artists
artists = []
with open("cleaned_playlist_data.csv", "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    artist_index = header.index("Artist")

    for row in reader:
        artists.append(row[artist_index])

# Count artist frequencies
artist_counts = Counter(artists)
top_artists = artist_counts.most_common(20)  # Top 20 most common artists

# Split the data into two lists for plotting
artist_names, counts = zip(*top_artists)

# Create bar graph
plt.figure(figsize=(10, 6))  # Adjust the size of the figure
plt.barh(artist_names, counts, color="skyblue")
plt.xlabel("Number of Songs")
plt.ylabel("Artists")
plt.title("Top 20 Most Common Artists in Playlist")
plt.gca().invert_yaxis()  # Invert y-axis to have the most common artist on top
plt.tight_layout()
plt.show()
