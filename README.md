DRUTILS - Drupal/Drush Utilities
================================

This project contains a collection of scripts that facilitate managing
Drupal sites with `drush`.  These scripts are written to work on
Linux and Mac OS X systems; they have not been tested on Windows.

All of these scripts make use of the concept of a SITEROOT, which is a
top level directory containing a Drupal installation.  Typically the
SITEROOT directory corresponds exactly with a web server (Apache)
document root directory for a virtual host, but it is also possible to
have multiple Drupal installations inside the same virtual host.  In
either case, as far as these DRUTILS scripts are concerned, SITEROOT
always corresponds to the top level of the Drupal installation ---
i.e.  the directory containing Drupal's index.php file.

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
