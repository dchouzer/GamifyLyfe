from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
	urlpatterns = patterns('core.views',
	    url(r'^$', 'dashboard'),
	    url(r'^login$', 'login'),
	    url(r'^logout$', 'logout'),
	    url(r'^list$', 'list'),
	)