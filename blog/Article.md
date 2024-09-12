# How to Build a LinkedIn Job Posting Scraper using Crawlee for Python and Streamlit

## Introduction

Crawlee is a web scraping and browser automation library that allows you to perform web scraping at scale. It gives you the flexibility and control you need to get the best outcome from your web scraping tasks.

In this article, we are going to be learning how to scrape LinkedIn’s website for job postings using Crawlee for Python. Furthermore, we will also be building a simple web application using Streamlit for the front end and FastAPI for the back end.

## Prerequisites

Here is a list of things we must have installed before moving further:

- [Python 3.9](https://www.python.org/) or later 
- [Crawlee ](https://crawlee.dev/python)
- [Streamlit ](https://streamlit.io/)
- [FastAPI](https://fastapi.tiangolo.com/)

### Virtual environment creation

It is good programming practice to always create a virtual environment at the start of your project to avoid dependency issues.

To create a virtual environment in Python, run this line in the path of your project directory

```bash
python -m venv name_of_virtual_enviroment
```
The name you choose for your virtual environment should replace `name_of_virtual_enviroment`. For the sake of this article, I will call mine `.crawl`

Activate your virtual environment

#### For Windows Os

```bash
.crawl\Scripts\activate
```

#### For Mac/Linux Os

```bash
 .crawl/bin/activate
```

Create a requirement.txt file and add the following lines

```
Crawlee[all]
Streamlit
uvicorn
fastapi
```

Run 

```bash
pip install -r requirements.txt
```

Now that we have everything set up, let's proceed.


## Building the LinkedIn Scraper using Crawlee for Python

In this section, we are going to be building the scraper using the Crawlee Python package. To learn more about Crawlee, check out their [documentation](https://crawlee.dev/python/docs/quick-start).

We will begin by creating a `src` directory and adding two Python files which are:

- **main.py**  - This will serve as the entry for your application

- **routes.py** - This file contains the logic for different scraping routes

Your file structure should have this order:

```
LINKEDIN_WEB_SCRAPING

- src
  - main.py
  - routes.py
  - requirements.txt
- .crawl
 
```

### Importing Libraries 

The next step is to configure our Playwright crawler in the `main.py` file. Crawlee allows us to choose from different crawlers depending on our use case. For websites with JavaScript rendering, we will typically want to use the Playwright crawler, while the Beautifulsoup and Scrapy crawlers will work well for other websites.

The next step is to import the required libraries in our main.py file 

```python
import asyncio
```

The standard asyncio library helps manage Crawlee's asynchronous operations. 

```python
from crawlee.playwright_crawler import PlaywrightCrawler
from crawlee.proxy_configuration import ProxyConfiguration
from routes_3 import router
import urllib.parse
```

Crawlee has built-in [configurations](https://crawlee.dev/blog/proxy-management-in-crawlee) to help handle the rotation and sessions of our proxy servers to avoid getting blocked by the websites we are scraping.

### Inspecting the LinkedIn job Search Page

Open LinkedIn on your web browser and sign out from the website (if you already have an account logged in). You should see an interface like this.

![Interface](image.png)

Navigate to the jobs section, search for a job and location of your choice; copy the Uniform Resource Locator (URL).

![LinkedIn](image-1.png)

You should have something like this:

`https://www.linkedin.com/jobs/search?keywords=Backend%20Developer&location=Canada&geoId=101174742&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0` 

The URL can be divided into two:

- The base URL
- The parameters

The base URL is usually before the question mark while the parameters come after the question mark. Furthermore, you can change the inputs to the parameters to get different results on your webpage.

Our focus is going to be on the keyword and location parameters. The job title the user supplies will serve as input to the keyword parameter while the location the user supplies  will go into the location parameter. Lastly, the geoId parameter will be removed while we keep the other parameters constant.

```python
title = "backend developer"  # Job title
location = "newyork"  # Job location
data_name = "backend job"

base_url = "https://www.linkedin.com/jobs/search"

params = {"keywords": title, "location": location, "trk": "public_jobs_jobs-search-bar_search-submit" ,"position": "1","pageNum": "0"}
encoded_params = urllib.parse.urlencode(params)
encoded_url = f"{base_url}?{encoded_params}"
```

We will use the Urllib library to encode the base URL and its parameters into a format that can be used to make requests to the web.

Now that we have encoded the URL, the next step for us is to set up the playwright crawler. The crawler takes in your list of proxies and your custom-defined routers.

```python
async def main() -> None:
    proxy_configuration = ProxyConfiguration(
    proxy_urls=[
'http://USERNAME:PASSWORD@proxy1.com:port',
'http://USERNAME:PASSWORD@proxy2.com:port',  
    ])
    crawler = PlaywrightCrawler(
	  # Number of requests it can make in a single crawl session
        max_requests_per_crawl=50,
        # Run with a visible browser window.
        headless=False,
        # Browser types supported by Playwright.
        browser_type='firefox',
        #handles the routing
        request_handler=router,
	  # handles your proxy configurations
        proxy_configuration=proxy_configuration,
        use_session_pool=True,
    )

    # Run the crawler with the initial list of URLs.
    await crawler.run([encoded_url])
         r = data_name + '.csv'

    #stores all the scraped data in a csv file
    await crawler.export_data(r)
if __name__ == '__main__':
    asyncio.run(main())
```

### Routing your Crawler

We will be making use of two routers for your application. These routes include:

- **Default handler** 

    The `default_handler` route is the fallback route that handles the start URL

- **Job listing** 

    The `job_listing` route extracts the individual job details.

The Playwright crawler is going to crawl through the job posting page and extract the links to all job postings on the page.

![alt text](image-2.png)

When you examine the job postings, you will discover that the job posting links are inside an ordered list with a class named `jobs-search__results-list`. We will then extract the links using the Playwright locator object and add them to the `job_listing` route for processing.

```python
import asyncio
from contextlib import suppress, asynccontextmanager
from crawlee.basic_crawler import Router
from crawlee.models import Request
from crawlee.playwright_crawler import PlaywrightCrawlingContext
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import re

router = Router[PlaywrightCrawlingContext]()

@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Default request handler."""

    #select all the links for the job posting on the page
    hrefs = await context.page.locator('ul.jobs-search__results-list a').evaluate_all("links => links.map(link => link.href)")

    #add all the links to the job listing route
    await context.add_requests(
            [Request.from_url(rec, label='job_listing') for rec in hrefs]
        )
```

Now that we have the job postings, the next step is to scrape the details on them.

We'II extract each job’s title, company's name, time of posting and the link to the job post. Open your dev tools to extract each element Xpath.

![alt text](image-3.png)

After scraping each of the parameters, we'll remove special characters from the text to make it clean and push the data to local storage using `context.push_data` function.

```python
@router.handler('job_listing')
async def listing_handler(context: PlaywrightCrawlingContext) -> None:
    """Handler for job listings."""

    await context.page.wait_for_load_state('load')

    job_title = await context.page.locator('//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h1').text_content()

    company_name  = await context.page.locator('//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a').text_content()

    time_of_posting= await context.page.locator('//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[2]/span').text_content()
   
    await context.push_data(
        {
            'title': re.sub(r'[\s\n]+', '', job_title),
            'Company name': re.sub(r'[\s\n]+', '', company_name),
            'Time of posting': re.sub(r'[\s\n]+', '', time_of_posting),
            'url': context.request.loaded_url,
        }
    )
```

## Creating your Application

A typical web application is made up of a frontend and a backend. For this project, we will be using Streamlit for the front end and a FastAPI backend.

Before we proceed, we are going to add two new files named `app.py` and `fast.py` to our `src` directory.

### Streamlit

The function `main` which serves as the entry point of the Streamlit application receives the title, location and download directory from the user and sends it to the FastAPI endpoint for scraping. Now place the code below in your `app.py` file.

```python
import requests
import streamlit as st

# Function to make a request to the FastAPI endpoint
def call_fastapi_endpoint(title, location, data_name):
    url = "http://127.0.0.1:6000/scrape"
   
    payload = {
        "title": title,
        "location": location,
        "data_name": str(data_name)
    }
    response = requests.post(url, json=payload)
    return response.json()

def main():
    st.title("LinkedIn Jobs Crawler")

    # User input fields
    title = st.text_input("Enter Job Title: ")
    location = st.text_input("Enter Job Location: ")
    data_name = st.text_input("Enter Data Name")

    if st.button("Start Processing"):
        with st.spinner("Crawling in progress..."):
            r = call_fastapi_endpoint(title, location, data_name)
        if r['status_code'] == 200:
            st.success("Processing complete!")
        else:
            st.success("Error")

    else:
        st.error("Please fill in all fields.")

if __name__ == "__main__":
    main()
```

### FastAPI

The FastAPI has two endpoints which are health and scrape. The first endpoint is to ensure the app is up and running while the second endpoint does the actual scraping.

Our scrape endpoint is going to consist of the code from our `main.py` file with a few modifications. The title, location and data\_name will come from the parameters of the post request. Now copy the code below and paste it into your `fast.py` file.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from crawlee.playwright_crawler import PlaywrightCrawler
from crawlee.proxy_configuration import ProxyConfiguration
from routes import router
import urllib.parse
from pydantic import BaseModel

app = FastAPI()

@app.get('/health')
async def health():
    return {
        "application": "Simple scraping API",
        "message": "running succesfully"
    }

@app.post('/scrape')
async def scrape(request: Request):  
    query = await request.json()

    title = query["title"]
    location = query["location"]
    data_name= query["data_name"]

    base_url = "https://www.linkedin.com/jobs/search"
    params = {
        "keywords": title,
        "location": location,
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "position": "1",
        "pageNum": "0"
    }
    encoded_params = urllib.parse.urlencode(params)
    encoded_url = f"{base_url}?{encoded_params}"

    proxy_configuration = ProxyConfiguration(
        proxy_urls=[
'http://USERNAME:PASSWORD@proxy1.com:port',
'http://USERNAME:PASSWORD@proxy2.com:port',  
        ]
    )

    crawler = PlaywrightCrawler(
        # Number of requests it can make in a single crawl session
        max_requests_per_crawl=50,
        # Run with a visible browser window.
        headless=False,
        # Browser types supported by Playwright.
        browser_type='firefox',
        #handles the routing
        request_handler=router,
	  # handles your proxy configurations
        proxy_configuration=proxy_configuration,
        use_session_pool=True,
    )

    await crawler.run([encoded_url])   
     
    r = data_name + '.csv'
    await crawler.export_data(r)

    return {"status_code": 200}

if __name__ == "__main__":
    import uvicorn
    print("Starting LLM API")
    uvicorn.run(app, host="0.0.0.0",reload= True)
```

You can then delete your `main.py` file since we don’t need it again.

## Testing your App

To run your application, ensure your FastAPI backend is running. To start your FastAPI backend, change the directory to your `src` directory and run this code in your terminal

```bash
uvicorn fast:app --port 6000
```

We will start the Streamlit application by running this code in the terminal:

```bash
streamlit run app.py
```

This is what your application what the application should look like on the browser

![alt text](image-4.png)

To access the scraped data, go over to your `src` directory and open the CSV file

![alt text](image-5.png)

You should have something like this as the output of your CSV file.

## Conclusion

In this tutorial, we have been able to learn how to build an application that is capable of scraping job posting data from LinkedIn using Crawlee. Have fun building great scraping applications with Crawlee.
