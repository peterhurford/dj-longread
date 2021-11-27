from datetime import datetime

from django.db import models
from django.urls import reverse


DEFAULT_TIME = datetime(1900, 1, 1, 0, 0, 0, 0)


class Link(models.Model):
    url = models.CharField(max_length=2000, default='http://www.example.com')
    title = models.CharField(max_length=2000, default='Example')
    summary = models.CharField(max_length=10000, blank=True, null=True, default='')
    domain = models.CharField(max_length=2000, blank=True, null=True, default='example.com')
    added = models.DateTimeField('date added', default=DEFAULT_TIME)
    modified = models.DateTimeField('date modified', default=DEFAULT_TIME)
    liked = models.FloatField(blank=True, null=True, default=-1)
    category = models.CharField(max_length=2000, blank=True, null=True, default='')
    aggregator = models.CharField(max_length=2000, default='Custom')
    seed = models.FloatField(blank=True, null=True, default=1)
    tweet = models.FloatField(blank=True, null=True, default=0)
    starred = models.FloatField(blank=True, null=True, default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('upcoming-list')

