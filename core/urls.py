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
	    url(r'^avatar$', 'avatar'),
        url(r'^profile/(?P<username>[^/]+)$', 'profile'),
        url(r'^addfriend/(?P<username>[^/]+)$', 'addfriend'),
        url(r'^unfriend/(?P<username>[^/]+)$', 'unfriend'),
        url(r'^post_update/(?P<goal>[^/]+)$', 'post_update'),
        url(r'^add_actionitem/(?P<goalgroup>[^/]+)$', 'add_actionitem'),
        url(r'^add_goal$', 'add_goal'),
        url(r'^delete_goal/(?P<goal>[^/]+)$', 'delete_goal'),
        url(r'^delete_goal/(?P<goal>[^/]+)/(?P<neworder_num>[^/]+)$', 'flip_goals'),
        url(r'^add_friendpoint/(?P<goal>[^/]+)$', 'add_friendpoint'),
        url(r'^add_comment/(?P<update>[^/]+)$', 'add_comment'),
        url(r'^delete_goalgroup/(?P<goalgroup>[^/]+)$', 'delete_goalgroup'),
	)
