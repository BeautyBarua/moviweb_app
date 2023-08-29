import json

from flask import Flask, render_template, request, redirect, url_for, request, abort
from datamanager.json_data_manager import JSONDataManager
import requests

app = Flask(__name__)

# Create an instance of the DataManager class
json_file_path = "user_data.json"  # Replace with the actual file path
data_manager = JSONDataManager(json_file_path)


@app.route('/')
def home():
    """This is the home page"""
    return render_template('index.html')


@app.route('/users')
def users_list():
    """Shows User List"""
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """User's Movie List"""
    users = data_manager.get_all_users()
    user = next((user for user in users if user.get("id") == user_id), None)
    movies = user.get('movies', []) if user else []
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add New user"""
    if request.method == 'POST':
        user_data = {
            'name': request.form['name'],
            'movies': []  # Initialize with an empty list of movies
        }
        data_manager.add_user(user_data)
        return redirect(url_for('users_list'))

    return render_template('add_users.html')


def fetch_movie_details_from_omdb(movie_title):
    api_key = 'bf224838'
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}'

    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        if movie_data.get('Response') == 'True':
            # Extract relevant movie details
            movie_details = {
                'title': movie_data['Title'],
                'director': movie_data['Director'],
                'year': int(movie_data['Year']),
                'rating': float(movie_data['imdbRating'])
            }
            return movie_details

    return None


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add New Movie"""
    if request.method == 'POST':
        # Get movie data from the form
        movie_title = request.form['title']

        # Fetch movie details from OMDb API using the movie title
        movie_details = fetch_movie_details_from_omdb(movie_title)

        if movie_details:
            data_manager.add_movie(user_id, movie_details)
            return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update the movies"""
    user_movies = data_manager.get_user_movies(user_id)
    movie_to_update = next((movie for movie in user_movies if movie.get('id') == movie_id), None)

    if movie_to_update is None:
        return "Movie not found", 404

    if request.method == 'POST':
        # Handle form submission and update movie details
        new_title = request.form['title']
        new_director = request.form['director']
        new_year = int(request.form['year'])
        new_rating = float(request.form['rating'])

        movie_to_update['Title'] = new_title
        movie_to_update['director'] = new_director
        movie_to_update['year'] = new_year
        movie_to_update['rating'] = new_rating

        data_manager.save_users()  # Save the updated user data

        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', user_id=user_id, movie=movie_to_update)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """Delete the movie"""
    users = data_manager.load_data()  # Load the user data

    user = next((user for user in users if user.get("id") == user_id), None)
    if user is None:
        return "User not found", 404

    user_movies = user.get("movies", [])
    movie_to_delete = next((movie for movie in user_movies if movie.get('id') == movie_id), None)

    if movie_to_delete is None:
        return "Movie not found", 404

    user_movies.remove(movie_to_delete)

    # If the user has no more movies, remove the 'movies' key
    if not user_movies:
        user.pop('movies', None)

    data_manager.save_data(users)  # Save the updated user data

    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
