import pickle
import pandas as pd
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Load trained data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values

# ✅ TMDB API key
API_KEY = "a5951bc7caf2019370101964abfe1210"

# ✅ Safer fetch_poster() function
def fetch_poster(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"
        response = requests.get(url, timeout=8)
        response.raise_for_status()  # raise HTTPError for bad status codes (4xx/5xx)
        data = response.json()

        if data.get('results') and data['results'][0].get('poster_path'):
            poster_path = data['results'][0]['poster_path']
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            print(f"⚠️ No poster found for: {movie_name}")
            return "https://via.placeholder.com/200x300?text=No+Image"

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching poster for {movie_name}: {e}")
        return "https://via.placeholder.com/200x300?text=No+Image"

@app.route('/')
def home():
    return render_template('index.html', movie_list=movie_list)

@app.route('/recommend', methods=['POST'])
def recommend():
    movie = request.form['movie']

    try:
        recommended_movies = recommend_movie(movie)
    except Exception as e:
        print(f"❌ Error recommending movies: {e}")
        return render_template(
            'index.html',
            movie_list=movie_list,
            recommendations=[],
            selected_movie=movie,
            error="Unable to generate recommendations right now."
        )

    # ✅ Fetch posters safely
    recommended_posters = [fetch_poster(m) for m in recommended_movies]

    return render_template(
        'index.html',
        movie_list=movie_list,
        recommendations=zip(recommended_movies, recommended_posters),
        selected_movie=movie
    )

def recommend_movie(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movies = [movies.iloc[i[0]].title for i in distances[1:6]]
    return recommended_movies

if __name__ == '__main__':
    app.run(debug=True)
