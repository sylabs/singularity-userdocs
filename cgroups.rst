.. _cgroups:

=========================================
Limiting Container Resources with Cgroups
=========================================

The cgroups (control groups) functionality of the Linux kernel allows you to
limit and meter the resources used by a process, or group of processes. Using
cgroups you can limit memory and CPU usage. You can also rate limit block IO,
network IO, and control access to device nodes.

There are two versions of cgroups in common use. Cgroups v1 sets resource limits
for a process within separate hierarchies per resource class. Cgroups v2, the
default in newer Linux distributions, implements a unified hierarchy,
simplifying the structure of resource limits on processes.

* v1 documentation: https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt
* v2 documentation: https://www.kernel.org/doc/Documentation/cgroup-v2.txt

-------------------------------------
Running {Singularity} Inside a Cgroup
-------------------------------------

Because {Singularity} starts a container as a simple process, rather than using
a daemon, you can limit resource usage by running the ``singularity`` command
inside an existing cgroup. This is convenient where, for example, a job
scheduler uses cgroups to control job limits. By running ``singularity`` inside
your batch script, your container will respect the limits set by the scheduler
on the job's cgroup.

systemd-run
===========

As well as schedulers you can use tools such as ``systemd-run`` to create a
cgroup, and run {Singularity} inside of it. This is convenient on modern cgroups
v2 systems, where the creation of cgroups can be delegated to users through
systemd. Without this delegation ``root`` privileges are required to create a
cgroup.

For example, assuming your system is configured correctly for unprivileged
cgroup creation via systemd, you can limit the number of CPUs a container run is
allowed to use:

.. code-block:: none

    $ systemd-run --user --scope -p AllowedCPUs=1,2 -- singularity run mycontainer.sif

* ``--user`` instructs systemd that we want to run as our own user account.

* ``--scope`` will run our command in an interactive scope that inherits from our
  environment. By default the command would run as a service, in the background.

* ``-p AllowedCPUs=1,2`` sets a property on our scope, so that in this case
  systemd will then setup a cgroup limiting our command to using CPU 1 and 2 only.

* The double hyphen ``--`` separates options for ``systemd-run`` from the actual
  command we wish to execute. This is important so that ``systemd-run`` doesn't
  capture any flags we might need to pass to ``singularity``.

You can read more about how systemd can control resources uses at the link
below, which details the properties you can set using ``systemd-run``.

https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html

------------------------------------
Using Singularity to Create a Cgroup
------------------------------------

{Singularity} 3.9 and above can directly apply resource limitations to systems
configured for both cgroups v1 and the v2 unified hierarchy. Resource limits are
specified using a TOML file that represents the `resources` section of the OCI
runtime-spec:
https://github.com/opencontainers/runtime-spec/blob/master/config-linux.md#control-groups

On a cgroups v1 system the resources configuration is applied directly. On a
cgroups v2 system the configuration is translated and applied to the unified
hierarchy.

Under cgroups v1, access restrictions for device nodes are managed directly.
Under cgroups v2, the restrictions are applied by attaching eBPF programs that
implement the requested access controls.

.. note::

   {Singularity} does not currently support applying native cgroups v2
   ``unified`` resource limit specifications. Use the cgroups v1 limits, which
   will be translated to v2 format when applied on a cgroups v2 system.


Examples
========

To apply resource limits to a container, use the ``--apply-cgroups`` flag, which
takes a path to a TOML file specifying the cgroups configuration to be applied:

.. code-block:: none

  $ sudo singularity shell --apply-cgroups /path/to/cgroups.toml my_container.sif

.. note::

  The ``--apply-cgroups`` option can only be used with root privileges.

Limiting Memory
---------------

To limit the amount of memory that your container uses to 500MB (524288000
bytes), set a ``limit`` value inside the ``[memory]`` section of your cgroups
TOML file:

.. code-block:: none

  [memory]
      limit = 524288000

Start your container, applying the toml file, e.g.:

.. code-block:: none

  $ sudo singularity run --apply-cgroups path/to/cgroups.toml library://alpine

After that, you can verify that the container is only using 500MB of memory.
This example assumes that there is only one running container. If you are
running multiple containers you will find multiple cgroups trees under the
``singularity`` directory.

.. code-block:: none

  # cgroups v1
  $ cat /sys/fs/cgroup/memory/singularity/*/memory.limit_in_bytes
    524288000

  # cgroups v2 - note translation of memory.limit_in_bytes -> memory.max
  $ cat /sys/fs/cgroup/singularity/*/memory.max
  524288000


Limiting CPU
------------

CPU usage can be limited using different strategies, with limits specified in
the ``[cpu]`` section of the TOML file.

**shares**

This corresponds to a ratio versus other cgroups with cpu shares. Usually the
default value is ``1024``. That means if you want to allow to use 50% of a
single CPU, you will set ``512`` as value.

.. code-block:: none

  [cpu]
      shares = 512

A cgroup can get more than its share of CPU if there are enough idle CPU cycles
available in the system, due to the work conserving nature of the scheduler, so
a contained process can consume all CPU cycles even with a ratio of 50%. The
ratio is only applied when two or more processes conflicts with their needs of
CPU cycles.

**quota/period**

You can enforce hard limits on the CPU cycles a cgroup can consume, so contained
processes can't use more than the amount of CPU time set for the cgroup.
``quota`` allows you to configure the amount of CPU time that a cgroup can use
per period. The default is 100ms (100000us). So if you want to limit amount of
CPU time to 20ms during period of 100ms:

.. code-block:: none

  [cpu]
      period = 100000
      quota = 20000

**cpus/mems**

You can also restrict access to specific CPUs (cores) and associated memory
nodes by using ``cpus/mems`` fields:

.. code-block:: none

  [cpu]
      cpus = "0-1"
      mems = "0-1"

Where the container has limited access to CPU 0 and CPU 1.

.. note::

  It's important to set identical values for both ``cpus`` and ``mems``.


Limiting IO
-----------

To control block device I/O, applying limits to competing container, use the
``[blockIO]`` section of the TOML file:

.. code-block:: none

  [blockIO]
      weight = 1000
      leafWeight = 1000

``weight`` and ``leafWeight`` accept values between ``10`` and ``1000``.

``weight`` is the default weight of the group on all the devices until and
unless overridden by a per device rule.

``leafWeight`` relates to weight for the purpose of deciding how heavily to
weigh tasks in the given cgroup while competing with the cgroup's child cgroups.


To apply limits to specific block devices, you must set configuration for
specific device major/minor numbers. For example, to override
``weight/leafWeight`` for ``/dev/loop0`` and ``/dev/loop1`` block devices, set
limits for device major 7, minor 0 and 1:

.. code-block:: none

  [blockIO]
      [[blockIO.weightDevice]]
          major = 7
          minor = 0
          weight = 100
          leafWeight = 50
      [[blockIO.weightDevice]]
          major = 7
          minor = 1
          weight = 100
          leafWeight = 50

You can also limit the IO read/write rate to a specific absolute value, e.g.
16MB per second for the ``/dev/loop0`` block device. The ``rate`` is specified
in bytes per second.

.. code-block:: none

  [blockIO]
      [[blockIO.throttleReadBpsDevice]]
          major = 7
          minor = 0
          rate = 16777216
      [[blockIO.throttleWriteBpsDevice]]
          major = 7
          minor = 0
          rate = 16777216

Limiting Device Access
----------------------

You can limit read (``r``), write (``w``), or creation (``c``) of devices by a
container. Like applying I/O limits to devices, you must use device node major
and minor numbers to create rules for specific devices or classes of device.

In this example, a container is configured to only be able to read from or write
to ``/dev/null``:

.. code-block:: none

    [[devices]]
        access = "rwm"
        allow = false
    [[devices]]
        access = "rw"
        allow = true
        major = 1
        minor = 3
        type = "c"

Other limits
------------

{Singularity} can apply all resource limits that are valid in the OCI
runtime-spec ``resources`` section, **except** native ``unified``
cgroups v2 constraints. Use the cgroups v1 limits, which will be
translated to v2 format when applied on a cgroups v1 system.

See
https://github.com/opencontainers/runtime-spec/blob/master/config-linux.md#control-groups
for information about the available limits. Note that {Singularity} uses TOML
format for the confiuration file, rather than JSON.
