import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *

class Container(object):
    def __init__(self, appName):
        self.appName = appName
        self.meta = NapplMeta(self.appName)

    def create(self):
        """Create a new application container.  This method simply creates the nappl
        metadata directory for the container; Container subclasses should override this
        method with an implementation that calls this method, then adds any necesssary
        subclass-specific creation steps."""
        #
        # create the nappl metadata file
        #
        if os.path.exists(self.meta.dir):
            raise Exception("Cowardly refusing to overwrite existing container :%s"
                            % self.appName)
        self.meta.data['container'] = {
            'name'      : self.appName
        }
        self.meta.save()

    def delete(self):
        """Delete an application container.  This method deletes the container's /deploy
        repo, if any, and then deletes the container's nappl metadata directory.  Subclasses
        should override this method with an implementation that does whatever subclass-specific
        deleting work is needed, then calls this method afterwards."""
        # if this container has a /deploy repo, delete it
        if ( ('deployrepo' in self.meta.data['container'])
             and os.path.exists(self.meta.data['container']['deployrepo']) ):
            shutil.rmtree(self.meta.data['container']['deployrepo'])
        # delete the nappl metadata dir
        if os.path.exists(self.meta.dir):
            rmtree(self.meta.dir)

    def makeDeployable(self):
        """Create a /deploy repo for a container."""
        appdir = self.meta.data['container']['location']
        if not os.path.exists(appdir + "/.git"):
            raise Exception(("Cannot make deployable; container directory %s does not exist or is not"
                            + " set up as a git project.") % appdir)
        #
        # Create the deploy repo, if it does not yet exist
        #
	deployrepo = "/deploy/" + self.appName + ".git"
        if not os.path.exists(deployrepo):
            # create the deploy repo dir
            os.system("mkdir %s" % deployrepo)
            # initialize the deploy repo dir as a bare git repo
            os.system("cd %s ; git init -q --bare" % deployrepo)
            # push the current app repo to the deploy repo
            os.system("cd %s ; git push -q %s master" % (appdir,deployrepo))
        #
	# Add the depoy repo as a remote for the application repo, if the
        # app repo does not already have a remote called 'deploy':
        #
        if bash_command("cd %s ; git remote | grep deploy" % appdir) == "":
            os.system("cd %s ; git remote add deploy %s" % (appdir, deployrepo))

        #
        # Install the post-update hook to cause the application dir/repo to automatically
        # pull any changes committed to the deployment repo.  This overwrites any
        # existing post-update hook.
        #
        with open("%s/hooks/post-update" % deployrepo, "w") as f:
            f.write("""\
#!/usr/bin/python

import os

print ""
print "**** Deploying updates to %(APPDIR)s ****"
print ""

if os.path.exists("%(APPDIR)s"):
    os.system("unset GIT_DIR ; cd %(APPDIR)s ; git pull deploy master")
    os.system("unset GIT_DIR ; cd %(APPDIR)s ; git update-server-info")
"""
                    % { 'APPDIR'  : appdir,
                        'APPNAME' : self.appName })
        os.system("chmod +x %s/hooks/post-update" % deployrepo)
        #
        # Add deploy repo info to container metadata
        #
        self.meta.data['container']['deployrepo'] = deployrepo
        self.meta.save()

    @staticmethod
    def load(appName):
        """Return a Container instance corresponding to an existing
        nappl container on the system. The returned object will have a
        'meta' property which has been pre-loaded with a NapplMeta
        object containing the container metadata."""
        meta = NapplMeta(appName)
        if not os.path.exists(meta.datafile):
            raise Exception("Container not found.")
        if meta.data['container']['type'] == "drupal":
            container = DrupalContainer(appName)
            container.meta = meta
            return container
        if meta.data['container']['type'] == "apache":
            container = ApacheContainer(appName)
            container.meta = meta
            return container
        raise Exception("Unknown container type '%s'" % meta.data['container']['type'])

    @staticmethod
    def list_containers():
        """Return a list of current containers on the system; each entry in the list
        is a python dict containing metadata about the container."""
        if not os.path.exists("/var/nappl"):
            raise Exception("/var/nappl directory not found")
        apps = []
        for appname in os.listdir("/var/nappl"):
            a = NapplMeta(appname)
            apps.append(a.data)
        return apps

#
# We need to import these subclasses for use in the load() method above.  These
# have to be imported after the definition of the Container class, rather than
# at the top of the file, because they inherit from Container.
#
from DrupalContainer import *
from ApacheContainer import *
