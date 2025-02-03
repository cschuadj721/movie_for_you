from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import time

# ---------------------------
# Setup Chrome and Options
# ---------------------------
options = ChromeOptions()
user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/131.0.0.0 Safari/537.36')
options.add_argument('user_agent=' + user_agent)
options.add_argument('lang=ko_KR')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ---------------------------
# Define XPaths for elements
# ---------------------------
# OTT buttons to enable movie lists (currently commented out)
ott_click_1 = '//*[@id="contents"]/section/div[2]/div/div/div/div[2]/button/i'
ott_click_2 = '//*[@id="contents"]/section/div[2]/div/div/div/div[3]/button/i'
ott_click_3 = '//*[@id="contents"]/section/div[2]/div/div/div/div[3]/button/i'

# Review button XPath
review_click = '//*[@id="review"]'

# Movie title XPath (after opening the movie page)
movie_title_xpath = '//*[@id="contents"]/div[1]/div[2]/div[1]/div[1]/h2'




# ---------------------------
# Open the main URL
# ---------------------------
url = 'https://m.kinolights.com/discover/explore'
driver.get(url)
time.sleep(7)  # wait for the page to load


# ---------------------------
# Helper function to scroll down the window
# ---------------------------
def scroll_down(units=1, sleep_time=0.5):
    """
    Scrolls down the page by executing a JavaScript scroll.
    Adjust the scroll distance per unit if needed.
    """
    for _ in range(units):
        driver.execute_script("window.scrollBy(0, window.innerHeight/3);")
        time.sleep(sleep_time)


# ---------------------------
# 1) (Optional) Click the 3 OTT buttons to enable movie lists
# ---------------------------
# If you need to click these, uncomment the following block:
# try:
#     driver.find_element(By.XPATH, ott_click_1).click()
#     time.sleep(1)
#     driver.find_element(By.XPATH, ott_click_2).click()
#     time.sleep(1)
#     driver.find_element(By.XPATH, ott_click_3).click()
#     time.sleep(1)
# except NoSuchElementException as e:
#     print("Error clicking one or more OTT buttons:", e)

# Scroll down 1 unit so that the movies are visible
scroll_down(units=1, sleep_time=1)

# ---------------------------
# Collect movie links
# ---------------------------
# Set the target movie count. For 25 files with 20 movies per file, set target_movie_count to 500.
target_movie_count = 500
movie_links = set()  # use a set to avoid duplicates

while len(movie_links) < target_movie_count:
    time.sleep(2)  # wait for movies to load
    try:
        # Assuming each movie is an <a> element inside the movie container.
        movies = driver.find_elements(By.XPATH, "//*[@id='contents']/div/div/div[3]/div[2]//a")
        for movie in movies:
            link = movie.get_attribute('href')
            if link:
                movie_links.add(link)
    except Exception as e:
        print("Error collecting movie links:", e)

    # If not enough movies, scroll down 8 units to trigger loading of more movies.
    if len(movie_links) < target_movie_count:
        scroll_down(units=8, sleep_time=0.7)
        print(f"Collected {len(movie_links)} movies so far...")

# Limit the list to the first target_movie_count movies
movie_links = list(movie_links)[:target_movie_count]
print(f"Total movie links collected: {len(movie_links)}")

# Save the movie links to a CSV file so you can reuse them later if needed.
df_links = pd.DataFrame(movie_links, columns=["movie_link"])
df_links.to_csv("movie_links2.csv", index=False, encoding="utf-8-sig")
print("Saved movie links to movie_links.csv")

# ---------------------------
# Prepare to store movie titles and reviews.
# ---------------------------
# We'll accumulate reviews in chunk_data and save to CSV for every 20 movies.
chunk_data = []  # each row is a dict with keys: movie_title, review
file_counter = 1  # to name output files sequentially

# ---------------------------
# Process each movie page.
# ---------------------------
for idx, movie_url in enumerate(movie_links, start=1):
    print(f"\nProcessing movie {idx}: {movie_url}")

    # Open the movie page in a new tab
    driver.execute_script("window.open(arguments[0]);", movie_url)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)  # wait for the movie page to load

    # ---------------------------
    # Extract the movie title
    # ---------------------------
    try:
        movie_title_elem = driver.find_element(By.XPATH, movie_title_xpath)
        movie_title = movie_title_elem.text.strip()
        print(f"Movie title: {movie_title}")
    except NoSuchElementException:
        movie_title = "Unknown Title"
        print("Movie title element not found; using 'Unknown Title'.")

    # ---------------------------
    # Click the review button to show reviews.
    # ---------------------------
    try:
        review_button = driver.find_element(By.XPATH, review_click)
        review_button.click()
        time.sleep(2)  # wait for review section to load
    except NoSuchElementException:
        print("Review button not found for this movie. Skipping reviews for this movie.")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        continue

    # ---------------------------
    # Scroll to load reviews.
    # ---------------------------
    # Instead of a large scroll, we now try with 1 scroll unit.
    scroll_down(units=1, sleep_time=0.5)
    time.sleep(2)


    # ---------------------------
    # Helper function to extract review texts from the page.
    # ---------------------------
    def extract_reviews():
        review_texts = []
        try:
            # Assuming each review is in an <article> element and the review text is inside the specified XPath.
            review_articles = driver.find_elements(By.XPATH, "//*[@id='contents']/div[5]/section[2]/div/article")
            for article in review_articles:
                try:
                    text_elem = article.find_element(By.XPATH, ".//div[3]/a/h5")
                    text = text_elem.text.strip()
                    if text and text not in review_texts:
                        review_texts.append(text)
                except NoSuchElementException:
                    continue
        except Exception as e:
            print("Error extracting reviews:", e)
        return review_texts


    # Collect the initially loaded reviews.
    reviews = extract_reviews()
    print(f"Initial review count: {len(reviews)}")

    # Scroll in batches of 1 unit until we have 50 reviews or no new reviews load.
    scroll_attempts = 0
    max_scroll_attempts = 10  # safeguard in case reviews stop loading
    while len(reviews) < 50 and scroll_attempts < max_scroll_attempts:
        prev_count = len(reviews)
        scroll_down(units=1, sleep_time=0.5)
        time.sleep(2)
        reviews = extract_reviews()
        if len(reviews) == prev_count:
            scroll_attempts += 1
        else:
            scroll_attempts = 0  # reset counter if new reviews loaded
        print(f"Total reviews loaded so far: {len(reviews)} (scroll attempt {scroll_attempts})")

    if len(reviews) < 50:
        print(f"Warning: Only {len(reviews)} reviews found for movie: {movie_url}")

    # Save each review along with the movie title.
    for review in reviews[:50]:
        chunk_data.append({
            "movie_title": movie_title,
            "review": review
        })

    # Close the movie tab and return to the main movies list tab.
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # After every 20 movies, save the accumulated data into a CSV file.
    if idx % 20 == 0:
        df_chunk = pd.DataFrame(chunk_data)
        output_filename = f"movie_reviews_{file_counter}.csv"
        df_chunk.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"Saved {len(df_chunk)} review records to {output_filename}")
        file_counter += 1
        chunk_data = []  # reset for the next batch

# If any movies remain that didn't fill a full batch, save them as well.
if chunk_data:
    df_chunk = pd.DataFrame(chunk_data)
    output_filename = f"movie_reviews_{file_counter}.csv"
    df_chunk.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"Saved remaining {len(df_chunk)} review records to {output_filename}")

print("Scraping completed.")
driver.quit()
