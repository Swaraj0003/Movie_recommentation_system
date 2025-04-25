import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


MOVIE_DATA_PATH = 'data/movies.csv'
movies_df = pd.read_csv(MOVIE_DATA_PATH)



def get_recommendations(movie_id):
    with open('data/tfidf_vectorizer.pkl', 'rb') as file:
        tfidf = pickle.load(file)
    
    movie_genre = movies_df[movies_df['id'] == movie_id]['genres'].values
    tf = tfidf.transform([movie_genre[0]])
    tfidf_matrix= tfidf.transform(movies_df['genres'])
    cosine_sim_scores = cosine_similarity(tf, tfidf_matrix)
    cosine_sim_scores = cosine_sim_scores.flatten()
    similar_movie_indices = cosine_sim_scores.argsort()[-6:-1][::-1]
    similar_movies = movies_df.iloc[similar_movie_indices]
    similar_titles = []
    for index, row in similar_movies.iterrows():
        similar_titles.append(row['original_title'])
    return(similar_titles)  # or return similar_titles from a function
