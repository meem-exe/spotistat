import os
import csv
import json
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

from analytics import calculate_analytics
from algorithms import bubble_sort_leaderboard, binary_search_tracks

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'spotistat-dev-key')

# Load CSV at startup so every route can access it without re-reading the file
CSV_PATH = os.path.join(os.path.dirname(__file__), 'listening_data.csv')
listening_data = []

try:
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            listening_data.append(dict(row))
    print(f'[Spotistat] Loaded {len(listening_data)} rows from listening_data.csv')
except FileNotFoundError:
    print('[Spotistat] WARNING: listening_data.csv not found. Analytics will be empty.')


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.environ.get('SPOTIPY_CLIENT_ID'),
        client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET'),
        redirect_uri=os.environ.get('SPOTIPY_REDIRECT_URI', 'http://localhost:5000/callback'),
        scope='user-read-recently-played user-read-private',
        cache_handler=spotipy.cache_handler.MemoryCacheHandler()
    )


@app.route('/')
def index():
    if 'access_token' in session:
        return redirect(url_for('analytics'))
    auth_url = get_spotify_oauth().get_authorize_url()
    return render_template('index.html', auth_url=auth_url)



@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error or not code:
        return render_template('index.html',
                               auth_url=get_spotify_oauth().get_authorize_url(),
                               error='Spotify login was cancelled or failed. Please try again.')
    try:
        token_info = get_spotify_oauth().get_access_token(code)
        session['access_token'] = token_info['access_token']
        sp = spotipy.Spotify(auth=session['access_token'])
        session['display_name'] = sp.current_user().get('display_name', 'User')
        return redirect(url_for('analytics'))
    except Exception as e:
        return render_template('index.html',
                               auth_url=get_spotify_oauth().get_authorize_url(),
                               error=f'Login error: {str(e)}')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    filtered_data = listening_data
    start_str = ''
    end_str = ''
    error_msg = None

    if request.method == 'POST':
        start_str = request.form.get('start_date', '').strip()
        end_str = request.form.get('end_date', '').strip()

        if start_str and end_str:
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_str, '%Y-%m-%d')

                if start_date > end_date:
                    error_msg = 'Start date must be on or before the end date.'
                    filtered_data = listening_data
                else:
                    filtered_data = []
                    for row in listening_data:
                        try:
                            played_at = datetime.strptime(row['played_at'], '%Y-%m-%dT%H:%M:%SZ')
                            if start_date <= played_at <= end_date:
                                filtered_data.append(row)
                        except (ValueError, KeyError):
                            pass
            except ValueError:
                error_msg = 'Invalid date format. Please use the date picker.'

    stats = calculate_analytics(filtered_data)

    chart_data = {}
    if stats:
        chart_data = {
            'artist_labels': [a[0] for a in stats['top_artists']],
            'artist_counts': [a[1] for a in stats['top_artists']],
            'track_labels':  [t[0] for t in stats['top_tracks']],
            'track_counts':  [t[1] for t in stats['top_tracks']],
            'genre_labels':  list(stats['genre_counts'].keys()),
            'genre_counts':  list(stats['genre_counts'].values()),
            'hour_labels':   list(stats['hour_counts'].keys()),
            'hour_counts':   list(stats['hour_counts'].values()),
        }

    return render_template(
        'analytics.html',
        display_name=session.get('display_name', 'User'),
        stats=stats,
        chart_data=json.dumps(chart_data),
        error_msg=error_msg,
        start_date=start_str,
        end_date=end_str,
    )


@app.route('/leaderboard')
def leaderboard():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    user_totals = {}
    for row in listening_data:
        user = row.get('user_id', 'Unknown')
        try:
            ms = int(row.get('duration_ms', 0))
        except (ValueError, TypeError):
            ms = 0
        user_totals[user] = user_totals.get(user, 0) + ms

    user_list = [(user, round(ms / 60000, 1)) for user, ms in user_totals.items()]
    sorted_users = bubble_sort_leaderboard(user_list)

    return render_template('leaderboard.html', users=sorted_users)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    result = None
    search_term = ''
    not_found = False

    if request.method == 'POST':
        search_term = request.form.get('track_name', '').strip()
        if search_term:
            result = binary_search_tracks(listening_data, search_term)
            if result is None:
                not_found = True

    return render_template('search.html', result=result,
                           search_term=search_term, not_found=not_found)


if __name__ == '__main__':
    app.run(debug=True)
