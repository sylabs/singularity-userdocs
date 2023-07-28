.. _registry:

####################
OCI Image Registries
####################

It is common for users of {Singularity} to use `OCI
<https://opencontainers.org/>`__ registries as sources for their container
images. Some registries require credentials to access certain images or even the
registry itself. Previously, the only method in {Singularity} to supply
credentials to registries was to supply credentials for each command or set
environment variables to contain the credentials for a single registry. See
:ref:`Authentication via Interactive Login
<sec:authentication_via_docker_login>` and :ref:`Authentication via Environment
Variables <sec:authentication_via_environment_variables>`.

Starting with {Singularity} 4.0, users can supply credentials
on a per-registry basis with the ``registry`` command.

.. note::

   In versions of {Singularity} starting from 3.7 but before 4.0, the
   functionality described here was grouped together with :ref:`remote endpoint
   management<endpoint>` under the ``remote`` command group. Beginning with
   version 4.0, this functionality has been given its own top-level command
   group, ``registry``.

Users can login to an OCI registry with the ``registry login`` command by
specifying a ``docker://`` prefix to the registry hostname:

.. code:: console

   $ singularity registry login --username myuser docker://docker.com
   Password / Token:
   INFO:    Token stored in /home/myuser/.singularity/remote.yaml

   $ singularity registry list

   URI                  SECURE?
   docker://docker.com  ✓

{Singularity} will automatically supply the configured credentials when
interacting with DockerHub. The checkmark in the ``SECURE?`` column indicates
that {Singularity} will use TLS when communicating with the registry.

A user can be logged-in to multiple OCI registries at the same time:

.. code:: console

   $ singularity registry login --username myuser docker://registry.example.com
   Password / Token:
   INFO:    Token stored in /home/myuser/.singularity/remote.yaml

   $ singularity registry list

   URI                            SECURE?
   docker://docker.com            ✓
   docker://registry.example.com  ✓

{Singularity} will supply the correct credentials for the registry based on the
hostname used, whenever one of the following commands is used with a
``docker://`` or ``oras://`` URI:

`pull
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_pull.html>`__,
`push
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_push.html>`__,
`build
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_build.html>`__,
`exec
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_exec.html>`__,
`shell
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_shell.html>`__,
`run
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_run.html>`__,
`instance
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_instance.html>`__

.. note::

   It is important for users to be aware that the ``registry login`` command
   will store the supplied credentials or tokens unencrypted in your home
   directory.

