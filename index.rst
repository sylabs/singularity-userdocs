##########################
 {Singularity} User Guide
##########################

Welcome to the {Singularity} User Guide!

This guide aims to give an introduction to {Singularity}, brief
installation instructions, and cover topics relevant to users building
and running containers.

For a detailed guide to installation and configuration, please see the
separate Admin Guide for this version of {Singularity} at
https://sylabs.io/guides/{adminversion}/admin-guide/.

******************************************
 Getting Started & Background Information
******************************************

.. toctree::
   :maxdepth: 2

   Introduction to {Singularity} <introduction>
   Quick Start <quick_start>
   Security in {Singularity} <security>

*********************
 Building Containers
*********************

Learn how to write a definition file that can be used to build a
container. Understand the environment within a build, how to perform
remote builds, and how to use the ``--fakeroot`` feature to build as a
non-root user.

.. toctree::
   :maxdepth: 1

   Build a container <build_a_container>
   The Definition File <definition_files>
   Build Environment <build_env>
   Fakeroot feature <fakeroot>

********************************
 Container Signing & Encryption
********************************

{Singularity} allows containers to be signed using a PGP key. The
signature travels with the container image, allowing you to verify that
the image is unmodified at any time. Encryption of containers using
LUKS2 is also supported. Encrypted containers can be run without
decrypting them to disk first.

.. toctree::
   :maxdepth: 1

   Sign and Verify <signNverify>
   Key management commands <key_commands>
   Encrypted Containers <encryption>

***************************
 Sharing & Online Services
***************************

Sylabs offers a suite of container services, with a free tier and
on-premise options. Learn how to make use these services to simplify the
process of building, signing, and sharing your containers.

.. toctree::
   :maxdepth: 1

   Remote Endpoints <endpoint>
   Sylabs Cloud Library <cloud_library>

****************
 Advanced Usage
****************

Once you've understood the basics, explore all the options which
{Singularity} provides for accessing data, running persistent services
in containers, manipulating the container environment, and applying
networking and security configuration.

.. toctree::
   :maxdepth: 1

   Bind Paths and Mounts <bind_paths_and_mounts>
   Persistent Overlays <persistent_overlays>
   Running Services <running_services>
   Environment and Metadata <environment_and_metadata>
   Plugins <plugins>
   Security Options <security_options>
   Network Options <networking>
   Cgroups Support <cgroups>

***************
 Compatibility
***************

{Singularity} has unique benefits and supports easy access to GPUs and
other hardware. It also strives for compatibility with Docker/OCI
container formats. Understand the differences between {Singularity} and
Docker, as well as how to use containerized MPI and GPU applications.

.. toctree::
   :maxdepth: 1

   Support for Docker / OCI Containers <singularity_and_docker>
   OCI Runtime Support <oci_runtime>
   Singularity and MPI applications <mpi>
   GPU Support <gpu>

**************
 Get Involved
**************

We'd love you to get involved in the {Singularity} community! Whether
through contributing feature and fixes, helping to answer questions from
other users, or simply testing new releases.

.. toctree::
   :maxdepth: 1

   Contributing <contributing>

***********
 Reference
***********

.. toctree::
   :maxdepth: 2

   Appendix <appendix>

.. toctree::
   :maxdepth: 1

   Command Line Reference <cli>
   License <license>
