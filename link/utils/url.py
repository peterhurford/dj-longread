from urllib.parse import urlparse

def clean_url(url):
    url = 'http' + url.split('http')[1]
    return url

def get_root_url(url):
    return urlparse(url).netloc
