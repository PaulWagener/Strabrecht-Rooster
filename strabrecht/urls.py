from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rooster.views.index'),
    url(r'^(teacher|room|group|student)/([a-zA-Z0-9_]+)\.(ics|json)$', 'rooster.views.events'),
    url(r'^admin/', include(admin.site.urls)),

)