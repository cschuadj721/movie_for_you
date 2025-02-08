import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread
import pickle
from gensim.models import Word2Vec

def getRecommendation(cosine_sim):
    simScore = list(enumerate(cosine_sim[-1]))
    simScore = sorted(simScore, key=lambda x:x[1], reverse = True)

    #자기 자신 포함 11개
    simScore = simScore[:11]
    movieIdx = [i[0] for i in simScore]

    recmovieList = df_reviews.iloc[movieIdx, 0]

    #자기 자신 빼고 10개 리턴
    return recmovieList[1:11]

df_reviews = pd.read_csv('./crawling_data/cleaned_reviews.csv')
Tfidf_matrix = mmread('./models/moviereview.mtx').tocsr()

with open('./models/tfidf.pickle', 'rb') as f:
    Tfidf = pickle.load(f)

#영화 10번으로 테스트
ref_idx = 349
print(df_reviews.iloc[ref_idx, 0])

#전체 영화 리스트에 대해 cosine sim 계산
cosine_sim = linear_kernel(Tfidf_matrix[ref_idx], Tfidf_matrix)

print(cosine_sim[0:5])
print(len(cosine_sim))

recommandations = getRecommendation(cosine_sim)
print(recommandations)

# df_reviews.info()

