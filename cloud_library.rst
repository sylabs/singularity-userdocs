.. _cloud_library:

Cloud Library
=============

--------
Overview
--------

The Sylabs Cloud Library is the place to :ref:`push <push>` your
containers to the cloud so other users can :ref:`pull <pull>`,
:ref:`verify <signNverify>`, and use them.

The Sylabs Cloud also provides a :ref:`Remote Builder
<remote_builder>`, allowing you to build containers on a secure remote
service. This is convenient so that you can build containers on
systems where you do not have root privileges.

.. _make_a_account:

---------------
Make an Account
---------------

Making an account is easy, and straightforward:

 1. Go to: https://cloud.sylabs.io/library.
 2. Click "Sign in to Sylabs" (top right corner).
 3. Select your method to sign in, with Google, GitHub, GitLab, or Microsoft.
 4. Type your passwords, and that's it!

.. _creating_a_access_token:

-----------------------
Creating a Access token
-----------------------

Access tokens for pushing a container, and remote builder.

To generate a access token, do the following steps:

  1) Go to: https://cloud.sylabs.io/
  2) Click "Sign In" and follow the sign in steps.
  3) Click on your login id (same and updated button as the Sign in one).
  4) Select "Access Tokens" from the drop down menu.
  5) Enter a name for your new access token, such as "test token"
  6) Click the "Create a New Access Token" button.
  7) Click "Copy token to Clipboard" from the "New API Token" page.
  8) Run ``singularity remote login`` and paste the access token at the prompt.

Now that you have your token, you are ready to push your container!

.. _push:

-------------------
Pushing a Container
-------------------

The ``singularity push`` command will push a container to the
container library with the given URL. Here's an example of a typical
push command:

.. code-block:: none

    $ singularity push my-container.sif library://your-name/project-dir/my-container:latest

The ``:latest`` is the container tag. Tags are used to have different
version of the same container.

.. note::
    When pushing your container, there's no need to add a ``.sif`` (Singularity Image Format) to the end of the container name, (like
    on your local machine), because all containers on the library are SIF containers.

Let's assume you have your container (v1.0.1), and you want to push
that container without deleting your ``:latest`` container, then you
can add a version tag to that container, like so:

.. code-block:: none

    $ singularity push my-container.sif library://your-name/project-dir/my-container:1.0.1

You can download the container with that tag by replacing the
``:latest``, with the tagged container you want to download.

To set a description against the container image as you push it, use
the `-D` flag introduced in {Singularity} 3.7. This provides an
alternative to setting the description via the web interface:

.. code-block:: console

    $ singularity push -D "My alpine 3.11 container" alpine_3.11.sif library://myuser/examples/alpine:3.11
    2.7MiB / 2.7MiB [=========================================================================] 100 % 1.1 MiB/s 0s

    Library storage: using 13.24 MiB out of 11.00 GiB quota (0.1% used)
    Container URL: https://cloud.sylabs.io/library/myuser/examples/alpine

Note that when you push to a library that supports it, {Singularity} 3.7
and above will report your quota usage and the direct URL to view the
container in your web browser.
               
.. _pull:

-------------------
Pulling a container
-------------------

The ``singularity pull`` command will download a container from the `Library <https://cloud.sylabs.io/library>`_
(``library://``), `Docker Hub <https://hub.docker.com/>`_ (``docker://``), and also
`Shub <https://singularity-hub.org>`_ (``shub://``).

.. note::
    When pulling from Docker, the container will automatically be converted to a SIF (Singularity Image Format) container.

Here's a typical pull command:

.. code-block:: none

    $ singularity pull file-out.sif library://alpine:latest

    # or pull from docker:

    $ singularity pull file-out.sif docker://alpine:latest

.. note::
    If there's no tag after the container name, {Singularity} automatically will pull the container with the ``:latest`` tag.

To pull a container with a specific tag, just add the tag to the library URL:

.. code-block:: none

    $ singularity pull file-out.sif library://alpine:3.8

Of course, you can pull your own containers. Here's what that will look like:

Pulling your own container
--------------------------

Pulling your own container is just like pulling from Github, Docker, etc...

.. code-block:: none

    $ singularity pull out-file.sif library://your-name/project-dir/my-container:latest

    # or use a different tag:

    $ singularity pull out-file.sif library://your-name/project-dir/my-container:1.0.1

.. note::
    You *don't* have to specify a output file, one will be created automatically, but it's good practice to always
    specify your output file.

--------------------------
Verify/Sign your Container
--------------------------

Verify containers that you pull from the library, ensuring they are bit-for-bit reproductions of the original image.

Check out :ref:`this page <signNverify>` on how to: :ref:`verify a container <verify_container_from_library>`,
:ref:`making PGP key, and sign your own containers <sign_your_own_containers>`.

.. _search_the_library:

------------------------------------
Searching the Library for Containers
------------------------------------

To find interesting or useful containers in the library, you can open
https://cloud.sylabs.io/library in your browser and search from there
through the web GUI.

Alternatively, from the CLI you can use ``singularity search
<query>``. This will search the library for container images matching
``<query>``.

Using the CLI Search
--------------------

Here is an example of searching the library for ``centos``:

.. code-block:: console

    singularity search centos
    Found 72 container images for amd64 matching "centos":

	library://dcsouthwick/iotools/centos7:latest

	library://dcsouthwick/iotools/centos7:sha256.48e81523aaad3d74e7af8b154ac5e75f2726cc6cab37f718237d8f89d905ff89
		Minimal centos7 image from yum bootstrap

	library://dtrudg/linux/centos:7,centos7,latest

	library://dtrudg/linux/centos:centos6,6

	library://emmeff/centos/centos:8

	library://essen1999/default/centos-tree:latest

	library://gallig/default/centos_benchmark-signed:7.7.1908
		Signed by: 6B44B0BC9CD273CC6A71DA8CED6FA43EF8771A02

	library://gmk/default/centos7-devel:latest
		Signed by: 7853F08767A4596B3C1AD95E48E1080AB16ED1BC


Containers can have multiple tags, and these are shown separated by
commas after the ``:`` in the
URL. E.g. ``library://dtrudg/linux/centos:7,centos7,latest`` is a
single container image with 3 tags, ``7``, ``centos7``, and
``latest``. You can ``singularity pull`` the container image using any
one of these tags.
                
                
Note that the results show ``amd64`` containers only. By default
``search`` returns only containers with an architecture matching your
current system. To e.g. search for ``arm64`` containers from an
``amd64`` machine you can use the ``--arch`` flag:

.. code-block:: console

    singularity search --arch arm64 alpine
    Found 5 container images for arm64 matching "alpine":

	library://dtrudg-sylabs-2/multiarch/alpine:latest

	library://geoffroy.vallee/alpine/alpine:latest
		Signed by: 9D56FA7CAFB4A37729751B8A21749D0D6447B268

	library://library/default/alpine:3.11.5,latest,3,3.11

	library://library/default/alpine:3.9,3.9.2

	library://sylabs/tests/passphrase_encrypted_alpine:3.11.5

        
You can also limit results to only signed containers with the
``--signed`` flag:

.. code-block:: console

    singularity search --signed alpine
    Found 45 container images for amd64 matching "alpine":

	library://deep/default/alpine:latest,1.0.1
		Signed by: 8883491F4268F173C6E5DC49EDECE4F3F38D871E

	library://godloved/secure/alpine:20200514.0.0
		Signed base image built directly from mirrors suitable for secure building. Make sure to check that the fingerprint is B7761495F83E6BF7686CA5F0C1A7D02200787921
		Signed by: B7761495F83E6BF7686CA5F0C1A7D02200787921

	library://godlovedc/blah/alpine:sha256.63259fd0a2acb88bb652702c08c1460b071df51149ff85dc88db5034532a14a0
		Signed by: 8883491F4268F173C6E5DC49EDECE4F3F38D871E

	library://heffaywrit/base/alpine:latest
		Signed by: D4038BDDE21017435DFE5ADA9F2D10A25D64C1EF

	library://hellseva/class/alpine:latest
		Signed by: 6D60F95E86A593603897164F8E09E44D12A7111C

	library://hpc110/default/alpine-miniconda:cupy
		Signed by: 9FF48D6202271D3C842C53BD0D237BE8BB5B5C76
        ...
            
.. _remote_builder:

--------------
Remote Builder
--------------

The remote builder service can build your container in the cloud removing the requirement for root access.

Here's a typical remote build command:

.. code-block:: none

    $ singularity build --remote file-out.sif docker://ubuntu:18.04


Building from a definition file:
--------------------------------

This is our definition file. Let's call it ``ubuntu.def``:

.. code-block:: singularity

    bootstrap: library
    from: ubuntu:18.04

    %runscript
        echo "hello world from ubuntu container!"

Now, to build the container, use the ``--remote`` flag, and without ``sudo``:

.. code-block:: none

    $ singularity build --remote ubuntu.sif ubuntu.def

.. note::
    Make sure you have a :ref:`access token <creating_a_access_token>`, otherwise the build will fail.

After building, you can test your container like so:

.. code-block:: none

    $ ./ubuntu.sif
    hello world from ubuntu container!

You can also use the web GUI to build containers remotely. First, go to https://cloud.sylabs.io/builder (make sure you are signed in).
Then you can copy and paste, upload, or type your definition file. When you are finished, click build. Then you can download the container
with the URL.
