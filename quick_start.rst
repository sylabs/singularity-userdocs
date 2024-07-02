.. _quick-start:

###########
Quick Start
###########

.. _sec:quickstart:

This guide is intended for running {Singularity} on a computer where you have
root (administrative) privileges, and will install {Singularity} from source
code. Other installation options, including building an RPM package and
installing {Singularity} without root privileges, are discussed in the
`installation section of the admin guide
<https://sylabs.io/guides/{adminversion}/admin-guide/installation.html>`__.

If you need to request an installation on your shared resource, see the section
on :ref:`requesting an installation <installation-request>` for information to
send to your system administrator.

For any additional help or support contact the Sylabs team:
https://www.sylabs.io/contact/

.. _quick-installation:

************************
Quick Installation Steps
************************

You will need a Linux system to run {Singularity} natively. Options for
using {Singularity} on Mac and Windows machines, along with alternate
Linux installation options, are discussed in the `installation section of
the admin guide
<https://sylabs.io/guides/{adminversion}/admin-guide/installation.html>`__.

If you have an existing version of {Singularity} installed from source, which
you wish to upgrade or remove / uninstall, see the `installation section of the
admin guide
<https://sylabs.io/guides/{adminversion}/admin-guide/installation.html>`__.

Prerequisites
=============

.. _sec:sysdeps:

Install system dependencies
---------------------------

You must first install development tools and libraries to your host.

On Debian-based systems, including Ubuntu:

.. code::

   # Ensure repositories are up-to-date
   sudo apt-get update
   # Install debian packages for dependencies
   sudo apt-get install -y \
      autoconf \
      automake \
      cryptsetup \
      git \
      libfuse-dev \
      libglib2.0-dev \
      libseccomp-dev \
      libtool \
      pkg-config \
      runc \
      squashfs-tools \
      squashfs-tools-ng \
      uidmap \
      wget \
      zlib1g-dev

On versions 8 or later of RHEL / Alma Linux / Rocky Linux, as well as on Fedora:

.. code::

   # Install basic tools for compiling
   sudo dnf groupinstall -y 'Development Tools'
   # Install RPM packages for dependencies
   sudo dnf install -y \
      autoconf \
      automake \
      crun \
      cryptsetup \
      fuse3-devel \
      git \
      glib2-devel \
      libseccomp-devel \
      libtool \
      squashfs-tools \
      wget \
      zlib-devel

On SLES / openSUSE Leap:

.. code::

   # Install RPM packages for dependencies
   sudo zypper in \
    autoconf \
    automake \
    cryptsetup \
    fuse3-devel \
    gcc \
    gcc-c++ \
    git \
    glib2-devel \
    libseccomp-devel \
    libtool \
    make \
    pkg-config \
    runc \
    squashfs \
    wget \
    zlib-devel

Install sqfstar / tar2sqfs for OCI-mode
---------------------------------------

If you intend to use the :ref:`OCI mode <oci_runtime>` of {Singularity}, your
system must provide either:

* ``squashfs-tools`` / ``squashfs`` >= 4.5, which provides the ``sqfstar``
  utility. Note that older versions of these packages, provided by many
  distributions, do not include ``sqfstar``.
* ``squashfs-tools-ng``, which provides the ``tar2sqfs`` utility. This is not
  packaged by all distributions.

Below are instructions on how to obtain one of these two utilities on various
distributions.

Debian / Ubuntu
^^^^^^^^^^^^^^^

On Debian/Ubuntu ``squashfs-tools-ng`` is available in the distribution
repositories. It has been included in the :ref:`Install system dependencies
<sec:sysdeps>` step above. No further action is necessary.

Fedora
^^^^^^

On Fedora, the ``squashfs-tools`` package, included in the :ref:`Install system
dependencies <sec:sysdeps>` step above, includes `sqfstar`. No further action is
necessary.

RHEL / Alma Linux / Rocky Linux
"""""""""""""""""""""""""""""""

On RHEL and derivatives, the ``squashfs-tools-ng`` package is now available in
the EPEL repositories.

Follow the `EPEL Quickstart <https://docs.fedoraproject.org/en-US/epel/#_quickstart>`__
for you distribution to enable the EPEL repository. Install ``squashfs-tools-ng`` with
``dnf``.

.. code::

   sudo dnf install squashfs-tools-ng


SLES / openSUSE Leap
^^^^^^^^^^^^^^^^^^^^

On SLES/openSUSE, follow the instructions at the `filesystems
project <https://software.opensuse.org//download.html?project=filesystems&package=squashfs>`_
to obtain a more recent ``squashfs`` package, which provides ``sqfstar``.

Next steps
----------

You are now ready to install {Singularity}. There are 3 broad steps to
installing {Singularity} itself:

#. :ref:`Installing Go <install>`
#. :ref:`Downloading {Singularity} <download>`
#. :ref:`Compiling {Singularity} Source Code <compile>`

.. _install:

Install Go
==========

{Singularity} is written in Go, and may require a newer version of Go than is
available in the repositories of your distribution. We recommend installing the
latest version of Go from the `official binaries <https://golang.org/dl/>`_.

{Singularity} aims to maintain support for the two most recent stable versions
of Go. This corresponds to the Go Release Maintenance Policy and Security
Policy, ensuring critical bug fixes and security patches are available for all
supported language versions.

.. note::

   If you have previously installed Go from a download, rather than an operating
   system package, it is important that you remove your ``go`` directory, e.g.
   ``rm -r /usr/local/go``, before installing a newer version. Extracting a new
   version of Go over an existing installation can lead to errors when building
   Go programs, as it may leave behind old files, which have been removed or
   replaced in newer versions.

Visit the `Go Downloads page <https://golang.org/dl/>`_ and pick a package
archive suitable to the environment you are in. Once the download is complete,
extract the archive to ``/usr/local`` (or follow other instructions on the Go
installation page). Alternatively, follow the commands here, making sure to
replace specific values as needed:

.. code::

   $ export VERSION=1.21.0 OS=linux ARCH=amd64 && \
     wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
     sudo tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
     rm go$VERSION.$OS-$ARCH.tar.gz

Set the Environment variable ``PATH`` to point to Go:

.. code::

   $ echo 'export PATH=/usr/local/go/bin:$PATH' >> ~/.bashrc && \
     source ~/.bashrc

.. _download:

Download {Singularity} from a release
=====================================

You can download {Singularity} from one of the releases. To see a full
list, visit `the GitHub release page
<https://github.com/sylabs/singularity/releases>`_. After deciding on a
release to install, you can run the following commands to proceed with
the installation.

.. code::

   $ export VERSION={InstallationVersion} && \
       wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz && \
       tar -xzf singularity-ce-${VERSION}.tar.gz && \
       cd singularity-ce-${VERSION}

.. note::

   Do not attempt to build {Singularity} from the *Source code (zip)* or *Source
   code (tar.gz)* archives that are auto-generated by GitHub. These do not
   include some of the required internal dependencies needed to build
   {Singularity}. Instead, to build {Singularity} from source, use the archive
   named **singularity-ce-${VERSION}.tar.gz**.

.. _compile:

Compile the {Singularity} source code
=====================================

Now you are ready to build {Singularity}. Internal dependencies will be
automatically downloaded. You can build {Singularity} using the following
commands:

.. code::

   $ ./mconfig && \
       make -C builddir && \
       sudo make -C builddir install

.. note::

   {Singularity} must be installed as root to function properly.

***************************************
Overview of the {Singularity} Interface
***************************************

{Singularity}'s :ref:`command line interface <cli>` allows you to build and
interact with containers transparently. You can run programs inside a container
as if they were running on your host system. You can easily redirect I/O, use
pipes, pass arguments, and access files, sockets, and ports on the host system
from within a container.

The ``help`` command gives an overview of {Singularity} options and subcommands
as follows:

.. code::

  $ singularity help

  Linux container platform optimized for High Performance Computing (HPC) and
  Enterprise Performance Computing (EPC)

  Usage:
    singularity [global options...]

  Description:
    Singularity containers provide an application virtualization layer enabling
    mobility of compute via both application and environment portability. With
    Singularity one is capable of building a root file system that runs on any
    other Linux system where Singularity is installed.

  Options:
    -c, --config string   specify a configuration file (for root or
                          unprivileged installation only) (default
                          "/usr/local/etc/singularity/singularity.conf")
    -d, --debug           print debugging information (highest verbosity)
    -h, --help            help for singularity
        --nocolor         print without color output (default False)
    -q, --quiet           suppress normal output
    -s, --silent          only print errors
    -v, --verbose         print additional information
        --version         version for singularity

  Available Commands:
    build       Build a Singularity image
    cache       Manage the local cache
    capability  Manage Linux capabilities for users and groups
    completion  Generate the autocompletion script for the specified shell
    config      Manage various singularity configuration (root user only)
    delete      Deletes requested image from the library
    exec        Run a command within a container
    help        Help about any command
    inspect     Show metadata for an image
    instance    Manage containers running as services
    key         Manage OpenPGP keys
    keyserver   Manage singularity keyservers
    oci         Manage OCI containers
    overlay     Manage an EXT3 writable overlay image
    plugin      Manage Singularity plugins
    pull        Pull an image from a URI
    push        Upload image to the provided URI
    registry    Manage authentication to OCI/Docker registries
    remote      Manage singularity remote endpoints
    run         Run the user-defined default command within a container
    run-help    Show the user-defined help for an image
    search      Search a Container Library for images
    shell       Run a shell within a container
    sif         Manipulate Singularity Image Format (SIF) images
    sign        Add digital signature(s) to an image
    test        Run the user-defined tests within a container
    verify      Verify digital signature(s) within an image
    version     Show the version for Singularity

  Examples:
    $ singularity help <command> [<subcommand>]
    $ singularity help build
    $ singularity help instance start


  For additional help or support, please visit https://www.sylabs.io/docs/

Information about individual subcommands can also be viewed by using the
``help`` command:

.. code::

  $ singularity help verify
  Verify digital signature(s) within an image

  Usage:
    singularity verify [verify options...] <image path>

  Description:
    The verify command allows a user to verify one or more digital signatures
    within a SIF image.

    Key material can be provided via PEM-encoded file, or via the PGP keyring. To
    manage the PGP keyring, see 'singularity help key'.

  Options:
    -a, --all                                verify all objects
        --certificate string                 path to the certificate
        --certificate-intermediates string   path to pool of intermediate
                                             certificates
        --certificate-roots string           path to pool of root certificates
    -g, --group-id uint32                    verify objects with the
                                             specified group ID
    -h, --help                               help for verify
    -j, --json                               output json
        --key string                         path to the public key file
        --legacy-insecure                    enable verification of
                                             (insecure) legacy signatures
    -l, --local                              only verify with local key(s)
                                             in keyring
        --ocsp-verify                        enable online revocation check
                                             for certificates
    -i, --sif-id uint32                      verify object with the specified ID
    -u, --url string                         specify a URL for a key server


  Examples:
    Verify with a public key:
    $ singularity verify --key public.pem container.sif

    Verify with PGP:
    $ singularity verify container.sif


  For additional help or support, please visit https://www.sylabs.io/docs/

{Singularity} uses positional syntax (i.e., the order of commands and options
matters). Global options affecting the behavior of all commands follow
immediately after the main ``singularity`` command. Then come subcommands,
followed by their options and arguments.

For example, to pass the ``--debug`` option to the main ``singularity``
command and run {Singularity} with debugging messages on:

.. code::

   $ singularity --debug run library://lolcow

To pass the ``--containall`` option to the ``run`` command and run a
{Singularity} image in an isolated manner:

.. code::

   $ singularity run --containall library://lolcow

{Singularity} 2.4 introduced the concept of command groups. For
instance, to list Linux capabilities for a particular user, you would
use the ``list`` command in the ``capability`` command group, as
follows:

.. code::

   $ singularity capability list myuser

Container authors might also write help docs specific to a container, or for an
internal module called an "app". If those help docs exist for a particular
container, you can view them as follows:

.. code::

   $ singularity inspect --helpfile container.sif  # See the container's help, if provided

   $ singularity inspect --helpfile --app=foo foo.sif  # See the help for the app foo, if provided

*************************
Download pre-built images
*************************

You can use the ``search`` command to locate groups, collections, and
containers of interest on the `Container Library
<https://cloud.sylabs.io/library>`_ .

.. code::

   $ singularity search tensorflow
   Found 22 container images for amd64 matching "tensorflow":

       library://ajgreen/default/tensorflow2-gpu-py3-r-jupyter:latest
               Current software: tensorflow2; py3.7; r; jupyterlab1.2.6
               Signed by: 1B8565093D80FA393BC2BD73EA4711C01D881FCB

       library://bensonyang/collection/tensorflow-rdma_v4.sif:latest

       library://dxtr/default/hpc-tensorflow:0.1

       library://emmeff/tensorflow/tensorflow:latest

       library://husi253/default/tensorflow:20.01-tf1-py3-mrcnn-2020.10.07

       library://husi253/default/tensorflow:20.01-tf1-py3-mrcnn-20201014

       library://husi253/default/tensorflow:20.01-tf2-py3-lhx-20201007

       library://irinaespejo/default/tensorflow-gan:sha256.0c1b6026ba2d6989242f418835d76cd02fc4cfc8115682986395a71ef015af18

       library://jon/default/tensorflow:1.12-gpu
               Signed by: D0E30822F7F4B229B1454388597B8AFA69C8EE9F

       ...

You can use the :ref:`pull <singularity_pull>` and :ref:`build
<singularity_build>` commands to download pre-built images from an external
resource like the `Container Library <https://cloud.sylabs.io/library>`_ or
`Docker Hub <https://hub.docker.com/>`_.

Using the ``pull`` subcommand
=============================

When called on a native {Singularity} image like those provided by the Container
Library, ``pull`` simply downloads the image file to your system:

.. code::

   $ singularity pull library://lolcow

You can also use ``pull`` with a ``docker://`` URI to reference Docker
images served from a registry. In this case, ``pull`` does not just
download an image file. Docker images are stored in layers, so ``pull``
must also combine those layers into a usable {Singularity} file.

.. code::

   $ singularity pull docker://sylabsio/lolcow

Pulling docker images may reduce reproducibility: if you were to pull a
Docker image today and then wait six months and pull it again, you are
not guaranteed to get the same image from docker on both occasions. If
any of the source layers of the docker image has changed, the image will
be altered. You can get around this by pulling docker images *by
digest*, as follows:

.. code::

   $ singularity pull docker://alpine@sha256:69665d02cb32192e52e07644d76bc6f25abeb5410edc1c7a81a10ba3f0efb90a

.. note::

   {Singularity} will make a SIF image out of the underlying docker
   image; and because SIF images contain metadata (including
   timestamps), resulting {Singularity} images will not be bit-for-bit
   identical, even if they are created from docker images that were
   pulled by digest.

If reproducibility is a priority for you, the best option is to always build
your images from the `Container Library <https://cloud.sylabs.io/library>`_ if
possible.

Using the ``build`` subcommand
===============================

You can also use the ``build`` command to download pre-built images from
an external resource. When using ``build`` you must specify a name for
your container like so:

.. code::

   $ singularity build ubuntu.sif library://ubuntu

   $ singularity build lolcow.sif docker://sylabsio/lolcow

Unlike ``pull``, ``build`` will convert your image to the latest {Singularity}
image format after downloading it. ``build`` is like a “Swiss Army knife” for
container creation. In addition to downloading images, you can use ``build`` to
create images from other images, or from scratch using a :ref:`definition file
<definition-files>`. You can also use ``build`` to convert an image between the
container formats supported by {Singularity}. To see a comparison of the
{Singularity} definition file with Dockerfile, please see: :ref:`this section
<sec:deffile-vs-dockerfile>`.

.. _cowimage:

***********************
Interacting with images
***********************

You can interact with images in several ways, each of which can accept image
URIs in addition to local image paths.

As an example, the following command will pull a ``lolcow_latest.sif`` image
from the Container Library:

.. code::

   $ singularity pull library://lolcow

Shell
=====

The :ref:`shell <singularity_shell>` command allows you to spawn a new shell
within your container and interact with it as though it were a virtual machine.

.. code::

   $ singularity shell lolcow_latest.sif
   Singularity>

The change in prompt indicates that you have entered the container (though you
should not rely on prompt forms to determine whether you are in a container or
not).

Once inside of a {Singularity} container, you are the same user as you are on
the host system.

.. code::

   Singularity> whoami
   david

   Singularity> id
   uid=1000(david) gid=1000(david) groups=1000(david),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),116(lpadmin),126(sambashare)

``shell`` also works with the ``library://``, ``docker://``, and ``shub://``
URIs. This creates an ephemeral container that disappears when the shell is
exited.

.. code::

   $ singularity shell library://lolcow

Executing Commands
==================

The :ref:`exec <singularity_exec>` command allows you to execute a custom
command within a container by specifying the image file. For instance, to
execute the ``cowsay`` program within the ``lolcow_latest.sif`` container:

.. code::

   $ singularity exec lolcow_latest.sif cowsay moo
    _____
   < moo >
    -----
           \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||

``exec`` also works with the ``library://``, ``docker://``, and
``shub://`` URIs. This creates an ephemeral container that executes a
command and disappears.

.. code::

   $ singularity exec library://lolcow cowsay 'Fresh from the library!'
    _________________________
   < Fresh from the library! >
    -------------------------
           \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||

.. _runcontainer:

Running a container
===================

{Singularity} containers contain :ref:`runscripts <runscript>`. These are
user-defined scripts that define the actions a container should perform when
someone runs it. The runscript can be triggered with the :ref:`run
<singularity_run>` command, or simply by calling the container as though it were
an executable.

.. code::

   $ singularity run lolcow_latest.sif
   ______________________________
   < Mon Aug 16 13:01:55 CDT 2021 >
    ------------------------------
           \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||

   $ ./lolcow_latest.sif
   ______________________________
   < Mon Aug 16 13:12:50 CDT 2021 >
    ------------------------------
           \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||

``run`` also works with the ``library://``, ``docker://``, and ``shub://`` URIs.
This creates an ephemeral container that runs and then disappears.

.. code::

   $ singularity run library://lolcow
   ______________________________
   < Mon Aug 16 13:12:33 CDT 2021 >
    ------------------------------
           \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||


Arguments to ``run``
--------------------

You can pass arguments to the runscript of a container. For example, the default
runscript of the ``library://alpine`` container passes any arguments to a shell.
We can ask the container to run ``echo`` command in this shell as follows:

.. code::

   $ singularity run library://alpine echo "hello"
   hello

Because {Singularity} runscripts are evaluated shell scripts, arguments can
behave slightly differently than in Docker/OCI runtimes, in the event that they
contain expressions that have special meaning to the shell. Here is an
illustrative example:

.. code::

   $ docker run -it --rm alpine echo "\$HOSTNAME"
   $HOSTNAME

   $ singularity run docker://alpine echo "\$HOSTNAME"
   p700

   $ singularity run docker://alpine echo "\\\$HOSTNAME"
   $HOSTNAME

To replicate Docker/OCI behavior, you may need additional escaping or quoting of
arguments.

Unlike the ``run`` command, the ``exec`` command does behave in the same manner
as Docker/OCI, because it calls the specified executable directly:

.. code::

   $ singularity exec docker://alpine echo "\$HOSTNAME"
   $HOSTNAME

   $ singularity exec docker://alpine echo "\\\$HOSTNAME"
   \$HOSTNAME

******************
Working with Files
******************

Files on the host are reachable from within the container:

.. code::

   $ echo "Hello from inside the container" > $HOME/hostfile.txt

   $ singularity exec lolcow_latest.sif cat $HOME/hostfile.txt
   Hello from inside the container

This example works because ``hostfile.txt`` exists in the user's home directory
(``$HOME``). By default, {Singularity} bind mounts ``$HOME``, the current
working directory, and additional system locations from the host into the
container.

You can specify additional directories to bind mount into your container with
the ``--bind`` option. In the following example, the ``data`` directory on the
host system is bind mounted to the ``/mnt`` directory inside the container.

.. code::

   $ echo "Drink milk (and never eat hamburgers)." > /data/cow_advice.txt

   $ singularity exec --bind /data:/mnt lolcow_latest.sif cat /mnt/cow_advice.txt
   Drink milk (and never eat hamburgers).

Pipes and redirects also work with {Singularity} commands, just like they
do with normal Linux commands:

.. code::

   $ echo "Drink milk (and never eat hamburgers)." | singularity exec lolcow_latest.sif cowsay
    ________________________________________
   < Drink milk (and never eat hamburgers). >
    ----------------------------------------
           \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||

.. _build-images-from-scratch:

****************************
Building images from scratch
****************************

.. _sec:buildimagesfromscratch:

{Singularity} versions 3.0 and above produce immutable images in the Singularity
Image File (SIF) format. This ensures reproducible and verifiable images, and
allows for many extra benefits such as the ability to sign and verify your
containers.

However, during testing and debugging, you may want an image format that is
writable. This way you can ``shell`` into the image and install software and
dependencies until you are satisfied that your container will fulfill your
needs. For these scenarios, {Singularity} also supports the ``sandbox`` format
(which is really just a directory).

Sandbox Directories
===================

To build into a ``sandbox`` (container in a directory) use the ``build
--sandbox`` command and option:

.. code::

   $ singularity build --sandbox ubuntu/ library://ubuntu

This command creates a sub-directory called ``ubuntu/`` with an entire
Ubuntu operating system and some {Singularity} metadata in your current
working directory.

You can use commands like ``shell``, ``exec`` , and ``run`` with this
directory just as you would with a {Singularity} image. If you pass the
``--writable`` option when you use your container, you can also write
files within the sandbox directory (provided you have the permissions to
do so).

.. code::

   $ singularity exec --writable ubuntu touch /foo

   $ singularity exec ubuntu/ ls /foo
   /foo

Converting images from one format to another
============================================

The ``build`` command allows you to build a new container from an existing
container. This means that you can use it to convert a container from one format
to another. For instance, if you have already created a sandbox (directory) and
want to convert it to the Singularity Image Format, you can do so as follows:

.. code::

   $ singularity build new.sif sandbox

Note, however, that this approach may break reproducibility, in the event that
you have altered your sandbox outside of the context of a :ref:`definition file
<qs-def-files>`, so you are advised to exercise care.

.. _qs-def-files:

{Singularity} Definition Files
==============================

For a reproducible, verifiable and production-quality container, it is
recommended that you build your SIF file using a {Singularity} definition file.
This also makes it easy to add files, environment variables, and install custom
software, while still starting from your base of choice (e.g., the Container
Library).

A definition file has a header and a body. The header determines the
base container to begin with, and the body is further divided into
sections that perform tasks such as software installation, environment
setup, and copying files into the container from host system.

Here is an example of a definition file:

.. code:: singularity

   BootStrap: library
   From: ubuntu:22.04

   %post
      apt-get -y update
      apt-get -y install cowsay lolcat

   %environment
      export LC_ALL=C
      export PATH=/usr/games:$PATH

   %runscript
      date | cowsay | lolcat

   %labels
      Author Sylabs

To build a container from this definition file (assuming it is a file
named ``lolcow.def``), you would call ``build`` as follows:

.. code::

   $ sudo singularity build lolcow.sif lolcow.def

In this example, the header tells {Singularity} to use a base Ubuntu 22.04 image
from the Container Library. The other sections in this definition file are as
follows:

-  The ``%post`` section is executed within the container at build time, after
   the base OS has been installed. The ``%post`` section is therefore the place
   to perform installations of new libraries and applications.

-  The ``%environment`` section defines environment variables that will be
   available to the container at runtime.

-  The ``%runscript`` section defines actions for the container to take when it
   is executed. (These commands will therefore not be run at build time.)

-  And finally, the ``%labels`` section allows for custom metadata to be
   added to the container.

This is a very small example of the things that you can do with a
:ref:`definition file <definition-files>`. In addition to building a container
from the Container Library, you can start with base images from Docker Hub and
use images directly from official repositories such as Ubuntu, Debian, CentOS,
Arch, and BusyBox. You can also use an existing container on your host system as
a base. Definition files also support :ref:`"templating" <sec:templating>`: the
ability to pass values from the command-line, or from a definitions file, that
will replace placeholders in the definition file at build time.

If you want to build {Singularity} images but you don't have
administrative (root) access on your build system, you can build images
using the `Remote Builder <https://cloud.sylabs.io/builder>`_.

This quickstart document just scratches the surface of all of the things
you can do with {Singularity}!

If you need additional help or support, contact the Sylabs team:
https://www.sylabs.io/contact/

.. _installation-request:

**********************************
{Singularity} on a shared resource
**********************************

Perhaps you are a user who wants a few talking points and background to
share with your administrator. Or maybe you are an administrator who
needs to decide whether to install {Singularity}.

This document and the accompanying administrator documentation provide
answers to many common questions.

If you need to request an installation from your administrator, you may decide
to draft a message similar to this:

.. code::

   Dear shared resource administrator,

   We are interested in having {Singularity} (https://www.sylabs.io/docs/)
   installed on our shared resource. {Singularity} containers will allow us to
   build encapsulated environments, meaning that our work is reproducible and
   we are empowered to choose all dependencies including libraries, operating
   system, and custom software. {Singularity} is already in use on many of the
   top HPC centers around the world. Examples include:

       Texas Advanced Computing Center
       GSI Helmholtz Center for Heavy Ion Research
       Oak Ridge Leadership Computing Facility
       Purdue University
       National Institutes of Health HPC
       UFIT Research Computing at the University of Florida
       San Diego Supercomputing Center
       Lawrence Berkeley National Laboratory
       University of Chicago
       McGill HPC Centre/Calcul Québec
       Barcelona Supercomputing Center
       Sandia National Lab
       Argonne National Lab

   Importantly, it has a vibrant team of developers, scientists, and HPC
   administrators that invest heavily in the security and development of the
   software, and are quick to respond to the needs of the community. To help
   learn more about {Singularity}, I thought these items might be of interest:

       - Security: A discussion of security concerns is discussed at
       https://www.sylabs.io/guides/{adminversion}/admin-guide/admin_quickstart.html

       - Installation:
       https://www.sylabs.io/guides/{adminversion}/admin-guide/installation.html

   If you have questions about any of the above, you can contact the open
   source list (https://groups.google.com/g/singularity-ce), join the open
   source slack channel (singularityce.slack.com), or contact the organization
   that supports {Singularity} directly (sylabs.io/contact). I can do my best
   to facilitate this interaction if help is needed.

   Thank you kindly for considering this request!

   Best,

   User
