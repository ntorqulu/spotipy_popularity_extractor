import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import pandas as pd

# fetch the csv file
df_csv = pd.read_csv('/Users/ntorqulu/PycharmProjects/pythonProject/assets/MSD_SMOL.csv')
# convert csv col author and title to dict
author_csv = {"artist": df_csv['artist_name'].tolist()}
title_csv = {"title": df_csv['title'].tolist()}
# merge dicts
songs_name_author = {**title_csv, **author_csv}
# print(songs_name_author)

# open spotify account connection
scope = "playlist-modify-public"
username = "po0oxtt4gt6miz8qqxl641c8k"
token = SpotifyOAuth(scope=scope, username=username)
spotifyObject = spotipy.Spotify(auth_manager=token)

# create the playlist
playlist_name = input("Enter a playlist name: ")
playlist_description = input("Enter a playlist description: ")

# create empty playlist
spotifyObject.user_playlist_create(user=username, name=playlist_name, public=True, description=playlist_description)

list_of_songs = []
# for each title in the csv col title
for i in range(len(songs_name_author["title"])):
    # reset the values
    max_value = 0
    curr_value = 0
    step = 0
    enter = 1
    # search a matching track in spotify, fetch only first five results
    results = spotifyObject.search(q=f"{songs_name_author['title'][i]} {songs_name_author['artist'][i]}", limit=5,
                                   type='track')  # get 5 responses since first isn't always accurate
    # if there aren't coincidences
    if results['tracks']['total'] == 0:  # if track isn't on spotify as queried
        # search for the title, assume similar music taste...
        results = spotifyObject.search(q=f"{songs_name_author['title'][i]}", limit=5, type='track')
        # if there isn't any matching title
        if results['tracks']['total'] == 0:
            # search for the author, assume similar music taste...
            results = spotifyObject.search(q=f"{songs_name_author['artist'][i]}", limit=5, type='track')
            if results['tracks']['total'] == 0:
                enter = 0
                print("NOT FOUND: " + songs_name_author['title'][i] + songs_name_author['artist'][i])
                # exit if no coincidences

    # check again results after the if-nested-conditions
    if enter:
        # for each query returned from spotify, study max 5 possible matching tracks
        for j in range(len(results['tracks']['items'])):
            # if the substrings are similar ( > 90 )
            if fuzz.partial_ratio(results['tracks']['items'][j]['name'], songs_name_author['title'][i]) > 90\
                    and fuzz.partial_ratio(results['tracks']['items'][j]['artists'][0]['name'], songs_name_author['artist'][i]) > 90:  # get
                # right response by matching on artist and title
                # we keep this track!
                list_of_songs.append(results['tracks']['items'][j]['id'])  # append track id
                curr_value = -1
                break  # don't want repeats of a sample ex: different versions
            else:
                # if the titles aren't matching, keep the similarity number
                curr_value = fuzz.partial_ratio(results['tracks']['items'][j]['artists'][0]['name'],
                                                songs_name_author['artist'][i]) \
                             + fuzz.partial_ratio(results['tracks']['items'][j]['name'], songs_name_author['title'][i])
                # and make it the biggest possible from the five tracks
                if curr_value > max_value:
                    max_value = curr_value
                    step = j  # and keep this track!
        if curr_value != -1:
            # if the title isn't matching we keep the track with the highest score
            list_of_songs.append(results['tracks']['items'][step]['id'])  # append track id

prePlaylist = spotifyObject.user_playlists(user=username)
playlist = prePlaylist["items"][0]["id"]

# append the songs to the playlist
while list_of_songs:
    spotifyObject.user_playlist_add_tracks(username, playlist, list_of_songs[:100], position=None)
    list_of_songs = list_of_songs[100:]
