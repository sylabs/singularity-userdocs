.. _security:

*************************
Security in {Singularity}
*************************

Security Policy
###############

If you suspect you have found a vulnerability in {Singularity} we want
to work with you so that it can be investigated, fixed, and disclosed
in a responsible manner. Please follow the steps in our published
`Security Policy <https://sylabs.io/security-policy>`__, which begins
with contacting us privately via security@sylabs.io

Sylabs discloses vulnerabilities found in {Singularity} through public
CVE reports, and notifications on our community channels. We encourage
all users to monitor new releases of {Singularity} for security
information. Security patches are applied to the latest open-source
release.

SingularityPRO is a professionally curated and licensed version of
{Singularity} that provides added security, stability, and support
beyond that offered by the open source project. Security and bug-fix
patches are backported to select versions of SingularityPRO, so that
they can be deployed long-term where required. PRO users receive
security fixes as detailed in the `Sylabs Security Policy
<https://sylabs.io/security-policy>`__.

Background
##########

{Singularity} grew out of the need to implement a container platform
that was suitable for use on shared systems, such as HPC clusters. In
these environments multiple people access a shared resource. User
accounts, groups, and standard file permissions limit their access to
data, devices, and prevent them from disrupting or accessing others'
work.

To provide security in these environments a container needs to run as
the user who starts it on the system. Before the widepread adoption of
the Linux user namespace, only a privileged user could perform the
operations which are needed to run a container. A default Docker
installation uses a root-owned daemon to start containers. Users can
request that the daemon starts a container on their behalf. However,
co-ordinating a daemon with other schedulers is difficult and, since
the daemon is privileged, users can ask it to carry out actions that
they wouldn't normally have permission to do.

When a user runs a container with {Singularity}, it is started as a
normal process running under the user's account. Standard file
permissions and other security controls based on user accounts,
groups, and processes apply. In a default installation {Singularity}
uses a setuid starter binary to perform only the specific tasks needed
to setup the container.


Setuid & User Namespaces
########################

Using a setuid binary to run container setup operations is essential
to support containers on older Linux distributions, such as CentOS 6,
that were previously common in HPC and enterprise. Newer distributions
have support for 'unprivileged user namespace creation'. This means a
normal user can create a user namespace, in which most setup operations
needed to run a container can be run, unprivileged.

{Singularity} supports running containers without setuid, using user
namespaces. It can be compiled with the ``--without-setuid`` option,
or ``allow setuid = no`` can be set in ``singularity.conf`` to enable
this. In this mode *all* operations run as the user who starts the
``singularity`` program. However, there are some disadvantages:

* SIF and other single file container images cannot be mounted
  directly. The container image must be extracted to a directory on
  disk to run. This impact the speed of execution. Workloads accessing
  large numbers of small files (such as python application startup) do
  not benefit from the reduced metadata load on the filesystem an
  image file provides.

* Replacing direct kernel mounts with a FUSE approach is likely to
  cause a significant reduction in perfomance.

* The effectiveness of signing and verifying container images is
  reduced as, when extracted to a directory, modification is possible
  and verification of the image's original signature cannot be
  performed.

* Encryption is not supported. {Singularity} leverages kernel LUKS2
  mounts to run encrypted containers without decrypting their content
  to disk.

* Some sites hold the opinion that vulnerabilities in kernel user
  namespace code could have greater impact than vulnerabilities
  confined to a single piece of setuid software. Therefore they are
  reluctant to enable unprivileged user namespace creation.

Because of the points above, the default mode of operation of
{Singularity} uses a setuid binary. Sylabs aims to reduce the
circumstances that require this as new functionality is developed and
reaches commonly deployed Linux distributions.

Runtime & User Privilege Model
##############################

While other runtimes have aimed to safely sandbox containers executing
as the ``root`` user, so that they cannot affect the host system,
{Singularity} has adopted an alternative security model:

* Containers should be run as an unprivileged user.

* The user should never be able to elevate their privileges inside the
  container to gain control over the host.

* All permission restrictions on the user outside of a container
  should apply inside the container.

* Favor integration over isolation. Allow a user to use host resources
  such as GPUs, network filesystems, high speed interconnects
  easily. The process ID space, network etc. are not isolated in
  separate namespaces by default.

To accomplish this, {Singularity} uses a number of Linux kernel
features. The container file system is mounted using the ``nosuid``
option, and processes are started with the ``PR_NO_NEW_PRIVS`` flag
set. This means that even if you run ``sudo`` inside your container,
you won't be able to change to another user, or gain root privileges
by other means.

If you do require the additional isolation of the network, devices,
PIDs etc. provided by other runtimes, {Singularity} can make use of
additional namespaces and functionality such as seccomp and cgroups.


Singularity Image Format (SIF)
##############################

{Singularity} uses SIF as its default container format. A SIF
container is a single file, which makes it easy to manage and
distribute. Inside the SIF file, the container filesystem is held in a
SquashFS object. By default, we mount the container filesystem
directly using SquashFS. On a network filesytem this means that reads
from the container are data-only. Metadata operations happen locally,
speeding up workloads with many small files.

Holding the container image in a single file also enable unique
security features. The container filesystem is immutable, and can be
signed. The signature travels in the SIF image itself so that it is
always possible to verify that the image has not been tampered with or
corrupted.

We use private PGP keys to create a container signature, and the
public key in order to verify the container. Verification of signed
containers happens automatically in ``singularity pull`` commands
against the Sylabs Cloud Container Library. A Keystore in the Sylabs
Cloud makes it easier to share and obtain public keys for container
verification.

A container may be signed once, by a trusted individual who approves
its use. It could also be signed with multiple keys to signify it has
passed each step in a CI/CD QA & Security process. {Singularity} can
be configured with an execution control list (ECL), which requires the
presence of one or more valid signatures, to limit execution to
approved containers.

In {Singularity} 3.4 and above, the root filesystem of a container
(stored in the squashFS partition of SIF) can be encrypted. As a
result, everything inside the container becomes inaccessible without
the correct key or passphrase. The content of the container is
private, even if the SIF file is shared in public.

Encryption and decryption are performed using the Linux kernel's LUKS2
feature. This is the same technology routinely used for full disk
encryption. The encrypted container is mounted directly through the
kernel. Unlike other container formats, an encrypted container is not
decrypted to disk in order to run it.


Configuration & Runtime Options
###############################

System administrators who manage {Singularity} can use configuration
files to set security restrictions, grant or revoke a user’s
capabilities, manage resources and authorize containers etc.

For example, the `ecl.toml
<https://sylabs.io/guides/\{adminversion\}/admin-guide/configfiles.html#ecl-toml>`_
file allows blacklisting and whitelisting of containers.

Configuration files and their parameters are documented for
administrators documented `here
<https://sylabs.io/guides/\{adminversion\}/admin-guide/configfiles.html>`__.

When running a container as root, Singularity can apply hardening
rules using cgroups, seccomp, apparmor. See :ref:`details of these
options here <security-options>`.
