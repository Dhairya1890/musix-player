import sqlite3
import os


db_path = os.path.expanduser("~/.musix/musix.db")

def get_connection():
    '''Get a connection'''

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def init_db():

    with get_connection() as conn:
        conn.execute("""
CREATE TABLE IF NOT EXIST playlist(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                     """)
        
        conn.execute("""

                     """)
