.. _installation:

============
Installation
============

.. _sec:installation:

This document will guide you through the process of installing
Singularity from source with the version and location of your choice.

----------------
Before you begin
----------------

If you have an earlier version of Singularity installed, you should
remove it before executing the installation commands.

These instructions will build Singularity from source on your system.
So you will need to have some development tools installed. If you run
into missing dependencies, try installing them WITH ``apt-get`` or ``yum/rpm`` as shown below.

.. code-block:: none

    $ sudo apt-get update && \

        sudo apt-get install \

        python \

        dh-autoreconf \

        build-essential \

        libarchive-dev


.. code-block:: none

    $ sudo yum update && \

        sudo yum groupinstall 'Development Tools' && \

        sudo yum install libarchive-devel


-------------------------
Install from a tag
-------------------------

The following commands will install a tagged version of the `GitHub
repo <https://github.com/sylabs/singularity>`_ to ``/usr/local``.
This will work for pre 3.0 tags.

.. code-block:: none

    $ git clone https://github.com/sylabs/singularity.git

    $ cd singularity

    $ git fetch --all

    $ git tag -l

    $ git checkout [TAG]

    $ ./autogen.sh

    $ ./configure --prefix=/usr/local --sysconfdir=/etc

    $ make

    $ sudo make install


Singularity will be installed in the ``/usr/local`` directory hierarchy by default.
And if you specify a custom directory with the ``--prefix`` option, all of
Singularity's binaries and the configuration file will be installed within that
directory. This last option can be useful if you want to install multiple versions
of Singularity, install Singularity on a shared system, or if you want to remove
Singularity easily after installing it.

If you omit the ``--sysconfdir`` option , the configuration file will be installed in ``/usr/local/etc``.
If you omit the ``--prefix`` option, Singularity will be installed in the ``/usr/local`` directory
hierarchy by default. And if you specify a custom directory with the ``--prefix``
option, all of Singularity’s binaries and the configuration file will be installed within that directory.

--------------------------
Install a specific release
--------------------------

The following commands will install a specific release from `GitHub
releases <https://github.com/sylabs/singularity/releases>`_ page to ``/usr/local``.

.. code-block:: none

    $ VER=2.5.1

    $ wget https://github.com/sylabs/singularity/releases/download/$VER/singularity-$VER.tar.gz

    $ tar xvf singularity-$VER.tar.gz

    $ cd singularity-$VER

    $ ./configure --prefix=/usr/local --sysconfdir=/etc

    $ make

    $ sudo make install


------------------------------
Install the development branch
------------------------------

The primary development of Singularity now happens on the ``master`` branch.
Please see the ``INSTALL.md`` file in a copy of the repository.


---------------------
Remove an old version
---------------------

Let's say that we installed Singularity to ``/usr/local``. To remove it completely,
you need to hit all of the following:

.. code-block:: none

    $ sudo rm -rf /usr/local/libexec/singularity

    $ sudo rm -rf /usr/local/etc/singularity

    $ sudo rm -rf /usr/local/include/singularity

    $ sudo rm -rf /usr/local/lib/singularity

    $ sudo rm -rf /usr/local/var/lib/singularity/

    $ sudo rm /usr/local/bin/singularity

    $ sudo rm /usr/local/bin/run-singularity

    $ sudo rm /usr/local/etc/bash_completion.d/singularity

    $ sudo rm /usr/local/man/man1/singularity.1


If you modified the system configuration directory, remove the ``singularity.conf`` file
there as well.
If you installed Singularity in a custom directory, you need only
remove that directory to uninstall Singularity. For instance if you
installed singularity with the ``--prefix=/some/temp/dir`` option argument pair, you can remove
Singularity like so:

.. code-block:: none

    $ sudo rm -rf /some/temp/dir

What should you do next? You can check out the :ref:`quickstart <quick-start>` guide, or learn how to
interact with your container via the :ref:`shell <shell-command>` , :ref:`exec <exec-command>` , or :ref:`run <run-command>` commands. Or click **next**
below to continue reading.

-------------------
Install on Windows
-------------------

Setup
=====

First, install the following software:

- install `Git for Windows <https://git-for-windows.github.io/>`_

- install `VirtualBox for Windows <https://www.virtualbox.org/wiki/Downloads>`_

- install `Vagrant for Windows <https://www.vagrantup.com/downloads.html>`_

- install `Vagrant Manager for Windows <http://vagrantmanager.com/downloads/>`_

Singularity Vagrant Box
=======================

We are maintaining a set of Vagrant Boxes via `Vagrant Cloud <https://www.vagrantup.com/>`_, one of `Hashicorp <https://www.hashicorp.com/#open-source-tools>`_ many tools that likely you’ve used and haven’t known it. The current stable version of Singularity is available here:

- `sylabs/singularity-2.4 <https://app.vagrantup.com/singularityware/boxes/singularity-2.4/versions/2.4>`_

For other versions of Singularity see `our Vagrant Cloud repository <https://app.vagrantup.com/singularityware>`_

Run GitBash. The default home directory will be C:\Users\your_username

.. code-block:: none

    mkdir singularity-2.4

    cd singularity-2.4


Note that if you had installed a previous version of the vm (and are using the same folder), you must destroy it first. In our example we create a new folder. To destroy a previous vm:

.. code-block:: none

    vagrant destroy

Then issue the following commands to bring up the Virtual Machine:

.. code-block:: none

    vagrant init singularityware/singularity-2.4

    vagrant up

    vagrant ssh


You are then ready to go with Singularity 2.4!

.. code-block:: none

    vagrant@vagrant:~$ which singularity

    /usr/local/bin/singularity

    vagrant@vagrant:~$ singularity --version

    2.4-dist


    vagrant@vagrant:~$ sudo singularity build growl-llo-world.simg shub://vsoch/hello-world

    Cache folder set to /root/.singularity/shub

    Progress |===================================| 100.0%

    Building from local image: /root/.singularity/shub/vsoch-hello-world-master.simg

    Building Singularity image...

    Singularity container built: growl-llo-world.simg

    Cleaning up...

    vagrant@vagrant:~$ ./growl-llo-world.simg

    RaawwWWWWWRRRR!!


Note that when you do ``vagrant up`` you can also select the provider, if you use vagrant for multiple providers. For example:

.. code-block:: none

    vagrant up --provider virtualbox


although this isn’t entirely necessary if you only have it configured for virtualbox.


----------------
Install on Linux
----------------

Installation from Source
========================

You can try the following two options:

Option 1: Download latest stable release
----------------------------------------

You can always download the latest tarball release from `GitHub <https://github.com/sylabs/singularity/releases>`_

For example, here is how to download version ``2.5.2`` and install:

.. code-block:: none

    VERSION=2.5.2

    wget https://github.com/sylabs/singularity/releases/download/$VERSION/singularity-$VERSION.tar.gz

    tar xvf singularity-$VERSION.tar.gz

    cd singularity-$VERSION

    ./configure --prefix=/usr/local

    make

    sudo make install


Note that when you configure, ``squashfs-tools`` is **not** required, however it is required for full functionality. You will see this message after the configuration:

.. code-block:: none

    mksquashfs from squash-tools is required for full functionality

If you choose not to install ``squashfs-tools``, you will hit an error when you try a pull from Docker Hub, for example.

Option 2: Download the latest development code
----------------------------------------------

To download the most recent development code, you should use Git and do the following:

.. code-block:: none

    git clone https://github.com/sylabs/singularity.git

    cd singularity

    ./autogen.sh

    ./configure --prefix=/usr/local

    make

    sudo make install



.. note::
    The ‘make install’ is required to be run as root to get a properly installed Singularity implementation. If you do not run it as root, you will only be able to launch Singularity as root due to permission limitations.

Prefix in special characters
----------------------------

If you build Singularity with a non-standard ``--prefix`` argument, please be sure to review the `admin guide <https://www.sylabs.io/guides/2.5.2/admin-guide/>`_ for details regarding the ``--localstatedir`` variable. This is especially important in environments utilizing shared filesystems.

Updating
--------

To update your Singularity version, you might want to first delete the executables for the old version:

.. code-block:: none

    sudo rm -rf /usr/local/libexec/singularity

And then install using one of the methods above.


Debian Ubuntu Package
=====================

Singularity is available on Debian (and Ubuntu) systems starting with Debian stretch and the Ubuntu 16.10 yakkety releases.
The package is called ``singularity-container``. For recent releases of singularity and backports for older Debian and Ubuntu releases,
we recommend that you use the `NeuroDebian repository <http://neuro.debian.net/pkgs/singularity-container.html>`_.

Testing first with Docker
-------------------------

If you want a quick preview of the NeuroDebian mirror, you can do this most easily with the NeuroDebian Docker image (and if you don’t, skip to the next section). Obviously you should have `Docker installed <https://docs.docker.com/engine/installation/linux/ubuntu/>`_ before you do this.

First we run the ``neurodebian`` Docker image:

.. code-block:: none

    $ docker run -it --rm neurodebian

Then we update the cache (very quietly), and look at the ``singularity-container`` policy provided:

.. code-block:: none

    $ apt-get update -qqq

    $ apt-cache policy singularity-container

    singularity-container:

      Installed: (none)

      Candidate: 2.3-1~nd80+1

      Version table:

        2.3-1~nd80+1 0

          500 http://neuro.debian.net/debian/ jessie/main amd64 Packages



You can continue working in Docker, or go back to your host and install Singularity.

Adding the Mirror and installing
--------------------------------

You should first enable the NeuroDebian repository following instructions on the `NeuroDebian <http://neuro.debian.net/>`_ site. This means using the dropdown menus to find the correct mirror for your operating system and location. For example, after selecting Ubuntu 16.04 and selecting a mirror in CA, I am instructed to add these lists:

.. code-block:: none

    sudo wget -O- http://neuro.debian.net/lists/xenial.us-ca.full | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list

    sudo apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9


and then update

.. code-block:: none

    sudo apt-get update

then singularity can be installed as follows:

.. code-block:: none

    sudo apt-get install -y singularity-container

During the above, if you have a previously installed configuration, you might be asked if you want to define a custom configuration/init, or just use the default provided by the package, eg:

.. code-block:: none

    Configuration file '/etc/singularity/init'

      ==> File on system created by you or by a script.

      ==> File also in package provided by package maintainer.

        What would you like to do about it ?  Your options are:

          Y or I  : install the package maintainer's version

          N or O  : keep your currently-installed version

            D     : show the differences between the versions

            Z     : start a shell to examine the situation

    The default action is to keep your current version.

    *** init (Y/I/N/O/D/Z) [default=N] ? Y


    Configuration file '/etc/singularity/singularity.conf'

      ==> File on system created by you or by a script.

      ==> File also in package provided by package maintainer.

        What would you like to do about it ?  Your options are:

          Y or I  : install the package maintainer's version

          N or O  : keep your currently-installed version

            D     : show the differences between the versions

            Z     : start a shell to examine the situation

    The default action is to keep your current version.

    *** singularity.conf (Y/I/N/O/D/Z) [default=N] ? Y


And for a user, it’s probably well suited to use the defaults. For a cluster admin, we recommend that you read the `admin docs <https://www.sylabs.io/guides/2.5.2/admin-guide/>`_ to get a better understanding of the configuration file options available to you. Remember that you can always tweak the files at ``/etc/singularity/singularity.conf`` and ``/etc/singularity/init`` if you want to make changes.

After this install, you should confirm that ``2.3-dist`` is the version installed:

.. code-block:: none

    $ singularity --version

      2.4-dist


Note that if you don’t add the NeuroDebian lists, the version provided will be old (e.g., 2.2.1). If you need a backport build of the recent release of Singularity on those or older releases of Debian and Ubuntu, you can `see all the various builds and other information here <http://neuro.debian.net/pkgs/singularity-container.html>`_.

Build an RPM from source
========================

Like the above, you can build an RPM of Singularity so it can be more easily managed, upgraded and removed. From the base Singularity source directory do the following:

.. code-block:: none

    ./autogen.sh

    ./configure

    make dist

    rpmbuild -ta singularity-*.tar.gz

    sudo yum install ~/rpmbuild/RPMS/*/singularity-[0-9]*.rpm


.. note::

     If you want to have the RPM install the files to an alternative location, you should define the environment variable ‘PREFIX’ to suit your needs, and use the following command to build:

.. code-block:: none

    PREFIX=/opt/singularity

    rpmbuild -ta --define="_prefix $PREFIX" --define "_sysconfdir $PREFIX/etc" --define "_defaultdocdir $PREFIX/share" singularity-*.tar.gz



When using ``autogen.sh`` If you get an error that you have packages missing, for example on Ubuntu 16.04:

.. code-block:: none

    ./autogen.sh

    +libtoolize -c

    ./autogen.sh: 13: ./autogen.sh: libtoolize: not found

    +aclocal

    ./autogen.sh: 14: ./autogen.sh: aclocal: not found

    +autoheader

    ./autogen.sh: 15: ./autogen.sh: autoheader: not found

    +autoconf

    ./autogen.sh: 16: ./autogen.sh: autoconf: not found

    +automake -ca -Wno-portability

    ./autogen.sh: 17: ./autogen.sh: automake: not found


then you need to install dependencies:

.. code-block:: none

    sudo apt-get install -y build-essential libtool autotools-dev automake autoconf

Build an DEB from source
========================

To build a deb package for Debian/Ubuntu/LinuxMint invoke the following commands:

.. code-block:: none

    $ fakeroot dpkg-buildpackage -b -us -uc # sudo will ask for a password to run the tests

    $ sudo dpkg -i ../singularity-container_2.3_amd64.deb


Note that the tests will fail if singularity is not already installed on your system. This is the case when you run this procedure for the first time. In that case run the following sequence:

.. code-block:: none

    $ echo "echo SKIPPING TESTS THEYRE BROKEN" > ./test.sh

    $ fakeroot dpkg-buildpackage -nc -b -us -uc # this will continue the previous build without an initial 'make clean'


Install on your Cluster Resource
================================

In the case that you want Singularity installed on a shared resource, you will need to talk to the administrator of the resource. Toward this goal, we’ve prepared a :ref:`helpful guide <installation-request>` that you can send to him or her. If you have unanswered questions, please `reach out <https://www.sylabs.io/contact/>`_..


--------------
Install on Mac
--------------

This recipe demonstrates how to run Singularity on your Mac via Vagrant and Ubuntu. The recipe requires access to ``brew`` which is a package installation subsystem for OS X. This recipe may take anywhere from 5-20 minutes to complete.

Setup
=====

First, install brew if you do not have it already.

.. code-block:: none

    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


Next, install Vagrant and the necessary bits.

.. code-block:: none

    brew install cask virtualbox

    brew install cask vagrant

    brew install cask vagrant-manager


Option 1: Singularity Vagrant Box
=====================================

We are maintaining a set of Vagrant Boxes via `Vagrant Cloud <https://www.vagrantup.com/>`_, one of `Hashicorp <https://www.hashicorp.com/#open-source-tools>`_ many tools that likely you’ve used and haven’t known it. The current stable version of Singularity is available here:

- `singularityware/singularity-2.4 <https://app.vagrantup.com/singularityware/boxes/singularity-2.4/versions/2.4>`_

For other versions of Singularity see `our Vagrant Cloud repository <https://app.vagrantup.com/singularityware>`_.

.. code-block:: none

    mkdir singularity-vm

    cd singularity-vm


Note that if you have installed a previous version of the vm, you can either destroy it first, or create a new directory.

.. code-block:: none

    vagrant destroy

Then issue the following commands to bring up the Virtual Machine:

.. code-block:: none

    vagrant init singularityware/singularity-2.4

    vagrant up

    vagrant ssh


You are then ready to go with Singularity 2.4!

.. code-block:: none

    vagrant@vagrant:~$ which singularity

    /usr/local/bin/singularity

    vagrant@vagrant:~$ singularity --version

    2.4-dist


    vagrant@vagrant:~$ sudo singularity build growl-llo-world.simg shub://vsoch/hello-world

    Cache folder set to /root/.singularity/shub

    Progress |===================================| 100.0%

    Building from local image: /root/.singularity/shub/vsoch-hello-world-master.simg

    Building Singularity image...

    Singularity container built: growl-llo-world.simg

    Cleaning up...

    vagrant@vagrant:~$ ./growl-llo-world.simg

    RaawwWWWWWRRRR!!



Note that when you do ``vagrant up`` you can also select the provider, if you use vagrant for multiple providers. For example:

.. code-block:: none

    vagrant up --provider virtualbox


although this isn’t entirely necessary if you only have it configured for virtualbox.


Option 2: Vagrant Box from Scratch (more advanced alternative)
==============================================================

If you want to get more familiar with how Vagrant and VirtualBox work, you can instead build your own Vagrant Box from scratch. In this case, we will use the Vagrantfile for ``bento/ubuntu-16.04``, however you could also try any of the `other bento boxes <https://atlas.hashicorp.com/bento>`_ that are equally delicious. As before, you should first make a separate directory for your Vagrantfile, and then init a base image.

.. code-block:: none

    mkdir singularity-2.4

    cd singularity-2.4

    vagrant init bento/ubuntu-16.04


Next, build and start the vagrant hosted VM, and you will install Singularity by sending the entire install script as a command (with the ``-c`` argument). You could just as easily shell into the box first with vagrant ssh, and then run these commands on your own. To each bento, his own.

.. code-block:: none

    vagrant up --provider virtualbox


    # Run the necessary commands within the VM to install Singularity

    vagrant ssh -c /bin/sh <<EOF

        sudo apt-get update

        sudo apt-get -y install build-essential curl git sudo man vim autoconf libtool

        git clone https://github.com/sylabs/singularity.git

        cd singularity

        ./autogen.sh

        ./configure --prefix=/usr/local

        make

        sudo make install

    EOF



At this point, Singularity is installed in your Vagrant Ubuntu VM! Now you can use Singularity as you would normally by logging into the VM directly

.. code-block:: none

    vagrant ssh

Remember that the VM is running in the background because we started it via the command ``vagrant up``. You can shut the VM down using the command ``vagrant halt`` when you no longer need it.

--------------------------
Requesting an Installation
--------------------------

How do I ask for Singularity on my local resource?
==================================================

Installation of a new software is no small feat for a shared cluster resource. Whether you are an administrator reading this, or a user that wants a few talking points and background to share with your administrator, this document is for you. Here we provide you with some background and resources to learn about Singularity. We hope that this information will be useful to you in making the decision to build reproducible containers with Singularity

Information Resources
=====================

Background
----------

- Frequently Asked Questions is a good first place to start for quick question and answer format.

- Singularity Publication: Reviews the history and rationale for development of the Software, along with comparison to other container software available at the time.

- Documentation Background is useful to read about use cases, and goals of the Software.

Security
--------

- Administrator Control: The configuration file template is the best source to learn about the configuration options that are under the administrator’s control.

- Security Overview discusses common security concerns

Presentations
-------------

- Contributed Content is a good source of presentations, tutorials, and links.



.. _installation-request:

Installation Request
====================

Putting all of the above together, a request might look like the following:

.. code-block:: none

    Dear Research Computing,


    We are interested in having an installation of the Singularity software (https://sylabs.github.io) installed on our cluster. Singularity containers will allow us to build encapsulated environments, meaning that our work is reproducible and we are empowered to choose all dependencies including libraries, operating system, and custom software. Singularity is already installed on over 50 centers internationally (http://singularity.lbl.gov/citation-registration) including TACC, NIH,

    and several National Labs, Universities, Hospitals. Importantly, it has a vibrant team of developers, scientists, and HPC administrators that invest heavily in the security and development of the software, and are quick to respond to the needs of the community. To help learn more about Singularity, I thought these items might be of interest:


      - Security: A discussion of security concerns is discussed at https://www.sylabs.io/guides/2.5.2/user-guide/introduction.html#security-and-privilege-escalation

      - Installation: https://www.sylabs.io/guides/2.5.2/admin-guide/


    If you have questions about any of the above, you can email the list (singularity@lbl.gov) or join the slack channel (singularity-container.slack.com) to get a human response. I can do my best to facilitate this interaction if help is needed. Thank you kindly for considering this request!

    Best,

    User

As is stated in the letter above, you can always `reach out <https://www.sylabs.io/contact/>`_ to us for additional questions or support.
