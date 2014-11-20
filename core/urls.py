from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DEBUG:
	urlpatterns = patterns('core.views',
	    url(r'^$', 'dashboard'),
	    url(r'^login$', 'login'),
	    url(r'^logout$', 'logout'),
	    url(r'^list$', 'avatar'),
        url(r'^profile/(?P<username>[^/]+)$', 'profile'),
	)
