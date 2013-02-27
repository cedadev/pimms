from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.utils import error, warn

import sys
import os.path as op
from string import Template

here = op.dirname(__file__)

env.hosts = ['gdevine@puma.nerc.ac.uk']

# Defaults overridden in some tasks:
env.deployment = sys.prefix

def gitupdate():
    local("git add .")
    local("git add -u")
    local("git commit")
    local("git push")


def deploy():
    code_dir = '/home/gdevine/web/prod/pimms'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:gerarddevine/pimms.git %s" % code_dir)
    with cd(code_dir):
        run("pwd")
        run("ls -la")
        run("git pull")
        #run("touch app.wsgi")


def ceda_deployment(deployment='/pyEnv/ve/pimms'):
    """
    Specific deployment configuration for CEDA.

    """
    wsgi_path = deployment+'/lib64/python2.6/site-packages/pimms/resources'
    with settings(deployment=deployment,
                  apache_logdir='/pyEnv/log',
                  wsgi_path=wsgi_path,
                  ):
        wsgi()
        wsgi_conf()

def wsgi(filepath=None):
    """
    Create the wsgi script used for deployment.

    :param filepath: The path to write the resulting wsgi file to.
        This defaults to ./apache/pimms.wsgi

    """


    if filepath is None:
        filepath = op.join(here, 'apache/pimms.wsgi')


    wsgi_template = op.join(here, 'apache/pimms.wsgi.tmpl')
    write_template(wsgi_template, filepath,
                   DEPLOYMENT=env.deployment)


def wsgi_conf(filepath=None):
    """
    Create the apache configuration file for a wsgi deployment of PIMMS

    :filepath: The output file to write the configuration file

    """
    if filepath is None:
        filepath = op.join(here, 'apache/pimms_wsgi.conf')

    params = {
        'DEPLOYMENT': env.deployment,
        'LOG_DIR': env.apache_logdir,
        'PROJECT_WSGI': env.wsgi_path,
        }
    conf_template = op.join(here, 'apache/pimms_wsgi.conf.tmpl')
    write_template(conf_template, filepath, **params)



def tarball():
    local('python setup.py sdist')


def local_settings(db_password, filepath=None):
    if filepath is None:
        filepath = op.join(here, 'pimms/local_settings.py')

    # Make sure we don't clobber local settings
    if op.exists(filepath):
        warn('%s exists.  Please remove to recreate' % filepath)
        return

    params = {
        'ADMIN_NAME': env.admin_name,
        'ADMIN_EMAIL': env.admin_email,
        'SERVER_EMAIL': env.server_email,
        'DB_PASSWORD': db_password,
        'DB_HOST': env.db_host,
        'DB_PORT': env.db_port,
        }
    settings_template = op.join(here, 'pimms/local_settings.py.tmpl')
    write_template(settings_template, filepath, **params)

def write_template(template_file, output_file, **kwargs):
    t = Template(open(template_file).read())
    wsgi_src = t.substitute(kwargs)

    with open(output_file, 'w') as fh:
        fh.write(wsgi_src)
