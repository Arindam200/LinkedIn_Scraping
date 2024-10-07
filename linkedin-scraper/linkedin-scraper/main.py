from crawlee.playwright_crawler import PlaywrightCrawler
from .routes import router  
from urllib.parse import urlencode, urljoin                                    



async def main(title: str, location: str, data_name: str) -> None:
    base_url = "https://www.linkedin.com/jobs/search"

    # URL encode the parameters
    params = {
        "keywords": title,
        "location": location,
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "position": "1",
        "pageNum": "0"
    }

    encoded_params = urlencode(params)
    
    # Encode parameters into a query string
    query_string = '?' + encoded_params

    # Combine base URL with the encoded query string
    encoded_url = urljoin(base_url, "") + query_string
    

    # Initialize the crawler
    crawler = PlaywrightCrawler(
        request_handler=router,
    )

    # Run the crawler with the initial list of URLs
    await crawler.run([
        encoded_url
        
        ])

    # Save the data in a CSV file
    output_file = f"{data_name}.csv"
    await crawler.export_data(output_file)