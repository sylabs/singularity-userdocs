.. _nested:

#################
Nested Containers
#################

{Singularity} was designed for HPC environments, allowing applications run
inside containers to easily access high speed networks, GPUs, parallel file
systems etc. Running {Singularity} nested inside another container negates some
of its benefits, but can be necessary e.g. in CI / CD environments that only
allow execution of jobs within containers, and not on bare-metal or in a virtual
machine.

From version 4.3, basic nested container execution and container builds are
tested and supported. Regressions in nested container support are now considered
bugs that would e.g. block a new release.

**************************
Singularity-in-Singularity
**************************

To use {Singularity} inside a container that is itself run with {Singularity}
installed on a host system, ensure that both the container and host versions of
{Singularity} are 4.3 or above.

Building a Singularity-in-Singularity container
===============================================

An example definition file that will build a SIF containing the latest release
of {Singularity} from GitHub can be found in the ``examples/nested`` directory.
To build it use either the ``sudo`` or ``--fakeroot`` approach. Building as an
unprivileged user without ``--fakeroot`` is not supported for this definition
file.

.. code:: console

   # As root via sudo
   $ sudo singularity build nested.sif singularity/examples/nested/Singularity

   # As a user with --fakeroot (sub[ug]id configuration required)
   $ singularity build --fakeroot nested.sif singularity/examples/nested/Singularity

For maximum compatibility with alternative nested workflows, the setuid flow is
disabled for the {Singularity} installation in this container. See the `Admin
Guide <https://docs.sylabs.io/guides/{adminversion}/admin-guide/>`__ for details
of the limitations of unprivileged {Singularity}.

You can use the example definition file as a template when constructing your own
nested container environment.

Running containers nested
=========================

The ``nested.sif`` built above calls ``singularity`` inside the container,
passing any arguments provided. For example, to run ``singularity --version``
nested:

.. code:: console

   $ singularity run nested.sif --version
   singularity-ce version 4.3.0-noble

You can now execute a container, nested:

.. code:: 

   $ singularity run nested.sif run library://lolcow
   ...
   ______________________________
   < Wed Feb 26 12:09:43 GMT 2025 >
   ------------------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||

The outer ``singularity run`` calls the ``%runscript`` of the ``nested.sif``
container. This then calls ``singularity`` inside the container with the
arguments ``run library://lolcow``.

Depending on the configuration of your host system, you may see warnings that
certain mounts are not possible. {Singularity} will automatically fall back to a
compatible approach.


To work as root inside the nested container, start the outer ``singularity``
command on the host as ``root``, or with ``--fakeroot``:

.. code:: console

   $ sudo singularity run nested.sif run library://alpine id
   INFO:    Using cached image
   uid=0(root) gid=0(root) groups=0(root)

   $ singularity run --fakeroot nested.sif run library://alpine id
   INFO:    Using cached image
   uid=0 gid=0(root) groups=0(root)

Attempting to use ``--fakeroot`` on the inner ``run library://alpine``
singularity command will fail.

Building containers nested
==========================

To build a container using nested singularity, you must start the outer
``singularity`` command on the host as ``root``, or with ``--fakeroot``. The
following commands will build from a definition file, creating ``test.sif``:

.. code:: console

   $ sudo singularity run nested.sif build test.sif singularity/examples/library/Singularity
   INFO:    Starting build...
   ...
   INFO:    Build complete: test.sif


   $ singularity run --fakeroot nested.sif build test.sif singularity/examples/library/Singularity
   INFO:    Starting build...
   ...
   INFO:    Build complete: test.sif

Attempting to use ``--fakeroot`` on the inner ``build`` command will fail.

OCI-mode
========

Executing containers in OCI-mode using nested {Singularity} is supported when
both the host and inner command use the ``--oci`` flag. 

At present, the outer container must provide a ``root`` user, so you must start the
outer ``singularity`` command as ``root`` or with ``--fakeroot``.

You must also add the ``--keep-privs`` flag to the outer ``singularity``
command. In OCI-Mode, capabilities and other configuration required to run
nested containers are dropped unless ``--keep-privs`` is specified.

.. code:: console

   # As a non-root user on the host
   $ singularity run --oci --fakeroot --keep-privs nested.sif run --oci docker://alpine date
   Wed Feb 26 01:54:19 PM GMT 2025

   # As the root user on the host
   $ sudo singularity run --oci --keep-privs nested.sif run --oci docker://alpine date
   Wed Feb 26 01:54:19 PM GMT 2025

.. code::

When the inner OCI container declares a ``USER``, it will be run as this user
via subuid/subgid mapping: 

.. code:: console

   $ singularity run --oci --fakeroot --keep-privs nested.sif run --oci docker://sylabsio/docker-user
   uid=2000(testuser) gid=2000(testgroup)

Nested OCI-mode builds are not supported.

*********************
Singularity-in-Docker
*********************

Both native mode and OCI-mode containers can be executed when Singularity is
running inside of a Docker container. These instructions assume a standard
(rootful) Docker installation, where a standard user has permission to run
containers via the Docker daemon, with the ``--privileged`` flag.

Building a Singularity-in-Docker container
==========================================

An example Dockerfile that will build a SIF containing the latest release of
{Singularity} from GitHub can be found in the ``examples/nested`` directory. To
build it with Docker:

.. code:: console

   $ cd singularity/examples/nested
   $ docker build -t nested-singularity:latest .

For maximum compatibility with alternative nested workflows, the setuid flow is
disabled for the {Singularity} installation in this container. See the `Admin
Guide <https://docs.sylabs.io/guides/{adminversion}/admin-guide/>`__ for details
of the limitations of unprivileged {Singularity}.

You can use the example Dockerfile as a template when constructing your own
nested container environment.

Running containers nested
=========================

The ``nested-singularity:latest`` image above calls ``singularity`` inside the
container, with any arguments provided, or the ``version`` command if no
arguments are provided:

.. code:: console

   $ docker run -it --rm nested-singularity:latest
   4.3.0-noble

You can now execute a container, nested. Note that you must add the
``--privileged`` flag so that the nested {Singularity} can create namespaces and
perform other system calls that are required to create a container.

.. note::

   The ``--privileged`` flag allows a container to affect the host system.
   Please consult the Docker documentation to understand the security
   implications of this flag.


.. code:: console

   $ docker run -it --rm --privileged nested-singularity:latest run library://lolcow
   ...
   ______________________________
   < Wed Feb 26 14:24:21 UTC 2025 >
   ------------------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||

The outer ``docker run`` invokes the ``ENRTYPOINT`` of the
``nested-singularity:latest`` container. This starts ``singularity`` inside the
container with the arguments ``run library://lolcow``.

Depending on the configuration of your host system, you may see warnings that
certain mounts are not possible. {Singularity} will automatically fall back to a
compatible approach.

Building containers nested
==========================

To build a container using {Singularity} nested inside Docker you will need to
explicitly make the definition file available inside the Docker container. To
retrieve the SIF file created, you must ensure it is also writtend to a location
mounted from the host. Unlike nested singularity-in-singularity, where mounts of
the current directory and user home directory propagate, the Docker container
filesystem is isolated from the host by default.

For example, to build the defintition file at ``examples/library`` and place the
resulting SIF at ``examples/output.sif`` on the host:

.. code:: console
   
   $ docker run -it --rm --privileged \
      -v $(pwd)/examples/library:/my-build \
      nested-singularity:latest \
      build /my-build/output.sif /my-build/Singularity
   INFO:    Starting build...
   ...
   INFO:    Build complete: /my-build/output.sif

   $ ls examples/library
   output.sif  Singularity

OCI-mode
========

To use OCI-Mode with singularity-in-docker, follow the same approach as with
native mode, but add the ``--oci`` flag to the inner singularity command:

.. code::

   $ docker run -it --rm --privileged nested-singularity:latest run --oci docker://sylabsio/lolcow
   ...
   ______________________________
   < Wed Feb 26 14:24:21 UTC 2025 >
   ------------------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||

Nested OCI-mode builds using singularity-in-docker are not supported. You should
use docker to build an OCI container, and ``singularity pull --oci`` to convert it to
OCI-SIF.

*********************
Singularity-in-Podman
*********************

Both native mode and OCI-mode containers can be executed when Singularity is
running inside of a Podman container. Podman can be used in rootful, or rootless
mode. These instructions assume it is being run in rootless mode by a non-root
user. The same instructions apply in rootful mode, but the security context of
the container(s) will differ.

Building a Singularity-in-Podman container
==========================================

An example Dockerfile that will build a SIF containing the latest release of
{Singularity} from GitHub can be found in the ``examples/nested`` directory. To
build it with Podman:

.. code:: console

   $ cd singularity/examples/nested
   $ podman build -t localhost/nested-singularity:latest .

For compatibility with rootless podman, the setuid flow is disabled for the
{Singularity} installation in this container. See the `Admin Guide
<https://docs.sylabs.io/guides/{adminversion}/admin-guide/>`__ for details of
the limitations of unprivileged {Singularity}.

You can use the example Dockerfile as a template when constructing your own
nested container environment.

Running containers nested
=========================

The ``nested-singularity:latest`` image above calls ``singularity`` inside the
container, with any arguments provided, or the ``version`` command if no
arguments are provided:

.. code:: console

   $ podman run -it --rm nested-singularity:latest
   4.3.0-noble

You can now execute a container, nested. Note that you must add the
``--privileged`` flag so that the nested {Singularity} can create namespaces and
perform other system calls that are required to create a container.

.. note::

   In podman's rootless mode, the ``--privileged`` flag does not give the
   container access to the host as root. If you use podman in rootful mode,
   consult the documentation carefully to understand the security implications.

.. code:: console

   $ podman run -it --rm --privileged nested-singularity:latest run library://lolcow
   INFO:    Downloading library image
   ...
   ______________________________
   < Wed Feb 26 14:48:04 UTC 2025 >
   ------------------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||


The outer ``podman run`` invokes the ``ENTRYPOINT`` of the
``nested-singularity:latest`` container. This starts ``singularity`` inside the
container with the arguments ``run library://lolcow``.

Depending on the configuration of your host system, you may see warnings that
certain mounts are not possible. {Singularity} will automatically fall back to a
compatible approach.

Building containers nested
==========================

To build a container using {Singularity} nested inside Podman you will need to
explicitly make the definition file available inside the Podman container. To
retrieve the SIF file created, you must ensure it is also writtend to a location
mounted from the host. Unlike nested singularity-in-singularity, where mounts of
the current directory and user home directory propagate, the Podman container
filesystem is isolated from the host by default.

For example, to build the defintition file at ``examples/library`` and place the
resulting SIF at ``examples/output.sif`` on the host:

.. code:: console
   
   $ podman run -it --rm --privileged \
      -v $(pwd)/examples/library:/my-build \
      nested-singularity:latest \
      build /my-build/output.sif /my-build/Singularity
   INFO:    Starting build...
   ...
   INFO:    Build complete: /my-build/output.sif

   $ ls examples/library
   output.sif  Singularity

OCI-mode
========

To use OCI-Mode with singularity-in-podman, follow the same approach as with
native mode, but add the ``--oci`` flag to the inner singularity command:

.. code::

   $ podman run -it --rm --privileged nested-singularity:latest run --oci docker://sylabsio/lolcow
   ...
   ______________________________
   < Wed Feb 26 14:24:21 UTC 2025 >
   ------------------------------
         \   ^__^
            \  (oo)\_______
               (__)\       )\/\
                  ||----w |
                  ||     ||

Nested OCI-mode builds using singularity-in-podman are not supported. You should
use podman to build an OCI container, and ``singularity pull --oci`` to convert it to
OCI-SIF.

