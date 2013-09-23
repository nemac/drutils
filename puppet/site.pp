$server_name = "drutils-dev"
$mysql_root_password = "drutils"

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

exec { disable_selinux_sysconfig:
    command => '/bin/sed -i "s@^\(SELINUX=\).*@\1disabled@" /etc/selinux/config',
    unless  => '/bin/grep -q "SELINUX=disabled" /etc/selinux/config',
}

exec { 'set-hostname':
    command => "/bin/sed -i 's/HOSTNAME=.*/HOSTNAME=${server_name}/' /etc/sysconfig/network",
    unless  => "/bin/grep -q 'HOSTNAME=${server_name}' /etc/sysconfig/network",
}

exec { 'etc-hosts':
    command => "/bin/echo '127.0.0.1 ${server_name}' >> /etc/hosts",
    unless  => "/bin/grep -q '127.0.0.1 ${server_name}' /etc/hosts",
}

file { "/etc/ssh/ssh_config" :
  ensure => present,
  source => "/etc/puppet/files/assets/ssh/ssh_config",
  owner   => "root",
  group   => "root"
}

package { 'emacs-nox':
  ensure => installed
}

package { 'man':
  ensure => installed
}

package { 'make':
  ensure => installed
}

package { 'wget':
  ensure => installed
}

package { 'git':
  ensure => installed
}

class apache-server {

  package { 'httpd':
    ensure => 'present'
  }

  service { 'httpd':
    require => Package['httpd'],
    ensure => running,            # this makes sure httpd is running now
    enable => true                # this make sure httpd starts on each boot
  }

  service { 'iptables':
    ensure => stopped,
    enable => false
  }

  service { 'ip6tables':
    ensure => stopped,
    enable => false
  }

}

class nappl-server {

  file { "/home/git/.ssh":
    require => Package['drutils'],
    ensure  => directory,
    owner   => "git",
    group   => "git",
    mode    => 0700
  }  

  file { "/home/git/.ssh/authorized_keys":
    require => File['/home/git/.ssh'],
    ensure  => present,
    owner   => "git",
    group   => "git",
    mode    => 0600
  }

  group { "admin" :
    ensure => present,
    system => true
  }
  exec { "admin-group-can-sudo":
    require => Group['admin'],
    command => '/bin/chmod u+w /etc/sudoers ; echo "%admin ALL=NOPASSWD: ALL" >> /etc/sudoers ; /bin/chmod u-w /etc/sudoers',
    unless  => '/bin/grep -q "%admin ALL=NOPASSWD: ALL" /etc/sudoers'
  }

#  group { "sudoers" :
#    ensure => present,
#    system => true
#  }
#  file { "/etc/sudoers.d/sudoers_group":
#    ensure => present,
#    content => "%sudoers        ALL=(ALL)       NOPASSWD: ALL",
#    owner => root,
#    group => root,
#    mode => 0440
#  }

  exec { 'vagrant-user-in-git-goup':
    require => Package['drutils'],
    command => '/etc/puppet/files/assets/util/add_user_to_group vagrant git' 
  }
  exec { 'vagrant-user-in-nappl-goup':
    require => Package['drutils'],
    command => '/etc/puppet/files/assets/util/add_user_to_group vagrant nappl' 
  }
  file { '/etc/hosts':
    ensure => present,
    group => nappl,
    mode => 0664
  }
  exec { 'vagrant-user-has-mysql-root-access':
    require => Class["mysql::server"],
    command => '/etc/puppet/files/assets/util/give_user_mysql_root_access vagrant'
  }

}

class { "nappl-server" : }
class { "apache-server" : }

class { 'mysql::server':
  config_hash => { 'root_password' => $mysql_root_password }
}

class { 'mysql::php': }

exec { 'secure-mysql-server' :
    require => Class["mysql::server"],
    command => '/usr/bin/mysql --defaults-extra-file=/root/.my.cnf --force mysql < /etc/puppet/files/assets/mysql/secure.sql'
}

package { 'drutils':
  ensure => installed
}

package { 'php':
  ensure => installed,
}

package { 'php-gd':
  ensure => installed,
}

package { 'php-domxml-php4-php5' :
  ensure => installed,
}

package { 'php-pear':
  ensure => installed
}

exec { 'install-drush' :
    command => '/usr/bin/pear channel-discover pear.drush.org ; /usr/bin/pear install drush/drush ; cd /usr/share/pear/drush/lib ; /bin/mkdir tmp ; cd tmp ; /bin/tar xfz /etc/puppet/files/assets/drush-dependencies/Console_Table-1.1.3.tgz ; /bin/rm -f package.xml ; /bin/mv Console_Table-1.1.3 .. ; cd .. ; /bin/rm -rf tmp',
    unless => '/usr/bin/test -f /usr/bin/drush'
}
