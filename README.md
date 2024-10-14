YouTube Playlist Manager Project
Video Demo URL: [Watch the Demo](https://youtu.be/9HF1nr_0zw0)

Project Overview
The YouTube Playlist Manager project automates and manages a YouTube playlist by fetching video statistics, cleaning data, managing new song releases, and identifying top artists. It integrates various components and services to provide a seamless playlist management experience with efficient data handling and visualization.

Main Components
1. YouTube API Manager (authenticate.py)
Handles authentication and interaction with the YouTube Data API v3.

Features
OAuth 2.0 Authentication: Manages user authentication and token storage.
Token Management: Refreshes expired tokens automatically.
YouTube API Integration: Sets up the YouTube Data API client for further interactions.
Prerequisites
Python 3.x
Libraries: google-auth, google-auth-oauthlib, google-api-python-client, python-dotenv
Environment Variables: Store paths to credentials and token files in a .env file.
Setup
Google API Credentials: Set up in Google API Console, enable YouTube Data API v3, create OAuth 2.0 credentials, and download credentials.json.
Token Management: The script generates token.json for future interactions.
Key Class: YouTubeAPIManager
Initialization: __init__(self, credentials_file, token_file, scopes)
Authentication: authenticate(self)
Private Method: _run_auth_flow(self)
2. Automate New Songs (new_releases.py)
Automates the addition of new songs from a source YouTube playlist to a personal playlist.

Features
Authenticate YouTube API
Fetch Playlist Items
Identify and Add New Songs
Error Handling & Logging
Prerequisites
Python 3.x
Library: google-api-python-client
Script Breakdown
Class: AutomateNew (inherits from YouTubeAPIManager)
Methods: get_playlist_items(playlist_id), add_song_to_playlist(playlist_id, video_id), add_new_songs(from_playlist_id, to_playlist_id, number_of_songs_to_add)
3. Playlist Manager (manager.py)
Manages playlist data by retrieving videos, parsing titles, and saving to CSV.

Features
Retrieve Playlist Videos
Parse Video Titles
Save Data to CSV
Prerequisites
Python 3.x
Libraries: pandas
Script Breakdown
Class: PlaylistManager (inherits from YouTubeAPIManager)
Methods: __init__(), get_playlist_items(playlist_id), parse_video_title(title)
Example Usage
Replace Playlist ID: Update PLAYLIST_ID in main().
Run the Script: python playlist_manager.py
4. YouTube Playlist Manager (Video_stats.py)
Handles fetching video statistics, saving to CSV, and visualizing data.

Features
Fetch Playlist Videos
Fetch Video Statistics
Save to CSV
Visualize Data
Method Breakdown
get_playlist_videos(playlist_id)
get_video_statistics(video_id)
collect_playlist_statistics(playlist_id, output_csv)
visualize_statistics(df)
5. Data Cleaning and Visualization
Data Cleaning: Removes unwanted text and ensures uniform formatting in CSV files.

Top Artists Visualization: Identifies and visualizes the most common artists from the playlist data.

Main Program Flow (main.py)
Integrates functionalities to:

Clean Playlist Statistics and Data
Plot Top Common Artists
Fetch New Songs
Fetch Video Statistics
Fetch Song Data
Configuration
PLAYLIST_ID: ID of the playlist to manage.
FROM_PLAYLIST_ID: ID of the source playlist for new songs.
STATS_OUTPUT_CSV: Output file for video statistics.
NUMBER_OF_SONGS_TO_ADD: Limit for new songs to be added.
Logging
Tracks operations and errors to assist in debugging.
"/YouTubePlaylistManager
│
├──Video_stats.py # YouTube playlist statistics handling logic
├── manager.py # General playlist management and parsing logic
├── new_releases.py # Automated fetching and addition of new songs
├── playlist_data.csv # Playlist song data (generated if not present)
├── playlist_stats.csv # Playlist video statistics data (generated if not present)
├── cleaned_playlist_data.csv # Cleaned playlist data file
├── clean_playlist_stats.csv # Cleaned playlist statistics data file
├── README.md # Project documentation (this file)
└── project.py # Main script integrating all functionalities
"
Running the Program
Execute: python project.py
Follow Prompts: Use the console menu to select operations.
Requirements
The project requires the following Python libraries:

pandas: For handling CSV files and DataFrame operations.
matplotlib: For visualizing data through graphs.
logging: For logging information, warnings, and errors during execution.
re: For text cleaning using regular expressions.
csv: For reading from and writing to CSV files.
os: For checking file existence.
collections.Counter: For counting occurrences of elements (e.g., artists).
Ensure that these libraries are installed before running the project.
Dependencies Installation:
pip install google-auth google-auth-oauthlib google-api-python-client python-dotenv pandas matplotlib
or
pip install -r requirements.txt


Unit Test Description
This unit test file validates key functionalities of the YouTube Playlist Manager project:

test_clean_stats: Verifies that playlist statistics are cleaned and written to a CSV file.
test_clean_playlist_data: Ensures playlist data is cleaned and saved to a new CSV file.
test_common_artists: Checks if common artists in the playlist are correctly identified and counted.
test_parse_video_title: Confirms the parsing of video titles to extract artist and song names.
test_automate_new_add_songs: Simulates adding new songs to playlists.
test_youtube_playlist_statistics: Tests the collection of playlist statistics into a DataFrame.
Mocking is used to simulate file operations and method behavior.
