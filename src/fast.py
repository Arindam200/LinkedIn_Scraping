from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from crawlee.playwright_crawler import PlaywrightCrawler
from crawlee.proxy_configuration import ProxyConfiguration
from routes import router
import urllib.parse


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
        max_requests_per_crawl= 50,
        headless=True,
        browser_type='firefox',
        request_handler=router,
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