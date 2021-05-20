.. _cgroups:

=========================================
Limiting container resources with cgroups
=========================================

Starting in {Singularity} 3.0, users have the ability to limit container resources
using cgroups.

--------
Overview
--------

{Singularity} cgroups support can be configured and utilized via a TOML file. An
example file is typically installed at
``/usr/local/etc/singularity/cgroups/cgroups.toml`` (but may also be installed 
in other locations such as ``/etc/singularity/cgroups/cgroups.toml`` depending 
on your installation method).  You can copy and edit this file to suit your 
needs.  Then when you need to limit your container resources, apply the settings 
in the TOML file by using the path as an argument to the ``--apply-cgroups`` 
option like so:

.. code-block:: none

    $ sudo singularity shell --apply-cgroups /path/to/cgroups.toml my_container.sif

The ``--apply-cgroups`` option can only be used with root privileges.


--------
Examples
--------

Limiting memory
===============

To limit the amount of memory that your container uses to 500MB (524288000
bytes), follow this example.  First, create a ``cgroups.toml`` file like this
and save it in your home directory.

.. code-block:: none

    [memory]
        limit = 524288000

Start your container like so:

.. code-block:: none

    $ sudo singularity instance start --apply-cgroups /home/$USER/cgroups.toml \
        my_container.sif instance1

After that, you can verify that the container is only using 500MB of memory.
(This example assumes that ``instance1`` is the only running instance.)

.. code-block:: none

    $ cat /sys/fs/cgroup/memory/singularity/*/memory.limit_in_bytes
    524288000


After you are finished with this example, be sure to cleanup your instance with
the following command.

.. code-block:: none

    $ sudo singularity instance stop instance1

Similarly, the remaining examples can be tested by starting instances and
examining the contents of the appropriate subdirectories of ``/sys/fs/cgroup/``.

Limiting CPU
============

Limit CPU resources using one of the following strategies. The ``cpu`` section
of the configuration file can limit memory with the following:

shares
------

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

quota/period
------------

You can enforce hard limits on the CPU cycles a cgroup can consume, so
contained processes can't use more than the amount of CPU time set for the
cgroup. ``quota`` allows you to configure the amount of CPU time that a cgroup
can use per period. The default is 100ms (100000us). So if you want to limit
amount of CPU time to 20ms during period of 100ms:

.. code-block:: none

    [cpu]
        period = 100000
        quota = 20000

cpus/mems
---------

You can also restrict access to specific CPUs and associated memory nodes by
using ``cpus/mems`` fields:

.. code-block:: none

    [cpu]
        cpus = "0-1"
        mems = "0-1"

Where container has limited access to CPU 0 and CPU 1.

.. note::

    It's important to set identical values for both ``cpus`` and ``mems``.

For more information about limiting CPU with cgroups, see the following external
links:

- `Red Hat resource management guide section 3.2 CPU <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-cpu/>`_

- `Red Hat resource management guide section 3.4 CPUSET <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-cpuset>`_

- `Kernel scheduler documentation <https://www.kernel.org/doc/Documentation/scheduler/sched-bwc.txt>`_

Limiting IO
===========

You can limit and monitor access to I/O for block devices.  Use the
``[blockIO]`` section of the configuration file to do this like so:

.. code-block:: none

    [blockIO]
        weight = 1000
        leafWeight = 1000

``weight`` and ``leafWeight`` accept values between ``10`` and ``1000``.

``weight`` is the default weight of the group on all the devices until and
unless overridden by a per device rule.

``leafWeight`` relates to weight for the purpose of deciding how heavily to
weigh tasks in the given cgroup while competing with the cgroup's child cgroups.

To override ``weight/leafWeight`` for ``/dev/loop0`` and ``/dev/loop1`` block
devices you would do something like this:

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

You could limit the IO read/write rate to 16MB per second for the ``/dev/loop0``
block device with the following configuration.  The rate is specified in bytes
per second.

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

To limit the IO read/write rate to 1000 IO per second (IOPS) on ``/dev/loop0``
block device, you can do the following. The rate is specified in IOPS.

.. code-block:: none

    [blockIO]
        [[blockIO.throttleReadIOPSDevice]]
            major = 7
            minor = 0
            rate = 1000
        [[blockIO.throttleWriteIOPSDevice]]
            major = 7
            minor = 0
            rate = 1000

For more information about limiting IO, see the following external links:

- `Red Hat resource management guide section 3.1 blkio <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/ch-subsystems_and_tunable_parameters#sec-blkio>`_

- `Kernel block IO controller documentation <https://www.kernel.org/doc/Documentation/cgroup-v1/blkio-controller.txt>`_

- `Kernel CFQ scheduler documentation <https://www.kernel.org/doc/Documentation/block/cfq-iosched.txt>`_

Limiting device access
----------------------

You can limit read, write, or creation of devices. In this example, a container
is configured to only be able to read from or write to ``/dev/null``.

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

For more information on limiting access to devices the `Red Hat resource
management guide section 3.5 DEVICES <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-devices>`_.
