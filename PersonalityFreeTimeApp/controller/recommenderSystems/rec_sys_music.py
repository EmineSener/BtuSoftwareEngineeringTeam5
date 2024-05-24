import pandas as pd
import numpy as np
import nltk 
from nltk.stem.porter import PorterStemmer
nltk.download('punkt')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


musics = pd.read_csv('spotify_millsongdata.csv')

musics = musics.sample(5000).drop('link',axis = 1).reset_index(drop=True)

musics['text'] = musics['text'].str.lower().replace(r'^\w\s','').replace(r'\n',' ',regex = True)

stemmer = PorterStemmer()

def token(txt):
    token = nltk.word_tokenize(txt)
    tokens = [stemmer.stem(w) for w in token]
    return " ".join(tokens)

musics['text'].apply(lambda x:token(x))

tfid = TfidfVectorizer(analyzer= 'word',stop_words = 'english')
matrix = tfid.fit_transform(musics['text'])
smiler = cosine_similarity(matrix)
def recommender(song_name):
    idx =  musics[musics['song'] == song_name].index[0]
    distance = sorted(list(enumerate(smiler[idx])),reverse=True, key=lambda x:x[1])
    song = []
    for s_id in distance[1:20]:
        song.append(musics.iloc[s_id[0]].song)
    return song

songs = recommender("You Make Me Feel Like Dancing")

songs = musics[musics['song'].isin(songs)][['artist', 'song']]

songs.to_json("songs.json")