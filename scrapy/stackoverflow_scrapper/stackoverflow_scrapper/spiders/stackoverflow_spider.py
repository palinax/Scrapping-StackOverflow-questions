import scrapy

# Define the spider class
class StackoverflowSpider(scrapy.Spider):
    name = 'stackoverflow_spider'  # Set the name of the spider
    start_urls = ["https://stackoverflow.com/questions/tagged/web-scraping?tab=Votes&page=1&pagesize=15"]  # Specify the start URLs
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 50,
        'DOWNLOAD_DELAY': 0.2,  # Download delay to respect server 
        'COOKIES_ENABLED': False,  # Disable cookies
        'TELNETCONSOLE_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': False,
        'HTTPCACHE_ENABLED': True,  # Enable HTTP cache
    }

    page_counter = 0  # Counter for the number of pages
    limit_pages = True  # Boolean parameter to limit the number of pages

    # Parse method to handle the response
    def parse(self, response):
        questions = response.css('div.s-post-summary')  # Extract the question elements
        question_counter = 0  # Counter for the number of questions

        for question in questions:
            # Extract the question information
            q_title = question.css('a.s-link::text').get().strip()  # Extract the question title
            q_link = response.urljoin(question.css('a.s-link::attr(href)').get())  # Extract the question link
            q_tags = question.css('a.post-tag::text').getall()  # Extract the question tags
            q_votes = question.css('.s-post-summary--stats-item__emphasized span::text').get()  # Extract the question votes
            q_answers_span = question.css('.s-post-summary--stats-item.has-answers span::text')  # Extract the question answers
            q_answers = q_answers_span.get() if q_answers_span else 'N/A'  # Handle cases where answers are not available

            q_views_span = question.css('.s-post-summary--stats-item:nth-child(3) span::text')  # Extract the question views
            q_views = q_views_span.get() if q_views_span else 'N/A'  # Handle cases where views are not available

            # Yield the question information as a dictionary
            yield {
                'Title': q_title,
                'Link': q_link,
                'Tags': q_tags,
                'Votes': q_votes,
                'Views': q_views,
                'Answers': q_answers
            }

            question_counter += 1  # Increment the question counter

            if question_counter >= 15:  # Stop scraping if the question count reaches 15
                break

        self.page_counter += 1  # Increment the page counter

        if self.limit_pages and self.page_counter >= 100:  # Stop crawling if the page count reaches 100
            return

        next_link = response.css('a[rel=next]::attr(href)').get()  # Extract the URL for the next page
        if next_link:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse)