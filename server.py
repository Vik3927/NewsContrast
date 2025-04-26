from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from google import genai
from googlesearch import search
from utils import build_domain_url_map

# Load configuration
env_loaded = load_dotenv()
app = Flask(__name__)
CORS(app)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Gemini client
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

@app.route('/summarize')
def summarize():
    url = request.args.get('url')
    logger.info(f"Received URL: {url}")

    # 1. Prompt to generate search query
    prompt = f"""
If I share a webpage URL would you be able to fetch me its content? If yes, read content from this website and create a search text that I can use on google.com to search and read more about this news article. Return only the search text. Here's the URL: 
{url}
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    SearchQuery = response.text.strip()
    logger.info(f"Search query: {SearchQuery}")

    # 2. Retrieve Google search results
    results = list(search(SearchQuery, num_results=15))
    logger.info(f"Fetched {len(results)} search results")

    # 3. Filter down to 7 trusted domains
    filter_prompt = f"""
Take a look at this list of URLs of news articles, and filter it down to the most reliable 7 webpages based how trustable the news channel/journal or websites is : {results}
*Instruction* : Do not return anything but the domain name of the news website that we should use. Do not use any formating on the list like this: 
python . I want plain text representing a python list that I can directly use with the eval function to make it into a real list.
"""
    filter_resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=filter_prompt
    )
    filtered_text = filter_resp.text.replace('```python', '').replace('```', '').strip()
    domains = eval(filtered_text)
    logger.info(f"Trusted domains: {domains}")

    # 4. Map each domain to its first URL
    domain_map = build_domain_url_map(domains, results)
    logger.info(f"Domain map entries: {len(domain_map)}")

    # 5. Summarize articles per domain
    bullet_map = {}
    for domain, links in domain_map.items():
        logger.info(f"Summarizing {domain}")
        bullet_prompt = f"Please read and summarize in bullet points for all the fine details: {links[0]}"
        bullet_resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=bullet_prompt
        )
        bullet_map[domain] = bullet_resp.text.strip()
        logger.info(f"Received {domain} summary ({len(bullet_map[domain])} chars)")

    # 6. Combine bullets and generate final summary
    combined = "".join([f"## {d}\n{t}\n\n" for d, t in bullet_map.items()])
    final_prompt = f"""
I have collected bullet summaries from various news websites. Point out where they converge (majority agreement) and where they diverge, also present a generalised summary and an advise for the reader based on your convergence and divergence analysis. Mention any bias that you detect with any of the news reporting. Here are the summaries:
{combined}
"""
    summary_resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=final_prompt
    )
    logger.info("Generated final summary")

    return jsonify({'markdown': summary_resp.text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)