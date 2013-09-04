Nappl / Drutils
===============

Nappl, which stands for 'NEMAC Application', is a program that
aids in software application development and server deployment.

This project contains the `nappl` program itself, plus the `drutils`
utilities for managing Drupal web sites.  The `drutils` utilities
are being phased out, and generally speaking, should not be used
any more, except to continue managing Drupal sites that have previously
been set up with `drutils`.  Most of the functionality of the `drutils`
scripts has been replaced with functionality in Nappl, and new
development should take place with Nappl.

The old `drutils` README file is still available as
[DRUTILS.md](https://github.com/nemac/drutils/blob/master/DRUTILS.md);
consult that file for documentation for the `drutils` scripts.

Application Containers
======================

Nappl makes use of the distinct concepts of *application* and *container*.
An *application* is any collection of software that needs to be managed as
a project and deployed as a unit to a server.  The following are all
examples of applications:

* a static html web site
* a dynamic database-driven web site, such as a Drupal site
* any dynamic web application
* an sftp site 
* a collection of cron jobs that perform regular tasks
* a MapServer installation that provides OGC web services

For the purposes of Nappl, each application corresponds to a single
git repository that tracks the history of the files (including
programs) in the application.  Many applications, however, require
more than just the files and programs in their git repository in order
to function.  For example, a static html web site requires that a web
server (apache httpd) be present and running.  A Drupal web site
requires a web server and a MySQL database, and the application's
files need to be modified to contain the connection information
(username, password) for that database.

Nappl uses the term *container* to refer to the software prerequisites
and configuration settings needed for an application.  Think of a
Nappl container as a thing that can contain an application; it loosely
corresponds to a directory on the system where the application
resides.  (In reality, creating a container for an application often
involves doing much more than just creating a directory for it, such
as creating a database and storing the database connection information
in a place where the application can read it.)

Basic Nappl Usage
=================

All Nappl actions are done using the `nappl` command, which takes
various options and/or arguments to control what happens.
Nappl manages a collection of application containers, and applications
contained in those containers.  You can get a list of the currently
available application containers on the system by typing

    nappl --list-containers

Creating a Container
====================

To create a new application container, use the `--create-container`
option.  This option requires an additional option `--type` which
specifies the type of application to create a container for; currently
Nappl recognizes `--type=apache`, for a static html web site, and
`--type=drupal` for a Drupal web site.

To create a container for a static html web site called foo.example.org:

    nappl --create-container --type=apache [ --init ] foo.example.org
    
To create a container for a Drupal web site called bar.example.org:

    nappl --create-container --type=apache [ --init ] bar.example.org
    
If the optional `--init` option is present, Nappl will populate the new
container with a newly created application, including a freshly-initialized
git repository.  The new application's git project will reside at the location
/var/vsites/APPLICATION_NAME (so, /var/vsites/foo.example.org or
/var/vsites/bar.example.org for the above examples).

bla bla don't forget to `sudo service httpd restart`

If the `--init` option is not present, Nappl will create an empty container
for the application, and you will later need to populate that
container with an actual application; see "Populating a Container" below.

Populating a Container
======================

bla bla how to populate an empty container

bla bla don't forget to `sudo service httpd restart`
