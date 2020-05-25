import psycopg2

from datetime import datetime

import pandas as pd

from utils.sql import table_exists, drop_table, escape, enquote, add_row


print('Psycopg2 connect')
conn = psycopg2.connect('dbname=stanza_dev user=dbuser')
cur = conn.cursor()


print('Load onetab data')
with open('data/onetab.txt', 'r') as f:
    lines = f.readlines()


print('Upload links CSV to links table')
for i, line in enumerate(lines):
    if '|' in line:
        linex = line.split(' | ')
        url = linex[0]
        title = linex[1]
        data = [enquote(url),
                enquote(title),
                enquote(str(datetime.now().date())),
                enquote(str(datetime.now().date())),
                enquote('Custom')]
        add_row(cur,
                'link_link',
                ['url', 'title', 'added', 'modified', 'aggregator'],
                data)

conn.commit()
print('Done')

