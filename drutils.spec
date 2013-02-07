Summary: Drutils - Drupal/Drush Utilities
Name: drutils
Version: 1.2
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
%makeinstall

%clean
rm -rf %{buildroot}

%files
${_libdir}/drutils.py
${_bindir}/dumpsite
${_bindir}/loadsite
${_bindir}/makesite
${_bindir}/dblist
${_bindir}/dbdrop
${_bindir}/dbpw

%changelog
* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.2-1
- tweaks spec file (embeepea@git)

* Thu Feb 07 2013 Mark Phillips <embeepea@git> 1.1-1
- new package built with tito

