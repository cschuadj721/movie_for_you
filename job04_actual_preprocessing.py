import pandas as pd
from konlpy.tag import Okt
import re

df = pd.read_csv('./crawling_data/reviews_kinolights.csv')
df.info()

df_stopwords = pd.read_csv('./crawling_data/stopwords.csv')
stopwords = list(df_stopwords['stopword'])

# print(stopwords)

okt = Okt()

cleaned_sentences = []

for review in df.reviews:
    review = re.sub('[^가-힣]', ' ', review)
    print(review)

    # stem=True 원형으로 다시 바꿔줌
    tokened_review = okt.pos(review, stem=True)
    print(tokened_review)

    # 명사, 동사, 형용사만 사용하고 나머지는 다 버린다
    df_token = pd.DataFrame(tokened_review, columns = ['word', 'class'])
    df_token = df_token[(df_token['class'] == 'Noun') |
                        (df_token['class'] == 'Verb') |
                        (df_token['class'] == 'Adjective')]
    print(df_token)

    words = []
    for word in df_token.word:
        if 1 < len(word):
            if word not in stopwords:
                words.append(word)

    cleaned_sentence = ' '.join(words)
    cleaned_sentences.append(cleaned_sentence)

df.reviews = cleaned_sentences
df.dropna(inplace = True)
df.info()

df.to_csv('./crawling_data/cleaned_reviews.csv', index = False)
print(cleaned_sentence)

