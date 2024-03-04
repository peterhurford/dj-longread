import boto3 # Fail fast if Python env is not properly loaded
import psycopg2

# Fail fast if psql is not properly loaded
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
psycopg2.connect(DATABASE_URL, sslmode='require')
