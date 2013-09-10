import sys, re, os, optparse, shutil, json, drutils, subprocess, time

from Nappl import *
from NapplMeta import *
from Container import *
from ApacheContainer import *

class DrupalContainer(ApacheContainer):

    def __init__(self, appName):
        super(DrupalContainer, self).__init__(appName)

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
        # Create the ApacheContainer
        #
        super(DrupalContainer, self).create()
        #
        # Change the application type to 'drupal'
        #
        self.meta.data['application']['type'] = 'drupal'
        self.meta.save()
        #
        # create the mysql database
        #
        if dbname is None:
            dbname = infer_database_name(self.appName)
        try:
            create_database(dbname)
            #print "Created database/user '%s'" % dbname
            pw = drutils.get_db_password(dbname)
            #print "Database password: '%s'" % pw
            self.meta.data['database'] = {
              'name'     : dbname,
              'user'     : dbname,
              'password' : pw
            }
            self.meta.save()
        except:
            super(DrupalContainer, self).delete()
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

    def delete(self):
        """Deletes a Drupal container"""
        # drop the database
        try:
            dbname = self.get_dbname()
            # drop the database & user
            (DB_SU, DB_SU_PW) = drutils.get_dbsu()
            drutils.drop_database(dbname, DB_SU, DB_SU_PW)
            drutils.drop_user(dbname, DB_SU, DB_SU_PW)
            # delete the drutils mysql cnf file
            drutils_mysql_cnf = "/var/drutils/mysql/%s.cnf" % dbname
            if os.path.exists(drutils_mysql_cnf):
                os.remove(drutils_mysql_cnf)
        except:
            pass
        # delete the mysql credentials files
        mysql_credentials_dir = "/var/vsites/mysql/%s" % self.appName
        if os.path.exists(mysql_credentials_dir):
            rmtree(mysql_credentials_dir)
        #
        # Delete the ApacheContainer
        #
        super(DrupalContainer, self).delete()

    def init(self):
        """Populate a Drupal container with a freshly downloaded (via drush) copy of Drupal,
        and initialize it as a new git repo."""
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
        # use drush to download drupal into the 'html' subdir of vsitesdir
        os.system("cd %s ; %s" % (vsitesdir,drush_dl_command()))
        # use drush to install that copy of drupal into the database
        os.system(("cd %s/html ; %s")
                  % (vsitesdir, drush_site_install_command(self.appName, dbname, dbpassword)))
        # edit the new drupal's settings.php file to point to the container's mysql credentials file
        edit_drupal_settingsphp(vsitesdir, self.appName)
        # edit the new drupal's .gitignore file so that it will allow settings.php in git repo
        edit_drupal_gitignore(vsitesdir)
        super(DrupalContainer, self).init()

    def dump_db(self, timestamp=None):
        """Write a compressed sql dump file for the application into the current directory."""
        vsitesdir = "/var/vsites/%s" % self.appName
        sha = bash_command("cd %s ; git rev-parse --short HEAD" % vsitesdir)
        if not self.git_wd_clean():
            sha = sha + "--edited"
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        dumpfile = "%s--%s--%s.sql.gz" % (self.appName, sha, timestamp)
        os.system("drush -r %s/html sql-dump | gzip > %s" % (vsitesdir, dumpfile))
        print "wrote %s" % dumpfile

    def load_db(self, dumpfile):
        """Load a compressed sql dump file into the database for this container."""
        # 'git rev-parse --short HEAD' will print current commit sha
        vsitesdir = "/var/vsites/%s" % self.appName
        os.system("gunzip < %s | drush -r %s/html sqlc" % (dumpfile, vsitesdir))
        print "loaded database from %s" % dumpfile

    def get_files_dirs(self):
        vsitesdir = "/var/vsites/%s" % self.appName
        dirs = []
        for dir in os.listdir("%s/html/sites" % vsitesdir):
            if os.path.isdir("%s/html/sites/%s" % (vsitesdir,dir)):
                for f in ['files','private']:
                    if (os.path.exists("%s/html/sites/%s/%s" % (vsitesdir,dir,f))
                        and os.path.isdir("%s/html/sites/%s/%s" % (vsitesdir,dir,f))):
                        dirs.append("sites/%s/%s" % (dir,f))
        return dirs

    def dump_files(self, timestamp=None):
        """Write a compressed tar file for the drupal application's files into the current directory."""
        vsitesdir = "/var/vsites/%s" % self.appName
        sha = bash_command("cd %s ; git rev-parse --short HEAD" % vsitesdir)
        if not self.git_wd_clean():
            sha = sha + "--edited"
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        dumpfile = "%s--%s--%s.files.tgz" % (self.appName, sha, timestamp)
        dirs = self.get_files_dirs()
        cmd = "(cd %s/html ; tar cfz - %s) > %s" % (vsitesdir, " ".join(dirs), dumpfile)
        os.system(cmd)
        print "wrote %s" % dumpfile

    def load_files(self, dumpfile):
        """Load a compressed tar file of uploaded files into the application."""
        if not os.path.exists(dumpfile):
            raise Exception("Dump file %s not found" % dumpfile)
        vsitesdir = "/var/vsites/%s" % self.appName
        dirs = self.get_files_dirs()
        for d in dirs:
            p = "%s/html/%s" % (vsitesdir, d)
            if os.path.isdir(p):
                shutil.rmtree(p)
        os.system("cat %s | (cd %s/html ; tar xfz -)" % (dumpfile, vsitesdir))
        print "loaded files from %s" % dumpfile

    def dump_all(self, timestamp=None):
        """Write both a database dump and a files archive into the current directory."""
        vsitesdir = "/var/vsites/%s" % self.appName
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        self.dump_db(timestamp)
        self.dump_files(timestamp)

    @staticmethod
    def get_drutils_dump_info(dir):
        """Return a dict with keys 'sqlfile' and 'docroot' containing the sql file name and document
        root directory, respectively, from an unpacked drutils dump file in the given directory."""
        drutils_info = { "sqlfile" : None, 'docroot' : None }
        for f in os.listdir(dir):
            m = re.match(r'^(.+)\.sql$', f)
            if m and os.path.isfile("%s/%s" % (dir,f)):
                drutils_info["sqlfile"] = f
                continue
            if (os.path.isdir("%s/%s" % (dir,f))
                and os.path.exists("%s/%s/index.php" % (dir,f))):
                drutils_info["docroot"] = f
        return drutils_info

    def import_drutils_dump(self, dumpfile):
        """Populate a Drupal container with a new project obtained by importing from a dump file
        that was written by the drutils `dumpsite` command, and initialize it as a new git repo."""
        if not os.path.exists(dumpfile):
            raise Exception("Drutils dump file %s not found" % dumpfile)
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
        # create a temporary directory for unpacking the drutils dump file
        tmpdir = "/tmp/nappl-%s" % os.getpid()
        if os.path.exists(tmpdir):
            if os.path.isdir(tmpdir):
                shutil.rmtree(tmpdir)
            else:
                os.remove(tmpdir)
        os.mkdir(tmpdir)
        # unpack the drutils dump file into the tmp dir
        print "unpacking dump file %s" % dumpfile
        os.system("cat %s | (cd %s ; tar xfz -)" % (dumpfile, tmpdir))
        drutils_info = DrupalContainer.get_drutils_dump_info(tmpdir)
        # create the container's html dir
        os.mkdir("%s/html" % vsitesdir)
        # copy the docroot contents from the drutils dump into the html dir
        print "copying Drupal files into container %s" % self.appName
        os.system("(cd %s/%s ; tar cf - .) | (cd %s/html ; tar xf -)" % (tmpdir,drutils_info["docroot"],vsitesdir))
        # make the new files writable by owner/group (but not other)
        os.system("chmod u+w,g+w,o-w %s/html" % vsitesdir)
        os.system("chmod u+w,g+w %s/html/sites/default" % vsitesdir)
        os.system("chmod u+w,g+w %s/html/sites/default/settings.php" % vsitesdir)
        os.system("(cd %s/html ; ( find . -type d -print | xargs chmod g+wxs ))" % vsitesdir)
        # make the new uploaded files dir(s) writable by other
        for dir in self.get_files_dirs():
            os.system("chmod -R o+w %s/html/%s" % (vsitesdir,dir))
        # edit the new drupal's settings.php file to point to the container's mysql credentials file
        edit_drupal_settingsphp(vsitesdir, self.appName)
        # use drush to load the sql file from the drutils dump
        print "loading database from %s found in dump file" % drutils_info["sqlfile"]
        os.system("drush -r %s/html sqlc < %s/%s" % (vsitesdir, tmpdir, drutils_info["sqlfile"]))
        # edit the new drupal's .gitignore file so that it will allow settings.php in git repo
        edit_drupal_gitignore(vsitesdir)
        # initialize the apache container
        print "initializing git repo in %s" % vsitesdir
        super(DrupalContainer, self).init(gitmessage=("imported drutils dump file %s" % dumpfile))
        # clean up the tmp dir
        print "cleaning up"
        os.system("chmod -R u+rw %s" % tmpdir) # make sure it's all writable first, so that the following command can delete it
        shutil.rmtree(tmpdir)
