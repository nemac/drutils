actions:

* provision server
* create a 'git container' for a deployable application

  - create an apache virtualhost
  - create a database/user
* edit an application in place in its container
* deploy an application to a container

------------------------------------------------------------------------

* create a drupal project:
    makeproj foobar.nemac.org
    sudo dbcreate foobar
    cd /var/vsites/foobar.nemac.org
    drush dl drupal --drupal-project-rename=html
    cd /var/vsites/foobar.nemac.org/html
    drush site-install standard '--db-url=mysql://foobar:ZW8YtaNz4x@localhost/foobar' \
         --site-name=foobar.nemac.org
    edit sites/default/settings.php:
      - remove the database settings from it (set all values to empty string)
      - append the following line to the end:
           include "../../mysql/foobar.nemac.org-database.php";

------------------------------------------------------------------------

operations:
  * create a new server
  * create a container for an application
  * start a new application project in a container
  * check out an existing application project into a container
  * configure a container as a deploy destination
  * deploy an application to a deploy destination
      git remote add production git@cloud1.nemac.org:deploy/foobar.nemac.org.git
      git push production master

------------------------------------------------------------------------

nappl
  --create-container --type=drupal [ OPTIONS ] foobar.nemac.org
      + creates a database & user named 'foobar'
      + creates /var/vsites/mysql/foobar.nemac.org/{d7,d6}.php
      + does not create /var/vsites/foobar.nemac.org, unless --init or --clone option is given
      + OPTIONS:
        --dbname=NAME
          + use NAME for the name of the database to be created, instead of 'foobar'
        --init
          + create the dir /var/vsites/foobar.nemac.org
          + in the dir /var/vsites/foobar.nemac.org:
            + create an initial site.conf file
            + download the latest dist of drupal into a subdir named 'html'
            + do a drupal install into the database for this container
            + edit the settings.php file to load the database settings from ../../mysql/foobar.nemac.org/d7.ph
            + create a .gitignore file
            + intialize a new git project and do an initial commit with everything that is here
          + runs `napps --install foobar.nemac.org`
        --clone=REPO
          + use git to clone a copy of REPO into the dir /var/vsites/foobar.nemac.org
          + runs `napps --install foobar.nemac.org`
  --install foobar.nemac.org          
    + creates a symlink /var/vsites/conf/foobar.nemac.org.conf -> ../foobar.nemac.org/site.conf
  --delete-container foobar.nemac.org
    + deletes the given container, along with any application contained in it

------------------------------------------------------------------------

/
|
|-- etc/
|     |
|     |-- httpd/
|           |
|           |-- conf.d/
|                 |
|                 | - vsites.conf
|   
|-- var/
|     | 
|     |-- vsites/
|           |   
|           |-- conf/
|           |     |
|           |     |-- foobar.nemac.org.conf
|           |  
|           |-- foobar.nemac.org/
|           |     |
|           |     |-- .git/
|           |     |-- site.conf
|           |     |-- html/
|           |
|           |-- mysql/                  
|                 |                     
|                 |-- foobar.nemac.org/ 
|                       |               
|                       |-- d7.php      
|                       |-- d6.php      
|    
|-- drutils/
      | 
      |-- mysql/
            | 
            |-- foobar.cnf

