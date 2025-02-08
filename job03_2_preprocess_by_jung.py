import pandas as pd
import glob


#각 영화당 모든 리뷰를 하나로 합치기 + 모든 csv 파일 통합하기
data_paths = glob.glob('./crawling_data/movie_reviews_500_movies/*')
print(data_paths)

df = pd.DataFrame()
for path in data_paths:
    df_temp = pd.read_csv(path)
    print(df_temp.head())
    titles = []
    reviews = []
    old_title = ''

    for i in range(len(df_temp)):

        title = df_temp.iloc[i, 0]
        if title != old_title:
            title = title.replace('\"', '')
            titles.append(title)
            old_title = title
            df_movie = df_temp[(df_temp.movie_title == title)]
            review = ' '.join(df_movie.review)

            # for i in range(len(df_movie)):
            #     review = review + ' ' + df_movie.iloc[i, 1]
            reviews.append(review)

        review = df_temp.iloc[i, 1]

    print(len(titles))
    print(len(reviews))

    df_batch = pd.DataFrame({'titles': titles, 'reviews': reviews})
    df_batch.info()
    print(df_batch)
    df = pd.concat([df, df_batch], ignore_index = True)

df.info()
df.to_csv('./crawling_data/reviews_kinolights.csv', index=False)
