# TODO: DRY with utils/url.py

from urllib.parse import urlparse

def clean_url(url):
    if 'http' not in url:
        return 'http:' + url
    else:
        url = 'http' + url.split('http')[1]
        return url

def get_root_url(url):
    return urlparse(url).netloc
