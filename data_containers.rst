.. _sec:data-containers:

###############
Data Containers
###############

*New in {Singularity} 4.2 OCI-Mode.*

********
Overview
********

Workflows in HPC often involve three distinct inputs:

- User data, which needs to be analyzed.
- A software application, which will analyze the user data.
- Reference data, which the software uses to make sense of the user data.

Packaging the software application into an OCI-SIF, with {Singularity} in
OCI-Mode, makes it easy to run and share. User data is also easy to handle with
{Singularity}; simply bind your project directories or files from the HPC system
into the container.

Reference data is a little more complicated, as it tends to be specific to the
software being used and the data being analyzed. Perhaps you are aligning
RNA-Seq data to a reference genome sequence, or passing medical images through a
neural network model. Different reference data might be needed for different
inputs (human vs mouse sequences, CT vs MRI images). Although software is
containerized and ready to go, you will probably have to download reference data
from a 3rd party, assemble, and often pre-process it before it can be used with
the specific program that you need to run.

Putting all the reference data that might ever be needed into the same container
as the software application could simplify things, but could make that container
very large. What if we could easily distribute different sets of reference data
alongside, but separately from the software application? The solution is a data
container.

*************************
Creating a Data Container
*************************

{Singularity} 4.2 introduces the ``data package`` command, to create a data
container OCI-SIF, by 'packaging' files and directories on the host:

.. code::

    $ singularity data package <source file/dir> <data container>

For example, to create a data container from the content of the directory
``mydata/`` on the host:

.. code::

    $ singularity data package mydata mydata.oci.sif
    INFO:    Converting layers to SquashFS

The resulting OCI-SIF file contains the packaged data as a SquashFS image,
stored as an OCI artifact, with associated manifest. This allows it to be pushed / pulled
to and from standard OCI registries.

**********************
Using a Data Container
**********************

.. note::

    OCI-SIF data containers can only be used in OCI-Mode (when running
    containers with ``--oci``).

To use a data container with an application container, the ``--data`` flag is
passed to ``run / shell / exec`` in OCI-Mode. The data flag takes one or more
comma separated ``<data container>:<dest>`` pairs, where ``<data container>`` is
the path to the data container to use, and ``<dest>`` is the path in the
application container at which its content should be made available.

For example, to make the content of the ``mydata.oci.sif`` data container
available under ``/mydata`` in an application container:

.. code::

    $ singularity run --oci --data mydata.oci.sif:/mydata application.oci.sif
    dtrudg-sylabs@mini:~$ ls /mydata/
    bar  foo

You can use more than one data container by specifying the ``--data`` flag
multiple times, or listing comma separated ``<data container>:<dest>`` pairs:

.. code::

    $ singularity run --oci \
        --data mydata.oci.sif:/mydata,otherdata.oci.sif:/otherdata \
        application.oci.sif

Is equivalent to:

.. code::

    $ singularity run --oci \
        --data mydata.oci.sif:/mydata \
        --data otherdata.oci.sif:/otherdata \
        application.oci.sif

************************
Sharing a Data Container
************************

As mentioned above, a data container stores a SquashFS filesystem as an OCI
artifact. This means it can be pushed to, and pulled from, standard OCI
registries alongside application container images.

To push to the container library:

.. code::

    $ singularity push -U mydata.oci.sif library://example/datac/mydata:latest
    WARNING: Skipping container verification
    INFO:    Pushing an OCI-SIF to the library OCI registry. Use `--oci` to pull this image.
    4.0KiB / 4.0KiB [=================================================================] 100 %0s

To pull from the container library:

.. code::

    $ singularity pull --oci mydata.oci.sif library://example/datac/mydata:latest
    WARNING: OCI image doesn't declare a platform. It may not be compatible with this system.
    INFO:    Cleaning up.
    WARNING: integrity: signature not found for object group 1
    WARNING: Skipping container verification

To push to Docker Hub, or a similar OCI registry, :ref:`after authenticating <registry>`:

.. code::

    $ singularity push mydata.oci.sif docker://dctrud/mydata:latest
    4.0KiB / 4.0KiB [=================================================================] 100 %0s
    INFO:    Upload complete

To pull from Docker Hub, or a similar OCI registry:

.. code::

    $ singularity pull --oci docker://dctrud/mydata:latest
    WARNING: OCI image doesn't declare a platform. It may not be compatible with this system.
    INFO:    Using cached OCI-SIF image




















