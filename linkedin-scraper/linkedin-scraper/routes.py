from contextlib import suppress, asynccontextmanager
from crawlee.router import Router
from crawlee import Request
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
            [
                Request.from_url(rec, label='job_listing') for rec in hrefs
             ]
        )

  

@router.handler('job_listing')
async def listing_handler(context: PlaywrightCrawlingContext) -> None:
    """Handler for job listings."""

    await context.page.wait_for_load_state('load')


    job_title = await context.page.locator('//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h1').text_content()

    company_name  = await context.page.locator('//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a').text_content()

    time_of_posting= await context.page.locator('//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[2]/span').text_content()

    

    
    await context.push_data(
        {
            'title': re.sub(r'[\s\n]+', '', job_title),
            'Company name': re.sub(r'[\s\n]+', '', company_name),
            # 'number of applicants':  re.sub(r'[\s\n]+', '', number_of_applicants), 
            'Time of posting': re.sub(r'[\s\n]+', '', time_of_posting), 
            'url': context.request.loaded_url,
        }
    )









        