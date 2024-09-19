# Prerequisites:
# Spotify Web API credentials
# pip3 install spotipy --break-system-packages
# brew install python-tk

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
import os
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

# Spotify credentials
client_id = input("Enter your Spotify Client ID: ")
client_secret = input("Enter your Spotify Client Secret: ")
redirect_uri = 'http://localhost:8888/callback'

# Set the scope to access playlists
scope = 'playlist-read-private'

# Spotify OAuth object
connection = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                               client_secret=client_secret, 
                                               redirect_uri=redirect_uri, 
                                               scope=scope))

def get_playlists(connection):
    playlists = []
    results = connection.current_user_playlists(limit=50)  # Adjust limit if needed
    playlists.extend(results['items'])
    # Loop to get all playlists if there are more than the limit
    while results['next']:
        results = connection.next(results)
        playlists.extend(results['items'])
    return playlists

def get_playlist_tracks(connection, playlist_id):
    tracks = []
    results = connection.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    # Loop to get all tracks if there are more than the limit
    while results['next']:
        results = connection.next(results)
        tracks.extend(results['items'])
    return tracks

def save_to_csv(playlists, file_path):
    unique_tracks = set()  # A set to store unique tracks (name, artist, year combination)

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Playlist', 'Track Number', 'Track Name', 'Artists', 'Release Year'])

        for playlist in playlists:
            tracks = get_playlist_tracks(connection, playlist['id'])
            for idx, track in enumerate(tracks):
                track_info = track['track']
                artist_names = ', '.join([artist['name'] for artist in track_info['artists']])
                
                # Extract the release date (year) from the album information
                release_date = track_info['album']['release_date']
                release_year = release_date.split('-')[0]  # Get only the year part of the date

                track_tuple = (track_info['name'], artist_names, release_year)

                # Only write to CSV if this track combination is unique
                if track_tuple not in unique_tracks:
                    unique_tracks.add(track_tuple)
                    writer.writerow([playlist['name'], idx + 1, track_info['name'], artist_names, release_year])


# Main function to run the script
if __name__ == '__main__':
    playlists = get_playlists(connection)

    # Open a file dialog to ask the user where to save the file
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = asksaveasfilename(defaultextension='.csv', filetypes=[("CSV files", "*.csv")], title="Save CSV File")

    # If the user cancels the dialog, the file_path will be an empty string, so handle this case
    if file_path:
        # Save the playlists and tracks to CSV
        save_to_csv(playlists, file_path)
        print(f'Successfully saved to {file_path}')
    else:
        print("File save operation was cancelled.")