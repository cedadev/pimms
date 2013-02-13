from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm


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
