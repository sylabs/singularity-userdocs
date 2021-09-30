.. _build-environment:

=================
Build Environment
=================

.. _sec:buildenv:

--------
Overview
--------

You may wish to customize your build
environment by doing things such as specifying a custom cache directory for images or
sending your Docker Credentials to the registry endpoint. Here we will discuss these and other topics
related to the build environment.

.. _sec:cache:

-------------
Cache Folders
-------------

{Singularity} will cache SIF container images generated from remote
sources, and any OCI/docker layers used to create them. The cache is
created at ``$HOME/.singularity/cache`` by default. The location of
the cache can be changed by setting the ``SINGULARITY_CACHEDIR``
environment variable.

When you run builds as root, using ``sudo``, images will be cached
in root’s home at ``/root`` and not your user’s home. Use the
``-E`` option to sudo to pass through the ``SINGULARITY_CACHEDIR``
environment variable, if you set it.

.. code-block:: none

    $ export SINGULARITY_CACHEDIR=/tmp/user/temporary-cache

    # Running a build under your user account
    $ singularity build --fakeroot myimage.sif mydef.def

    # Running a build with sudo, must use -E to pass env var
    $ sudo -E singularity build myimage.sif mydef.def

If you change the value of ``SINGULARITY_CACHEDIR`` be sure to choose
a location that is:

 - Unique to you. Permissions are set on the cache so that private
   images cached for one user are not exposed to another. This means
   that ``SINGULARITY_CACHEDIR`` cannot be shared.
 - Located on a filesystem with sufficient space for the number and size of
   container images anticipated.
 - Located on a filesystem that supports atomic rename, if possible.

.. warning::

   If you are not certain that your ``$HOME`` or
   ``SINGULARITY_CACHEDIR`` filesystems support atomic rename, do not
   run {Singularity} in parallel using remote container URLs. Instead
   use ``singularity pull`` to create a local SIF image, and then run
   this SIF image in a parallel step. An alternative is to use the
   ``--disable-cache`` option, but this will result in each
   {Singularity} instance independently fetching the container from the
   remote source, into a temporary location.


Inside the cache location you will find separate directories for the
different kinds of data that are cached:

.. code-block:: none

    $HOME/.singularity/cache/blob
    $HOME/.singularity/cache/library
    $HOME/.singularity/cache/net
    $HOME/.singularity/cache/oci-tmp
    $HOME/.singularity/cache/shub

You can safely delete these directories, or content within
them. {Singularity} will re-create any directories and data that are
needed in future runs.

You should not add any additional files, or modify files in the cache,
as this may cause checksum / integrity errors when you run or build
containers. If you experience problems use ``singularity cache clean``
to reset the cache to a clean, empty state.
    
BoltDB Corruption Errors
========================

The library that {Singularity} uses to retrieve and cache Docker/OCI layers
keeps track of them using a single file database. If your home directory is on a
network filesystem which experiences interruptions, or you run out of storage,
it is possible for this database to become inconsistent.

If you observe error messages when trying to run {Singularity} that mention
`github.com/etcd-io/bbolt` then you should remove the database file:

.. code::

    rm ~/.local/share/containers/cache/blob-info-cache-v1.boltdb

--------------
Cache commands
--------------

The ``cache`` command for {Singularity} allows you to view and clean up
your cache, without manually inspecting the cache directories.

.. note::

   If you have built images as root, directly or via ``sudo``, the
   cache location for those builds is ``/root/.singularity``. You
   will need to use ``sudo`` when running ``cache clean`` or ``cache
   list`` to manage these cache entries.

   

Listing Cache
=============

To view a summary of cache usage, use ``singularity cache list``:

.. code-block:: none

    $ singularity cache list
    There are 4 container file(s) using 59.45 MB and 23 oci blob file(s) using 379.10 MB of space
    Total space used: 438.55 MB

To view detailed information, use ``singularity cache list -v``:

.. code-block:: none

    $ singularity cache list -v
    NAME                     DATE CREATED           SIZE             TYPE
    0ed5a98249068fe0592edb   2020-05-27 12:57:22    192.21 MB        blob
    1d9cd1b99a7eca56d8f2be   2020-05-28 15:19:07    0.35 kB          blob
    219c332183ec3800bdfda4   2020-05-28 12:22:13    0.35 kB          blob
    2adae3950d4d0f11875568   2020-05-27 12:57:16    51.83 MB         blob
    376057ac6fa17f65688c56   2020-05-27 12:57:12    50.39 MB         blob
    496548a8c952b37bdf149a   2020-05-27 12:57:14    10.00 MB         blob
    5a63a0a859d859478f3046   2020-05-27 12:57:13    7.81 MB          blob
    5efaeecfa72afde779c946   2020-05-27 12:57:25    0.23 kB          blob
    6154df8ff9882934dc5bf2   2020-05-27 08:37:22    0.85 kB          blob
    70d0b3967cd8abe96c9719   2020-05-27 12:57:24    26.61 MB         blob
    8f5af4048c33630473b396   2020-05-28 15:19:07    0.57 kB          blob
    95c3f3755f37380edb2f8f   2020-05-28 14:07:20    2.48 kB          blob
    96878229af8adf91bcbf11   2020-05-28 14:07:20    0.81 kB          blob
    af88fdb253aac46693de78   2020-05-28 12:22:13    0.58 kB          blob
    bb94ffe723890b4d62d742   2020-05-27 12:57:23    6.15 MB          blob
    c080bf936f6a1fdd2045e3   2020-05-27 12:57:25    1.61 kB          blob
    cbdbe7a5bc2a134ca8ec91   2020-05-28 12:22:13    2.81 MB          blob
    d51af753c3d3a984351448   2020-05-27 08:37:21    28.56 MB         blob
    d9cbbca60e5f0fc028b13c   2020-05-28 15:19:06    760.85 kB        blob
    db8816f445487e48e1d614   2020-05-27 12:57:25    1.93 MB          blob
    fc878cd0a91c7bece56f66   2020-05-27 08:37:22    32.30 kB         blob
    fee5db0ff82f7aa5ace634   2020-05-27 08:37:22    0.16 kB          blob
    ff110406d51ca9ea722112   2020-05-27 12:57:25    7.78 kB          blob
    sha256.02ee8bf9dc335c2   2020-05-29 13:45:14    28.11 MB         library
    sha256.5111f59250ac94f   2020-05-28 13:14:39    782.34 kB        library
    747d2dbbaaee995098c979   2020-05-28 14:07:22    27.77 MB         oci-tmp
    9a839e63dad54c3a6d1834   2020-05-28 12:22:13    2.78 MB          oci-tmp

    There are 4 container file(s) using 59.45 MB and 23 oci blob file(s) using 379.10 MB of space
    Total space used: 438.55 MB

All cache entries are named using a content hash, so that identical
layers or images that are pulled from different URIs do not consume
more space than needed.
    
Entries marked ``blob`` are OCI/docker layers and manifests, that are
used to create SIF format images in the ``oci-tmp`` cache. Other
caches are named for the source of the image e.g. ``library`` and
``oras``.

You can limit the cache list to a specific cache type with the
``-type`` / ``-t`` option.

    
Cleaning the Cache
==================

To reclaim space used by the {Singularity} cache, use ``singularity
cache clean``.

By default ``singularity cache clean`` will remove all cache entries,
after asking you to confirm:

.. code-block:: none

    $ singularity cache clean
    This will delete everything in your cache (containers from all sources and OCI blobs). 
    Hint: You can see exactly what would be deleted by canceling and using the --dry-run option.
    Do you want to continue? [N/y] n

Use the ``--dry-run`` / ``-n`` option to see the files that would be
deleted, or the ``--force`` / ``-f`` option to clean without asking
for confirmation.

If you want to leave your most recent cached images in place, but
remove images that were cached longer ago, you can use the ``--days``
/ ``-d`` option. E.g. to clean cache entries older than 30 days:

.. code-block:: none

    $ singularity cache clean --days 30

To remove only a specific kind of cache entry, e.g. only library
images, use the ``type`` / ``-T`` option:

.. code-block:: none

    $ singularity cache clean --type library


.. _sec:temporaryfolders:

-----------------
Temporary Folders
-----------------

When building a container, or pulling/running a {Singularity} container
from a Docker/OCI source, a temporary working space is required. The
container is constructed in this temporary space before being packaged
into a {Singularity} SIF image. Temporary space is also used when
running containers in unprivileged mode, and performing some
operations on filesystems that do not fully support ``--fakeroot``.

The location for temporary directories defaults to
``/tmp``. {Singularity} will also respect the environment variable
``TMPDIR``, and both of these locations can be overridden by setting
the environment variable ``SINGULARITY_TMPDIR``.

The temporary directory used during a build must be on a filesystem
that has enough space to hold the entire container image,
uncompressed, including any temporary files that are created and later
removed during the build. You may need to set ``SINGULARITY_TMPDIR``
when building a large container on a system which has a small ``/tmp``
filesystem.

Remember to use ``-E`` option to pass the value of
``SINGULARITY_TMPDIR`` to root's environment when executing the
``build`` command with ``sudo``.

.. warning::

   Many modern Linux distributions use an in-memory ``tmpfs``
   filesystem for ``/tmp`` when installed on a computer with a
   sufficient amount of RAM. This may limit the size of container you
   can build, as temporary directories under ``/tmp`` share RAM with
   runniing programs etc. A ``tmpfs`` also uses default mount options
   that can interfere with some container builds.

   Set ``SINGULARITY_TMPDIR`` to a disk location, or disable the
   ``tmpfs`` ``/tmp`` mount on your system if you experience
   problems.

 
--------------------
Encrypted Containers
--------------------

Beginning in {Singularity} 3.4.0 it is possible to build and run encrypted
containers.  The containers are decrypted at runtime entirely in kernel space, 
meaning that no intermediate decrypted data is ever present on disk or in 
memory.  See :ref:`encrypted containers <encryption>` for more details.

---------------------
Environment Variables
---------------------

#. If a flag is represented by both a CLI option and an environment variable, and both are set, the CLI option will always take precedence. This is true for all environment variables except for ``SINGULARITY_BIND`` and ``SINGULARITY_BINDPATH`` which is combined with the ``--bind`` option, argument pair if both are present.

#. Environment variables overwrite default values in the CLI code

#. Any defaults in the CLI code are applied.


Defaults
========

The following variables have defaults that can be customized by you via
environment variables at runtime.

Docker
------

**SINGULARITY_DOCKER_LOGIN** Used for the interactive login for Docker Hub.

**SINGULARITY_DOCKER_USERNAME** Your Docker username.

**SINGULARITY_DOCKER_PASSWORD** Your Docker password.

**RUNSCRIPT_COMMAND** Is not obtained from the environment, but is a
hard coded default (“/bin/bash”). This is the fallback command used in
the case that the docker image does not have a CMD or ENTRYPOINT.
**TAG** Is the default tag, ``latest``.

**SINGULARITY_NOHTTPS** This is relevant if you want to use a
registry that doesn’t have https, and it speaks for itself. If you
export the variable ``SINGULARITY_NOHTTPS`` you can force the software to not use https when
interacting with a Docker registry. This use case is typically for use
of a local registry.

Library
-------

**SINGULARITY_BUILDER** Used to specify the remote builder service URL. The default value is our remote builder.

**SINGULARITY_LIBRARY** Used to specify the library to pull from. Default is set to our Cloud Library.

**SINGULARITY_REMOTE** Used to build an image remotely (This does not require root). The default is set to false.

Encryption
----------

**SINGULARITY_ENCRYPTION_PASSPHRASE** Used to pass a plaintext passphrase to encrypt a container file system (with the ``--encrypt`` flag). The default is empty.

**SINGULARITY_ENCRYPTION_PEM_PATH** Used to specify the location of a public key to use for container encryption (with the ``--encrypt`` flag). The default is empty.
