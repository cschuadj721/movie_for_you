import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.io import mmwrite, mmread
import pickle

# TF는 문장당 반복도
# I는 Inverse
# DF는 문서당 반복도

# 너무 모든 문장에 기본적으로 많이 나오는 단어 예를들어 "영화" 같은 단어들을 특수 처리해주어야 함으로 이 과정이 필요하다
# 이것은 총 횟수의 역수를 취해주면 된다.

df_reviews = pd.read_csv('./crawling_data/cleaned_reviews.csv')
df_reviews.info()

Tfidf = TfidfVectorizer(sublinear_tf=True)
Tfidf_matrix = Tfidf.fit_transform(df_reviews.reviews)

print(Tfidf_matrix.shape)


#나중에 활용해야하기 때문에 Tfidf를 저장해 놓아야 한다
with open('./models/tfidf.pickle', 'wb') as f:
 pickle.dump(Tfidf, f)

mmwrite('./models/moviereview.mtx', Tfidf_matrix)
