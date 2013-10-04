from django.conf.urls.defaults import patterns, include, url
import views;

from django.contrib import admin
# admin.autodiscover()
admin.site.login_template = 'webauth/admin_redirect.html'

urlpatterns = patterns(
    '',
    url(r'^$', 'views.index', name='index'),
    url(r'^add_links$','views.add_links',name='add_links'),
    url(r'^add_links_no_user$','views.add_links_no_user',name='add_links_no_user'),
    url(r'^get_updates$','views.get_updates',name='get_updates'),
    url(r'^webauth/', include('webauth.urls')), 
)

