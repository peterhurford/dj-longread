import pandas as pd

from datetime import datetime

from utils.url import get_root_url, clean_url


def add_to_csv(links, url, title, aggregator, category, summary, label):
    new_link = {'url': url,
                'title': title,
                'summary': summary,
                'domain': get_root_url(clean_url(url)),
                'date': str(datetime.now().date()),
                'liked': label,
                'cluster': category,
                'aggregator': aggregator}
    new_link = pd.DataFrame([new_link])
    new_links = pd.concat((links, new_link))
    new_links = new_links.reset_index(drop=True)
    new_links.to_csv('data/links.csv', index=False)
    return new_links
