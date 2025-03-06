.. _whats_new:

###############################
What's New in {Singularity} 4.3
###############################

This section highlights important changes and new features in {Singularity} 4.3
that are of note to users. See also the "What's New" section in the Admin Guide
for administrator-facing changes.

========
OCI-Mode
========

- Images in OCI-SIF files can now be signed with a :ref:`cosign-compatible
  signature <sec:cosign>`. These signatures can be pushed/pulled to/from OCI
  registries.
- Containers run in OCI-Mode now start in a cgroup, :ref:`cgroup namespace
  <sec:cgroup_namespace>`, and mount the cgroup filesystem wherever possible.


=======
Runtime
=======

- :ref:`Nesting Singularity-in-Docker and Singularity-in-Singularity <nested>`
  is now explicitly supported and tested in native mode and OCI-Mode.
- Subuid and subgid mappings used for :ref:`fakeroot <fakeroot>` and OCI-Mode
  are now obtained with libsubid on supported systems.

=====
Build
=====

- A ``dnf`` bootstrap is now available, as an alias of ``yum``.
