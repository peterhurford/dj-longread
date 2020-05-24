from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.utils import timezone

from link.models import Link, Upcoming
from link.forms import LinkForm

from .utils.url import clean_url, get_root_url


class LinkDetailView(DetailView):
    model = Link

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LinkListView(ListView):
    model = Link
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LinkCreate(CreateView):
    model = Link
    fields = ['url', 'title', 'summary', 'liked', 'category', 'aggregator']

    def form_valid(self, form):
        form.instance.date = timezone.now()
        form.instance.domain = get_root_url(clean_url(form.instance.url)) 
        return super().form_valid(form)

    def create(self, *args, **kwargs):
        self.date = timezone.now()
        self.domain = get_root_url(clean_url(self.url)) 
        return super().create(*args, **kwargs)


class UpcomingDetailView(DetailView):

    model = Upcoming

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpcomingListView(ListView):
    model = Upcoming
    paginate_by = 13

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpcomingDelete(DeleteView):
    model = Upcoming
    success_url = reverse_lazy('upcoming-list')

    def delete(self, request, *args, **kwargs):
        upcoming = Upcoming.objects.get(pk=kwargs['pk'])
        domain = get_root_url(clean_url(upcoming.url)) 
        date = timezone.now()
        link = Link(url=upcoming.url,
                    title=upcoming.title,
                    summary='',
                    domain=domain,
                    date=date,
                    liked=0,
                    category='',
                    aggregator=upcoming.aggregator)
        link.save()
        return super().delete(request, *args, **kwargs)

