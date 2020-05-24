from django.db import models
from django.urls import reverse


class Link(models.Model):
    url = models.CharField(max_length=2000)
    title = models.CharField(max_length=2000)
    summary = models.CharField(max_length=10000, blank=True, null=True)
    domain = models.CharField(max_length=2000)
    date = models.DateTimeField('date added')
    liked = models.IntegerField(default=0)
    category = models.CharField(max_length=2000)
    aggregator = models.CharField(max_length=2000)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('upcoming-list')


class Upcoming(models.Model):
    url = models.CharField(max_length=2000)
    title = models.CharField(max_length=2000)
    aggregator = models.CharField(max_length=2000)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('upcoming-list')

