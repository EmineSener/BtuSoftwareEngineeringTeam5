import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os 
import json


def identify_popular_books(folder):
    file_path = os.path.join(folder,'books.csv')
    books = pd.read_csv(file_path, dtype={'column_name': str})
    file_path = os.path.join(folder,'users.csv')
    users = pd.read_csv(file_path, dtype={'column_name': str})
    file_path = os.path.join(folder,'ratings.csv')
    ratings = pd.read_csv(file_path, dtype={'column_name': str})
    print(ratings.head())
    ratings_with_books = ratings.merge(books, on= 'ISBN')
    ratings_with_title = ratings_with_books.groupby('Book-Title')
    title_and_num_rating = ratings_with_title.count()['Book-Rating'].reset_index()
    title_and_num_rating.rename(columns = {'Book-Rating':'num_ratings'},inplace=True)
    title_and_avg_rating = ratings_with_books.groupby('Book-Title')['Book-Rating'].mean().reset_index()
    title_and_avg_rating.rename(columns={'Book-Rating':'avg_rating'},inplace=True)
    popular_books = title_and_num_rating.merge(title_and_avg_rating,on='Book-Title')
    popular_books = popular_books[popular_books['num_ratings']>=250]
    popular_books = popular_books.sort_values('avg_rating',ascending = False)
    popular_books = popular_books.merge(books,on = 'Book-Title')
    popular_books  = popular_books.drop_duplicates('Book-Title')
    popular_books = popular_books[['Book-Title','Book-Author','Image-URL-L']]
    popular_books = popular_books.head(20)
    folder = os.path.join(os.getcwd(), 'model', 'contents_of_feed')

    file_path = os.path.join(folder, 'popular_books.json')
    popular_books_dict = popular_books.to_dict(orient='records')

    with open(file_path, 'w') as json_file:
        json.dump(popular_books_dict, json_file)
    return ratings_with_books,books,popular_books

def identify_similarity(ratings_with_books):
    x = ratings_with_books.groupby('User-ID').count()['Book-Rating'] > 200
    bookworm_users = x[x].index
    filtered_rating = ratings_with_books[ratings_with_books['User-ID'].isin(bookworm_users)]
    y = filtered_rating.groupby("Book-Title").count()["Book-Rating"] >=50
    famous_books = y[y].index
    final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]
    pt = final_ratings.pivot_table(index = 'Book-Title', columns='User-ID', values='Book-Rating')
    pt.fillna(0,inplace = True)
    similarity_scores = cosine_similarity(pt)
    return similarity_scores,pt


