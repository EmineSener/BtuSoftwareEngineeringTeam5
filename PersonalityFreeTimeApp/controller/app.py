from flask import Flask, render_template, request
import pickle
import numpy as np
import json
import os
import requests
from dotenv import load_dotenv
from recommenderSystems.rec_sys_book import identify_popular_books, identify_similarity
from recommenderSystems.rec_sys_movie import similarity, recommend
app = Flask(__name__)

global number 
number = 0
folder = r'C:\Users\emine\Desktop\PersonalityFreeTimeApp\model\book_rec_sys_data'
ratings_with_books, books,popular_books = identify_popular_books(folder)
similarity_scores, pt = identify_similarity(ratings_with_books)

popular_data = {
        "book_name": list(popular_books['Book-Title'].values),
        "author": list(popular_books['Book-Author'].values),
        "image":list(popular_books['Image-URL-L'].values),
        "genre": ["Book"] * len(popular_books['Book-Author'])
}


user_last_book = 'Winter Solstice'
def recommend_book(user_last_book):

    index = np.where(pt.index == user_last_book)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))
        item.append('Book')
        data.append(item)

        folder = os.path.join(os.getcwd(), 'model', 'contents_of_feed')

        file_path = os.path.join(folder, 'contents_of_feed.json')
        

        if os.path.exists(folder) :
         
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file)
        else:
            with open(file_path, 'a') as json_file:
                json.dump(popular_data, json_file)

recommend_book(user_last_book)

def extract_feed_data():
    contents = []
    folder = os.path.join(os.getcwd(), 'model', 'contents_of_feed')

    file_path = os.path.join(folder, 'contents_of_feed_book.json')
    with open(file_path, 'r') as file:
        data = json.load(file)


    for content in data:
        contents.append(content)
    return contents

extract_feed_data()
@app.route('/')
def index():
    contents = extract_feed_data()
    return render_template('index.html',
                           contents = contents)

# *************** Movie Recommender *************** #
movies = pickle.load(open('movies_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))
movies_list = movies['title'].values

@app.route('/')
def home():
    return render_template('index.html', movies_list=movies_list)

@app.route('/recommend', methods=['POST'])
def recommend():
    selectValue = request.form['movie']
    load_dotenv()

    def fetch_poster(movie_id):
        api_key = os.getenv("API_KEY")
        url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, api_key)
        data=requests.get(url)
        data=data.json()
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
        return full_path

    def get_recommendations(movie):
        index = movies[movies['title'] == movie].index[0]
        distance = sorted(list(enumerate(similarity[index])),reverse = True, key = lambda vector:vector[1])
        recommend_movie = []
        recommend_poster = []
        for i in distance[1:5]:
            movies_id = movies.iloc[i[0]].id
            recommend_movie.append(movies.iloc[i[0]].title)
            recommend_poster.append(fetch_poster(movies_id))
        return recommend_movie, recommend_poster

    movie_name, movie_poster = get_recommendations(selectValue)
    return render_template('recommendations.html', movie_name=movie_name, movie_poster=movie_poster)

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
