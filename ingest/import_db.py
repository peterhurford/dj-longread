import os
import psycopg2

import pandas as pd

from utils.sql import import_db, fix_data_types


print('Psycopg2 connect...')
links = pd.read_csv('data/export.csv')
links = fix_data_types(links)
links.to_csv('data/export.csv', index=False)
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
import_db(conn)
conn.close()
