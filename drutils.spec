Summary: Drutils - Drupal/Drush Utilities
Name: drutils
Version: 1.9
Release: 42
License: GPL
Group: Web Development
Source: %{name}-%{version}.tar.gz
URL: http://github.com/nemac/drutils
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-root
Requires: httpd

%description
Drutils is a collection of scripts to make the tasks of creating, backing up, and
restoring Drupal web sites easy.  The scripts are basically wrappers around various
drush commands.

%prep
%setup

%build

%pre
/usr/bin/getent group nappl || /usr/sbin/groupadd -r nappl
/usr/bin/getent passwd git  || /usr/sbin/useradd -r -m -G nappl -U git

%post
/bin/chgrp nappl /var/nappl
/bin/chmod g=rwsx /var/nappl
/bin/chgrp nappl /var/drutils /var/drutils/mysql
/bin/chmod g=rwsx /var/drutils /var/drutils/mysql
/bin/chown git.git /deploy
/bin/chmod g=rwsx /deploy
/usr/lib/drutils/generate-vsites-conf > /etc/httpd/conf.d/vsites.conf
/bin/chgrp -R nappl /var/vsites
/bin/chmod -R g=rwsx /var/vsites
/bin/chgrp -R nappl /dumps
/bin/chmod -R g=rwsx /dumps

%install
rm -rf %{buildroot}
echo make root=%{buildroot}/ prefix=%{buildroot}/usr dest_prefix=/usr install
make root=%{buildroot}/ prefix=%{buildroot}/usr dest_prefix=/usr install

%clean
rm -rf %{buildroot}

%files
/usr/lib/drutils/*.py*
/usr/lib/drutils/generate-vsites-conf
/usr/bin/dumpsite
/usr/bin/loadsite
/usr/bin/makesite
/usr/bin/dbcreate
/usr/bin/dblist
/usr/bin/dbdrop
/usr/bin/dbpw
/usr/bin/nappl
%dir /var/drutils/mysql
%dir /var/nappl
%dir /var/vsites
%dir /var/vsites/conf
%dir /var/vsites/mysql
%dir /deploy
%dir /dumps

%changelog
* Wed Nov 26 2014 Mark Phillips <embeepea@git> 1.9-42
- darn fix typo in new apache conf (embeepea@git)

* Wed Nov 26 2014 Mark Phillips <embeepea@git> 1.9-41
- fix bug in spec file (embeepea@git)

* Wed Nov 26 2014 Mark Phillips <embeepea@git> 1.9-40
- change how vsites.conf is generated, to work with newer Apache versions
  (embeepea@git)
- modify updaterepo to work with new yum repo (embeepea@git)

* Wed Oct 29 2014 Mark Phillips <embeepea@git> 1.9-39
- update deploy hook again (embeepea@git)

* Wed Oct 22 2014 Mark Phillips <embeepea@git> 1.9-38
- update deploy hook again (embeepea@git)

* Tue Sep 30 2014 Mark Phillips <embeepea@git> 1.9-37
- improve deploy post-update hook, again (embeepea@git)

* Tue Sep 30 2014 Mark Phillips <embeepea@git> 1.9-36
- fix another annoying bug (embeepea@git)

* Tue Sep 30 2014 Mark Phillips <embeepea@git> 1.9-35
- add sys import to post-update hook (embeepea@git)

* Tue Sep 30 2014 Mark Phillips <embeepea@git> 1.9-34
- add re import to post-update hook (embeepea@git)

* Tue Sep 30 2014 Mark Phillips <embeepea@git> 1.9-33
- fix typo in post-update hook creation (embeepea@git)

* Tue Sep 30 2014 Mark Phillips <embeepea@git> 1.9-32
- improve deploy post-update hook (embeepea@git)

* Fri Sep 26 2014 Mark Phillips <embeepea@git> 1.9-31
- add submodule updating to git deploy hook (embeepea@git)
- updates README (embeepea@git)
- updates README (embeepea@git)

* Fri Dec 13 2013 Mark Phillips <embeepea@git> 1.9-30
- trivial edit (embeepea@git)

* Fri Dec 13 2013 Mark Phillips <embeepea@git> 1.9-29
- switch nappl back to using drush to download latest Drupal; seems to be
  working now (embeepea@git)

* Mon Nov 04 2013 Mark Phillips <embeepea@git> 1.9-28
- temporarily change nappl to download drupal from dev.nemac.org, as workaround
  for broken drupal.org drush download (embeepea@git)

* Mon Sep 23 2013 Mark Phillips <embeepea@git> 1.9-27
- nappl --type now defaults to "drupal" (embeepea@git)
- drupal installation makes sites/default/files world writable (embeepea@git)
- add additional dependencies to puppet config for full drutils functionality
  testing (embeepea@git)

* Thu Sep 12 2013 Mark Phillips <embeepea@git> 1.9-26
- updaterepo no longer removes old drutils versions from nemac yum repo
  (embeepea@git)
- fix missing container name error message (embeepea@git)
- adds drutils installation to drutils dev VM, to facilitate testing
  (embeepea@git)
- print error message if no container name given; print help if invoked with 0
  options/args (embeepea@git)

* Thu Sep 12 2013 Mark Phillips <embeepea@git> 1.9-25
- DrupalContainer.import_code() makes container deployable and restarts apache
  automatically if possible (embeepea@git)
- ApacheContainer.init() skips projectdir git repo setup if on already exists
  (embeepea@git)
- makeDeployable() silently does nothing if deploy repo already exists
  (embeepea@git)

* Thu Sep 12 2013 Mark Phillips <embeepea@git> 1.9-24
- install now creates /dumps dir (embeepea@git)
- puppet now modifies ssh_config to make outgoing ssh faster (embeepea@git)

* Wed Sep 11 2013 Mark Phillips <embeepea@git> 1.9-23
- verbose output when transferring files given with uri (embeepea@git)
- use underscores, not dashes, in database names (embeepea@git)
- change name of DrupalContainer import code method (embeepea@git)
- --load-db and --load-files now accept file URIs (embeepea@git)
- add uri_open utility class, write dumps into /dumps dir by default now
  (embeepea@git)

* Wed Sep 11 2013 Mark Phillips <embeepea@git> 1.9-22
- better database name generation; better support for importing old d6 sites
  (embeepea@git)
- restructure container so application is in `project` subdir (embeepea@git)

* Tue Sep 10 2013 Mark Phillips <embeepea@git> 1.9-21
- adds --import-drutils-dump option (embeepea@git)
- change --db-dump/--db-load to --dump-db/--load-db, add --dump-files/--load-
  files and --dump-all (embeepea@git)

* Tue Sep 10 2013 Mark Phillips <embeepea@git> 1.9-20
- do not remove git user, nappl group on uninstall (embeepea@git)

* Tue Sep 10 2013 Mark Phillips <embeepea@git> 1.9-19
- DrupalContainer.create() fails gracefully and cleans up if database creation
  fails (embeepea@git)
- DrupalContainer.delete() now correctly deletes incomplete container
  (embeepea@git)

* Wed Sep 04 2013 Mark Phillips <embeepea@git> 1.9-18
- adds git user to nappl group on install (embeepea@git)
- updates README (embeepea@git)
- updates README (embeepea@git)
- updates README (embeepea@git)
- updates README (embeepea@git)
- updates README.md (embeepea@git)
- rename drutils's old README.md to DRUTILS.md; create new README.md for nappl
  (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-17
- change type of drupal app from "apache" to "drupal" (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-16
- fix ownership of /var/vsites on install (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-15
- really include /var/vsites in install (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-14
- install creates /var/vsites (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-13
- install sets /deploy dir ownership to git.git (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-12
- fix problem checking for git user (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-11
- install creates git user, /deploy dir with correct permissions (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-10
- only run vagrant shell provision scripts if necessary; puppet now installs
  hostname entry (embeepea@git)
- adds makeDeployable() Container method, --init now initializes /deploy repo
  automatically (embeepea@git)

* Tue Sep 03 2013 Mark Phillips <embeepea@git> 1.9-9
- fix tabs in Makefile (embeepea@git)
- fix import, namespace issues, add --type=apache option (embeepea@git)
- create ApacheContainer.py (embeepea@git)
- refactor nappl into one py file per class (embeepea@git)
- add --install option (embeepea@git)
- fix existence test for apache symlink (embeepea@git)

* Sun Sep 01 2013 Mark Phillips <embeepea@git> 1.9-8
- adds --db-load option to nappl (embeepea@git)
- adds --db-dump option (embeepea@git)
- fix a few permissions issues (embeepea@git)

* Fri Aug 30 2013 Mark Phillips <embeepea@git> 1.9-7
- make /var/drutils accessible to nappl group (embeepea@git)
- look for .my.cnf in ~/.my.cnf, rather than /root/.my.cnf (embeepea@git)

* Fri Aug 30 2013 Mark Phillips <embeepea@git> 1.9-6
- fix another path issue (embeepea@git)
- fix rpm postun typo, load path issues (vagrant@server.uncanet.unca.edu)

* Fri Aug 30 2013 Mark Phillips <embeepea@git> 1.9-5
- more fixes related to nappl group (embeepea@git)
- create nappl group, give it permissions on /var/nappl (embeepea@git)
- adds nappl (embeepea@git)

* Tue Aug 27 2013 Mark Phillips <embeepea@git> 1.9-4
- make opts arg to get_dbsu() function optional (embeepea@git)

* Mon Aug 19 2013 Mark Phillips <embeepea@git> 1.9-3
- add .vagrant dir to .gitignore (embeepea@git)
- adds file puppet/modules/README.md (embeepea@git)
- adds Vagrantfile and puppet manifests for virtual rpm build environment
  (embeepea@git)

* Mon Aug 19 2013 Mark Phillips <embeepea@git> 1.9-2
- add script for updating yum repo (embeepea@git)

* Mon Aug 19 2013 Mark Phillips <embeepea@git> 1.9-1
- fix version metadata (embeepea@git)
- bump version to 1.9 (embeepea@git)
- fix version number (embeepea@git)
- Automatic commit of package [drutils] minor release [1.8-3].
  (vagrant@server.(none))
- change perms of  /var/drutils/mysql on installation (embeepea@git)
- pass root var from spec file to Makefile (vagrant@server.(none))
- `make install` now creates dir /var/drutils/mysql (vagrant@server.(none))
- add /var/drutils/mysql dir to rpm spec file (vagrant@server.(none))

* Mon Aug 19 2013 Unknown name 1.8-2
- change perms of  /var/drutils/mysql on installation (embeepea@git)
- pass root var from spec file to Makefile (vagrant@server.(none))
- `make install` now creates dir /var/drutils/mysql (vagrant@server.(none))
- add /var/drutils/mysql dir to rpm spec file (vagrant@server.(none))

* Fri Aug 16 2013 Mark Phillips <embeepea@git> 1.8-2
- switch to tito ReleaseTagger (embeepea@git)
- include dbcreate in built rpm (embeepea@git)

* Fri Aug 16 2013 Mark Phillips <embeepea@git> 1.8-1
- store db passwords in /var/drutils/mysql files, add dbcreate script
  (embeepea@git)

* Sun Feb 10 2013 Mark Phillips <embeepea@git> 1.7-1
- tweaked dbdrop (embeepea@git)

* Fri Feb 08 2013 Mark Phillips <embeepea@git> 1.6-1
- adds --dbname option to makesite; fixes #1 (embeepea@git)
- fixes dbdrop, fixes permissions on new sites' files dir; fixes #2
  (embeepea@git)

* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.5-1
- edits DEVNOTES (embeepea@git)
- adds DEVNOTES.md (embeepea@git)
- fix typo in Makefile (embeepea@git)

* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.4-1
- more spec tweaks (embeepea@git)
- tweaks spec file (embeepea@git)

* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.3-1
- tweaks Makefile (embeepea@git)

* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.2-1
- tweaks spec file (embeepea@git)

* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.1-1
- new package built with tito

