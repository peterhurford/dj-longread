import os

import pandas as pd


ALL_COLS = ['id', 'url', 'title', 'summary', 'domain', 'added', 'modified',
            'liked', 'category', 'aggregator', 'seed']


def table_exists(cur, table_name):
    cur.execute('SELECT * FROM information_schema.tables WHERE table_name=%s', (table_name,))
    return cur.rowcount >= 1


def drop_table(cur, table_name):
    cur.execute('DROP TABLE {}'.format(table_name))
    return None


def escape(text):
    return text.replace('\'', '\'\'')

def enquote(text):
     return '\'' + escape(str(text)) + '\''


def add_row(cur, table_name, column_names, row):
     cur.execute('INSERT INTO {} {} VALUES {}'.format(table_name,
                                                      '(' + ', '.join(column_names) + ')',
                                                      '(' + ', '.join(row) + ')'))
     return None


def delete_row(cur, table_name, column_name, value):
    cur.execute('DELETE FROM {} WHERE {} = {}'.format(table_name, column_name, value))
    return None


def find_row(cur, table_name, col, value, n=1):
    cur.execute('SELECT * FROM {} WHERE {} = {}'.format(table_name, col, enquote(value)))
    if n == 1:
        return cur.fetchone()
    elif n == 'many':
        return cur.fetchall()
    else:
        return ValueError('n must be 1 or many')


def export_db(cur, outfile='data/export.csv', verbose=True):
    with open(outfile, 'r') as f:
        if verbose:
            print('...Downloading')
        path = os.path.abspath(outfile)
        copy_sql = 'COPY (SELECT * FROM link_link) TO \'{}\' WITH CSV;'.format(path)
        cur.copy_expert(copy_sql, f)

    if verbose:
        print('...Formatting')
    links = pd.read_csv(outfile)
    links.columns = ALL_COLS
    links.to_csv(outfile, index=False)
    return links

