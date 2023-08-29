import json
# from .data_manager_interface import DataManagerInterface
from moviweb_app.datamanager.data_manager_interface import DataManagerInterface


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename
        self.users = self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            return []

    def save_data(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    def save_users(self):
        self.save_data(self.users)

    def get_all_users(self):
        # Return all the users all users
        with open(self.filename, 'r') as file:
            data = json.load(file)
        return data

    def get_user_movies(self, user_id):
        # Return all the movies for a given user
        with open(self.filename, 'r') as file:
            data = json.load(file)
        user_movies = []
        for user in data:

            if user.get("id") == user_id:
                print(user_id)
                user_movies = user.get("movies", [])
                break
        return user_movies

    def add_user(self, user_data):
        all_users = self.get_all_users()
        new_user_id = max(user['id'] for user in all_users) + 1
        user_data['id'] = new_user_id
        all_users.append(user_data)

        with open(self.filename, 'w') as file:
            json.dump(all_users, file, indent=4)

    def update_user(self, updated_user):
        all_users = self.get_all_users()

        for i, user in enumerate(all_users):
            if user['id'] == updated_user['id']:
                all_users[i] = updated_user
                break

        with open(self.filename, 'w') as file:
            json.dump(all_users, file)

    def add_movie(self, user_id, movie_data):
        users = self.get_all_users()
        for user in users:
            if user["id"] == user_id:
                user["movies"].append(movie_data)
                break

        with open(self.filename, 'w') as json_file:
            json.dump(users, json_file, indent=4)

    def update_movie(self, user_id, movie_id, updated_title, updated_rating):
        users = self.get_user_movies(user_id)
        user = next((u for u in users if u['id'] == user_id), None)

        if user:
            print("Found user:", user)
            user_movies = user.get('movies', [])

            movie = next((m for m in user_movies if m.get('id') == movie_id), None)

            if movie:
                print("Found movie:", movie)
                movie['title'] = updated_title
                movie['rating'] = float(updated_rating)

                with open(self.filename, 'w') as json_file:
                    json.dump(users, json_file, indent=4)

                print("Movie updated successfully.")
            else:
                print("Movie not found.")
        else:
            print("User not found.")

    def delete_movie(self, user_id, movie_id):
        users = self.load_data()
        user = next((u for u in users if u['id'] == user_id), None)

        if user:
            movie_to_delete = next((m for m in user['movies'] if m.get('id') == movie_id), None)
            if movie_to_delete:
                user['movies'].remove(movie_to_delete)
                self.save_data(users)
