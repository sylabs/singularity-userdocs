.. _whats_new:

###############################
What's New in {Singularity} 4.0
###############################

This section highlights important changes in {Singularity} 4.0 that are of note
to users. See also the "What's New" section in the Admin Guide for
administrator-facing changes.

********
OCI-mode
********

Singularity 4 introduces :ref:`OCI-mode <oci_mode>` as a fully supported
feature. It is enabled by using the ``--oci`` flag with the run / shell / exec /
pull commands, or when ``oci mode = yes`` is set in ``singularity.conf``.

In OCI-mode:

- Container images from OCI sources will be ``pull``-ed to an :ref:`OCI-SIF
  <oci_sif>` file. An OCI-SIF file encapsulates the OCI image configuration and
  squashed filesystem using an OCI, rather than Singularity specific, structure.
- The run / shell / exec commands use a low-level OCI runtime (crun/runc) for
  container execution.
- Default operation is :ref:`compatible with other OCI tools <oci_compat>`,
  similar to ``--compat`` in Singularity's non-OCI native mode.
- OCI-mode supports running existing Singularity SIF images, that are not
  OCI-SIF, and can be made to :ref:`imitate native mode default
  behavior <oci_compat>` by using the ``--no-compat`` flag.

***********
CLI Changes
***********

- The commands related to OCI/Docker registries that were under ``singularity
  remote`` have been moved to their own, dedicated :ref:`registry command
  <registry>`.
- The keyserver-related commands that were under ``singularity remote`` have
  been moved to their own, dedicated :ref:`keyserver command <key_commands>`.
- Adding a new remote endpoint using the ``singularity remote add`` command will
  now set the new endpoint as default. This behavior can be suppressed by
  supplying the ``--no-default`` (or ``-n``) flag to ``remote add``.
- ``--cwd`` is now the preferred form of the flag for setting the container's
  working directory, though ``--pwd`` is still supported for compatibility.

************************
Runtime Behavior Changes
************************

- The way ``--home`` is handled when running as root (e.g. ``sudo singularity``) or with
  ``--fakeroot`` has changed. Previously, we were only modifying the ``HOME``
  environment variable in these cases, while leaving the container's ``/etc/passwd``
  file unchanged (with its homedir field pointing to ``/root``, regardless of the
  value passed to ``--home)``. Now, both the value of HOME and the
  contents of ``/etc/passwd`` in the container will reflect the value passed to
  ``--home``.
- Bind mounts are now performed in the order of their occurrence on the command
  line, or within the value of the ``SINGULARITY_BIND`` environment variable.
  (Previously, image-mounts were always performed first, regardless of order.)
- The current working directory is created in the container when it doesn't
  exist, so that it can be entered. You must now specify ``--no-mount home,cwd``
  instead of just ``--no-mount home`` to avoid mounting from ``$HOME`` if you
  run ``singularity`` from inside ``$HOME``.
- If the path of the current working directory in the container and on the host
  contain symlinks to different locations, the current working directory will
  not be mounted.

****************************
New Features & Functionality
****************************

- Templating support for definition files: users can now :ref:`define variables
  in definition files <sec:templating>` via a matching pair of double curly
  brackets.
- Added a ``--secret`` flag (shorthand: ``-s``) to the ``key remove``
  subcommand, to allow removal of a private key by fingerprint.
- Added ``--private`` as a synonym for ``--secret`` in ``key list``, ``key
  export``, and ``key remove`` subcommands.
- The ``instance start`` command now accepts an optional ``--app <name>``
  argument which invokes the start script within the ``%appstart <name>``
  section in the definition file. The ``instance stop`` command still only
  requires the instance name.
- A new ``--no-pid`` flag for ``singularity run/shell/exec`` disables the PID
  namespace inferred by ``--containall`` and ``--compat``.
- :ref:`Caching of OCI images <sec:cache>` is now architecture aware. This fixes
  behavior in cases where a user's home directory is shared between systems of
  different architectures. If you do not use older versions of {Singularity} on
  a system, you can remove obsolete cache entries with ``singularity cache clean
  --type blob``.
- A new ``--platform`` flag can be used to specify an
  ``OS/Architecture[/Variant]`` when :ref:`pulling images from OCI
  <oci_platform>` or :ref:`library <library_platform_arch>` sources. When
  pulling from library sources the optional variant is ignored.
- The ``--arch`` flag can now be used to specify a required architecture when
  :ref:`pulling images from OCI <oci_arch>`, as well as :ref:`library
  <library_platform_arch>` sources.
