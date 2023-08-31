.. _build-environment:

#################
Build Environment
#################

.. _sec:buildenv:

********
Overview
********

You may wish to customize your build environment by doing things such as
specifying a custom cache directory for images, or sending your Docker
Credentials to the registry endpoint. In this section, we will discuss these and
other topics related to the build environment.

.. _sec:cache:

*************
Cache Folders
*************

{Singularity} will cache SIF container images generated from remote
sources, and any OCI/docker layers used to create them. The cache is
created at ``$HOME/.singularity/cache`` by default. The location of the
cache can be changed by setting the ``SINGULARITY_CACHEDIR`` environment
variable.

When you run builds as root using ``sudo``, images will be cached in root's home
directory at ``/root``, rather than your user's home directory. If you have set
the ``SINGULARITY_CACHEDIR`` environment variable, you may use ``sudo``'s ``-E``
option to pass the value of ``SINGULARITY_CACHEDIR`` through to the root user's
environment. This allows you to control where images will be cached even when
running builds under ``sudo``.

.. code::

   $ export SINGULARITY_CACHEDIR=/tmp/user/temporary-cache

   # Running a build under your user account
   $ singularity build --fakeroot myimage.sif mydef.def

   # Running a build with sudo, must use -E to pass env var
   $ sudo -E singularity build myimage.sif mydef.def

If you change the value of ``SINGULARITY_CACHEDIR`` be sure to choose a
location that is:

   -  Unique to you. Permissions are set on the cache so that private images
      cached for one user are not exposed to another. This means that
      {Singularity} cache directories cannot be shared across users.

   -  Located on a filesystem with sufficient space for the number and size of
      container images you anticipate using.

   -  Located on a filesystem that supports atomic rename, if possible.

.. warning::

   If you are not certain that your ``$HOME`` or ``SINGULARITY_CACHEDIR``
   filesystems support atomic rename, do not run {Singularity} in parallel using
   remote container URLs. Instead, use ``singularity pull`` to create a local
   SIF image, and then run this SIF image in a parallel step. Alternatively, you
   may use the ``--disable-cache`` option, but this will result in each
   {Singularity} instance independently fetching the container from the remote
   source, into a temporary location.

Inside the cache location you will find separate directories for the
different kinds of data that are cached:

.. code::

   $HOME/.singularity/cache/blob
   $HOME/.singularity/cache/library
   $HOME/.singularity/cache/net
   $HOME/.singularity/cache/oci-sif
   $HOME/.singularity/cache/oci-tmp
   $HOME/.singularity/cache/oras
   $HOME/.singularity/cache/shub

You can safely delete these directories, or content within them.
{Singularity} will re-create any directories and data that are needed in
future runs.

You should not add any additional files, or modify files in the cache, as this
may cause checksum / integrity errors when you run or build containers. If you
experience problems, use ``singularity cache clean`` to reset the cache to a
clean, empty state.

BoltDB Corruption Errors
========================

The library that {Singularity} uses to retrieve and cache Docker/OCI
layers keeps track of them using a single-file database. If your home
directory is on a network filesystem which experiences interruptions, or
you run out of storage, it is possible for this database to become
inconsistent.

If you observe error messages that mention `github.com/etcd-io/bbolt` when
trying to run {Singularity}, then you should remove the database file:

.. code::

   rm ~/.local/share/containers/cache/blob-info-cache-v1.boltdb

**************
Cache commands
**************

The ``cache`` command for {Singularity} allows you to view and clean up your
cache, without needing to manually inspect the cache directories.

.. note::

   If you have built images as root, directly or via ``sudo``, the default cache
   location for those builds is ``/root/.singularity``. You will need to use
   ``sudo`` when running ``cache clean`` or ``cache list`` to manage these cache
   entries.

Listing the Cache
=================

To view a summary of cache usage, use ``singularity cache list``:

.. code::

   $ singularity cache list
   There are 5 container file(s) using 74.80 MiB and 18 oci blob file(s) using 71.70 MiB of space
   Total space used: 146.50 MiB

To view more detailed information, use ``singularity cache list -v``:

.. code::

   $ singularity cache list -v
   NAME                     DATE CREATED           SIZE             TYPE
   07a18d51e256ea8c9e8de0   2023-08-14 16:09:04    1.75 KiB         blob
   278d875d73f02153bf7ed2   2023-08-14 16:09:03    0.15 KiB         blob
   332c15a4bec38b7947aec0   2023-08-14 16:09:03    0.13 KiB         blob
   553345aafebc934b169982   2023-08-14 12:14:24    0.95 KiB         blob
   7176c5ea9d28ae84d6accb   2023-08-14 16:09:03    0.20 KiB         blob
   7264a8db6415046d36d16b   2023-08-11 17:13:59    3.24 MiB         blob
   913cf3a39d377faf89ed38   2023-08-11 17:13:59    0.57 KiB         blob
   9fda8d8052c61740409c4b   2023-08-14 16:09:04    3.18 MiB         blob
   a1d08a2769560809bf03ba   2023-08-14 16:09:04    0.20 KiB         blob
   b3283fa64ecd626e391440   2023-08-14 12:14:39    0.99 KiB         blob
   b9e0aa7145707602cfc584   2023-08-14 16:09:03    0.12 KiB         blob
   c5c5fda71656f28e49ac9c   2023-08-11 17:13:53    1.60 KiB         blob
   cc82f5d421a1914e2ce2a8   2023-08-14 12:14:39    0.40 KiB         blob
   cf4e5bc0709f07284518b2   2023-08-11 17:13:59    0.40 KiB         blob
   deb9cd9f829fea30353f8c   2023-08-14 12:14:39    65.27 MiB        blob
   eb9556ecd24f1fa496f2f7   2023-08-14 16:09:03    0.15 KiB         blob
   f1dc9184bcff6fbdfd18dc   2023-08-14 16:09:04    0.15 KiB         blob
   fd4ed8f3240239c3dde6dc   2023-08-14 16:09:04    2.59 KiB         blob
   sha256.9a6ee1f8fdecb21   2023-08-31 09:54:44    2.65 MiB         library
   sha256:07a18d51e256ea8   2023-08-14 16:09:05    3.11 MiB         oci-tmp
   sha256:c5c5fda71656f28   2023-08-16 14:00:27    3.19 MiB         oci-tmp
   sha256:553345aafebc934   2023-08-14 12:14:55    62.68 MiB        oci-sif
   sha256:c5c5fda71656f28   2023-08-15 09:02:11    3.18 MiB         oci-sif

   There are 5 container file(s) using 74.80 MiB and 18 oci blob file(s) using 71.70 MiB of space
   Total space used: 146.50 MiB

All cache entries are named using a content hash, so that identical
layers or images that are pulled from different URIs do not result in
duplication within the cache.

You can limit the cache list to a specific cache type with the ``--type`` /
``-t`` option. The cache types are:

- **blob**: Configuration and filesystem layers for OCI containers that have
  been retrieved from a registry or other source.
- **library**: SIF images retrieved from a ``library://`` source.
- **net**: SIF, squashfs, and extfs images retrieved from ``http/https`` URIs.
- **oci-sif**: OCI-SIF images created from OCI blobs. These are cached to avoid
  multiple conversions when a container is run repeatedly from an OCI URI
  (``singularity run --oci docker://alpine``).
- **oci-tmp**: SIF images created from OCI blobs. These are cached to avoid
  multiple conversions when a container is run repeatedly from an OCI URI
  (``singularity run docker://alpine``).
- **oras**: SIF images retrieved from an OCI registry via the ``oras://``
  protocol.
- **shub**: SIF, squashfs, and extfs images retrieved from a ``shub://`` source.

Cleaning the Cache
==================

To reclaim space used by the {Singularity} cache, use ``singularity
cache clean``.

By default, ``singularity cache clean`` will remove all cache entries,
after asking you to confirm:

.. code::

   $ singularity cache clean
   This will delete everything in your cache (containers from all sources and OCI blobs).
   Hint: You can see exactly what would be deleted by canceling and using the --dry-run option.
   Do you want to continue? [N/y] n

Use the ``--dry-run`` / ``-n`` option to see the files that would be
deleted, or the ``--force`` / ``-f`` option to clean without asking for
confirmation.

If you want to leave your most recent cached images in place, but remove
images that were cached longer ago, you can use the ``--days`` / ``-d``
option. E.g. to clean cache entries older than 30 days:

.. code::

   $ singularity cache clean --days 30

To remove only a specific kind of cache entry, e.g. only library images,
use the ``type`` / ``-T`` option:

.. code::

   $ singularity cache clean --type library

.. _sec:temporaryfolders:

*****************
Temporary Folders
*****************

When building a container, or pulling/running a {Singularity} container from a
Docker/OCI source, a temporary working space is required. The container is
constructed in this temporary space before being packaged into a {Singularity}
SIF image. Temporary space is also used when running containers in unprivileged
mode, and when performing certain operations on filesystems that do not fully
support ``--fakeroot``.

The location for temporary directories defaults to ``/tmp``.
However, {Singularity} will respect the environment variable ``TMPDIR``, and
both of these locations can be overridden by setting the environment
variable ``SINGULARITY_TMPDIR``.

The temporary directory used during a build must be on a filesystem that has
enough space to hold the entire container image, uncompressed, including any
temporary files that are created and later removed in the course of the build.
You may therefore need to set ``SINGULARITY_TMPDIR`` when building a large
container on a system which has a small ``/tmp`` filesystem.

Remember to use ``-E`` option to pass the value of ``SINGULARITY_TMPDIR``
through to root's environment when executing the ``build`` command with
``sudo``.

.. warning::

   Many modern Linux distributions use an in-memory ``tmpfs`` filesystem
   for ``/tmp`` when installed on a computer with a sufficient amount of
   RAM. This may limit the size of container you can build, as temporary
   directories under ``/tmp`` share RAM with runniing programs etc. A
   ``tmpfs`` also uses default mount options that can interfere with
   some container builds.

   If you experience problems, set ``SINGULARITY_TMPDIR`` to a disk location, or
   disable the ``tmpfs`` ``/tmp`` mount on your system .

********************
Encrypted Containers
********************

Starting with {Singularity} 3.4.0, it is possible to build and run encrypted
containers. The containers are decrypted at runtime entirely in kernel space,
meaning that no intermediate decrypted data is ever written to disk. See
:ref:`encrypted containers <encryption>` for more details.

*********************
Environment Variables
*********************

#. If a flag is represented by both a CLI option and an environment variable,
   and both are set, the CLI option will take precedence. This is true for all
   environment variables with the exception of ``SINGULARITY_BIND`` and
   ``SINGULARITY_BINDPATH``, which are combined with the ``--bind`` option /
   argument pair, if both are present.

#. Environment variables will override default values of CLI options that have
   not been explicitly set in the command line.

#. Any default values for CLI options that have not been overridden on the
   command line, or by corresponding environment variables, will then take
   effect.

Defaults
========

The following variables have defaults that can be overridden by assigning your
own values to the corresponding environment variables at runtime:

Docker
------

| ``SINGULARITY_DOCKER_LOGIN``
| Set this to login to a Docker Repository interactively.

| ``SINGULARITY_DOCKER_USERNAME``
| Your Docker username.

| ``SINGULARITY_DOCKER_PASSWORD``
| Your Docker password.

| ``RUNSCRIPT_COMMAND``
| Is not obtained from the environment, but is a hard coded default
  ("/bin/bash"). This is the fallback command used in the case that the docker
  image does not have a CMD or ENTRYPOINT. ``TAG`` Is the default tag,
  ``latest``.

| ``SINGULARITY_NOHTTPS``
| This is relevant if you want to use a registry that doesn't support https. A
  typical use-case for this variable is when using local registry, running on
  the same machine as {Singularity} itself.

Library
-------

| ``SINGULARITY_BUILDER``
| Used to specify the remote builder service URL. The default value is Sylabs'
  remote builder.

| ``SINGULARITY_LIBRARY``
| Used to specify the library to pull from.
| Default is set to Sylabs' Cloud Library.

| ``SINGULARITY_REMOTE``
| Used to build an image remotely. (Importantly, such remote builds do not
  require root access on the local machine.) The default is false.

Encryption
----------

| ``SINGULARITY_ENCRYPTION_PASSPHRASE``
| Used to pass a plaintext passphrase to be used to encrypt a container file
  system (in conjunction with the ``--encrypt`` flag). The default is empty.

| ``SINGULARITY_ENCRYPTION_PEM_PATH``
| Used to specify the location of a public key to use for container encryption
  (in conjunction with the ``--encrypt`` flag). The default is empty.
