import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine
from collections import defaultdict
import re
from typing import List, Dict

class MovieRecommender:
    def __init__(self, db):
        self.db = db
        self.movie_data = {}
        self.vocab = {}
        self.tfidf_matrix = None
        self.cosine_sim = None

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()

    def _build_vocab(self, documents: List[str]):
        vocab = defaultdict(int)
        for doc in documents:
            for token in self._tokenize(doc):
                vocab[token] += 1
        self.vocab = {term: idx for idx, (term, _) in enumerate(
            sorted(vocab.items(), key=lambda x: x[1], reverse=True))}

    def _compute_tfidf(self, documents: List[str]):
        n_docs = len(documents)
        n_terms = len(self.vocab)

        # TF матрица
        data = []
        row_ind = []
        col_ind = []

        # DF (document frequency)
        df = np.zeros(n_terms)

        for doc_idx, doc in enumerate(documents):
            tokens = self._tokenize(doc)
            term_counts = defaultdict(int)
            for token in tokens:
                if token in self.vocab:
                    term_idx = self.vocab[token]
                    term_counts[term_idx] += 1

            doc_length = len(tokens)
            for term_idx, count in term_counts.items():
                data.append(count / doc_length)
                row_ind.append(doc_idx)
                col_ind.append(term_idx)
                df[term_idx] += 1

        # Создаем TF матрицу
        self.tf_matrix = csr_matrix((data, (row_ind, col_ind)), 
                          shape=(n_docs, n_terms))

        # Вычисляем IDF
        idf = np.log(n_docs / (df + 1)) + 1

        # TF-IDF = TF * IDF
        self.tfidf_matrix: csr_matrix = self.tf_matrix.multiply(idf).tocsr()

    def _compute_cosine_similarity(self):
        n_docs = self.tfidf_matrix.shape[0]
        self.cosine_sim = np.zeros((n_docs, n_docs))

        for i in range(n_docs):
            for j in range(i, n_docs):
                vec_i = self.tfidf_matrix[i].toarray().flatten()
                vec_j = self.tfidf_matrix[j].toarray().flatten()
                sim = 1 - cosine(vec_i, vec_j)
                self.cosine_sim[i][j] = sim
                self.cosine_sim[j][i] = sim

    def prepare_data(self):
        movies = self.db.execute("SELECT * FROM movies").fetchall()
        self.movie_data = {m['id']: m for m in movies}

        movie_descriptions = [
            f"{m['title']} {m['genre']} {m['description']}" 
            for m in movies
        ]

        self._build_vocab(movie_descriptions)
        self._compute_tfidf(movie_descriptions)
        self._compute_cosine_similarity()

    def recommend(self, movie_id: int, top_n: int = 5) -> List[Dict]:
        if movie_id not in self.movie_data:
            return []

        movie_ids = list(self.movie_data.keys())
        idx = movie_ids.index(movie_id)

        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]

        recommendations = []
        for i in movie_indices:
            movie_id = movie_ids[i]
            movie = self.movie_data[movie_id]
            recommendations.append({
                "movie_id": movie['id'],
                "title": movie['title'],
                "genre": movie['genre'],
                "similarity_score": float(sim_scores[movie_indices.index(i)][1])
            })

        return recommendations

    def recommend_for_user(self, user_id: int, top_n: int = 5) -> List[Dict]:
        ratings = self.db.execute(
            "SELECT * FROM movie_ratings WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        if not ratings:
            return []

        top_rated = sorted(ratings, key=lambda x: x['rating'], reverse=True)[:3]

        all_recommendations = []
        for rating in top_rated:
            recs = self.recommend(rating['movie_id'], top_n)
            all_recommendations.extend(recs)

        unique_recs = {}
        for rec in all_recommendations:
            if rec['movie_id'] not in unique_recs:
                unique_recs[rec['movie_id']] = rec
            elif rec['similarity_score'] > unique_recs[rec['movie_id']]['similarity_score']:
                unique_recs[rec['movie_id']] = rec

        rated_movie_ids = [r['movie_id'] for r in ratings]
        final_recs = [rec for rec in unique_recs.values() 
                     if rec['movie_id'] not in rated_movie_ids]

        return sorted(final_recs, key=lambda x: x['similarity_score'], reverse=True)[:top_n]
