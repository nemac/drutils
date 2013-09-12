import sys, re, os, optparse, shutil, json, drutils, subprocess, time, urllib2, urlparse, random

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
    name = re.sub(r'^www\.', '', name) # remove any "www." prefix
    name = re.sub(r'\..*$', '', name)  # remove everything after the first "."
    name = name[0:12]                  # truncate to the 1st 12 chars
    name = re.sub(r'-', '_', name)     # replace all '-' with '_'
    # get list of existing databases
    (DB_SU, DB_SU_PW) = drutils.get_dbsu()
    dblist = drutils.get_databases(DB_SU, DB_SU_PW)
    # if name is nonempty and is not in the list of databases, use it
    if name != "" and name not in dblist:
        return name
    # if name is empty, use "nappl"
    if name == "":
        name = "nappl"
    # find the first unused name of the form NAME-DDD:
    i = 1
    while True:
        dbname = "%s_%03d" % (name, i)
        if dbname not in dblist:
            break
        ++i
    return dbname

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

class uri_transfer(object):
    """This is like uri_open() below, but returns the name of a local file to read from,
    rather than an open file object."""
    def __init__(self, uri, verbose=False):
        self.uri = uri
        self.tmpfile = None
        self.verbose = verbose
    def generate_tmpfile_name(self):
        random.seed()
        filename = "/tmp/uri_transfer_%s_%05d" % (os.getpid(),random.randint(100,99999))
        return filename
    def __enter__(self):
        self.parsed_uri = urlparse.urlparse(self.uri)
        if (self.parsed_uri.scheme == "http"
            or self.parsed_uri.scheme == "https"
            or self.parsed_uri.scheme == "ftp"):
            if self.verbose:
                print "transferring %s" % self.uri
            res = urllib2.urlopen(self.uri)
            self.tmpfile = self.generate_tmpfile_name()
            with open(self.tmpfile, "w") as f:
                for line in res.readlines():
                    f.write(line)
            return self.tmpfile
        elif self.parsed_uri.scheme == "ssh":
            m = re.match(r'^(([^@]+)@)?([^:]+)(:(\d+))?$', self.parsed_uri.netloc)
            if not m:
                raise Exception("cannot parse ssh url")
            username = m.group(2)
            host = m.group(3)
            port = m.group(5)
            if port is None:
                port = 22
            self.tmpfile = self.generate_tmpfile_name()
            scp = "scp -q %s%s%s:%s %s" % (
                ("-P %s " % port) if port != 22 else "",
                (username+"@") if username else "",
                host,
                self.parsed_uri.path,
                self.tmpfile
                )
            if self.verbose:
                print "transferring %s" % self.uri
            if os.system(scp) != 0:
                raise Exception('transfer of file % failed' % self.uri)
            return self.tmpfile
        elif self.parsed_uri.scheme == "":
            return self.uri

    def __exit__(self, type, value, traceback):
        if self.tmpfile:
            os.remove(self.tmpfile)

class uri_open(uri_transfer):
    """This class can be used in the python `with` statement to read from a file specified with
    a variety of URIs.  Usage is like this:

        with uri_open(URI) as f:
            for line in f.readlines():
                print line

    The object assigned to the `as` variable (`f` in the code above) is a regular python file
    object which has been opened for reading, so you call any of the normal file object methods
    on it.  The file object is automatically closed when the `with` statement finishes (or if
    it triggers an exception).

    The URI may be simply a string, which refers to a file on the local system, or a URL
    using the `http`, `https`, or `ftp` protocol, or a URI using the ssh protocol.  The
    following are all valid values for URI:

        * foo.txt
        * path/to/foo.txt
        * /var/lib/path/to/foo.txt
        * http://www.example.com/path/to/foo.txt
        * https://www.example.com/path/to/foo.txt
        * ssh://www.example.com/path/to/foo.txt
        * ssh://user@www.example.com/path/to/foo.txt
        * ssh://user@www.example.com:port/path/to/foo.txt

    """
    def __init__(self, uri, verbose=False):
        super(uri_open, self).__init__(uri,verbose)
    def __enter__(self):
        self.f = open(super(uri_open, self).__enter__(), "r")
        return self.f
    def __exit__(self, type, value, traceback):
        self.f.close()
        super(uri_open, self).__exit__(type, value, traceback)
