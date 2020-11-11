## Use Machine Learning to Read the Internet for You

There are too many articles on the internet to possibly read them all. We want to read the best. Luckily, text models have reached new heights in 2019. Let's see if we can harness this for good.

## Install

1. Install [postgres.app](https://postgresapp.com/downloads.html) - or figure out how to install postgres yourself
2. Run `make setup`
3. Make sure you got your Clang working `xcode-select --install`
4. Once you have postgres running, please also create a database called `stanza_dev` and a user:

 ```sql
 CREATE DATABASE stanza_dev;
 CREATE USER dbuser;
 ALTER USER dbuser WITH SUPERUSER;
 ```

5. Run `env DEVELOPMENT=1 make migrate`
6. Run `env DEVELOPMENT=1 python manage.py createsuperuser`
7. [optional] Set up AWS S3 access, add env vars for `AWS_ACCESS_KEY_ID` and `AWS_SECRET_KEY`, and then download the data export CSV using `make importdb`.
8. Get latest data by running `make update`


## Run

```
make update
make run
```


## Deployment

Deployment is on Heroku. `heroku run make update` can manually update the list of articles.


## Debugging 

If you encounter `ValueError: Entering production with no SECRET_KEY`, you should either set a `SECRET_KEY` environment variable or set a `DEVELOPMENT=1` environment variable.

Set a `DEVELOPMENT=1` variable to see errors in local dev.


## Testing

There aren't any formal tests yet, but we hope all of the following commands work:

```
make exportdb
make update
make run
```

