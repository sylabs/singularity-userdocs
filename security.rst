.. _security:

#########################
Security in {Singularity}
#########################

***************
Security Policy
***************

If you suspect you have found a vulnerability in {Singularity}, we want
to work with you so that it can be investigated, fixed, and disclosed in
a responsible manner. Please follow the steps in our published `Security
Policy <https://sylabs.io/security-policy>`__, which begins with
contacting us privately via `security@sylabs.io
<mailto:security@sylabs.io>`__.

Sylabs discloses vulnerabilities found in {Singularity} through public
CVE reports, as well as notifications on our community channels. We
encourage all users to monitor new releases of {Singularity} for
security information. Security patches are applied to the latest
open-source release.

SingularityPRO is a professionally curated and licensed version of
{Singularity} that provides added security, stability, and support
beyond that offered by the open-source project. Security and bug-fix
patches are backported to select versions of SingularityPRO, so that
they can be deployed long-term where required. PRO users receive
security fixes as detailed in the `Sylabs Security Policy
<https://sylabs.io/security-policy>`__.

**********
Background
**********

{Singularity} grew out of the need to implement a container platform
that was suitable for use on shared systems, such as HPC clusters. In
these environments, multiple people typically need to access the same
shared resource. User accounts, groups, and standard file permissions
limit their access to data and devices, and prevent them from disrupting
or accessing others' work.

To provide security in these environments a container needs to run as
the user who starts it on the system. Before the widespread adoption of
the Linux user namespace, only a privileged user could perform the
operations which are needed to run a container. A default Docker
installation uses a root-owned daemon to start containers, and users can
request that the daemon start a container on their behalf. However,
coordinating a daemon with other schedulers is difficult and, since the
daemon is privileged, users can ask it to carry out actions that they
wouldn't normally have permission to carry out themselves.

When a user runs a container with {Singularity}, it is started as a
normal process running under the user's account. Standard file
permissions and other security controls based on user accounts, groups,
and processes apply. In a default installation, {Singularity} uses a
setuid starter binary to perform only the specific tasks needed to setup
the container.

.. _setuid_and_userns:

************************
Setuid & User Namespaces
************************

Using a setuid binary to run container setup operations is essential to
support containers on older Linux distributions, such as CentOS 6, that
were previously common in HPC and enterprise. Newer distributions have
support for 'unprivileged user namespace creation'. This means a normal
user can create a user namespace, in which most setup operations needed
to run a container can be run, unprivileged.

Security Implications of Unprivileged User Namespaces
=====================================================

.. warning::

   **If you rely on the ECL or other container execution limits, you must
   disable unprivileged user namespace creation on your systems.**

When unprivileged user namespace creation is allowed on a system, a user can
supply and use their own unprivileged installation of Singularity or another
container runtime. They may also be able to use standard system tools such as
``unshare``, ``nsenter``, and FUSE mounts to access / execute arbitrary
containers without installing any runtime. Both of these approaches will allow
users to bypass any restrictions that have been set in a system-wide
installation of {Singularity}. These include:

* The ``allow container`` and ``limit container`` directives in
  ``singularity.conf``.
* The Execution Control List, which restricts execution of SIF container images
  via signature checks.

Note also that {Singularity}'s `--oci` mode is an unprivileged runtime that
requires unprivileged user namespace creation. It does not implement the
container restrictions that cannot be effectively enforced when unprivileged
user namespaces are available.

If your primary security concern is that of restricting the containers which
users can execute, you should use singularity in setuid mode, and ensure
unprivileged user namespace creation is disabled on the host.

Configuration and Limitations of User Namespace Mode
====================================================

{Singularity} supports running containers without setuid, using user
namespaces. It can be compiled with the ``--without-setuid`` option, or
``allow setuid = no`` can be set in ``singularity.conf`` to enable this.
In this mode *all* operations run as the user who starts the
``singularity`` program. However, there are some disadvantages to this
approach:

-  SIF and other single-file container images cannot be mounted using kernel
   mounts. {Singularity} will attempt to mount them in user space, using FUSE.
   If this is not possible, the container image must be extracted to a directory
   on disk to run. This impacts the speed of execution. As a result, workloads
   accessing large numbers of small files (as is the case with python
   application startup, for example) do not benefit from the reduced metadata
   load on the filesystem an image file provides. To force extraction to disk,
   instead of FUSE mount, use the ``--tmp-sandbox`` flag. To ensure containers
   are not extracted to disk, even when FUSE mounts fail,  use the
   ``--no-tmp-sandbox`` flag.

-  The effectiveness of signing and verifying container images is reduced. With
   both FUSE mounts, and sandbox directories, the content of the container can
   easily be modified at runtime and verification against the image's original
   signature cannot be performed.

-  Encryption is not supported. {Singularity} leverages kernel LUKS2
   mounts to run encrypted containers without writing a decrypted
   version of their content to disk.

-  Some hold the opinion that vulnerabilities in kernel user namespace
   code could have greater impact than vulnerabilities confined to a
   single piece of setuid software, and are therefore reluctant to
   enable unprivileged user namespace creation.

-  Limitations on container execution by location, valid signatures, user/group
   cannot be enforced.

Because of the points above, the default mode of operation of
{Singularity} uses a setuid binary. Sylabs aims to reduce the
circumstances that require this as new functionality is developed and
reaches commonly deployed Linux distributions.

******************************
Runtime & User Privilege Model
******************************

While other runtimes have aimed to tackle security concerns by
sandboxing containers executing as the ``root`` user so that they cannot
affect the host system, {Singularity} has adopted a different security
model:

-  Containers should be run as an unprivileged user.

-  The user should never be able to elevate their privileges inside the
   container to gain control over the host.

-  All permission restrictions on the user outside of a container should
   apply inside the container, as well.

-  Favor integration over isolation: a user is allowed to easily use
   host resources such as GPUs, network filesystems, and high speed
   interconnects. The process ID space, network, etc., are not isolated
   in separate namespaces by default.

To accomplish this, {Singularity} uses a number of Linux kernel
features. The container file system is mounted using the ``nosuid``
option, and processes are started with the ``PR_NO_NEW_PRIVS`` flag set.
This means that even if you run ``sudo`` inside your container, you
won't be able to change to another user, or gain root privileges by
other means.

If you do require the additional isolation of the network, devices,
PIDs, etc., which other runtimes provide, {Singularity} can make use of
additional namespaces and functionality such as seccomp and cgroups.

******************************
Singularity Image Format (SIF)
******************************

{Singularity} uses SIF as its default container format. A SIF container
is a single file, which makes it easy to manage and distribute. Inside
the SIF file, the container filesystem is held in a SquashFS object. By
default, we mount the container filesystem directly using SquashFS. On a
network filesystem, this means that reads from the container are
data-only. Metadata operations happen locally, speeding up workloads
that involve many small files.

Holding the container image in a single file also enables unique
security features. The container filesystem is immutable, and can be
signed. The signature travels as part of the SIF image itself so that it
is always possible to verify that the image has not been tampered with
or corrupted.

We use private PGP keys to create a container signature, and the corresponding
public keys to verify the container. Verification of signed containers happens
automatically in ``singularity pull`` commands against the Singularity Container
Services (SCS) Library. The SCS keystore makes it easier to share and obtain
public keys for container verification.

A container may be signed once, by a trusted individual who approves its use. It
could also be signed with multiple keys to signify it has passed each step in a
CI/CD QA & Security process. In setuid mode, {Singularity} can be configured
with an execution control list (ECL). The ECL requires the presence of one or
more valid signatures, to limit execution to approved containers on systems that
have unprivileged user namespace creation disabled.

In {Singularity} 3.4 and above, the root filesystem of a container
(stored in the SquashFS partition of SIF) can be encrypted. As a result,
everything inside the container becomes inaccessible without the correct
key or passphrase. The content of the container then remains private,
even if the SIF file is shared in public.

Encryption and decryption are performed using the Linux kernel's LUKS2
feature. This is the same technology routinely used for full disk
encryption. The encrypted container is mounted directly through the
kernel. Unlike other container formats, the encrypted container is run
without ever decrypting its contents to disk.

*******************************
Configuration & Runtime Options
*******************************

System administrators who manage {Singularity} can use configuration
files to set security restrictions, grant or revoke a user's
capabilities, manage resources, authorize containers, etc.

For example, the `ecl.toml
<https://sylabs.io/guides/{adminversion}/admin-guide/configfiles.html#ecl-toml>`_
configuration file allows blacklisting and whitelisting of containers.

Documentation for administrators about configuration files and their
parameters is available `here
<https://sylabs.io/guides/{adminversion}/admin-guide/configfiles.html>`__.

When running a container as root, {Singularity} can apply hardening rules
using cgroups, seccomp, and apparmor. See :ref:`here <security-options>`
for details on these options.
