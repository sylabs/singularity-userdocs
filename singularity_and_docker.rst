.. _singularity-and-docker:


==========================
Support for Docker and OCI
==========================


--------
Overview
--------

Effort has been expended in developing `Docker <https://www.docker.com/>`_ containers. Deconstructed into one or more compressed archives (typically split across multiple segments, or **layers** as they are known in Docker parlance) plus some metadata, images for these containers are built from specifications known as ``Dockerfiles``. The public `Docker Hub <https://hub.docker.com/>`_, as well as various private registries, host images for use as Docker containers. {Singularity} has from the outset emphasized the importance of interoperability with Docker. As a consequence, this section of the {Singularity} User Docs first makes its sole focus interoperabilty with Docker. In so doing, the following topics receive attention here:

    - Application of {Singularity} action commands on ephemeral containers derived from public Docker images

    - Converting public Docker images into {Singularity}'s native format for containerization, namely the Singularity Image Format (SIF)

    - Authenticated application of {Singularity} commands to containers derived from private Docker images

    - Authenticated application of {Singularity} commands to containers derived from private Docker images originating from private registries

    - Building SIF containers for {Singularity} via the command line or definition files from a variety of sources for Docker images and image archives

The second part of this section places emphasis upon {Singularity}'s interoperability with open standards emerging from the `Open Containers Initiative <https://www.opencontainers.org/>`_ (OCI). Specifically, in documenting {Singularity} interoperability as it relates to the OCI Image Specification, the following topics are covered:

    - Compliance with the OCI Image Layout Specification

    - OCI-compliant caching in {Singularity}

    - Acquiring OCI images and image archives via {Singularity}

    - Building SIF containers for {Singularity} via the command line or definition files from a variety of sources for OCI images and image archives

The section closes with a brief enumeration of emerging best practices plus consideration of troubleshooting common issues.


.. _sec:action_commands_prebuilt_public_docker_images:

--------------------------------------------------------
Running action commands on public images from Docker Hub
--------------------------------------------------------

``sylabsio/lolcow`` is a whimsical example of a publicly accessible image hosted via `Docker Hub <https://hub.docker.com/>`_. {Singularity} can execute this image as follows:

.. code-block:: none

    $ singularity run docker://sylabsio/lolcow
    INFO:    Converting OCI blobs to SIF format
    INFO:    Starting build...
    Getting image source signatures
    Copying blob 16ec32c2132b done  
    Copying blob 5ca731fc36c2 done  
    Copying config fd0daa4d89 done  
    Writing manifest to image destination
    Storing signatures
    2021/08/16 13:17:01  info unpack layer: sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    2021/08/16 13:17:02  info unpack layer: sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    INFO:    Creating SIF file...
    ______________________________
    < Mon Aug 16 13:17:11 CDT 2021 >
    ------------------------------
            \   ^__^
            \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

Here ``docker`` is prepended to ensure that the ``run`` command of {Singularity} is instructed to boostrap container creation based upon this Docker image, thus creating a complete URI for {Singularity}. {Singularity} subsequently downloads :ref:`all the OCI blobs that comprise this image <sec:oci_overview>`, and converts them into a *single* SIF file - the native format for {Singularity} containers. Because this image from Docker Hub is cached locally in the ``$HOME/.singularity/cache/oci-tmp/<org.opencontainers.image.ref.name>/lolcow_latest.sif`` directory, where ``<org.opencontainers.image.ref.name>`` will be replaced by the appropriate hash for the container, the image does not need to be downloaded again (from Docker Hub) the next time a {Singularity} ``run`` is executed. In other words, the cached copy is sensibly reused:

.. code-block:: none

    $ singularity run docker://sylabsio/lolcow
    INFO:    Using cached SIF image
    ______________________________
    < Mon Aug 16 13:17:47 CDT 2021 >
    ------------------------------
            \   ^__^
            \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

.. note::

    Image caching is :ref:`documented in detail below <sec:oci_overview>`.

.. note::

    Use is made of the ``$HOME/.singularity`` directory by default to :ref:`cache images <sec:cache>`. To cache images elsewhere, use of the environment variable ``SINGULARITY_CACHEDIR`` can be made.

As the runtime of this container is encapsulated as a single SIF file, it is possible to

.. code-block:: none

    cd /home/vagrant/.singularity/cache/oci-tmp/a692b57abc43035b197b10390ea2c12855d21649f2ea2cc28094d18b93360eeb/

and then execute the SIF file directly:

.. code-block:: none

    ./lolcow_latest.sif
    ______________________________
    < Mon Aug 16 13:17:47 CDT 2021 >
    ------------------------------
            \   ^__^
            \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||

.. note::

    SIF files abstract {Singularity} containers as a single file. As with any executable, a SIF file can be executed directly.

``date | cowsay | lolcat`` is executed by *default* when this container is ``run`` by {Singularity}. {Singularity}'s ``exec`` command allows a different command to be executed; for example:

.. code-block:: none

    $ singularity exec docker://sylabsio/lolcow date
    INFO:    Using cached SIF image
    Mon Aug 16 13:20:11 CDT 2

.. note::

    The *same* cached copy of the ``lolcow`` container is reused here by {Singularity} ``exec``, and immediately below here by ``shell``.

.. note::

    Execution defaults are documented below - see :ref:`Directing Execution <sec:def_files_execution>` and :ref:`Container Metadata <sec:inspect_container_metadata>`.

In addition to non-interactive execution of an image from Docker Hub, {Singularity} provides support for an *interactive* ``shell`` session:

.. code-block:: none

    $ singularity shell docker://sylabsio/lolcow
    INFO:    Using cached SIF image
    Singularity> cat /etc/os-release 
    NAME="Ubuntu"
    VERSION="20.04.2 LTS (Focal Fossa)"
    ID=ubuntu
    ID_LIKE=debian
    PRETTY_NAME="Ubuntu 20.04.2 LTS"
    VERSION_ID="20.04"
    HOME_URL="https://www.ubuntu.com/"
    SUPPORT_URL="https://help.ubuntu.com/"
    BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
    PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
    VERSION_CODENAME=focal
    UBUNTU_CODENAME=focal
    Singularity>

From this it is evident that use is being made of Ubuntu 20.04 *within* this container, whereas the shell *external* to the container is running a more recent release of Ubuntu (not illustrated here).

``inspect`` reveals the metadata for a {Singularity} container encapsulated via SIF; :ref:`Container Metadata <sec:inspect_container_metadata>` is documented below.

.. note::

    ``singularity search [search options...] <search query>`` does *not* support Docker registries like `Docker Hub <https://hub.docker.com/>`_. Use the search box at Docker Hub to locate Docker images. Docker ``pull`` commands, e.g., ``docker pull sylabsio/lolcow``, can be easily translated into the corresponding command for {Singularity}. The Docker ``pull`` command is available under "DETAILS" for a given image on Docker Hub.


.. TODO-ND add content re: singularity capability - possibly a new section

.. TODO-ND add content re: singularity instance - possibly a new section ... review first sushma-98's edits for the running services page


.. _sec:use_prebuilt_public_docker_images:

---------------------------------------------------------
Making use of public images from Docker Hub
---------------------------------------------------------

{Singularity} can make use of public images available from the `Docker Hub <https://hub.docker.com/>`_. By specifying the ``docker://`` URI for an image that has already been located, {Singularity} can ``pull``  it - e.g.:

.. code-block:: none

    $ singularity pull docker://sylabsio/lolcow
    INFO:    Converting OCI blobs to SIF format
    INFO:    Starting build...
    Getting image source signatures
    Copying blob 16ec32c2132b done  
    Copying blob 5ca731fc36c2 done  
    Copying config fd0daa4d89 done  
    Writing manifest to image destination
    Storing signatures
    2021/08/16 13:22:26  info unpack layer: sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    2021/08/16 13:22:27  info unpack layer: sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    INFO:    Creating SIF file

This ``pull`` results in a *local* copy of the Docker image in SIF, the Singularity Image Format:

.. code-block:: none

    $ file lolcow_latest.sif
    lolcow_latest.sif: a /usr/bin/env run-singularity script executable (binary data)

In converting to SIF, individual layers of the Docker image have been *combined* into a single, native file for use by {Singularity}; there is no need to subsequently ``build`` the image for {Singularity}. For example, you can now ``exec``, ``run`` or ``shell`` into the SIF version via {Singularity}, :ref:`as described above <sec:action_commands_prebuilt_public_docker_images>`.

.. _sec:use_prebuilt_public_docker_images_SUB_inspect:

``inspect`` reveals metadata for the container encapsulated via SIF:

.. code-block:: none

    $ singularity inspect lolcow_latest.sif 
    org.label-schema.build-arch: amd64
    org.label-schema.build-date: Monday_16_August_2021_13:22:28_CDT
    org.label-schema.schema-version: 1.0
    org.label-schema.usage.singularity.deffile.bootstrap: docker
    org.label-schema.usage.singularity.deffile.from: sylabsio/lolcow
    org.label-schema.usage.singularity.version: 3.8.1

.. note::

    :ref:`Container Metadata <sec:inspect_container_metadata>` is documented below.

SIF files built from Docker images are *not* crytographically signed:

.. code-block:: none

    $ singularity verify lolcow_latest.sif 
    Verifying image: lolcow_latest.sif
    FATAL:   Failed to verify container: integrity: signature not found for object group 1

The ``sign`` command allows a cryptographic signature to be added. Refer to
:ref:`Signing and Verifying Containers <signNverify>` for details. But caution
should be exercised in signing images from Docker Hub because, unless you build
an image from scratch (OS mirrors) you are probably not really sure about the
complete contents of that image.

.. note::

    ``pull`` is a one-time-only operation that builds a SIF file corresponding to the image retrieved from Docker Hub. Updates to the image on Docker Hub will *not* be reflected in the *local* copy.

In our example ``docker://sylabsio/lolcow``, ``sylabsio`` specifies a Docker Hub user, whereas ``lolcow`` is the name of the repository. Adding the option to specifiy an image tag, the generic version of the URI is ``docker://<user>/<repo-name>[:<tag>]``. `Repositories on Docker Hub <https://docs.docker.com/docker-hub/repos/>`_ provides additional details.


.. _sec:using_prebuilt_private_images:

----------------------------------------------------------
Making use of private images from Docker Hub
----------------------------------------------------------

After successful authentication, {Singularity} can also make use of *private* images available from the `Docker Hub <https://hub.docker.com/>`_. The three means available for authentication follow here. Before describing these means, it is instructive to illustrate the error generated when attempting access a private image *without* credentials:

.. code-block:: none

    $ singularity pull docker://sylabsio/private
    FATAL:   While making image from oci registry: error fetching image to cache: failed to get checksum for docker://sylabsio/private: Error reading manifest latest in docker.io/sylabsio/private: errors:
    denied: requested access to the resource is denied
    unauthorized: authentication require

In this case, the ``private`` repository of user ``sylabsio`` **requires** authentication through specification of a valid username and password.


Authentication via Remote Login
===============================

{Singularity} 3.7 introduces the ability for users to supply credentials on a per
registry basis with the ``remote`` command group. See :ref:`Managing OCI Registries <sec:managing_oci_registries>`
for detailed instructions.

Using this method of authentication will allow you to pull private images
without needing to specify any of the login related environment variables
or flags described below.


.. _sec:authentication_via_docker_login:

Authentication via Interactive Login
====================================

Interactive login is the first of two means provided for authentication with Docker Hub. It is enabled through use of the ``--docker-login`` option of {Singularity}'s ``pull`` command; for example:

.. code-block:: none

    $ singularity pull --docker-login docker://sylabsio/private
    Enter Docker Username: sylabsio
    Enter Docker Password:
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:7b8b6451c85f072fd0d7961c97be3fe6e2f772657d471254f6d52ad9f158a580
    Skipping fetch of repeat blob sha256:ab4d1096d9ba178819a3f71f17add95285b393e96d08c8a6bfc3446355bcdc49
    Skipping fetch of repeat blob sha256:e6797d1788acd741d33f4530106586ffee568be513d47e6e20a4c9bc3858822e
    Skipping fetch of repeat blob sha256:e25c5c290bded5267364aa9f59a18dd22a8b776d7658a41ffabbf691d8104e36
    Skipping fetch of repeat blob sha256:258e068bc5e36969d3ba4b47fd3ca0d392c6de465726994f7432b14b0414d23b
    Copying config sha256:8a8f815257182b770d32dffff7f185013b4041d076e065893f9dd1e89ad8a671
     3.12 KiB / 3.12 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: private_latest.sif

After successful authentication, the private Docker image is pulled and converted to SIF as described above.

.. note::

    For interactive sessions, ``--docker-login`` is *recommended* as use of plain-text passwords in your environment is *avoided*. Encoded authentication data is communicated with Docker Hub via secure HTTP.


.. _sec:authentication_via_environment_variables:

Authentication via Environment Variables
========================================

Environment variables offer an alternative means for authentication with Docker Hub. The **required** exports are as follows:

.. code-block:: none

    export SINGULARITY_DOCKER_USERNAME=sylabsio
    export SINGULARITY_DOCKER_PASSWORD=<redacted>

Of course, the ``<redacted>`` plain-text password needs to be replaced by a valid one to be of practical use.

Based upon these exports, ``$ singularity pull docker://sylabsio/private`` allows for the retrieval of this private image.

.. note::

    This approach for authentication supports both interactive and non-interactive sessions. However, the requirement for a plain-text password assigned to an envrionment variable, is the security compromise for this flexibility.

.. note::

    When specifying passwords, 'special characters' (e.g., ``$``, ``#``, ``.``) need to be 'escaped' to avoid interpretation by the shell.


.. _sec:using_prebuilt_private_images_parivate_registries:

--------------------------------------------------------------
Making use of private images from Private Registries
--------------------------------------------------------------

Authentication is required to access *private* images that reside in Docker Hub. Of course, private images can also reside in **private registries**. Accounting for locations *other* than Docker Hub is easily achieved.

In the complete command line specification

.. code-block:: none

    docker://<registry>/<user>/<repo-name>[:<tag>]

``registry`` defaults to ``index.docker.io``. In other words,

.. code-block:: none

    $ singularity pull docker://sylabsio/lolcow

is functionally equivalent to

.. code-block:: none

    $ singularity pull docker://index.docker.io/sylabsio/lolcow

From the above example, it is evident that

.. code-block:: none

    $ singularity pull docker://nvcr.io/nvidia/pytorch:18.11-py3
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:18d680d616571900d78ee1c8fff0310f2a2afe39c6ed0ba2651ff667af406c3e
    <blob fetching details deleted>
    Skipping fetch of repeat blob sha256:c71aeebc266c779eb4e769c98c935356a930b16d881d7dde4db510a09cfa4222
    Copying config sha256:b77551af8073c85588088ab2a39007d04bc830831ba1eef4127b2d39aaf3a6b1
     21.28 KiB / 21.28 KiB [====================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: pytorch_18.11-py3.sif

will retrieve a specific version of the `PyTorch platform <https://pytorch.org/>`_ for Deep Learning from the NVIDIA GPU Cloud (NGC). Because NGC is a private registry, the above ``pull`` assumes :ref:`authentication via environment variables <sec:authentication_via_environment_variables>` when the blobs that collectively comprise the Docker image have not already been cached locally. In the NGC case, the required environment variable are set as follows:

.. code-block:: none

    export SINGULARITY_DOCKER_USERNAME='$oauthtoken'
    export SINGULARITY_DOCKER_PASSWORD=<redacted>

Upon use, these environment-variable settings allow for authentication with NGC.

.. note::

    ``$oauthtoken`` is to be taken literally - it is not, for example, an environment variable.

    The password provided via these means is actually an API token. This token is generated via your NGC account, and is **required** for use of the service.

    For additional details regarding authentication with NGC, and much more, please consult the NGC `Getting Started <https://docs.nvidia.com/ngc/ngc-getting-started-guide/index.html>`_ documentation.

Alternatively, for purely interactive use, ``--docker-login`` is recommended:

.. code-block:: none

    $ singularity pull --docker-login docker://nvcr.io/nvidia/pytorch:18.11-py3
    Enter Docker Username: $oauthtoken
    Enter Docker Password:
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:18d680d616571900d78ee1c8fff0310f2a2afe39c6ed0ba2651ff667af406c3e
    <blob fetching details deleted>
    Skipping fetch of repeat blob sha256:c71aeebc266c779eb4e769c98c935356a930b16d881d7dde4db510a09cfa4222
    Copying config sha256:b77551af8073c85588088ab2a39007d04bc830831ba1eef4127b2d39aaf3a6b1
    21.28 KiB / 21.28 KiB [====================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: pytorch_18.11-py3.sif

Authentication aside, the outcome of the ``pull`` command is the {Singularity} container ``pytorch_18.11-py3.sif`` - i.e., a locally stored copy, that has been coverted to SIF.


--------------------------------------------------------
Building images for {Singularity} from Docker Registries
--------------------------------------------------------

The ``build`` command is used to **create** {Singularity} containers. Because it is documented extensively :ref:`elsewhere in this manual <build-a-container>`, only specifics relevant to Docker are provided here - namely, working with Docker Hub via :ref:`the {Singularity} command line <sec:singularity_build_cli>` and through :ref:`{Singularity} definition files <sec:singularity_build_def_files>`.


.. _sec:singularity_build_cli:

Working from the {Singularity} Command Line
===========================================

Remotely Hosted Images
----------------------

In the simplest case, ``build`` is functionally equivalent to ``pull``:

.. code-block:: none

    $ singularity build mylolcow_latest.sif docker://sylabsio/lolcow
    INFO:    Starting build...
    Getting image source signatures
    Copying blob 16ec32c2132b skipped: already exists  
    Copying blob 5ca731fc36c2 [--------------------------------------] 0.0b / 0.0b
    Copying config fd0daa4d89 done  
    Writing manifest to image destination
    Storing signatures
    2021/08/16 13:26:42  info unpack layer: sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    2021/08/16 13:26:43  info unpack layer: sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    INFO:    Creating SIF file...
    INFO:    Build complete: mylolcow_latest.sif

This ``build`` results in a *local* copy of the Docker image in SIF, as did ``pull`` :ref:`above <sec:use_prebuilt_public_docker_images>`. Here, ``build`` has named the {Singularity} container ``mylolcow_latest.sif``.

.. note::

     ``docker://sylabsio/lolcow`` is the **target** provided as input for ``build``. Armed with this target, ``build`` applies the appropriate boostrap agent to create the container - in this case, one appropriate for Docker Hub.

In addition to a read-only container image in SIF (**default**), ``build`` allows for the creation of a writable (ch)root *directory* called a **sandbox** for interactive development via the ``--sandbox`` option:

.. code-block:: none

    $ singularity build --sandbox mylolcow_latest_sandbox docker://sylabsio/lolcow
    INFO:    Starting build...
    Getting image source signatures
    Copying blob 16ec32c2132b skipped: already exists  
    Copying blob 5ca731fc36c2 [--------------------------------------] 0.0b / 0.0b
    Copying config fd0daa4d89 done  
    Writing manifest to image destination
    Storing signatures
    2021/08/16 13:27:37  info unpack layer: sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    2021/08/16 13:27:38  info unpack layer: sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    INFO:    Creating sandbox directory...
    INFO:    Build complete: mylolcow_latest_sandbox

After successful execution, the above command results in creation of the ``mylolcow_latest_sandbox`` directory with contents:

.. code-block:: none

    bin  boot  core  dev  environment  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  singularity  srv  sys  tmp  usr  var

The ``build`` command of {Singularity} allows (e.g., development) sandbox containers to be converted into (e.g., production) read-only SIF containers, and vice-versa. Consult the :ref:`Build a container <build-a-container>` documentation for the details.

Implicit in the above command-line interactions is use of public images from Docker Hub. To make use of **private** images from Docker Hub, authentication is required. Available means for authentication were described above. Use of environment variables is functionally equivalent for {Singularity} ``build`` as it is for ``pull``; see :ref:`Authentication via Environment Variables <sec:authentication_via_environment_variables>` above. For purely interactive use, authentication can be added to the ``build`` command as follows:

.. code-block:: none

    singularity build --docker-login my_private.sif docker://sylabsio/private

(Recall that ``docker://sylabsio/private`` is a private image available via Docker Hub.) See :ref:`Authentication via Interactive Login <sec:authentication_via_docker_login>` above regarding use of ``--docker-login``.


Building Containers Remotely
----------------------------

By making use of the `Sylabs Cloud Remote Builder <https://cloud.sylabs.io/builder>`_, it is possible to build SIF containers *remotely* from images hosted at Docker Hub. The Sylabs Cloud Remote Builder is a **service** that can be used from the {Singularity} command line or via its Web interface. Here use of the {Singularity} CLI is emphasized.

Once you have an account for Sylabs Cloud, and have logged in to the portal, select `Remote Builder <https://cloud.sylabs.io/builder>`_. The right-hand side of this page is devoted to use of the {Singularity} CLI. Self-generated API tokens are used to enable authenticated access to the Remote Builder. To create a token, follow the `instructions provided <https://cloud.sylabs.io/auth/tokens>`_. Once the token has been created, run ``singularity remote login`` and paste it at the prompt.

The above token provides *authenticated* use of the Sylabs Cloud Remote Builder when ``--remote`` is *appended* to the {Singularity} ``build`` command. For example, for remotely hosted images:

.. code-block:: none

    $ singularity build --remote lolcow_rb.sif docker://sylabsio/lolcow
    INFO:    Remote "default" added.
    INFO:    Access Token Verified!
    INFO:    Token stored in /root/.singularity/remote.yaml
    INFO:    Remote "default" now in use.
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    Copying blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    Copying blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    Copying blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    Copying blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    Copying blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
    Writing manifest to image destination
    Storing signatures
    2021/08/16 18:28:54  info unpack layer: sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    2021/08/16 18:28:56  info unpack layer: sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    2021/08/16 18:28:56  info unpack layer: sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    2021/08/16 18:28:56  info unpack layer: sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    2021/08/16 18:28:56  info unpack layer: sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    2021/08/16 18:28:56  info unpack layer: sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    INFO:    Creating SIF file...
    INFO:    Build complete: /tmp/image-990604230
    WARNING: Skipping container verification
    88.0MiB / 88.0MiB [========================================] 100 % 65.8 MiB/s 0s

    Library storage: using 136.43 MiB out of unlimited quota
    Container URL: https://cloud.sylabs.io/library/dtrudg-sylabs-2/remote-builds/rb-611aae5f596e300e6bbdda64
    INFO:    Build complete: lolcow_rb.sif


.. note::

    Elevated privileges (e.g., via ``sudo``) are *not* required when use is made of the Sylabs Cloud Remote Builder.

During the build process, progress can be monitored in the Sylabs Cloud portal on the Remote Builder page - as illustrated upon completion by the screenshot below. Once complete, this results in a *local* copy of the SIF file ``lolcow_rb.sif``. From the `Sylabs Cloud {Singularity} Library <https://cloud.sylabs.io/library>`_ it is evident that the 'original' SIF file remains available via this portal.

.. image:: lolcow_sylabsrb.png


.. _sec:mandatory_headers_docker_locally_boostrapped_cli:

Locally Available Images: Cached by Docker
------------------------------------------

{Singularity} containers can be built at the command line from images cached *locally* by Docker. Suppose, for example:

.. code-block:: none

    $ docker images
    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    sylabsio/lolcow     latest              5a15b484bc65        2 hours ago         188MB

This indicates that ``sylabsio/lolcow:latest`` has been cached locally by Docker. Then

.. code-block:: none

    $ sudo singularity build lolcow_from_docker_cache.sif docker-daemon://sylabsio/lolcow:latest
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

results in ``lolcow_from_docker_cache.sif`` for native use by {Singularity}. There are two important differences in syntax evident in the above ``build`` command:

    1. The ``docker`` part of the URI has been appended by ``daemon``. This ensures {Singularity} seek an image locally cached by Docker to boostrap the conversion process to SIF, as opposed to attempting to retrieve an image remotely hosted via Docker Hub.

    2. ``sudo`` is prepended to the ``build`` command for {Singularity}; this is required as the Docker daemon executes as ``root``. However, if the user issuing the ``build`` command is a member of the ``docker`` Linux group, then ``sudo`` need not be prepended.

.. note::

    The image tag, in this case ``latest``, is **required** when bootstrapping creation of a container for {Singularity} from an image locally cached by Docker.

.. note::

    The Sylabs Cloud Remote Builder *does not* interoperate with local Docker daemons; therefore, images cached locally by Docker, *cannot* be used to bootstrap creation of SIF files via the Remote Builder service. Of course, a SIF file could be created locally as detailed above. Then, in a separate, manual step, :ref:`pushed to the Sylabs Cloud {Singularity} Library <sec:pushing_locally_available_images_to_library>`.



.. _sec:mandatory_headers_docker_locally_stored_bootstrap_cli:

Locally Available Images: Stored Archives
------------------------------------------

{Singularity} containers can also be built at the command line from Docker images stored locally as ``tar`` files.

The ``lolcow.tar`` file employed below in this example can be produced by making use of an environment in which Docker is available as follows:

    1. Obtain a local copy of the image from Docker Hub via ``sudo docker pull sylabsio/lolcow``. Issuing the following command confirms that a copy of the desired image is available locally:

    .. code-block:: none

        $ sudo docker images
        REPOSITORY                        TAG               IMAGE ID       CREATED          SIZE
        sylabsio/lolcow                   latest            5a15b484bc65   2 hours ago      188MB

    2. Noting that the image identifier above is ``577c1fe8e6d8``, the required archive can be created by ``docker save 5a15b484bc65 -o lolcow.tar``.

Thus ``lolcow.tar`` is a locally stored archive in the *current* working directory with contents:

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

In other words, it is evident that this 'tarball' is a Docker-format image comprised of multiple layers along with metadata in a JSON manifest.

Through use of the ``docker-archive`` bootstrap agent, a SIF file (``lolcow_tar.sif``) for use by {Singularity} can be created via the following ``build`` command:

.. code-block:: none

    $ singularity build lolcow_tar.sif docker-archive://lolcow.tar
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

There are two important differences in syntax evident in the above ``build`` command:

    1. The ``docker`` part of the URI has been appended by ``archive``. This ensures {Singularity} seek a Docker-format image archive stored locally as ``lolcow.tar`` to boostrap the conversion process to SIF, as opposed to attempting to retrieve an image remotely hosted via Docker Hub.

    2. ``sudo`` is *not* prepended to the ``build`` command for {Singularity}. This is *not* required if the executing user has the appropriate access privileges to the stored file.

.. note::

    The ``docker-archive`` bootstrap agent handles archives (``.tar`` files) as well as compressed archives (``.tar.gz``) when containers are built for {Singularity} via its ``build`` command.

.. note::

    The Sylabs Cloud Remote Builder *does not* interoperate with locally stored Docker-format images; therefore, images cached locally by Docker, *cannot* be used to bootstrap creation of SIF files via the Remote Builder service. Of course, a SIF file could be created locally as detailed above. Then, in a separate, manual step, :ref:`pushed to the Sylabs Cloud {Singularity} Library <sec:pushing_locally_available_images_to_library>`.


.. _sec:pushing_locally_available_images_to_library:

Pushing Locally Available Images to a Library
---------------------------------------------

The outcome of bootstrapping from an image cached locally by Docker, or one stored locally as an archive, is of course a *locally* stored SIF file. As noted above, this is the *only* option available, as the Sylabs Cloud Remote Builder *does not* interoperate with the Docker daemon or locally stored archives in the Docker image format. Once produced, however, it may be desirable to  make the resulting SIF file available through the Sylabs Cloud {Singularity} Library; therefore, the procedure to ``push`` a locally available SIF file to the Library is detailed here.

From the `Sylabs Cloud {Singularity} Library <https://cloud.sylabs.io/library>`_, select ``Create a new Project``. In this first of two steps, the publicly accessible project is created as illustrated below:

.. image:: create_project.png

Because an access token for the cloud service already exists, attention can be focused on the ``push`` command prototyped towards the bottom of the following screenshot:

.. image:: push_prototype.png

In fact, by simply replacing ``image.sif`` with ``lolcow_tar.sif``, the following upload is executed:

.. code-block:: none

    $ singularity push lolcow_tar.sif library://ilumb/default/lolcow_tar
    INFO:    Now uploading lolcow_tar.sif to the library
     87.94 MiB / 87.94 MiB [=============================================================================] 100.00% 1.25 MiB/s 1m10s
    INFO:    Setting tag latest


Finally, from the perspective of the Library, the *hosted* version of the SIF file appears as illustrated below. Directions on how to ``pull`` this file are included from the portal.

.. image:: lolcow_lib_listing.png

.. note::

    The hosted version of the SIF file in the Sylabs Cloud {Singularity} Library is maintainable. In other words, if the image is updated locally, the update can be pushed to the Library and tagged appropriately.


.. _sec:singularity_build_def_files:

Working with Definition Files
=============================

.. _sec:def_file_mandatory_headers_remotely_boostrapped:

Mandatory Header Keywords: Remotely Boostrapped
-----------------------------------------------

Akin to a set of blueprints that explain how to build a custom container, {Singularity} definition files (or "def files") are considered in detail :ref:`elsewhere in this manual <definition-files>`. Therefore, only def file nuances specific to interoperability with Docker receive consideration here.

{Singularity} definition files are comprised of two parts - a **header** plus **sections**.

When working with repositories such as Docker Hub, ``Bootstrap`` and ``From`` are **mandatory** keywords within the header; for example, if the file ``lolcow.def`` has contents

.. code-block:: singularity

    Bootstrap: docker
    From: sylabsio/lolcow

then

.. code-block:: none

    sudo singularity build lolcow.sif lolcow.def

creates a {Singularity} container in SIF by bootstrapping from the public ``sylabsio/lolcow`` image from Docker Hub.

In the above definition file, ``docker`` is one of numerous, possible bootstrap agents; this, and other bootstrap agents receive attention :ref:`in the appendix <build-docker-module>`.

.. TODO-ND remote builder content

Through :ref:`the means for authentication described above <sec:using_prebuilt_private_images>`, definition files permit use of private images hosted via Docker Hub. For example, if the file ``mylolcow.def`` has contents

.. code-block:: singularity

    Bootstrap: docker
    From: ilumb/mylolcow

then

.. code-block:: none

    sudo singularity build --docker-login mylolcow.sif mylolcow.def

creates a {Singularity} container in SIF by bootstrapping from the *private* ``ilumb/mylolcow`` image from Docker Hub after successful :ref:`interactive authentication <sec:authentication_via_docker_login>`.

Alternatively, if :ref:`environment variables have been set as above <sec:authentication_via_environment_variables>`, then

.. code-block:: none

    $ sudo -E singularity build mylolcow.sif mylolcow.def

enables authenticated use of the private image.

.. note::

    The ``-E`` option is required to preserve the user's existing environment variables upon ``sudo`` invocation - a priviledge escalation *required* to create {Singularity} containers via the ``build`` command.


Remotely Bootstrapped and Built Containers
------------------------------------------

Consider again :ref:`the definition file used the outset of the section above <sec:def_file_mandatory_headers_remotely_boostrapped>`:

.. code-block:: singularity

    Bootstrap: docker
    From: sylabsio/lolcow

With two small adjustments to the {Singularity} ``build`` command, the Sylabs Cloud Remote Builder can be utilized:


.. code-block:: none

    $ singularity build --remote lolcow_rb_def.sif lolcow.def
    INFO:    Access Token Verified!
    INFO:    Token stored in /root/.singularity/remote.yaml
    INFO:    Remote "default" now in use.
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    Copying blob sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    Copying config sha256:fd0daa4d897cbb381c3bad481073f53ee667a2216cc24961ca4d661e83e56b4b
    Writing manifest to image destination
    Storing signatures
    2021/08/16 18:34:41  info unpack layer: sha256:16ec32c2132b43494832a05f2b02f7a822479f8250c173d0ab27b3de78b2f058
    2021/08/16 18:34:42  info unpack layer: sha256:5ca731fc36c28789c5ddc3216563e8bfca2ab3ea10347e07554ebba1c953242e
    INFO:    Creating SIF file...
    INFO:    Build complete: /tmp/image-014136319
    WARNING: Skipping container verification
    71.5MiB / 71.5MiB [========================================] 100 % 50.9 MiB/s 0s

    Library storage: using 207.95 MiB out of unlimited quota
    Container URL: https://cloud.sylabs.io/library/dtrudg-sylabs-2/remote-builds/rb-611aafbcd78bf1ce9c2123c4
    INFO:    Build complete: lolcow_rb_def.sif

In the above, ``--remote`` has been added as the ``build`` option that causes use of the Remote Builder service. A much more subtle change, however, is the *absence* of ``sudo`` ahead of ``singularity build``. Though subtle here, this absence is notable, as users can build containers via the Remote Builder with *escalated privileges*; in other words, steps in container creation that *require* ``root`` access *are* enabled via the Remote Builder even for (DevOps) users *without* admninistrative privileges locally.

In addition to the command-line support described above, the Sylabs Cloud Remote Builder also allows definition files to be copied and pasted into its Graphical User Interface (GUI). After pasting a definition file, and having that file validated by the service, the build-centric part of the GUI appears as illustrated below. By clicking on the ``Build`` button, creation of the container is initiated.

.. image:: build_gui.png

Once the build process has been completed, the corresponding SIF file can be retrieved from the service - as shown below. A log file for the ``build`` process is provided by the GUI, and made available for download as a text file (not shown here).

.. image:: build_output.png

A copy of the SIF file created by the service remains in the Sylabs Cloud {Singularity} Library as illustrated below.

.. image:: mysylabslibrary.png

.. note::

    The Sylabs Cloud is currently available as an Alpha Preview. In addition to the {Singularity} Library and Remote Builder, a Keystore service is also available. All three services make use of a *freemium* pricing model in supporting {Singularity} Community Edition. In contrast, all three services are included in SingularityPRO - an enterprise grade subscription for {Singularity} that is offered for a fee from Sylabs. For addtional details regarding the different offerings available for {Singularity}, please `consult the Sylabs website <https://www.sylabs.io/singularity/>`_.


.. _sec:mandatory_headers_docker_locally_boostrapped_def_file:

Mandatory Header Keywords: Locally Boostrapped
----------------------------------------------

When ``docker-daemon`` is the bootstrap agent in a {Singularity} definition file, SIF containers can be created from images cached locally by Docker. Suppose the definition file ``lolcow-d.def`` has contents:

.. code-block:: singularity

    Bootstrap: docker-daemon
    From: sylabsio/lolcow:latest

.. note::

    Again, the image tag ``latest`` is **required** when bootstrapping creation of a container for {Singularity} from an image locally cached by Docker.

Then,

.. code-block:: none

    $ sudo singularity build lolcow_from_docker_cache.sif lolcow-d.def
    Build target already exists. Do you want to overwrite? [N/y] y
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

In other words, this is the definition-file counterpart to :ref:`the command-line invocation provided above <sec:mandatory_headers_docker_locally_boostrapped_cli>`.

.. note::

    The ``sudo`` requirement in the above ``build`` request originates from {Singularity}; it is the standard requirement when use is made of definition files. In other words, membership of the issuing user in the ``docker`` Linux group is of no consequence in this context.

.. TODO-ND remote builder content note - exclusion above

Alternatively when ``docker-archive`` is the bootstrap agent in a {Singularity} definition file, SIF containers can be created from images stored locally by Docker. Suppose the definition file ``lolcow-da.def`` has contents:

.. code-block:: singularity

    Bootstrap: docker-archive
    From: lolcow.tar

Then,

.. code-block:: none

    $ sudo singularity build lolcow_tar_def.sif lolcow-da.def
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
    INFO:    Build complete: lolcow_tar_def.sif

through ``build`` results in the SIF file ``lolcow_tar_def.sif``. In other words, this is the definition-file counterpart to :ref:`the command-line invocation provided above <sec:mandatory_headers_docker_locally_stored_bootstrap_cli>` .

.. TODO-ND RB Test


.. _sec:optional_headers_def_files:

Optional Header Keywords
------------------------

In the two-previous examples, the ``From`` keyword specifies *both* the ``user`` and ``repo-name`` in making use of Docker Hub. *Optional* use of ``Namespace`` permits the more-granular split across two keywords:

.. code-block:: singularity

    Bootstrap: docker
    Namespace: sylabsio
    From: lolcow

.. note::

    In `their documentation <https://docs.docker.com/docker-hub/repos/>`_, "Docker ID namespace" and ``user`` are employed as synonyms in the text and examples, respectively.

.. note::

    The default value for the optional keyword ``Namespace`` is ``library``.


Private Images and Registries
-----------------------------

Thus far, use of Docker Hub has been assumed. To make use of a different repository of Docker images the **optional** ``Registry`` keyword can be added to the {Singularity} definition file. For example, to make use of a Docker image from the NVIDIA GPU Cloud (NGC) corresponding definition file is:

.. code-block:: singularity

    Bootstrap: docker
    From: nvidia/pytorch:18.11-py3
    Registry: nvcr.io

This def file ``ngc_pytorch.def`` can be passed as a specification to ``build`` as follows:

.. code-block:: none

    $ sudo singularity build --docker-login mypytorch.sif ngc_pytorch.def
    Enter Docker Username: $oauthtoken
    Enter Docker Password: <obscured>
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:18d680d616571900d78ee1c8fff0310f2a2afe39c6ed0ba2651ff667af406c3e
     41.34 MiB / 41.34 MiB [====================================================] 2s
    <blob copying details deleted>
    Copying config sha256:b77551af8073c85588088ab2a39007d04bc830831ba1eef4127b2d39aaf3a6b1
    21.28 KiB / 21.28 KiB [====================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: mypytorch.sif

After successful authentication via interactive use of the ``--docker-login`` option, output as the SIF container ``mypytorch.sif`` is (ultimately) produced. As above, :ref:`use of environment variables <sec:authentication_via_environment_variables>` is another option available for authenticating private Docker type repositories such as NGC; once set, the ``build`` command is as above save for the absence of the ``--docker-login`` option.


.. _sec:def_files_execution:

Directing Execution
-------------------

The ``Dockerfile`` corresponding to ``sylabsio/lolcow`` is as follows:

.. code-block:: none

    FROM ubuntu:20.04

    RUN apt-get update && apt-get install -y cowsay lolcat

    ENV PATH /usr/games:${PATH}
    ENV LC_ALL=C

    ENTRYPOINT date | cowsay | lolcat

The execution-specific part of this ``Dockerfile`` is the ``ENTRYPOINT`` - "... an optional definition for the first part of the command to be run ..." according to `the available documentation <https://docs.docker.com/search/?q=ENTRYPOINT>`_. After conversion to SIF, execution of ``date | cowsay | lolcat`` *within* the container produces the output:

.. code-block:: none

    $ ./mylolcow.sif
    ______________________________
    < Mon Aug 16 13:38:45 CDT 2021 >
     ------------------------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
  
In addition, ``CMD`` allows an arbitrary string to be *appended* to the ``ENTRYPOINT``. Thus, multiple commands or flags can be passed together through combined use.

Suppose now that a {Singularity} ``%runscript`` **section** is added to the definition file as follows:

.. code-block:: singularity

    Bootstrap: docker
    Namespace: sylabsio
    From: lolcow

    %runscript

        date

After conversion to SIF via the {Singularity} ``build`` command, exection of the resulting container produces the output:

.. code-block:: none

    $ ./lolcow.sif
    Mon Aug 16 13:39:20 CDT 2021

In other words, introduction of a ``%runscript`` section into the {Singularity} definition file causes the ``ENTRYPOINT`` of the ``Dockerfile`` to be *bypassed*. The presence of the ``%runscript`` section would also bypass a ``CMD`` entry in the ``Dockerfile``.

To *preserve* use of ``ENTRYPOINT`` and/or ``CMD`` as defined in the ``Dockerfile``, the ``%runscript`` section must be *absent* from the {Singularity} definition. In this case, and to favor execution of ``CMD`` *over* ``ENTRYPOINT``, a non-empty assignment of the *optional* ``IncludeCmd`` should be included in the header section of the {Singularity} definition file as follows:

.. code-block:: singularity

    Bootstrap: docker
    Namespace: sylabsio
    From: lolcow
    IncludeCmd: yes

.. note::

    Because only a non-empty ``IncludeCmd`` is required, *either* ``yes`` (as above) or ``no`` results in execution of ``CMD`` *over* ``ENTRYPOINT``.

.. _sec:def_files_execution_SUB_execution_precedence:

To summarize execution precedence:

    1. If present, the ``%runscript`` section of the {Singularity} definition file is executed

    2. If ``IncludeCmd`` is a non-empty keyword entry in the header of the {Singularity} definition file, then ``CMD`` from the ``Dockerfile`` is executed

    3. If present in the ``Dockerfile``, ``ENTRYPOINT`` appended by ``CMD`` (if present) are executed in sequence

    4. Execution of the ``bash`` shell is defaulted to

.. TODO-ND Test CMD vs ENTRYPOINT via a documented example

.. _sec:inspect_container_metadata:

Container Metadata
------------------

{Singularity}'s ``inspect`` command displays container metadata - data about data that is encapsulated *within* a SIF file. Default output (assumed via the ``--labels`` option) from the command was :ref:`illustrated above <sec:use_prebuilt_public_docker_images_SUB_inspect>`. ``inspect``, however, provides a number of options that are :ref:`detailed elsewhere <environment-and-metadata>`; in the remainder of this section, Docker-specific use to establish execution precedence is emphasized.

As stated above (i.e., :ref:`the first case of execution precedence <sec:def_files_execution_SUB_execution_precedence>`), the very existence of a ``%runscript`` section in a {Singularity} definition file *takes precedence* over commands that might exist in the ``Dockerfile``.

When the ``%runscript`` section is *removed* from the {Singularity} definition file, the result is (once again):

.. code-block:: none

    $ singularity inspect --deffile lolcow.sif

    from: lolcow
    bootstrap: docker
    namespace: sylabsio

.. TODO-ND below ... Need to add a CMD to lolcow ...

The runscript 'inherited' from the ``Dockerfile`` is:

.. code-block:: none

    #!/bin/sh
    OCI_ENTRYPOINT='"/bin/sh" "-c" "date | cowsay | lolcat"'
    OCI_CMD=''
    CMDLINE_ARGS=""
    # prepare command line arguments for evaluation
    for arg in "$@"; do
        CMDLINE_ARGS="${CMDLINE_ARGS} \"$arg\""
    done

    # ENTRYPOINT only - run entrypoint plus args
    if [ -z "$OCI_CMD" ] && [ -n "$OCI_ENTRYPOINT" ]; then
        if [ $# -gt 0 ]; then
            SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT} ${CMDLINE_ARGS}"
        else
            SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT}"
        fi
    fi

    # CMD only - run CMD or override with args
    if [ -n "$OCI_CMD" ] && [ -z "$OCI_ENTRYPOINT" ]; then
        if [ $# -gt 0 ]; then
            SINGULARITY_OCI_RUN="${CMDLINE_ARGS}"
        else
            SINGULARITY_OCI_RUN="${OCI_CMD}"
        fi
    fi

    # ENTRYPOINT and CMD - run ENTRYPOINT with CMD as default args
    # override with user provided args
    if [ $# -gt 0 ]; then
        SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT} ${CMDLINE_ARGS}"
    else
        SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT} ${OCI_CMD}"
    fi

    # Evaluate shell expressions first and set arguments accordingly,
    # then execute final command as first container process
    eval "set ${SINGULARITY_OCI_RUN}"
    exec "$@"

From this Bourne shell script, it is evident that only an ``ENTRYPOINT`` is detailed in the ``Dockerfile``; thus the ``ENTRYPOINT only - run entrypoint plus args`` conditional block is executed. In this case then, :ref:`the third case of execution precedence <sec:def_files_execution_SUB_execution_precedence>` has been illustrated.

The above Bourne shell script also illustrates how the following scenarios will be handled:

    - A ``CMD`` only entry in the ``Dockerfile``

    - **Both** ``ENTRYPOINT`` *and* ``CMD`` entries in the ``Dockerfile``

From this level of detail, use of ``ENTRYPOINT`` *and/or* ``CMD`` in a Dockerfile has been made **explicit**. These remain examples within :ref:`the third case of execution precedence <sec:def_files_execution_SUB_execution_precedence>`.


-----------------
OCI Image Support
-----------------

.. _sec:oci_overview:


Overview
========

OCI is an acronym for the `Open Containers Initiative <https://www.opencontainers.org/>`_ - an independent organization whose mandate is to develop open standards relating to containerization. To date, standardization efforts have focused on container formats and runtimes; it is the former that is emphasized here. Stated simply, an **OCI blob** is content that can be addressed; in other words, *each* layer of a Docker image is rendered as an OCI blob as illustrated in the (revisited) ``pull`` example below.

.. note::

    To facilitate interoperation with Docker Hub, the {Singularity} core makes use of  the ``containers/image`` `library <https://github.com/containers/image/>`_ - "... a set of Go libraries aimed at working in various way[s] with containers' images and container image registries."


Image Pulls Revisited
---------------------

After describing various :ref:`action commands that could be applied to images hosted remotely via Docker Hub <sec:action_commands_prebuilt_public_docker_images>`, the notion of having :ref:`a local copy in {Singularity}'s native format for containerization (SIF) <sec:use_prebuilt_public_docker_images>` was introduced:

.. code-block:: none

    $ singularity pull docker://sylabsio/lolcow
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
     45.33 MiB / 45.33 MiB [====================================================] 1s
    Copying blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
     848 B / 848 B [============================================================] 0s
    Copying blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
     621 B / 621 B [============================================================] 0s
    Copying blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
     853 B / 853 B [============================================================] 0s
    Copying blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
     169 B / 169 B [============================================================] 0s
    Copying blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
     53.75 MiB / 53.75 MiB [====================================================] 2s
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: lolcow_latest.sif

Thus use of {Singularity}'s ``pull`` command results in the *local* file copy in SIF, namely ``lolcow_latest.sif``. Layers of the image from Docker Hub are copied locally as OCI blobs.

.. TODO minor - fix appearance of above link


Image Caching in {Singularity}
------------------------------

If the *same* ``pull`` command is issued a *second* time, the output is different:

.. code-block:: none

    $ singularity pull docker://sylabsio/lolcow
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    Skipping fetch of repeat blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    Skipping fetch of repeat blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    Skipping fetch of repeat blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    Skipping fetch of repeat blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    Skipping fetch of repeat blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: lolcow_latest.sif

As the copy operation has clearly been *skipped*, it is evident that a copy of all OCI blobs **must** be cached locally. Indeed, {Singularity} has made an entry in its local cache as follows:

.. code-block:: none

    $ tree .singularity/
    .singularity/
    └── cache
        └── oci
            ├── blobs
            │   └── sha256
            │       ├── 3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
            │       ├── 73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
            │       ├── 7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
            │       ├── 8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
            │       ├── 9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
            │       ├── 9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
            │       ├── d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
            │       └── f2a852991b0a36a9f3d6b2a33b98a461e9ede8393482f0deb5287afcbae2ce10
            ├── index.json
            └── oci-layout

    4 directories, 10 files

.. _misc:OCI_Image_Layout_Specification:

Compliance with the OCI Image Layout Specification
--------------------------------------------------

From the perspective of the directory ``$HOME/.singularity/cache/oci``, this cache implementation in {Singularity} complies with the `OCI Image Layout Specification <https://github.com/opencontainers/image-spec/blob/master/image-layout.md>`_:

    - ``blobs`` directory - contains content addressable data, that is otherwise considered opaque

    - ``oci-layout`` file - a mandatory JSON object file containing both mandatory and optional content

    - ``index.json`` file - a mandatory JSON object file containing an index of the images

Because one or more images is 'bundled' here, the directory ``$HOME/.singularity/cache/oci`` is referred to as the ``$OCI_BUNDLE_DIR``.

For additional details regarding this specification, consult the `OCI Image Format Specification <https://github.com/opencontainers/image-spec>`_.


OCI Compliance and the {Singularity} Cache
------------------------------------------

As required by the layout specification, OCI blobs are *uniquely* named by their contents:

.. code-block:: none

    $ shasum -a 256 ./blobs/sha256/9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118  ./blobs/sha256/9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118

They are also otherwise opaque:

.. code-block:: none

    $ file ./blobs/sha256/9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118 ./blobs/sha256/9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118: gzip compressed data

The content of the ``oci-layout`` file in this example is:

.. code-block:: javascript

    $ cat oci-layout | jq
    {
      "imageLayoutVersion": "1.0.0"
    }

This is as required for compliance with the layout standard.

.. note::

    In rendering the above JSON object files, use has been made of ``jq`` - the command-line JSON processor.

The index of images in this case is:

.. code-block:: javascript

    $ cat index.json | jq
    {
      "schemaVersion": 2,
      "manifests": [
        {
          "mediaType": "application/vnd.oci.image.manifest.v1+json",
          "digest": "sha256:f2a852991b0a36a9f3d6b2a33b98a461e9ede8393482f0deb5287afcbae2ce10",
          "size": 1125,
          "annotations": {
            "org.opencontainers.image.ref.name": "a692b57abc43035b197b10390ea2c12855d21649f2ea2cc28094d18b93360eeb"
          },
          "platform": {
            "architecture": "amd64",
            "os": "linux"
          }
        }
      ]
    }

The ``digest`` blob in this index file includes the details for all of the blobs that collectively comprise the ``sylabsio/lolcow`` image:

.. code-block:: javascript

    $ cat  ./blobs/sha256/f2a852991b0a36a9f3d6b2a33b98a461e9ede8393482f0deb5287afcbae2ce10 | jq
    {
      "schemaVersion": 2,
      "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "digest": "sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82",
        "size": 3410
      },
      "layers": [
        {
          "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
          "digest": "sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118",
          "size": 47536248
        },
        {
          "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
          "digest": "sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a",
          "size": 848
        },
        {
          "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
          "digest": "sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2",
          "size": 621
        },
        {
          "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
          "digest": "sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e",
          "size": 853
        },
        {
          "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
          "digest": "sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9",
          "size": 169
        },
        {
          "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
          "digest": "sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945",
          "size": 56355961
        }
      ]
    }

The ``digest`` blob referenced in the ``index.json`` file references the following configuration file:

.. code-block:: javascript

    $ cat ./blobs/sha256/73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82 | jq
    {
      "created": "2017-09-21T18:37:47.278336798Z",
      "architecture": "amd64",
      "os": "linux",
      "config": {
        "Env": [
          "PATH=/usr/games:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
          "LC_ALL=C"
        ],
        "Entrypoint": [
          "/bin/sh",
          "-c",
          "fortune | cowsay | lolcat"
        ]
      },
      "rootfs": {
        "type": "layers",
        "diff_ids": [
          "sha256:a2022691bf950a72f9d2d84d557183cb9eee07c065a76485f1695784855c5193",
          "sha256:ae620432889d2553535199dbdd8ba5a264ce85fcdcd5a430974d81fc27c02b45",
          "sha256:c561538251751e3685c7c6e7479d488745455ad7f84e842019dcb452c7b6fecc",
          "sha256:f96e6b25195f1b36ad02598b5d4381e41997c93ce6170cab1b81d9c68c514db0",
          "sha256:7f7a065d245a6501a782bf674f4d7e9d0a62fa6bd212edbf1f17bad0d5cd0bfc",
          "sha256:70ca7d49f8e9c44705431e3dade0636a2156300ae646ff4f09c904c138728839"
        ]
      },
      "history": [
        {
          "created": "2017-09-18T23:31:37.453092323Z",
          "created_by": "/bin/sh -c #(nop) ADD file:5ed435208da6621b45db657dd6549ee132cde58c4b6763920030794c2f31fbc0 in / "
        },
        {
          "created": "2017-09-18T23:31:38.196268404Z",
          "created_by": "/bin/sh -c set -xe \t\t&& echo '#!/bin/sh' > /usr/sbin/policy-rc.d \t&& echo 'exit 101' >> /usr/sbin/policy-rc.d \t&& chmod +x /usr/sbin/policy-rc.d \t\t&& dpkg-divert --local --rename --add /sbin/initctl \t&& cp -a /usr/sbin/policy-rc.d /sbin/initctl \t&& sed -i 's/^exit.*/exit 0/' /sbin/initctl \t\t&& echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup \t\t&& echo 'DPkg::Post-Invoke { \"rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true\"; };' > /etc/apt/apt.conf.d/docker-clean \t&& echo 'APT::Update::Post-Invoke { \"rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true\"; };' >> /etc/apt/apt.conf.d/docker-clean \t&& echo 'Dir::Cache::pkgcache \"\"; Dir::Cache::srcpkgcache \"\";' >> /etc/apt/apt.conf.d/docker-clean \t\t&& echo 'Acquire::Languages \"none\";' > /etc/apt/apt.conf.d/docker-no-languages \t\t&& echo 'Acquire::GzipIndexes \"true\"; Acquire::CompressionTypes::Order:: \"gz\";' > /etc/apt/apt.conf.d/docker-gzip-indexes \t\t&& echo 'Apt::AutoRemove::SuggestsImportant \"false\";' > /etc/apt/apt.conf.d/docker-autoremove-suggests"
        },
        {
          "created": "2017-09-18T23:31:38.788043199Z",
          "created_by": "/bin/sh -c rm -rf /var/lib/apt/lists/*"
        },
        {
          "created": "2017-09-18T23:31:39.411670721Z",
          "created_by": "/bin/sh -c sed -i 's/^#\\s*\\(deb.*universe\\)$/\\1/g' /etc/apt/sources.list"
        },
        {
          "created": "2017-09-18T23:31:40.055188541Z",
          "created_by": "/bin/sh -c mkdir -p /run/systemd && echo 'docker' > /run/systemd/container"
        },
        {
          "created": "2017-09-18T23:31:40.215057796Z",
          "created_by": "/bin/sh -c #(nop)  CMD [\"/bin/bash\"]",
          "empty_layer": true
        },
        {
          "created": "2017-09-21T18:37:46.483638061Z",
          "created_by": "/bin/sh -c apt-get update && apt-get install -y fortune cowsay lolcat"
        },
        {
          "created": "2017-09-21T18:37:47.041333952Z",
          "created_by": "/bin/sh -c #(nop)  ENV PATH=/usr/games:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
          "empty_layer": true
        },
        {
          "created": "2017-09-21T18:37:47.170535967Z",
          "created_by": "/bin/sh -c #(nop)  ENV LC_ALL=C",
          "empty_layer": true
        },
        {
          "created": "2017-09-21T18:37:47.278336798Z",
          "created_by": "/bin/sh -c #(nop)  ENTRYPOINT [\"/bin/sh\" \"-c\" \"fortune | cowsay | lolcat\"]",
          "empty_layer": true
        }
      ]
    }

.. TODO Is the above not the config.json file referred to at https://github.com/opencontainers/runtime-spec/blob/master/config.md ???

Even when all OCI blobs are already in {Singularity}'s local cache, repeated image pulls cause *both* these last-two JSON object files, as well as the ``oci-layout`` and ``index.json`` files, to be updated.


Building Containers for {Singularity} from OCI Images
=====================================================

.. _cli-oci-bootstrap-agent:

Working Locally from the {Singularity} Command Line: ``oci`` Boostrap Agent
---------------------------------------------------------------------------

The example detailed in the previous section can be used to illustrate how a SIF file for use by {Singularity} can be created from the local cache - an albeit contrived example, that works because the {Singularity} cache is compliant with the OCI Image Layout Specification.

.. note::

    Of course, the ``oci`` bootstrap agent can be applied to *any* **bundle** that is compliant with the OCI Image Layout Specification - not *just* the {Singularity} cache, as created by executing a {Singularity} ``pull`` command.

In this local case, the ``build`` command of {Singularity} makes use of the ``oci`` boostrap agent as follows:

.. code-block:: none

    $ singularity build ~/lolcow_oci_cache.sif oci://$HOME/.singularity/cache/oci:a692b57abc43035b197b10390ea2c12855d21649f2ea2cc28094d18b93360eeb
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    Skipping fetch of repeat blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    Skipping fetch of repeat blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    Skipping fetch of repeat blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    Skipping fetch of repeat blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    Skipping fetch of repeat blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: /home/vagrant/lolcow_oci_cache.sif

As can be seen, this results in the SIF file ``lolcow_oci_cache.sif`` in the user's home directory.

The syntax for the ``oci`` boostrap agent requires some elaboration, however. In this case, and as illustrated above, ``$HOME/.singularity/cache/oci`` has content:

.. code-block:: none

    $ ls
    blobs  index.json  oci-layout


In other words, it is the ``$OCI_BUNDLE_DIR`` containing the data and metadata that collectively comprise the image layed out in accordance with the OCI Image Layout Specification :ref:`as discussed previously <misc:OCI_Image_Layout_Specification>` - the same data and metadata that are assembled into a single SIF file through the ``build`` process. However,

.. code-block:: none

    $ singularity build ~/lolcow_oci_cache.sif oci://$HOME/.singularity/cache/oci
    INFO:    Starting build...
    FATAL:   While performing build: conveyor failed to get: more than one image in oci, choose an image

does not *uniquely* specify an image from which to bootstrap the ``build`` process. In other words, there are multiple images referenced via ``org.opencontainers.image.ref.name`` in the ``index.json`` file. By appending ``:a692b57abc43035b197b10390ea2c12855d21649f2ea2cc28094d18b93360eeb`` to ``oci`` in this example, the image is uniquely specified, and the container created in SIF (as illustrated previously).

.. note::

    Executing the {Singularity} ``pull`` command multiple times on the same image produces multiple ``org.opencontainers.image.ref.name`` entries in the ``index.json`` file. Appending the value of the unique ``org.opencontainers.image.ref.name`` allows for use of the ``oci`` boostrap agent.


.. _cli-oci-archive-bootstrap-agent:

Working Locally from the {Singularity} Command Line: ``oci-archive`` Boostrap Agent
-----------------------------------------------------------------------------------

OCI archives, i.e., ``tar`` files obeying the OCI Image Layout Specification :ref:`as discussed previously <misc:OCI_Image_Layout_Specification>`, can seed creation of a container for {Singularity}. In this case, use is made of the ``oci-archive`` bootstrap agent.

To illustrate this agent, it is convenient to build the archive from the {Singularity} cache. After a single ``pull`` of the ``sylabsio/lolcow`` image from Docker Hub, a ``tar`` format archive can be generated from the ``$HOME/.singularity/cache/oci`` directory as follows:

.. code-block:: none

    $ tar cvf $HOME/sylabsio.tar *
    blobs/
    blobs/sha256/
    blobs/sha256/73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
    blobs/sha256/8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    blobs/sha256/9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    blobs/sha256/3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    blobs/sha256/9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    blobs/sha256/d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    blobs/sha256/f2a852991b0a36a9f3d6b2a33b98a461e9ede8393482f0deb5287afcbae2ce10
    blobs/sha256/7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    index.json
    oci-layout

The native container ``lolcow_oci_tarfile.sif`` for use by {Singularity} can be created by issuing the ``build`` command as follows:

.. code-block:: none

    $ singularity build lolcow_oci_tarfile.sif oci-archive://sylabsio.tar
    Build target already exists. Do you want to overwrite? [N/y] y
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    Skipping fetch of repeat blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    Skipping fetch of repeat blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    Skipping fetch of repeat blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    Skipping fetch of repeat blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    Skipping fetch of repeat blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: lolcow_oci_tarfile.sif

This assumes that the ``tar`` file exists in the current working directory.

.. note::

    Cache maintenance is a manual process at the current time. In other words, the cache can be cleared by **carefully** issuing the command ``rm -rf $HOME/.singularity/cache``. Of course, this will clear the local cache of all downloaded images.

.. TODO-ND: Update owing to intro of new capab???

.. note::

    Because the layers of a Docker image as well as the blobs of an OCI image are already ``gzip`` compressed, there is a minimal advantage to having compressed archives representing OCI images. For this reason, the ``build`` detailed above boostraps a SIF file for use by {Singularity} from only a ``tar`` file, and not a ``tar.gz`` file.


Working from the {Singularity} Command Line with Remotely Hosted Images
-----------------------------------------------------------------------

In the previous section, an OCI archive was created from locally available OCI blobs and metadata; the resulting ``tar`` file served to bootstrap the creation of a container for {Singularity} in SIF via the ``oci-archive`` agent. Typically, however, OCI archives of interest are remotely hosted. Consider, for example, an Alpine Linux OCI archive stored in Amazon S3 storage. Because such an archive can be retrieved via secure HTTP, the following ``pull`` command results in a local copy as follows:

.. code-block:: none

    $ singularity pull https://s3.amazonaws.com/singularity-ci-public/alpine-oci-archive.tar
     1.98 MiB / 1.98 MiB [==================================================================================] 100.00% 7.48 MiB/s 0s

Thus ``https`` (and ``http``) are additional bootstrap agents available to seed development of containers for {Singularity}.

It is worth noting that the OCI image specfication compliant contents of this archive are:

.. code-block:: none

    $ tar tvf alpine-oci-archive.tar
    drwxr-xr-x 1000/1000         0 2018-06-25 14:45 blobs/
    drwxr-xr-x 1000/1000         0 2018-06-25 14:45 blobs/sha256/
    -rw-r--r-- 1000/1000       585 2018-06-25 14:45 blobs/sha256/b1a7f144ece0194921befe57ab30ed1fd98c5950db7996719429020986092058
    -rw-r--r-- 1000/1000       348 2018-06-25 14:45 blobs/sha256/d0ff39a54244ba25ac7447f19941765bee97b05f37ceb438a72e80c9ed39854a
    -rw-r--r-- 1000/1000   2065537 2018-06-25 14:45 blobs/sha256/ff3a5c916c92643ff77519ffa742d3ec61b7f591b6b7504599d95a4a41134e28
    -rw-r--r-- 1000/1000       296 2018-06-25 14:45 index.json
    -rw-r--r-- 1000/1000        31 2018-06-25 14:45 oci-layout

Proceeding as before, for a (now) locally available OCI archive, a SIF file can be produced by executing:

.. code-block:: none

    $ singularity build alpine_oci_archive.sif oci-archive://alpine-oci-archive.tar
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:ff3a5c916c92643ff77519ffa742d3ec61b7f591b6b7504599d95a4a41134e28
     1.97 MiB / 1.97 MiB [======================================================] 0s
    Copying config sha256:b1a7f144ece0194921befe57ab30ed1fd98c5950db7996719429020986092058
     585 B / 585 B [============================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: alpine_oci_archive.sif

The resulting SIF file can be validated as follows, for example:

.. code-block:: none

    $ ./alpine_oci_archive.sif
    Singularity> cat /etc/os-release
    NAME="Alpine Linux"
    ID=alpine
    VERSION_ID=3.7.0
    PRETTY_NAME="Alpine Linux v3.7"
    HOME_URL="http://alpinelinux.org"
    BUG_REPORT_URL="http://bugs.alpinelinux.org"
    Singularity>
    $

.. note::


    The ``http`` and ``https`` bootstrap agents can only be used to ``pull`` OCI archives from where they are hosted.

    In working with remotely hosted OCI image archives then, a two-step workflow is *required* to produce SIF files for native use by {Singularity}:

        1. Transfer of the image to local storage via the ``https`` (or ``http``) bootstrap agent. The {Singularity} ``pull`` command achieves this.

        2. Creation of a SIF file via the ``oci-archive`` bootstrap agent. The {Singularity} ``build`` command achieves this.

Established with nothing more than a Web server then, any individual, group or organization, *could* host OCI archives. This might be particularly appealing, for example, for organizations having security requirements that preclude access to public registries such as Docker Hub. Other that having a very basic hosting capability, OCI archives need only comply to the OCI Image Layout Specification :ref:`as discussed previously <misc:OCI_Image_Layout_Specification>`.


Working with Definition Files: Mandatory Header Keywords
--------------------------------------------------------

Three, new bootstrap agents have been introduced as a consequence of compliance with the OCI Image Specification - assuming ``http`` and ``https`` are considered together. In addition to bootstrapping images for {Singularity} completely from the command line, definition files can be employed.

As :ref:`above <cli-oci-bootstrap-agent>`, the OCI image layout compliant {Singularity} cache can be employed to create SIF containers; the definition file, ``lolcow-oci.def``, equivalent is:


.. code-block:: singularity

    Bootstrap: oci
    From: .singularity/cache/oci:a692b57abc43035b197b10390ea2c12855d21649f2ea2cc28094d18b93360eeb

Recall that the colon-appended string in this file uniquely specifies the ``org.opencontainers.image.ref.name`` of the desired image, as more than one possibility exists in the ``index.json`` file. The corresponding ``build`` command is:

.. code-block:: none

    $ sudo singularity build ~/lolcow_oci_cache.sif lolcow-oci.def
    WARNING: Authentication token file not found : Only pulls of public images will succeed
    Build target already exists. Do you want to overwrite? [N/y] y
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
     45.33 MiB / 45.33 MiB [====================================================] 0s
    Copying blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
     848 B / 848 B [============================================================] 0s
    Copying blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
     621 B / 621 B [============================================================] 0s
    Copying blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
     853 B / 853 B [============================================================] 0s
    Copying blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
     169 B / 169 B [============================================================] 0s
    Copying blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
     53.75 MiB / 53.75 MiB [====================================================] 0s
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: /home/vagrant/lolcow_oci_cache.sif

Required use of ``sudo`` allows {Singularity} to ``build`` the SIF container ``lolcow_oci_cache.sif``.

When it comes to OCI archives, the definition file, ``lolcow-ocia.def`` corresponding to the command-line invocation above is:

.. code-block:: singularity

    Bootstrap: oci-archive
    From: sylabsio.tar

Applying ``build`` as follows

.. code-block:: none

    $ sudo singularity build lolcow_oci_tarfile.sif lolcow-ocia.def
    WARNING: Authentication token file not found : Only pulls of public images will succeed
    INFO:    Starting build...
    Getting image source signatures
    Skipping fetch of repeat blob sha256:9fb6c798fa41e509b58bccc5c29654c3ff4648b608f5daa67c1aab6a7d02c118
    Skipping fetch of repeat blob sha256:3b61febd4aefe982e0cb9c696d415137384d1a01052b50a85aae46439e15e49a
    Skipping fetch of repeat blob sha256:9d99b9777eb02b8943c0e72d7a7baec5c782f8fd976825c9d3fb48b3101aacc2
    Skipping fetch of repeat blob sha256:d010c8cf75d7eb5d2504d5ffa0d19696e8d745a457dd8d28ec6dd41d3763617e
    Skipping fetch of repeat blob sha256:7fac07fb303e0589b9c23e6f49d5dc1ff9d6f3c8c88cabe768b430bdb47f03a9
    Skipping fetch of repeat blob sha256:8e860504ff1ee5dc7953672d128ce1e4aa4d8e3716eb39fe710b849c64b20945
    Copying config sha256:73d5b1025fbfa138f2cacf45bbf3f61f7de891559fa25b28ab365c7d9c3cbd82
     3.33 KiB / 3.33 KiB [======================================================] 0s
    Writing manifest to image destination
    Storing signatures
    INFO:    Creating SIF file...
    INFO:    Build complete: lolcow_oci_tarfile.sif

results in the SIF container ``lolcow_oci_tarfile.sif``.


Working with Definition Files: Additonal Considerations
-------------------------------------------------------

In working with definition files, the following additional considerations arise:

    - In addition to the mandatory header keywords documented above, :ref:`optional header keywords <sec:optional_headers_def_files>` are possible additions to OCI bundle and/or archive bootstrap definition files.

    - As distribution of OCI bundles and/or archives is out of the Initiative's scope, so is the authentication required to access private images and/or registries.

    - The direction of execution follows along the same lines :ref:`as described above <sec:def_files_execution>`. Of course, the SIF container's metadata will make clear the ``runscript`` through application of the ``inspect`` command :ref:`as described previously <sec:inspect_container_metadata>`.

    - Container metadata will also reveal whether or not a given SIF file was bootstrapped from an OCI bundle or archive; for example, below it is evident that an OCI archive was employed to bootstrap creation of the SIF file:

.. code-block:: javascript

    $ singularity inspect --labels lolcow_oci_tarfile.sif | jq
    {
      "org.label-schema.build-date": "Sunday_27_January_2019_0:5:29_UTC",
      "org.label-schema.schema-version": "1.0",
      "org.label-schema.usage.singularity.deffile.bootstrap": "oci-archive",
      "org.label-schema.usage.singularity.deffile.from": "sylabsio.tar",
      "org.label-schema.usage.singularity.version": "3.0.3-1"
    }


.. _sec:docker_cache:

-----------------
Container Caching
-----------------

To avoid fetching duplicate docker or OCI layers every time you want to ``run``, ``exec`` etc. a ``docker://`` or ``oci://`` container directly, {Singularity} keeps a cache of layer files. The SIF format container that {Singularity} creates from these layers is also cached. This means that re-running a docker container, e.g. ``singularity run docker://alpine`` is much faster until the upstream image changes in docker hub, and a new SIF must be built from updated layers.

By default the cache directory is ``.singularity/cache`` in your ``$HOME`` directory. You can modify the cache directory by setting the ``SINGULARITY_CACHEDIR`` environment variable. To disable caching altogether, set the ``SINGULARITY_DISABLE_CACHE`` environment variable.

The ``singularity cache`` command can be used to see the content of your cache dir, and clean the cache if needed:

.. code-block:: none
                
    $ singularity cache list
    There are 10 container file(s) using 4.75 GB and 78 oci blob file(s) using 5.03 GB of space
    Total space used: 9.78 GB

    $ singularity cache clean
    This will delete everything in your cache (containers from all sources and OCI blobs). 
    Hint: You can see exactly what would be deleted by canceling and using the --dry-run option.
    Do you want to continue? [N/y] y
    Removing /home/dave/.singularity/cache/library
    Removing /home/dave/.singularity/cache/oci-tmp
    Removing /home/dave/.singularity/cache/shub
    Removing /home/dave/.singularity/cache/oci
    Removing /home/dave/.singularity/cache/net
    Removing /home/dave/.singularity/cache/oras

For a more complete guide to caching and the ``cache`` command, see the :ref:`build-environment` page.

    
.. _sec:best_practices:

--------------
Best Practices
--------------

{Singularity} can make use of most Docker and OCI images without complication. However, there exist  known cases where complications can arise. Thus a brief compilation of best practices follows below.

    1. Accounting for trust

    Docker containers *allow for* privilege escalation. In a ``Dockerfile``, for example, the ``USER`` instruction allows for user and/or group settings to be made in the Linux operating environment. The trust model in {Singularity} is completely different: {Singularity} allows untrusted users to run untrusted containers in a trusted way. Because {Singularity} containers embodied as SIF files execute in *user* space, there is no possibility for privilege escalation. In other words, those familiar with Docker, should *not* expect access to elevated user permissions; and as a corollary, use of the ``USER`` instruction must be *avoided*.

    {Singularity} does, however, allow for fine-grained control over the permissions that containers require for execution. Given that Singularilty executes in user space, it is not surprising that permissions need to be externally established *for* the container through use of the ``capability`` command. :ref:`Detailed elsewhere in this documentation <security-options>`, {Singularity} allows users and/or groups to be granted/revoked authorized capabilties. Owing to {Singularity}'s trust model, this fundamental best practice can be stated as follows:

        "Employ ``singularity capability`` to manage execution privileges for containers"


    2. Maintaining containers built from Docker and OCI images

    SIF files created by boostrapping from Docker or OCI images are, of course, only as current as the most recent {Singularity} ``pull``. Subsequent retrievals *may* result in containers that are built and/or behave differently, owing to changes in the corresponding ``Dockerfile``. A prudent practice then, for maintaining containers of value, is based upon use of {Singularity} definition files. Styled and implemented after a ``Dockerfile`` retrieved at some point in time, use of ``diff`` on subsequent versions of this same file, can be employed to inform maintenance of the corresponding {Singularity} definition file. Understanding build specifications at this level of detail places container creators in a much more sensible position prior to signing with an encrypted key. Thus the best practice is:

        "Maintain detailed build specifications for containers, rather than opaque runtimes"

    3. Working with environment variables

    In a ``Dockerfile``, `environment variables are declared <https://docs.docker.com/engine/reference/builder/#env>`_ as key-value pairs through use of the ``ENV`` instruction. Declaration in the build specification for a container is advised, rather than relying upon user
    (e.g., ``.bashrc``, ``.profile``) or system-wide configuration files for interactive shells. Should a ``Dockerfile`` be converted into a definition file for {Singularity}, as suggested in the container-maintenance best practice above, :ref:`environment variables can be explicitly represented <definition-files>` as ``ENV`` instructions that have been converted into entries in the ``%environment`` section, respectively. This best practice can be stated as follows:


    "Define environment variables in container specifications, not interactive shells"


    4. Installation to ``/root``

    Docker and OCI container's are typically run as the ``root`` user; therefore, ``/root`` (this user's ``$HOME`` directory) will be the installation target when ``$HOME`` is specified. Installation to ``/root`` may prove workable in some circumstances - e.g., while the container is executing, or if read-only access is required to this directory after installation. In general, however, because this is the ``root`` directory conventional wisdom suggests this practice be avoided. Thus the best practice is:

        "Avoid installations that make use of ``/root``."

    5. Read-only ``/`` filesystem

    {Singularity} mounts a container's ``/`` filesystem in read-only mode. To ensure a Docker container meets {Singularity}'s requirements, it may prove useful to execute ``docker run --read-only --tmpfs /run --tmpfs /tmp sylabsio/lolcow``. The best practioce here is:

        "Ensure Docker containers meet {Singularity}'s read-only ``/`` filesystem requirement"

    6. Installation to ``$HOME`` or ``$TMP``

    In making use of {Singularity}, it is common practice for ``$USER`` to be automatically mounted on ``$HOME``, and for ``$TMP`` also to be mounted. To avoid the side effects (e.g., 'missing' or conflicting files) that might arise as a consequence of executing ``mount`` commands then, the best practice is:

        "Avoid placing container 'valuables' in ``$HOME`` or ``$TMP``."

    A detailed review of the container's build specification (e.g., its ``Dockerfile``) may be required to ensure this best practice is adhered to.

    7. Current library caches

    Irrespective of containers, `a common runtime error <https://codeyarns.com/2014/01/14/how-to-fix-shared-object-file-error/>`_ stems from failing to locate shared libraries required for execution. Suppose now there exists a requirement for symbolically linked libraries *within* a {Singularity} container. If the builld process that creates the container fails to update the cache, then it is quite likely that (read-only) execution of this container will result in the common error of missing libraries. Upon investigation, it is likely revealed that the library exists, just not the required symbolic links. Thus the best practice is:

        "Ensure calls to ``ldconfig`` are executed towards the *end* of ``build`` specifications (e.g., ``Dockerfile``), so that the library cache is updated when the container is created."

    8. Use of plain-text passwords for authentication

    For obvious reasons, it is desireable to completely *avoid* use of plain-text passwords. Therefore, for interactive sessions requiring authentication, use of the ``--docker-login`` option for {Singularity}'s ``pull`` and ``build`` commands is *recommended*. At the present time, the *only* option available for non-interactive use is to :ref:`embed plain-text passwords into environment variables <sec:authentication_via_environment_variables>`. Because the Sylabs Cloud {Singularity} Library employs `time-limited API tokens for authentication <https://cloud.sylabs.io/auth>`_, use of SIF containers hosted through this service provides a more secure means for both interactive *and* non-interactive use. This best practice is:

        "Avoid use of plain-text passwords"

    9. Execution ambiguity

    Short of converting an *entire* ``Dockerfile`` into a {Singularity} definition file, informed specification of the ``%runscript`` entry in the def file *removes* any ambiguity associated with ``ENTRYPOINT`` :ref:`versus <sec:def_files_execution>` ``CMD`` and ultimately :ref:`execution precedence <sec:def_files_execution>`. Thus the best practice is:

        "Employ {Singularity}'s ``%runscript`` by default to avoid execution ambiguity"

    Note that the ``ENTRYPOINT`` can be bypassed completely, e.g., ``docker run -i -t --entrypoint /bin/bash sylabsio/lolcow``. This allows for an interactive session within the container, that may prove useful in validating the built runtime.

Best practices emerge from experience. Contributions that allow additional experiences to be shared as best practices are always encouraged. Please refer to :ref:`Contributing <contributing>` for additional details.


.. _sec:troubleshooting:

---------------
Troubleshooting
---------------

In making use of Docker and OCI images through {Singularity} the need to troubleshoot may arise. A brief compilation of issues and their resolution is provided here.

    1. Authentication issues

    Authentication is required to make use of Docker-style private images and/or private registries. Examples involving private images hosted by the public Docker Hub were :ref:`provided above <sec:using_prebuilt_private_images>`, whereas the NVIDIA GPU Cloud was used to :ref:`illustrate access to a private registry <sec:using_prebuilt_private_images_parivate_registries>`. Even if the intended use of containers is non-interactive, issues in authenticating with these image-hosting services are most easily addressed through use of the ``--docker-login`` option that can be appended to a {Singularity} ``pull`` request. As soon as image signatures and blobs start being received, authentication credentials have been validated, and the image ``pull`` can be cancelled.

    2. Execution mismatches

    Execution intentions are detailed through specification files - i.e., the ``Dockerfile`` in the case of Docker images. However, intentions and precedence aside, the reality of executing a container may not align with expectations. To alleviate this mismatch, use of ``singularity inspect --runscript <somecontainer>.sif`` details the *effective* runscript - i.e., the one that is actually being executed. Of course, the ultimate solution to this issue is to develop and maintain {Singularity} definition files for containers of interest.

    3. More than one image in the OCI bundle directory

    :ref:`As illustrated above <cli-oci-bootstrap-agent>`, and with respect to the bootstrap agent ``oci://$OCI_BUNDLE_DIR``, a fatal error is generated when *more* than one image is referenced in the ``$OCI_BUNDLE_DIR/index.json`` file. The workaround shared previously was to append the bootstrap directive with the unique reference name for the image of interest - i.e., ``oci://$OCI_BUNDLE_DIR:org.opencontainers.image.ref.name``. Because it may take some effort to locate the reference name for an image of interest, an even simpler solution is to ensure that each ``$OCI_BUNDLE_DIR`` contains at most a single image.

    4. Cache maintenance

    Maintenance of the {Singularity} cache (i.e., ``$HOME/.singularity/cache``) requires manual intervention at this time. By **carefully** issuing the command ``rm -rf $HOME/.singularity/cache``, its local cache will be cleared of all downloaded images.

    5. The ``http`` and ``https`` are ``pull`` only boostrap agents

    ``http`` and ``https`` are the only examples of ``pull`` only boostrap agents. In other words, when used with {Singularity}'s ``pull`` command, the result is a local copy of, for example, an OCI archive image. This means that a subsequent step is necessary to actually create a SIF container for use by {Singularity} - a step involving the ``oci-archive`` bootstrap agent in the case of an OCI image archive.

Like :ref:`best practices <sec:best_practices>`, troubleshooting scenarios and solutions emerge from experience. Contributions that allow additional experiences to be shared  are always encouraged. Please refer to :ref:`Contributing <contributing>` for additional details.

.. TODO-ND SIFtool - does it have more to offer here???

.. _sec:deffile-vs-dockerfile:

--------------------------------------------
{Singularity} Definition file vs. Dockerfile
--------------------------------------------

On the following table, you can see which are the similarities/differences between a Dockerfile and a {Singularity} definition file:

================ ========================== ================ =============================
{Singularity} Definition file                 Dockerfile
------------------------------------------- ----------------------------------------------
Section          Description                Section          Description
================ ========================== ================ =============================
``Bootstrap``    | Defines from which
                 | library to build
                 | your container from.      \-              | Can only bootstrap
                 | You are free to choose                    | from Docker Hub.
                 | between ``library``
                 | (Our cloud library)
                 | , ``docker`` , ``shub``
                 | and ``oras``.

``From:``        | To specify the provider   ``FROM``        | Creates a layer from
                 | from which to build the                   | the described docker image.
                 | container.                                | For example, if you got a
                                                             | Dockerfile with the ``FROM``
                                                             | section set like:
                                                             | ``FROM:ubuntu:18.04``,
                                                             | this means that a layer
                                                             | will be created from the
                                                             | ``ubuntu:18.04``
                                                             | **Docker** image.
                                                             | (You cannot choose any
                                                             | other bootstrap provider)

``%setup``       | Commands that run        \-               | Not supported.
                 | outside the
                 | container (in the host
                 | system) after the base
                 | OS has been installed.

``%files``       | To copy files from
                 | your local               ``COPY``         | To copy files from your
                 | to the host.                              | Docker's client current
                                                             | directory.

``%environment`` | To declare and set       ``ENV``          | ``ENV`` will take the name
                 | your environment                          | of the variable and the
                 | variables.                                | value and set it.

``%help``        | To provide a help
                 | section to your          \-               | Not supported on the
                 | container image.                          | Dockerfile.

``%post``        | Commands that will
                 | be run at                ``RUN``          | Commands to build your
                 | build-time.                               | application image
                                                             | with ``make``

``%runscript```  | Commands that will
                 | be run at                ``CMD``          | Commands that run
                 | running your                              | within the Docker
                 | container image.                          | container.

``%startscript`` | Commands that will
                 | be run when                \-             | Not supported.
                 | an instance is started.
                 | This is useful for
                 | container images
                 | using services.

``%test``        | Commands that run
                 | at the very end          ``HEALTHCHECK``  | Commands that verify
                 | of the build process                      | the health status of
                 | to validate the                           | the container.
                 | container using
                 | a method of your
                 | choice. (to verify
                 | distribution or
                 | software versions
                 | installed inside
                 | the container)

``%apps``        | Allows you to install
                 | internal modules           \-             | Not supported.
                 | based on the concept
                 | of SCIF-apps.

``%labels``      | Section to add and
                 | define metadata          ``LABEL``        | Section to declare
                 | within your container.                    | metadata as a
                                                             | key-value pair.

================ ========================== ================ =============================

.. TODO-ND SIFtool - does it have more to offer here???
