.. _oci_runtime:

#####################
 OCI Runtime Support
#####################

.. _sec:oci_runtime_overview:

**********
 Overview
**********

The `Open Containers Initiative <https://www.opencontainers.org/>`_ is an
independent organization whose mandate is to develop open standards relating to
containerization. There are three OCI specifications covering the OCI container
image format, distribution methods for containers, and the behaviour of
compliant container runtimes.

The OCI specifications inherited from the historic behaviour of Docker, and have
been refined over time. The majority of container runtimes, and tools that work
with containers on Linux follow the OCI standards.

{Singularity} was initially developed to address difficulties with using Docker
in shared HPC compute environments. A development goal is to allow users to work
with Docker/OCI containers where Docker or other OCI runtimes cannot easily be
deployed, for various reasons.

OCI Spec Support
================

**OCI Image Spec** - {Singularity} can convert container images that satisfy the
OCI Image Specification into its own SIF format, or a simple sandbox directory.
Most of the configuration that a container image can specify is supported by the
{Singularity} runtime, but there are :ref:`some limitations
<singularity-and-docker>`, and workarounds required for certain container
images.

**OCI Distribution Spec** - {Singularity} is able to pull images from registries
that satisfy the OCI Distribution Specification.

**OCI Runtime Spec** - By default, {Singularity} does not follow the OCI Runtime
Specification closely. Instead, it uses its own runtime that is better matched
to the requirements and limitations of multi-user shared compute environments.
The ``singularity oci`` commands were added to provide a mode of operation in
which {Singularity} does implement the OCI runtime specification and container
lifecycle. These commands are primarily of interest to tooling that might use
{Singularity} as a container runtime, rather than end users.

Future Development
==================

As newer Linux kernels and system software reach production environments, many
of the limitations that required {Singularity} to operate quite differently from
OCI runtimes are becoming less-applicable. Over future releases, {Singularity}
development will bring greater OCI compliance for typical usage, while
maintaining the same ease-of-use and application focus.

You can read more about these plans in the following article and open community
roadmap:

* https://sylabs.io/2022/02/singularityce-4-0-and-beyond/
* https://github.com/sylabs/singularityce-community

*****************
OCI Command Group
*****************

To run Singularity containers in an OCI Runtime Spec compliant manner, you can
use the ``oci`` command group.

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
