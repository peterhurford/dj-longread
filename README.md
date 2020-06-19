## Use Machine Learning to Read the Internet for You

There are too many articles on the internet to possibly read them all. We want to read the best. Luckily, text models have reached new heights in 2019. Let's see if we can harness this for good.

## Install

1. Run `make setup`
2. Install [postgres.app](https://postgresapp.com/downloads.html) - or figure out how to install
 postgres yourself
3. Make sure you got your Clang working `xcode-select --install`
4. Once you have postgres running, please also create a database called `stanza_dev` and a user:

 ```sql
 CREATE DATABASE stanza_dev;
 CREATE USER dbuser;
 ALTER USER dbuser WITH SUPERUSER;
 ```

5. Run `make migrate`
6. Run `python manage.py createsuperuser`
7. [optional] Seed the DB by obtaining a data export CSV and [importing it into Postgres](https://www.postgresqltutorial.com/import-csv-file-into-posgresql-table/). Data export can be obtained with `make exportdb` from someone with a complete database.
8. Get latest data by running `make update`


## Run

```
make update
make run
```
