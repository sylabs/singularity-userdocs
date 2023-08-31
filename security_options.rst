.. _security-options:

################
Security Options
################

.. _sec:security_options:

{Singularity} can make use of various Linux kernel features to modify the
security scope and context of running containers. Non-root users may be granted
additional permissions using Linux capabilities. SELinux, AppArmor, and Seccomp
can be used to restrict the operations that can be performed by a container.

******************
Linux Capabilities
******************

Native runtime / non-OCI-Mode
=============================

In {Singularity}'s default configuration, without ``--oci``, a container started
by root receives all capabilities, while a container started by a non-root user
receives no capabilities.

Additionally, {Singularity} provides support for granting and revoking Linux
capabilities on a user or group basis. For example, let us suppose that an
administrator has decided to grant a user (named ``pinger``) capabilities to
open raw sockets so that they can use ``ping`` in a container where the binary
is controlled via capabilities. For information about how to manage capabilities
as an admin please refer to the `capability admin docs
<https://sylabs.io/guides/{adminversion}/admin-guide/configfiles.html#capability.json>`_.

.. note::

   In {Singularity}'s default setuid and non-OCI mode, containers are only
   isolated in a mount namespace. A user namespace, which limits the scope of
   capabilities, is not used by default.

   Therefore, it is extremely important to recognize that **granting users Linux
   capabilities with the** ``capability`` **command group is usually identical
   to granting those users root level access on the host system**. Most, if not
   all, capabilities will allow users to "break out" of the container and become
   root on the host. This feature is targeted toward special use cases (like
   cloud-native architectures) where an admin/developer might want to limit the
   attack surface within a container that normally runs as root. This is not a
   good option in multi-tenant HPC environments where an admin wants to grant a
   user special privileges within a container. For that and similar use cases,
   the :ref:`fakeroot feature <fakeroot>` is a better option.

To take advantage of this granted capability as a user, ``pinger`` must
also request the capability when executing a container with the
``--add-caps`` flag like so:

.. code::

   $ singularity exec --add-caps CAP_NET_RAW library://sylabs/tests/ubuntu_ping:v1.0 ping -c 1 8.8.8.8
   PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
   64 bytes from 8.8.8.8: icmp_seq=1 ttl=52 time=73.1 ms

   --- 8.8.8.8 ping statistics ---
   1 packets transmitted, 1 received, 0% packet loss, time 0ms
   rtt min/avg/max/mdev = 73.178/73.178/73.178/0.000 ms

If the admin decides that it is no longer necessary to allow the user
``pinger`` to open raw sockets within {Singularity} containers, they can
revoke the appropriate Linux capability and ``pinger`` will not be able
to add that capability to their containers anymore:

.. code::

   $ singularity exec --add-caps CAP_NET_RAW library://sylabs/tests/ubuntu_ping:v1.0 ping -c 1 8.8.8.8
   WARNING: not authorized to add capability: CAP_NET_RAW
   ping: socket: Operation not permitted

Another scenario which is atypical of shared resource environments, but
useful in cloud-native architectures is dropping capabilities when
spawning containers as the root user to help minimize attack surfaces.
With a default installation of {Singularity}, containers created by the
root user will maintain all capabilities. This behavior is configurable
if desired. Check out the `capability configuration
<https://sylabs.io/guides/{adminversion}/admin-guide/configfiles.html#capability.json>`_
and `root default capabilities
<https://sylabs.io/guides/{adminversion}/admin-guide/configfiles.html#setuid-and-capabilities>`_
sections of the admin docs for more information.

Assuming the root user will execute containers with the ``CAP_NET_RAW``
capability by default, executing the same container ``pinger`` executed
above works without the need to grant capabilities:

.. code::

   # singularity exec library://sylabs/tests/ubuntu_ping:v1.0 ping -c 1 8.8.8.8
   PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
   64 bytes from 8.8.8.8: icmp_seq=1 ttl=52 time=59.6 ms

   --- 8.8.8.8 ping statistics ---
   1 packets transmitted, 1 received, 0% packet loss, time 0ms
   rtt min/avg/max/mdev = 59.673/59.673/59.673/0.000 ms

Now we can manually drop the ``CAP_NET_RAW`` capability like so:

.. code::

   # singularity exec --drop-caps CAP_NET_RAW library://sylabs/tests/ubuntu_ping:v1.0 ping -c 1 8.8.8.8
   ping: socket: Operation not permitted

And now the container will not have the ability to create new sockets,
causing the ``ping`` command to fail.

The ``--add-caps`` and ``--drop-caps`` options will accept the ``all``
keyword. Of course appropriate caution should be exercised when using
this keyword.

OCI-Mode
========

When containers are run in OCI-mode, by a non-root user, initialization is
always performed inside a user namespace. The capabilities granted to a
container are specific to this user namespace. For example, ``CAP_SYS_ADMIN``
granted to an OCI-mode container does not give the user the ability to mount a
filesystem outside of the container's user namespace.

Because of this isolation of capabilities users can add and drop capabilities,
using ``--add-caps`` and ``--drop-caps``, without the need for the administrator
to have granted permission to do so with the ``singularity capabilities``
command.

OCI-mode containers do not inherit the user's own capabilities, but instead run
with a default set of capabilities that matches other OCI runtimes.

-  CAP_NET_RAW
-	CAP_NET_BIND_SERVICE
-	CAP_AUDIT_READ
-	CAP_AUDIT_WRITE
-	CAP_DAC_OVERRIDE
-	CAP_SETFCAP
-	CAP_SETPCAP
-	CAP_SETGID
-	CAP_SETUID
-	CAP_MKNOD
-	CAP_CHOWN
-	CAP_FOWNER
-	CAP_FSETID
-	CAP_KILL
-	CAP_SYS_CHROOT

When the container is entered as the root user (e.g. with ``--fakeroot``), these
default capabilities are added to the effective, permitted, and bounding sets.

When the container is entered as a non-root user, these default capabilities are
added to the bounding set.

*******************************
Security related action options
*******************************

When starting a container with the action commands ``shell``, ``exec``, and
``run``, various flags allow fine grained control of security.

``--add-caps``
==============

In the default non-OCI-mode, ``--add-caps`` will grant specified Linux
capabilities (e.g. ``CAP_NET_RAW``) to a container, provided that those
capabilities have been granted to the user by an administrator using the
``capability add`` command. This option will also accept the case insensitive
keyword ``all`` to add every capability granted by the administrator.

In OCI-mode, ``--add-caps`` will grant specified Linux capabilities (e.g.
``CAP_NET_RAW``) to the container. Because the container runs in a user
namespace, the capabilities are not effective on the host and do not have to be
granted by the administrator. The keyword ``all`` will grant all available
capabilities to the container.

``--drop-caps``
===============

In the default non-OCI-mode, the root user has a full set of capabilities when
they enter the container. You may choose to drop specific capabilities when you
initiate a container as root to enhance security.

For instance, to drop the ability for the root user to open a raw socket
inside the container:

.. code::

   $ sudo singularity exec --drop-caps CAP_NET_RAW library://centos ping -c 1 8.8.8.8
   ping: socket: Operation not permitted

In OCI-mode any user can use ``--drop-caps`` to run a container with fewer
capabilities than the default OCI capability set.

The ``--drop-caps`` option will also accept the case insensitive keyword
``all`` as an option to drop all capabilities when entering the
container.

``--allow-setuid``
==================

The SetUID bit allows a program to be executed as the user that owns the
binary. The most well-known SetUID binaries are owned by root and allow
a user to execute a command with elevated privileges. But other SetUID
binaries may allow a user to execute a command as a service account.

By default SetUID is disallowed within {Singularity} containers as a
security precaution, by mounting container filesystems as ``nosetuid.``

In the default non-OCI-mode, the root user can override this precaution and
allow SetUID binaries to behave as expected within a {Singularity} container
with the ``--allow-setuid`` option like so:

.. code::

   $ sudo singularity shell --allow-setuid some_container.sif

In OCI-mode, any user can permit SetUID binaries with the ``--allow-setuid``
option. Because an OCI-mode container is always run in a user namespace, SetUID
will change to UIDs inside a user's permitted subuid/subgid mapping. This does
not allow access to arbitrary UIDs on the host system.

``--keep-privs``
================

In the default non-OCI-mode, it is possible for an admin to set a different set
of default capabilities or to reduce the default capabilities to zero for the
root user by setting the ``root default capabilities`` parameter in the
``singularity.conf`` file to ``file`` or ``no`` respectively. If this change is
in effect, the root user can override the ``singularity.conf`` file and enter
the container with full capabilities using the ``--keep-privs`` option.

.. code::

   $ sudo singularity exec --keep-privs library://centos ping -c 1 8.8.8.8
   PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
   64 bytes from 8.8.8.8: icmp_seq=1 ttl=128 time=18.8 ms

   --- 8.8.8.8 ping statistics ---
   1 packets transmitted, 1 received, 0% packet loss, time 0ms
   rtt min/avg/max/mdev = 18.838/18.838/18.838/0.000 ms

In OCI-mode, the ``--keep-privs`` option can be used by any user. In this
mode, ``--keep-privs`` will cause the container to run inheriting the current
effective capabilities rather than using the OCI default capability set. When
entering the container as a non-root user, the capabilities are only inherited
to the bounding set.

``--no-privs``
==============

In the default non-OCI-mode, the ``--no-privs`` option allows the root user to run
a container with all capabilities dropped, and sets the ``no_new_privs`` bit
that will prevent the container process gaining any further privilege.

In OCI-mode, the ``--no-privs`` option can be used by any user to run a
container with all capabilities dropped, and to set the ``no_new_privs`` bit
that will prevent the container process gaining any further privilege.

``--security``
==============

The ``--security`` flag, currently supported in non-OCI-mode only, allows the
root user to leverage security modules such as SELinux, AppArmor, and seccomp
within your {Singularity} container. It is also possible to change the UID and
GID of the user within the container at runtime.

For instance:

.. code::

   $ sudo whoami
   root

   $ sudo singularity exec --security uid:1000 my_container.sif whoami
   david

To use seccomp to blacklist a command follow this procedure. (It is
actually preferable from a security standpoint to whitelist commands but
this will suffice for a simple example.) Note that this example was run
on Ubuntu and that {Singularity} was installed with the
``libseccomp-dev`` and ``pkg-config`` packages as dependencies.

First write a configuration file. An example configuration file is
installed with {Singularity}, normally at
``/usr/local/etc/singularity/seccomp-profiles/default.json``. For this
example, we will use a much simpler configuration file to blacklist the
``mkdir`` command.

.. code::

   {
       "defaultAction": "SCMP_ACT_ALLOW",
       "archMap": [
           {
               "architecture": "SCMP_ARCH_X86_64",
               "subArchitectures": [
                   "SCMP_ARCH_X86",
                   "SCMP_ARCH_X32"
               ]
           }
       ],
       "syscalls": [
           {
               "names": [
                   "mkdir"
               ],
               "action": "SCMP_ACT_KILL",
               "args": [],
               "comment": "",
               "includes": {},
               "excludes": {}
           }
       ]
   }

We'll save the file at ``/home/david/no_mkdir.json``. Then we can invoke
the container like so:

.. code::

   $ sudo singularity shell --security seccomp:/home/david/no_mkdir.json my_container.sif

   Singularity> mkdir /tmp/foo
   Bad system call (core dumped)

Note that attempting to use the blacklisted ``mkdir`` command resulted
in a core dump.

The full list of arguments accepted by the ``--security`` option are as
follows:

.. code::

   --security="seccomp:/usr/local/etc/singularity/seccomp-profiles/default.json"
   --security="apparmor:/usr/bin/man"
   --security="selinux:context"
   --security="uid:1000"
   --security="gid:1000"
   --security="gid:1000:1:0" (multiple gids, first is always the primary group)

********************
Encrypted containers
********************

Beginning in {Singularity} 3.4.0 it is possible to build and run
encrypted containers. The containers are decrypted at runtime entirely
in kernel space, meaning that no intermediate decrypted data is ever
present on disk. See :ref:`encrypted containers <encryption>` for more
details.