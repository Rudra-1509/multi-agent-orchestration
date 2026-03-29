import requests
from pydantic import BaseModel
from langchain.tools import StructuredTool
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright

class ScraperInput(BaseModel):
    url:str

def bs4_scrape(url: str)->str:
    response=requests.get(url=url,timeout=10,headers={"User-Agent": "Mozilla/5.0"})
    soup=bs(response.text,"lxml")
    for tags in soup(["script","style"]):
        tags.extract()
    text = soup.get_text(separator="\n")
    return text.strip()[:3000]

def playwright_scrape(url: str)->str:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto(url=url,timeout=15000)
        content=page.content()
        context.close()
        browser.close()
    soup=bs(content,"lxml")
    for tags in soup(["script","style"]):
        tags.extract()
    text = soup.get_text(separator="\n")
    return text.strip()[:3000]

def smart_scrape(url: str)-> str:
    try:
        text=bs4_scrape(url)
        if len(text) < 500 or "enable javascript" in text.lower():
            text=playwright_scrape(url)
        return text
    except Exception as e:
        return f"Error in scrape tool: {str(e)}"
    
scrape_tool = StructuredTool.from_function(
    func=smart_scrape,
    name="web_scraper",
    description="Scrape webpage content. Uses fast scraping first, falls back to browser if needed.",
    args_schema=ScraperInput
)