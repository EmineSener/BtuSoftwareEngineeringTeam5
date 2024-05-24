import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os 
import requests
import json

movies = pd.read_csv('movie_dataset.csv')
movies = movies[['id', 'title', 'overview', 'genre']]
movies['tags'] = movies['overview'] + movies['genre']
new_data = movies.drop(columns=['overview', 'genre'])
cv = CountVectorizer(max_features=10000, stop_words='english')
vector = cv.fit_transform(new_data['tags'].values.astype('U')).toarray()
similarity = cosine_similarity(vector)

def fetch_poster(movie_id):
    api_key = os.getenv("API_KEY")
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, api_key)
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    recommend_poster = []
    for i in distance[1:5]:
        movie_id = movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movie_id))
    return recommend_movie, recommend_poster

def save_recommendations_to_json(movie_title):
    recommendations, posters = recommend(movie_title)
    data = {"recommendations": recommendations, "posters": posters}
    with open('../../model/recommendations.json', 'w') as f:
        json.dump(data, f)

save_recommendations_to_json("Iron Man")