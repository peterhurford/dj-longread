import psycopg2

from datetime import datetime

import pandas as pd

from utils.sql import table_exists, drop_table, escape, enquote, add_row, delete_row, find_row


# DRY with ingest/aggregate_feeds.py
ALL_COLS = ['id', 'url', 'title', 'summary', 'domain', 'added', 'modified',
            'liked', 'category', 'aggregator']


def add_link_row(cur, content):
    add_row(cur,
            'link_link',
            ['title', 'url', 'aggregator', 'added', 'modified'],
            [enquote(c) for c in content + [str(datetime.now())] * 2])
    return None


def delete_link_row(cur, url):
    delete_row(cur, 'link_link', 'url', enquote(url))
    return None


def find_link_row(cur, url):
    result = find_row(cur, 'link_link', 'url', url, n='many')
    if result:
        return [dict(zip(ALL_COLS, r)) for r in result]
    else:
        return []


print('Psycopg2 connect')
conn = psycopg2.connect('dbname=stanza_dev user=dbuser')
cur = conn.cursor()


print('Load onetab data')
with open('data/onetab.txt', 'r') as f:
    lines = f.readlines()


print('Upload links CSV to links table')
contents = []
for i, line in enumerate(lines):
    if '|' in line:
        linex = line.split(' | ')
        if len(linex) < 2:
            raise ValueError('{} was not a valid line'.format(line))
        url = linex[0]
        title = linex[1]
        contents.append([title.replace('\n', ''), url, 'Custom'])
    else:
        raise ValueError('{} was not a valid line'.format(line))


# TODO: DRY with ingest/aggregate_feeds.py
print('Psycopg2 connect')
conn = psycopg2.connect('dbname=stanza_dev user=dbuser')
cur = conn.cursor()
lines = len(contents)
for i, content in enumerate(contents):
    if i % 10 == 0:
        print('{}/{}'.format(i, lines))

    result = find_link_row(cur, content[1])

    if len(result) == 0:
        add_link_row(cur, content)
    elif len(result) > 1:
        delete_link_row(cur, content[1])
        add_link_row(cur, content)
    elif str(result[0]['added'].date()) == '2020-01-01':
        delete_link_row(cur, content[1])
        add_link_row(cur, content)

    result = find_link_row(cur, content[1])
    if len(result) == 0:
        print('FATAL ERROR 1')
        import pdb
        pdb.set_trace()

    if len(result) > 1:
        print('FATAL ERROR 2')
        import pdb
        pdb.set_trace()

cur.close()
conn.commit()
conn.close()
print('Done')

