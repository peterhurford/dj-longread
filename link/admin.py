from django.contrib import admin

from .models import Link


class LinkAdmin(admin.ModelAdmin):
    search_fields = ('title', 'summary', 'category', 'aggregator')


admin.site.register(Link, LinkAdmin)
