Summary: Drutils - Drupal/Drush Utilities
Name: drutils
Version: 1.5
Release: 1
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
make prefix=%{buildroot}/usr dest_prefix=/usr install

%clean
rm -rf %{buildroot}

%files
/usr/lib/drutils/drutils.py*
/usr/bin/dumpsite
/usr/bin/loadsite
/usr/bin/makesite
/usr/bin/dblist
/usr/bin/dbdrop
/usr/bin/dbpw

%changelog
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

