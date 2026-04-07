"""
ingest.py - run locally to pull recent Spotify plays into MySQL.
Requires XAMPP MySQL running and .env credentials set.
Does not run on Render.
"""

import os
import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'SPOTIPY_DB')
    )


def setup_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id      VARCHAR(50)  PRIMARY KEY,
            display_name VARCHAR(100),
            refresh_token TEXT        NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            track_id    VARCHAR(50)  PRIMARY KEY,
            track_name  VARCHAR(200) NOT NULL,
            artist_name VARCHAR(200) NOT NULL,
            album_name  VARCHAR(200),
            duration_ms INT,
            genre       VARCHAR(100)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plays (
            play_id   INT AUTO_INCREMENT PRIMARY KEY,
            user_id   VARCHAR(50) NOT NULL,
            track_id  VARCHAR(50) NOT NULL,
            played_at DATETIME    NOT NULL,
            UNIQUE KEY unique_play (user_id, played_at),
            FOREIGN KEY (user_id)  REFERENCES users(user_id),
            FOREIGN KEY (track_id) REFERENCES tracks(track_id)
        )
    """)


def ingest():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.environ.get('SPOTIPY_CLIENT_ID'),
        client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET'),
        redirect_uri='http://localhost:5000/callback',
        scope='user-read-recently-played user-read-private'
    ))

    user_info = sp.current_user()
    user_id = user_info['id']
    display_name = user_info.get('display_name', user_id)

    results = sp.current_user_recently_played(limit=50)
    items = results.get('items', [])

    conn = get_db_connection()
    cursor = conn.cursor()
    setup_tables(cursor)

    cursor.execute(
        "INSERT INTO users (user_id, display_name, refresh_token) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE display_name = VALUES(display_name)",
        (user_id, display_name, 'placeholder')
    )

    inserted = 0
    skipped = 0

    for item in items:
        track = item['track']
        played_at = item['played_at']
        track_id = track['id']

        cursor.execute(
            "INSERT IGNORE INTO tracks (track_id, track_name, artist_name, album_name, duration_ms, genre) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (track_id, track['name'], track['artists'][0]['name'],
             track['album']['name'], track['duration_ms'], '')
        )

        try:
            cursor.execute(
                "INSERT IGNORE INTO plays (user_id, track_id, played_at) VALUES (%s, %s, %s)",
                (user_id, track_id, played_at)
            )
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except mysql.connector.Error as e:
            print(f'Warning: could not insert play for {track["name"]}: {e}')

    conn.commit()
    cursor.close()
    conn.close()
    print(f'Done. Inserted: {inserted}  Skipped: {skipped}')


if __name__ == '__main__':
    ingest()
