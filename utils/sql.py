import io
import re
import csv
import warnings

import numpy as np
import pandas as pd

warnings.simplefilter(action='ignore', category=FutureWarning)


ALL_COLS = ['id', 'url', 'title', 'summary', 'domain', 'added', 'modified',
            'liked', 'category', 'aggregator', 'seed', 'tweet', 'starred']


def clean_str(txt):
    if not isinstance(txt, str):
        return txt
    txt = txt.replace('&nbsp;', '')
    txt = txt.replace('&ldquo;', '"')
    txt = txt.replace('&rdquo;', '"')
    txt = txt.replace('&lsquo;', '\'')
    txt = txt.replace('&rsquo;', '\'')
    txt = txt.replace('&mdash;', '-')
    txt = txt.replace('&ndash;', '-')
    for i in range(10):
        txt = txt.replace('"""', '"')
        txt = txt.replace('\'\'\'', '\'')
    txt = txt.replace('n"t', 'n\'t')
    txt = txt.replace('n""t', 'n\'t')
    return txt


def clean_links(links):
    links.columns = ALL_COLS
    links = links[links['id'].notnull()]   # Drop empty column
    links['id'] = links['id'].astype(int)  # Fix float ID issue
    links['seed'] = links['seed'].astype(float).fillna(0)
    links['tweet'] = links['tweet'].apply(lambda x: 0 if (str(x) == '\\N' or str(x) == '') else str(x).split('.')[0]).astype(float)
    links['liked'] = links['liked'].apply(lambda x: np.nan if (str(x) == '\\N' or str(x) == '') else str(x).split('.')[0]).astype(float)
    for var in ['url', 'title', 'summary', 'domain', 'category', 'aggregator']:
        links[var] = links[var].apply(clean_str)
    links['title'] = links['title'].fillna('')
    links['liked'] = links['liked'].fillna(np.nan)
    return links.sort_values('id')


def clean_input(val):
    if np.issubdtype(type(val), np.integer) or np.issubdtype(type(val), np.floating) or isinstance(val, float):
        return int(val)
    else:
        return str(val)


def table_exists(cur, table_name):
    cur.execute('SELECT * FROM information_schema.tables WHERE table_name=%s', (table_name,))
    return cur.rowcount >= 1


def drop_table(cur, table_name):
    if table_exists(cur, table_name):
        cur.execute(f'DROP TABLE {table_name}')
    else:
        ValueError(f'{table_name} not found')
    return None


def add_row(cur, table_name, column_names, row):
    query = 'INSERT INTO {} ({}) VALUES ({})'.format(
                table_name,
                    ', '.join(column_names),
                        ', '.join(['%s' for _ in row])
                        )
    cur.execute(query, row)
    return None


def delete_row(cur, table_name, column_name, value):
    cur.execute('DELETE FROM {} WHERE {} = %s'.format(table_name, column_name), (value,))
    return None


def update_row(cur, table_name, set_col, set_val, where_col, where_val):
    set_val = clean_input(set_val)
    where_val = clean_input(where_val)
    cur.execute('UPDATE {} SET {} = %s WHERE {} = %s'.format(table_name, set_col, where_col), (set_val, where_val))
    return None


def find_row(cur, table_name, col, value, n=1):
    cur.execute('SELECT * FROM %s WHERE %s = %%s', (table_name, col, value))
    if n == 1:
        return cur.fetchone()
    elif n == 'many':
        return cur.fetchall()
    else:
        return ValueError('n must be 1 or many')


def export_db(cur, outfile='data/export.csv', verbose=True):
    with open(outfile, 'w') as f:
        if verbose:
            print('...Downloading')
        # Ideally we would just copy directly, but Heroku permissions don't allow that
        # so we have to hack around with StringIO
        data_io = io.StringIO()
        cur.copy_to(data_io, 'link_link', sep=',')
        data_io.seek(0)
        content = data_io.read()
        if content == '':
            blank_db = True
        else:
            blank_db = False
            content = content.split('\n')
            # Use re.split to ignore escaped commas
            content = [re.split('(?<!\\\\),', c) for c in content]
            writer = csv.writer(f, delimiter=',')
            writer.writerows(content)
    if verbose:
        print('...Formatting')
    if blank_db:
        links = None
    else:
        links = pd.read_csv(outfile,
                          names=['id', 'title', 'url', 'aggregator', 'added', 'modified', 
                                'seed', 'starred', 'liked', 'read', 'viewed', 'meta', 'score'],
                          dtype='str',
                          na_values='\\N')
        
        links = links.dropna(subset=['id'])
        links['id'] = links['id'].astype(float).astype(int)
        
        numeric_cols = ['seed', 'starred', 'liked', 'read', 'viewed', 'score']
        for col in numeric_cols:
            links[col] = pd.to_numeric(links[col], errors='coerce')
            
        clean_links(links).to_csv(outfile, index=False)
    return links


def import_db(conn, infile='data/export.csv', verbose=True):
    data_io = io.StringIO()
    df = clean_links(pd.read_csv(infile))
    df['modified'] = df['modified'].fillna(df['added'])
    df['aggregator'] = df['aggregator'].fillna('Unknown')
    df.to_csv(data_io, index_label='id', header=False, index=False, na_rep='\\N')
    data_io.seek(0)
    cur = conn.cursor()
    if verbose:
        print('...Clearing table')
    cur.execute('DELETE FROM link_link')
    if verbose:
        print('...Importing to PSQL')
    cur.copy_from(data_io, 'link_link', sep=',')
    conn.commit()
    cur.close()
    return None
