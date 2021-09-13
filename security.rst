.. _security:

*************************
Security in {Singularity}
*************************

Containers are popular for many good reasons. They are light weight,
easy to spin-up and require reduced IT management resources as
compared to hardware VM environments. More importantly, container
technology facilitates advanced research computing by granting the
ability to package software in highly portable and reproducible
environments encapsulating all dependencies, including the operating
system. But there are still some challenges to container security.

{Singularity} addresses some core missions of containers : Mobility of
Compute, Reproducibility, HPC support, and **Security**. This section
gives an overview of security features supported by {Singularity},
especially where they differ from other container runtimes.

Security Policy
###############

Security is not a check box that one can tick and forget.  Ensuring
security is a ongoing process that begins with software architecture,
and continues all the way through to ongoing security practices.  In
addition to ensuring that containers are run without elevated
privileges where appropriate, and that containers are produced by
trusted sources, users must monitor their containers for newly
discovered vulnerabilities and update when necessary just as they
would with any other software. Sylabs is constantly probing to find
and patch vulnerabilities within {Singularity}, and will continue to do
so.

If you suspect you have found a vulnerability in {Singularity}, please
follow the steps in our published `Security Policy
<https://sylabs.io/security-policy>`__.

so that it can be disclosed, investigated, and fixed in an appropriate
manner.

SingularityPRO - Long Term Support & Security Patches
#####################################################

Security patches for {Singularity} are applied to the latest open-source
version, so it is important to follow new releases and upgrade when
necessary.

SingularityPRO is a professionally curated and licensed version of
{Singularity} that provides added security, stability, and support
beyond that offered by the open source project. Security and bug-fix
patches are backported to select versions of SingularityPRO, so that
they can be deployed long-term where required. PRO users receive
security fixes (without specific notification or detail) prior to
public disclosure, as detailed in the `Sylabs Security Policy
<https://sylabs.io/security-policy>`__.


{Singularity} Runtime & User Privilege
######################################

The {Singularity} Runtime enforces a unique security model that makes it
appropriate for *untrusted users* to run *untrusted containers* safely
on multi-tenant resources. When you run a container, the processes in
the container will run as your user account. {Singularity} dynamically
writes UID and GID information to the appropriate files within the
container, and the user remains the same *inside* and *outside*
the container, i.e., if you're an unprivileged user while entering the
container you'll remain an unprivileged user inside the container.

Additional blocks are in place to prevent users from escalating
privileges once they are inside of a container. The container file
system is mounted using the ``nosuid`` option, and processes are
started with the ``PR_NO_NEW_PRIVS`` flag set. This means that even if
you run `sudo` inside your container, you won't be able to change to
another user, or gain root privileges by other means. This approach
provides a secure way for users to run containers and greatly
simplifies things like reading and writing data to the host system
with appropriate ownership.

It is also important to note that the philosophy of {Singularity} is
*Integration* over *Isolation*. Most container run times strive to
isolate your container from the host system and other containers as
much as possible. {Singularity}, on the other hand, assumes that the
user’s primary goals are portability, reproducibility, and ease of use
and that isolation is often a tertiary concern. Therefore, {Singularity}
only isolates the mount namespace by default, and will bind mount
several host directories such as ``$HOME`` and ``/tmp`` into the
container at runtime. If needed, additional levels of isolation can be
achieved by passing options causing {Singularity} to enter any or all of
the other kernel namespaces and to prevent automatic bind mounting.
These measures allow users to interact with the host system from
within the container in sensible ways.

Singularity Image Format (SIF)
##############################

Ensuring container security as a continuous process. {Singularity}
provides ways to ensure integrity throughout the lifecycle of a
container, i.e. at rest, in transit and while running. The SIF
Singularity Image Format has been designed to achieve these goals.

A SIF file is an immutable container image that packages the container
environment into a single file. SIF supports security and integrity
through the ability to cryptographically sign a container, creating a
signature block within the SIF file which can guarantee immutability
and provide accountability as to who signed it. {Singularity} follows
the `OpenPGP <https://www.openpgp.org/>`_ standard to create and
manage these signatures, and the keys used to create them. After
building an image with {Singularity}, a user can ``singularity sign``
the container and push it to the Library along with its public PGP key
(stored in :ref:`Keystore <keystore>`). The signature can be verified
(``singularity verify``) while pulling or downloading the
image. :ref:`This feature <signNverify>` makes it easy to to establish
trust in collaborations within and between teams.

In {Singularity} 3.4 and above, the root file system of a container
(stored in the squashFS partition of SIF) can be encrypted. As a
result, everything inside the container becomes inaccessible without
the correct key or passphrase. Other users on the system will be able
to look inside your container files. The content of the container is
private, even if the SIF file is shared in public.

Unlike other container platforms where execution requires a number of
layers to be extracted to a rootfs directory on the host, {Singularity}
executes containers in a single step, directly from the immutable
``.sif``. This reduces the attack surface and allows the container to
be easily verified at runtime, to ensure it has not been tampered with.


Admin Configurable Files
#########################

System administrators who manage {Singularity} can use configuration
files, to set security restrictions, grant or revoke a user’s
capabilities, manage resources and authorize containers etc.

For example, the `ecl.toml
<https://sylabs.io/guides/\{adminversion\}/admin-guide/configfiles.html#ecl-toml>`_
file allows blacklisting and whitelisting of containers.

Configuration files and their parameters are documented for administrators
documented `here
<https://sylabs.io/guides/\{adminversion\}/admin-guide/configfiles.html>`__.

cgroups support
****************

Starting with v3.0, {Singularity} added native support for ``cgroups``,
allowing users to limit the resources their containers consume without
the help of a separate program like a batch scheduling system. This
feature can help to prevent DoS attacks where one container seizes
control of all available system resources in order to stop other
containers from operating properly.  To use this feature, a user first
creates a cgroups configuration file. An example configuration file is
installed by default with {Singularity} as a guide. At runtime, the
``--apply-cgroups`` option is used to specify the location of the
configuration file to apply to the container and cgroups are
configured accordingly. More about cgroups support `here
<https://sylabs.io/guides/\{adminversion\}/admin-guide/configfiles.html#cgroups-toml>`__.

``--security`` options
***********************

{Singularity} supports a number of methods for further modifying the
security scope and context when running {Singularity} containers.  Flags
can be passed to the action commands; ``shell``, ``exec``, and ``run``
allowing fine grained control of security. Details about them are
documented :ref:`here <security-options>`.

Security in the Sylabs Cloud
############################

`Sylabs Cloud <https://cloud.sylabs.io/home>`_ consists of a Remote
Builder, a Container Library, and a Keystore. Together, these
services provide an end-to-end solution for packaging and distributing
applications in secure and trusted containers.

Remote Builder
**************

As mentioned earlier, the {Singularity} runtime prevents executing code
with root-level permissions on the host system. However, building a
container requires elevated privileges that most shared environments
do not grant their users. The `Build Service
<https://cloud.sylabs.io/builder>`_ aims to address this by allowing
unprivileged users to build containers remotely, with root level
permissions inside the secured service. System administrators can use
the system to monitor which users are building containers, and the
contents of those containers. The {Singularity} CLI has native
integration with the Build Service from version 3.0 onwards. In
addition, a browser interface to the Build Service also exists, which
allows users to build containers using only a web browser.

.. note::

    Please also see the :ref:`Fakeroot feature <fakeroot>` which is a
    secure option for admins in multi-tenant HPC environments and
    similar use cases where they might want to grant a user special
    privileges inside a container.

    Fakeroot has some limitations, and requires unpriveleged user
    namespace support in the host kernel.

Container Library
*****************

The `Container Library <https://cloud.sylabs.io/library>`_ allows
users to store and share {Singularity} container images in the
Singularity Image Format (SIF). A web front-end allows users to create
new projects within the Container Library, edit documentation
associated with container images, and discover container images
published by their peers.

.. _keystore:

Key Store
*********

The `Key Store <https://cloud.sylabs.io/keystore>`_ is a key
management system offered by Sylabs that uses an `OpenPGP
implementation <https://gnupg.org/>`_ to permit sharing and discovery
of PGP public keys used to sign and verify {Singularity} container
images. This service is based on the OpenPGP HTTP Keyserver Protocol
(HKP), with several enhancements:

- The Service requires connections to be secured with Transport Layer
  Security (TLS).
- The Service implements token-based authentication, allowing only
  authenticated users to add or modify PGP keys.
- A web front-end allows users to view and search for PGP keys using a
  web browser.


Authentication and encryption
******************************

1. Communication between users, the authentication service other
   services is secured via TLS encryption.

2. The services support authentication of users via signed and encrypted authentication
   tokens.

3. There is no implicit trust relationship between each service. Each
   request between the services is authenticated using the
   authentication token supplied by the user in the associated
   request.
