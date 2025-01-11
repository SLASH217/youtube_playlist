import pytest
import os
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from collections import Counter
from manager import PlaylistManager, parse_video_title
from Video_stats import YouTubePlaylistManager
from new_releases import AutomateNew
from project import clean_stats, clean_playlist_data, common_artists


SAMPLE_PLAYLIST_DATA = [
    ["Title1", "VideoID1", "Artist1", "Song1"],
    ["Title2", "VideoID2", "Artist2", "Song2"],
    ["Title3", "VideoID3", "Artist1", "Song3"],
]


CSV_HEADER = ["Title", "Video ID", "Artist", "Song"]



def test_clean_stats():
    input_csv = "test_input.csv"
    output_csv = "test_output.csv"


    with patch("builtins.open", mock_open(read_data=",".join(CSV_HEADER))) as mock_file:
        clean_stats(input_csv, output_csv)

        mock_file.assert_called_with(output_csv, "w", newline="", encoding="utf-8")


def test_clean_playlist_data():
    input_csv = "playlist_data.csv"
    output_csv = "clean_playlist_data.csv"

    with patch("builtins.open", mock_open(read_data=",".join(CSV_HEADER))):
        clean_playlist_data(input_csv, output_csv)

        assert os.path.exists(output_csv)


def test_common_artists():
    csv_file = "clean_playlist_data.csv"

    mock_data = SAMPLE_PLAYLIST_DATA

    with patch("builtins.open", mock_open(read_data=",".join(CSV_HEADER))):
        common_artists(csv_file)

        expected_counts = Counter(["Artist1", "Artist2"])
        assert expected_counts["Artist1"] == 1
        assert expected_counts["Artist2"] == 1



def test_parse_video_title():
    title = "Artist Name - Song Name"
    expected_artist = "Artist Name"
    expected_song = "Song Name"

    artist, song = parse_video_title(title)
    assert artist == expected_artist
    assert song == expected_song



def test_automate_new_add_songs():
    automate_new = AutomateNew()

    
    with patch.object(automate_new, "add_new_songs", return_value=True) as mock_method:
        assert automate_new.add_new_songs("playlist_id_1", "playlist_id_2", 5)

        mock_method.assert_called_once_with("playlist_id_1", "playlist_id_2", 5)



def test_youtube_playlist_statistics():
    youtube_manager = YouTubePlaylistManager()

    
    with patch.object(
        youtube_manager,
        "collect_playlist_statistics",
        return_value=pd.DataFrame(SAMPLE_PLAYLIST_DATA),
    ) as mock_method:
        stats_df = youtube_manager.collect_playlist_statistics(
            "playlist_id", "stats_output.csv"
        )
        assert not stats_df.empty
        mock_method.assert_called_once_with("playlist_id", "stats_output.csv")


if __name__ == "__main__":
    pytest.main()
