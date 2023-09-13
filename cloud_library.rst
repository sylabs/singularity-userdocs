.. _cloud_library:

###########
SCS Library
###########

********
Overview
********

The Singularity Container Services (SCS) Library is the place to :ref:`push
<push>` your containers to the cloud so other users can :ref:`pull <pull>`,
:ref:`verify <signNverify>`, and use them.

SCS also provides a :ref:`Remote Builder <remote_builder>`, allowing you to
build containers on a secure remote service. This is convenient so that you can
build containers on systems where you do not have root privileges.

.. _make_a_account:

***************
Make an Account
***************

Making an account is easy, and straightforward:

   #. Go to: https://cloud.sylabs.io/library.
   #. Click "Sign in to Sylabs" (top right corner).
   #. Select your method to sign in, with Google, GitHub, GitLab, or
      Microsoft.
   #. Type your passwords, and that's it!

.. _creating_a_access_token:

***********************
Creating a Access token
***********************

Access tokens for pushing a container, and remote builder.

To generate a access token, do the following steps:

   #. Go to: https://cloud.sylabs.io/
   #. Click "Sign In" and follow the sign in steps.
   #. Click on your login id (same and updated button as the Sign in
      one).
   #. Select "Access Tokens" from the drop down menu.
   #. Enter a name for your new access token, such as "test token"
   #. Click the "Create a New Access Token" button.
   #. Click "Copy token to Clipboard" from the "New API Token" page.
   #. Run ``singularity remote login`` and paste the access token at the
      prompt.

Now that you have your token, you are ready to push your container!

.. _push:

*******************
Pushing a Container
*******************

The ``singularity push`` command will push a container to the container
library with the given URL. Here's an example of a typical push command:

.. code::

   $ singularity push my-container.sif library://your-name/project-dir/my-container:latest

The ``:latest`` is the container tag. Tags are used to have different
version of the same container.

.. note::

   When pushing your container, there's no need to add a ``.sif``
   (Singularity Image Format) to the end of the container name, (like on
   your local machine), because all containers on the library are SIF
   containers.

Let's assume you have your container (v1.0.1), and you want to push that
container without deleting your ``:latest`` container, then you can add
a version tag to that container, like so:

.. code::

   $ singularity push my-container.sif library://your-name/project-dir/my-container:1.0.1

You can download the container with that tag by replacing the
``:latest``, with the tagged container you want to download.

To set a description against the container image as you push it, use the
`-D` flag introduced in {Singularity} 3.7. This provides an alternative
to setting the description via the web interface:

.. code:: console

   $ singularity push -D "My alpine 3.11 container" alpine_3.11.sif library://myuser/examples/alpine:3.11
   2.7MiB / 2.7MiB [=========================================================================] 100 % 1.1 MiB/s 0s

   Library storage: using 13.24 MiB out of 11.00 GiB quota (0.1% used)
   Container URL: https://cloud.sylabs.io/library/myuser/examples/alpine

Note that when you push to a library that supports it, {Singularity} 3.7
and above will report your quota usage and the direct URL to view the
container in your web browser.

OCI-SIF Images
==============

If you are using {Singularity} 4's new OCI-mode, you may wish to push OCI-SIF
images to a ``library://`` destination. The standard ``push`` command can be
used, and {Singularity} will perform the push as an OCI image.

Instead of uploading the container as a single SIF file, the OCI configuration
and layer blobs that are encapsulated in the OCI-SIF will be uploaded to the OCI
registry that sits behind the SCS / Singularity Enterprise Library. 

.. note::

   The OCI image specification doesn't support SIF signatures, or any additional
   partitions that can be added to SIF (including OCI-SIF) files by
   {Singularity}.

   If you have signed an OCI-SIF image locally, the signature(s) will not be
   pushed to the library. You may wish to push the OCI-SIF, as a single file, to
   an OCI registry using the ``oras://`` protocol instead.

Pushing OCI-SIF containers to the library in this manner means that they can be
accessed by other OCI tools. For example, you can use the `Skopeo CLI tool
<https://github.com/containers/skopeo>`__ to examine the image in the registry
after it has been pushed. First, ``push`` an OCI-SIF to the SCS ``library://``.
The ``-U`` option is needed because the image is unsigned.

.. code::

   $ singularity push -U alpine_latest.oci.sif library://example/userdoc/alpine:latest
   WARNING: Skipping container verification
   INFO:    Pushing an OCI-SIF to the library OCI registry. Use `--oci` to pull this image.

Now use ``skopeo`` to access the image in the library. This requires
authentication, which is handled automatically when you use ``singularity
push``. For other tools, {Singularity} provides a command ``singularity remote
get-login-password`` that will provide a token that we can use to login to
``registry.sylabs.io``, which is the address of the OCI registry backing the SCS
library.

.. code::

   $ singularity remote get-login-password | \
       skopeo login -u example --password-stdin registry.sylabs.io
   Login Succeeded!

Finally, use ``skopeo inspect`` to examine the image pushed earlier:

 .. code::

   $ skopeo inspect docker://registry.sylabs.io/example/userdoc/alpine:latest
   {
      "Name": "registry.sylabs.io/example/userdoc/alpine",
      "Digest": "sha256:d08ad9745675812310727c0a99a4472b82fb1cc81e5c42ceda023f1bc35ca34a",
      "RepoTags": [
         "latest"
      ],
      "Created": "2023-08-07T20:16:26.309461618Z",
      "DockerVersion": "",
      "Labels": null,
      "Architecture": "amd64",
      "Os": "linux",
      "Layers": [
         "sha256:a0c5ced3a57bd1d0d71aaf4a0ea6131d5f163a4a8c5355468c18d4ef006f5d7d"
      ],
      "LayersData": [
         {
               "MIMEType": "application/vnd.sylabs.image.layer.v1.squashfs",
               "Digest": "sha256:a0c5ced3a57bd1d0d71aaf4a0ea6131d5f163a4a8c5355468c18d4ef006f5d7d",
               "Size": 3248128,
               "Annotations": null
         }
      ],
      "Env": [
         "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      ]
   }

Because the OCI-SIF was pushed as an OCI image, ``skopeo inspect`` is able to
show the image configuration. This is not possible for non-OCI-SIF images:

.. code::

   $ skopeo inspect docker://registry.sylabs.io/library/default/alpine:latest
   FATA[0001] unsupported image-specific operation on artifact with type "application/vnd.sylabs.sif.config.v1+json"

.. _pull:

*******************
Pulling a container
*******************

The ``singularity pull`` command will download a container from the
`Library <https://cloud.sylabs.io/library>`_ (``library://``), `Docker
Hub <https://hub.docker.com/>`_ (``docker://``), and also `Shub
<https://singularity-hub.org>`_ (``shub://``).

.. note::

   When pulling from Docker, the container will automatically be
   converted to a SIF (Singularity Image Format) container.

Here's a typical pull command:

.. code::

   $ singularity pull file-out.sif library://alpine:latest

   # or pull from docker:

   $ singularity pull file-out.sif docker://alpine:latest

.. note::

   If there's no tag after the container name, {Singularity}
   automatically will pull the container with the ``:latest`` tag.

To pull a container with a specific tag, just add the tag to the library
URL:

.. code::

   $ singularity pull file-out.sif library://alpine:3.8

Of course, you can pull your own containers. Here's what that will look
like:

Pulling your own container
==========================

Pulling your own container is just like pulling from Github, Docker,
etc...

.. code::

   $ singularity pull out-file.sif library://your-name/project-dir/my-container:latest

   # or use a different tag:

   $ singularity pull out-file.sif library://your-name/project-dir/my-container:1.0.1

.. note::

   You *don't* have to specify a output file, one will be created
   automatically, but it's good practice to always specify your output
   file.

OCI-SIF Images
==============

If you are using {Singularity} 4's new OCI-mode and have pushed OCI-SIF
containers to the SCS library, they are stored as OCI images in the OCI registry
that backs the library. You can pull these images with the standard ``pull``
command:

.. code::

   $ singularity pull library://sylabs/test/alpine-oci-sif:latest
   INFO:    sylabs/test/alpine-oci-sif:latest is an OCI image, attempting to fetch as an OCI-SIF
   Getting image source signatures
   Copying blob af32528d4445 done  
   Copying config a5d222bd0d done  
   Writing manifest to image destination
   INFO:    Writing OCI-SIF image
   INFO:    Cleaning up.
   WARNING: integrity: signature not found for object group 1
   WARNING: Skipping container verification

Note that {Singularity} detects the image is an OCI image, and automatically
retrieves it to an OCI-SIF file.

If the image was a non-OCI-SIF, built for {Singularity}'s default native mode,
then it would be retrieved as-is. To ensure that an image retrieved from a
``library://`` URI is an OCI-SIF, use the ``--oci`` flag. This will produce an
error if a non-OCI-SIF is pulled:

.. code::

   $ singularity pull --oci library://sylabs/examples/ruby
   Getting image source signatures
   Copying blob a21814eefb7f done  
   Copying config 5211e7986c done  
   Writing manifest to image destination
   INFO:    Cleaning up.
   FATAL:   While pulling library image: error fetching image: while creating OCI-SIF: while checking OCI image: json: cannot unmarshal string into Go struct field ConfigFile.rootfs of type v1.RootFS

.. _library_platform_arch:

Specifying a platform / architecture
====================================

By default, ``singularity pull`` from a ``library://`` URI will attempt to fetch
a container that matches the architecture of your host system. If you need to
retrieve a container that does not have the same architecture as your host (e.g.
an ``arm64`` container on an ``amd64`` host), you can use the ``--platform`` or
``--arch`` options.

The ``--arch`` option accepts a CPU architecture only. For example, to pull an
Ubuntu image for a 64-bit ARM system:

.. code::

   $ singularity pull --arch arm64 library://ubuntu

The ``--platform`` option accepts an OCI platform string. This has two or three
parts, separated by forward slashes (``/``):

- An OS value. Only ``linux`` is supported by {Singularity}.
- A CPU architecture value, e.g. ``arm64``.
- An optional CPU variant, e.g. ``v8``.

Note that the library does not support CPU variants. Any CPU variant provided
will be ignored.

To pull an Ubuntu image for a 64-bit ARM system from the library, using the
``--platform`` option:

.. code::

   $ singularity pull --platform linux/arm64 library://ubuntu

**************************
Verify/Sign your Container
**************************

Verify containers that you pull from the library, ensuring they are
bit-for-bit reproductions of the original image.

Check out :ref:`this page <signNverify>` on how to: :ref:`verify a
container <verify_container_from_library>`, :ref:`making PGP key, and
sign your own containers <sign_your_own_containers>`.

.. _search_the_library:

************************************
Searching the Library for Containers
************************************

To find interesting or useful containers in the library, you can open
https://cloud.sylabs.io/library in your browser and search from there
through the web GUI.

Alternatively, from the CLI you can use ``singularity search <query>``.
This will search the library for container images matching ``<query>``.

Using the CLI Search
====================

Here is an example of searching the library for ``centos``:

.. code:: console

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
commas after the ``:`` in the URL. E.g.
``library://dtrudg/linux/centos:7,centos7,latest`` is a single container
image with 3 tags, ``7``, ``centos7``, and ``latest``. You can
``singularity pull`` the container image using any one of these tags.

Note that the results show ``amd64`` containers only. By default
``search`` returns only containers with an architecture matching your
current system. To e.g. search for ``arm64`` containers from an
``amd64`` machine you can use the ``--arch`` flag:

.. code:: console

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

.. code:: console

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

**************
Remote Builder
**************

The remote builder service can build your container in the cloud
removing the requirement for root access.

Here's a typical remote build command:

.. code::

   $ singularity build --remote file-out.sif docker://ubuntu:22.04

Building from a definition file:
================================

This is our definition file. Let's call it ``ubuntu.def``:

.. code:: singularity

   bootstrap: library
   from: ubuntu:22.04

   %runscript
       echo "hello world from ubuntu container!"

Now, to build the container, use the ``--remote`` flag, and without
``sudo``:

.. code::

   $ singularity build --remote ubuntu.sif ubuntu.def

.. note::

   Make sure you have a :ref:`access token <creating_a_access_token>`,
   otherwise the build will fail.

After building, you can test your container like so:

.. code::

   $ ./ubuntu.sif
   hello world from ubuntu container!

You can also use the web GUI to build containers remotely. First, go to
https://cloud.sylabs.io/builder (make sure you are signed in). Then you
can copy and paste, upload, or type your definition file. When you are
finished, click build. Then you can download the container with the URL.
