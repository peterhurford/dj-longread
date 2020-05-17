from django.db import models


class Links(models.Model):
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=2000)
    domain = models.CharField(max_length=200)
    date = models.DateTimeField('date added')
    linked = models.IntegerField(default=0)
    category = models.CharField(max_length=200)
    aggregator = models.CharField(max_length=200)


class Upcoming(models.Model):
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    aggregator = models.CharField(max_length=200)

