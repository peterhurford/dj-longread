import pandas as pd

from collections import Counter

from utils.download import download, file_name_from_url


links = pd.read_csv('data/links.csv')
urls = links['url'].values.tolist()

def download_urls(urls):
    log = {}
    for i, url in enumerate(urls):
        file_name = file_name_from_url(url)
        print('{}/{}: {}'.format(i + 1, len(urls), file_name))
        msg, error = download(url, 'data/extract/{}.txt'.format(file_name))
        print(msg)
        log[url] = msg
    return log

log = download_urls(urls)

import pdb
pdb.set_trace()
print(Counter(log.values()))
