import pandas as pd
import glob

# Get all CSV file paths from the directory
data_paths = glob.glob('./crawling_data/movie_reviews_500_movies/*.csv')

# Initialize an empty DataFrame to hold all the combined data
combined_df = pd.DataFrame()

# Loop through each file path in the list
for file_path in data_paths:
    # Read the CSV file into a DataFrame
    temp_df = pd.read_csv(file_path)
    # Concatenate the temporary DataFrame to the main DataFrame
    combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

# Now 'combined_df' contains all the data from the CSV files
print(combined_df.head())
print(combined_df.shape)
# Number of unique movie titles
print("Unique movie titles:", combined_df['movie_title'].nunique())

# Review counts per movie
print("Review counts per movie:")
print(combined_df['movie_title'].value_counts())

# Count the number of reviews for each movie
review_counts = combined_df['movie_title'].value_counts()

# Print each movie title with its corresponding review count
# for title, count in review_counts.items():
#     print(f"{title}: {count}")

# Count the number of movies that have exactly 50 reviews
movies_with_50_reviews = review_counts[review_counts == 50].count()

print(f"Number of movies with exactly 50 reviews: {movies_with_50_reviews}")