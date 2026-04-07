"""
export_csv.py - exports MySQL data to listening_data.csv for deployment.
Run locally after ingest.py. Commit the CSV to git and push to update Render.
"""

import os
import csv
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'SPOTIPY_DB')
    )


def export():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.user_id, t.track_id, t.track_name, t.artist_name,
               t.album_name, t.duration_ms, t.genre, p.played_at
        FROM plays p
        JOIN tracks t ON p.track_id = t.track_id
        ORDER BY p.played_at ASC
    """)

    rows = cursor.fetchall()

    if not rows:
        print('No data found.')
        cursor.close()
        conn.close()
        return

    output_path = os.path.join(os.path.dirname(__file__), 'listening_data.csv')

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['user_id', 'track_id', 'track_name', 'artist_name',
                      'album_name', 'duration_ms', 'genre', 'played_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if hasattr(row['played_at'], 'strftime'):
                row['played_at'] = row['played_at'].strftime('%Y-%m-%dT%H:%M:%SZ')
            writer.writerow(row)

    cursor.close()
    conn.close()
    print(f'Exported {len(rows)} rows to {output_path}')


if __name__ == '__main__':
    export()
