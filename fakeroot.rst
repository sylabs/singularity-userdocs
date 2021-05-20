.. _fakeroot:

================
Fakeroot feature
================

--------
Overview
--------

The fakeroot feature (commonly referred as rootless mode) allows an unprivileged user
to run a container as a **"fake root"** user by leveraging
`user namespace UID/GID mapping <http://man7.org/linux/man-pages/man7/user_namespaces.7.html>`_.

.. note:: 

	This feature requires a Linux kernel >= 3.8, but the recommended version is >= 3.18

A **"fake root"** user has almost the same administrative rights as root but only **inside the container**
and the **requested namespaces**, which means that this user:

  - can set different user/group ownership for files or directories they own
  - can change user/group identity with su/sudo commands
  - has full privileges inside the requested namespaces (network, ipc, uts)

---------------------
Restrictions/security
---------------------

Filesystem
==========

A **"fake root"** user can't access or modify files and directories for which they don't
already have access or rights on the host filesystem, so a **"fake root"** user won't be able
to access root-only host files like ``/etc/shadow`` or the host ``/root`` directory.

Additionally, all files or directories created by the **"fake root"** user are owned by
``root:root`` inside container but as ``user:group`` outside of the container.
Let's consider the following example, in this case "user" is authorized to use the fakeroot feature
and can use 65536 UIDs starting at 131072 (same thing for GIDs).

+----------------------+-----------------------+
| UID inside container | UID outside container |
+======================+=======================+
| 0 (root)             | 1000 (user)           |
+----------------------+-----------------------+
| 1 (daemon)           | 131072 (non-existent) |
+----------------------+-----------------------+
| 2 (bin)              | 131073 (non-existent) |
+----------------------+-----------------------+
| ...                  | ...                   |
+----------------------+-----------------------+
| 65536                | 196607                |
+----------------------+-----------------------+

Which means if the **"fake root"** user creates a file under a ``bin`` user in the container, this file will
be owned by ``131073:131073`` outside of container. The responsibility relies on the administrator
to ensure that there is no overlap with the current user's UID/GID on the system.

Network
=======

Restrictions are also applied to networking, if ``singularity`` is executed without the ``--net`` flag,
the **"fake root"** user won't be able to use ``ping`` or bind a container service to a port below
1024.

With ``--net`` the **"fake root"** user has full privileges in a dedicated container network. Inside
the container network they can bind on privileged ports below 1024, use ping, manage firewall rules,
listen to traffic, etc. Anything done in this dedicated network won't affect the host network.

.. note:: 
    Of course an unprivileged user could not map host ports below than 1024 by using:
    ``--network-args="portmap=80:80/tcp"``

.. warning::
    For unprivileged installation of {Singularity} or if ``allow setuid = no`` is set in ``singularity.conf``
    users won't be able to use a ``fakeroot`` network.

----------------------------
Requirements / Configuration
----------------------------

Fakeroot depends on user mappings set in ``/etc/subuid`` and group mappings in ``/etc/subgid``, so your username 
needs to be listed in those files with a valid mapping (see the admin-guide for details), if you can't edit
the files ask an administrator.

In {Singularity} ``3.5`` a ``singularity config fakeroot`` command has been added to allow configuration
of the ``/etc/subuid`` and ``/etc/subgid`` mappings from the {Singularity} command line. You must be a root
user or run with ``sudo`` to use ``config fakeroot``, as the mapping files are security sensitive. See the
admin-guide for more details.

-----
Usage
-----

If your user account is configured with valid ``subuid`` and ``subgid`` mappings you work as a fake root user
inside a container by using the ``--fakeroot`` or ``-f`` option. 

The ``--fakeroot`` option is available with the following singularity commands:

  - ``shell``
  - ``exec``
  - ``run``
  - ``instance start``
  - ``build``

Build
=====

With fakeroot an unprivileged user can now build an image from a definition file with few restrictions. Some bootstrap
methods that require creation of block devices (like ``/dev/null``) may not always work correctly with **"fake root"**,
{Singularity} uses seccomp filters to give programs the illusion that block device creation succeeded. This appears to
work with ``yum`` bootstraps and *may* work with other bootstrap methods, although ``debootstrap`` is known to not work.

Examples
========

Build from a definition file:
-----------------------------

.. code-block:: none

    singularity build --fakeroot /tmp/test.sif /tmp/test.def

Ping from container:
--------------------

.. code-block:: none

    singularity exec --fakeroot --net docker://alpine ping -c1 8.8.8.8

HTTP server:
------------

.. code-block:: none

    singularity run --fakeroot --net --network-args="portmap=8080:80/tcp" -w docker://nginx
