########## libraries
import requests
from bs4 import BeautifulSoup
import math
import time
import pandas as pd
import csv

######### functions
def time_minutes(time):
	mm = math.floor(time / 60)
	ss = time - 60 * mm
	return f"{mm} minutes {ss:.2f} seconds"

######### settings
# Boolean parameter to limit the number of pages
limit_pages = True

# Set up the session and user agent
base_url = "https://stackoverflow.com"
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

# List to store the scraped question information
questions_info = []

# Questions per page (will be used in creating an url parameter)
# we tested several values, it does not impact the performance
question_limit = 25

# Obligatory parameter
page_limit = 150
if limit_pages == True:
	page_limit = 100

########## scraping
# Start timestamp
start_time = time.time()
  
# Iterate through the range of page numbers (Start from 1, go up to page_limit)
for page_num in range(1, page_limit + 1):
	print(f"Page number: {page_num} (out of {page_limit}), total time elapsed: {time_minutes(time.time() - start_time)}")
	# Construct the URL for the page
	url = f"https://stackoverflow.com/questions/tagged/web-scraping?tab=votes&page={page_num}&pagesize={question_limit}"
	
	# Send the request and get the response
	response = s.get(url)
	
	# Parse the HTML text using BeautifulSoup
	soup = BeautifulSoup(response.text, 'html.parser')
	
	# Find all the question elements on the page
	questions = soup.find_all('div', class_ = 's-post-summary')
	
	# Counter for the number of questions
	question_counter = 0
	
	# Iterate through each question element
	for question in questions:
		# Extract the question title, link, tags, votes, answers, and views
		q_title = question.find('a', class_ = 's-link').text.strip()
		q_link = base_url + question.find('a', class_ = 's-link')['href']
		q_tags = [tag.text for tag in question.find_all('a', class_ = 'post-tag')]
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
		
		# Increment the question counter 
		question_counter += 1  
		
		# Stop scraping if the question count reaches limit (beac)
		if question_counter >= question_limit:
			break
	
	# Pause for 1 second before making the next request
	time.sleep(1)

# End timestamp
end_time = time.time()  

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the results
print(f"Total items scraped: {len(questions_info)}")
print(f"Total elapsed time: {time_minutes(elapsed_time)}")

# Convert the list of question information to a DataFrame
df = pd.DataFrame(questions_info)

# Save the DataFrame to a .csv file
df.to_csv('questions_output.csv', index = False)
