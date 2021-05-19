===================
Persistent Overlays
===================

Persistent overlay directories allow you to overlay a writable file
system on an immutable read-only container for the illusion of
read-write access. You can run a container and make changes, and these
changes are kept separately from the base container image.


--------
Overview
--------

A persistent overlay is a directory or file system image that “sits on
top” of your immutable SIF container. When you install new software or
create and modify files the overlay will store the changes.

If you want to use a SIF container as though it were writable, you can
create a directory, an ext3 file system image, or embed an ext3 file
system image in SIF to use as a persistent overlay. Then you can
specify that you want to use the directory or image as an overlay at
runtime with the ``--overlay`` option, or ``--writable`` if you want
to use the overlay embedded in SIF.

If you want to make changes to the image, but do not want them to
persist, use the ``--writable-tmpfs`` option. This stores all changes
in an in-memory temporary filesystem which is discarded as soon as
the container finishes executing.

You can use persistent overlays with the following commands:

- ``run``
- ``exec``
- ``shell``
- ``instance.start``

-----
Usage
-----

To use a persistent overlay, you must first have a container.

.. code-block:: none

    $ sudo singularity build ubuntu.sif library://ubuntu

File system image overlay
=========================

Since 3.8, {Singularity} provides a command ``singularity overlay create`` to
create persistent overlay images. You can create a single EXT3 overlay image
or adding a EXT3 writable overlay partition to an existing SIF image.

.. note::

    ``dd`` and ``mkfs.ext3`` must be installed on your system. Additionally
    ``mkfs.ext3`` must support ``-d`` option in order to create an overlay
    directory tree usable by a regular user.

For example, to create a 1 GiB overlay image:

.. code-block:: none

    $ singularity overlay create --size 1024 /tmp/ext3_overlay.img

To add a 1 GiB writable overlay partition to an existing SIF image:

.. code-block:: none

    $ singularity overlay create --size 1024 ubuntu.sif

.. warning::

    It is not possible to add a writable overlay partition to a **signed**, **encrypted**
    SIF image or if the SIF image already contain a writable overlay partition.

``singularity overlay create`` also provides an option ``--create-dir``
to create additional directories owned by the calling user, it can be specified
multiple times to create many directories. This is particularly useful when you
need to make a directory writable by your user.

So for example:

.. code-block:: none

    $ singularity build /tmp/nginx.sif docker://nginx
    $ singularity overlay create --size 1024 --create-dir /var/cache/nginx /tmp/nginx.sif
    $ echo "test" | singularity exec /tmp/nginx.sif sh -c "cat > /var/cache/nginx/test"

Create an overlay image (< 3.8)
-------------------------------

You can use tools like ``dd`` and ``mkfs.ext3`` to create and format
an empty ext3 file system image, which holds all changes made in your
container within a single file. Using an overlay image file makes it
easy to transport your modifications as a single additional file
alongside the original SIF container image.

Workloads that write a very large number of small files into an
overlay image, rather than a directory, are also faster on HPC
parallel filesystems. Each write is a local operation within the
single open image file, and does not cause additional metadata
operations on the parallel filesystem.

To create an overlay image file with 500MBs of empty space:

.. code-block:: none

    $ dd if=/dev/zero of=overlay.img bs=1M count=500 && \
        mkfs.ext3 overlay.img

Now you can use this overlay with your container, though filesystem
permissions still control where you can write, so ``sudo`` is needed
to run the container as ``root`` if you need to write to ``/`` inside
the container.

.. code-block:: none

   $ sudo singularity shell --overlay overlay.img ubuntu.sif

To manage permissions in the overlay, so the container is writable by
unprivileged users you can create a directory structure on your host,
set permissions on it as needed, and include it in the overlay with
the ``-d`` option to ``mkfs.ext3``:

.. code-block:: none

   $ mkdir -p overlay/upper overlay/work
   $ dd if=/dev/zero of=overlay.img bs=1M count=500 && \
        mkfs.ext3 -d overlay overlay.img

Now the container will be writable as the unprivileged user who
created the ``overlay/upper`` and ``overlay/work`` directories
that were placed into ``overlay.img``.

.. code-block:: none

   $ singularity shell --overlay overlay.img ubuntu.sif
   Singularity> echo $USER
   dtrudg
   Singularity> echo "Hello" > /hello
                
.. note::

   The ``-d`` option to ``mkfs.ext3`` does not support ``uid`` or
   ``gid`` values >65535. To allow writes from users with larger uids
   you can create the directories for your overlay with open
   permissions, e.g. ``mkdir -p -m 777 overlay/upper overlay/work``. At runtime
   files and directories created in the overlay will have the correct
   ``uid`` and ``gid``, but it is not possible to lock down
   permissions so that the overlay is only writable by certain users.
   

Directory overlay
=================

A directory overlay is simpler to use than a filesystem image overlay,
but a directory of modifications to a base container image cannot be
transported or shared as easily as a single overlay file.

.. note::

    For security reasons, you must be root to use a bare directory as an
    overlay. ext3 file system images can be used as overlays without root
    privileges.

Create a directory as usual:

.. code-block:: none

    $ mkdir my_overlay


The example below shows the directory overlay in action.

.. code-block:: none

    $ sudo singularity shell --overlay my_overlay/ ubuntu.sif

    {Singularity} ubuntu.sif:~> mkdir /data

    {Singularity} ubuntu.sif:~> chown user /data

    {Singularity} ubuntu.sif:~> apt-get update && apt-get install -y vim

    {Singularity} ubuntu.sif:~> which vim
    /usr/bin/vim

    {Singularity} ubuntu.sif:~> exit

.. _overlay-sif:
    
Overlay embedded in SIF
=======================

It is possible to embed an overlay image in the SIF file that holds a
container. This allows the read-only container image and your
modifications to it to be managed as a single file.  In order to do
this, you must first create a file system image:

.. code-block:: none

    $ dd if=/dev/zero of=overlay.img bs=1M count=500 && \
        mkfs.ext3 overlay.img

Then, you can add the overlay to the SIF image using the ``sif``
functionality of {Singularity}.

.. code-block:: none

   $ singularity sif add --datatype 4 --partfs 2 --parttype 4 --partarch 2 --groupid 1 ubuntu_latest.sif overlay.img

Below is the explanation what each parameter means, and how it can possibly affect the operation:

- ``datatype`` determines what kind of an object we attach, e.g. a
  definition file, environment variable, signature.
- ``partfs`` should be set according to the partition type,
  e.g. SquashFS, ext3, raw.
- ``parttype`` determines the type of partition. In our case it is
  being set to overlay.
- ``partarch`` must be set to the architecture against you're
  building. In this case it's ``amd64``.
- ``groupid`` is the ID of the container image group. In most cases
  there's no more than one group, therefore we can assume it is 1.

All of these options are documented within the CLI help. Access it by
running ``singularity sif add --help``.

After you've completed the steps above, you can shell into your
container with the ``--writable`` option.

.. code-block:: none

        $ sudo singularity shell --writable ubuntu_latest.sif

Final note
==========

You will find that your changes persist across sessions as though you
were using a writable container.

.. code-block:: none

    $ singularity shell --overlay my_overlay/ ubuntu.sif

    {Singularity} ubuntu.sif:~> ls -lasd /data
    4 drwxr-xr-x 2 user root 4096 Apr  9 10:21 /data

    {Singularity} ubuntu.sif:~> which vim
    /usr/bin/vim

    {Singularity} ubuntu.sif:~> exit


If you mount your container without the ``--overlay`` directory, your changes
will be gone.

.. code-block:: none

    $ singularity shell ubuntu.sif

    {Singularity} ubuntu.sif:~> ls /data
    ls: cannot access 'data': No such file or directory

    {Singularity} ubuntu.sif:~> which vim

    {Singularity} ubuntu.sif:~> exit

To resize an overlay, standard Linux tools which manipulate ext3
images can be used.  For instance, to resize the 500MB file created
above to 700MB one could use the ``e2fsck`` and ``resize2fs``
utilities like so:

.. code-block:: none

    $ e2fsck -f my_overlay && \
        resize2fs my_overlay 700M

Hints for creating and manipulating ext3 images on your distribution
are readily available online and are not treated further in this
manual.
