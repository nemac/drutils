package { 'emacs-nox':
  ensure => installed
}

exec { 'set-hostname':
    command => '/bin/sed -i "s/HOSTNAME=.*/HOSTNAME=drutils-dev/" /etc/sysconfig/network',
    unless  => '/bin/grep -q "HOSTNAME=drutils-dev" /etc/sysconfig/network',
}

exec { 'etc-hosts':
    command => '/bin/echo "127.0.0.1 drutils-dev" > /etc/hosts',
    unless  => '/bin/grep -q "127.0.0.1 drutils-dev" /etc/hosts',
}

package { 'git':
  ensure => installed
}

package { 'rpm-build':
  ensure => installed
}

package { 'redhat-rpm-config':
  ensure => installed
}

package { 'tito':
  ensure => installed
}

file { ["/home/vagrant/rpmbuild",
        "/home/vagrant/rpmbuild/BUILD",
        "/home/vagrant/rpmbuild/RPMS",
        "/home/vagrant/rpmbuild/SOURCES",
        "/home/vagrant/rpmbuild/SPECS",
        "/home/vagrant/rpmbuild/SRPMS" ] :
  ensure => directory,
  owner  => "vagrant",
  group  => "vagrant",
}

file { "/home/vagrant/.rpmmacros" :
  ensure => present,
  content => "%_topdir %(echo \$HOME)/rpmbuild\n",
  owner  => "vagrant",
  group  => "vagrant",
}

### exec { disable_selinux_sysconfig:
###     command => '/bin/sed -i "s@^\(SELINUX=\).*@\1disabled@" /etc/selinux/config',
###     unless  => '/bin/grep -q "SELINUX=disabled" /etc/selinux/config',
### }
### 
### exec { 'set-hostname':
###     command => '/bin/sed -i "s/HOSTNAME=.*/HOSTNAME=cloud1/" /etc/sysconfig/network',
###     unless  => '/bin/grep -q "HOSTNAME=cloud1" /etc/sysconfig/network',
### }
### 
### package { 'man':
###   ensure => installed
### }
### 
### package { 'wget':
###   ensure => installed
### }
### 
### package { 'git':
###   ensure => installed
### }
### 
### class apache-server {
### 
###   package { 'httpd':
###     ensure => 'present'
###   }
### 
###   service { 'httpd':
###     require => Package['httpd'],
###     ensure => running,            # this makes sure httpd is running now
###     enable => true                # this make sure httpd starts on each boot
###   }
### 
###   service { 'iptables':
###     ensure => stopped,
###     enable => false
###   }
### 
###   service { 'ip6tables':
###     ensure => stopped,
###     enable => false
###   }
### 
### }
### 
### class git-server {
### 
###   group { "git":
###           ensure => present,
###           gid => 721
###   }
### 
###   user { "git":
###           ensure => present,
###           uid => 721,
###           gid => "git",
###           require => Group["git"]
###   }
### 
###   file { "/prod":
###     require => User["git"],
###     ensure => directory,
###     owner  => "git",
###     group  => "git",
###     mode => 0755
###   }
### 
###   file { "/git":
###     require => User["git"],
###     ensure => directory,
###     owner  => "git",
###     group  => "git",
###     mode => 0755
###   }
### 
###   file { "/home/git":
###     ensure => directory,
###     owner  => "git",
###     group  => "git",
###     mode => 0755
###   }
### 
###   file { "/home/git/.ssh":
###     require => File["/home/git"],
###     ensure => directory,
###     owner  => "git",
###     group  => "git",
###     mode => 0700
###   }
### 
###   file { "/home/git/.ssh/authorized_keys":
###     require => File["/home/git/.ssh"],
###     ensure => present,
###     owner  => "git",
###     group  => "git",
###     mode => 0644
###   }
### 
### }
### 
### class apache-vsites-server {
### 
###   class { "apache-server": }
###   
###   file { ["/var/vsites", "/var/vsites/conf"] :
###     require => Class["git-server"],
###     ensure => directory,
###     owner  => "git",
###     group  => "git",
###     mode => 0755
###   }
### 
###   file { "/etc/httpd/conf.d/vsites.conf" :
###     require => Class["apache-server"],
###     ensure => present,
### content => "ServerName ${hostname}:80
### NameVirtualHost *:80
### Include /var/vsites/conf/*.conf
### "
###   }
### 
###   file { "/usr/local/bin/makeproj":
###     ensure => present,
###     source => "puppet:///files/assets/vsites/makeproj",
###     mode => 0755
###   }
### 
### }
### 
### class { "git-server" : }
### class { "apache-vsites-server" : }
### 
### import 'assets/mysql/password.pp'
### 
### class { 'mysql::server':
###   config_hash => { 'root_password' => $mysql_root_password }
### }
### 
### class { 'mysql::php': }
### 
### exec { 'secure-mysql-server' :
###     require => Class["mysql::server"],
###     command => '/usr/bin/mysql --defaults-extra-file=/root/.my.cnf --force mysql < /etc/puppet/files/assets/mysql/secure.sql'
### }
### 
### 
### class drutils-server {
### 
###   package { 'drutils':
###     ensure => installed
###   }
### 
###   file { ["/var/drutils", "/var/drutils/mysql"] :
###     ensure => directory,
###     owner  => "root",
###     group  => "root",
###     mode => 0700
###   }
### 
### }
### 
### class { 'drutils-server': }
### 
### ########################################################################
### 
### ###   #                  www.billy.org   puppet:///files/www.billy.org.conf
### ###   define line($file, $line, $ensure = 'present') {
### ###       case $ensure {
### ###           default : { err ( "unknown ensure value ${ensure}" ) }
### ###           present: {
### ###               exec { "/bin/echo '${line}' >> '${file}'":
### ###                   unless => "/bin/grep -qFx '${line}' '${file}'"
### ###               }
### ###           }
### ###           absent: {
### ###               exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
### ###                 onlyif => "/bin/grep -qFx '${line}' '${file}'"
### ###               }
### ###           }
### ###       }
### ###   }
### ###   
### ###   class apache-vhost($vhost_name,    $vhost_source) {
### ###   
### ###     line { "/etc/hosts-${vhost_name}" :
### ###       file => '/etc/hosts',
### ###       line => "127.0.0.1    ${vhost_name}"
### ###     }
### ###   
### ###     file { "/var/${vhost_name}" :
### ###       ensure => directory
### ###     }
### ###   
### ###   #  file { "/var/${vhost_name}/html" :
### ###   #    require => File["/var/${vhost_name}"],
### ###   #    ensure => directory
### ###   #  }
### ###   
### ###     file { "/etc/httpd/conf.d/${vhost_name}.conf" :
### ###       require => [ Package['httpd'], Line["/etc/hosts-${vhost_name}"] ],
### ###       ensure  => file,
### ###       source  => $vhost_source
### ###     }
### ###   
### ###   }
### ###   
### ###   
### ###   class apache-vhost-git($vhost_name, $vhost_source, $git_source) {
### ###   
### ###     class { "apache-vhost" :
### ###       vhost_name   => $vhost_name,
### ###       vhost_source => $vhost_source
### ###     }
### ###   
### ###     package { "git" :
### ###       ensure => present
### ###     }
### ###   
### ###     vcsrepo { $vhost_name:
### ###       require  => Package['git'],
### ###   #   require  => apache-vhost[$vhost_name],
### ###       path     => "/var/www.billy.org/html",
### ###       ensure   => present,
### ###       provider => git,
### ###       source   => $git_source
### ###     }
### ###   
### ###   }
