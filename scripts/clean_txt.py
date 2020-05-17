import pandas as pd

from datetime import datetime, timedelta

from utils.url import clean_url, get_root_url


with open('data/links.txt') as f:
    lines = f.readlines()

cleaned_lines = ''.join(lines).split('@s@')[1:]
data = []
datum = []
i = 0
for j, line in enumerate(cleaned_lines):
    print('.', end = '')
    datum.append(line)
    i += 1
    if i == 3:
        if 'http' not in datum[0]:
            print('Error 1 @ {}'.format(j))
            import pdb
            pdb.set_trace()
        if 'http' in datum[2]:
            print('Error 2 @ {}'.format(j))
            import pdb
            pdb.set_trace()
        data.append(datum)
        i = 0
        datum = []

df = pd.DataFrame(data)
df.columns = ['url', 'title', 'summary']
df['domain'] = df['url'].apply(clean_url).apply(get_root_url)
df = df.reset_index()
ix = df.shape[0]
df['date'] = df['index'].apply(lambda i: str((datetime.now() - timedelta(days=(ix - i))).date()))
df.drop('index', axis=1, inplace=True)
df['liked'] = 1
df.to_csv('data/links.csv', index=False)
