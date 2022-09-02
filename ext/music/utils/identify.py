from enum import Enum


class Sites(Enum):
    Spotify = "Spotify"
    Spotify_Playlist = "Spotify Playlist"
    YouTube = "YouTube"
    Twitter = "Twitter"
    SoundCloud = "SoundCloud"
    Bandcamp = "Bandcamp"
    Custom = "Custom"
    Unknown = "Unknown"


class PlaylistTypes(Enum):
    Spotify_Playlist = "Spotify Playlist"
    YouTube_Playlist = "YouTube Playlist"
    BandCamp_Playlist = "BandCamp Playlist"
    Unknown = "Unknown"


class Origins(Enum):
    Default = "Default"
    Playlist = "Playlist"


def identify_url(url: str) -> Sites:
    if url is None:
        return Sites.Unknown

    if "https://www.youtu" in url or "https://youtu.be" in url:
        return Sites.YouTube

    if "https://open.spotify.com/track" in url:
        return Sites.Spotify

    if "https://open.spotify.com/playlist" in url or "https://open.spotify.com/album" in url:
        return Sites.Spotify_Playlist

    if "bandcamp.com/track/" in url:
        return Sites.Bandcamp

    if "https://twitter.com/" in url:
        return Sites.Twitter

    if url.lower().endswith((".webm", ".mp4", ".mp3", ".avi", ".wav", ".m4v", ".ogg", ".mov")):
        return Sites.Custom

    if "soundcloud.com/" in url:
        return Sites.SoundCloud

    return Sites.Unknown


def identify_playlist(url: str) -> Sites | PlaylistTypes:
    if url is None:
        return Sites.Unknown

    if "playlist?list=" in url:
        return PlaylistTypes.YouTube_Playlist

    if "https://open.spotify.com/playlist" in url or "https://open.spotify.com/album" in url:
        return PlaylistTypes.Spotify_Playlist

    if "bandcamp.com/album/" in url:
        return PlaylistTypes.BandCamp_Playlist

    return PlaylistTypes.Unknown
