from django.contrib import admin

from .models import Link, Upcoming


class LinkAdmin(admin.ModelAdmin):
    search_fields = ('title', 'summary', 'category', 'aggregator')


class UpcomingAdmin(admin.ModelAdmin):
    search_fields = ('title', 'aggregator')


admin.site.register(Link, LinkAdmin)
admin.site.register(Upcoming, UpcomingAdmin)
