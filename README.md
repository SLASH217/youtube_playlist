# YouTube Playlist Manager

## Overview

The YouTube Playlist Manager is a Python-based project designed to help users efficiently manage their YouTube playlists. It offers features like collecting song names and singer names, categorizing songs, identifying the most and least played tracks, automating the addition of new releases, and removing songs that have never been played. The project is built with a modular approach, allowing easy integration of additional features.

## Features

- **Playlist Management**: Collect and store song names, singer names, and play counts from your YouTube playlists.
- **Categorization**: Organize songs by genre, singer, or custom categories.
- **Analytics**: Identify the top 10 most and least played songs in your playlist.
- **Automation**: Automatically add new song releases to your playlist by scraping relevant websites.
- **Cleanup**: Remove songs that have never been played from your playlist.
- **Visualization**: Generate graphical reports for playlist analytics.
- **Integration**: Optionally, integrate with external APIs for currency conversion or other utilities.

## Installation

### Prerequisites

- Python 3.7 or higher
- A Google Cloud project with YouTube Data API v3 enabled
- Virtual environment setup (optional but recommended)

### Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/youtube_playlist_manager.git
    cd youtube_playlist_manager
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your YouTube Data API credentials:
    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    - Create a new project and enable the YouTube Data API v3.
    - Get your API key and add it to your project.

## Usage

### Main Script

The main functionality is implemented in `project.py`. Run the script as follows:

```bash
python project.py
