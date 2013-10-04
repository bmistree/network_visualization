from django.conf.urls.defaults import *

urlpatterns = patterns('webauth.views',
    (r'^logout/$', 'logout'),
    (r'^login/$','login'),
    # usually disabled because unnecessary -- uncomment to test
    #(r'^whoami$','whoami'),
)