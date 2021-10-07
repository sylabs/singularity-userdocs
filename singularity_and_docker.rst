.. _singularity-and-docker:

=====================================
Support for Docker and OCI Containers
=====================================

The Open Containers Initiative (OCI) container format, which grew out
of Docker, is the dominant standard for cloud-focused containerized
deployments of software. Although {Singularity}'s own container format
has many unique advantages, it's likely you will need to work with
Docker/OCI containers at some point.

{Singularity} aims for maximum compatibility with Docker, within the
constraints on a runtime that is well suited for use on shared systems
and especially in HPC environments.

Using {Singularity} you can:

* Pull, run, and build from most containers on Docker Hub, without
  changes.

* Pull, run, and build from containers hosted on other registries,
  including private registries deployed on premise, or in the cloud.

* Pull and build from OCI containers in archive formats, or cached in
  a local Docker daemon.

This section will highlight these workflows, and discuss the
limitations and best practices to keep in mind when creating
containers targeting both Docker and {Singularity}.

--------------------------
Containers From Docker Hub
--------------------------

Docker Hub is the most common place that projects publish public
container images. At some point, it's likely that you will want to run
or build from containers that are hosted there.

Public Containers
=================

It's easy to run a public Docker Hub container with
{Singularity}. Just put ``docker://`` in front of the container
repository and tag. To run the container that's called
``sylabsio/lolcow:latest``:

.. code-block:: none

    $ singularity run docker://sylabsio/lolcow:latest
    INFO:    Converting OCI blobs to SIF format
    INFO:    Starting build...
    Getting image source signatures
    Copying blob 16ec32c2132b done
    Copying blob 5ca731fc36c2 done
    Copying config fd0daa4d89 done
    Writing manifest to image destination
    Storing signatures
    2021/10/04 14:50:21  info unpack layer: sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    2021/10/04 14:50:23  info unpack layer: sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    INFO:    Creating SIF file...
     _____________________________
    < Mon Oct 4 14:50:30 CDT 2021 >
     -----------------------------
	    \   ^__^
	     \  (oo)\_______
		(__)\       )\/\
		    ||----w |
		    ||     ||


Note that {Singularity} retrieves blobs and configuration data from
Docker Hub, extracts the layers that make up the Docker container, and
creates a SIF file from them. This SIF file is kept in your
{Singularity} :ref:`cache directory <sec:cache>`, so if you run the
same Docker container again the downloads and conversion aren't
required.

To obtain the Docker container as a SIF file in a specific location,
which you can move, share, and keep for later, ``singularity pull``
it:

.. code-block:: none

    $ singularity pull docker://sylabsio/lolcow
    INFO:    Using cached SIF image

    $ ls -l lolcow_latest.sif
    -rwxr-xr-x 1 myuser myuser 74993664 Oct  4 14:55 lolcow_latest.sif

If it's the first time you pull the container it'll be downloaded and
translated. If you have pulled the container before, it will be copied
from the cache.

.. note::

   ``singularity pull`` of a Docker container actually runs a
   ``singularity build`` behind the scenes, since we are translating
   from OCI to SIF. If you ``singularity pull`` a Docker container
   twice, the output file isn't identical because metadata such as
   dates from the conversion will vary. This differs from pulling a
   SIF container (e.g. from a ``library://`` URI), which always give
   you an exact copy of the image.


Docker Hub Limits
=================

Docker Hub introduced limits on anonymous access to its API in
November 2020. Every time you use a ``docker://`` URI to run, pull
etc. a container {Singularity} will make requests to Docker Hub in
order to check whether the container has been modified there. On
shared systems, and when running containers in parallel, this can
quickly exhaust the Docker Hub API limits.

We recommend that you ``singularity pull`` a Docker image to a local
SIF, and then always run from the SIF file, rather than using
``singularity run docker://...`` repeatedly.

Alternatively, if you have signed up for a Docker Hub account, make
sure that you authenticate before using ``docker://`` container URIs.

Authentication / Private Containers
===================================

To make use of the API limits under a Docker Hub account, or to access
private containers, you'll need to authenticate to Docker Hub. There
are a number of ways to do this with {Singularity}.

Singularity CLI Remote Command
------------------------------

The ``singularity remote login`` command supports logging into Docker
Hub and other OCI registries. For Docker Hub, the registry hostname is
``docker.io``, so you will need to login as below, specifying your
username:

.. code-block::

    $ singularity remote login --username myuser docker://docker.io
    Password / Token:
    INFO:    Token stored in /home/myuser/.singularity/remote.yaml

The Password / Token you enter must be a Docker Hub CLI access token,
which you should generate in the 'Security' section of your account
profile page on Docker Hub.

To check which Docker / OCI registries you are currently logged in to,
use ``singularity remote list``.

To logout of a registry, so that your credentials are forgotten, use
``singularity remote logout``:

.. code-block::

   $ singularity remote logout docker://docker.io
   INFO:    Logout succeeded

Docker CLI Authentication
-------------------------

If you have the ``docker`` CLI installed on your machine, you can
``docker login`` to your account. This stores authentication
information in ``~/.docker/config.json``. The process that
{Singularity} uses to retrieve Docker / OCI containers will attempt to
use this information to login.

.. note::

   {Singularity} can only read credentials stored directly in
   ``~/.docker/config.json``. It cannot read credentials from external
   Docker credential helpers.

Interactive Login
-----------------

To perform a one-off interactive login, which will not store your
credentials, use the ``--docker-login`` flag:

.. code-block::

   $ singularity pull --docker-login docker://sylabsio/private
   Enter Docker Username: myuser
   Enter Docker Password:

Environment Variables
---------------------

When calling {Singularity} in a CI/CD workflow, or other
non-interactive scenario, it may be useful to specify Docker Hub login
credentials using environment variables. These are often the default
way of passing secrets into jobs within CI pipelines.

Singularity accepts a username, and password / token, as
``SINGULARITY_DOCKER_USERNAME`` and ``SINGULARITY_DOCKER_PASSWORD``
respectively. These environment variables will override any stored
credentials.

.. code-block::

   $ export SINGULARITY_DOCKER_USERNAME=myuser
   $ export SINGULARITY_DOCKER_PASSWORD=mytoken
   $ singularity pull docker://sylabsio/private

--------------------------------
Containers From Other Registries
--------------------------------

You can use ``docker://`` URIs with {Singularity} to pull and run
containers from OCI registries other than Docker Hub. To do this,
you'll need to include the hostname or IP address of the registry in
your ``docker://`` URI. Authentication with other registries is
carried out in the same basic manner, but sometimes you'll need to
retrieve your credentials using a specific tool, especially when
working with Cloud Service Provider environments.

Below are specific examples for some common registries. Most other
registries follow a similar pattern for pulling public images, and
authenticating to access private images.

Quay.io
=======

Quay is an OCI container registry used by a large number of projects,
and hosted at ``https://quay.io``. To pull public containers from
Quay, just include the ``quay.io`` hostname in your ``docker://`` URI:

.. code-block::

    $ singularity pull docker://quay.io/bitnami/python:3.7
    INFO:    Converting OCI blobs to SIF format
    INFO:    Starting build...
    ...

    $ singularity run python_3.7.sif
    Python 3.7.12 (default, Sep 24 2021, 11:48:27)
    [GCC 8.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

To pull containers from private repositories you will need to generate
a CLI token in the Quay web interface, then use it to login with
{Singularity}. Use the same methods as described for Docker Hub above:

* Run ``singularity remote login --username myuser docker://quay.io``
  to store your credentials for {Singularity}.

* Use ``docker login quay.io`` if ``docker`` is on your machine.

* Use the ``--docker-login`` flag for a one-time interactive login.

* Set the ``SINGULARITY_DOCKER_USERNAME`` and
  ``SINGULARITY_DOCKER_PASSWORD`` environment variables.


NVIDIA NGC
==========

The NVIDIA NGC catalog at https://ngc.nvidia.com contains various GPU
software, packaged in containers. Many of these containers are
specifically documented by NVIDIA as supported by {Singularity}, with
instructions available.

Previously, an account and API token was required to pull NGC
containers. However, they are now available to pull as a guest without
login:

.. code-block::

   $ singularity pull docker://nvcr.io/nvidia/pytorch:21.09-py3
   INFO:    Converting OCI blobs to SIF format
   INFO:    Starting build...

If you do need to pull containers using an NVIDIA account, e.g. if you
have access to an NGC Private Registry, you will need to generate an
API key in the web interface in order to authenticate.

Use one of the following authentication methods (detailed above for
Docker Hub), with the username ``$oauthtoken`` and the password set to
your NGC API key.

* Run ``singularity remote login --username \$oauthtoken
  docker://nvcr.io`` to store your credentials for {Singularity}.

* Use ``docker login nvcr.io`` if ``docker`` is on your machine.

* Use the ``--docker-login`` flag for a one-time interactive login.

* Set the ``SINGULARITY_DOCKER_USERNAME="\$oauthtoken"`` and
  ``SINGULARITY_DOCKER_PASSWORD`` environment variables.

See also: https://docs.nvidia.com/ngc/ngc-private-registry-user-guide/index.html


GitHub Container Registry
=========================

GitHub Container Registry is increasingly used to provide Docker
containers alongside the source code of hosted projects. You can pull
a public container from GitHub Container Registry using a ``ghcr.io``
URI:

.. code-block::

   $ singularity pull docker://ghcr.io/containerd/alpine:latest
   INFO:    Converting OCI blobs to SIF format
   INFO:    Starting build...


To pull private containers from GHCR you will need to generate a
personal access token in the GitHub web interface in order to
authenticate. This token must have required scopes. See
`the GitHub documentation here. <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`__

Use one of the following authentication methods (detailed above for
Docker Hub), with your username and personal access token:

* Run ``singularity remote login --username myuser docker://ghcr.io`` to store your
  credentials for {Singularity}.

* Use ``docker login ghcr.io`` if ``docker`` is on your machine.

* Use the ``--docker-login`` flag for a one-time interactive login.

* Set the ``SINGULARITY_DOCKER_USERNAME`` and
  ``SINGULARITY_DOCKER_PASSWORD`` environment variables.

AWS ECR
=======

To work with an AWS hosted Elastic Container Registry (ECR) generally
requires authentication. There are various ways to generate
credentials. You should follow one of the approaches in
`the ECR guide <https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html>`__
in order to obtain a username and password.

.. warning::

    The ECR Docker credential helper cannot be used, as {Singularity}
    does not currently support external credential helpers used with
    Docker, only reading credentials stored directly in the
    ``.docker/config.json`` file.

The ``get-login-password`` approach is the most straightforward. It
uses the AWS CLI to request a password, which can then be used to
authenticate to an ECR private registry in the specified region. The
username used in conjunction with this password is always ``AWS``.

.. code-block:: none

    $ aws ecr get-login-password --region region

Then login using one of the following methods:

* Run ``singularity remote login --username AWS
  docker://<accountid>.dkr.ecr.<region>.amazonaws.com`` to store your
  credentials for {Singularity}.

* Use ``docker login --username AWS
  <accountid>.dkr.ecr.<region>.amazonaws.com`` if ``docker`` is on
  your machine.

* Use the ``--docker-login`` flag for a one-time interactive login.

* Set the ``SINGULARITY_DOCKER_USERNAME=AWS`` and
  ``SINGULARITY_DOCKER_PASSWORD`` environment variables.

You should now be able to pull containers from your ECR URI at
``docker://<accountid>.dkr.ecr.<region>.amazonaws.com``.


Azure ACR
=========

An Azure hosted Azure Container Registry (ACR) will generally hold
private images and require authentication to pull from. There are
several ways to authenticate to ACR, depending on the account type you
use in Azure. See the
`ACR documentation <https://docs.microsoft.com/en-us/azure/container-registry/container-registry-authentication?tabs=azure-cli>`__
for more information on these options.

Generally, for identities, using ``az acr login`` from the Azure
CLI will add credentials to ``.docker/config.json`` which can be read
by {Singularity}.

Service Principle accounts will have an explicit username and
password, and you should authenticate using one of the following
methods:

* Run ``singularity remote login --username myuser
  docker://myregistry.azurecr.io`` to store your credentials for
  {Singularity}.

* Use ``docker login --username myuser myregistry.azurecr.io`` if
  ``docker`` is on your machine.

* Use the ``--docker-login`` flag for a one-time interactive login.

* Set the ``SINGULARITY_DOCKER_USERNAME`` and
  ``SINGULARITY_DOCKER_PASSWORD`` environment variables.

The recent repository-scoped access token preview may be more
convenient. See the
`preview documentation <https://docs.microsoft.com/en-us/azure/container-registry/container-registry-repository-scoped-permissions>`__
which details how to use ``az acr token create`` to obtain a token
name and password pair that can be used to authenticate with the above
methods.

-------------------------------------
Building From Docker / OCI Containers
-------------------------------------

If you wish to use an existing Docker or OCI container as the basis
for a new container, you will need to specifiy it as the *bootstrap*
source in a {Singularity} definition file.

Just as you can run or pull containers from different registries using
a ``docker://`` URI, you can use different headers in a definition file
to instruct {Singularity} where to find the container you want to use
as the starting point for your build.


Registries In Definition Files
==============================

When you wish to build from a Docker or OCI container that's hosted in
a registry, such as Docker Hub, your definition file should begin with
``Bootstrap: docker``, followed with a ``From:`` line which specifies
the location of the container you wish to pull.

Docker Hub
----------

Docker Hub is the default registry, so when building from Docker Hub
the ``From:`` header only needs to specify the container respository
and tag:

.. code-block:: singularity

    Bootstrap: docker
    From: ubuntu:20.04

If you ``singularity build`` a definition file with these lines,
{Singularity} will fetch the ``ubuntu:20.04`` container image from
Docker Hub, and extract it as the basis for your new container.

Other Registries
----------------

To pull from a different Docker registry, you can either specify the
hostname in the ``From:`` header, or use the separate ``Registry:``
header. The following two examples are equivalent:


.. code-block:: singularity

    Bootstrap: docker
    From: quay.io/bitnami/python:3.7

.. code-block:: singularity

   Bootstrap: docker
   Registry: quay.io
   From: bitnami/python:3.7


Authentication During a Build
-----------------------------

If you are building from an image in a private registry you will need
to ensure that the credentials needed to access the image are
available to {Singularity}.

A build might be run as the ``root`` user, e.g. via ``sudo``, or under
your own account with ``--fakeroot``.

If you are running the build as ``root``, using ``sudo``, then any
stored credentials or environment variables must be available to the
``root`` user:

* Use the ``--docker-login`` flag for a one-time interactive
  login. I.E. run ``sudo singularity build --docker-login myimage.sif
  Singularity``.

* Set the ``SINGULARITY_DOCKER_USERNAME`` and
  ``SINGULARITY_DOCKER_PASSWORD`` environment variables. Pass the
  environment variables through sudo to the ``root`` build process by
  running ``sudo -E singularity build ...``.

* Run ``sudo singularity remote login ...`` to store your credentials
  for the ``root`` user on your system. This is separate from storing
  the credentials under your own account.

* Use ``sudo docker login`` if ``docker`` is on your
  machine. This is separate from storing the credentials under your
  own account.

If you are running the build under your account via the ``--fakeroot``
feature you do not need to specially set credentials for the root
user.


Archives & Docker Daemon
========================

As well as being hosted in a registry, Docker / OCI containers might
be found inside a running Docker daemon, or saved as an
archive. {Singularity} can build from these locations by using
specialised bootstrap agents.

Containers Cached by the Docker Daemon
--------------------------------------

If you have pulled or run a container on your machine under
``docker``, it will be cached locally by the Docker daemon. The
``docker images`` command will list containers that are available:

.. code-block:: none

    $ docker images
    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    sylabsio/lolcow     latest              5a15b484bc65        2 hours ago         188MB

This indicates that ``sylabsio/lolcow:latest`` has been cached locally
by Docker. You can directly build it into a SIF file using a
``docker-daemon://`` URI specifying the ``REPOSITORY:TAG`` container
name:

.. code-block:: none

    $ singularity build lolcow_from_docker_cache.sif docker-daemon://sylabsio/lolcow:latest
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:a2022691bf950a72f9d2d84d557183cb9eee07c065a76485f1695784855c5193
     119.83 MiB / 119.83 MiB [==================================================] 6s
    Copying blob sha256:ae620432889d2553535199dbdd8ba5a264ce85fcdcd5a430974d81fc27c02b45
     15.50 KiB / 15.50 KiB [====================================================] 0s
    Copying blob sha256:c561538251751e3685c7c6e7479d488745455ad7f84e842019dcb452c7b6fecc
     14.50 KiB / 14.50 KiB [====================================================] 0s
    Copying blob sha256:f96e6b25195f1b36ad02598b5d4381e41997c93ce6170cab1b81d9c68c514db0
     5.50 KiB / 5.50 KiB [======================================================] 0s
    Copying blob sha256:7f7a065d245a6501a782bf674f4d7e9d0a62fa6bd212edbf1f17bad0d5cd0bfc
     3.00 KiB / 3.00 KiB [======================================================] 0s
    Copying blob sha256:70ca7d49f8e9c44705431e3dade0636a2156300ae646ff4f09c904c138728839
     116.56 MiB / 116.56 MiB [==================================================] 6s
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: lolcow_from_docker_cache.sif

The tag name must be included in the URI. Unlike when pulling from a
registry, the ``docker-daemon`` bootstrap agent will not try to pull a
``latest`` tag automatically.


.. note::

   In the example above, the build was performed without
   ``sudo``. This is possible only when the user is part of the
   ``docker`` group on the host, since {Singularity} must contact the
   Docker daemon through its socket. If you are not part of the
   ``docker`` group you will need to use ``sudo`` for the build to
   complete successfully.

To build from an image cached by the Docker daemon in a definition
file use ``Bootstrap: docker-daemon``, and a ``From:
<REPOSITORY>:TAG`` line:

.. code-block:: singularity

    Bootstrap: docker-daemon
    From: sylabsio/lolcow:latest


Containers in Docker Archive Files
----------------------------------

Docker allows containers to be exported into single file tar
archives. These cannot be run directly, but are intended to be
imported into Docker to run at a later date, or another
location. {Singularity} can build from (or run) these archive files,
by extracting them as part of the build process.

If an image is listed by the ``docker images`` command, then we can
create a tar archive file using ``docker save`` and the image ID:

.. code-block:: none

        $ sudo docker images
        REPOSITORY                        TAG               IMAGE ID       CREATED          SIZE
        sylabsio/lolcow                   latest            5a15b484bc65   2 hours ago      188MB

	$ docker save 5a15b484bc65 -o lolcow.tar

If we examine the contents of the tar file we can see that it contains
the layers and metadata that make up a Docker container:

.. code-block:: none

    $ tar tvf lolcow.tar
    drwxr-xr-x  0 0      0           0 Aug 16 11:22 2f0514a4c044af1ff4f47a46e14b6d46143044522fcd7a9901124209d16d6171/
    -rw-r--r--  0 0      0           3 Aug 16 11:22 2f0514a4c044af1ff4f47a46e14b6d46143044522fcd7a9901124209d16d6171/VERSION
    -rw-r--r--  0 0      0         401 Aug 16 11:22 2f0514a4c044af1ff4f47a46e14b6d46143044522fcd7a9901124209d16d6171/json
    -rw-r--r--  0 0      0    75156480 Aug 16 11:22 2f0514a4c044af1ff4f47a46e14b6d46143044522fcd7a9901124209d16d6171/layer.tar
    -rw-r--r--  0 0      0        1499 Aug 16 11:22 5a15b484bc657d2b418f2c20628c29945ec19f1a0c019d004eaf0ca1db9f952b.json
    drwxr-xr-x  0 0      0           0 Aug 16 11:22 af7e389ea6636873dbc5adc17826e8401d96d3d384135b2f9fe990865af202ab/
    -rw-r--r--  0 0      0           3 Aug 16 11:22 af7e389ea6636873dbc5adc17826e8401d96d3d384135b2f9fe990865af202ab/VERSION
    -rw-r--r--  0 0      0         946 Aug 16 11:22 af7e389ea6636873dbc5adc17826e8401d96d3d384135b2f9fe990865af202ab/json
    -rw-r--r--  0 0      0   118356480 Aug 16 11:22 af7e389ea6636873dbc5adc17826e8401d96d3d384135b2f9fe990865af202ab/layer.tar
    -rw-r--r--  0 0      0         266 Dec 31  1969 manifest.json


We can convert this tar file into a singularity container using the
``docker-archive`` bootstrap agent. Because the agent accesses a file,
rather than an object hosted by a service, it uses ``:<filename>``,
not ``://<location>``. To build a tar archive directly to a SIF
container:

.. code-block:: none

    $ singularity build lolcow_tar.sif docker-archive:lolcow.tar
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:2f0514a4c044af1ff4f47a46e14b6d46143044522fcd7a9901124209d16d6171
     119.83 MiB / 119.83 MiB [==================================================] 6s
    Copying blob sha256:af7e389ea6636873dbc5adc17826e8401d96d3d384135b2f9fe990865af202ab
     15.50 KiB / 15.50 KiB [====================================================] 0s
    Copying config sha256:5a15b484bc657d2b418f2c20628c29945ec19f1a0c019d004eaf0ca1db9f952b
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: lolcow_tar.sif


.. note::

    The ``docker-archive`` bootstrap agent can also handle gzipped Docker
    archives (``.tar.gz`` or ``.tgz`` files).


To build an image using a definition file, which starts from a
container in a Docker archive, use ``Bootstrap: docker-archive`` and
specify the filename in the ``From:`` line:

.. code-block:: singularity

    Bootstrap: docker-archive
    From: lolcow.tar

.. _sec:optional_headers_def_files:

-------------------------------------
Differences and Limitations vs Docker
-------------------------------------

Though Docker / OCI container compatibility is a goal of
{Singularity}, there are some differences and limitations due to the
way {Singularity} was designed to work well on shared systems and HPC
clusters. If you are having difficulty running a specific Docker
container, check through the list of differences below. There are
workarounds for many of the issues that you are most likely to face.

Read-only by Default
====================

{Singularity}'s container image format (SIF) is generally
read-only. This permits containers to be run in parallel from a shared
location on a network filesystem, support in-built signing and
verification, and offer encryption. A container's filesystem is
mounted directly from the SIF, as SquashFS, so cannot be written to by
default.

When a container is run using Docker its layers are extracted, and the
resulting container filesystem can be written to and modified by
default. If a Docker container expects to write files, you will need
to follow one of the following methods to allow it to run under
{Singularity}.

* A directory from the host can be passed into the container with the
  ``--bind`` or ``--mount`` flags. It needs to be mounted inside the
  container at the location where files will be written.

* The ``--writable-tmpfs`` flag can be used to allow files to be
  created in a special temporary overlay. Any changes are lost when
  the container exits. The SIF file is never modified.

* The container can be converted to a sandbox directory, and executed
  with the ``--writable`` flag, which allows modification of the
  sandbox content.

* A writable overlay partition can be added to the SIF file, and the container
  executed with the ``--writable`` flag. Any changes made are kept
  permanently in the overlay partition.

Of these methods, only ``--writable-tmpfs`` is always safe to run in
parallel. Each time the container is executed, a separate temporary
overlay is used and then discarded.

Binding a directory into a container, or running a writable sandbox
may or may not be safe, depending on the program executed. The program
must use, and the filesystem support, some type of locking in order
that the parallel runs do not interfere.

A writable overlay file in a SIF partition cannot be used in
parallel. {Singularity} will refuse to run concurrently using the same
SIF writable overlay partition.

Dockerfile ``USER``
===================

The ``Dockerfile`` used to build a Docker container may contain a
``USER`` statement. This tells the container runtime that it should
run the container under the specified user account.

Because {Singularity} is designed to provide easy and safe access to
data on the host system, work under batch schedulers, etc., it does
not permit changing the user account the container is run as.

Any ``USER`` statement in a ``Dockerfile`` will be ignored by
{Singularity} when the container is run. In practice, this often does
not affect the execution of the software in the container. Software
that is written in a way that requires execution under a specific user
account will generally require modification for use with {Singularity}.

{Singularity}'s ``--fakeroot`` mode will start a container as a fake
``root`` user, mapped to the user's real account outside of the
container. Inside the container it is possible to change to another
user account, which is mapped to a configured range of sub-uids / gids
belonging to the original user. It may be possible to execute software
expecting a fixed user account manually inside a ``--fakeroot`` shell,
if your adminstrator has configured the system for ``--fakeroot``.

Default Mounts / $HOME
======================

A default installation of {Singularity} will mount the user's home
directory, ``/tmp`` directory, and the current working directory, into
each container that is run. Administrators may also configure e.g. HPC
project directories to automatically bind mount. Docker does not mount
host directories into the container by default.

The home directory mount is the most likely to cause problems when
running Docker containers. Various software will look for packages,
plugins, and configuration files in ``$HOME``. If you have, for
example, installed packages for Python into your home directory (``pip
install --user``) then a Python container may find and attempt to use
them. This can cause conflicts and unexpected behaviour.

If you experience issues, use the ``--contain`` option to stop
{Singularity} automatically binding directories into the
container. You may need to use ``--bind`` or ``--mount`` to then add
back e.g. an HPC project directory that you need access to.

.. code-block::

   # Without --contain, python in the container finds packages
   # in your $HOME directory.
   $ singularity exec docker://python:3.9 pip list
   Package    Version
   ---------- -------
   pip        21.2.4
   rstcheck   3.3.1
   setuptools 57.5.0
   wheel      0.37.0

   # With --contain, python in the container only finds packages
   # installed in the container.
   $ singularity exec --contain docker://python:3.9 pip list
   Package    Version
   ---------- -------
   pip        21.2.4
   setuptools 57.5.0
   wheel      0.37.0


Environment Propagation
=======================

{Singularity} propagates most environment variables set on the host
into the container, by default. Docker does not propagate any host
environment variables into the container. Environment variables may
change the behaviour of software.

To disable automatic propagation of environment variables, the
``--cleanenv / -e`` flag can be specified. When ``--cleanenv`` is
used, only variables on the host that are prefixed with
``SINGULARITYENV_`` are set in the container:

.. code-block:: none

    # Set a host variable
    $ export HOST_VAR=123
    # Set a singularity container environment variable
    $ export "SINGULARITYENV_FORCE_VAR="123"

    $ singularity run library://alpine env | grep VAR
    FORCE_VAR=123
    HOST_VAR=ABC

    $ singularity run --cleanenv library://alpine env | grep VAR
    FORCE_VAR=123

Any environment variables set via an ``ENV`` line in a ``Dockerfile``
will be available when the container is run with {Singularity}.


Namespace & Device Isolation
============================

Because {Singularity} favors an integration over isolation approach it
does not, by default, use all the methods through which a container
can be isolated from the host system. This makes it much easier to run
a {Singularity} container like any other program, while the unique
security model ensures safety. You can access the host's network, GPUs,
and other devices directly. Processes in the container are not
numbered separately from host processes. Hostnames are not changed,
etc.

Most containers are not impacted by the differences in isolation. If
you require more isolation, than {Singularity} provides by default, you
can enable some of the extra namespaces that Docker uses, with flags:

* ``--ipc / -i`` creates a separate IPC (inter process communication)
  namespace, for SystemV IPC objects and POSIX message queues.

* ``--net / -n`` creates a new network namespace, abstracting the container
  networking from the host.

* ``--userns / -u`` runs the container unprivileged, inside a user
  namespace and avoiding setuid setup code. This prevents executing
  SIF images directly. They will be extracted to a directory sandbox.

* ``--uts`` creates a new UTS namespace, which allows a different
  hostname and/or NIS domain for the container.

To limit presentation of devices from the host into the container, use
the ``--contain`` flag. As well as preventing automatic binds of host
directories into the container, ``--contain`` sets up a minimal
``/dev`` directory, rather than binding in the entire host ``/dev``
tree.

.. note::

   When using the ``--nv`` or ``--rocm`` flags, GPU devices are
   present in the container even when ``--contain`` is used.

Init Shim Process
=================

When a {Singularity} container is run using the ``--pid / p`` option,
or started as an instance (which implies ``--pid``), a shim init
process is executed that will run the container payload itself.

The shim process helps to ensure signals are propagated correctly from
the terminal, or batch schedulers etc. when containers are not
designed for interactive use. Because Docker does not provide an init
process by default, some containers have been designed to run their
own init process, which cannot operate under the control of
{Singularity}'s shim.

For example, a container using the ``tini`` init process will produce
warnings when started as an instance, or if run with ``--pid``. To
work around this, use the ``--no-init`` flag to disable the shim:

.. code-block::

    $ singularity run --pid tini_example.sif
    [WARN  tini (2690)] Tini is not running as PID 1 .
    Zombie processes will not be re-parented to Tini, so zombie reaping won't work.
    To fix the problem, run Tini as PID 1.

    $ singularity run --pid --no-init tini_example.sif
    ...
    # NO WARNINGS

-----------------------------
Docker-like ``--compat`` Flag
-----------------------------

If Docker-like behavior is important, {Singularity} can be started
with the ``--compat`` flag. This flag is a convenient short-hand
alternative to using all of:

* ``--containall``
* ``--no-init``
* ``--no-umask``
* ``--writable-tmpfs``

A container run with ``--compat`` has:

* A writable root filesystem, using a temporary overlay where changes
  are discarded at container exit.

* No automatic bind mounts of ``$HOME`` or other directories from the
  host into the container.

* Empty temporary ``$HOME`` and ``/tmp`` directories, the contents of
  which will be discarded at container exit.

* A minimal ``/dev`` tree, that does not expose host devices inside
  the container (except GPUs when used with ``--nv`` or ``--rocm``).

* An clean environment, not including environment variables set on the
  host.

* Its own PID and IPC namespaces.

* No shim init process.

These options will allow most, but not all, Docker / OCI containers to
execute correctly under {Singularity}. The user namespace and network
namespace are not used, as these negate benefits of SIF and direct
access to high performance cluster networks.

--------------------------
CMD / ENTRYPOINT Behaviour
--------------------------

When a container is run using ``docker``, its default behavior depends
on the ``CMD`` and/or ``ENTRYPOINT`` set in the ``Dockerfile`` that
was used to build it, along with any arguments on the command
line. The ``CMD`` and ``ENTRYPOINT`` can also be overridden by flags.

A {Singularity} container has the concept of a *runscript*, which is a
single shell script defining what happens when you ``singularity run``
the container. Because there is no internal concept of ``CMD`` and
``ENTRYPOINT``, {Singularity} must create a runscript from the ``CMD``
and ``ENTRYPOINT`` when converting a Docker container. The behavior of
this script mirrors Docker as closely as possible.

If the Docker container only has an ``ENTRYPOINT`` - that
``ENTRYPOINT`` is run, with any arguments appended:

.. code-block:: none

   # ENTRYPOINT="date"

   # Runs 'date'
   $ singularity run mycontainer.sif
   Wed 06 Oct 2021 02:42:54 PM CDT

   # Runs 'date --utc`
   $ singularity run mycontainer.sif --utc
   Wed 06 Oct 2021 07:44:27 PM UTC

If the Docker container only has a ``CMD`` - the ``CMD`` is run, or is
*replaced* with any arguments:

.. code-block:: none

   # CMD="date"

   # Runs 'date'
   $ singularity run mycontainer.sif
   Wed 06 Oct 2021 02:45:39 PM CDT

   # Runs 'echo hello'
   $ singularity run mycontainer.sif echo hello
   hello

If the Docker container has a ``CMD`` *and* ``ENTRYPOINT``, then we
run ``ENTRYPOINT`` with either ``CMD`` as default arguments, or
replaced with any user supplied arguments:

.. code-block:: none

   # ENTRYPOINT="date"
   # CMD="--utc"

   # Runs 'date --utc'
   $ singularity run mycontainer.sif
   Wed 06 Oct 2021 07:48:43 PM UTC

   # Runs 'date -R'
   $ singularity run mycontainer.sif -R
   Wed, 06 Oct 2021 14:49:07 -0500

There is no flag to override an ``ENTRYPOINT`` set for a Docker
container. Instead, use ``singularity exec`` to run an arbitrary
program inside a container.


.. _sec:best_practices:

-------------------------------------------------------
Best Practices for Docker & {Singularity} Compatibility
-------------------------------------------------------

As detailed previously, {Singularity} can make use of most Docker and
OCI images without issues, or via simple workarounds. In general,
however, there are some best practices that should be applied when
creating Docker / OCI containers that will also be run using
{Singularity}.


    1. **Don't require execution by a specific user**

    Avoid using the ``USER`` instruction in your Docker file, as it is
    ignored by Singularity. Install and configure software inside the
    container so that it can be run by any user.

    2. **Don't install software under /root or in another user's home
       directory**

    Because a Docker container builds and runs as the ``root`` user by
    default, it's tempting to install software into root's home
    directory (``/root``). Permissions on ``/root`` are usually set so
    that it is inaccessible to non-root users. When the container is
    run as another user the software may be inaccessible.

    Software inside another user's home directory,
    e.g. ``/home/myapp``, may be obscured by {Singularity}'s automatic
    mounts onto ``/home``.

    Install software into system-wide locations in the container,
    such as under ``/usr`` or ``/opt`` to avoid these issues.

    3. **Support a read-only filesystem**

    Because of the immutable nature of the SIF format, a container run
    with {Singularity} is read-only by default.

    Try to ensure your container will run with a read-only
    filesystem. If this is not possible, document exactly where the
    container needs to write, so that a user can bind in a writable
    location, or use ``--writable-tmpfs`` as appropriate.

    You can test read-only execution with Docker using ``docker
    run --read-only --tmpfs /run --tmpfs /tmp sylabsio/lolcow``.

    4. **Be careful writing to /tmp**

    {Singularity} mounts the *host* ``/tmp`` into the container, by
    default. This means you must be be careful when writing sensitive
    information to ``/tmp``, and should ensure your container cleans
    up files it writes there.

    5. **Consider library caches / ldconfig**

    If your ``Dockerfile`` adds libraries and / or manipulates the ld
    search path in the container (``ld.so.conf`` / ``ld.so.conf.d``),
    you should ensure the library cache is updated during the build.

    Because Singularity runs containers read-only by default, the
    cache and any missing library symlinks may not be able to be
    updated / created at execution time.

    Run ``ldconfig`` toward the *end* of your ``Dockerfile`` to ensure
    symbolic links and the the ``ld.so.cache`` are up-to-date.


.. _sec:troubleshooting:

---------------
Troubleshooting
---------------

Registry Authentication Issues
==============================

If you experience problems pulling containers from a private registry,
check your credentials carefully. You can ``singularity pull`` with
the ``--docker-login`` flag to perform an interactive login. This may
be useful if you are unsure whether you have stored credentials
properly via ``singularity remote login`` or ``docker login``.

OCI registries expect different values for username and password
fields. Some require a token to be generated and used instead of your
account password. Some take a generic username, and rely only on the
token to identify you. Consult the documentation for your registry
carefully. Look for instructions that detail how to login via ``docker
login`` without external helper programs, if possible.

Container Doesn't Start
=======================

If a Docker container fails to start, the most common cause is that it
needs to write files, while {Singularity} runs read-only by default.

Try running with the ``--writable-tmpfs`` option, or the ``--compat``
flag (which enables additional compatibility fixes).

You can also look for error messages mentioning 'permission denied' or
'read-only filesystem'. Note where the program is attempting to write,
and use ``--bind`` or ``--mount`` to bind a directory from the host
system into that location. This will allow the container to write the
needed files, which will appear in the directory you bind in.

Unexpected Container Behaviour
==============================

If a Docker container runs, but exhibits unexpected behavior, the most
likely cause is the different level of isolation that Singularity
provides vs Docker.

Try running the container with the ``--contain`` option, or the
``--compat`` option (which is more strict). This disables the
automatic mount of your home directory, which is a common source of
issues where software in the container loads configuration or packages
that may be present there.

Getting Help
============

The community Slack channels and mailing list are excellent places to
ask for help with running a specific Docker container. Other users may
have already had success running the same container or
software. Please don't report issues with specific Docker containers
on GitHub, unless you believe they are due to a bug in {Singularity}.


.. _sec:deffile-vs-dockerfile:

--------------------------------------------
{Singularity} Definition file vs. Dockerfile
--------------------------------------------

An alternative to running Docker containers with {Singularity} is to
re-write the ``Dockerfile`` as a definition file, and build a native
SIF image.

The table below gives a quick reference comparing Dockerfile and
{Singularity} definition files. For more detail please see :ref:`definition-files`.

================ =========================== ================ =============================
{Singularity} Definition file                Dockerfile
-------------------------------------------- ----------------------------------------------
Section          Description                 Section          Description
================ =========================== ================ =============================
``Bootstrap``    | Defines the source of
                 | the base image to build
                 | your container from.      \-               | Can only bootstrap
                 | Many bootstrap agents                      | from Docker Hub.
                 | are supported, e.g.
                 | ``library``, ``docker``,
                 | ``http``, ``shub``,
                 | ``yum``, ``debootstrap``.

``From:``        | Specifies the base        ``FROM``         | Creates a layer from
                 | image from which to the                    | the specified docker image.
                 | build the container.

``%setup``       | Run setup commands        \-               | Not supported.
                 | outside of the
                 | container (on the host
                 | system) after the base
                 | image bootstrap.

``%files``       | Copy files from           ``COPY``         | Copy files from
                 | your host to                               | your host to
                 | the container, or                          | the container, or
                 | between build stages.                      | between build stages.

``%environment`` | Declare and set           ``ENV``          | Declare and set
                 | container environment                      | a container environment
                 | variables.                                 | variable.

``%help``        | Provide a help
                 | section for your          \-               | Not supported.
                 | container image.

``%post``        | Commands that will                         | Commands that will
                 | be run at                 ``RUN``          | be run at
                 | build-time.                                | build-time.


``%runscript```  | Commands that will
                 | be run when you           ``ENTRYPOINT``   | Commands / arguments
                 | ``singularity run``       ``CMD``          | that will run in the
                 | the container image.                       | container image.

``%startscript`` | Commands that will
                 | be run when               \-               | Not Applicable.
                 | an instance is started.

``%test``        | Commands that run
                 | at the very end           ``HEALTHCHECK``  | Commands that verify
                 | of the build process                       | the health status of
                 | to validate the                            | the container.
                 | container using
                 | a method of your
                 | choice. (to verify
                 | distribution or
                 | software versions
                 | installed inside
                 | the container)

``%apps``        | Allows you to install
                 | internal modules           \-              | Not supported.
                 | based on the concept
                 | of SCIF-apps.

``%labels``      | Section to add and
                 | define metadata           ``LABEL``        | Declare container
                 | describing your                            | metadata as a
                 | container.                                 | key-value pair.

================ =========================== ================ =============================
