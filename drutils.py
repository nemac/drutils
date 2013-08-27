from time import localtime, strftime
import re, os, tarfile, random, ConfigParser

def system(command):
    #print command
    return os.system(command)

def common_usage():
    print "See https://github.com/nemac/drutils/blob/master/README.md for more details."

def command_success(command):
    # Execute a command in a subshell and return True if it ran successfully, False if not
    return system(command)==0

def generate_dumpfile_name(SITEROOT):
    # Create the dumpfile name, by changing the slashes in SITEROOT to dashes,
    # and appending the timestamp and the ".tgz" suffix.  Also remove any leading
    # slash, so the dumpfile name won't start with a dash.
    s = re.sub(r'^/', '', SITEROOT);
    return "%s--%s.tgz" % (re.sub(r'/', '-', s), strftime("%Y-%m-%d--%H-%M-%S", localtime()))

def get_dumpfile_base(dumpfile):
    # Return the base part of a dumpfile name --- that is, everything except the ".tgz" suffix:
    return re.sub(r'\.tgz$', '', dumpfile)

def get_base_timestamp(base):
    # Return the timestamp part of a dumpfile name or base
    match = re.search(r'\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2}', base)
    if match:
        return match.group(0)
    return ""

def standardize_siteroot(SITEROOT):
    # If SITEROOT is not an absolute path (starts with a '/'), and if there is no
    # directory at SITEROOT interpreted as a relative path, return a modified
    # copy of SITEROOT which has been prepended with the value of the
    # DRUTILS_SITE_PARENT environment variable, if such an environment variable
    # is set.  If there is no such env var, return SITEROOT unmodified.
    #
    # This function does NOT validate that the resulting SITEROOT value is
    # a valid Drupal site root directory.
    #
    SITEROOT = re.sub(r'/$', '', SITEROOT) # remove any trailing '/' from SITEROOT
    if SITEROOT.startswith("/"):
        return SITEROOT
    if os.path.exists(SITEROOT):
        return SITEROOT
    if 'DRUTILS_SITE_PARENT' not in os.environ:
        return SITEROOT
    parent = re.sub(r'/$', '', os.environ['DRUTILS_SITE_PARENT'])
    return os.path.join(parent, SITEROOT)

def validate_siteroot(SITEROOT):
    # Return True or False, depending on whether SITEROOT seems to be
    # a valid Drupal site root directory.  This checks for the
    # existence of sites/default/settings.php, and also checks to make
    # sure that the database connection details in that file can be
    # used to successfully connect to a database.
    if not os.path.exists(os.path.join(SITEROOT,"sites/default/settings.php")):
        return False
    sql_connect = os.popen('(cd %s ; drush sql-connect)' % SITEROOT).read().strip()
    if sql_connect == '':
        return False
    if not command_success("%s -e 'select count(*) from users' > /dev/null 2>&1" % sql_connect):
        return False
    return True

def get_drupal_version(SITEROOT):
    # Return an array of two numbers: [N,M], where N = drupal major version,
    # M = drupal minor version, for a given SITEROOT.  For example, for a SITEROOT
    # running Drupal 7.10, this function would return [7,10].
    for line in os.popen('(cd %s ; drush status)' % SITEROOT).read().split("\n"):
        match = re.search(r'^\s*Drupal version\s*:\s*([^\.]+)\.([^\.]+)$', line)
        if match:
            return [match.group(1), match.group(2)]
    return None

def get_siteroot_from_dumpfile(dumpfile):
    f = tarfile.open(dumpfile, 'r')
    m = f.getmember('MANIFEST.ini')
    fp = f.extractfile(m)
    docroot = None
    for line in fp:
        match = re.search(r'docroot\s*=\s*"([^"]*)"', line)
        if match:
            docroot = match.group(1)
            break
    fp.close()
    f.close()
    return docroot

def find_arg(string, arg):
    # Search a string for a substring of the form
    #    --arg=value
    # and return the value part
    match = re.search(r'--%s=(\S*)' % arg, string)
    if match:
        return match.group(1)
    return None

def get_db_url(siteroot):
    # Return a Drupal-6 style db-url for a given site root
    sql_connect = os.popen('drush -r %s sql-connect' % siteroot).read().strip()
    database = find_arg(sql_connect, "database")
    host = find_arg(sql_connect, "host")
    user = find_arg(sql_connect, "user")
    password = find_arg(sql_connect, "password")
    return "mysql://%s:%s@%s/%s" % (user,password,host,database)

def get_db_password(name):
    cnf = "/var/drutils/mysql/%s.cnf" % name
    if not os.path.exists(cnf):
        raise Exception("No password for database/user %s found." % name)
    c = parse_ini(cnf)
    if 'client' not in c:
        raise Exception("No password for database/user %s found." % name)
    return c['client']['password']


def generate_random_password():
    random.seed()
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm',
               'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M',
               'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    N = 10
    chars = []
    for i in range(0,N):
        if (random.random() < 0.67):
            chars.append(letters[ random.randint(0,len(letters)-1) ])
        else:
            chars.append(digits[ random.randint(0,len(digits)-1) ])
    return "".join(chars)


def validate_db_su_credentials(db_su, db_su_pw):
    # Check to make sure that the specified superuser credentials (db_su is username, db_su_pw is password)
    # can be used to connect to MySql
    result = os.popen(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"select count(*) as COUNT from db\"") % (
            db_su,
            db_su_pw)).read()
    # This checks to make sure that the result of the above query consists of COUNT followed by a number:
    return re.search(r'COUNT\s+\d+', result)!=None

def database_user_exists(user, db_su, db_su_pw):
    # Return True if the specified database user exists, False if not
    result = os.popen(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"select User from user where User='%s'\"") % (
            db_su,
            db_su_pw,
            user)).read()
    # Above query results are empty if user does not exists
    return result!=''

def database_exists(db, db_su, db_su_pw):
    # Return True if the specified database exists, False if not
    result = os.popen(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"select Db from db where Db='%s'\"") % (
            db_su,
            db_su_pw,
            db)).read()
    # Above query results are empty if database does not exists
    return result!=''

def get_databases(db_su, db_su_pw):
    # Return a list of all databases
    result = os.popen(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"select Db from db\"") % (
            db_su,
            db_su_pw)).read()
    return [d for d in  result.split("\n") if (d != 'Db' and d != '')]

def confirm_with_yes(prompt):
    ans = raw_input(prompt)
    return ans.lower()=="yes"

def create_database_and_user(name, db_su, db_su_pw):
    # Create a new database and user by the same same, giving that user full privs in that database
    success = command_success(("mysqladmin --host=localhost --user=%s --password=%s create %s") % (
            db_su,
            db_su_pw,
            name))
    if not success:
        raise Exception("database creation failed")
    password = generate_random_password()
    success = command_success(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"grant all privileges on %s.* to '%s'@'localhost' identified by '%s'\"") % (
            db_su,
            db_su_pw,
            name,name,password))
    if not success:
        raise Exception("user creation failed")
    cnf = "/var/drutils/mysql/%s.cnf" % name
    f = open(cnf, "w")
    f.write("[client]\n")
    f.write("user=%s\n" % name)
    f.write("password=%s\n" % password)
    f.close()
    os.chmod(cnf, 0600)

def drop_user(user, db_su, db_su_pw):
    # Delete the given user from MySql
    success = command_success(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"drop user %s@localhost\"") % (
            db_su,
            db_su_pw,
            user))
    return success

def drop_database(db, db_su, db_su_pw):
    # Delete the given user from MySql
    success = command_success(("mysql --database=mysql --host=localhost --user=%s --password=%s "
                      + "-e \"drop database %s\"") % (
            db_su,
            db_su_pw,
            db))
    return success

def parse_ini(file):
    '''This function parses an INI-style conf file, and returns a python
dict object containing its contents.  For example, the file

   [client]
   user=foo
   password="bar"
   [stuff]
   x=3

would result in the following dict object:

  {
     'client' : {
       'user' : 'foo',
       'password' : 'bar'
     },
     'stuff' : {
       'x' : '3'
     }
   }

This function also strips off any quotes which delimit variable values, as
illustrated by the "password" variable in the above example.'''
    h = {}
    Config = ConfigParser.ConfigParser()
    try:
        Config.read(file)
        for section in Config.sections():
            if section not in h:
                h[section] = {}
            for option in Config.options(section):
                val = Config.get(section, option)
                val = re.sub(r'^"(.*)"$', '\\1', val)
                val = re.sub(r"^'(.*)'$", '\\1', val)
                h[section][option] = val
    except:
        pass
    return h

def add_dbsu_option(parser):
    parser.add_option("--dbsu", help='optional dbsu stuff', dest="dbsu", type="string")

def get_dbsu(opts=None):
    # check for --dbsu command-line option, and if found, use values from it:
    if opts and opts.dbsu:
        m = re.match(r'^([^:]+):(.*)$', opts['dbsu'])
        if m:
            DB_SU    = m.group(1)
            DB_SU_PW = m.group(2)
            return (DB_SU, DB_SU_PW)
        return (None,None)

    #
    # If we didn't get DB_SU info from the args, check for it in environment vars:
    # 
    if ("DRUTILS_DB_SU" in os.environ) and ('DRUTILS_DB_SU_PW' in os.environ):
        DB_SU    = os.environ['DRUTILS_DB_SU']
        DB_SU_PW = os.environ['DRUTILS_DB_SU_PW']
        return (DB_SU, DB_SU_PW)

    #
    # If we still don't have DB_SU, try to read it from /root/.my.cnf; this will
    # work only if the user running this script has permission to read that file.
    # 
    try:
        cfg = parse_ini("/root/.my.cnf")
        if 'client' in cfg:
            DB_SU    = cfg['client']['user']
            DB_SU_PW = cfg['client']['password']
            return (DB_SU, DB_SU_PW)
    except:
        pass

    return (None,None)
