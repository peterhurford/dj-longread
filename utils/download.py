import gzip

from os import path
from bs4 import BeautifulSoup
from urllib import request


def file_name_from_url(url):
    file_name = url.replace('/', '_').replace('-', '_').replace(':', '').replace('.', '_')
    file_name = file_name.replace('http__', '').replace('https__', '').replace('www_', '')
    file_name = ''.join([c for c in file_name][0:100])
    return file_name


def read(url, return_type='text', reader_type='lxml'):
    error = False
    output = None
    response = None
    msg = 'no response'

    if not isinstance(url, str):
        msg = 'URL malformed'
        error = True
    elif 'pdf' in url:
        msg = 'is PDF'
        error = True
    elif 'youtube' in url:
        msg = 'is YouTube'
        error = True

    if not error:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}
        try:
            req = request.Request(url, headers=hdr)
            response = request.urlopen(req, timeout=10)
            msg = 'Success'
        except Exception as e:
            msg = str(e)
            error = True

        if response is not None and response.status != 200:
            msg = response.status
            error = True

    if not error:
        blacklist = [
            '[document]',
            'noscript',
            'header',
            'html',
            'meta',
            'head', 
            'input',
            'script',
            'style'
        ]
        try:
            content = response.read()
            if reader_type == 'gzip':
                content = gzip.decompress(content)
                reader_type = 'xml'
            soup = BeautifulSoup(content, features=reader_type)
        except Exception as e:
            msg = str(e)
            error = True
        if not error:
            output = ''
            text = soup.find_all(text=True)
            for t in text:
                if t.parent.name not in blacklist:
                    output += '{} '.format(t)

            if output == '':
                output = None
                error = True
                msg = 'Output malformed'
                # TODO: solution in this case is to ungzip
                # import gzip
                # gzip.decompress(content).decode('utf-8')

            if return_type == 'raw':
                output = content
            elif return_type == 'soup':
                output = soup
            elif return_type == 'list':
                output = text
            elif return_type == 'text':
                output = output

    return output, error, msg


def download(url, file_name):
    output, error, msg = read(url)
    if not error:
        with open(file_name, 'w') as text_file:
            text_file.write(output)
        msg = 'Success'

    return msg, error


def read_cache(file_name):
    file_name = 'data/extract/{}.txt'.format(file_name)
    if path.exists(file_name):
        with open(file_name, 'r') as text_file:
            return ' \n '.join(text_file.readlines())
    else:
        return None
