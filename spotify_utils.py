import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter


def authenticate_to_spotify(client_id, client_secret, redirect_uri, scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))
    return sp


def get_followed_artists(sp, limit=10):
    followed_artists = []
    cursor = None

    while True:
        results = sp.current_user_followed_artists(limit=limit, after=cursor)

        if not results:
            break

        followed_artists.extend(results['artists']['items'])

        if results['artists']['cursors']['after']:
            cursor = results['artists']['cursors']['after']
        else:
            break

    return followed_artists


def get_all_liked_tracks(sp, limit=50):
    liked_tracks = []
    offset = 0

    while True:
        results = sp.current_user_saved_tracks(offset=offset, limit=limit)
        liked_tracks.extend(results['items'])

        if len(results['items']) < limit:
            break
        offset += limit

    return liked_tracks


def get_current_user_top_artists(sp, limit=10, time_range='medium_term'):
    artists = sp.current_user_top_artists(limit=limit, time_range=time_range)
    top_artists = [artist['name'] for artist in artists['items']]

    return top_artists


def get_current_user_top_tracks(sp, limit=10, time_range='medium_term'):
    tracks = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    top_tracks = [(track['name'], ', '.join([artist['name'] for artist in track['artists']])) for track in tracks['items']]
    return top_tracks


def get_artists_sorted_by_liked_tracks(sp, limit=10):
    followed_artists = get_followed_artists(sp, limit)
    liked_tracks = get_all_liked_tracks(sp)

    artist_likes_count = Counter()
    for track in liked_tracks:
        artists = track['track']['artists']
        artist_names = [artist['name'] for artist in artists]
        artist_likes_count.update(artist_names)

    sorted_artists = sorted(
        followed_artists,
        key=lambda artist: artist_likes_count[artist['name']],
        reverse=True
    )
    artist_names = [artist['name'] for artist in sorted_artists]

    return artist_names


if __name__ == "__main__":
    load_dotenv()

    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    scope = "user-library-read user-read-playback-state user-follow-read user-library-read user-read-playback-state"

    sp_ = authenticate_to_spotify(client_id, client_secret, redirect_uri, scope)

    get_artists = get_followed_artists(sp=sp_, limit=10)
    print(len(get_artists))
    print(get_artists[0])

    liked_tracks = get_all_liked_tracks(sp=sp_)
    print(len(liked_tracks))
    print(liked_tracks[0])

    print(get_current_user_top_artists(sp_))
    print(get_current_user_top_tracks(sp_))