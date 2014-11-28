from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


admin.autodiscover()

urlpatterns = patterns('',
   url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   url(r'^admin/', include(admin.site.urls)),
   url(r'', include('social_auth.urls')),
   (r'^accounts/login/$', 'django.contrib.auth.views.login',
   {'template_name': 'core/django-login.html'}),
   url(r'^beers/', include('beers.urls')),
   url(r'^core/', include('core.urls')), 
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
