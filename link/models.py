from django.db import models
from django.urls import reverse


class Link(models.Model):
    url = models.CharField(max_length=2000, default='htpp://www.example.com')
    title = models.CharField(max_length=2000, default='Example')
    summary = models.CharField(max_length=10000, blank=True, null=True, default='')
    domain = models.CharField(max_length=2000, blank=True, null=True, default='example.com')
    date = models.DateTimeField('date added', blank=True, null=True)
    liked = models.IntegerField(blank=True, null=True, default=1)
    category = models.CharField(max_length=2000, blank=True, null=True, default='')
    aggregator = models.CharField(max_length=2000, default='')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('upcoming-list')
