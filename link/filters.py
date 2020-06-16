from link.models import Link
import django_filters

class LinkFilter(django_filters.FilterSet):
    class Meta:
        model = Link
        fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator']
