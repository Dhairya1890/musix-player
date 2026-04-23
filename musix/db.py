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


def DeletePlaylist(playlist : str):
    res = con.execute('''DELETE FROM playlist WHERE PlaylistName = (?)''', (playlist,))
    con.commit()

    return res.rowcount > 0

if __name__ == "__main__":
    CheckPlaylist()
    CreatePlaylist()