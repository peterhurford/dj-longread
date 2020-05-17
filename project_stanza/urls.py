from django.contrib import admin
from django.urls import path
from link.views import LinkListView, UpcomingListView

urlpatterns = [
    path('', UpcomingListView.as_view(), name='upcoming-list'),
    path('links/', LinkListView.as_view(), name='link-list'),
    path('admin/', admin.site.urls),
]
