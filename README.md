Nappl
=====

Nappl, which stands for 'Nemac APPLication manager', is a program that
streamlines the deployment and management of applications on a production
server.

Application Containers
----------------------

Nappl makes use of the distinct concepts of *application* and *container*.
An *application* is a collection of software that needs to be managed as
a project and deployed as a unit to a server.  The following are all
examples of applications:

* a static html web site
* a dynamic database-driven web site, such as a Drupal site
* a collection of programs with a crontab entry that arranges
  for certain programs to run repeatedly on a regular schedule

For the purposes of Nappl, each application corresponds to a single
git repository that tracks the history of the files (including
programs) in the application.  Many applications, however, require
more than just the files and programs in their git repository in order
to function.  For example, a static html web site requires that a web
server (apache httpd) be present and running.  A Drupal web site
requires a web server and a MySQL database, and the application's
files need to be modified to contain the connection information
(username, password) for that database.  An application that requires
that a program be run regularly on a repeated basis requires that
a linux user account for that program to run as, and a crontab entry
for that account which schedules the program execution.

Nappl uses the term *container* to refer to the software prerequisites
and configuration settings needed for an application.  Think of a
Nappl container as a thing that can contain an application; it loosely
corresponds to a directory on the system where the application
resides.  (In reality, creating a container for an application often
involves doing much more than just creating a directory for it, such
as creating a database and storing the database connection information
in a place where the application can read it.)

Basic Nappl Usage
-----------------

All Nappl actions are done using the `nappl` command, which takes
various options and/or arguments to control what happens.
Nappl manages a collection of application containers, and applications
contained in those containers.  You can get a list of the currently
available application containers on the system by typing

    nappl --list-containers

Creating a Container
--------------------

To create a new application container, use the `--create-container`
option.  This option requires an additional option `--type` which
specifies the type of application to create a container for; currently
Nappl recognizes the following application types:

  * `--type=apache`, for a static (non-database-driven) web site
  * `--type=drupal` for a Drupal web site with a MySQL database
  * `--type=plain` for an application that is simply a collection of files and
    programs that is not served to the outside world through apache

To create a container for a static html web site called foo.example.org:

    nappl --create-container --type=apache [ --init ] foo.example.org
    
To create a container for a Drupal web site called bar.example.org:

    nappl --create-container --type=drupal [ --init ] bar.example.org
    
If the optional `--init` option is present, Nappl will populate the new
container with a newly created application, including a freshly-initialized
git repository.  The new application's git project will reside at the location
/var/vsites/APPLICATION_NAME (so, /var/vsites/foo.example.org or
/var/vsites/bar.example.org for the above examples).

If the `--init` option is not present, Nappl will create an empty container
for the application, and you will later need to populate that
container with an actual application; see "Populating a Container" below.

Nappl Container Linux Accounts / Crontabs
-------------------------------------------

Each nappl container has a linux user account associated with it, and
may optionally include a file named `crontab` in the top level
directory of the container.  If the `crontab` file exists, it should
be formatted as a regular linux crontab file (see `man 5 crontab` for
details), and it will be registered as the crontab entry for the
container's associated linux account.  This provides a way for a
container to schedule programs to run on the system on a regular
basis.

You can see the name of the user account associated with all current
containers in the output of `nappl --list-containers`.

These linux user accounts, and the associated crontab entries if any,
are created and updated asyncronously by the nappl user manager which
is installed on the system as part of nappl.  The nappl user manager
runs once each minute; each time it runs it scans the system for all
nappl containers, and updates the linux accounts and/or their crontab
entries on the system accordingly (i.e. it creates any accounts for
containers that have been added, deletes accounts for containers which
have been removed, and updates the crontab entry for all containers
based on the presence or absense of their `crontab` files).  The nappl
user manager runs asyncronously once each minute, rather than directly
as a part of what `nappl --create-container` or `nappl
--delete-container` does, because it needs to run as the `root`
user.  Note that this means that there will be a delay of up to a
minute between the time when a nappl container is created, or when a
crontab file is created or deleted from a container, and the moment
when the corresponding user account or crontab entry is created or
updated.

The files and directories that are part of a nappl application are not
owned by the container's linux account -- they are owned by the user
who created the application.  The container's linux account is a
member of the `nappl` linux group, however, which by default has write
access to the files in all nappl applications.

Drutils
-------

*Drutils* was the name of the precursor to Nappl.  Several of the
Drutils utilities are included in Nappl, but they are
being phased out, and generally speaking, should not be used
any more, except to continue managing Drupal sites that have previously
been set up with `drutils`.  Most of the functionality of the `drutils`
scripts has been replaced with functionality in Nappl, and new
development should take place with Nappl.

The old `drutils` README file is still available as
[DRUTILS.md](https://github.com/nemac/nappl/blob/master/DRUTILS.md);
consult that file for documentation for the `drutils` scripts.
