import sys, re, os, optparse, shutil, json, drutils, subprocess, time

os.environ['DRUSH_DL_COMMAND'] = "tar xfz %s/drupal-7.23.tgz ; mv drupal-7.23 html" % os.getcwd()

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
            raise Exception("Metadata file for container '%s' not found." % self.appName)
        meta.load()
        return meta.data['database']['name']

    def get_dbpassword(self):
        """Returns the password for this container's database, as read from its nappl metadata file"""
        meta = NapplMeta(self.appName)
        if not os.path.exists(meta.datafile):
            raise Exception("Metadata file for container '%s' not found." % self.appName)
        meta.load()
        return meta.data['database']['password']

    def mysql_credentials_dir(self):
        return "%s/mysql" % self.vsitesdir()

    def create(self, dbname=None):
        #
        # Create the ApacheContainer
        #
        super(DrupalContainer, self).create()
        #
        # Change the container type to 'drupal'
        #
        self.meta.data['container']['type'] = 'drupal'
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
        if not os.path.exists(self.mysql_credentials_dir()):
            os.mkdir(self.mysql_credentials_dir())
        d6file = "%s/d6.php" % self.mysql_credentials_dir()
        f = open(d6file, "w")
        f.write("<?php\n$db_url = 'mysqli://%s:%s@localhost/%s';\n" % (dbname, pw, dbname))
        f.close()
        #print "wrote %s." % d6file
        d7file = "%s/d7.php" % self.mysql_credentials_dir()
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
            raise Exception("Cannot find database name for container '%s'" % self.appName)
        # get the database password
        dbpassword = self.get_dbpassword()
        if dbpassword is None:
            raise Exception("Cannot find database password for container '%s'" % self.appName)
        # create the project directory (projectdir)
        if os.path.exists(self.projectdir()):
            raise Exception("Container project directory %s already exists; refusing to overwrite" % self.projectdir())
        os.mkdir(self.projectdir())
        # use drush to download drupal into the 'html' subdir of projectdir
        os.system("cd %s ; %s" % (self.projectdir(),drush_dl_command()))
        # use drush to install that copy of drupal into the database
        os.system(("cd %s/html ; %s")
                  % (self.projectdir(), drush_site_install_command(self.appName, dbname, dbpassword)))
        # edit the new drupal's settings.php file to point to the container's mysql credentials file
        self.edit_drupal_settingsphp()
        # edit the new drupal's .gitignore file so that it will allow settings.php in git repo
        self.edit_drupal_gitignore()
        # call the parent class method to initialize the git repo
        super(DrupalContainer, self).init()

    def dump_db(self, timestamp=None):
        """Write a compressed sql dump file for the container into the current directory."""
        sha = bash_command("cd %s ; git rev-parse --short HEAD" % self.projectdir())
        if not self.git_wd_clean():
            sha = sha + "--edited"
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        dumpfile = "%s--%s--%s.sql.gz" % (self.appName, sha, timestamp)
        os.system("drush -r %s/html sql-dump | gzip > %s" % (self.projectdir(), dumpfile))
        print "wrote %s" % dumpfile

    def load_db(self, dumpfile):
        """Load a compressed sql dump file into the database for this container."""
        # 'git rev-parse --short HEAD' will print current commit sha
        os.system("gunzip < %s | drush -r %s/html sqlc" % (dumpfile, self.projectdir()))
        print "loaded database from %s" % dumpfile

    def get_files_dirs(self):
        dirs = []
        for dir in os.listdir("%s/html/sites" % self.projectdir()):
            if os.path.isdir("%s/html/sites/%s" % (self.projectdir(),dir)):
                for f in ['files','private']:
                    if (os.path.exists("%s/html/sites/%s/%s" % (self.projectdir(),dir,f))
                        and os.path.isdir("%s/html/sites/%s/%s" % (self.projectdir(),dir,f))):
                        dirs.append("sites/%s/%s" % (dir,f))
        return dirs

    def dump_files(self, timestamp=None):
        """Write a compressed tar file for the drupal application's files into the current directory."""
        sha = bash_command("cd %s ; git rev-parse --short HEAD" % self.projectdir())
        if not self.git_wd_clean():
            sha = sha + "--edited"
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        dumpfile = "%s--%s--%s.files.tgz" % (self.appName, sha, timestamp)
        dirs = self.get_files_dirs()
        cmd = "(cd %s/html ; tar cfz - %s) > %s" % (self.projectdir(), " ".join(dirs), dumpfile)
        os.system(cmd)
        print "wrote %s" % dumpfile

    def load_files(self, dumpfile):
        """Load a compressed tar file of uploaded files into the container."""
        if not os.path.exists(dumpfile):
            raise Exception("Dump file %s not found" % dumpfile)
        dirs = self.get_files_dirs()
        for d in dirs:
            p = "%s/html/%s" % (self.projectdir(), d)
            if os.path.isdir(p):
                shutil.rmtree(p)
        os.system("cat %s | (cd %s/html ; tar xfz -)" % (dumpfile, self.projectdir()))
        print "loaded files from %s" % dumpfile

    def dump_all(self, timestamp=None):
        """Write both a database dump and a files archive into the current directory."""
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
        that was written by the drutils `dumpsite` command, and initialize it as a new git repo.
        This is analogous to the init() method above, but populates the container with an existing
        Drupal site from a drutils dump file, rather than by initializing it with a new Drupal
        site with the latest version of Drupal."""
        if not os.path.exists(dumpfile):
            raise Exception("Drutils dump file %s not found" % dumpfile)
        # get the database name
        dbname = self.get_dbname()
        if dbname is None:
            raise Exception("Cannot find database name for container '%s'" % self.appName)
        # get the database password
        dbpassword = self.get_dbpassword()
        if dbpassword is None:
            raise Exception("Cannot find database password for container '%s'" % self.appName)
        # create the project directory (projectdir)
        if os.path.exists(self.projectdir()):
            raise Exception("Container project directory %s already exists; refusing to overwrite" % self.projectdir())
        os.mkdir(self.projectdir())
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
        os.mkdir("%s/html" % self.projectdir())
        # copy the docroot contents from the drutils dump into the html dir
        print "copying Drupal files into container %s" % self.appName
        os.system("(cd %s/%s ; tar cf - .) | (cd %s/html ; tar xf -)" % (tmpdir,drutils_info["docroot"],self.projectdir()))
        # make the new files writable by owner/group (but not other)
        os.system("chmod u+w,g+w,o-w %s/html" % self.projectdir())
        os.system("chmod u+w,g+w %s/html/sites/default" % self.projectdir())
        os.system("chmod u+w,g+w %s/html/sites/default/settings.php" % self.projectdir())
        os.system("(cd %s/html ; ( find . -type d -print | xargs chmod g+wxs ))" % self.projectdir())
        # make the new uploaded files dir(s) writable by other
        for dir in self.get_files_dirs():
            os.system("chmod -R o+w %s/html/%s" % (self.projectdir(),dir))
        # edit the new drupal's settings.php file to point to the container's mysql credentials file
        self.edit_drupal_settingsphp()
        # use drush to load the sql file from the drutils dump
        print "loading database from %s found in dump file" % drutils_info["sqlfile"]
        os.system("drush -r %s/html sqlc < %s/%s" % (self.projectdir(), tmpdir, drutils_info["sqlfile"]))
        # edit the new drupal's .gitignore file so that it will allow settings.php in git repo
        self.edit_drupal_gitignore()
        # initialize the apache container
        print "initializing git repo in %s" % self.projectdir()
        super(DrupalContainer, self).init(gitmessage=("imported drutils dump file %s" % dumpfile))
        # clean up the tmp dir
        print "cleaning up"
        os.system("chmod -R u+rw %s" % tmpdir) # make sure it's all writable first, so that the following command can delete it
        shutil.rmtree(tmpdir)

    def edit_drupal_settingsphp(self):
        settingsphp = "%s/html/sites/default/settings.php" % self.projectdir()
        if not os.path.exists(settingsphp):
            raise Exception("Drupal not correctly installed into container; missing sites/default/settings.php")
        with open(settingsphp, "r") as f:
            contents = f.readlines()
        d7 = False
        d6 = False
        newcontents = []
        for line in [x.strip("\n") for x in contents]:
            if re.match(r'^\s*\$databases\s*=\s*array.*$', line):
                d7 = True
            elif d7 and re.search(r"'database'\s*=>\s*", line):
                line = "      'database' => '',"
            elif d7 and re.search(r"'username'\s*=>\s*", line):
                line = "      'username' => '',"
            elif d7 and re.search(r"'password'\s*=>\s*", line):
                line = "      'password' => '',"
            elif re.search(r'^\s*$db_url\s*=\s*\S+\s*;', line):
                d6 = True
                line = "$db_url = 'mysqli://xxx:xxx@localhost/xxx';"
            newcontents.append(line)
        if not d7 and not d6:
            raise Exception("Cannot parse Drupal settings file %s" % settingsphp)
        if not os.access(settingsphp, os.W_OK):
            os.system("chmod u+w %s" % settingsphp)
        if not os.access(settingsphp, os.W_OK):
            raise Exception("Unable to modify drupal's settings.php file %s" % settingsphp)
        with open(settingsphp, "w") as f:
            f.write("\n".join(newcontents))
            f.write("\n")
            f.write("\nrequire_once DRUPAL_ROOT . '/../../mysql/%s.php';" % ("d7" if d7 else "d6"))

    def edit_drupal_gitignore(self):
        gitignore = "%s/html/.gitignore" % self.projectdir()
        if not os.path.exists(gitignore):
            raise Exception("Drupal not correctly installed into container; missing %s" % gitignore)
        with open(gitignore, "r") as f:
            contents = f.readlines()
        newcontents = []
        changed = False
        for line in [x.strip("\n") for x in contents]:
            if re.match(r'^sites/\*/settings\*.php$', line):
                line = '#' + line
                changed = True
            newcontents.append(line)
        if changed:
            with open(gitignore, "w") as f:
                f.write("\n".join(newcontents) + "\n")

