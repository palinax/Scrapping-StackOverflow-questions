import time
from multiprocessing import Pool, cpu_count
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.common.exceptions import NoSuchElementException

# Define the path to the ChromeDriver executable
chrome_path = '/path/to/chromedriver'
ser = Service(chrome_path)

# Define options for the Chrome driver
options = webdriver.ChromeOptions()

# Enable headless mode for faster scraping
options.add_argument("--headless")

# Disable images and CSS for faster page loading
prefs = {
    "profile.managed_default_content_settings.images": 2,  # Disable images
    "profile.managed_default_content_settings.stylesheets": 2,  # Disable CSS
    "profile.managed_default_content_settings.popups": 2,
    "profile.managed_default_content_settings.geolocation": 2,
    "profile.managed_default_content_settings.media_stream": 2,
}
options.add_experimental_option("prefs", prefs)

def scrape_website(url, limit_100_pages=True):
    # Number of pages you want to scrape
    if limit_100_pages:
        num_pages = 100
    else:
        num_pages = 999999  # A large number to scrape all available pages

    # Number of CPU cores on your machine
    num_cores = cpu_count()

    # Create a list of page numbers/URLs
    page_numbers = list(range(1, num_pages + 1))

    with Pool(num_cores) as p:
        all_results = p.map(scrape, page_numbers)

    try:
        # Open the CSV file in write mode
        with open('stackoverflow_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)

            # Write the header row
            writer.writerow(['Title', 'Link', 'Tags', 'Votes', 'Views', 'Answers'])

            # Write each row of data
            for page_results in all_results:
                for result in page_results:
                    writer.writerow([
                        result['Title'],
                        result['Link'],
                        ','.join(result['Tags']),
                        result['Votes'],
                        result['Views'],
                        result['Answers']
                    ])

        print("CSV file created successfully")

    except Exception as e:
        print("Error occurred while writing to CSV file:", str(e))

    print("Script finished")


def scrape(page_number):
    # Define the URL to be scraped
    url = f"https://stackoverflow.com/questions/tagged/web-scraping?tab=votes&pagesize=15&page={page_number}"

    # Instantiate the Chrome driver with the defined service and options
    driver = webdriver.Chrome(service=ser, options=options)

    # Navigate to the defined URL
    driver.get(url)

    # Accept cookies if the button is present
    try:
        cookie_accept_button = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'js-accept-cookies')))
        cookie_accept_button.click()
    except NoSuchElementException:
        pass

    # List to store information about the questions
    questions_info = []

    # Wait for all question elements to be present on the page
    questions = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 's-post-summary')))

    # Loop through each question on the page
    for question_counter, question in enumerate(questions, start=1):
        # Extract title element and title text
        q_title_element = question.find_element(By.CSS_SELECTOR, '.s-post-summary--content-title .s-link')
        q_title = q_title_element.text.strip()

        # Print progress after each 15th question
        if question_counter % 15 == 0:
            page_index = page_number - 1  # Adjust page index for zero-based indexing
            print(f"Page {page_index} scrapped")

        # Extract link to the question
        q_link = q_title_element.get_attribute('href')

        # Extract tags associated with the question
        q_tags = [tag.text for tag in question.find_elements(By.CLASS_NAME, 'post-tag')]

        # Extract the number of votes for the question
        q_votes = question.find_element(By.CSS_SELECTOR, '.s-post-summary--stats-item__emphasized span').text

        # Extract the number of answers for the question
        q_answers_elements = question.find_elements(By.CSS_SELECTOR, '.s-post-summary--stats-item.has-answers span')
        q_answers = q_answers_elements[0].text if q_answers_elements else 'N/A'

        # Extract the number of views for the question
        q_views_elements = question.find_elements(By.CSS_SELECTOR, '.s-post-summary--stats-item:nth-child(3) span')
        q_views = q_views_elements[0].text if q_views_elements else 'N/A'

        # Append all extracted data to the questions_info list
        questions_info.append({
            'Title': q_title,
            'Link': q_link,
            'Tags': q_tags,
            'Votes': q_votes,
            'Views': q_views,
            'Answers': q_answers,
        })

    # Wait for a short period before quitting the driver
    time.sleep(1)

    # Quit the driver after scraping
    driver.quit()

    return questions_info

if __name__ == "__main__":
    # Define the URL of the website to be scraped
    url = "https://stackoverflow.com/questions/tagged/web-scraping?tab=votes"

    # Set the boolean parameter to limit scraped pages to 100
    limit_100_pages = True

    # Call the scrape_website function with the URL and boolean parameter
    scrape_website(url, limit_100_pages)
