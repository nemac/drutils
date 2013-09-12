import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *
from Container import *
from EtcHoster import *

class ApacheContainer(Container):

    def __init__(self, appName):
        super(ApacheContainer, self).__init__(appName)

    def create(self):
        """Create a container for an Apache vhost application."""
        #
        # make sure the container dir (vsitesdir) does not already exist before getting started
        #
        if os.path.exists(self.vsitesdir()):
            raise Exception("Container directory %s already exists; refusing to overwrite"
                            % self.vsitesdir())
        #
        # create the basic container
        #
        super(ApacheContainer, self).create()
        #
        # add apache-specific settings to the nappl  metadata file
        #
        self.meta.data['container']['type'] = 'apache'
        self.meta.data['container']['location'] = "/var/vsites/%s/project" % self.appName
        self.meta.save()
        #
        # create the container directory (vsitesdir)
        #
        os.mkdir(self.vsitesdir())
        #
        # create the vhost conf file (site.conf) in vsitesdir:
        #
        apacheconf = "%s/site.conf" % self.vsitesdir()
        with open(apacheconf, "w") as f:
            f.write((""
                     + "<VirtualHost *:80>\n"
                     + "    DocumentRoot %s/html\n"
                     + "    ServerName %s\n"
                     + "    ErrorLog logs/%s-error_log\n"
                     + "    CustomLog logs/%s-access_log common\n"
                     + "    <Directory %s/html>\n"
                     + "      AllowOverride All\n"
                     + "    </Directory>\n"
                     + "</VirtualHost>\n") % (self.projectdir(), self.appName, self.appName,
                                              self.appName, self.projectdir()))
        #
        # create a symlink to the apache conf file from /var/vsites/conf
        #
        apacheconf_symlink = "/var/vsites/conf/%s.conf" % self.appName
        if os.path.lexists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
        os.symlink(apacheconf, apacheconf_symlink)
        #
        # Create an entry for this vhost sitename in /etc/hosts
        #
        EtcHoster(self.appName).add_line()

    def delete(self):
        """Deletes an Apache container"""
        # delete the vsites dir for the app
        if os.path.exists(self.vsitesdir()):
            rmtree(self.vsitesdir())
        # delete the apache conf symlink
        apacheconf_symlink = "/var/vsites/conf/%s.conf" % self.appName
        if os.path.lexists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
            ApacheContainer.restart_apache()
        # remove entry for this vhost sitename from /etc/hosts
        EtcHoster(self.appName).remove_lines()
        # delete the nappl metadata dir
        super(ApacheContainer, self).delete()

    def vsitesdir(self):
        return "/var/vsites/%s" % self.appName

    def projectdir(self):
        return "/var/vsites/%s/project" % self.appName

    def init(self, gitmessage=None):
        """Initialize a container for an apache application.  This involves the
        following:
        
        * create a new `project` subdir for an apache container, populating
          it with a new apache project
        * initialize a git repo in the `project` subdir
        * make the container deployable (set up /deploy repo for it)
        * restart apache (if the current user has permission to do so)
        
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
            # create the html subdir, if it does not yet exist
            htmldir = "%s/html" % self.projectdir()
            if not os.path.exists(htmldir):
                os.mkdir(htmldir)
                # create the index.html file, if it does not exist
                indexhtml = "%s/index.html" % htmldir
                if not os.path.exists(indexhtml):
                    with open(indexhtml, "w") as f:
                        f.write(self.appName)
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
        ApacheContainer.restart_apache()

    @staticmethod
    def restart_apache():
        """Restart apache if possible, otherwise display a warning message."""
        code = os.system("sudo -n service httpd restart")
        if code != 0:
            print "WARNING ***"
            print "WARNING *** Apache restart required.  Your account does not have the appropriate"
            print "WARNING *** permissions for restarting Apache.  Someone with that permission needs"
            print "WARNING *** to execute the command"
            print "WARNING ***     sudo service httpd restart"
            print "WARNING *** in order for the change(s) you have just made to completely take effect."
            print "WARNING ***"

    def git_wd_clean(self):
        """Return True iff the application project in this container has no outstanding edits since
        the last git commit."""
        return git_wd_clean(self.projectdir())
