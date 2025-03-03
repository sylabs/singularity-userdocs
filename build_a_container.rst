.. _build-a-container:

#################
Build a Container
#################

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

********
Overview
********

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

************************************************************
Downloading an existing container from the Container Library
************************************************************

You can use the ``build`` command to download a container from the
Container Library:

.. code::

   $ sudo singularity build lolcow.sif library://lolcow

The first argument (``lolcow.sif``) specifies the path and name for your
container. The second argument (``library://lolcow``) gives the
Container Library URI from which to download. By default, the container
will be converted to a compressed, read-only SIF. If you want your
container in a writable format, use the ``--sandbox`` option.

*************************************************
Downloading an existing container from Docker Hub
*************************************************

You can use ``build`` to download layers from Docker Hub and assemble
them into {Singularity} containers.

.. code::

   $ sudo singularity build lolcow.sif docker://sylabsio/lolcow

*************************************************
Building from an existing local Docker container
*************************************************

You can also use ``build`` to create a {Singularity} container
from a local Docker image.

.. code::

   $ sudo singularity build lolcow.sif docker-daemon://lolcow:latest

.. _create_a_writable_container:

*******************************************
Creating writable ``--sandbox`` directories
*******************************************

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

************************************************
Converting containers from one format to another
************************************************

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

*******************************************************
Building containers from {Singularity} definition files
*******************************************************

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

``--remote`` builds
===================

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

Unprivileged ``proot`` builds
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

- Do not support ``arch`` / ``debootstrap`` / ``yum`` / ``zypper``
  bootstraps. Use ``localimage``, ``library``, ``oras``, or one of the
  ``docker``/``oci`` sources.
- Do not support ``%pre`` and ``%setup`` sections of definition files.
- Run the ``%post`` sections of a build in the container as an emulated
  root user.
- Run the ``%test`` section of a build as the non-root user, like
  ``singularity test``.
- Are subject to any restrictions imposed in ``singularity.conf``.
- Incur a performance penalty due to the``ptrace``-based interception of
  syscalls used by ``proot``.
- May fail if the ``%post`` script requires privileged operations that
  ``proot`` cannot emulate.

Generally, if your definition file starts from an existing SIF/OCI
container image, and adds software using system package managers, an
unprivileged proot build is appropriate. If your definition file
compiles and installs large complex software from source, you may wish
to investigate ``--remote`` or ``--fakeroot`` builds instead.

*****************************
Building encrypted containers
*****************************

Starting with {Singularity} 3.4.0, it is possible to build and run encrypted
containers. The containers are decrypted at runtime entirely in kernel space,
meaning that no intermediate decrypted data is ever written to disk. See
:ref:`encrypted containers <encryption>` for more details.

.. _dockerfile:

*************************
Building from Dockerfiles
*************************

Starting with version 4.1, {Singularity} can build OCI-SIF images directly from
`Dockerfiles
<https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>`__,
creating images that can be run using {Singularity}'s :ref:`OCI mode
<oci_runtime>`.

.. code:: console

   $ cat ./Dockerfile
   FROM debian
   CMD cat /etc/os-release

   $ singularity build --oci ./debian.oci.sif ./Dockerfile
   INFO:    Did not find usable running buildkitd daemon; spawning our own.
   INFO:    cfg.Root for buildkitd: /home/myuser/.local/share/buildkit
   INFO:    Using crun runtime for buildkitd daemon.
   INFO:    running buildkitd server on /run/user/1000/buildkit/buildkitd-0179484509442521.sock
   [+] Building 4.3s (5/5)
   [+] Building 4.4s (5/5) FINISHED
   => [internal] load build definition from Dockerfile               0.0s
   => => transferring dockerfile: 131B                               0.0s
   => [internal] load metadata for docker.io/library/debian:latest   1.2s
   => [internal] load .dockerignore                                  0.0s
   => => transferring context: 2B                                    0.0s
   => [1/1] FROM docker.io/library/debian:latest@sha256:fab22df3737  2.9s
   => => resolve docker.io/library/debian:latest@sha256:fab22df3737  0.0s
   => => sha256:8457fd5474e70835e4482983a5662355d 49.58MB / 49.58MB  2.8s
   => exporting to docker image format                               3.1s
   => => exporting layers                                            0.0s
   => => exporting manifest sha256:9fec77672dfa11e5eb28e3fe9377cd6c  0.0s
   => => exporting config sha256:4243e816256d45bb137ff40bafe396da5f  0.0s
   => => sending tarball                                             0.2s
   Getting image source signatures
   Copying blob 8457fd5474e7 done   |
   Copying config 46c53efffd done   |
   Writing manifest to image destination
   INFO:    Converting OCI image to OCI-SIF format
   INFO:    Squashing image to single layer
   INFO:    Writing OCI-SIF image
   INFO:    Cleaning up.
   INFO:    Build complete: ./debian.oci.sif

   $ singularity run --oci ./debian.oci.sif
   PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
   NAME="Debian GNU/Linux"
   VERSION_ID="12"
   VERSION="12 (bookworm)"
   VERSION_CODENAME=bookworm
   ID=debian
   HOME_URL="https://www.debian.org/"
   SUPPORT_URL="https://www.debian.org/support"
   BUG_REPORT_URL="https://bugs.debian.org/"

The resulting containers can be used with all the :ref:`action commands
<cowimage>` (`exec
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_exec.html>`__
/ `shell
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_shell.html>`__
/ `run
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_run.html>`__)
in the expected way.

.. code:: console

   $ singularity exec --oci ./debian.oci.sif uname -a
   Linux myhost 5.14.0-284.30.1.el9_2.x86_64 #1 SMP PREEMPT_DYNAMIC Fri Aug 25 09:13:12 EDT 2023 x86_64 GNU/Linux

   $ singularity shell --oci ./debian.oci.sif uname
   Singularity> uname -a
   Linux myhost 5.14.0-284.30.1.el9_2.x86_64 #1 SMP PREEMPT_DYNAMIC Fri Aug 25 09:13:12 EDT 2023 x86_64 GNU/Linux
   Singularity>

.. note::

   If the `exec
   <https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_exec.html>`__
   or `shell
   <https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_shell.html>`__
   commands are used, the ``CMD`` / ``ENTRYPOINT`` directives in the Dockerfile
   will be ignored.

The resulting containers also accept command-line arguments, as well as input
that is piped through ``stdin``. The following example demonstrates both:

.. code:: console

   $ cat ./Dockerfile
   FROM debian

   SHELL ["/bin/bash", "-c"]

   RUN apt-get update
   RUN apt-get install -y cowsay lolcat

   RUN echo $'#! /bin/bash \n\
   echo from cmdline: $@ | /usr/games/cowsay | /usr/games/lolcat \n\
   sed "s/^/from stdin: /g" | /usr/games/cowsay | /usr/games/lolcat' > /myscript.sh

   RUN chmod +x /myscript.sh

   ENTRYPOINT ["/myscript.sh"]

   $ singularity build --oci ./lolcow.oci.sif ./Dockerfile
   INFO:    Did not find usable running buildkitd daemon; spawning our own.
   INFO:    cfg.Root for buildkitd: /home/myuser/.local/share/buildkit
   INFO:    Using crun runtime for buildkitd daemon.
   INFO:    running buildkitd server on /run/user/1000/buildkit/buildkitd-8961170237105250.sock
   [+] Building 15.1s (9/9)
   [+] Building 15.2s (9/9) FINISHED
   => [internal] load build definition from Dockerfile               0.0s
   => => transferring dockerfile: 549B                               0.0s
   => [internal] load metadata for docker.io/library/debian:latest   0.5s
   => [internal] load .dockerignore                                  0.0s
   => => transferring context: 2B                                    0.0s
   => [1/5] FROM docker.io/library/debian:latest@sha256:fab22df3737  1.0s
   => => resolve docker.io/library/debian:latest@sha256:fab22df3737  0.0s
   => => extracting sha256:8457fd5474e70835e4482983a5662355d892d5f6  1.0s
   => [2/5] RUN apt-get update                                       2.2s
   => [3/5] RUN apt-get install -y cowsay lolcat                     7.9s
   => [4/5] RUN echo $'#! /bin/bash \necho from cmdline: $@ | /usr/  0.1s
   => [5/5] RUN chmod +x /myscript.sh                                0.1s
   => exporting to docker image format                               3.3s
   => => exporting layers                                            2.7s
   => => exporting manifest sha256:fc7222347c207c35165ccd2fee562af9  0.0s
   => => exporting config sha256:74c5da659e8504e4be283ad6d82774194e  0.0s
   => => sending tarball                                             0.5s
   Getting image source signatures
   Copying blob 8457fd5474e7 done   |
   Copying blob 4769fe2f22da done   |
   Copying blob 173d009c20af done   |
   Copying blob 7ec86debbe9b done   |
   Copying blob 491c7ee403c2 done   |
   Copying config 74b69e878e done   |
   Writing manifest to image destination
   INFO:    Converting OCI image to OCI-SIF format
   INFO:    Squashing image to single layer
   INFO:    Writing OCI-SIF image
   INFO:    Cleaning up.
   INFO:    Build complete: ./lolcow.oci.sif

   $ echo "world" | singularity run --oci ./lolcow.oci.sif hello
   _____________________
   < from cmdline: hello >
   ---------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||
   ___________________
   < from stdin: world >
   -------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||

{Singularity} uses `buildkit <https://docs.docker.com/build/buildkit/>`__ to
build an OCI image from a Dockerfile. It checks if there is a ``buildkitd``
daemon that is already running on the system (and whose permissions allow access
by the current user), and if so, that daemon is used for the build process. If a
usable ``buildkitd`` daemon is not found, {Singularity} will launch an ephemeral
build daemon of its own, inside a :ref:`user namespace <setuid_and_userns>`,
that will be used for the build process and torn down when the build is
complete. This ephemeral build daemon is based on `moby/buildkit
<httpshttps://github.com/moby/buildkit/>`__, but is embedded within
{Singularity} and runs as part of the same process.

.. note::

   Launching the ephemeral build daemon requires a system with
   :ref:`user namespace support <setuid_and_userns>` as well as ``crun`` /
   ``runc`` installed. These are independently required for using
   {Singularity}'s :ref:`OCI mode <oci_sysreq>`. See the `Admin Guide
   <https://sylabs.io/guides/{adminversion}/admin-guide/>`__ for more
   information on these system requirements.

The `build context <https://docs.docker.com/build/building/context/>`__ for
Dockerfile builds using {Singularity} is always the current working directory.
Therefore, if you want to have the build context set to a different directory
than the one your Dockerfile is in, all you have to do is run {Singularity}
*from the desired context dir*, and provide a relative or absolute path to the
Dockerfile:

.. code:: console

   $ pwd
   /home/myuser/tmp/my_context_dir

   $ ls
   some_file

   $ cat some_file
   Some text.

   $ cat ../Dockerfile
   From alpine
   ADD some_file /
   CMD cat /some_file

   $ singularity build --oci ./container.oci.sif ../Dockerfile
   INFO:    Did not find usable running buildkitd daemon; spawning our own.
   INFO:    cfg.Root for buildkitd: /home/myuser/.local/share/buildkit
   INFO:    Using "crun" runtime for buildkitd daemon.
   INFO:    running buildkitd server on /run/user/1000/buildkit/buildkitd-8519770128063388.sock
   [+] Building 1.3s (6/7)
   [+] Building 1.4s (7/7) FINISHED
   => [internal] load build definition from Dockerfile               0.0s
   => => transferring dockerfile: 143B                               0.0s
   => [internal] load metadata for docker.io/library/alpine:latest   1.3s
   => [internal] load .dockerignore                                  0.0s
   => => transferring context: 2B                                    0.0s
   => [internal] load build context                                  0.0s
   => => transferring context: 88B                                   0.0s
   => [1/2] FROM docker.io/library/alpine:latest@sha256:eece025e432  0.0s
   => => resolve docker.io/library/alpine:latest@sha256:eece025e432  0.0s
   => CACHED [2/2] ADD some_file /                                   0.0s
   => exporting to docker image format                               0.0s
   => => exporting layers                                            0.0s
   => => exporting manifest sha256:78c2cbf8ea2441c7a3d75f80bd0660ef  0.0s
   => => exporting config sha256:58e9a24e9242901475f317e201185cbf10  0.0s
   => => sending tarball                                             0.0s
   Getting image source signatures
   Copying blob 96526aa774ef done   |
   Copying blob 15061a177792 done   |
   Copying config 3d12fd8035 done   |
   Writing manifest to image destination
   INFO:    Converting OCI image to OCI-SIF format
   INFO:    Squashing image to single layer
   INFO:    Writing OCI-SIF image
   INFO:    Cleaning up.
   INFO:    Build complete: ./container.oci.sif

   $ singularity run --oci ./container.oci.sif
   Some text.

Additional features
===================

Build from Dockerfiles supports many of the same command-line options as regular
(non-OCI-SIF) ``build``, including:

* ``--build-arg KEY=VAL`` / ``--build-arg-file <path>``: pass value for
  Dockerfile variables at build time (see `Dockerfile ARG documentation
  <https://docs.docker.com/engine/reference/builder/#arg>`__).

* ``--docker-login`` / Docker credential-related environment variables /
  ``--authfile``: see the documentation on :ref:`authenticating with Docker/OCI
  registries <docker_auth>` and on the :ref:`authfile flag <sec:authfile>`.

* ``--arch``: build a container for a different CPU architecture than that of
  the running host.
  
As an example, if you are running on an ``amd64`` machine, you can run the
following to build a container image for the 64-bit ARM architecure:

.. code:: console

   $ singularity build --arch arm64 --oci ./alpine.oci.sif ./Dockerfile.alpine
   INFO:    Did not find usable running buildkitd daemon; spawning our own.
   INFO:    cfg.Root for buildkitd: /home/myuser/.local/share/buildkit
   INFO:    Using "crun" runtime for buildkitd daemon.
   INFO:    running buildkitd server on /run/user/1000/buildkit/buildkitd-4747966236261602.sock
   [+] Building 0.6s (1/2)
   [+] Building 0.7s (5/5) FINISHED
   => [internal] load build definition from Dockerfile.alpine     0.0s
   => => transferring dockerfile: 142B                               0.0s
   => [internal] load metadata for docker.io/library/alpine:latest   0.6s
   => [internal] load .dockerignore                                  0.0s
   => => transferring context: 2B                                    0.0s
   => CACHED [1/1] FROM docker.io/library/alpine:latest@sha256:eece  0.0s
   => => resolve docker.io/library/alpine:latest@sha256:eece025e432  0.0s
   => exporting to docker image format                               0.0s
   => => exporting layers                                            0.0s
   => => exporting manifest sha256:b799c38cef1756bcc55b0684617fda7d  0.0s
   => => exporting config sha256:5118299610d621e305a9153753a52e2f9e  0.0s
   => => sending tarball                                             0.0s
   Getting image source signatures
   Copying blob 579b34f0a95b done   |
   Copying config 5a13726077 done   |
   Writing manifest to image destination
   INFO:    Converting OCI image to OCI-SIF format
   INFO:    Squashing image to single layer
   INFO:    Writing OCI-SIF image
   INFO:    Cleaning up.
   INFO:    Build complete: ./alpine.oci.sif

.. note::

   In order to use Dockerfile directives like ``RUN`` in a cross-architecture
   build, you will have to have ``qemu-static`` / ``binfmt_misc`` emulation
   installed. See the discussion of :ref:`CPU emulation <qemu>` for more
   information.

*************
Build options
*************

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

This flag allows you to mount the NVIDIA CUDA libraries from your host
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

*****************
More Build topics
*****************

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
