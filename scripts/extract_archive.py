import pandas as pd

from utils.download import read


ll = []
for page in range(1, 154):
    print('Page {}...'.format(page))
    content, error, message = read('http://sebastianmarshall.com/page/{}'.format(page), return_type='soup')
    if error:
        print(message)
    else:
        content = [c.find_all('a') for c in content.find_all('h2')]
        content = [str(c).split('"')[1:] for c in content if c != []]
        content = [['Archives', c[0], c[1].replace('</a>]', '').replace('>', '')] for c in content]
        ll += content


ll = sum(ll, [])
tmp2 = pd.DataFrame(ll, columns=['aggregator', 'title', 'url'])
tmp = pd.read_csv('data/tmp.csv')
tmp2 = pd.concat((tmp, tmp2))

import pdb
pdb.set_trace()
tmp2.tail()
tmp2.to_csv('data/tmp.csv', index=False)
