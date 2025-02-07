import sys
from PyQt5.QtWidgets import *

from PyQt5 import uic
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from gensim.models import Word2Vec
from scipy.io import mmread
import pickle
from PyQt5.QtCore import QStringListModel

form_window = uic.loadUiType('./movie_recommendation.ui')[0]

class Exam(QWidget, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Tfidf_matrix = mmread('./models/moviereview.mtx').tocsr()
        with open('./models/Tfidf.pickle', 'rb') as f:
            self.Tfidf = pickle.load(f)
        self.embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')

        self.df_reviews = pd.read_csv('./crawling_data/cleaned_reviews.csv')

        #리스트로 바꾸어서 sort하기
        self.titles = list(self.df_reviews.titles)
        self.titles.sort()
        for title in self.titles:
            self.cb_title.addItem(title)

        model = QStringListModel()
        model.setStringList(self.titles)
        completer = QCompleter()
        completer.setModel(model)
        self.le_keyword.setCompleter(completer)

        self.cb_title.currentIndexChanged.connect(self.combobox_slot)
        self.btn_recommend.clicked.connect(self.btn_slot)

    def btn_slot(self):
        keyword = self.le_keyword.text()
        if keyword in self.titles:
            recommendation = self.recommendation_by_title(keyword)
        else:
            recommendation = self.recommendation_by_keyword(keyword)
        if recommendation:
            self.lbl_recommendation.setText(recommendation)

    def combobox_slot(self):
        title = self.cb_title.currentText()
        print(title)
        recommendation = self.recommendation_by_title(title)
        self.lbl_recommendation.setText(recommendation)

    def recommendation_by_title(self, title):
        movie_idx = self.df_reviews[self.df_reviews.titles == title].index[0]
        cosine_sim = linear_kernel(self.Tfidf_matrix[movie_idx], self.Tfidf_matrix)
        recommandation = self.getRecommendation(cosine_sim)
        recommandation = '\n'.join(list(recommandation))
        return recommandation

    def recommendation_by_keyword(self, keyword):
        try:
            sim_word = self.embedding_model.wv.most_similar(keyword, topn=10)
        except:
            self.lbl_recommendation.setText('제가 모르는 단어에요')
            return 0

        words =[keyword]

        for word,_ in sim_word:
            words.append(word)
        print(words)
        sentence = []
        count = 10
        for word in words:
            sentence = sentence + [word] * count
            count -= 1
        sentence = ' '.join(sentence)
        print(sentence)
        sentence_vec = self.Tfidf.transform([sentence])
        cosine_sim = linear_kernel(sentence_vec, self.Tfidf_matrix)
        recommendation = self.getRecommendation(cosine_sim)
        recommendation = '\n'.join(recommendation)
        return recommendation


    def getRecommendation(self, cosine_sim):
        simScore = list(enumerate(cosine_sim[-1]))
        simScore = sorted(simScore, key=lambda x:x[1], reverse = True)

        #자기 자신 포함 11개
        simScore = simScore[:11]
        movieIdx = [i[0] for i in simScore]

        recmovieList = self.df_reviews.iloc[movieIdx, 0]

        #자기 자신 빼고 10개 리턴
        return recmovieList[1:11]



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Exam()
    mainWindow.show()
    sys.exit(app.exec_())
















