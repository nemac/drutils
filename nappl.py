#! /usr/bin/python

import sys, re, os, optparse, shutil, json, drutils

# The following is in support of running unit tests, to allow them to run without
# incurring the wait associated with actually downloading drupal.  The DRUSH_DL_COMMAND
# normally contains the drush command to download a copy of drupal into the 'html'
# subdir of the current directory.  The 'test' script uses an environment variable of
# the same name to replace this command with one that simply unpacks a locally stored
# drupal archive file.
def drush_dl_command():
    if 'DRUSH_DL_COMMAND' in os.environ:
        return os.environ['DRUSH_DL_COMMAND']
    return 'drush dl drupal --drupal-project-rename=html'

def drush_site_install_command(appname, dbname, dbpassword):
    if 'DRUSH_SITE_INSTALL_COMMAND' in os.environ:
        return os.environ['DRUSH_SITE_INSTALL_COMMAND']
    return (" drush --yes site-install standard"
            + " '--db-url=mysql://%s:%s@localhost/%s'"
            + " '--site-name=%s'"
            ) % (dbname, dbpassword, dbname, appname)

class DatabaseError(Exception):
    pass

def infer_database_name(name):
    m = re.match(r'^([^\.]+).*$', name)
    if m:
        return m.group(1)
    return None

def create_database(dbname):
    (DB_SU, DB_SU_PW) = drutils.get_dbsu()
    if drutils.database_exists(dbname, DB_SU, DB_SU_PW):
        raise DatabaseError("There is already a mysql database named '%s'." % dbname)
    if drutils.database_user_exists(dbname, DB_SU, DB_SU_PW):
        raise DatabaseError("There is already a mysql user named '%s'." % dbname)
    drutils.create_database_and_user(dbname, DB_SU, DB_SU_PW)
    return True

def edit_drupal_settingsphp(vsitesdir, appname):
    settingsphp = "%s/html/sites/default/settings.php" % vsitesdir
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
        newcontents.append(line)
    with open(settingsphp, "w") as f:
        f.write("\n".join(newcontents) + "\n")
        if d7:
            f.write("\nrequire_once DRUPAL_ROOT . '/../../mysql/foobar.nemac.org/d7.php';\n")

def edit_drupal_gitignore(vsitesdir):
    gitignore = "%s/html/.gitignore" % vsitesdir
    if not os.path.exists(gitignore):
        raise Exception("Drupal not correctly installed into container; missing html/.gitignore")
    with open(gitignore, "r") as f:
        contents = f.readlines()
    newcontents = []
    changed = False
    for line in [x.strip("\n") for x in contents]:
        if re.match(r'settings\.php', line):
            line = '#' + line
            changed = True
    newcontents.append(line)
    if changed:
        with open(gitignore, "w") as f:
            f.write("\n".join(newcontents) + "\n")


class EtcHoster:
    """Utility class to manage adding/removing lines from /etc/hosts corresponding
    to an application name.  Only attempts to modify /etc/hosts if the user running
    the program has permission to do so; otherwise, silently does nothing."""
    def __init__(self, appname):
        self.appname = appname
        self.appline = "127.0.0.1    %s    # this line written by nappl" % appname
        self.etchosts = "/etc/hosts"
    def add_line(self):
        """Add the line for this app to /etc/hosts, if one is not already there."""
        if not os.access(self.etchosts, os.W_OK):
            return
        haveline = False
        # store all the lines, without newlines
        with open(self.etchosts, "r") as f:
            lines = [x.strip("\n") for x in f.readlines()]
        # check to see if we have a line for this app
        for line in lines:
            if line == self.appline:
                haveline = True
                break
        # if we didn't, write all the lines, followed by our app line
        if not haveline:
            with open(self.etchosts, "w") as f:
                for line in lines:
                    f.write(line + "\n")
                f.write(self.appline + "\n")
    def remove_lines(self):
        """Remove all lines corresponding to this app from /etc/hosts."""
        if not os.access(self.etchosts, os.W_OK):
            return
        changed = False
        # read and store all the lines, without newlines
        with open(self.etchosts, "r") as f:
            lines = [x.strip("\n") for x in f.readlines()]
        changed = False
        lines2 = []
        # copy them into lines2 array, skipping any that match our app line
        for line in lines:
            if line == self.appline:
                changed = True
            else:
                lines2.append(line)
        # if we skipped any lines, write the lines2 lines to the file
        if changed:
            with open(self.etchosts, "w") as f:
                for line in lines2:
                    f.write(line + "\n")

class NapplMeta:
    def __init__(self, appName):
        self.appName = appName
        self.dir = "/var/nappl/%s" % self.appName
        self.datafile = "/var/nappl/%s/metadata.json" % self.appName
        self.data = {}
    def load(self):
        with open(self.datafile, 'r') as f:
            self.data = json.loads(f.read())
    def save(self):
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        with open(self.datafile, 'w') as f:
            f.write(json.dumps(self.data, sort_keys=True, indent=2, separators=(',', ': ')))

class Container:
    def __init__(self, appName):
        self.appName = appName

    @staticmethod
    def list_containers():
        """Return a list of the current application containers; each entry in the list
        is a python dict containing metadata about the application."""
        if not os.path.exists("/var/nappl"):
            raise Exception("/var/nappl directory not found")
        apps = []
        for appname in os.listdir("/var/nappl"):
            a = NapplMeta(appname)
            a.load()
            apps.append(a.data)
        return apps


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
        shutil.rmtree(mysql_credentials_dir)
        # delete the nappl metadata dir
        meta = NapplMeta(self.appName)
        if os.path.exists(meta.dir):
            shutil.rmtree(meta.dir)
        # delete the vsites dir for the app
        vsitesdir = "/var/vsites/%s" % self.appName
        if os.path.exists(vsitesdir):
            shutil.rmtree(vsitesdir)
        # delete the apache conf symlink
        apacheconf_symlink = "/var/vsites/conf/%s.conf" % self.appName
        if os.path.exists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
        EtcHoster(self.appName).remove_lines()

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
        if os.path.exists(apacheconf_symlink):
            os.remove(apacheconf_symlink)
        os.symlink(apacheconf, apacheconf_symlink)
