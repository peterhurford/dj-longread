import os
import psycopg2

import pandas as pd

from utils.sql import import_db


print('Psycopg2 connect...')
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
import_db(conn)
conn.close()
