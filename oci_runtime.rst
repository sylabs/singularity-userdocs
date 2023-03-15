.. _oci_runtime:

###################
OCI Runtime Support
###################

.. _sec:oci_runtime_overview:

********
Overview
********

The `Open Containers Initiative <https://www.opencontainers.org/>`_ is an
independent organization whose mandate is to develop open standards relating to
containerization. There are three OCI specifications covering the OCI container
image format, distribution methods for containers, and the behaviour of
compliant container runtimes.

The OCI specifications inherited from the historic behaviour of Docker, and have
been refined over time. The majority of container runtimes and tools, which work
with containers on Linux, follow the OCI standards.

{Singularity} was initially developed to address difficulties with using Docker
in shared HPC compute environments. Because of the ways these issues were
addressed, it is not an OCI runtime in its default mode. However, over time,
{Singularity} has continuously improved compatibility with OCI standards so that
the majority of OCI container images can be run using it. Work has also been
carried out to ensure that {Singularity} fits into workflows involving other
tools from the OCI ecosystem.

Commands and features of {Singularity} that provide OCI compatibility, or direct
support, are discussed in three areas of this guide:

1. In the :ref:`Support for Docker page <singularity-and-docker>`, limitations,
   compatibility options, and best practices for running OCI / Docker containers
   with {Singularity}'s default runtime are explored.
2. In the :ref:`OCI Mode section <oci_mode>`, the experimental OCI runtime (``--oci``), which runs
   OCI / Docker containers in their native format is introduced. 
3. In the :ref:`OCI Command Group section <oci_command>`, the ``singularity oci`` commands, which
   provides a low-level means to run {Singularity} SIF containers with a command
   line that matches other OCI runtimes, are documented.

OCI Spec Support
================

**OCI Image Spec** - {Singularity} can convert container images that satisfy the
OCI Image Specification into its own SIF format, or a simple sandbox directory.
Most of the configuration that a container image can specify is supported by the
{Singularity} runtime, but there are :ref:`some limitations
<singularity-and-docker>`, and workarounds required for certain container
images. From 3.11, the experimental ``--oci`` mode :ref:`can run containers OCI
container images directly <oci_mode>`, to improve compatibility further.

**OCI Distribution Spec** - {Singularity} is able to pull images from registries
that satisfy the OCI Distribution Specification. Images can be pushed to
registries that permit arbitrary content types, using ORAS.

**OCI Runtime Spec** - By default, {Singularity} does not follow the OCI Runtime
Specification closely. Instead, it uses its own runtime that is better matched
to the requirements and limitations of multi-user shared compute environments.
From 3.11, the experimental ``--oci`` mode :ref:`can run containers using a true
OCI runtime <oci_mode>`.

**OCI Runtime CLI** - The ``singularity oci`` commands were added to provide a
mode of operation in which {Singularity} does implement the OCI runtime
specification and container lifecycle. These commands are primarily of interest
to tooling that might use {Singularity} as a container runtime, rather than end
users. End users will general use the ``--oci`` mode with ``run / shell /
exec``.

Future Development
==================

As newer Linux kernels and system software reach production environments, many
of the limitations that required {Singularity} to operate quite differently from
OCI runtimes are becoming less-applicable. From 3.11, {Singularity} development
will focus strongly on greater OCI compliance for typical usage, while
maintaining the same ease-of-use and application focus.

You can read more about these plans in the following article and open community
roadmap:

* https://sylabs.io/2022/02/singularityce-4-0-and-beyond/
* https://github.com/sylabs/singularityce-community

.. _oci_mode:

********************
OCI Mode (``--oci``)
********************

Overview
========

Beginning in {Singularity} 3.11, users can run an OCI / Docker container in its
native format by adding the ``--oci`` flag to a ``run / shell /exec`` command:

.. code::

  $ singularity shell --oci docker://ubuntu 
  2023/02/06 11:00:10  info unpack layer: sha256:677076032cca0a2362d25cf3660072e738d1b96fe860409a33ce901d695d7ee8
  Singularity> echo "Hello OCI World!"
  Hello OCI World!

In ``--oci`` mode, the familiar ``singularity`` command line is used, and
friendly defaults such as auto-mounting of the ``$HOME`` directory are still
applied. The user experience is similar to when the ``--compat`` flag is used
with the default runtime mode.

The ``--oci`` mode only works with OCI containers, i.e. those from sources
beginning with ``docker`` or ``oci``. {Singularity} retrieves and prepares the
container image, before instructing a low-level OCI runtime (either ``runc`` or
``crun``) to execute the container. When running containers in this way OCI
image compatibility is improved. For example, the ``Dockerfile`` ``USER``
directive can now be honored:

.. code:: 

  # I am dtrudg-sylabs outside of the container
  $ whoami
  dtrudg-sylabs

  # The Dockerfile adds a `testuser`
  $ cat Dockerfile 
  FROM alpine
  MAINTAINER David Trudgian
  RUN addgroup -g 2000 testgroup
  RUN adduser -D -u 2000 -G testgroup testuser
  USER testuser
  CMD id

  # I am testuser inside the container
  $ singularity shell --oci docker-archive:docker-user.tar 
  2023/02/06 11:05:38  info unpack layer: sha256:2815b02d45841c8d883e7b46b390e60fdfed11a471cccc85254595147e8e4588
  2023/02/06 11:05:38  info unpack layer: sha256:bc1572635922ace72233986284e0b371556e9a985a642e70c339f58ea4f8548a
  2023/02/06 11:05:38  info unpack layer: sha256:c93fe14ead6e5ea5328756a33aa9020d4d2bee5c2b974a95ae55b7412ee7e31a
  Singularity> whoami
  testuser

.. warning::

  In {Singularity} 3.11, ``--oci`` mode is designated an experimental feature.
  It has requirements and limitations that will be addressed when full OCI
  support is introduced in 4.0.

  Due to its experimental status, features may be added to ``--oci`` mode in
  3.11.x patch releases, and small behavior changes may occur.

  Use of ``--oci`` mode is appropriate where the default runtime does not
  support execution of a particular Docker / OCI container image. At this time,
  the default runtime should be preferred for general usage.

Requirements
============

To use OCI mode, the following requirements must be met by the host system:

* Unprivileged user namespace creation is supported by the kernel, and enabled.
* Subuid and subgid mappings are configured for users who require ``--oci`` mode.
* The ``TMPDIR`` / ``SINGULARITY_TMPDIR`` is located on a filesystem that
  supports subuid/subgid mapping.
* ``crun`` or ``runc`` are available on the ``PATH``.

The majority of these requirements are in common with an unprivileged
installation of {Singularity}, as ``--oci`` mode does not use setuid. See the
admin guide for further information on configuring a system appropriately.

Limitations
===========

The ``--oci`` functionality is implemented on the existing ``run / shell /
exec`` commands. These commands can be used in ``--oci`` mode in the same manner
as with the default runtime, discussed elsewhere in this guide. However, not
all flags or options for ``run / shell / exec`` are supported at this time.

The following features are supported in ``--oci`` mode:

* ``docker://``, ``docker-archive:``, ``docker-daemon:``, ``oci:``,
  ``oci-archive:`` image sources.
* ``--fakeroot`` for effective root in the container.
* Additional namespace requests with ``--net``, ``--uts``, ``--user``.
* Bind mounts via ``--bind`` or ``--mount``.
* ``--rocm`` to bind ROCm GPU libraries and devices into the container.
* ``--nv`` to bind Nvidia driver / basic CUDA libraries and devices into the container.
* ``--apply-cgroups``, and the ``--cpu*``, ``--blkio*``, ``--memory*``,
  ``--pids-limit`` flags to apply resource limits.

Other features are not supported, including but not limited to:

* No support running Singularity SIF, SquashFS, or EXT3 images.
* No mounts from image files (SIF, EXT3, etc.).
* No support for overlays.
* No CNI networking configuration.
* No custom ``--security`` options.
* No support for instances (starting containers in the background).

Future Development
==================

In {Singularity} 4.0, the ``--oci`` mode will approach feature / option parity
with the default native runtime. It will be possible to execute existing SIF
format {Singularity} images using the OCI low-level runtime. In addition, SIF
will support encapsulation of OCI images in their native format, without
translation in to a {Singularity} image.

.. _oci_command:

*****************
OCI Command Group
*****************

To run native Singularity containers following the OCI runtime lifecycle, you
can use the ``oci`` command group.

.. note::

   All commands in the ``oci`` command group currently require ``root``
   privileges.

OCI containers follow a different lifecycle to containers that are run with
``singularity run/shell/exec``. Rather than being a simple process that starts,
and exits, they are created, run, killed, and deleted. This is similar to
instances. Additionally, containers must be run from an OCI bundle, which is a
specific directory structure that holds the container's root filesystem and
configuration file. To run a {Singularity} SIF image, you must mount it into a
bundle.

Mounting an OCI Filesystem Bundle
=================================

Let's work with a busybox container image, pulling it down with the default
``busybox_latest.sif`` filename:

.. code::

  $ singularity pull library://busybox
  INFO:    Downloading library image
  773.7KiB / 773.7KiB [===============================================================] 100 % 931.4 KiB/s 0s

Now use ``singularity oci mount`` to create an OCI bundle onto which the SIF is
mounted:

.. code::

   $ sudo singularity oci mount ./busybox_latest.sif /var/tmp/busybox

By issuing the ``mount`` command, the root filesystem encapsulated in the SIF
file ``busybox_latest.sif`` is mounted on ``/var/tmp/busybox`` with an overlay
setup to hold any changes, as the SIF file is read-only.

Content of an OCI Compliant Filesystem Bundle
=============================================

The OCI bundle, created by the mount command consists of the following files and
directories:

* ``config.json`` - a generated OCI container configuration file, which
  instructs the OCI runtime how to run the container, which filesystems to bind
  mount, what environment to set, etc.
* ``overlay/`` - a directory that holds the contents of the bundle overlay - any
  new files, or changed files, that differ from the content of the read-only SIF
  container image.
* ``rootfs/`` - a directory containing the mounted root filesystem from the SIF
  container image, with its overlay.
* ``volumes/`` - a directory used by the runtime to stage any data mounted into
  the container as a volume.

OCI config.json
===============

The container configuration file, ``config.json`` in the OCI bundle, is
generated by ``singularity mount`` with generic default options. It may not
reflect the ``config.json`` used by an OCI runtime working directly from a
native OCI image, rather than a mounted SIF image.

You can inspect and modify ``config.json`` according to the `OCI runtime
specification
<https://github.com/opencontainers/runtime-spec/blob/main/config.md>`_ to
influence the behavior of the container.

Running a Container
====================

For simple interactive use, the ``oci run`` command will create and start a
container instance, attaching to it in the foreground. This is similar to the
way ``singularity run`` works, with {Singularity}'s native runtime engine:

.. code:: 

  $ sudo singularity oci run -b /var/tmp/busybox busybox1
  / # echo "Hello"
  Hello
  / # exit

When the process running in the container (in this case a shell) exits, the
container is automatically cleaned up, but note that the OCI bundle remains
mounted.

Full Container Lifecycle
========================

If you want to run a detached background service, or interact with SIF
containers from 3rd party tools that are compatibile with OCI runtimes, you will
step through the container lifecycle using a number of ``oci`` subcommands.
These move the container between different states in the lifecycle.

Once an OCI bundle is available, you can create a instance of the container with
the ``oci create`` subcommand:

.. code::

  $ sudo singularity oci create -b /var/tmp/busybox busybox1
  INFO:    Container busybox1 created with PID 20105

At this point the runtime has prepared container processes, but the payload
(``CMD / ENTRYPOINT`` or ``runscript``) has not been started.

Check the state of the container using the ``oci state`` subcommand:

.. code::

  $ sudo singularity oci state busybox1
  {
    "ociVersion": "1.0.2-dev",
    "id": "busybox1",
    "pid": 20105,
    "status": "created",
    "bundle": "/var/tmp/busybox",
    "rootfs": "/var/tmp/busybox/rootfs",
    "created": "2022-04-27T15:39:08.751705502Z",
    "owner": ""
  }

Start the container's ``CMD/ENTRYPOINT`` or ``runscript`` with the ``oci
start`` command:

.. code:: 

  $ singularity start busybox1

There is no output, but if you check the container state it will now be
``running``. The container is *detached*. To view output or provide input we
will need to attach to its input and output streams. with the ``oci attach``
command:

.. code:: 

  $ sudo singularity oci attach busybox1
  / # date
  date
  Wed Apr 27 15:45:27 UTC 2022
  / # 

When finished with the container, first ``oci kill`` running processes, than
``oci delete`` the container instance:

.. code ::

  $ sudo singularity oci kill busybox1
  $ sudo singularity oci delete busybox1

Unmounting OCI Filesystem Bundles
=================================

When you are finished with an OCI bundle, you will need to explicitly unmount
it using the ``oci umount`` subcommand:

.. code::

   $ sudo singularity oci umount /var/tmp/busybox

Technical Implementation
========================

{Singularity} 3.10 uses `runc <https://github.com/opencontainers/runc>`_ as the
low-level runtime engine to execute containers in an OCI Runtime Spec compliant
manner. ``runc`` is expected to be provided by your Linux distribution.

To manage container i/o streams and attachment, `conmon
<https://github.com/containers/conmon>`_ is used. {Singularity} ships with a
suitable version of `conmon` to support the ``oci`` command group.

In {Singularity} 3.9 and prior, {Singularity}'s own low-level runtime was
employed for ``oci`` operations. This was retired to simplify maintenance,
improve OCI compliance, and make possible future development in the roadmap to
4.0.
