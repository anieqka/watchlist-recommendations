from tkinter.font import names
from math import sqrt
import pandas as pd
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

class Movie:
    def __init__(self, name, duration, director, keywords, genres, language):
        self.name = name
        self.duration = duration
        self.director = director
        self.keywords = keywords
        self.genres = genres
        self.language = language

    def __repr__(self):
        return f'Movie("{self.name}" min: {self.duration}, Dir: {self.director}, Keywords: {self.keywords}, Genre: {self.genres}, Language: {self.language})'

class Watchlist:
    def __init__(self):
        self.movies_to_watch = []
        self.movies_watched = []

    def add_movies(self, movie_list):
        self.movies_to_watch.extend(movie_list)

    def watch_movie(self, movie_name):
        print(f"Trying to watch: {movie_name}")
        for movie in self.movies_to_watch:
            if movie.name == movie_name:
                print(f"Found {movie_name} in to-watch list.")
                self.movies_to_watch.remove(movie)
                self.movies_watched.append(movie)
                return f'You have watched "{movie_name}"'
        return f'Movie "{movie_name}" not found in your to-watch list.'

    def print_status(self):
        print("\nMovies to watch (showing first 15):")
        for movie in self.movies_to_watch[:15]:
            print(movie)

        print(f"Total movies in the watchlist: {len(self.movies_to_watch)}\n")
        
        print("\nMovies watched:")
        for movie in self.movies_watched:
            print(movie)

    def total_duration_to_watch(self):
        return sum(movie.duration for movie in self.movies_to_watch)

    def total_duration_watched(self):
        return sum(movie.duration for movie in self.movies_watched)

    def watch_all_movies_of_director(self, movie_director):
        movies_by_director = [movie for movie in self.movies_to_watch if movie.director == movie_director]
        if movies_by_director:
            for movie in movies_by_director:
                self.movies_to_watch.remove(movie)
                self.movies_watched.append(movie)
            return f'You have watched all movies by {movie_director}.'
        return f'No movies by {movie_director} found in your to-watch list.'

    def build_feature_matrix(self):
        all_genres = set()
        all_keywords = set()

        for movie in self.movies_to_watch + self.movies_watched:
            all_genres.update(movie.genres)
            all_keywords.update(movie.keywords)

        all_genres = list(all_genres)
        all_keywords = list(all_keywords)

        feature_matrix = []
        for movie in self.movies_to_watch + self.movies_watched:
            genre_vector = [1 if genre in movie.genres else 0 for genre in all_genres]
            keyword_vector = [1 if keyword in movie.keywords else 0 for keyword in all_keywords]
            feature_vector = genre_vector + keyword_vector
            feature_matrix.append(feature_vector)

        return np.array(feature_matrix), all_genres + all_keywords

    def recommend_movies(self, liked_movie_name, k=3):
        liked_movie = None
        for movie in self.movies_watched:
            if movie.name == liked_movie_name:
                liked_movie = movie
                break

        if liked_movie is None:
            print(f'You haven\'t watched "{liked_movie_name}" yet, so no recommendations.')
            return []

        feature_matrix, feature_names = self.build_feature_matrix()

        movie_list = self.movies_to_watch + self.movies_watched
        liked_movie_idx = movie_list.index(liked_movie)

        similarities = cosine_similarity([feature_matrix[liked_movie_idx]], feature_matrix)[0]

        similar_movies = sorted(
            [(movie, sim) for movie, sim in zip(self.movies_to_watch, similarities[:len(self.movies_to_watch)])],
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = [movie[0] for movie in similar_movies[:k]]

        return recommendations

    def load_from_csv(self, csv_path):
        df = pd.read_csv(csv_path)

        for index, row in df.iterrows():
            movie = Movie(
                name=row['original_title'],
                duration=int(row['runtime']) if pd.notna(row['runtime']) else 0,
                director=row['director'],
                keywords=str(row['keywords']).split(', ') if pd.notna(row['keywords']) else [],
                genres=row['genres'].split(', ') if pd.notna(row['genres']) else [],
                language=row['original_language']
            )
            self.movies_to_watch.append(movie)

watchlist = Watchlist()

csv_file_path = '/Users/annapaseva/Downloads/movies.csv'
watchlist.load_from_csv(csv_file_path)

print(watchlist.watch_movie("Avatar"))
print(watchlist.watch_movie("Spectre"))

watchlist.print_status()

recommendations = watchlist.recommend_movies("Avatar", k=3)
if recommendations:
    print("Recommendations based on 'Avatar':")
    for rec in recommendations:
        print(rec)

else:
    print("\nNo recommendations found.")
