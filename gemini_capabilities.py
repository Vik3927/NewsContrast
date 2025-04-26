import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial
from googlesearch import search
from utils import build_domain_url_map

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

prompt = """If I share a webpage URL would you be able to fetch me its content? If yes read content from this website and create a search text that I can use on google.com to search and read more about this news article. Return nothing else but the text that I can use to search about this news on the internet and read more about it. Do not share anything apart from the search text. Here's the URL to the news article: 
https://www.thehindu.com/news/national/supreme-court-waqf-amendment-bill-hearing-highlights/article69455323.ece"""
response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt)

SearchQuery = response.text
print(f"SearchQuery :: {SearchQuery}")

SearchResults = search(SearchQuery, num_results=15)

# for i, result in enumerate(SearchResults):
#     print(f"{result}")

ResultLinks = list(SearchResults)

FilterPrompt = f"""Take a look at this list of URLs of news articles, and filter it down to the most reliable 7 webpages based how trustable the news channel/journal or websites is : {ResultLinks}
*Instruction* : Do not return anything but the domain name of the news website that we should use. Do not use any formating on the list like this: ```python . I want plain text representing a python list that I can directly use with the eval function to make it into a real list. """
FilterResponse = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=FilterPrompt)

print(f"FilterResponse ::{FilterResponse.text}")
FilteredResponse = FilterResponse.text
FilteredResponse = FilteredResponse.replace("```python", "").replace("```", "").strip()

print(f"FilteredResponse ::{FilteredResponse}")

FilteredList = eval(FilteredResponse)  
DomainMap =build_domain_url_map(FilteredList, ResultLinks)
DomainBulletinMap = {}
domains = DomainMap.keys()

for domain in domains:
    prompt = f"""Please read through the news article on this website and summarise it in bullet points with clear details of every aspect: {DomainMap[domain][0]}"""
    newsbulletins = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt)
    DomainBulletinMap[domain]=newsbulletins.text

combined_news = """"""

for k,v in DomainBulletinMap.items():
    combined_news += f"{k} :: \n {v} \n\n"

prompt = f"""I have collected a list of summaries about a news piece from mutiple news website. Please review this text and point out where does websites converge to the news (which all parts majority of them agree with), then point out where does the news articles diverge from each other. Here's the summary: \n\n {combined_news}"""
news_summary = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt)

print(news_summary.text)
