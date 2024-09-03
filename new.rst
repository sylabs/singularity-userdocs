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

*******
Runtime
*******

- The new ``--netns-path`` flag takes a path to a network namespace to join when
  starting a container. The root user may join any network namespace. An
  unprivileged user can only join a network namespace specified in the new
  allowed ``netns paths directive`` in ``singularity.conf``, if they are also
  listed in ``allow net users`` / ``allow net groups``. Not currently supported
  with ``--fakeroot``, or in ``--oci`` mode. See :ref:`sec:netns-path`.
