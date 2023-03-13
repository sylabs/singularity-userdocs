.. _build-a-container:

###################
 Build a Container
###################

.. _sec:build_a_container:

The ``build`` command is the “Swiss army knife” of container creation.
You can use it to download and assemble existing containers from
external resources like the `Container Library
<https://cloud.sylabs.io/library>`_ and `Docker Hub
<https://hub.docker.com/>`_. You can use it to convert containers
between the formats supported by {Singularity}. And you can use it in
conjunction with a :ref:`{Singularity} definition <definition-files>`
file to create a container from scratch and customized it to fit your
needs.

**********
 Overview
**********

The ``build`` command accepts a target as input and produces a container
as output.

The type of target given determines the method that ``build`` will use
to create the container. It can be one of the following:

-  URI beginning with **library://** to build from the Container Library
-  URI beginning with **docker://** to build from Docker Hub
-  URI beginning with **shub://** to build from Singularity Hub
-  path to an **existing container** on your local machine
-  path to a **directory** to build from a sandbox
-  path to a :ref:`{Singularity} definition file <definition-files>`

``build`` can produce containers in two different formats, which can be
specified as follows:

-  a compressed read-only **Singularity Image File (SIF)** format,
   suitable for production *(default)*
-  a writable **(ch)root directory** called a sandbox, for interactive
   development ( ``--sandbox`` option)

Because ``build`` can accept an existing container as a target and
create a container in either supported format, you can use it to convert
existing containers from one format to another.

**************************************************************
 Downloading an existing container from the Container Library
**************************************************************

You can use the ``build`` command to download a container from the
Container Library:

.. code::

   $ sudo singularity build lolcow.sif library://lolcow

The first argument (``lolcow.sif``) specifies the path and name for your
container. The second argument (``library://lolcow``) gives the
Container Library URI from which to download. By default, the container
will be converted to a compressed, read-only SIF. If you want your
container in a writable format, use the ``--sandbox`` option.

***************************************************
 Downloading an existing container from Docker Hub
***************************************************

You can use ``build`` to download layers from Docker Hub and assemble
them into {Singularity} containers.

.. code::

   $ sudo singularity build lolcow.sif docker://sylabsio/lolcow

.. _create_a_writable_container:

*********************************************
 Creating writable ``--sandbox`` directories
*********************************************

If you want to create a container within a writable directory (called a
*sandbox*) you can do so with the ``--sandbox`` option. It's possible to
create a sandbox without root privileges, but to ensure proper file
permissions, it is recommended to do so as root:

.. code::

   $ sudo singularity build --sandbox lolcow/ library://lolcow

The resulting directory operates just like a container in a SIF file. To
make persistent changes within the sandbox container, use the
``--writable`` flag when you invoke your container. It's a good idea to
do this as root to ensure you have permission to access the files and
directories that you want to change.

.. code::

   $ sudo singularity shell --writable lolcow/

**************************************************
 Converting containers from one format to another
**************************************************

If you already have a container saved locally, you can use it as a
target to build a new container. This allows you convert containers from
one format to another. For example, if you had a sandbox container
called ``development/`` and you wanted to convert it to SIF container
called ``production.sif``, you could do so as follows:

.. code::

   $ sudo singularity build production.sif development/

Use care when converting a sandbox directory to the default SIF format.
If changes were made to the writable container before conversion, there
is no record of those changes in the {Singularity} definition file,
which compromises the reproducibility of your container. It is therefore
preferable to build production containers directly from a {Singularity}
definition file, instead.

*********************************************************
 Building containers from {Singularity} definition files
*********************************************************

{Singularity} definition files are the most powerful type of target when
building a container. For detailed information on writing {Singularity}
definition files, please see the :doc:`Container Definitions
documentation <definition_files>`. Suppose you already have the
following container definition file, called ``lolcow.def``, and you want
to use it to build a SIF container:

.. code:: singularity

   Bootstrap: docker
   From: ubuntu:22.04

   %post
       apt-get -y update
       apt-get -y install cowsay lolcat

   %environment
       export LC_ALL=C
       export PATH=/usr/games:$PATH

   %runscript
       date | cowsay | lolcat

You can do so with the following command.

.. code::

   $ sudo singularity build lolcow.sif lolcow.def

In this case, we're running ``singularity build`` with ``sudo`` because
installing software with ``apt-get``, as in the ``%post`` section,
requires the root privileges. By default, when you run {Singularity},
you are the same user inside the container as on the host machine. Using
``sudo`` on the host, to acquire root privileges, ensures we can use
``apt-get`` as root inside the container.

If you aren't able or do not wish to use ``sudo`` when building a
container, {Singularity} offers several other options: ``--remote``
builds, a ``--fakeroot`` mode, and limited unprivileged builds using
``proot``.

Building with ``--remote``
==========================

`Singularity Container Services <https://cloud.sylabs.io/>`__ and
`Singularity Enterprise <https://sylabs.io/singularity-enterprise/>`__
provide a *Remote Build Service*. This service can perform a container
build, as the root user, inside a secure single-use virtual machine.

Remote builds do not have the system requirements of ``--fakeroot``
builds, or the limitations of unprivileged ``proot`` builds. They are a
convenient way to build {Singularity} containers on systems where
``sudo`` rights are not available.

To perform a remote build, you will need a `Singularity Container
Services <https://cloud.sylabs.io/>`__ account. (If you do not already
have an account, you can create one on the site.) Once you have an
account, ensure you are logged in from your command-line environment by
running:

.. code::

	$ singularity remote login

You can then add the ``--remote`` flag to your build command:

.. code::

    $ singularity build --remote lolcow.sif lolcow.def

The build will be sent to the remote build service, and the progress and
output of your build will be displayed on your local machine. When the
build is complete, the resulting SIF container image will be downloaded
to your machine.

``--fakeroot`` builds
=====================

A build run with the ``--fakeroot`` flag uses certain Linux kernel
features to enable you to run as an emulated, 'fake' root user inside
the container, while running as your regular user (and not as root) on
the host system.

The ``--fakeroot`` feature has particular requirements in terms of the
capabilities and configuration of the host system. This is covered
further in the :ref:`fakeroot <fakeroot>` fakeroot section of this user
guide, as well as in the admin guide.

If your system is configured for ``--fakeroot`` support, then you can
run the above build without using ``sudo``, by adding the ``--fakeroot``
flag:

.. code::

   $ singularity build --fakeroot lolcow.sif lolcow.def

Unprivilged ``proot`` builds
============================

{Singularity} 3.11 introduces the ability to run some definition file builds
without ``--fakeroot`` or ``sudo``. This is useful on systems where you
cannot ``sudo``, and the administrator cannot perform the configurations
necessary for ``--fakeroot`` support.

Unprivileged ``proot`` builds are automatically performed when `proot
<https://proot-me.github.io/>`__ is available on the system ``PATH``, and
``singularity build`` is run by a non-root user against a definition file:

.. code::

   $ singularity build lolcow.sif lolcow.def
   INFO:    Using proot to build unprivileged. Not all builds are supported. If build fails, use --remote or --fakeroot.
   INFO:    Starting build...

Unprivileged builds that use ``proot`` have limitations, because
``proot``'s emulation of the root user is not complete. In particular,
such builds:

- Do not support ``arch`` / ``debootstrap`` / ``yum`` / ``zypper`` bootstraps. Use ``localimage``, ``library``, ``oras``, or one of the ``docker``/``oci`` sources.
- Do not support ``%pre`` and ``%setup`` sections of definition files.
- Run the ``%post`` sections of a build in the container as an emulated root user.
- Run the ``%test`` section of a build as the non-root user, like ``singularity test``.
- Are subject to any restrictions imposed in ``singularity.conf``.
- Incur a performance penalty due to the``ptrace``-based interception of syscalls used by ``proot``.
- May fail if the ``%post`` script requires privileged operations that ``proot`` cannot emulate.

Generally, if your definition file starts from an existing SIF/OCI container
image, and adds software using system package managers, an unprivileged proot build is
appropriate. If your definition file compiles and installs large complex
software from source, you may wish to investigate ``--remote`` or
``--fakeroot`` builds instead.

*******************************
 Building encrypted containers
*******************************

Beginning in {Singularity} 3.4.0, it is possible to build and run
encrypted containers. The containers are decrypted at runtime entirely
in kernel space, meaning that no intermediate decrypted data is ever
written to disk. See :ref:`encrypted containers <encryption>` for more
details.

***************
 Build options
***************

``--builder``
=============

{Singularity} 3.0 introduces the option to perform a remote build. The
``--builder`` option allows you to specify a URL to a different build
service. For instance, you may need to specify a URL pointing to an
on-premises installation of the remote builder. This option must be used
in conjunction with ``--remote``.

``--detached``
==============

When used in combination with the ``--remote`` option, the
``--detached`` option will detach the build from your terminal and allow
it to build in the background without echoing any output to your
terminal.

``--encrypt``
=============

Specifies that {Singularity} should use a secret saved in either the
``SINGULARITY_ENCRYPTION_PASSPHRASE`` or
``SINGULARITY_ENCRYPTION_PEM_PATH`` environment variable to build an
encrypted container. See :ref:`encrypted containers <encryption>` for
more details.

``--fakeroot``
==============

Gives users a way to build containers without root privileges. See
:ref:`the fakeroot feature <fakeroot>` for details.

``--force``
===========

The ``--force`` option will delete and overwrite an existing
{Singularity} image without presenting the normal interactive
confirmation prompt.

``--json``
==========

The ``--json`` option will force {Singularity} to interpret a given
definition file as JSON.

``--library``
=============

This command allows you to set a different image library. (The default
library is "https://library.sylabs.io")

``--notest``
============

If you don't want to run the ``%test`` section during the container
build, you can skip it using the ``--notest`` option. For instance, you
might be building a container intended to run in a production
environment with GPUs, while your local build resource does not have
GPUs. You want to include a ``%test`` section that runs a short
validation, but you don't want your build to exit with an error because
it cannot find a GPU on your system. In such a scenario, passing the
``--notest`` flag would be appropriate.

``--passphrase``
================

This flag allows you to pass a plaintext passphrase to encrypt the
container filesystem at build time. See :ref:`encrypted containers
<encryption>` for more details.

``--pem-path``
==============

This flag allows you to pass the location of a public key to encrypt the
container file system at build time. See :ref:`encrypted containers
<encryption>` for more details.

``--remote``
============

{Singularity} 3.0 introduces the ability to build a container on an
external resource running a remote builder. (The default remote builder
is located at "https://cloud.sylabs.io/builder".)

``--sandbox``
=============

Build a sandbox (container in a directory) instead of the default SIF
format.

``--section``
=============

Instead of running the entire definition file, only run a specific
section or sections. This option accepts a comma-delimited string of
definition file sections. Acceptable arguments include ``all``, ``none``
or any combination of the following: ``setup``, ``post``, ``files``,
``environment``, ``test``, ``labels``.

Under normal build conditions, the {Singularity} definition file is
saved into a container's metadata so that there is a record of how the
container was built. The ``--section`` option may render this metadata
inaccurate, compromising reproducibility, and should therefore be used
with care.

``--update``
============

You can build into the same sandbox container multiple times (though the
results may be unpredictable, and under most circumstances, it would be
preferable to delete your container and start from scratch).

By default, if you build into an existing sandbox container, the
``build`` command will prompt you to decide whether or not to overwrite
existing container data. Instead of this behavior, you can use the
``--update`` option to build *into* an existing container. This will
cause {Singularity} to skip the definition-file's header, and build any
sections that are in the definition file into the existing container.

The ``--update`` option is only valid when used with sandbox containers.

``--nv``
========

This flag allows you to mount the Nvidia CUDA libraries from your host
environment into your build environment. Libraries are mounted during
the execution of ``post`` and ``test`` sections.

``--rocm``
==========

This flag allows you to mount the AMD Rocm libraries from your host
environment into your build environment. Libraries are mounted during
the execution of ``post`` and ``test`` sections.

``--bind``
==========

This flag allows you to mount a directory, file or image during build.
It works the same way as ``--bind`` for the ``shell``, ``exec`` and
``run`` subcommands of {Singularity}, and can be specified multiple
times. See :ref:`user defined bind paths <user-defined-bind-paths>`.
Bind mounts occur during the execution of ``post`` and ``test``
sections.

``--writable-tmpfs``
====================

This flag will run the ``%test`` section of the build with a writable
``tmpfs`` overlay filesystem in place. This allows the tests to create
files, which will be discarded at the end of the build. Other portions
of the build do not use this temporary filesystem.

*******************
 More Build topics
*******************

-  If you want to **customize the cache location** (where Docker layers
   are downloaded on your system), specify Docker credentials, or apply
   other custom tweaks to your build environment, see :ref:`build
   environment <build-environment>`.

-  If you want to make internally **modular containers**, check out the
   Getting Started guide `here <https://sci-f.github.io/tutorials>`_.

-  If you want to **build your containers** on the Remote Builder,
   (because you don't have root access on a Linux machine, or you want
   to host your container on the cloud), check out `this site
   <https://cloud.sylabs.io/builder>`_.

-  If you want to **build a container with an encrypted file system**
   consult the {Singularity} documentation on encryption :ref:`here
   <encryption>`.
