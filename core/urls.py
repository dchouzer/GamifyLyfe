from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DEBUG:
	urlpatterns = patterns('core.views',
	    url(r'^$', 'home'),
	    url(r'^dashboard$', 'dashboard'),
	    url(r'^login$', 'login'),
        url(r'^register$', 'register'),
	    url(r'^logout$', 'logout'),
	    url(r'^list$', 'avatar'),
        url(r'^profile/(?P<username>[^/]+)$', 'profile'),
        url(r'^addfriend/(?P<username>[^/]+)$', 'addfriend'),
        url(r'^unfriend/(?P<username>[^/]+)$', 'unfriend'),
        url(r'^post_update/(?P<goalgroup>[^/]+)$', 'post_update'),
	)
