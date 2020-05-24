from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render

from link.models import Link, Upcoming
from link.forms import LinkForm

def get_link(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/links')
    else:
        form = LinkForm()
    return render(request, 'link/add_link.html', {'form': form})


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


# TODO: Implement
class LinkCreate(CreateView):
    model = Link


class UpcomingDetailView(DetailView):

    model = Upcoming

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpcomingListView(ListView):
    model = Upcoming
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpcomingDelete(DeleteView):
    model = Upcoming
    success_url = reverse_lazy('upcoming-list')

    def delete(self, *args, **kwargs):
		# TODO: Log in links DB
        return super().delete(*args, **kwargs)
