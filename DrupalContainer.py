import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *
from Container import *

class DrupalContainer(Container):

    def __init__(self, appName):
        Container.__init__(self, appName)

    def get_dbname(self):
        """Returns the name of this container's database, as read from its nappl metadata file"""
        meta = NapplMeta(self.appName)
        if not os.path.exists(meta.datafile):
            raise Exception("Metadata file for application '%s' not found." % self.appName)
        meta.load()
        return meta.data['database']['name']

    def get_dbpassword(self):
        """Returns the password for this container's database, as read from its nappl metadata file"""
        meta = NapplMeta(self.appName)
        if not os.path.exists(meta.datafile):
            raise Exception("Metadata file for application '%s' not found." % self.appName)
        meta.load()
        return meta.data['database']['password']

    def create(self, dbname=None):
        #
        # create the nappl metadata file
        #
        meta = NapplMeta(self.appName)
        if os.path.exists(meta.dir):
            raise Exception("Cowardly refusing to overwrite existing container for application '%s'"
                            % self.appName)
        meta.data['application'] = {
            'name'      : self.appName,
            'type'      : 'drupal',
            'location'  : "/var/vsites/%s" % self.appName
        }
        meta.save()
        #
        # create the mysql database
        #
        if dbname is None:
            dbname = infer_database_name(self.appName)
        if create_database(dbname):
            #print "Created database/user '%s'" % dbname
            pw = drutils.get_db_password(dbname)
            #print "Database password: '%s'" % pw
            meta.data['database'] = {
              'name'     : dbname,
              'user'     : dbname,
              'password' : pw
            }
            meta.save()
        else:
            raise Exception("Cannot create database/user '%s'; container not created." % dbname)
        #
        # create the database credentials files
        #
        mysql_credentials_dir = "/var/vsites/mysql/%s" % self.appName
        if not os.path.exists(mysql_credentials_dir):
            os.mkdir(mysql_credentials_dir)
        d6file = "%s/d6.php" % mysql_credentials_dir
        f = open(d6file, "w")
        f.write("<?php\n$db_url = 'mysqli://%s:%s@localhost/%s';\n" % (dbname, pw, dbname))
        f.close()
        #print "wrote %s." % d6file
        d7file = "%s/d7.php" % mysql_credentials_dir
        f = open(d7file, "w")
        f.write((
                "<?php\n"
                + "$databases = array (\n"
                + "  'default' =>\n"
                + "  array (\n"
                + "    'default' =>\n"
                + "    array (\n"
                + "      'database' => '%s',\n"
                + "      'username' => '%s',\n"
                + "      'password' => '%s',\n"
                + "      'host' => 'localhost',\n"
                + "      'port' => '',\n"
                + "      'driver' => 'mysql',\n"
                + "      'prefix' => '',\n"
                + "    ),\n"
                + "  ),\n"
                + ");\n"
                ) % (dbname, dbname, pw))
        f.close()
        EtcHoster(self.appName).add_line()

    def delete(self):
        """Deletes a Drupal container"""
        # get the database name
        dbname = self.get_dbname()
        # drop the database & user
        (DB_SU, DB_SU_PW) = drutils.get_dbsu()
        drutils.drop_database(dbname, DB_SU, DB_SU_PW)
        drutils.drop_user(dbname, DB_SU, DB_SU_PW)
        # delete the drutils mysql cnf file
        drutils_mysql_cnf = "/var/drutils/mysql/%s.cnf" % dbname
        if os.path.exists(drutils_mysql_cnf):
            os.remove(drutils_mysql_cnf)
        # delete the mysql credentials files
        mysql_credentials_dir = "/var/vsites/mysql/%s" % self.appName
        rmtree(mysql_credentials_dir)
        # delete the vsites dir for the app
        vsitesdir = "/var/vsites/%s" % self.appName
        if os.path.exists(vsitesdir):
            rmtree(vsitesdir)
        # delete the apache conf symlink
        apacheconf_symlink = "/var/vsites/conf/%s.conf" % self.appName
        if os.path.lexists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
        EtcHoster(self.appName).remove_lines()
        # delete the nappl metadata dir
        meta = NapplMeta(self.appName)
        if os.path.exists(meta.dir):
            rmtree(meta.dir)

        #print "Container for app %s deleted" % self.appName

    def init(self):
        """Populate a Drupal container with a freshly downloaded (via drush) copy of Drupal,
        and initialize it as a new git repo.
        """
        # get the database name
        dbname = self.get_dbname()
        if dbname is None:
            raise Exception("Cannot find database name for application '%s'" % self.appName)
        # get the database password
        dbpassword = self.get_dbpassword()
        if dbpassword is None:
            raise Exception("Cannot find database password for application '%s'" % self.appName)
        # create the application directory (vsitesdir)
        vsitesdir = "/var/vsites/%s" % self.appName
        if os.path.exists(vsitesdir):
            raise Exception("Application directory %s already exists; refusing to overwrite" % vsitesdir)
        os.mkdir(vsitesdir)
        # write the apache conf file for the application
        apacheconf = "%s/site.conf" % vsitesdir
        f = open(apacheconf, "w")
        f.write((""
                 + "<VirtualHost *:80>\n"
                 + "    DocumentRoot %s/html\n"
                 + "    ServerName %s\n"
                 + "    ErrorLog logs/%s-error_log\n"
                 + "    CustomLog logs/%s-access_log common\n"
                 + "    <Directory %s/html>\n"
                 + "      AllowOverride All\n"
                 + "    </Directory>\n"
                 + "</VirtualHost>\n") % (vsitesdir, self.appName, self.appName, self.appName, vsitesdir))
        f.close()
        # use drush to download drupal into the 'html' subdir of vsitesdir
        os.system("cd %s ; %s" % (vsitesdir,drush_dl_command()))
        # use drush to install that copy of drupal into the database
        os.system(("cd %s/html ; %s")
                  % (vsitesdir, drush_site_install_command(self.appName, dbname, dbpassword)))
        # edit the new drupal's settings.php file to point to the container's mysql credentials file
        edit_drupal_settingsphp(vsitesdir, self.appName)
        # edit the new drupal's .gitignore file so that it will allow settings.php in git repo
        edit_drupal_gitignore(vsitesdir)
        # initialize a git repo for the application
        with open("%s/.gitignore" % vsitesdir, "w") as f:
            f.write("*~\n")
        os.system("cd %s ; git init -q ; git add . ; git commit -q -m 'initial nappl setup'" % vsitesdir)
        self.install()

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

    def git_wd_clean(self):
        """Return True iff the application in this container has no outstanding edits since
        the last git commit."""
        vsitesdir = "/var/vsites/%s" % self.appName
        return git_wd_clean(vsitesdir)

    def dbdump(self):
        """Write a compressed sql dump file for the application into the current directory."""
        vsitesdir = "/var/vsites/%s" % self.appName
        sha = bash_command("cd %s ; git rev-parse --short HEAD" % vsitesdir)
        if not self.git_wd_clean():
            sha = sha + "--edited"
        timestamp = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        dumpfile = "%s--%s--%s.sql.gz" % (self.appName, sha, timestamp)
        os.system("drush -r %s/html sql-dump | gzip > %s" % (vsitesdir, dumpfile))
        print "wrote %s" % dumpfile

    def dbload(self, dumpfile):
        """Load a compressed sql dump file into the database for this container."""
        # 'git rev-parse --short HEAD' will print current commit sha
        vsitesdir = "/var/vsites/%s" % self.appName
        os.system("gunzip < %s | drush -r %s/html sqlc" % (dumpfile, vsitesdir))
