import logging

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.utils import timezone

from link.models import Link

from .utils.url import clean_url, get_root_url


class LinkDetailView(DetailView):
    model = Link

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LinkListView(ListView):
    model = Link
    paginate_by = 5
    queryset = (Link.objects.exclude(liked__isnull=True)
                            .exclude(liked__exact=0)
                            .exclude(summary__isnull=True)
                            .exclude(summary__exact='')
                            .exclude(summary__exact='nan')
                            .order_by('benched', '-added'))
    context_object_name = 'link_list'
    template_name = 'link/link_list.html'


class UpcomingListView(ListView):
    model = Link
    paginate_by = 14
    queryset = Link.objects.filter(liked__isnull=True).order_by('benched', '-added')
    context_object_name = 'upcoming_list'
    template_name = 'link/upcoming_list.html'


class LinkCreate(CreateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator']

    def form_valid(self, form):
        form.instance.modified = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

    def create(self, *args, **kwargs):
        self.modified = timezone.now()
        self.domain = get_root_url(clean_url(self.url)) 
        return super().create(*args, **kwargs)


class LinkUpdate(UpdateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'benched', 'category', 'aggregator']
    template_name_suffix = '_update_form'

    def _is_bench_request(self):
        if not self.request:
            return False
        if not self.request.POST:
            return False
        if not self.request.POST.get('bench'):
            return False
        return self.request.POST['bench'] == '-'

    def form_valid(self, form):
        if self._is_bench_request():
            form.instance.benched = 1
            logging.info('Benched {}'.format(form.instance.title))
        elif not form.instance.liked:
            form.instance.liked = 0
            logging.info('Deleted {}'.format(form.instance.title))

        form.instance.modified = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)


    def update(self, request, *args, **kwargs):
        if not self.liked:
            self.liked = 0
        if not self.added or str(self.added.date()) == '2020-01-01':
            self.added = timezone.now()
        self.modified = timezone.now()
        self.domain = get_root_url(clean_url(self.url)) 
        return super().create(*args, **kwargs)

