from urllib.parse import urlparse
from collections import defaultdict

def build_domain_url_map(allowed_domains, url_list):
    """
    Returns {domain: [urls …]} for URLs whose netloc matches an allowed domain
    (exactly or as a sub‑domain).  Non‑matching URLs are ignored.
    """
    # Normalise the allow‑list once
    allowed = {d.lower().strip() for d in allowed_domains}

    domain2urls = defaultdict(list)

    for url in url_list:
        try:
            host = urlparse(url).netloc.lower()
            host = host[4:] if host.startswith('www.') else host  # strip `www.`
        except Exception:
            continue  # skip malformed URLs

        # Check against every allowed domain (the list is small)
        for dom in allowed:
            if host == dom or host.endswith(f'.{dom}'):
                domain2urls[dom].append(url)
                break   # stop at first match

    return dict(domain2urls)   # drop domains that got no URLs


# ---------------- Example -----------------
allowed = [
    'economictimes.indiatimes.com', 'livemint.com', 'outlookbusiness.com',
    'moneycontrol.com', 'thehindu.com', 'businesstoday.in', 'economictimes.com'
]

sample_urls = [
    'https://economictimes.indiatimes.com/markets/stocks/news/…',
    'https://www.livemint.com/money/personal‑finance/…',
    'https://businesstoday.in/latest/economy/story/…',
    'https://foo.example.com/should/be/ignored',
    'https://www.economictimes.com/news/markets/…'
]

domain_map = build_domain_url_map(allowed, sample_urls)
