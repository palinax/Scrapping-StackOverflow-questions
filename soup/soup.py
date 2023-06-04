import requests
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd

# Boolean parameter to limit the number of pages
limit_pages = True

# Set up the session and user agent
base_url = "https://stackoverflow.com"
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

questions_info = []  # List to store the scraped question information

page_count = 0  # Counter for the number of pages

start_time = time.time()  # Start timestamp

# Iterate through the range of page numbers
for page_num in range(1, 101):  # Start from 1, go up to 100
    if limit_pages and page_count >= 100:
        break

    # Construct the URL for the page
    url = f"https://stackoverflow.com/questions/tagged/web-scraping?tab=votes&page={page_num}&pagesize=15"

    # Send the request and get the response
    response = s.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the question elements on the page
    questions = soup.find_all('div', class_='s-post-summary')

    question_counter = 0  # Counter for the number of questions

    # Iterate through each question element
    for question in questions:
        # Extract the question title, link, tags, votes, answers, and views
        q_title = question.find('a', class_='s-link').text.strip()
        q_link = base_url + question.find('a', class_='s-link')['href']
        q_tags = [tag.text for tag in question.find_all('a', class_='post-tag')]
        q_votes = question.select_one('.s-post-summary--stats-item__emphasized span').text
        q_answers_span = question.select_one('.s-post-summary--stats-item.has-answers span')
        q_answers = q_answers_span.text if q_answers_span else 'N/A'
        q_views_span = question.select_one('.s-post-summary--stats-item:nth-child(3) span')
        q_views = q_views_span.text if q_views_span else 'N/A'

        # Add the question information to the list
        questions_info.append({
            'Title': q_title,
            'Link': q_link,
            'Tags': q_tags,
            'Votes': q_votes,
            'Views': q_views,
            'Answers': q_answers,
        })

        question_counter += 1  # Increment the question counter

        if question_counter >= 15:  # Stop scraping if the question count reaches 15
            break

    time.sleep(1)  # Pause for 1 second before making the next request

end_time = time.time()  # End timestamp

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Convert the elapsed time to minutes
elapsed_time_minutes = elapsed_time / 60

# Print the results
print(f"Total items scraped: {len(questions_info)}")
print(f"Total elapsed time: {elapsed_time_minutes} minutes")

# Convert the list of question information to a DataFrame
df = pd.DataFrame(questions_info)

# Save the DataFrame to a CSV file
df.to_csv('questions_output.csv', index=False)
