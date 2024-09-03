.. _whats_new:

###############################
What's New in {Singularity} 4.2
###############################

This section highlights important changes and new features in {Singularity} 4.2
that are of note to users. See also the "What's New" section in the Admin Guide
for administrator-facing changes.

If you are upgrading from a 3.x version of {Singularity} we recommend also
reviewing the `"What's New" section for 4.0
<https://docs.sylabs.io/guides/4.0/user-guide/new.html>`__.

********
OCI-mode
********

- A new ``--layer-format tar`` flag for ``singularity push`` allows layers in an
  OCI-SIF image to be pushed to ``library://`` and ``docker://`` registries with
  layers in the standard OCI tar format. Images pushed with ``--layer-format``
  tar can be pulled and run by other OCI runtimes. See :ref:`sec:layer-format`.
- Persistent overlays embedded in OCI-SIF files. See :ref:`overlay-oci-sif`.

  - A writable overlay can be added to an OCI-SIF file with the ``singularity
    overlay create`` command. The overlay will be applied read-only, by default,
    when executing the OCI-SIF. To write changes to the container into the
    overlay, use the ``--writable`` flag. 
  - A writable overlay is added to an OCI-SIF file as an ext3 format layer,
    appended to the encapsulated OCI image. After the overlay has been modified,
    use the ``singularity overlay sync`` command to synchronize the OCI digests with
    the overlay content.
  - A new ``singularity overlay seal`` command converts a writable overlay inside
    an OCI-SIF image into a read-only squashfs layer. This seals changes made to
    the image via the overlay, so that they are permanent.

*******
Runtime
*******

- The new ``--netns-path`` flag takes a path to a network namespace to join when
  starting a container. The root user may join any network namespace. An
  unprivileged user can only join a network namespace specified in the new
  allowed ``netns paths directive`` in ``singularity.conf``, if they are also
  listed in ``allow net users`` / ``allow net groups``. Not currently supported
  with ``--fakeroot``, or in ``--oci`` mode. See :ref:`sec:netns-path`.
- Instances can now be started via the new subcommand ``singularity instance
  run``, which will cause the instance to execute its ``%runscript`` rather than
  the ``%startscript``.

