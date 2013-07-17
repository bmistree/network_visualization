from django.conf.urls.defaults import patterns, include, url
import views;

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'views.index', name='index'),
    url(r'^add_links$','views.add_links',name='add_links'),
    url(r'^get_updates$','views.get_updates',name='get_updates')
    
)

