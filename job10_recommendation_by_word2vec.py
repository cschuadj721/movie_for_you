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


embedding_model =Word2Vec.load('./models/word2vec_movie_review.model')
keyword = '공포'
if keyword in list(embedding_model.wv.index_to_key):
    sim_word = embedding_model.wv.most_similar(keyword, topn=10)
    words = [keyword]
    for word, _ in sim_word:
        words.append(word)
    print(words)
else:
    print('no word')
    exit()

# 유사도 높은 단어 순으로 반복하는 임의의 문장 만들기
sentence = []
count = 10
for word in words:
    sentence = sentence + [word] * count
    count -= 1
sentence = ' '.join(sentence)
print(sentence)

sentence_vec = Tfidf.transform([sentence])
cosine_sim = linear_kernel(sentence_vec, Tfidf_matrix)
recommendation = getRecommendation(cosine_sim)

print(recommendation)