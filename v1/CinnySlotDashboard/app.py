from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import pandas as pd
from recommendation import get_recommendations  # ← import the function

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'users.db'

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = 20

    df = pd.read_csv('data/posters.csv')
    total_pages = (len(df) + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    movies = df.iloc[start:end].to_dict(orient='records')

    user = session.get('user')

    start_page = max(1, page - 3)
    end_page = min(total_pages, page + 3)

    return render_template(
        'index.html',
        movies=movies,
        user=user,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Try another one.', 'warning')
            conn.close()
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/details/<int:tmdb_id>')
def movie_details(tmdb_id):
    movies_df = pd.read_csv('data/movies.csv')
    posters_df = pd.read_csv('data/posters.csv')

    movie = movies_df[movies_df['id'] == tmdb_id]
    if movie.empty:
        return "<h1>Movie not found</h1>", 404

    # Add poster
    poster_row = posters_df[posters_df['tmdb_id'] == tmdb_id]
    if not poster_row.empty:
        movie.loc[:, 'poster'] = poster_row.iloc[0]['poster']
    else:
        movie.loc[:, 'poster'] = '/static/default.png'

    # Get recommendations using separate file
    recommendations = get_recommendations(tmdb_id)

    return render_template('details.html', movie=movie.iloc[0], recommendations=recommendations)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
