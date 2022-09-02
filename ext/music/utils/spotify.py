import re

import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

from constants import config

sp_api = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=config.spotify.id,
        client_secret=config.spotify.secret
    )
)

url_regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


async def convert_spotify(url, session):
    if re.search(url_regex, url):
        result = url_regex.search(url)

        if "?si=" in url:
            url = result.group(0) + "&nd=1"

    async with session.get(url) as response:
        page = await response.text()
        soup = BeautifulSoup(page, 'html.parser')

        title = soup.find('title')
        title = title.string
        title = title.replace('- song by', '')
        title = title.replace('| Spotify', '')

        return title


async def get_spotify_playlist(url, session):
    """Return Spotify_Playlist class"""

    code = url.split('/')[4].split('?')[0]

    if "open.spotify.com/album" in url:
        try:
            results = sp_api.album_tracks(code)
            tracks = results['items']

            while results['next']:
                results = sp_api.next(results)
                tracks.extend(results['items'])

            links = []

            for track in tracks:
                try:
                    links.append(track['external_urls']['spotify'])
                except:
                    pass
            return links
        except:
            if config.spotify.id != "" or config.spotify.secret != "":
                print("ERROR: Check spotify CLIENT_ID and SECRET")

    if "open.spotify.com/playlist" in url:
        results = sp_api.playlist_items(code)
        tracks = results['items']
        while results['next']:
            results = sp_api.next(results)
            tracks.extend(results['items'])

        links = []

        for track in tracks:
            try:
                links.append(
                    track['track']['external_urls']['spotify'])
            except:
                pass
        return links

    async with session.get(url + "&nd=1") as response:
        page = await response.text()

    soup = BeautifulSoup(page, 'html.parser')
    results = soup.find_all(property="music:song", attrs={"content": True})
    links = [item['content'] for item in results]

    return links
