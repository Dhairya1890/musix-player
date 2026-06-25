import sqlite3
import pytest
from unittest.mock import patch


def _make_test_connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute('''
        CREATE TABLE playlist(
            PlayID INTEGER PRIMARY KEY,
            PlaylistName VARCHAR(100) UNIQUE
        )
    ''')
    con.execute('''
        CREATE TABLE songs(
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
        CREATE TABLE history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_name TEXT NOT NULL,
            youtube_id TEXT,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    con.commit()
    return con


@pytest.fixture
def db():
    con = _make_test_connection()
    import musix.db as _db
    with patch.object(_db, 'con', con):
        yield _db
    con.close()


# --- playlist CRUD ---

def test_create_and_check_playlist(db):
    assert not db.check_playlist("rock")
    db.create_playlist("rock")
    assert db.check_playlist("rock")


def test_list_playlists(db):
    db.create_playlist("rock")
    db.create_playlist("jazz")
    assert set(db.list_playlists()) == {"rock", "jazz"}


def test_list_playlists_empty(db):
    assert db.list_playlists() == []


def test_delete_playlist_returns_true(db):
    db.create_playlist("pop")
    assert db.delete_playlist("pop") is True
    assert not db.check_playlist("pop")


def test_delete_nonexistent_playlist(db):
    assert db.delete_playlist("ghost") is False


def test_delete_playlist_cascades_songs(db):
    db.create_playlist("chill")
    db.add_song_to_playlist("Song A", "chill", "yt123", 180, "Artist X")
    db.delete_playlist("chill")
    rows = db.con.execute("SELECT * FROM songs WHERE SongID = 'yt123'").fetchall()
    assert rows == []


# --- songs ---

def test_add_and_get_playlist_songs(db):
    db.create_playlist("workout")
    db.add_song_to_playlist("Pump It", "workout", "yt789", 240, "BEP")
    songs = db.get_playlist_songs("workout")
    assert len(songs) == 1
    assert songs[0][1] == "Pump It"


def test_add_duplicate_song_is_ignored(db):
    db.create_playlist("lofi")
    db.add_song_to_playlist("Chill Beat", "lofi", "yt456", 200, "LoFi Artist")
    db.add_song_to_playlist("Chill Beat", "lofi", "yt456", 200, "LoFi Artist")
    rows = db.con.execute("SELECT * FROM songs WHERE SongID = 'yt456'").fetchall()
    assert len(rows) == 1


def test_get_songs_from_nonexistent_playlist(db):
    assert db.get_playlist_songs("nope") == []


# --- history ---

def test_log_and_get_history(db):
    db.log_play("Shape of You", "yt001")
    db.log_play("Blinding Lights", "yt002")
    entries = db.get_history()
    assert len(entries) == 2
    assert entries[0][0] == "Blinding Lights"  # most recent first


def test_history_respects_limit(db):
    for i in range(10):
        db.log_play(f"Song {i}", f"yt{i:03d}")
    assert len(db.get_history(limit=5)) == 5


def test_history_empty(db):
    assert db.get_history() == []
