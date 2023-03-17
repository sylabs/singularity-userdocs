.. _cgroups:

############################
Limiting Container Resources
############################

It's often useful to limit the resources that are consumed by a container, e.g.
to allow the container to only use 1 CPU, or 50% of the RAM on the system.
Although on HPC clusters it's common to launch containers with a job scheduler
that can set limits per job, the following scenarios are examples where more
direct control is useful:

* When running multiple containerized applications inside an HPC job, where each
  container in the job should have different resource limits.

* When testing HPC code on a workstation, to avoid excessive CPU / RAM usage
  bringing the desktop environment and other applications to a halt.

* When benchmarking code that doesn't provide internal means to limit the number
  of CPUs it uses.

There are three ways to apply limits to a container that is run with
{Singularity}:

* Using the command line flags introduced in v3.10.

* Using the ``--apply-cgroups`` flag to apply a ``cgroups.toml`` file that
  defines the resource limits.

* Using external tools such as ``systemd-run`` tool to apply limits, and then
  call ``singularity``.

****************************
Requirements - Linux Cgroups
****************************

Resource limits are applied to containers using functionality in the Linux
kernel known as *control groups* or *cgroups*. There are two versions of
*cgroups*:

**cgroups v1** has a more complex structure, and allows only the root user to
safely apply limits to applications. If your system is using cgroups v1 then you
can only use the CLI resource limit flags or ``--apply-cgroups`` when running
containers as the root user.

**cgroups v2** has a simplified structure, and is designed in a way that permits
*delegation* of cgroups control to standard users. This delegation is usually
accomplished via `systemd`.

Generally, to apply resource limits to a container as a non-root user your
system must:

* Be using cgroups v2, in the unified hierarchy mode.
* Have a Linux kernel version >= 4.15.
* Have systemd version >= 224.
* Have ``systemd cgroups`` enabled in ``singularity.conf`` (this is the default).
* Have systemd configured to delegate cgroups controllers to non-root users.

Recent distributions such as Ubuntu 22.04, Debian 11, Fedora 31, and newer,
satisfy these criteria by default. On older distributions support can often be
enabled. Consult the admin documentation or speak to your system administrator
about this.

.. _cgroup_flags:

*************************
Command Line Limit Flags
*************************

{Singularity} 3.10 introduced a number of simple command line flags that you can
use with `shell/run/exec` and the `instance` commands to directly apply resource
limits to a container when you run it.

The flags detailed below are compatible with those used by the ``docker`` CLI,
except that the short forms are not supported. For example, you cannot use
``-c`` instead of ``--cpu-shares`` because ``-c`` is used by {Singularity} for
another purpose.

Not all limits provided by other runtimes are currently supported by
{Singularity}. Specifically, the ``--device-`` flags supported by the ``docker``
CLI are not yet available.

CPU Limits
==========

``--cpus`` sets the number of CPUs, or fractional CPUs, that the container can
use.  The minimum is ``0.01`` or one tenth of a physical CPU. The maximum is the
number of CPU cores on your system.

.. code::

   # Limit container to 3.5 CPUs
   $ singularity run --cpus 3.5 myfirstapp.sif

``--cpu-shares`` sets a relative weight for a container's access to the system's
CPUs, versus other containers that also have a ``--cpus-shares`` value set. If
container A has 1024 cpu shares, and container B has 512 cpu shares, then
container A will receive twice as much CPU time than container B, but *only when
there is contention for CPUs*, i.e. the containers are able to consume more CPU
time than is available.

.. code::

   # Container A - twice as much CPU priority as container B
   $ singularity run --cpu-shares 1024 myfirstapp.sif

   # Container A - half as much CPU priority as container A
   $ singularity run --cpu-shares 512 mysecondapp.sif

``--cpu-set-cpus`` specifies a list of physical CPU IDs on which a container can
run. For example, on a dual CPU system you might pin one container to the first
12 cores on CPU 1, and a second container to the second 12 cores on CPU 2.

``--cpu-set-mems`` specifies a list of memory nodes the container can use. It
should generally be set to the same value as ``--cpu-set-cpus``.

.. code::

   # Container A - first CPU
   $ singularity run --cpu-set-cpus 0-11 --cpu-set-mems 0-11 myfirstapp.sif

   # Container B - second CPU
   $ singularity run --cpu-set-cpus 12-23 --cpu-set-mems 12-23 myfirstapp.sif

Memory Limits
=============

``--memory`` sets the maximum amount of RAM that a container can use, in bytes.
You can use suffixes such as ``M`` or ``G`` to specify megabytes or gigabytes.
If the container tries to use more memory than its limit, the system will kill
it.

.. code::

   # Run a program that will use 10GB of RAM, with a 100MB limit
   $ singularity exec --memory 100M memhog.sif memhog 10G
   .................................................Killed

``--memory-reservation`` sets a soft limit, which should be lower than the hard
limit set with ``--memory``. When there is contention for memory, the system
will attempt to make sure the container doesn't exceed the soft limit.

.. code::

   # Kill my program if it exceeds 10G, but aim for 8G if there is contention
   $ singularity exec --memory 10G --memory-reservation 8G myfirstapp.sif

``--memory-swap`` sets the total amount of memory and swap space that a
container can use. You must set ``--memory`` along with ``--memory-swap``. A
value of ``-1`` means *unlimited swap*. If ``--memory-swap`` is not set or is
``0``, then the container can use an amount of swap up to the value of
``--memory``. It's easier to understand this flag with examples:

.. code::

   # Run a container that can use up to 1G RAM, or swap if it is swapped out
   $ singularity run --memory 1G myfirstapp.sif

   # Run a container that can use up to 1G RAM, and no swap space
   $ singularity run --memory 1G --memory-swap 1G myfirstapp.sif

   # Run a container that can use up to 1G RAM, and unlimited swap space
   $ singularity run --memory 1G --memory-swap -1 myfirstapp.sif

   # Run a container that can use up to 1G RAM, and 1G swap space
   $ singularity run --memory 1G --memory-swap 2G myfirstapp.sif


IO Limits
=========

.. note::

   Requires the ``cfq`` or ``bfq`` IO scheduler to be configured for block IO on
   the system. This is common on modern distributions, but not universal. Ask
   your system administrator if IO limits are not working as expected.

``--blkio-weight`` sets a relative weight for the container when performing
block I/O, e.g. reading/writing to/from disk. The weight should be between 10
and 1000, and will control how much I/O access a container recieves when there
is contention for I/O with other containers. It may be useful to give high
priority to a container that needs infrequent but time sensitive data access,
running alongside an application that is continuously performing bulk reads.

.. code::

   # Container A - ten times as much block IO priority as container B
   $ singularity run --blkio-weight 1000 myfirstapp.sif

   # Container A - ten times less block IO priority as container A
   $ singularity run --blkio-weight 100 mysecondapp.sif

``--blkio-weight-device`` sets a relative weight for the container when performing
block I/O on a specific device. Specify the device and weight as ``<device path>:weight``:

.. code::

   # Container A - ten times as much block IO priority as container B on disk /dev/sda
   $ singularity run --blkio-weight-device /dev/sda:1000 myfirstapp.sif

   # Container A - ten times less block IO priority as container A on disk /dev/sda
   $ singularity run --blkio-weight-device /dev/sda:100 mysecondapp.sif

******************************************
Applying Resource Limits From a TOML file
******************************************

{Singularity} 3.9 and above can directly apply resource limitations to systems
configured for both cgroups v1 and the v2 unified hierarchy, using the
``--apply-cgroups`` flag. Resource limits are specified using a TOML file that
represents the `resources` section of the OCI runtime-spec:
https://github.com/opencontainers/runtime-spec/blob/master/config-linux.md#control-groups

On a cgroups v1 system the resources configuration is applied directly.
On a cgroups v2 system the configuration is translated and applied to
the unified hierarchy.

Under cgroups v1, access restrictions for device nodes are managed
directly. Under cgroups v2, the restrictions are applied by attaching
eBPF programs that implement the requested access controls.

To apply resource limits to a container, using the ``--apply-cgroups``
flag, which takes a path to a TOML file specifying the cgroups
configuration to be applied:

.. code::

   $ singularity shell --apply-cgroups /path/to/cgroups.toml my_container.sif

.. note::

   Using ``--apply-cgroups`` as a non-root user requires a cgroups v2 system,
   configured to use the ``systemd cgroups`` manager in ``singularity.conf``.

CPU Limits
==========

CPU usage can be limited using different strategies, with limits
specified in the ``[cpu]`` section of the TOML file.

**shares**

This corresponds to a ratio versus other cgroups with cpu shares.
Usually the default value is ``1024``. That means if you want to allow
to use 50% of a single CPU, you will set ``512`` as value.

.. code::

   [cpu]
       shares = 512

A cgroup can get more than its share of CPU if there are enough idle CPU
cycles available in the system, due to the work conserving nature of the
scheduler, so a contained process can consume all CPU cycles even with a
ratio of 50%. The ratio is only applied when two or more processes
conflicts with their needs of CPU cycles.

**quota/period**

You can enforce hard limits on the CPU cycles a cgroup can consume, so
contained processes can't use more than the amount of CPU time set for
the cgroup. ``quota`` allows you to configure the amount of CPU time
that a cgroup can use per period. The default is 100ms (100000us). So if
you want to limit amount of CPU time to 20ms during period of 100ms:

.. code::

   [cpu]
       period = 100000
       quota = 20000

**cpus/mems**

You can also restrict access to specific CPUs (cores) and associated
memory nodes by using ``cpus/mems`` fields:

.. code::

   [cpu]
       cpus = "0-1"
       mems = "0-1"

Where the container has limited access to CPU 0 and CPU 1.

.. note::

   It's important to set identical values for both ``cpus`` and
   ``mems``.

Memory Limits
=============

To limit the amount of memory that your container uses to 500MB
(524288000 bytes), set a ``limit`` value inside the ``[memory]`` section
of your cgroups TOML file:

.. code::

   [memory]
       limit = 524288000

Start your container, applying the toml file, e.g.:

.. code::

   $ singularity run --apply-cgroups path/to/cgroups.toml library://alpine

After that, you can verify that the container is only using 500MB of
memory. This example assumes that there is only one running container.
If you are running multiple containers you will find multiple cgroups
trees under the ``singularity`` directory.

.. code::

   # cgroups v1
   $ cat /sys/fs/cgroup/memory/singularity/*/memory.limit_in_bytes
     524288000

   # cgroups v2 - note translation of memory.limit_in_bytes -> memory.max
   $ cat /sys/fs/cgroup/singularity/*/memory.max
   524288000

IO Limits
=========

To control block device I/O, applying limits to competing container, use
the ``[blockIO]`` section of the TOML file:

.. code::

   [blockIO]
       weight = 1000
       leafWeight = 1000

``weight`` and ``leafWeight`` accept values between ``10`` and ``1000``.

``weight`` is the default weight of the group on all the devices until
and unless overridden by a per device rule.

``leafWeight`` relates to weight for the purpose of deciding how heavily
to weigh tasks in the given cgroup while competing with the cgroup's
child cgroups.

To apply limits to specific block devices, you must set configuration
for specific device major/minor numbers. For example, to override
``weight/leafWeight`` for ``/dev/loop0`` and ``/dev/loop1`` block
devices, set limits for device major 7, minor 0 and 1:

.. code::

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

You can also limit the IO read/write rate to a specific absolute value,
e.g. 16MB per second for the ``/dev/loop0`` block device. The ``rate``
is specified in bytes per second.

.. code::

   [blockIO]
       [[blockIO.throttleReadBpsDevice]]
           major = 7
           minor = 0
           rate = 16777216
       [[blockIO.throttleWriteBpsDevice]]
           major = 7
           minor = 0
           rate = 16777216

Device Limits
=============

.. note::

   Device limits can only be applied when running as the root user, and will be
   ignored as a non-root user.

You can limit read (``r``), write (``w``), or creation (``c``) of
devices by a container. Like applying I/O limits to devices, you must
use device node major and minor numbers to create rules for specific
devices or classes of device.

In this example, a container is configured to only be able to read from
or write to ``/dev/null``:

.. code::

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
============

{Singularity} can apply all resource limits that are valid in the OCI
runtime-spec ``resources`` section. If you use cgroups v1 limits on a cgroups v2
system they will be translated at runtime. You may also specify native cgroups
v2 limits under the ``unified`` key.

See
https://github.com/opencontainers/runtime-spec/blob/master/config-linux.md#control-groups
for information about the available limits. Note that {Singularity} uses
TOML format for the configuration file, rather than JSON.

********************************************
Applying Resource Limits With External Tools
********************************************

Because {Singularity} starts a container as a simple process, rather
than using a daemon, you can limit resource usage by running the
``singularity`` command inside an existing cgroup. This is convenient
where, for example, a job scheduler uses cgroups to control job limits.
By running ``singularity`` inside your batch script, your container will
respect the limits set by the scheduler on the job's cgroup.

systemd-run
===========

As well as schedulers you can use tools such as ``systemd-run`` to
create a cgroup, and run {Singularity} inside of it. This is convenient
on modern cgroups v2 systems, where the creation of cgroups can be
delegated to users through systemd. Without this delegation ``root``
privileges are required to create a cgroup.

For example, assuming your system is configured correctly for
unprivileged cgroup creation via systemd, you can limit the number of
CPUs a container run is allowed to use:

.. code::

   $ systemd-run --user --scope -p AllowedCPUs=1,2 -- singularity run mycontainer.sif

-  ``--user`` instructs systemd that we want to run as our own user
   account.

-  ``--scope`` will run our command in an interactive scope that
   inherits from our environment. By default the command would run as a
   service, in the background.

-  ``-p AllowedCPUs=1,2`` sets a property on our scope, so that in this
   case systemd will then setup a cgroup limiting our command to using
   CPU 1 and 2 only.

-  The double hyphen ``--`` separates options for ``systemd-run`` from
   the actual command we wish to execute. This is important so that
   ``systemd-run`` doesn't capture any flags we might need to pass to
   ``singularity``.

You can read more about how systemd can control resources uses at the
link below, which details the properties you can set using
``systemd-run``.

https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html