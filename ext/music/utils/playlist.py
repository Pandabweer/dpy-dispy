import random
from collections import deque

from constants import config
from ext.music.utils.song import Song


class Playlist:
    def __init__(self) -> None:
        self.playque = deque()
        self.playhistory = deque()
        self.trackname_history = deque()
        self.loop = False

    def __len__(self) -> int:
        return len(self.playque)

    def add(self, track: Song) -> None:
        self.playque.append(track)

    def add_name(self, trackname: str) -> None:
        self.trackname_history.append(trackname)
        if len(self.trackname_history) > config.music.max_trackname_history_lenght:
            self.trackname_history.popleft()

    def next(self, song_played) -> deque | None:
        if self.loop:
            self.playque.appendleft(self.playhistory[-1])

        if len(self.playque) == 0:
            return

        if song_played != "Dummy":
            if len(self.playhistory) > config.music.max_history_length:
                self.playhistory.popleft()

        return self.playque[0]

    def prev(self, current_song: Song) -> Song:
        if current_song is None:
            self.playque.appendleft(self.playhistory[-1])
            return self.playque[0]

        ind = self.playhistory.index(current_song)
        self.playque.appendleft(self.playhistory[ind - 1])
        if current_song is not None:
            self.playque.insert(1, current_song)

    def shuffle(self) -> None:
        random.shuffle(self.playque)

    def move(self, oldindex: int, newindex: int) -> None:
        temp = self.playque[oldindex]
        del self.playque[oldindex]
        self.playque.insert(newindex, temp)

    def empty(self) -> None:
        self.playque.clear()
        self.playhistory.clear()
