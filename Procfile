release: pip install -r requirements.txt && python manage.py migrate
web: gunicorn djlongread.wsgi --log-file -
