from datetime import datetime


def calculate_analytics(data):
    if not data:
        return None

    total_plays = len(data)

    total_ms = 0
    for row in data:
        try:
            total_ms += int(row.get('duration_ms', 0))
        except (ValueError, TypeError):
            pass
    total_minutes = round(total_ms / 60000, 1)

    artist_counts = {}
    for row in data:
        name = row.get('artist_name', 'Unknown')
        artist_counts[name] = artist_counts.get(name, 0) + 1
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # key combines track and artist to distinguish same-name tracks by different artists
    track_counts = {}
    for row in data:
        key = f"{row.get('track_name', 'Unknown')} - {row.get('artist_name', 'Unknown')}"
        track_counts[key] = track_counts.get(key, 0) + 1
    top_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    genre_counts = {}
    for row in data:
        genre = row.get('genre', 'Unknown') or 'Unknown'
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    genre_counts = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))

    hour_counts = {h: 0 for h in range(24)}
    for row in data:
        try:
            dt = datetime.strptime(row['played_at'], '%Y-%m-%dT%H:%M:%SZ')
            hour_counts[dt.hour] += 1
        except (ValueError, KeyError):
            pass

    return {
        'total_plays':   total_plays,
        'total_minutes': total_minutes,
        'top_artists':   top_artists,
        'top_tracks':    top_tracks,
        'genre_counts':  genre_counts,
        'hour_counts':   hour_counts,
    }
