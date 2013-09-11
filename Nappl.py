import sys, re, os, optparse, shutil, json, drutils, subprocess, time

def bash_command(command):
    """Run command in a bash subshell, and return its output as a string"""
    return subprocess.Popen(['/bin/bash', '-c', command],
                            stdout=subprocess.PIPE).communicate()[0].strip()

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

def git_wd_clean(dir):
    """Return True iff there are no outstanding edits in DIR since the most recent git commit."""
    if re.search(r'working directory clean', bash_command("cd %s ; git status" % dir)):
        return True
    return False

def rmtree(path):
    if os.path.exists(path):
        os.system("chmod -R u+w %s" % path)
        shutil.rmtree(path)
