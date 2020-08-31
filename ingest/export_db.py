import os
import psycopg2

import pandas as pd

from utils.sql import export_db


DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
export_db(cur)
conn.commit()
conn.close()
