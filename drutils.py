from time import localtime, strftime
import re, os, tarfile, random

def system(command):
    print command
    return os.system(command)

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
