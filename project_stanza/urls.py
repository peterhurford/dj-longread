from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from link import views


urlpatterns = [
    path('', views.UpcomingListView.as_view(), name='upcoming-list'),
    path('links/', views.LinkListView.as_view(), name='link-list'),
    path('links/add_link.html', views.get_link, name='add-link'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
