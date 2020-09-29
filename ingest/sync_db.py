import os
import boto3
import argparse


parser = argparse.ArgumentParser(description='Sync DB with S3.')
parser.add_argument('--mode', metavar='M', type=str, help='up(load) or down(load)')
args = parser.parse_args()
mode = args.mode


ACCESS_KEY = os.environ['AWS_ACCESS_KEY_ID']
SECRET_KEY = os.enivron['AWS_SECRET_KEY']
BUCKET = 'jeffreyrunner'


if mode == 'up':
	print('Uploading data/export.csv to S3...')
	s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
					  aws_secret_access_key=SECRET_KEY)
	s3.upload_file('data/export.csv', BUCKET, 'djlongread_db_export.csv')
elif mode == 'down':
	print('Uploading data/export.csv to S3...')
	s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
					  aws_secret_access_key=SECRET_KEY)
	with open('data/export.csv', 'wb') as f:
		s3.download_fileobj(BUCKET, 'djlongread_db_export.csv', f)
else:
	raise ValueError('mode not recognized... must be `up` or `down`')


print('...Done')
