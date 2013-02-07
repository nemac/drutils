from time import localtime, strftime
import re, os

def system(command):
    #print command
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

