import os
import sys

sys.path.append('/var/www/sems/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sems.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
