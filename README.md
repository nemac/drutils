DRUTILS - Drupal/Drush Utilities
================================

This project contains a collection of scripts that facilitate managing
Drupal sites with `drush`.  These scripts are writtent to work on
Linux and Mac OS X systems; they have not been tested on Windows.

All of these scripts make use of the concept of a SITEROOT, which is a
top-level directory containing a Drupal installation.  Typically the
SITEROOT directory corresponds exactly with a web server (Apache)
document root directory for a virtual host, but it is also possible to
have multiple Drupal installations inside the same virtual host.  In
either case, as far as these DRUTILS scripts are concerned, SITEROOT
always corresponds to the top level of the Drupal installation ---
i.e.  the directory containing Drupal's index.php file.

* dumpsite SITEROOT

  Creates a gzipped tar dump (.tgz file) containing a snapshot of the
  Drupal site with the given SITEROOT.  This dump file will contain a
  dump of the site MySQL database as well as copies of all files in
  the SITEROOT directory structure, with the single exception of the
  `sites/default/settings.php` file, which is not included.
  
  The copying process also does NOT follow symbolic links, so any
  files in symlinked directories that are outside SITEROOT will not be
  included. (The symbolic links themselves are included, however).
  
  SITEROOT should be the absolute path to the site's root directory.
  The dump file records the value of SITEROOT in the dump file, to
  facilitate reloading the dumpfile into the same site later using
  `loadsite`.
  
  The name of the dumpfile will be SITEROOT, with all slashes
  replaced by dashes, followed by a timestamp, followed by the
  `.tgz` suffix.  For example,
  
      dumpsite /var/www.foobar.com/html
      
   would create a dump file named something like

      var-www.foobar.com-html--2012-08-01--14-36-52.tgz
      
   Note that the resulting dumpfile does not contain the site's
   `sites/default/settings.php` file, so it does not include sensitive
   database password details.  It does include a dump of the Drupal
   database, however, which includes hashed copies of all Drupal
   user passwords, so it's best to treat the dumpfile as sensitive
   material.
      
* loadsite [-d SITEROOT ] DUMPFILE

  Loads a dumpfile written by `dumpsite` into a Drupal SITEROOT.  This
  involves doing the following:
  
    1. Save a copy of the current `SITEROOT/sites/default/settings.php` file
    2. Delete all existing files in SITEROOT
    3. Restore the files from the dumpfile into SITEROOT
    4. Replace `SITEROOT/sites/default/settings.php` with the one
       saved in step 1 above
    5. Delete everything (data and tables) from the site database
    6. Restore everything (data and tables) in the site database from the
       dumpfile

  Note that this process preseves the database connection details (usename,
  password, port, etc) details for the site.  The process will clear out
  the contents of the database, replacing them with the contents from
  the dumpfile, but the database password is not modified.
  
  Note also that `loadsite` requires that SITEROOT already be set up
  as a Drupal siteroot directory, with a working database, and a
  `sites/default/settings.php` file containing valid Drupal database
  connection details.
