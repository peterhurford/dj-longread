import re

import numpy as np

from nltk.corpus import stopwords


def clean(txt):
    txt = txt.replace('&nbsp;', ' ')
    txt = txt.replace('&ldquo;', ' ')
    txt = txt.replace('&rdquo;', ' ')
    txt = txt.replace('&lsquo;', '\'')
    txt = txt.replace('&rsquo;', '\'')
    txt = txt.replace('&mdash;', ' ')
    txt = txt.replace('&ndash;', ' ')
    txt = txt.replace('&hellip;', ' ')
    txt = txt.replace('[...]', ' ')
    txt = txt.replace('[', ' ')
    txt = txt.replace(']', ' ')
    txt = txt.replace('www.', '')
    txt = txt.replace('.com', '')
    txt = txt.replace('.org', '')
    txt = txt.replace(u'\xa0', u' ')
    txt = txt.replace('\n', ' ')
    txt = txt.lower()
    return txt


def embed(text, embeddings_dict):
    blank = np.zeros(300)
    stop_words = stopwords.words('english')
    words = [w for w in re.split(r'\W+', text) if w not in stop_words and w != '']
    return np.mean(np.array([embeddings_dict.get(w, blank) for w in words]), axis=0)
