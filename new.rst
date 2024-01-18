.. _whats_new:

###############################
What's New in {Singularity} 4.1
###############################

This section highlights important changes and new features in {Singularity} 4.1
that are of note to users. See also the "What's New" section in the Admin Guide
for administrator-facing changes.

If you are upgrading from a 3.x version of {Singularity} we recommend also
reviewing the `"What's New" section for 4.0
<https://docs.sylabs.io/guides/4.0/user-guide/new.html>`__.

********
OCI-mode
********

- Singularity will now :ref:`build OCI-SIF images from Dockerfiles
  <dockerfile>`, if the ``--oci`` flag is used with the ``build`` command.
  Provide a Dockerfile as the final argument to ``build``, instead of a
  Singularity definition (.def) file. Supports ``--build-arg`` /
  ``--build-arg-file`` options, ``--arch`` for cross-architecture builds,
  `--authfile` and other authentication options, and more. Dockerfile builds are
  not available on EL7 / SLES12 distributions.
- `Docker-style SCIF containers <https://sci-f.github.io/tutorial-preview-install>`__
  are now supported. If the entrypoint of an OCI container is the ``scif``
  executable, then the ``run`` / ``exec`` / ``shell`` commands in ``--oci`` mode
  can be given the ``--app <appname>`` flag, and will automatically invoke the
  relevant SCIF command.
- `Multi layer OCI-SIF images <sec:multi_layer_oci_sif>` can now be created
  using a new ``--keep-layers`` flag, for the ``pull`` and ``run/shell/exec``
  commands. This allows individual layers to be preserved when an OCI-SIF image
  is created from an OCI source. Multi layer OCI-SIF images can be run with
  SingularityCE 4.1 and later.

***********
CLI Changes
***********

- The ``registry login`` and ``registry logout`` commands now support an
  ``--authfile <path>`` flag, which causes the OCI credentials to be written to
  / removed from a custom file located at ``<path>`` instead of the default
  location (``$HOME/.singularity/docker-config.json``). The commands ``pull``,
  ``push``, ``run``, ``exec``, ``shell``, and ``instance start`` can now also be
  passed a ``--authfile <path>`` option, to read OCI registry credentials from
  this custom file.
- A new `--tmp-sandbox` flag has been added to the `run / shell / exec /
  instance start` commands. This will force Singularity to extract a container
  to a temporary sandbox before running it, when it would otherwise perform a
  kernel or FUSE mount.

************************
Runtime Behavior Changes
************************

- In native mode, SIF/SquashFS container images will now be mounted with
  squashfuse when kernel mounts are disabled in ``singularity.conf``, or cannot
  be used (non-setuid / user namespace workflow). If the FUSE mount fails,
  Singularity will fall back to extracting the container to a temporary sandbox
  in order to run it.
- In native mode, bare extfs container images will now be mounted with
  ``fuse2fs`` when kernel mounts are disabled in ``singularity.conf``, or cannot
  be used (non-setuid / user namespace workflow).

************
Deprecations
************

- The experimental ``--sif-fuse`` flag, and ``sif fuse`` directive in
  ``singularity.conf`` are deprecated. The flag and directive were used to
  enable experimental mounting of SIF/SquashFS container images with FUSE in
  prior versions of Singularity. From 4.1, FUSE mounts are used automatically
  when kernel mounts are disabled / not available.
