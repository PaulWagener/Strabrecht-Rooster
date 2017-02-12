from django.conf.urls import include, url
from rooster import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(teacher|room|group|student)/([a-zA-Z0-9_]+)\.(ics|json)$', views.events),
    url(r'^admin/', include(admin.site.urls)),
]