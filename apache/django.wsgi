# This application object is used by the development server
# as well as any WSGI server configured to use this file.
#
# See http://jmoiron.net/blog/deploying-django-mod-wsgi-virtualenv/


import os
import sys
import site

vepath = '/home/gdevine/web/prod/pimms/venv/lib/python2.6/site-packages'

# Remember original sys.path.
prev_sys_path = list(sys.path)

# add the site-packages of our virtualenv as a site dir
site.addsitedir(vepath)

# Add each new site-packages directory.
for directory in vepath:
  site.addsitedir(directory)

# add the app's directory to the PYTHONPATH
sys.path.append('/home/gdevine/web/prod/pimms')
sys.path.append('/home/gdevine/web/prod/pimms/pimms')

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

for x in sys.path:
    print x

# import from down here to pull in possible virtualenv django install
os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()



