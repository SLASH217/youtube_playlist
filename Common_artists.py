import csv
from collections import Counter

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
print(artist_counts.most_common(10))  # Print 10 most common artists
