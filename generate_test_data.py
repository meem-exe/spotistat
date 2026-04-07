"""
generate_test_data.py
Generates ~1050 rows of test data based on real Spotify tracks.
Run once to produce listening_data.csv. Not part of the deployed app.
"""

import csv
import random
from datetime import datetime, timedelta
import os

REAL_TRACKS = [
    {'track_id': 'tr001', 'track_name': 'Espresso',             'artist_name': 'Sabrina Carpenter', 'album_name': 'Short n Sweet',           'duration_ms': 175459, 'genre': 'Pop'},
    {'track_id': 'tr002', 'track_name': 'Please Please Please', 'artist_name': 'Sabrina Carpenter', 'album_name': 'Short n Sweet',           'duration_ms': 186614, 'genre': 'Pop'},
    {'track_id': 'tr003', 'track_name': 'APT.',                 'artist_name': 'ROSÉ',              'album_name': 'rosie',                   'duration_ms': 170000, 'genre': 'K-Pop'},
    {'track_id': 'tr004', 'track_name': 'Die With A Smile',     'artist_name': 'Lady Gaga',         'album_name': 'Die With A Smile',        'duration_ms': 251333, 'genre': 'Pop'},
    {'track_id': 'tr005', 'track_name': 'Birds Of A Feather',   'artist_name': 'Billie Eilish',     'album_name': 'HIT ME HARD AND SOFT',    'duration_ms': 210000, 'genre': 'Indie Pop'},
    {'track_id': 'tr006', 'track_name': 'Good Luck, Babe!',     'artist_name': 'Chappell Roan',     'album_name': 'Good Luck, Babe!',        'duration_ms': 218000, 'genre': 'Pop'},
    {'track_id': 'tr007', 'track_name': 'Beautiful Things',     'artist_name': 'Benson Boone',      'album_name': 'Beautiful Things',        'duration_ms': 197000, 'genre': 'Pop Rock'},
    {'track_id': 'tr008', 'track_name': 'Harlequin',            'artist_name': 'Lady Gaga',         'album_name': 'Harlequin',               'duration_ms': 162000, 'genre': 'Pop'},
    {'track_id': 'tr009', 'track_name': 'Columbia',             'artist_name': 'Quavo',             'album_name': 'Rocket Power',            'duration_ms': 156000, 'genre': 'Hip-Hop'},
    {'track_id': 'tr010', 'track_name': 'TEXAS HOLD EM',        'artist_name': 'Beyonce',           'album_name': 'Cowboy Carter',           'duration_ms': 237000, 'genre': 'Country Pop'},
    {'track_id': 'tr011', 'track_name': 'Not Like Us',          'artist_name': 'Kendrick Lamar',    'album_name': 'Not Like Us',             'duration_ms': 274000, 'genre': 'Hip-Hop'},
    {'track_id': 'tr012', 'track_name': 'Lose Control',         'artist_name': 'Teddy Swims',       'album_name': 'I ve Tried Everything',   'duration_ms': 203000, 'genre': 'R&B'},
    {'track_id': 'tr013', 'track_name': 'Too Sweet',            'artist_name': 'Hozier',            'album_name': 'Too Sweet',               'duration_ms': 298000, 'genre': 'Indie Folk'},
    {'track_id': 'tr014', 'track_name': 'Lunch',                'artist_name': 'Billie Eilish',     'album_name': 'HIT ME HARD AND SOFT',    'duration_ms': 187000, 'genre': 'Indie Pop'},
    {'track_id': 'tr015', 'track_name': 'STARGAZING',           'artist_name': 'Myles Smith',       'album_name': 'STARGAZING',              'duration_ms': 205000, 'genre': 'Indie Pop'},
    {'track_id': 'tr016', 'track_name': 'One Of The Girls',     'artist_name': 'The Weeknd',        'album_name': 'One Of The Girls',        'duration_ms': 218000, 'genre': 'R&B'},
    {'track_id': 'tr017', 'track_name': 'Blinding Lights',      'artist_name': 'The Weeknd',        'album_name': 'After Hours',             'duration_ms': 200000, 'genre': 'Synth-Pop'},
    {'track_id': 'tr018', 'track_name': 'Cruel Summer',         'artist_name': 'Taylor Swift',      'album_name': 'Lover',                   'duration_ms': 178427, 'genre': 'Pop'},
    {'track_id': 'tr019', 'track_name': 'Shake It Off',         'artist_name': 'Taylor Swift',      'album_name': '1989',                    'duration_ms': 219200, 'genre': 'Pop'},
    {'track_id': 'tr020', 'track_name': 'Anti-Hero',            'artist_name': 'Taylor Swift',      'album_name': 'Midnights',               'duration_ms': 200698, 'genre': 'Pop'},
    {'track_id': 'tr021', 'track_name': 'Vampire',              'artist_name': 'Olivia Rodrigo',    'album_name': 'GUTS',                    'duration_ms': 218000, 'genre': 'Pop Rock'},
    {'track_id': 'tr022', 'track_name': 'bad idea right?',      'artist_name': 'Olivia Rodrigo',    'album_name': 'GUTS',                    'duration_ms': 175000, 'genre': 'Pop Rock'},
    {'track_id': 'tr023', 'track_name': 'Flowers',              'artist_name': 'Miley Cyrus',       'album_name': 'Endless Summer Vacation', 'duration_ms': 200455, 'genre': 'Pop'},
    {'track_id': 'tr024', 'track_name': 'As It Was',            'artist_name': 'Harry Styles',      'album_name': "Harry's House",           'duration_ms': 167303, 'genre': 'Indie Pop'},
    {'track_id': 'tr025', 'track_name': 'Watermelon Sugar',     'artist_name': 'Harry Styles',      'album_name': 'Fine Line',               'duration_ms': 174000, 'genre': 'Indie Pop'},
    {'track_id': 'tr026', 'track_name': 'Heat Waves',           'artist_name': 'Glass Animals',     'album_name': 'Dreamland',               'duration_ms': 238805, 'genre': 'Indie Pop'},
    {'track_id': 'tr027', 'track_name': 'Levitating',           'artist_name': 'Dua Lipa',          'album_name': 'Future Nostalgia',        'duration_ms': 203064, 'genre': 'Dance Pop'},
    {'track_id': 'tr028', 'track_name': 'Unholy',               'artist_name': 'Sam Smith',         'album_name': 'Gloria',                  'duration_ms': 156943, 'genre': 'Pop'},
    {'track_id': 'tr029', 'track_name': 'Ghost',                'artist_name': 'Justin Bieber',     'album_name': 'Justice',                 'duration_ms': 153496, 'genre': 'Pop'},
    {'track_id': 'tr030', 'track_name': 'Peaches',              'artist_name': 'Justin Bieber',     'album_name': 'Justice',                 'duration_ms': 197913, 'genre': 'R&B'},
]

USERS = ['user1', 'user2', 'user3']

USER_WEIGHTS = {
    'user1': [5,5,2,3,4,4,3,2,1,1,2,3,3,4,3,2,3,5,4,5,4,3,4,5,4,3,3,2,2,2],
    'user2': [3,2,5,2,3,3,4,3,4,3,5,4,3,3,2,4,3,2,2,2,3,3,2,3,2,4,4,3,4,5],
    'user3': [2,2,1,4,2,2,3,4,2,4,3,2,4,2,4,3,5,3,3,3,2,2,3,2,3,2,2,4,3,3],
}

HOUR_WEIGHTS = [1,1,1,1,1,1, 2,3,4,3,3,4, 5,4,4,5,6,7, 8,9,9,8,6,3]


def random_played_at(start_date, end_date):
    delta = end_date - start_date
    dt = start_date + timedelta(
        days=random.randint(0, delta.days),
        hours=random.choices(range(24), weights=HOUR_WEIGHTS)[0],
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def generate():
    random.seed(42)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    rows = []
    used_timestamps = set()

    for user in USERS:
        weights = USER_WEIGHTS[user]
        plays_for_user = 0
        attempts = 0

        while plays_for_user < 350 and attempts < 2000:
            attempts += 1
            track = random.choices(REAL_TRACKS, weights=weights)[0]
            played_at = random_played_at(start_date, end_date)
            key = (user, played_at)
            if key in used_timestamps:
                continue
            used_timestamps.add(key)
            rows.append({
                'user_id':     user,
                'track_id':    track['track_id'],
                'track_name':  track['track_name'],
                'artist_name': track['artist_name'],
                'album_name':  track['album_name'],
                'duration_ms': track['duration_ms'],
                'genre':       track['genre'],
                'played_at':   played_at,
            })
            plays_for_user += 1

    rows.sort(key=lambda x: x['played_at'])

    output_path = os.path.join(os.path.dirname(__file__), 'listening_data.csv')
    fieldnames = ['user_id','track_id','track_name','artist_name',
                  'album_name','duration_ms','genre','played_at']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Written {len(rows)} rows to {output_path}')


if __name__ == '__main__':
    generate()
