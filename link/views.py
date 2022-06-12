import logging

import numpy as np

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, ExpressionWrapper, FloatField
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.utils import timezone


from link.models import Link

from .utils.url import clean_url, get_root_url
from .config import PRIORITY_WEIGHT, TIME_WEIGHT, RANDOM_WEIGHT, AGGREGATOR_WEIGHTS

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logger.info('Logger is on')


class CustomListViewMixin(ListView):
    model = Link
    paginate_by = 500

    def _get_queryset_part(self, queryset, var_name):
        var = self.request.GET.get(var_name)
        if var:
            if var.startswith('-'):
                var = var[1:]
                queryset = queryset.exclude(Q(**{ var_name + '__icontains': var }))
            else:
                queryset = queryset.filter(Q(**{ var_name + '__icontains': var }))
        return queryset

    def _process_queryset(self, queryset):
        for var in ['url', 'title', 'aggregator', 'category', 'summary']:
            queryset = self._get_queryset_part(queryset, var)

        before = self.request.GET.get('before')
        if before:
            try:
                before = datetime.strptime(before, '%Y-%d-%m %H:%M:%S') # e.g., 2021-05-31
                queryset = queryset.filter(Q(added__lte=before))
            except ValueError:
                pass
        after = self.request.GET.get('after')
        if after:
            try:
                after = datetime.strptime(after, '%Y-%d-%m %H:%M:%S')
                queryset = queryset.filter(Q(added__gte=after))
            except ValueError:
                pass

        starred = self.request.GET.get('starred')
        if str(starred) == '1':
            queryset = queryset.filter(Q(starred=1))

        sort = self.request.GET.get('sort')
        if sort == 'random':
            queryset = queryset.order_by('?')
        elif sort == 'diverse':
            queryset = queryset.order_by('aggregator', '-modified', 'id').distinct('aggregator')
        elif sort == 'oldest':
            queryset = queryset.order_by('modified', 'id')
        else:
            queryset = queryset.order_by('-modified', 'id')
            
        queryset = queryset.all()
        return queryset


class LinkTweetListView(CustomListViewMixin):
    context_object_name = 'link_tweet_list'
    template_name = 'link/tweet_list.html'

    def get_queryset(self):
        queryset = (Link.objects.filter(tweet=1)
                                .exclude(liked__isnull=True)
                                .exclude(liked__exact=0)
                                .exclude(liked__exact=-1))
        return self._process_queryset(queryset)


class LinkListView(CustomListViewMixin):
    def get_queryset(self):
        queryset = (Link.objects.exclude(liked__isnull=True)
                                .exclude(summary__isnull=True)
                                .exclude(summary__exact='')
                                .exclude(summary__exact='nan'))
        return self._process_queryset(queryset)

    context_object_name = 'link_list'
    template_name = 'link/link_list.html'


class UpcomingListView(LoginRequiredMixin, CustomListViewMixin):
    model = Link
    paginate_by = 16
    login_url = 'admin/login'

    def get_context_data(self, **kwargs):
        context = super(UpcomingListView, self).get_context_data(**kwargs)
        today = datetime.today()
        today = datetime(today.year, today.month, today.day)
        queryset = self._process_queryset(Link.objects)
        context['total_count'] = (queryset.exclude(liked__exact=1)
                                          .exclude(liked__exact=0)
                                          .exclude(liked__exact=-1)).count()
        context['read_count'] = (queryset.exclude(liked__isnull=True)
                                                  .filter(modified__gte=today)
                                                  .count())
        context['liked_count'] = (queryset.exclude(liked__isnull=True)
                                                   .filter(modified__gte=today)
                                                   .exclude(liked__exact=0)
                                                   .exclude(liked__exact=-1)
                                                   .count())
        return context

    def get_queryset(self):
        queryset = (Link.objects.exclude(liked__exact=1)
                                .exclude(liked__exact=0)
                                .exclude(liked__exact=-1))
        queryset = self._process_queryset(queryset)

        sort = self.request.GET.get('sort')
        if sort == 'recent':
            queryset = queryset.order_by('-added', 'id')
        elif sort == 'oldest':
            queryset = queryset.order_by('added', 'id')
        elif sort == 'random':
            queryset = queryset.order_by('?')
        elif sort == 'diverse':
            queryset = queryset.order_by('seed', 'aggregator', '-added')
        elif sort == 'diverserecent':
            queryset = queryset.order_by('seed', '-added')
        elif sort == 'diverseoldest':
            queryset = queryset.order_by('seed', 'added')
        else:
            queryset = (queryset.annotate(priority=AGGREGATOR_WEIGHTS)
                        .annotate(total_priority=ExpressionWrapper((1 + (F('priority') / float(PRIORITY_WEIGHT))) +
                                                                   (F('id') / (float(TIME_WEIGHT) * 100)) +
                                                                   (F('seed') / float(RANDOM_WEIGHT)),
                                  output_field=FloatField()))
                        .order_by('-total_priority', 'id'))
        queryset = queryset.all()
        return queryset

    context_object_name = 'upcoming_list'
    template_name = 'link/upcoming_list.html'


class LinkCreate(LoginRequiredMixin, CreateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator', 'tweet', 'starred']
    login_url = 'admin/login'

    def form_valid(self, form):
        form.instance.modified = timezone.now()
        form.instance.added = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

    def create(self, *args, **kwargs):
        self.modified = timezone.now()
        self.added = timezone.now()
        self.domain = get_root_url(clean_url(self.url)) 
        return super().create(*args, **kwargs)


class LinkUpdate(LoginRequiredMixin, UpdateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator', 'tweet', 'starred']
    template_name_suffix = '_update_form'
    login_url = 'admin/login'

    def get_success_url(self):
        get_ = self.request.GET
        url = get_.get('url', '')
        title = get_.get('title', '')
        aggregator = get_.get('aggregator', '')
        page = get_.get('page', '')
        sort = get_.get('sort', '')
        before = get_.get('before', '')
        after = get_.get('after', '')
        starred = get_.get('starred', '')
        return '/?url={}&title={}&aggregator={}&before={}&after={}&page={}&sort={}&starred={}'.format(url, title, aggregator, before, after, page, sort, starred)

    def form_valid(self, form):
        if not form.instance.liked or np.isnan(form.instance.liked):
            if self.request.POST.get('bin') == '-':
                form.instance.liked = -1
                form.instance.tweet = 0
                logger.info('Binned "{}"'.format(form.instance.title))
            elif self.request.POST.get('star') == '*':
                form.instance.starred = 1
                logger.info('Starred "{}"'.format(form.instance.title))
            elif self.request.POST.get('star') == 'v':
                form.instance.starred = 0
                logger.info('Unstarred "{}"'.format(form.instance.title))
            else:
                form.instance.liked = 0
                form.instance.tweet = 0
                logger.info('Deleted "{}"'.format(form.instance.title))
        elif form.instance.liked == 1:
            logger.info('Liked "{}"'.format(form.instance.title))
        elif form.instance.liked == 0:
            logger.info('Binned "{}"'.format(form.instance.title))
        elif form.instance.liked == -1:
            logger.info('Binned "{}"'.format(form.instance.title))
        else:
            logger.error('ERROR UNKNOWN like = `{}`'.format(form.instance.liked))

        form.instance.modified = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

