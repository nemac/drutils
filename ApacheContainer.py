import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *
from Container import *
from EtcHoster import *

class ApacheContainer(Container):

    def __init__(self, appName):
        super(ApacheContainer, self).__init__(appName)

    def create(self, dbname=None):
        super(ApacheContainer, self).create()
        #
        # add apache-specific settings to application metadata file
        #
        self.meta.data['application']['type'] = 'apache'
        self.meta.data['application']['location'] = "/var/vsites/%s" % self.appName
        self.meta.save()
        #
        # Create an entry for this web site in /etc/hosts
        #
        EtcHoster(self.appName).add_line()

    def delete(self):
        """Deletes an Apache container"""
        # delete the vsites dir for the app
        vsitesdir = "/var/vsites/%s" % self.appName
        if os.path.exists(vsitesdir):
            rmtree(vsitesdir)
        # delete the apache conf symlink
        apacheconf_symlink = "/var/vsites/conf/%s.conf" % self.appName
        if os.path.lexists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
            ApacheContainer.restart_apache()
        EtcHoster(self.appName).remove_lines()
        # delete the nappl metadata dir
        super(ApacheContainer, self).delete()

    def init(self, gitmessage=None):
        """Populate an Apache container with an htmldir, a placeholder index.html file,
        an initial site.conf file, and initialize it as a new git repo."""
        # create the application directory (vsitesdir), if it does not yet exist
        vsitesdir = "/var/vsites/%s" % self.appName
        if not os.path.exists(vsitesdir):
            os.mkdir(vsitesdir)
        # create the html subdir, if it does not yet exist
        htmldir = "%s/html" % vsitesdir
        if not os.path.exists(htmldir):
            os.mkdir(htmldir)
            # create the index.html file, if it does not exist
            indexhtml = "%s/index.html" % htmldir
            if not os.path.exists(indexhtml):
                with open(indexhtml, "w") as f:
                    f.write(self.appName)
        # write the apache conf file for the application
        apacheconf = "%s/site.conf" % vsitesdir
        if not os.path.exists(apacheconf):
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
                         + "</VirtualHost>\n") % (vsitesdir, self.appName, self.appName,
                                                  self.appName, vsitesdir))
        # initialize a git repo for the application
        with open("%s/.gitignore" % vsitesdir, "w") as f:
            f.write("*~\n")
        if gitmessage is None:
            gitmessage = "initial nappl setup"
        else:
            gitmessage = "initial nappl setup (%s)" % gitmessage
        os.system("cd %s ; git init -q ; git add . ; git commit -q -m '%s'" % (vsitesdir, gitmessage.replace("'", "\\'")))
        self.makeDeployable()
        self.install()

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

    def install(self):
        """Create a symlink in /var/vsites/conf for an application's apache conf file"""
        vsitesdir = "/var/vsites/%s" % self.appName
        apacheconf = "%s/site.conf" % vsitesdir
        if not os.path.exists(apacheconf):
            raise Exception("Apache conf file %s not found" % apacheconf)
        apacheconf_symlink = "/var/vsites/conf/%s.conf" % self.appName
        if os.path.lexists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
        os.symlink(apacheconf, apacheconf_symlink)
        ApacheContainer.restart_apache()

    def git_wd_clean(self):
        """Return True iff the application in this container has no outstanding edits since
        the last git commit."""
        vsitesdir = "/var/vsites/%s" % self.appName
        return git_wd_clean(vsitesdir)

