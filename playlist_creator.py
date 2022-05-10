import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import pandas as pd

df_csv = pd.read_csv('/Users/ntorqulu/PycharmProjects/spotifyApp/assets/MSD_SMOL.csv')
author_csv = {"artist": df_csv['artist_name'].tolist()}
title_csv = {"title": df_csv['title'].tolist()}
songs_name_author = {**title_csv, **author_csv}
print(songs_name_author)

scope = "playlist-modify-public"
username = "po0oxtt4gt6miz8qqxl641c8k"
token = SpotifyOAuth(scope=scope, username=username)
spotifyObject = spotipy.Spotify(auth_manager=token)

# create the playlist
playlist_name = input("Enter a playlist name: ")
playlist_description = input("Enter a playlist description: ")

spotifyObject.user_playlist_create(user=username, name=playlist_name, public=True, description=playlist_description)

list_of_songs = []

for i in range(len(songs_name_author["title"])):
    results = spotifyObject.search(q=f"{songs_name_author['title'][i]} {songs_name_author['artist'][i]}")  # get 5 responses since first isn't always accurate
    if results['tracks']['total'] == 0:  # if track isn't on spotify as queried, go to next track
        print("NOT FOUND: " + songs_name_author['title'][i] + songs_name_author['artist'][i])
        continue
    else:
        for j in range(len(results['tracks']['items'])):
            if fuzz.partial_ratio(results['tracks']['items'][j]['artists'][0]['name'],
                                  songs_name_author['artist'][i]) > 50 and fuzz.partial_ratio(
                    results['tracks']['items'][j]['name'],
                    songs_name_author['title'][i]) > 50:  # get right response by matching on artist and title
                list_of_songs.append(results['tracks']['items'][j]['id'])  # append track id
                break  # don't want repeats of a sample ex: different versions
            else:
                print("NOT FOUND: " + songs_name_author['title'][i] + songs_name_author['artist'][i])
                continue
prePlaylist = spotifyObject.user_playlists(user=username)
playlist = prePlaylist["items"][0]["id"]

spotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlist, tracks=list_of_songs)