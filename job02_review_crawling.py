import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# ---------------------------
# Constants & XPaths
# ---------------------------
BASE_URL = 'https://m.kinolights.com/discover/explore'
REVIEW_BUTTON_XPATH = '//*[@id="review"]'
MOVIE_TITLE_XPATH = '//*[@id="contents"]/div[1]/div[2]/div[1]/div[1]/h2'
REVIEW_ARTICLE_XPATH = "//*[@id='contents']/div[5]/section[2]/div/article"
SCROLLABLE_CONTAINER_XPATH = '//*[@id="content__body"]'  # Adjust this if needed

# ---------------------------
# Function to initialize a new driver instance
# ---------------------------
def init_driver():
    options = ChromeOptions()
    user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/131.0.0.0 Safari/537.36')
    options.add_argument('user_agent=' + user_agent)
    options.add_argument('lang=ko_KR')
    service = ChromeDriverManager().install()
    service = ChromeService(executable_path=service)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ---------------------------
# Helper function to scroll down
# ---------------------------
def scroll_down(driver, units=1, sleep_time=0.5):
    """
    Scrolls down the page by a fraction of the scrollable container's height.
    You might need to adjust the target container.
    """
    try:
        # First try to scroll the designated container
        container = driver.find_element(By.XPATH, SCROLLABLE_CONTAINER_XPATH)
        for _ in range(units):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;",
                container
            )
            time.sleep(sleep_time)
    except Exception:
        # Fallback to scrolling the window if container not found
        for _ in range(units):
            driver.execute_script("window.scrollBy(0, window.innerHeight/3);")
            time.sleep(sleep_time)

# ---------------------------
# Function to process a single movie
# ---------------------------
def process_movie(movie_url):
    data = []  # List to store review data for this movie
    driver = init_driver()
    try:
        # Optionally open BASE_URL first to set proper context (if needed)
        driver.get(BASE_URL)
        time.sleep(2)
        # Now navigate to the movie page
        driver.get(movie_url)
        time.sleep(3)
    except Exception as e:
        print("Error opening movie URL:", e)
        driver.quit()
        return data

    # ---------------------------
    # Extract the movie title
    # ---------------------------
    try:
        movie_title_elem = driver.find_element(By.XPATH, MOVIE_TITLE_XPATH)
        movie_title = movie_title_elem.text.strip()
        print(f"Movie title: {movie_title}")
    except NoSuchElementException:
        movie_title = "Unknown Title"
        print("Movie title element not found; using 'Unknown Title'.")

    # ---------------------------
    # Click the review button to display reviews
    # ---------------------------
    try:
        review_button = driver.find_element(By.XPATH, REVIEW_BUTTON_XPATH)
        review_button.click()
        time.sleep(2)
    except NoSuchElementException:
        print("Review button not found for movie:", movie_url)
        driver.quit()
        return data

    # ---------------------------
    # Helper function to extract reviews
    # ---------------------------
    def extract_reviews():
        review_texts = []
        try:
            review_articles = driver.find_elements(By.XPATH, REVIEW_ARTICLE_XPATH)
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

    # ---------------------------
    # Scroll to load reviews until we have 50 or no more reviews load
    # ---------------------------
    reviews = extract_reviews()
    print(f"Initial review count: {len(reviews)}")
    scroll_attempts = 0
    max_scroll_attempts = 5  # Reduced from 10 to 5
    while len(reviews) < 50 and scroll_attempts < max_scroll_attempts:
        prev_count = len(reviews)
        scroll_down(driver, units=1, sleep_time=0.5)
        time.sleep(2)
        reviews = extract_reviews()
        if len(reviews) == prev_count:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        print(f"Total reviews loaded so far: {len(reviews)} (scroll attempt {scroll_attempts})")

    if len(reviews) < 50:
        print(f"Warning: Only {len(reviews)} reviews found for movie: {movie_url}")

    # ---------------------------
    # Save reviews (up to 50) along with the movie title
    # ---------------------------
    for review in reviews[:50]:
        data.append({
            "movie_title": movie_title,
            "review": review
        })

    driver.quit()  # Close the driver after processing this movie
    return data

# ---------------------------
# Main Execution
# ---------------------------
def main():
    # Read movie links from CSV (expects a column "movie_link")
    df_links = pd.read_csv("movie_links2.csv")
    movie_links = df_links["movie_link"].tolist()
    print(f"Read {len(movie_links)} movie links from movie_links2.csv")

    all_data = []
    file_counter = 100
    movie_counter = 0  # Count movies processed in current file batch

    for idx, movie_url in enumerate(movie_links, start=1):
        print(f"\nProcessing movie {idx}: {movie_url}")
        movie_data = process_movie(movie_url)
        all_data.extend(movie_data)
        movie_counter += 1

        # After processing 10 movies, save the batch to a CSV and reset the counters.
        if movie_counter == 10:
            df_reviews = pd.DataFrame(all_data)
            output_filename = f"movie_reviews_batch_{file_counter}.csv"
            df_reviews.to_csv(output_filename, index=False, encoding="utf-8-sig")
            print(f"\nBatch {file_counter} completed. Total review records saved: {len(df_reviews)}")
            file_counter += 1
            all_data = []
            movie_counter = 0

    # Save any remaining movies that didn't fill a full batch
    if all_data:
        df_reviews = pd.DataFrame(all_data)
        output_filename = f"movie_reviews_batch_{file_counter}.csv"
        df_reviews.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"\nFinal batch {file_counter} completed. Total review records saved: {len(df_reviews)}")

if __name__ == "__main__":
    main()
