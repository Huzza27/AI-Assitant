import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyController:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                            client_secret=client_secret,
                                                            redirect_uri=redirect_uri,
                                                            scope="user-modify-playback-state user-read-playback-state"))

    def play_song(self, song_name):
        """ Play a song on Spotify based on the song name. """
        results = self.sp.search(q=song_name, limit=1, type='track')
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            self.sp.start_playback(uris=[track_uri])
            print(f"Playing: {song_name}")
        else:
            print("Song not found.")

    def pause_song(self):
        """ Pause playback. """
        self.sp.pause_playback()

