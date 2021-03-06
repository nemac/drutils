Drutils - Drupal/Drush Utilities
================================

This project contains a collection of scripts that facilitate managing
Drupal sites with `drush`.  These scripts are written to work on
Linux and Mac OS X systems; they have not been tested on Windows.

All Drutils scripts make use of the concept of a "site root", which is a
top level directory containing a Drupal installation.  Typically the
site root directory corresponds exactly with a web server (Apache)
document root directory for a virtual host, but it is also possible to
have multiple Drupal installations inside the same virtual host.  In
either case, as far as these Drutils scripts are concerned, the site root
always corresponds to the top level of the Drupal installation ---
i.e.  the directory containing Drupal's index.php file.

Normally the SITEROOT argument to all Drutils scripts should be the
absolute path to a Drupal site root directory.  If you create a lot of
Drupal sites under a common parent directory, however, you can use the
environment variable DRUTILS_SITE_PARENT to set a parent directory
that all SITEROOT value will be interpreted relative to; see the
"Environment Variables" section below for details.

`makesite [--dbsu=USER:PASSWORD] [--version=VERSION] SITEROOT`
--------------------------------------------------------------

Create a new Drupal site at the location specified by SITEROOT.
The SITEROOT directory must not already exist, but its parent
directory should already exist, and the user running `makesite`
should have write permission in that parent directory.

By default, `makesite` downloads whatever the latest version of Drupal
is from drupal.org and installs it into SITEROOT.  You can explicitly
specify a different version with the `--version=VERSION` option;
VERSION should be a Drupal version number.  If VERSION is a full
version number, such as "7.10" or "6.12", `makesite` will download
that exact version of Drupal.  If VERSION is a single number, like "7"
or "6", `makesite` will download the latest recommended release of
that major version.

This script needs a database superuser account; see "Database
Superuser Account" below for details.

`makesite` generates a random password for the site database, and also
sets the password for the site's _admin_ user to be the same as the
database password.  If you want the site's _admin_ user to have a
different password, you can change it immediately after `makesite`
finishes by running a command like:

    drush -r SITEROOT user-password admin --password="NEWPASSWORD"


`dumpsite SITEROOT`
-------------------

Creates a gzipped tar dump (.tgz file) containing a snapshot of the
Drupal site (codes, files, and database) with the given SITEROOT.

SITEROOT should be the absolute path to the site's root directory.

The name of the dumpfile will be SITEROOT, with all slashes
replaced by dashes, followed by a timestamp, followed by the
`.tgz` suffix.  For example,

        dumpsite /var/www.foobar.com/html
   
would create a dump file named something like

        var-www.foobar.com-html--2012-08-01--14-36-52.tgz
   
Note that the resulting dumpfile contains everything from the site
being dumped, including the site's settings.php file, which contains
the database password, and the contents of the database, which
contains (hashed copies of) all Drupal user passwords, so you should
treat this dumpfile as senstive.
      
`loadsite [-d SITEROOT ] DUMPFILE`
----------------------------------

Loads a dumpfile written by `dumpsite` into a Drupal SITEROOT. If `-d
SITEROOT` is specified, the site is loaded into the drupal site
currently at SITEROOT.  If `-d SITEROOT` is not specified, the site is
loaded into the SITEROOT that the dumpfile was created from.  In
either case, there must already be a Drupal site currently at
SITEROOT, with valid database connection information in its
settings.php file.  This command will replace that site's code, files,
and database contents with the ones saved in the dumpfile, and it will
adjust the restored site's settings.php file to point to the original
site's database.

This means that after restoring, the site running at SITEROOT will
still use the same database that the site running at that location
used before the restore, but the contents of that database will have
been replaced by the restore process.  

After restoring the site, `loadsite` also sets the password for the
site's _admin_ user to be the same as the database password.  If you
want the site's _admin_ user to have a different password, you can
change it immediately after `makesite` finishes by running a command
like:

    drush -r SITEROOT user-password admin --password="NEWPASSWORD"

`dbpw SITEROOT`
---------------

Print out the database password for the Drupal site at the given
SITEROOT.  This might be the same as the site's _admin_ account
password, if the site was created with `makesite` or loaded with
`loadsite`.

`dblist [--dbsu=USER:PASSWORD]`
-------------------------------

Print out a list of all the MySql databases in the local MySql.
This script needs a database superuser account; see "Database
Superuser Account" below for details.


`dbdrop [--dbsu=USER:PASSWORD] NAME`
------------------------------------

Drop the database and/or user with the given NAME.  This script needs
a database superuser account; see "Database Superuser Account" below
for details.


Database Superuser Account
--------------------------

Some of the Drutils scripts need the ability to connect to the local
MySql server using an account that has the permission to examine and
create databases and users, and to grant privileges. These scripts all
accept an optional argument of the form `--dbsu=USER:PASSWORD`.  If
that argument is present, the database superuser username and password
are taken from it.  If the `--dbsu=USER:PASSWORD` option is not
present, the scripts look for the DRUTILS_DB_SU and DRUTILS_DB_SU_PW
environment variables; see the "Environment Variables" section below
for details.

Environment Variables
---------------------

 * DRUTILS_SITE_PARENT
 * DRUTILS_DB_SU
 * DRUTILS_DB_SU_PW

Will write more about these soon.
