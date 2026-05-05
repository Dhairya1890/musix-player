import sqlite3

con = sqlite3.connect("musix.db")

cur = con.cursor()

cur.execute('''
            CREATE TABLE IF NOT EXISTS playlist(
            PlayID INTEGER PRIMARY KEY,
            PlaylistName varchar(100)
            )''')

con.commit()

cur.execute('''

            CREATE TABLE IF NOT EXISTS songs(
            SongID INT PRIMARY KEY,
            SongName VARCHAR(100),
            SongPlayTime INT,
            SongArtist VARCHAR(100),
            SongOrder INT,
            PlayID INT,
            FOREIGN KEY (PlayID) REFERENCES playlist(PlayID)
            )    ''')

con.commit()

def CheckPlaylist(playlist) -> bool:
    '''CHECKS FOR PLAYLIST NAME IN DATABASE, RETURNS BOOLEAN'''
    exists = cur.execute("SELECT EXISTS(SELECT 1 FROM playlist where PlaylistName = (?))", (playlist,),).fetchone()
    return (bool(exists[0]))


def CreatePlaylist(playlist : str):
    con.execute('''INSERT INTO playlist (PlaylistName) VALUES (?)''', (playlist,))
    con.commit()
    return True

def addSongToPlaylist(name : str, playlist : str, song_id : str, song_duration : int, song_channel : str):

    PlayID = cur.execute("SELECT PlayID from playlist WHERE PlaylistName = (?)", (playlist,)).fetchone()
    if PlayID:
        try :
            cur.execute('''
                        INSERT INTO songs (SongID, SongName, SongPlayTime, SongArtist, PlayID) VALUES (?,?,?,?,?)
                        ''', (song_id, name, song_duration, song_channel, PlayID[0]))
        except sqlite3.IntegrityError as e:
            print()
            print(f"{name} is already added in {playlist}!")
        else :
            print()
            print(f"Song added successfully!")
        con.commit()

def DeletePlaylist(playlist : str):
    res = con.execute('''DELETE FROM playlist WHERE PlaylistName = (?)''', (playlist,))
    con.commit()

    return res.rowcount > 0

def testing(playlist : str):
    playID = con.execute("SELECT PlayID from playlist WHERE PlaylistName = (?)", (playlist,)).fetchone()
    #res = con.execute("SELECT SongName from songs WHERE PlayID = (?)", (playid,)).fetchall()
    res = con.execute("SELECT SongName from songs WHERE PlayID = (?)", (playID[0],)).fetchall()
    for i in res:
       print(i)

if __name__ == "__main__":
    testing("test01")