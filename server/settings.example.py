from basesettings import *

# This is an example of settings that could be overridden. You can
# override more, but these are probably the ones you want to start
# with.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# where the map initially starts
MAP_DEFAULT_LATITUDE = 37.426
MAP_DEFAULT_LONGITUDE = -122.17054
MAP_DEFAULT_ZOOM = 15
MAP_DEFAULT_SATELITE = False


ADMINS = (
    ('behram mistree', 'bmistree@gmail.com'),
)
MANAGERS = ADMINS

DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = 'sessions.db'

# Make this unique, and don't share it with anybody. You MUST change this.
SECRET_KEY = '%5=mrbposk6qmf+y-4c5r-&mrqa(t*hpfkfl1fqmamq8!yuhm-'
