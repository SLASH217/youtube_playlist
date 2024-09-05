import csv
import re

def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove text within brackets and the brackets themselves
    text = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}', '', text)
    # Remove specific words irrespective of case
    words_to_remove = ["official", "music", "video", "lyrics"]
    text = re.sub(r'\b(?:' + '|'.join(words_to_remove) + r')\b', '', text, flags=re.IGNORECASE)
    # Remove extra spaces
    text = ' '.join(text.split())
    return text

# Open input and output CSV files
with open("playlist_data.csv", "r", newline="", encoding="utf-8") as input_file, \
     open("cleaned_playlist_data.csv", "w", newline="", encoding="utf-8") as output_file:
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)

    # Write the header
    header = next(reader)
    writer.writerow(header)

    # Process each row
    for row in reader:
        cleaned_row = [clean_text(cell) for cell in row]
        writer.writerow(cleaned_row)

print("Data cleaning complete. Cleaned data saved to 'cleaned_playlist_data.csv'.")
