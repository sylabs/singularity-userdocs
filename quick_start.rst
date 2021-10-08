.. _quick-start:

===========
Quick Start
===========

.. _sec:quickstart:

This guide is intended for running {Singularity} on a computer where you
have root (administrative) privileges, and will install {Singularity}
from source code. Other installation options, including building an
RPM package and installing {Singularity} without root privileges are
discussed in the `installation section of the admin guide
<https://sylabs.io/guides/\{adminversion\}/admin-guide/installation.html>`__.

If you need to request an installation on your shared resource, see the
:ref:`requesting an installation section <installation-request>` for
information to send to your system administrator.

For any additional help or support contact the Sylabs team:
https://www.sylabs.io/contact/


.. _quick-installation:

------------------------
Quick Installation Steps
------------------------

You will need a Linux system to run {Singularity} natively. Options for
using {Singularity} on Mac and Windows machines, along with alternate
Linux installation options are discussed in the `installation section of the
admin guide
<https://sylabs.io/guides/\{adminversion\}/admin-guide/installation.html>`__.

Install system dependencies
===========================

You must first install development libraries to your host. Assuming Ubuntu
(apply similar to RHEL derivatives):

.. code-block::

    $ sudo apt-get update && sudo apt-get install -y \
        build-essential \
        libssl-dev \
        uuid-dev \
        libgpgme11-dev \
        squashfs-tools \
        libseccomp-dev \
        wget \
        pkg-config \
        git \
        cryptsetup

.. note::
    Note that ``squashfs-tools`` is only a dependency for commands that build
    images. The ``build`` command obviously relies on ``squashfs-tools``, but
    other commands may do so as well if they are ran using container images
    from Docker Hub for instance.

There are 3 broad steps to installing {Singularity}:

1. :ref:`Installing Go <install>`
2. :ref:`Downloading {Singularity} <download>`
3. :ref:`Compiling {Singularity} Source Code <compile>`

.. _install:

Install Go
==========

{Singularity} v3 and above is written primarily in Go, so you will need Go
installed to compile it from source.

This is one of several ways to `install and configure Go
<https://golang.org/doc/install>`_.

.. note::

   If you have previously installed Go from a download, rather than an
   operating system package, you should remove your ``go`` directory,
   e.g. ``rm -r /usr/local/go`` before installing a newer version.
   Extracting a new version of Go over an existing installation can
   lead to errors when building Go programs, as it may leave old
   files, which have been removed or replaced in newer versions.

Visit the `Go Downloads page <https://golang.org/dl/>`_ and pick a package
archive suitable to the environment you are in. Once the Download is complete,
extract the archive to ``/usr/local`` (or use other instructions on go installation
page). Alternatively, follow the commands here:

.. code-block::

    $ export VERSION=1.16.4 OS=linux ARCH=amd64 && \  # Replace the values as needed
      wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \ # Downloads the required Go package
      sudo tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \ # Extracts the archive
      rm go$VERSION.$OS-$ARCH.tar.gz    # Deletes the ``tar`` file

Set the Environment variable ``PATH`` to point to Go:

.. code-block::

    $ echo 'export PATH=/usr/local/go/bin:$PATH' >> ~/.bashrc && \
      source ~/.bashrc

.. _download:

Download {Singularity} from a release
=====================================

You can download {Singularity} from one of the releases. To see a full list, visit
`the GitHub release page <https://github.com/sylabs/singularity/releases>`_.
After deciding on a release to install, you can run the following commands to
proceed with the installation.

.. code-block::

    $ export VERSION={InstallationVersion} && # adjust this as necessary \
        wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz && \
        tar -xzf singularity-ce-${VERSION}.tar.gz && \
        cd singularity-ce-${VERSION}

.. _compile:

Compile the {Singularity} source code
=====================================

Now you are ready to build {Singularity}. Dependencies will be automatically
downloaded. You can build {Singularity} using the following commands:

.. code-block::

    $ ./mconfig && \
        make -C builddir && \
        sudo make -C builddir install

{Singularity} must be installed as root to function properly.

---------------------------------------
Overview of the {Singularity} Interface
---------------------------------------

{Singularity}’s :ref:`command line interface <cli>` allows you to build
and interact with containers transparently. You can run programs inside a
container as if they were running on your host system. You can easily redirect
IO, use pipes, pass arguments, and access files, sockets, and ports on the host
system from within a container.

The ``help`` command gives an overview of {Singularity} options and subcommands as
follows:

.. code-block::

    $ singularity help

    Linux container platform optimized for High Performance Computing (HPC) and
    Enterprise Performance Computing (EPC)

    Usage:
      singularity [global options...]

    Description:
      {Singularity} containers provide an application virtualization layer enabling
      mobility of compute via both application and environment portability. With
      {Singularity} one is capable of building a root file system that runs on any
      other Linux system where {Singularity} is installed.

    Options:
      -d, --debug     print debugging information (highest verbosity)
      -h, --help      help for singularity
          --nocolor   print without color output (default False)
      -q, --quiet     suppress normal output
      -s, --silent    only print errors
      -v, --verbose   print additional information

    Available Commands:
      build       Build a {Singularity} image
      cache       Manage the local cache
      capability  Manage Linux capabilities for users and groups
      exec        Run a command within a container
      help        Help about any command
      inspect     Show metadata for an image
      instance    Manage containers running as services
      key         Manage OpenPGP keys
      oci         Manage OCI containers
      plugin      Manage singularity plugins
      pull        Pull an image from a URI
      push        Upload image to the provided library (default is "cloud.sylabs.io")
      remote      Manage singularity remote endpoints
      run         Run the user-defined default command within a container
      run-help    Show the user-defined help for an image
      search      Search a Container Library for images
      shell       Run a shell within a container
      sif         siftool is a program for Singularity Image Format (SIF) file manipulation
      sign        Attach a cryptographic signature to an image
      test        Run the user-defined tests within a container
      verify      Verify cryptographic signatures attached to an image
      version     Show the version for {Singularity}

    Examples:
      $ singularity help <command> [<subcommand>]
      $ singularity help build
      $ singularity help instance start


    For additional help or support, please visit https://www.sylabs.io/docs/


Information about subcommand can also be viewed with the ``help`` command.

.. code-block::

    $ singularity help verify
    Verify cryptographic signatures attached to an image

    Usage:
      singularity verify [verify options...] <image path>

    Description:
      The verify command allows a user to verify cryptographic signatures on SIF 
      container files. There may be multiple signatures for data objects and 
      multiple data objects signed. By default the command searches for the primary 
      partition signature. If found, a list of all verification blocks applied on 
      the primary partition is gathered so that data integrity (hashing) and 
      signature verification is done for all those blocks.

    Options:
      -a, --all               verify all objects
      -g, --group-id uint32   verify objects with the specified group ID
      -h, --help              help for verify
      -j, --json              output json
          --legacy-insecure   enable verification of (insecure) legacy signatures
      -l, --local             only verify with local keys
      -i, --sif-id uint32     verify object with the specified ID
      -u, --url string        key server URL (default "https://keys.sylabs.io")


    Examples:
      $ singularity verify container.sif


    For additional help or support, please visit https://www.sylabs.io/docs/


{Singularity} uses positional syntax (i.e. the order of commands and options
matters). Global options affecting the behavior of all commands follow the main
``singularity`` command. Then sub commands are followed by their options
and arguments.

For example, to pass the ``--debug`` option to the main ``singularity`` command
and run {Singularity} with debugging messages on:

.. code-block::

    $ singularity --debug run library://lolcow

To pass the ``--containall`` option to the ``run`` command and run a
{Singularity} image in an isolated manner:

.. code-block::

    $ singularity run --containall library://lolcow

{Singularity} 2.4 introduced the concept of command groups. For instance, to list
Linux capabilities for a particular user, you would use the  ``list`` command in
the ``capability`` command group like so:

.. code-block::

    $ singularity capability list dave

Container authors might also write help docs specific to a container or for an
internal module called an ``app``. If those help docs exist for a particular
container, you can view them like so.

.. code-block::

    $ singularity inspect --helpfile container.sif  # See the container's help, if provided

    $ singularity inspect --helpfile --app=foo foo.sif  # See the help for foo, if provided

-------------------------
Download pre-built images
-------------------------

You can use the ``search`` command to locate groups, collections, and
containers of interest on the `Container Library <https://cloud.sylabs.io/library>`_ .

.. code-block::

    singularity search tensorflow
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

You can use the `pull <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_pull.html>`_
and `build <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_build.html>`_
commands to download pre-built images from an external resource like the
`Container Library <https://cloud.sylabs.io/library>`_ or
`Docker Hub <https://hub.docker.com/>`_.

When called on a native {Singularity} image like those provided on the Container Library, ``pull``
simply downloads the image file to your system.

.. code-block::

    $ singularity pull library://lolcow

You can also use ``pull`` with the ``docker://`` uri to reference Docker images
served from a registry. In this case ``pull`` does not just download an image
file. Docker images are stored in layers, so ``pull`` must also combine those
layers into a usable {Singularity} file.

.. code-block::

    $ singularity pull docker://sylabsio/lolcow

Pulling Docker images reduces reproducibility. If you were to pull a Docker
image today and then wait six months and pull again, you are not guaranteed to
get the same image. If any of the source layers has changed the image will be
altered. If reproducibility is a priority for you, try building your images from
the Container Library.

You can also use the ``build`` command to download pre-built images from an
external resource. When using ``build`` you must specify a name for your
container like so:

.. code-block::

    $ singularity build ubuntu.sif library://ubuntu

    $ singularity build lolcow.sif docker://sylabsio/lolcow

Unlike ``pull``, ``build`` will convert your image to the latest {Singularity}
image format after downloading it.
``build`` is like a “Swiss Army knife” for container creation. In addition to
downloading images, you can use ``build`` to create images from other images or
from scratch using a :ref:`definition file <definition-files>`. You can also
use ``build`` to convert an image between the container formats supported by
{Singularity}. To see a comparison of {Singularity} definition file with Dockerfile,
please see: :ref:`this section <sec:deffile-vs-dockerfile>`.

.. _cowimage:

--------------------
Interact with images
--------------------

You can interact with images in several ways, each of which can accept image URIs
in addition to a local image path.

For demonstration, we will use a ``lolcow_latest.sif`` image that can be pulled
from the Container Library:

.. code-block::

    $ singularity pull library://lolcow

Shell
=====

The `shell <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_shell.html>`_
command allows you to spawn a new shell within your container and interact with
it as though it were a small virtual machine.

.. code-block::

    $ singularity shell lolcow_latest.sif

    {Singularity} lolcow_latest.sif:~>


The change in prompt indicates that you have entered the container (though you
should not rely on that to determine whether you are in container or not).

Once inside of a {Singularity} container, you are the same user as you are on the
host system.

.. code-block::

    {Singularity} lolcow_latest.sif:~> whoami
    david

    {Singularity} lolcow_latest.sif:~> id
    uid=1000(david) gid=1000(david) groups=1000(david),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),116(lpadmin),126(sambashare)

``shell`` also works with the ``library://``, ``docker://``, and ``shub://``
URIs. This creates an ephemeral container that disappears when the shell is
exited.

.. code-block::

    $ singularity shell library://lolcow

Executing Commands
==================

The `exec <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_exec.html>`_
command allows you to execute a custom command within a container by specifying
the image file. For instance, to execute the ``cowsay`` program within the
``lolcow_latest.sif`` container:

.. code-block::

    $ singularity exec lolcow_latest.sif cowsay moo
     _____
    < moo >
     -----
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

``exec`` also works with the ``library://``, ``docker://``, and ``shub://``
URIs. This creates an ephemeral container that executes a command and
disappears.

.. code-block::

    $ singularity exec library://lolcow cowsay "Fresh from the library!"
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

{Singularity} containers contain :ref:`runscripts <runscript>`. These are user
defined scripts that define the actions a container should perform when someone
runs it. The runscript can be triggered with the `run <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_run.html>`_
command, or simply by calling the container as though it were an executable.

.. code-block::

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

.. code-block::

    $ singularity run library://lolcow
    ______________________________
    < Mon Aug 16 13:12:33 CDT 2021 >
     ------------------------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

-------------------
Working with Files
-------------------

Files on the host are reachable from within the container.

.. code-block::

    $ echo "Hello from inside the container" > $HOME/hostfile.txt

    $ singularity exec lolcow_latest.sif cat $HOME/hostfile.txt

    Hello from inside the container

This example works because ``hostfile.txt`` exists in the user’s home directory.
By default {Singularity} bind mounts ``/home/$USER``, ``/tmp``, and ``$PWD`` into
your container at runtime.

You can specify additional directories to bind mount into your container with
the ``--bind`` option. In this example, the ``data`` directory on the host
system is bind mounted to the ``/mnt`` directory inside the container.

.. code-block::

    $ echo "Drink milk (and never eat hamburgers)." > /data/cow_advice.txt

    $ singularity exec --bind /data:/mnt lolcow_latest.sif cat /mnt/cow_advice.txt
    Drink milk (and never eat hamburgers).

Pipes and redirects also work with {Singularity} commands just like they do with
normal Linux commands.

.. code-block::

    $ cat /data/cow_advice.txt | singularity exec lolcow_latest.sif cowsay
     ________________________________________
    < Drink milk (and never eat hamburgers). >
     ----------------------------------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

.. _build-images-from-scratch:

-------------------------
Build images from scratch
-------------------------

.. _sec:buildimagesfromscratch:

{Singularity} v3.0 and above produces immutable images in the Singularity Image File (SIF)
format. This ensures reproducible and verifiable images and allows for many
extra benefits such as the ability to sign and verify your containers.

However, during testing and debugging you may want an image format that is
writable. This way you can ``shell`` into the image and install software and
dependencies until you are satisfied that your container will fulfill your
needs. For these scenarios, {Singularity} also supports the ``sandbox`` format
(which is really just a directory).

Sandbox Directories
===================

To build into a ``sandbox`` (container in a directory) use the
``build --sandbox`` command and option:

.. code-block::

    $ sudo singularity build --sandbox ubuntu/ library://ubuntu

This command creates a directory called ``ubuntu/`` with an entire Ubuntu
Operating System and some {Singularity} metadata in your current working
directory.

You can use commands like ``shell``, ``exec`` , and ``run`` with this directory
just as you would with a {Singularity} image. If you pass the ``--writable``
option when you use your container you can also write files within the sandbox
directory (provided you have the permissions to do so).

.. code-block::

    $ sudo singularity exec --writable ubuntu touch /foo

    $ singularity exec ubuntu/ ls /foo
    /foo

Converting images from one format to another
============================================

The ``build`` command allows you to build a container from an existing
container. This means that you can use it to convert a container from one format
to another. For instance, if you have already created a sandbox (directory) and
want to convert it to the default immutable image format (squashfs) you can do
so:

.. code-block::

    $ singularity build new-sif sandbox

Doing so may break reproducibility if you have altered your sandbox outside of
the context of a definition file, so you are advised to exercise care.

{Singularity} Definition Files
==============================

For a reproducible, verifiable and production-quality container you should
build a SIF file using a {Singularity} definition file. This also makes it easy to
add files, environment variables, and install custom software, and still start
from your base of choice (e.g., the Container Library).

A definition file has a header and a body. The header determines the base
container to begin with, and the body is further divided into sections that
perform things like software installation, environment setup, and copying files
into the container from host system, etc.

Here is an example of a definition file:

.. code-block:: singularity

    BootStrap: library
    From: ubuntu:16.04

    %post
        apt-get -y update
        apt-get -y install date cowsay lolcat

    %environment
        export LC_ALL=C
        export PATH=/usr/games:$PATH

    %runscript
        date | cowsay | lolcat

    %labels
        Author Sylabs


To build a container from this definition file (assuming it is a file
named lolcow.def), you would call build like so:

.. code-block::

    $ sudo singularity build lolcow.sif lolcow.def

In this example, the header tells {Singularity} to use a base Ubuntu 16.04 image
from the Container Library.

- The ``%post`` section executes within the container at build time after the base OS has been installed. The ``%post`` section is therefore the place to perform installations of new applications.

- The ``%environment`` section defines some environment variables that will be available to the container at runtime.

- The ``%runscript`` section defines actions for the container to take when it is executed.

- And finally, the ``%labels`` section allows for custom metadata to be added to the container.

This is a very small example of the things that you can do with a :ref:`definition file <definition-files>`.
In addition to building a container from the Container Library, you can start
with base images from Docker Hub and use images directly from official
repositories such as Ubuntu, Debian, CentOS, Arch, and BusyBox.  You can also
use an existing container on your host system as a base.

If you want to build {Singularity} images but you don't have administrative (root)
access on your build system, you can build images using the `Remote Builder <https://cloud.sylabs.io/builder>`_.

This quickstart document just scratches the surface of all of the things you can
do with {Singularity}!

If you need additional help or support, contact the Sylabs team:
https://www.sylabs.io/contact/


.. _installation-request:

{Singularity} on a shared resource
----------------------------------

Perhaps you are a user who wants a few talking points and background to share
with your administrator.  Or maybe you are an administrator who needs to decide
whether to install {Singularity}.

This document, and the accompanying administrator documentation provides answers
to many common questions.

If you need to request an installation you may decide to draft a message similar
to this:

.. code-block::

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
