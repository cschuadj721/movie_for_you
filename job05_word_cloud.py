import pandas as pd
from wordcloud import WordCloud
import collections
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = './malgun.ttf'
font_name = font_manager.FontProperties(fname = font_path).get_name()
plt.rc('font', family = 'NanumBarunGothic')

df = pd.read_csv('./crawling_data/cleaned_reviews.csv')

# 기본 설정 띄어쓰기 기준으로 단어들을 나누어 리스트로 만들기
words = df.iloc[4,1].split()

print(df.iloc[4,0])

# collctions함수는 unique한 값이 몇 번 반복되는지를 보여준다
# dictionary형태를 띄지만 dictionary는 아니다
worddict = collections.Counter(words)
worddict = dict(worddict)


print(worddict)

wordcloud_img = WordCloud(
    background_color = 'white', font_path = font_path).generate_from_frequencies(worddict)
plt.figure(figsize=(12,12))
plt.imshow(wordcloud_img, interpolation='bilinear')
plt.axis('off')

plt.show()




