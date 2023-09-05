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
addressed, {Singularity}'s default native runtime is not fully OCI compatible.
However, over time, {Singularity} has continuously improved compatibility with
OCI standards so that the majority of OCI container images can be run using it.

In {Singularity} 4.0, a new OCI-mode is now fully supported. This mode, enabled
via the ``--oci`` CLI option or ``oci mode`` directive in ``singularity.conf``, uses
an OCI low-level runtime to execute containers that achieve compatibility that is
not possible with {Singularity}'s native runtime. The familiar ``singularity``
command line interface is maintained and unique features such as the SIF image format
continue to offer benefits for HPC environments.

OCI compatibility is discussed in three areas of this guide:

#. The :ref:`OCI-mode section <oci_mode>` of this page introduces the new
   OCI-mode (``--oci``), which runs OCI / Docker containers using a true OCI
   low-level runtime.
#. The :ref:`Support for Docker <singularity-and-docker>` page discusses
   limitations, compatibility options, and best practices for running OCI /
   Docker containers with {Singularity}'s default runtime.
#. The :ref:`OCI Command Group section <oci_command>` of this page documents the
   ``singularity oci`` commands, which provide a low-level means to run
   {Singularity} SIF containers with a command line that matches other OCI
   runtimes.

********************
OCI Mode (``--oci``)
********************

OCI-mode, enabled with the ``--oci`` command line option, or the ``oci mode``
directive in ``singularity.conf``, is now fully supported from {Singularity}
4.0. When OCI-mode is enabled:

- OCI containers are executed using ``crun`` or ``runc`` as the low-level
  runtime, for true OCI runtime compatibility.
- Default behaviour (of bind mounts etc.) is comparable to using the
  ``--compat`` mode with the native runtime.
- Containers retrieved from OCI sources are encapsulated within a single OCI-SIF
  file, maintaining the benefits of SIF while avoiding a full conversion into
  {Singularity}'s native container format.

Users are encouraged to employ OCI-mode when their primary use-case for
{Singularity} is to run existing containers from Docker Hub or other OCI
registries. Behavior will more closely match that described for Docker than with
{Singularity}'s native runtime.

System Requirements
===================

To use OCI mode, the following requirements must be met by the host system:

* Unprivileged user namespace creation is supported by the kernel, and enabled.
* Subuid and subgid mappings are configured for users who plan to run ``--oci``
  mode.
* The ``TMPDIR`` / ``SINGULARITY_TMPDIR`` is located on a filesystem that
  supports subuid/subgid mapping.
* ``crun`` or ``runc`` are available on the ``PATH``.

The majority of these requirements are shared with the those of an unprivileged
installation of {Singularity}, as OCI mode does not use setuid. See the admin
guide for further information on configuring a system appropriately.

Pulling and Running OCI Containers
==================================

To activate OCI-mode when running a container from an OCI source (e.g. Docker
Hub), add the ``--oci`` flag to a ``run / shell / exec`` or ``pull`` command:

.. code::

  # Pull container to an OCI-SIF and run it
  $ singularity pull --oci docker://ubuntu
  Getting image source signatures
  Copying blob 445a6a12be2b done  
  Copying config c6b84b685f done  
  Writing manifest to image destination
  INFO:    Converting OCI image to OCI-SIF format
  INFO:    Squashing image to single layer
  INFO:    Writing OCI-SIF image
  INFO:    Cleaning up.
  $ singularity run --oci ubuntu_latest.oci.sif 
  dtrudg-sylabs@mini:~$ echo "HELLO OCI WORLD"
  HELLO OCI WORLD

  # Run directly from a URI
  $ singularity exec --oci docker://ubuntu date
  INFO:    Using cached OCI-SIF image
  Mon Sep  4 12:24:26 UTC 2023

Running containers in this manner greatly improves compatibility between
{Singularity}'s features and the OCI specification. For example, when running in
``--oci`` mode, Singularity honors the Dockerfile ``USER`` directive:

.. code::

  # I am joeuser outside of the container
  $ whoami
  joeuser

  # The Dockerfile adds a `testuser`
  $ cat Dockerfile
  FROM alpine
  MAINTAINER Joe User
  RUN addgroup -g 2000 testgroup
  RUN adduser -D -u 2000 -G testgroup testuser
  USER testuser
  CMD id

  # Create and save a docker archive from this Dockerfile
  $ docker build --tag docker-user-demo .
  $ docker save docker-user-demo > docker-user-demo.tar

  # Run the docker archive from singularity
  $ singularity run --oci docker-archive:./docker-user-demo.tar
  Getting image source signatures
  Copying blob 3f8df8c11beb done
  Copying blob 78a822fe2a2d done
  Copying blob f7cb6364f42b done
  Copying config 59af11197a done
  Writing manifest to image destination
  INFO:    Converting OCI image to OCI-SIF format
  INFO:    Squashing image to single layer
  INFO:    Writing OCI-SIF image
  INFO:    Cleaning up.
  uid=2000(testuser) gid=2000(testgroup)

As the last line of output shows, the user inside the container run by
``singularity run --oci`` is ``testuser`` (the user added as part of the
Dockerfile) rather than ``joeuser`` (the user on the host).

Default Behaviour & ``--no-compat``
===================================

By and large, the user experience when running in OCI-mode is similar to using
the ``--compat`` flag with the native runtime, or running containers with other
tools such as Docker. Particularly:

- A writable in-memory overlay is provided by default. The container can be
  written to, but changes to the filesystem are lost when the container exits.
- The home directory and current working directory are not mounted into the
  container.

While these defaults make it simpler to translate ``docker run`` commands to
``singularity run``, OCI-mode can also be used with the ``--no-compat`` option to
emulate {Singularity}'s traditional native runtime behaviour:

.. code::

  $ singularity shell --oci --no-compat docker://ubuntu

  # The container is read-only
  Singularity> touch /foo
  touch: cannot touch '/foo': Read-only file system

  # The current working directory was bind mounted, and is the default entry point
  Singularity> pwd
  /data

  # The user's home directory is bind mounted
  Singularity> echo $HOME
  /home/example
  Singularity> ls $HOME
  file1   file2   file3

Feature set
===========

With the release of {Singularity} 4.0, the functionality available in OCI mode -
that is, when running {Singularity} ``shell`` / ``exec`` / ``run`` commands with
the ``--oci`` flag - is approaching feature-parity with the native {Singularity}
runtime, with some important exceptions noted below.

.. note::

  {Singularity}'s OCI mode also supports the `Container Device Interface (CDI)
  <https://github.com/container-orchestrated-devices/container-device-interface>`__
  standard for making GPUs and other devices from the host available inside the
  container. See the :ref:`CDI section <sec:cdi>`, below, for details.

The following features are supported in ``--oci`` mode:

* ``docker://``, ``docker-archive:``, ``docker-daemon:``, ``oci:``,
  ``oci-archive:``, ``library://``, ``oras://``, ``http://``, and ``https://``
  image sources.

* ``--fakeroot`` for effective root in the container.

* Bind mounts via ``--bind`` or ``--mount``.

* ``--overlay`` to mount a SquashFS image (read-only), an EXT3 (read-only or
  writable), or a directory (read-only or writable), as overlays within the
  container.

  * Allows changes to the filesystem to persist across runs of the OCI container

  * Multiple simultaneous overlays are supported (though all but one must be
    mounted as read-only).

* ``--cwd`` (synonym: ``--pwd``) to set a custom starting working-directory for
  the container.

* ``--home`` to set the in-container user's home directory. Supplying a single
  location (e.g. ``--home /myhomedir``) will result in a new tmpfs directory
  being created at the specified location inside the container, and that dir
  being set as the in-container user's home dir. Supplying two locations
  separated by a colon (e.g. ``--home /home/user:/myhomedir``) will result in
  the first location on the host being bind-mounted as the second location
  in-container, and set as the in-container user's home dir.

* ``--scratch`` (shorthand: ``-S``) to mount a tmpfs scratch directory in the
  container.

* `--workdir <workdir>`: if specified, will map `/tmp` and `/var/tmp` in the
  container to `<workdir>/tmp` and `<workdir>/var_tmp`, respectively, on the
  host (rather than to tmpfs storage, which is the default). If `--scratch
  <scratchdir>` is used in conjunction with `--workdir`, scratch directories
  will be mapped to subdirectories nested under `<workdir>/scratch` on the host,
  rather than to tmpfs storage.

* ``--no-home`` to prevent the container home directory from being mounted.

* ``--no-mount`` to disable the mounting of ``proc``, ``sys``, ``devpts``,
  ``tmp``, and ``home`` mounts in the container. Note: ``dev`` cannot be
  disabled in OCI-mode, and ``bind-path`` mounts are not supported.

* Support for the ``SINGULARITY_CONTAINLIBS`` environment variable, to specify
  libraries to bind into ``/.singularity.d/libs/`` in the container.

* ``--hostname`` to set a custom hostname inside the container. (This requires a
  UTS namespace, therefore this flag will infer ``--uts``.)

* Handling ``--dns`` and ``resolv.conf`` on a par with native mode: the
  ``--dns`` flag can be used to pass a comma-separated list of DNS servers that
  will be used in the container; if this flag is not used, the container will
  use the same ``resolv.conf`` settings as the host.

* Additional namespace requests with ``--net``, ``--uts``, ``--user``.

* ``--no-privs`` to drop all capabilities from the container process and enable
  the ``NoNewPrivileges`` flag.

* ``--keep-privs`` to keep effective capabilities for the container process
  (bounding set only for non-root container users).

* ``--add-caps`` and ``--drop-caps``, to modify capabilities of the container
  process.

* ``--rocm`` to bind ROCm GPU libraries and devices into the container.

* ``--nv`` to bind NVIDIA driver / basic CUDA libraries and devices into the
  container.

* ``--apply-cgroups``, and the ``--cpu*``, ``--blkio*``, ``--memory*``,
  ``--pids-limit`` flags to apply resource limits.

Features that are not yet supported include but are not limited to:

* Custom ``--security`` options.

* Support for instances (starting containers in the background).

Running existing non-OCI Singularity containers
===============================================

OCI-mode can also be used to run containers in {Singularity}'s native format,
which were created with ``singularity build`` or pulled without ``--oci``. Note
that the ``--no-compat`` option must still be specified to achieve behavior
matching the native runtime defaults, otherwise the container will behave as if
``--compat`` was specified.

When running a native SIF container in OCI-mode, a compatibility warning is
shown, as it is not possible to perfectly emulate the behaviour of the native
runtime.

.. code::

  $ singularity run --oci --no-compat ubuntu_latest.sif 
  INFO:    Running a non-OCI SIF in OCI mode. See user guide for compatibility information.
   
Environment and action scripts are run using the container's shell, rather than
an embedded shell interpreter. Complex environment scripts may exhibit different
behavior. Bare images that do not contain ``/bin/sh`` cannot be run.

OCI-SIF Images
==============

When an OCI container is ``pull``-ed or run directly from a URI in OCI-mode, it
is encapsulated within a single OCI-SIF file.

.. note::

  OCI-SIF files are only supported by {Singularity} 4.0 and above. They cannot
  be run using older versions of {Singularity}.

An OCI-SIF file provides the same benefits as a native SIF images:

- The single file is easy to share and transport between systems, including
  air-gapped hosts.
- The container root filesystem is mounted at the point of execution, directly
  from the SIF. This avoids excessive metadata traffic when images are stored on
  shared network filesystems.
- Digital signatures may be added to the OCI-SIF, and later verifed, using the
  ``singularity sign`` and ``singularity verify`` commands.

An OCI-SIF differs from a native-runtime SIF as it aims to minimize the
ways in which the encapsulated container differs from its source:

- Container configuration and files are stored as OCI Blobs. This means that the
  container can be pushed from the OCI-SIF to a registry as a native OCI image,
  consisting of these blobs, rather than an ORAS entry / artifact.
- The container's OCI image manifest and config are preserved, and directly
  inserted into the OCI-SIF.
- The container's root filesystem is squashed to a single layer, in squashfs
  format, but using an approach that better preserves metadata than for native
  SIF images.
- The container root filesystem is not modified by the addition of
  Singularity-specific files and directories.

The differences in the layout of native SIF and OCI-SIF images can be seen by
inspecting the same OCI container, pulled with and without the ``--oci`` flag.

.. code::

  $ singularity pull docker://ubuntu

  $ singularity sif list ubuntu_latest.sif 
  ------------------------------------------------------------------------------
  ID   |GROUP   |LINK    |SIF POSITION (start-end)  |TYPE
  ------------------------------------------------------------------------------
  1    |1       |NONE    |32176-32208               |Def.FILE
  2    |1       |NONE    |32208-35190               |JSON.Generic
  3    |1       |NONE    |35190-35386               |JSON.Generic
  4    |1       |NONE    |36864-29818880            |FS (Squashfs/*System/amd64)

The native SIF, shown above, includes {Singularity} specific entries, such as a
definition file and metadata.

.. code::

  $ singularity pull --oci docker://ubuntu

  $ singularity sif list ubuntu_latest.oci.sif 
  ------------------------------------------------------------------------------
  ID   |GROUP   |LINK    |SIF POSITION (start-end)  |TYPE
  ------------------------------------------------------------------------------
  1    |1       |NONE    |32176-29806000            |OCI.Blob
  2    |1       |NONE    |29806000-29806807         |OCI.Blob
  3    |1       |NONE    |29806807-29807216         |OCI.Blob
  4    |1       |NONE    |29807216-29807456         |OCI.RootIndex

The OCI-SIF contains three ``OCI.Blob`` entries. These are the
container root filesystem (as a single squashfs format layer), the image config,
and the image manifest, respectively. There is no definition file or Singularity
specific JSON metadata.

The final ``OCI.RootIndex`` is for internal use, and indexes the content of the
OCI-SIF.

Future Development
==================

Subsequent 4.x releases of {Singularity} will aim to improve OCI-mode to address
missing features vs native mode, and improve the utility of the OCI-SIF format.
Development items include:

- Support for overlays embedded in OCI-SIF files.
- Multi-layer OCI-SIF images, allowing full preservation of the structure of an
  OCI image embedded in an OCI-SIF. This will permit faithful 2-way translation
  to/from OCI-SIF.

.. _sec:cdi:

********************************
Container Device Interface (CDI)
********************************

Beginning in {Singularity} 4.0, ``--oci`` mode supports the `Container Device
Interface (CDI)
<https://github.com/container-orchestrated-devices/container-device-interface>`__
standard for making GPUs and other devices from the host available inside the
container. It offers an alternative to previous approaches that were vendor
specific, and unevenly supported across different container runtimes. Users of
NVIDIA GPUs, and other devices with CDI configurations, will benefit from a
consistent way of using them in containers that spans the cloud native and HPC
fields.

{Singularity}'s "action" commands (``run`` / ``exec`` / ``shell``), when run in
OCI mode, now support a ``--device`` flag:

.. code::

  --device strings                fully-qualified CDI device name(s).
                                  A fully-qualified CDI device name
                                  consists of a VENDOR, CLASS, and
                                  NAME, which are combined as follows:
                                  <VENDOR>/<CLASS>=<NAME> (e.g.
                                  vendor.com/device=mydevice).
                                  Multiple fully-qualified CDI device
                                  names can be given as a comma
                                  separated list.

This allows device from the host to be mapped into the container with the added
benefits of the CDI standard, including:

* Exposing multiple nodes on ``/dev`` as part of what is, notionally, a single
  "device".
* Mounting files from the runtime namespace required to support the device.
* Hiding procfs entries.
* Performing compatibility checks between the container and the device to
  determine whether to make it available in-container.
* Performing runtime-specific operations (e.g. VM vs Linux container-based
  runtimes).
* Performing device-specific operations (e.g. scrubbing the memory of a GPU or
  reconfiguring an FPGA).

In addition, {Singularity}'s OCI mode provides a ``--cdi-dirs`` flag, which
enables the user to override the default search directory for CDI definition
files:

.. code::

  --cdi-dirs strings              comma-separated list of directories
                                  in which CDI should look for device
                                  definition JSON files. If omitted,
                                  default will be: /etc/cdi,/var/run/cdi

.. _oci_command:

*****************
OCI Command Group
*****************

To support execution of containers via a CLI conforming to the OCI runtime
specification, Singularity provides the ``oci`` command group.

The ``oci`` command group is not intended for end users, but as a low-level
interface that can be leveraged by other software. In most circumstances, the
OCI-mode (``--oci``) should be used instead of the ``oci`` command group.

.. note::

   All commands in the ``oci`` command group currently require ``root``
   privileges.

OCI containers follow a different lifecycle from containers that are run with
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

{Singularity} 3.10 and newer use `runc
<https://github.com/opencontainers/runc>`_ as the low-level runtime engine to
execute containers in an OCI Runtime Spec compliant manner. ``runc`` is expected
to be provided by your Linux distribution.

To manage container i/o streams and attachment, `conmon
<https://github.com/containers/conmon>`_ is used. {Singularity} ships with a
suitable version of `conmon` to support the ``oci`` command group.

In {Singularity} 3.9 and prior, {Singularity}'s own low-level runtime was
employed for ``oci`` operations. This was retired to simplify maintenance,
improve OCI compliance, and facilitate the development of OCI-mode.

**************************
OCI Specification Coverage
**************************

OCI Image Spec
==============

In the default native mode, {Singularity} can convert container images that
satisfy the OCI Image Format Specification into its own native SIF format or a simple
sandbox directory. Most of the configuration that a container image can specify
is supported by the {Singularity} runtime, but there are :ref:`various
limitations <singularity-and-docker>` and workarounds may be required for some
containers.

In OCI-mode, {Singularity} encapsulates OCI images in an OCI-SIF. The
image config is preserved, and the container runs via a low-level OCI runtime
for compatibiility with features of the image specification.

OCI Distribution Spec
=====================

{Singularity} is able to pull images from registries that satisfy the OCI
Distribution Specification.

Native SIF images can be pushed, as a single file, to registries that permit
artifacts with arbitrary content types using ``oras://`` URIs.

OCI-SIF images can be pushed to registries as a single file with ``oras://``
URIs, or as an OCI image with ``docker://`` URIs.

.. note::

  Although OCI-SIF images can be pushed to a registry as an OCI image, the
  squashfs layer format is not currently supported by other runtimes. The images
  can only be retrieved and run by {Singularity} 4.

OCI Runtime Spec
================

In its default mode, using the native runtime, {Singularity} does not follow the
OCI Runtime Specification closely. Instead, it uses its own runtime that is
better matched to the requirements and limitations of multi-user shared compute
environments. The ``--compat`` option will apply various other flags to achieve
behaviour that is closer (but not identical) to OCI runtimes such as Docker.

In OCI-mode, {Singularity} executes containers with a true OCI compatible
low-level runtime. This allows compatibility with features of the OCI runtime
specification that are not possible with the native runtime.

OCI Runtime CLI
===============

The ``singularity oci`` commands were added to provide a mode of operation in
which {Singularity} does implement the OCI runtime specification and container
lifecycle, via a command line compatible with other low-level OCI runtimes.
These commands are primarily of interest to tooling that might use {Singularity}
as a container runtime, rather than end users. End users will general use the
OCI-mode (``--oci``) with ``run / shell / exec``.

.. _oci_mode:

