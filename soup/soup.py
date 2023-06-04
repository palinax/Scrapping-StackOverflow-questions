import requests
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd
import sys

# Set up the session and user agent
base_url = "https://stackoverflow.com"
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

questions_info = []  # List to store the scraped question information

page_count = 0  # Counter for the number of pages

start_time = time.time()  # Start timestamp

# Get the command line arguments
limit_pages = True

# Iterate through the range of page numbers
for page_num in range(1, 101):  # Start from 1, go up to 100
    if limit_pages and page_count >= 100:
        break

    # Rest of the code remains the same

    question_counter += 1  # Increment the question counter
    page_count += 1  # Increment the page counter

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
df.head()
