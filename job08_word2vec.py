import pandas as pd
from gensim.models import Word2Vec

df_reviews = pd.read_csv('./crawling_data/cleaned_reviews.csv')
df_reviews.info()

reviews = list(df_reviews.reviews)
print(reviews[0])

tokens = []
for sentence in reviews:
    token = sentence.split()
    tokens.append(token)
print(tokens[0])

#word2Vec 모델 생성하여 저장하기
#차원의 저주때문에 원래 만차원 이상이 되어야 할 의미 차원은 100차원으로 제한한다
#window = 4 는 4형태소 단위로 학습을 한다.
#workers = 4 는 몇개의 CPU코어를 사용할것이냐
#min_count = 20 은 최소 20번 이상 나오는 표현을 기준으로 학습을 시키는것

embedding_model = Word2Vec(tokens, vector_size=100, window=4,
                           min_count=20, workers=4, epochs=100, sg=1)

embedding_model.save('./models/word2vec_movie_review.model')

#의미공간상 학습이 가능했던 형태소들 출력
print(list(embedding_model.wv.index_to_key))

#의미공간상 학습이 가능했던 형태소의 갯수
print(len(embedding_model.wv.index_to_key))

#너무 차원 수가 많기때문에 시각화할수 없기때문에 차원축소를 해야한다


