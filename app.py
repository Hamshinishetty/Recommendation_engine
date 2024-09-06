from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import requests
import logging

app = Flask(__name__)

# Load movies and ratings data
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# Create a user-based collaborative filtering movie recommendation engine

# Pivot the ratings data
final_dataset = ratings.pivot(index='movieId', columns='userId', values='rating')

# Fill missing values with 0
final_dataset.fillna(0, inplace=True)

# Count the number of votes per movie and user
no_user_voted = ratings.groupby('movieId')['rating'].agg('count')
no_movies_voted = ratings.groupby('userId')['rating'].agg('count')

# Filter movies with more than 10 votes and users with more than 50 votes
final_dataset = final_dataset.loc[no_user_voted[no_user_voted > 50].index, :]
final_dataset = final_dataset.loc[:, no_movies_voted[no_movies_voted > 100].index]

# Create a sample movie rating matrix
sample = np.array([[0,0,3,0,0],[4,0,0,0,2],[0,0,0,0,1]])

# Calculate sparsity
sparsity = 1.0 - (np.count_nonzero(sample) / float(sample.size))

# Convert the sample to a CSR matrix
csr_sample = csr_matrix(sample)

# Convert the final dataset to a CSR matrix
csr_data = csr_matrix(final_dataset.values)

# Fit a nearest neighbors model
knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
knn.fit(csr_data)

def get_movie_recommendation(movie_name):
    n_movies_to_recommend = 20
    movie_list = movies[movies['title'].str.contains(movie_name)]

    if len(movie_list):
        movie_idx = movie_list.iloc[0]['movieId']

        if movie_idx in final_dataset.index:
            movie_idx = final_dataset.index.get_loc(movie_idx)
            distances, indices = knn.kneighbors(csr_data[movie_idx], n_neighbors=n_movies_to_recommend + 1)
            rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),key=lambda x: x[1])[:0:-1]
            recommend_frame = []
            for val in rec_movie_indices:
                movie_idx = final_dataset.iloc[val[0]].name
                idx = movies[movies['movieId'] == movie_idx].index
                recommend_frame.append({'Title': movies.iloc[idx]['title'].values[0]})

            df = pd.DataFrame(recommend_frame, index=range(1, n_movies_to_recommend + 1))
            return df
        else:
            return pd.DataFrame(data=[{"Title": "Movie not found..Sorry"}])
    else:
        return pd.DataFrame(data=[{"Title": "Movie not found..Sorry"}])

@app.route('/')
def index():
    recommendations = pd.DataFrame()  # Define an empty DataFrame to avoid 'UndefinedError'
    return render_template('index.html', recommendations=recommendations)

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    movie_name = request.form.get('movie_name')
    recommendations = get_movie_recommendation(movie_name)

    return render_template('recommendations.html', movie_name=movie_name, recommendations=recommendations, get_movie_poster=get_movie_poster)

def get_movie_poster(movie_title):
    try:
        api_key = '66b309a9a99a994c040c6dca2a34d606'
        base_url = 'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': api_key,
            'query': movie_title,
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')

            if poster_path:
                poster_url = f'https://image.tmdb.org/t/p/w185/{poster_path}'
                return poster_url

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")

    # Use the provided link as the default poster
    return 'https://cdn.posteritati.com/posters/000/000/068/359/point-blank-md-web.jpg'



if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    app.run(debug=True, port=5001)

