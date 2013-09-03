Summary: Drutils - Drupal/Drush Utilities
Name: drutils
Version: 1.9
Release: 15
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
/usr/bin/getent passwd git  || /usr/sbin/useradd -r -m -U git

%post
/bin/chgrp nappl /var/nappl
/bin/chmod g=rwsx /var/nappl
/bin/chgrp nappl /var/drutils /var/drutils/mysql
/bin/chmod g=rwsx /var/drutils /var/drutils/mysql
/bin/chown git.git /deploy
/bin/chmod g=rwsx /deploy
/bin/echo "ServerName `/bin/hostname`:80" > /etc/httpd/conf.d/vsites.conf
/bin/echo "NameVirtualHost *:80" >> /etc/httpd/conf.d/vsites.conf
/bin/echo "Include /var/vsites/conf/*.conf" >> /etc/httpd/conf.d/vsites.conf
/bin/chgrp -R nappl /var/vsites
/bin/chmod -R g=rwsx /var/vsites

%install
rm -rf %{buildroot}
echo make root=%{buildroot}/ prefix=%{buildroot}/usr dest_prefix=/usr install
make root=%{buildroot}/ prefix=%{buildroot}/usr dest_prefix=/usr install

%postun
/usr/sbin/groupdel nappl

%clean
rm -rf %{buildroot}

%files
/usr/lib/drutils/*.py*
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

%changelog
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

