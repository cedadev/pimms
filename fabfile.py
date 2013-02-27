from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

import os.path as op
from string import Template

here = op.dirname(__file__)

env.hosts = ['gdevine@puma.nerc.ac.uk']


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



def make_wsgi(deployment=None, filepath=None):
    """
    Create the wsgi script used for deployment.

    :param deployment: A path to the virtualenv used to deploy.  
        This will default to the current virtualenv.  Note this can be set to
        a path on another system where the code will be deployed.
    :param filepath: The path to write the resulting wsgi file to.
        This defaults to ./apache/pimms.wsgi

    """

    if deployment is None:
        deployment = sys.prefix

    if filepath is None:
        filepath = op.join(here, 'apache/pimms.wsgi')

    wsgi_template = op.join(here, 'apache/pimms.wsgi.tmpl')
    t = Template(open(wsgi_template).read())
    wsgi_src = t.substitute(DEPLOYMENT=deployment)

    with open(filepath, 'w') as fh:
        fh.write(wsgi_src)

