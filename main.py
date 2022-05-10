import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import pandas as pd


def data_scraping():
    credentials = json.load(open('Authorization.json'))
    # own client id and client secret on the Spotify developers account
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    uri = "spotify:user:Test_1:playlist:5yTsPeUbnUdqTAagIXoHun"  # the URI is split by ':' to get the username and playlist ID
    username = uri.split(':')[2]
    playlist_id = uri.split(':')[4]

    results = sp.user_playlist_tracks(username, playlist_id)

    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    results = tracks

    for i in range(len(results)):
        print(i)  # counter
        if i == 0:
            playlist_tracks_id = results[i]['track']['id']
            playlist_tracks_titles = results[i]['track']['name']
            playlist_tracks_first_release_date = results[i]['track']['album']['release_date']
            playlist_tracks_popularity = results[i]['track']['popularity']

            artist_list = []
            for artist in results[i]['track']['artists']:
                artist_list = artist['name']
            playlist_tracks_artists = artist_list

            features = sp.audio_features(playlist_tracks_id)
            features_df = pd.DataFrame(data=features, columns=features[0].keys())
            features_df['title'] = playlist_tracks_titles
            features_df['all_artists'] = playlist_tracks_artists
            features_df['popularity'] = playlist_tracks_popularity
            features_df = features_df[['title', 'all_artists', 'popularity']]
            continue
        else:
            try:
                playlist_tracks_titles = results[i]['track']['name']
                playlist_tracks_popularity = results[i]['track']['popularity']
                artist_list = []
                for artist in results[i]['track']['artists']:
                    artist_list = artist['name']
                playlist_tracks_artists = artist_list
                new_row = {'title': [playlist_tracks_titles],
                           'all_artists': [playlist_tracks_artists],
                           'popularity': [playlist_tracks_popularity],
                           }

                dfs = [features_df, pd.DataFrame(new_row)]
                features_df = pd.concat(dfs, ignore_index=True)
            except:
                continue

    return features_df


if __name__ == '__main__':
    music_data = data_scraping()
    music_data.to_csv("csv_" + str("song_views") + ".csv", encoding='utf-8', index="false")
