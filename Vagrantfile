# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box     = "centos-6.4-base"
  config.vm.box_url = "http://dev.nemac.org/boxes/CentOS-6.4-base.box"

  config.vm.synced_folder ".", "/vagrant"

  # Use shell provisioner to install puppet yum repo, puppet, epel repo:
  config.vm.provision :shell, :inline => <<-HEREDOC
    if test ! -f /usr/bin/puppet ; then rpm -Uvh http://yum.puppetlabs.com/el/6/products/i386/puppetlabs-release-6-7.noarch.rpm ; yum -y install puppet ; fi
    if test ! -f /etc/yum.repos.d/epel.repo ; then rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm ; fi
    exit 0
  HEREDOC


  # use puppet provisioner to install everything else (see details in puppet/site.pp)
  config.vm.provision :puppet,
    :options => ["--fileserverconfig=/vagrant/puppet/fileserver.conf"] do
      |puppet|
    puppet.module_path    = "puppet/modules"
    puppet.manifests_path = "puppet"
    puppet.manifest_file  = "site.pp"
  end
end
