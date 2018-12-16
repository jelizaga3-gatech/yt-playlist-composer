# yt-playlist-compiler
# Heroku Pains
`heroku run python manage.py migrate` to do a Heroku db migration.
## PostgreSQL pains
https://devcenter.heroku.com/articles/python-concurrency-and-database-connections

> If you’re using the dj-database-url module, this configuration is recommended:

```
import dj_database_url

DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
```
`dj-database-url==0.5.0` in (pip) requirements.txt 

