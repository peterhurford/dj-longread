## Use Machine Learning to Read the Internet for You

There are too many articles on the internet to possibly read them all. We want to read the best. Luckily, text models have reached new heights in 2019. Let's see if we can harness this for good.

## Install

1. Run `make setup`
2. Install [postgres.app](https://postgresapp.com/downloads.html) - or figure out how to install
 postgres yourself
3. Make sure you got your Clang working `xcode-select --install`

Once you have postgres running, please also create a database called `stanza_dev` and a user:

 ```sql
 CREATE DATABASE stanza_dev;
 CREATE USER dbuser;
 ALTER USER dbuser WITH SUPERUSER;
 ```


## Run

```
make run
```
