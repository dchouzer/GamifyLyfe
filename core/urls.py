from django.conf.urls import patterns, include, url

urlpatterns = patterns('core.views',
    url(r'^$', 'dashboard'),
    url(r'^login$', 'login'),
    url(r'^logout$', 'logout'),
)
