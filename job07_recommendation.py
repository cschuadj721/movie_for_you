import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread
import pickle
from konlpy.tag import Okt
from gensim.models import Word2Vec

from job06_TFIDF import Tfidf_matrix


def getRecommendation(cosine_sim):
    simScore = list(enumerate(cosine_sim[-1]))
    simScore = sorted(simScore, key=lambda x:x[1], reverse = True)
    simScore = simScore[:11]
    movieIdx = [i[0] for i in simScore]

    recmovieList = df_reviews.iloc[movieIdx, 0]
    return recmovieList[1:11]

df_reviews = pd.read_csv('./crawling_data/cleaned_reviews.csv')
Tfidf_matrix = mmread('./models/moviereview.mtx').tocsr()

with open('./models/tfidf.pickle', 'rb') as f:
    Tfidf = pickle.load(f)

#영화 10번으로 테스트
ref_idx = 349
print(df_reviews.iloc[ref_idx, 0])
cosine_sim = linear_kernel(Tfidf_matrix[ref_idx], Tfidf_matrix)

print(cosine_sim[0:5])
print(len(cosine_sim))

recommandations = getRecommendation(cosine_sim)
print(recommandations)

# df_reviews.info()


