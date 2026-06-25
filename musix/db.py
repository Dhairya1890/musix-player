import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parent / "musix.db"
con = sqlite3.connect(_DB_PATH)

con.execute('''
    CREATE TABLE IF NOT EXISTS playlist(
        PlayID INTEGER PRIMARY KEY,
        PlaylistName VARCHAR(100) UNIQUE
    )
''')

con.execute('''
    CREATE TABLE IF NOT EXISTS songs(
        SongID VARCHAR(20) PRIMARY KEY,
        SongName VARCHAR(100),
        SongPlayTime INT,
        SongArtist VARCHAR(100),
        SongOrder INT,
        PlayID INT,
        FOREIGN KEY (PlayID) REFERENCES playlist(PlayID)
    )
''')

con.execute('''
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_name TEXT NOT NULL,
        youtube_id TEXT,
        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

con.commit()


def list_playlists() -> list[str]:
    rows = con.execute('SELECT PlaylistName FROM playlist').fetchall()
    return [row[0] for row in rows]


def check_playlist(name: str) -> bool:
    exists = con.execute(
        "SELECT EXISTS(SELECT 1 FROM playlist WHERE PlaylistName = (?))", (name,)
    ).fetchone()
    return bool(exists[0])


def create_playlist(name: str):
    con.execute('INSERT INTO playlist (PlaylistName) VALUES (?)', (name,))
    con.commit()


def delete_playlist(name: str) -> bool:
    play_id = con.execute(
        "SELECT PlayID FROM playlist WHERE PlaylistName = (?)", (name,)
    ).fetchone()
    if not play_id:
        return False
    con.execute("DELETE FROM songs WHERE PlayID = (?)", (play_id[0],))
    con.execute("DELETE FROM playlist WHERE PlayID = (?)", (play_id[0],))
    con.commit()
    return True


def add_song_to_playlist(name: str, playlist: str, song_id: str, song_duration: int, song_channel: str):
    play_id = con.execute(
        "SELECT PlayID FROM playlist WHERE PlaylistName = (?)", (playlist,)
    ).fetchone()
    if not play_id:
        return
    try:
        con.execute(
            'INSERT INTO songs (SongID, SongName, SongPlayTime, SongArtist, PlayID) VALUES (?,?,?,?,?)',
            (song_id, name, song_duration, song_channel, play_id[0])
        )
        con.commit()
        print(f"\nSong added to '{playlist}' successfully!")
    except sqlite3.IntegrityError:
        print(f"\n'{name}' is already in '{playlist}'!")


def get_playlist_songs(playlist: str) -> list[tuple]:
    play_id = con.execute(
        "SELECT PlayID FROM playlist WHERE PlaylistName = (?)", (playlist,)
    ).fetchone()
    if not play_id:
        return []
    return con.execute(
        "SELECT SongID, SongName FROM songs WHERE PlayID = (?)", (play_id[0],)
    ).fetchall()


def log_play(song_name: str, youtube_id: str = None):
    con.execute(
        'INSERT INTO history (song_name, youtube_id) VALUES (?, ?)',
        (song_name, youtube_id)
    )
    con.commit()


def get_history(limit: int = 20) -> list[tuple]:
    return con.execute(
        'SELECT song_name, youtube_id, played_at FROM history ORDER BY id DESC LIMIT ?',
        (limit,)
    ).fetchall()
