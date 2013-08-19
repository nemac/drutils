Summary: Drutils - Drupal/Drush Utilities
Name: drutils
Version: 1.9
Release: 2
License: GPL
Group: Web Development
Source: %{name}-%{version}.tar.gz
URL: http://github.com/nemac/drutils
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-root

%description
Drutils is a collection of scripts to make the tasks of creating, backing up, and
restoring Drupal web sites easy.  The scripts are basically wrappers around various
drush commands.

%prep
%setup

%build

%install
rm -rf %{buildroot}
echo make root=%{buildroot}/ prefix=%{buildroot}/usr dest_prefix=/usr install
make root=%{buildroot}/ prefix=%{buildroot}/usr dest_prefix=/usr install

%clean
rm -rf %{buildroot}

%files
/usr/lib/drutils/drutils.py*
/usr/bin/dumpsite
/usr/bin/loadsite
/usr/bin/makesite
/usr/bin/dbcreate
/usr/bin/dblist
/usr/bin/dbdrop
/usr/bin/dbpw
%dir /var/drutils/mysql

%changelog
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

