import logging

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, ExpressionWrapper, FloatField
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.utils import timezone


from link.models import Link

from .utils.url import clean_url, get_root_url
from .config import PRIORITY_WEIGHT, TIME_WEIGHT, RANDOM_WEIGHT, AGGREGATOR_WEIGHTS


class LinkTweetListView(ListView):
    model = Link
    paginate_by = 500

    def get_queryset(self):
        queryset = (Link.objects.exclude(liked__isnull=True)
                                .exclude(liked__exact=0)
                                .exclude(liked__exact=-1)
                                .exclude(tweet__exact=0))
        url = self.request.GET.get('url')
        if url:
            queryset = queryset.filter(Q(url__icontains=url))
        title = self.request.GET.get('title')
        if title:
            queryset = queryset.filter(Q(title__icontains=title))
        aggregator = self.request.GET.get('aggregator')
        if aggregator:
            queryset = queryset.filter(Q(aggregator__icontains=aggregator))
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(Q(category__icontains=category))
        summary = self.request.GET.get('summary')
        if summary:
            queryset = queryset.filter(Q(summary__icontains=summary))
        before = self.request.GET.get('before')
        if before:
            before = datetime.strptime(before, '%d/%m/%y %H:%M:%S') # e.g., 18/09/19
            queryset = queryset.filter(Q(added__gte=before))
        after = self.request.GET.get('after')
        if after:
            after = datetime.strptime(after, '%d/%m/%y %H:%M:%S') # e.g., 18/09/19
            queryset = queryset.filter(Q(added__gte=after))
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

    context_object_name = 'link_tweet_list'
    template_name = 'link/tweet_list.html'


class LinkListView(ListView):
    model = Link
    paginate_by = 500

    def get_queryset(self):
        queryset = (Link.objects.exclude(liked__isnull=True)
                                .exclude(liked__exact=0)
                                .exclude(liked__exact=-1)
                                .exclude(tweet__exact=1)
                                .exclude(summary__isnull=True)
                                .exclude(summary__exact='')
                                .exclude(summary__exact='nan'))
        url = self.request.GET.get('url')
        if url:
            queryset = queryset.filter(Q(url__icontains=url))
        title = self.request.GET.get('title')
        if title:
            queryset = queryset.filter(Q(title__icontains=title))
        aggregator = self.request.GET.get('aggregator')
        if aggregator:
            queryset = queryset.filter(Q(aggregator__icontains=aggregator))
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(Q(category__icontains=category))
        summary = self.request.GET.get('summary')
        if summary:
            queryset = queryset.filter(Q(summary__icontains=summary))
        before = self.request.GET.get('before')
        if before:
            before = datetime.strptime(before, '%d/%m/%y %H:%M:%S') # e.g., 18/09/19
            queryset = queryset.filter(Q(added__gte=before))
        after = self.request.GET.get('after')
        if after:
            after = datetime.strptime(after, '%d/%m/%y %H:%M:%S') # e.g., 18/09/19
            queryset = queryset.filter(Q(added__gte=after))
        sort = self.request.GET.get('sort')
        if sort == 'random':
            queryset = queryset.order_by('seed', 'id')
        elif sort == 'diverse':
            queryset = queryset.order_by('aggregator', '-modified', 'id').distinct('aggregator')
        elif sort == 'oldest':
            queryset = queryset.order_by('modified', 'id')
        else:
            queryset = queryset.order_by('-modified', 'id')
            
        queryset = queryset.all()
        return queryset

    context_object_name = 'link_list'
    template_name = 'link/link_list.html'


class UpcomingListView(LoginRequiredMixin, ListView):
    model = Link
    paginate_by = 16
    login_url = 'admin/login'

    def get_context_data(self, **kwargs):
        context = super(UpcomingListView, self).get_context_data(**kwargs)
        today = datetime.today()
        today = datetime(today.year, today.month, today.day)
        context['total_count'] = (Link.objects.exclude(liked__exact=0)
                                              .exclude(liked__exact=1)
                                              .count())
        context['read_count'] = (Link.objects.exclude(liked__isnull=True)
                                             .filter(modified__gte=today)
                                             .count())
        context['liked_count'] = (Link.objects.exclude(liked__isnull=True)
                                              .filter(modified__gte=today)
                                              .exclude(liked__exact=0)
                                              .count())
        return context

    def get_queryset(self):
        queryset = Link.objects.filter(liked__isnull=True)
        url = self.request.GET.get('url')
        if url:
            queryset = queryset.filter(Q(url__icontains=url))
        title = self.request.GET.get('title')
        if title:
            queryset = queryset.filter(Q(title__icontains=title))
        aggregator = self.request.GET.get('aggregator')
        if aggregator:
            queryset = queryset.filter(Q(aggregator__icontains=aggregator))
        before = self.request.GET.get('before')
        if before:
            before = datetime.strptime(before, '%d/%m/%y') # e.g., 18/09/19
            queryset = queryset.filter(Q(added__lte=before))
        after = self.request.GET.get('after')
        if after:
            after = datetime.strptime(after, '%d/%m/%y') # e.g., 18/09/19
            queryset = queryset.filter(Q(added__gte=after))
        sort = self.request.GET.get('sort')
        if sort == 'recent':
            queryset = queryset.order_by('-added', 'id')
        elif sort == 'oldest':
            queryset = queryset.order_by('added', 'id')
        elif sort == 'random':
            queryset = queryset.order_by('seed', 'id')
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
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator', 'tweet']
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
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator', 'tweet']
    template_name_suffix = '_update_form'
    login_url = 'admin/login'

    def get_success_url(self):
        get_ = self.request.GET
        url = get_.get('url', '')
        title = get_.get('title', '')
        aggregator = get_.get('aggregator', '')
        page = get_.get('page')
        sort = get_.get('sort')
        before = get_.get('before')
        after = get_.get('after')
        return '/?url={}&title={}&aggregator={}&before={}&after={}&page={}&sort={}'.format(url, title, aggregator, before, after, page, sort)

    def form_valid(self, form):
        if not form.instance.liked:
            form.instance.liked = 0
            logging.info('Deleted "{}"'.format(form.instance.title))
        else:
            logging.info('Liked "{}"'.format(form.instance.title))

        form.instance.modified = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

