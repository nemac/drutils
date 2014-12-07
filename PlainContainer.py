import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *
from Container import *
from EtcHoster import *

class PlainContainer(Container):

    def __init__(self, appName):
        super(PlainContainer, self).__init__(appName)

    def create(self):
        """Create a container for 'plain' nappl application."""
        #
        # make sure the container dir (vsitesdir) does not already exist before getting started
        #
        if os.path.exists(self.vsitesdir()):
            raise Exception("Container directory %s already exists; refusing to overwrite"
                            % self.vsitesdir())
        #
        # create the basic container
        #
        super(PlainContainer, self).create()
        #
        # add plain-specific settings to the nappl  metadata file
        #
        self.meta.data['container']['type'] = 'plain'
        self.meta.data['container']['location'] = "/var/vsites/%s/project" % self.appName
        self.meta.save()
        #
        # create the container directory (vsitesdir)
        #
        os.mkdir(self.vsitesdir())

    def delete(self):
        """Deletes a plain container"""
        # delete the vsites dir for the app
        if os.path.exists(self.vsitesdir()):
            rmtree(self.vsitesdir())
        # delete the nappl metadata dir
        super(PlainContainer, self).delete()

    def vsitesdir(self):
        return "/var/vsites/%s" % self.appName

    def projectdir(self):
        return "/var/vsites/%s/project" % self.appName

    def init(self, gitmessage=None):
        """Initialize a container for a plain application.  This involves the
        following:
        
        * create a new, empty `project` subdir for a plain container
        * initialize a git repo in the `project` subdir
        * make the container deployable (set up /deploy repo for it)
        
        Each of the above items is only done if it needs to be -- i.e. any
        step that is already done is skipped.  This allows subclasses to
        implement this method to initialize their own project subdir, then
        call this method to do everything else.
        
        The optional `gitmessage` argument is appended to the initial git
        commit log message when a git repo is being initialized.  This
        argument is ignored if the git repo already exists."""
        # create the project subdir, if it does not yet exist
        if not os.path.exists(self.projectdir()):
            os.mkdir(self.projectdir())
        # initialize a git repo for the application, if there isn't one already
        if not os.path.exists("%s/.git" % self.projectdir()):
            with open("%s/.gitignore" % self.projectdir(), "w") as f:
                f.write("*~\n")
            if gitmessage is None:
                gitmessage = "initial nappl setup"
            else:
                gitmessage = "initial nappl setup (%s)" % gitmessage
            os.system("cd %s ; git init -q ; git add . ; git commit -q -m '%s'" % (self.projectdir(), gitmessage.replace("'", "\\'")))
        self.makeDeployable()

    def git_wd_clean(self):
        """Return True iff the application project in this container has no outstanding edits since
        the last git commit."""
        return git_wd_clean(self.projectdir())
