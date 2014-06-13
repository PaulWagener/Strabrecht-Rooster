from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'strabrecht.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'rooster.views.index'),
    url(r'^sources\.json$', 'rooster.views.sources'),
    url(r'^admin/', include(admin.site.urls)),
)
