from django.views.generic.list import ListView

from link.models import Link, Upcoming


class LinkListView(ListView):
    model = Link
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpcomingListView(ListView):
    model = Upcoming
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
