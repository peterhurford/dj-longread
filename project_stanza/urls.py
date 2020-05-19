from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from link.views import LinkListView, UpcomingListView


urlpatterns = [
    path('', UpcomingListView.as_view(), name='upcoming-list'),
    path('links/', LinkListView.as_view(), name='link-list'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
