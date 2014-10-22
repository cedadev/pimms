#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pimms_site.settings")

    from django.core.management import execute_from_command_line

    # hack to prevent admin promt
    if  len(sys.argv) == 2 and sys.argv[1] == 'syncdb':
       sys.argv.append('--noinput')
    execute_from_command_line(sys.argv)
