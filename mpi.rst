.. _mpi:

==================================
{Singularity} and MPI applications
==================================

.. _sec-mpi:

The `Message Passing Interface (MPI) <https://mpi-forum.org>`_
is a standard extensively used by HPC applications to implement various communication
across compute nodes of a single system or across compute platforms.
There are two main open-source implementations of MPI at the
moment - `OpenMPI <https://www.open-mpi.org/>`_ and `MPICH <https://www.mpich.org/>`_,
both of which are supported by {Singularity}. The goal of this page is to
demonstrate the development and running of MPI programs using {Singularity} containers.

There are several ways of carrying this out, the most popular way of
executing MPI applications installed in a {Singularity} container is to rely on the
MPI implementation available on the host. This is called the *Host MPI* or
the *Hybrid* model since both the MPI implementations provided by system
administrators (on the host) and in the containers will be used.

Another approach is to only use the MPI implementation available on the host and
not include any MPI in the container. This is called the *Bind* model since it
requires to bind/mount the MPI version available on the host into the container.

.. note::

    The *bind* model requires users to be able to mount user-specified
    files from the host into the container. This ability is sometimes
    disabled by system administrators for operational reasons. If this
    is the case on your system please follow the *hybrid* approach.

------------
Hybrid model
------------

The basic idea behind the *Hybrid Approach* is when you execute a {Singularity}
container with MPI code, you will call ``mpiexec`` or a similar launcher on the
``singularity`` command itself. The MPI process outside of the container will
then work in tandem with MPI inside the container and the containerized MPI code
to instantiate the job.

The Open MPI/{Singularity} workflow in detail:

1. The MPI launcher (e.g., ``mpirun``, ``mpiexec``) is called by the resource manager or the user directly from a shell.
2. Open MPI then calls the process management daemon (ORTED).
3. The ORTED process launches the {Singularity} container requested by the launcher command.
4. {Singularity} instantiates the container and namespace environment.
5. {Singularity} then launches the MPI application within the container.
6. The MPI application launches and loads the Open MPI libraries.
7. The Open MPI libraries connect back to the ORTED process via the Process Management Interface (PMI).

At this point the processes within the container run as they would normally directly on the host.

The advantages of this approach are:
  - Integration with resource managers such as Slurm.
  - Simplicity since similar to natively running MPI applications.

The drawbacks are:
  - The MPI in the container must be compatible with the version of MPI
    available on the host.
  - The MPI implementation in the container must be carefully
    configured for optimal use of the hardware if performance is
    critical.

Since the MPI implementation in the container must be compliant with
the version available on the host system, a standard approach is to
build your own MPI container, including building the same MPI
framework installed on the host from source.


Test Application
================

To illustrate how {Singularity} can be used to execute MPI applications, we will
assume for a moment that the application is ``mpitest.c``, a simple Hello World:

.. code-block:: c

	#include <mpi.h>
	#include <stdio.h>
	#include <stdlib.h>

	int main (int argc, char **argv) {
		int rc;
		int size;
		int myrank;

		rc = MPI_Init (&argc, &argv);
		if (rc != MPI_SUCCESS) {
			fprintf (stderr, "MPI_Init() failed");
			return EXIT_FAILURE;
		}

		rc = MPI_Comm_size (MPI_COMM_WORLD, &size);
		if (rc != MPI_SUCCESS) {
			fprintf (stderr, "MPI_Comm_size() failed");
			goto exit_with_error;
		}

		rc = MPI_Comm_rank (MPI_COMM_WORLD, &myrank);
		if (rc != MPI_SUCCESS) {
			fprintf (stderr, "MPI_Comm_rank() failed");
			goto exit_with_error;
		}

		fprintf (stdout, "Hello, I am rank %d/%d\n", myrank, size);

		MPI_Finalize();

		return EXIT_SUCCESS;

	 exit_with_error:
		MPI_Finalize();
		return EXIT_FAILURE;
	}

.. note::
    MPI is an interface to a library, so it consists of function calls and
    libraries that can be used by many programming languages. It comes with
    standardized bindings for Fortran and C. However, it can support
    applications in many languages like Python, R, etc.

The next step is to create the definition file used to build the
container, which will depend on the MPI implementation available on
the host.

MPICH Hybrid Container
======================

If the host MPI is MPICH, a definition file such as the following example can be used:

.. code-block:: none

    Bootstrap: docker
    From: ubuntu:18.04

    %files
        mpitest.c /opt

    %environment
        # Point to MPICH binaries, libraries man pages
        export MPICH_DIR=/opt/mpich-3.3.2
        export PATH="$MPICH_DIR/bin:$PATH"
        export LD_LIBRARY_PATH="$MPICH_DIR/lib:$LD_LIBRARY_PATH"
        export MANPATH=$MPICH_DIR/share/man:$MANPATH

    %post
        echo "Installing required packages..."
        export DEBIAN_FRONTEND=noninteractive
        apt-get update && apt-get install -y wget git bash gcc gfortran g++ make

        # Information about the version of MPICH to use
        export MPICH_VERSION=3.3.2
        export MPICH_URL="http://www.mpich.org/static/downloads/$MPICH_VERSION/mpich-$MPICH_VERSION.tar.gz"
        export MPICH_DIR=/opt/mpich

        echo "Installing MPICH..."
        mkdir -p /tmp/mpich
        mkdir -p /opt
        # Download
        cd /tmp/mpich && wget -O mpich-$MPICH_VERSION.tar.gz $MPICH_URL && tar xzf mpich-$MPICH_VERSION.tar.gz
        # Compile and install
        cd /tmp/mpich/mpich-$MPICH_VERSION && ./configure --prefix=$MPICH_DIR && make install

        # Set env variables so we can compile our application
        export PATH=$MPICH_DIR/bin:$PATH
        export LD_LIBRARY_PATH=$MPICH_DIR/lib:$LD_LIBRARY_PATH

        echo "Compiling the MPI application..."
        cd /opt && mpicc -o mpitest mpitest.c

.. note::

   The version of MPICH you install in the container must be
   compatible with the version on the host. It should also be
   configured to support the same process management mechanism and
   version, e.g. PMI2 / PMIx, as used on the host.

   There are wide variations in MPI configuration across HPC
   systems. Consult your system documentation, or ask your support
   staff for details.
        

Open MPI Hybrid Container
=========================

If the host MPI is Open MPI, the definition file looks like:

.. code-block:: none

    Bootstrap: docker
    From: ubuntu:18.04

    %files
        mpitest.c /opt

    %environment
        # Point to OMPI binaries, libraries, man pages
        export OMPI_DIR=/opt/ompi
        export PATH="$OMPI_DIR/bin:$PATH"
        export LD_LIBRARY_PATH="$OMPI_DIR/lib:$LD_LIBRARY_PATH"
        export MANPATH="$OMPI_DIR/share/man:$MANPATH"

    %post
        echo "Installing required packages..."
        apt-get update && apt-get install -y wget git bash gcc gfortran g++ make file

        echo "Installing Open MPI"
        export OMPI_DIR=/opt/ompi
        export OMPI_VERSION=4.0.5
        export OMPI_URL="https://download.open-mpi.org/release/open-mpi/v4.0/openmpi-$OMPI_VERSION.tar.bz2"
        mkdir -p /tmp/ompi
        mkdir -p /opt
        # Download
        cd /tmp/ompi && wget -O openmpi-$OMPI_VERSION.tar.bz2 $OMPI_URL && tar -xjf openmpi-$OMPI_VERSION.tar.bz2
        # Compile and install
        cd /tmp/ompi/openmpi-$OMPI_VERSION && ./configure --prefix=$OMPI_DIR && make -j8 install

        # Set env variables so we can compile our application
        export PATH=$OMPI_DIR/bin:$PATH
        export LD_LIBRARY_PATH=$OMPI_DIR/lib:$LD_LIBRARY_PATH

        echo "Compiling the MPI application..."
        cd /opt && mpicc -o mpitest mpitest.c
                
.. note::
      
   The version of Open MPI you install in the container must be
   compatible with the version on the host. It should also be
   configured to support the same process management mechanism and
   version, e.g. PMI2 / PMIx, as used on the host.

   There are wide variations in MPI configuration across HPC
   systems. Consult your system documentation, or ask your support
   staff for details.

      
Running an MPI Application
==========================

The standard way to execute MPI applications with hybrid {Singularity} containers is to
run the native ``mpirun`` command from the host, which will start {Singularity}
containers and ultimately MPI ranks within the containers.

Assuming your container with MPI and your application is already built,
the ``mpirun`` command to start your application looks like when your container
has been built based on the hybrid model:

.. code-block:: none

    $ mpirun -n <NUMBER_OF_RANKS> singularity exec <PATH/TO/MY/IMAGE> </PATH/TO/BINARY/WITHIN/CONTAINER>

Practically, this command will first start a process instantiating ``mpirun``
and then {Singularity} containers on compute nodes. Finally, when the containers
start, the MPI binary is executed:

.. code-block:: none

    $ mpirun -n 8 singularity run hybrid-mpich.sif /opt/mpitest
    Hello, I am rank 3/8
    Hello, I am rank 4/8
    Hello, I am rank 6/8
    Hello, I am rank 2/8
    Hello, I am rank 0/8
    Hello, I am rank 5/8
    Hello, I am rank 1/8
    Hello, I am rank 7/8

----------      
Bind model
----------

Similar to the *Hybrid Approach*, the basic idea behind the *Bind Approach* is to start the MPI
application by calling the MPI launcher (e.g., `mpirun`) from the host. The main difference between
the hybrid and bind approach is the fact that with the bind approach, the container usually does
not include any MPI implementation. This means that {Singularity} needs to mount/bind the MPI
available on the host into the container.

Technically this requires two steps:

1. Know where the MPI implementation on the host is installed.
2. Mount/bind it into the container in a location where the system will be able to find libraries and binaries.

The advantages of this approach are:
  - Integration with resource managers such as Slurm.
  - Container images are smaller since there is no need to add an MPI in the containers.

The drawbacks are:
  - The MPI used to compile the application in the container must be compatible with
    the version of MPI available on the host.
  - The user must know where the host MPI is installed.
  - The user must ensure that binding the directory where the host MPI is installed is
    possible.
  - The user must ensure that the host MPI is compatible with the MPI used to compile
    and install the application in the container.

The creation of a {Singularity} container for the bind model is based on the following steps:

1. Compile your application on a system with the target MPI implementation, as you would do
   to install your application on any system.
2. Create a definition file that includes the copy of the application from the host to the container
   image, as well as all required dependencies.
3. Generate the container image.

As already mentioned, the compilation of the application on the host is not different from
the installation of your application on any system. Just make sure that the MPI on the system
where you create your container is compatible with the MPI available on the platform(s) where
you want to run your containers. For example, a container where the application has been compiled
with MPICH will not be able to run on a system where only Open MPI is available, even if you mount
the directory where Open MPI is installed.

Bind Mode Definition File
=========================

A definition file for a container in bind mode is fairly straight
forward. The following example shows the definition file for the test
program, which in this case has been compiled on the host to
``/tmp/mpitest``:

.. code-block:: none

  Bootstrap: docker
  From: ubuntu:18.04

  %files
        /tmp/mpitest /opt/mpitest

  %environment
        export PATH="$MPI_DIR/bin:$PATH"
        export LD_LIBRARY_PATH="$MPI_DIR/lib:$LD_LIBRARY_PATH"


In this example, the application ``mpitest`` is copied from the host
into ``/opt``, so we will need to run it as ``/opt/mpitest`` inside
our container.

The environment section adds paths for binaries and libraries under
``$MPI_DIR`` - which we will need to set when running the container.


Running an MPI Application
==========================

When running our bind mode container we need to ``--bind`` our host's
MPI installation into the container. We also need to set the
environment variable ``$MPI_DIR`` in the container to point to the
location where the MPI installation is bound in.

Setting up the container in this way makes it semi-portable between
systems that have a version-compatible MPI installation, but under
different installation paths. You can also hard code the MPI path in
the definition file if you wish.


.. code-block:: none

    $ export MPI_DIR="<PATH/TO/HOST/MPI/DIRECTORY>"            
    $ mpirun -n <NUMBER_OF_RANKS> singularity exec --bind "$MPI_DIR" <PATH/TO/MY/IMAGE> </PATH/TO/BINARY/WITHIN/CONTAINER>

On an example system we may be using an Open MPI installation at
``/cm/shared/apps/openmpi/gcc/64/4.0.5/``. This means that the
commands to run the container in bind mode are:

    
.. code-block:: none

    $ export MPI_DIR="/cm/shared/apps/openmpi/gcc/64/4.0.5"
    $ mpirun -n 8 singularity exec --bind "$MPI_DIR" bind.sif /opt/mpitest
    Hello, I am rank 1/8
    Hello, I am rank 2/8
    Hello, I am rank 0/8
    Hello, I am rank 7/8
    Hello, I am rank 5/8
    Hello, I am rank 3/8
    Hello, I am rank 4/8
    Hello, I am rank 6/8


-----------------------
Batch Scheduler / Slurm
-----------------------
    
If your target system is setup with a batch system such as SLURM, a standard
way to execute MPI applications is through a batch script. The following
example illustrates the context of a batch script for Slurm that aims at
starting a {Singularity} container on each node allocated to the execution of
the job. It can easily be adapted for all major batch systems available.

.. code-block:: none

    $ cat my_job.sh
    #!/bin/bash
    #SBATCH --job-name singularity-mpi
    #SBATCH -N $NNODES # total number of nodes
    #SBATCH --time=00:05:00 # Max execution time

    mpirun -n $NP singularity exec /var/nfsshare/gvallee/mpich.sif /opt/mpitest

In fact, the example describes a job that requests the number of nodes specified
by the ``NNODES`` environment variable and a total number of MPI processes specified
by the ``NP`` environment variable. The example is also assuming that the container
is based on the hybrid model; if it is based on the bind model, please add the
appropriate bind options.

A user can then submit a job by executing the following SLURM command:

.. code-block:: none

    $ sbatch my_job.sh

    
---------------------
Alternative Launchers
---------------------

On many systems it is common to use an alternative launcher to start
MPI applications, e.g. Slurm's ``srun`` rather than the ``mpirun``
provided by the MPI installation. This approach is supported with
{Singularity} as long as the container MPI version supports the same
process management interface (e.g. PMI2 / PMIx) and version as is used
by the launcher.

In the bind mode the host MPI is used in the container, and should
interact correctly with the same launchers as it does on the host.


--------------------------
Interconnects / Networking
--------------------------

High performance interconnects such as Infiniband and Omnipath require
that MPI implementations are built to support them. You may need to
install or bind Infiniband/Omnipath libraries into your containers
when using these interconnects.

By default {Singularity} exposes every device in ``/dev`` to the
container. If you run a container using the ``--contain`` or
``--containall`` flags a minimal ``/dev`` is used instead. You may
need to bind in additional ``/dev/`` entries manually to
support the operation of your interconnect drivers in the container in
this case.

--------------------
Troubleshooting Tips
--------------------

If your containers run N rank 0 processes, instead of operating
correctly as an MPI application, it is likely that the MPI stack used
to launch the containerized application is not compatible with, or
cannot communicate with, the MPI stack in the container.

E.g. if we attempt to run the hybrid Open MPI container, but with
``mpirun`` from MPICH loaded on the host:

.. code-block::

    $ module add mpich
    $ mpirun -n 8 singularity run hybrid-openmpi.sif /opt/mpitest
    Hello, I am rank 0/1
    Hello, I am rank 0/1
    Hello, I am rank 0/1
    Hello, I am rank 0/1
    Hello, I am rank 0/1
    Hello, I am rank 0/1
    Hello, I am rank 0/1
    Hello, I am rank 0/1

If your container starts processes of different ranks, but fails with
communications errors there may also be a version incompatibility, or
interconnect libraries may not be available or configured properly
with the MPI stack in the container.

Please check the following things carefully before asking questions in
the {Singularity} community:

 - For the hybrid mode, is the MPI version on the host compatible with
   the version in the container? Newer MPI versions can generally
   tolerate some mismatch in the version number, but it is safest to
   use identical versions.
 - Is the MPI stack in the container configured to support the process
   management method used on the host? E.g. if you are launching tasks
   with ``srun`` configured for PMIx only, then a containerized MPI
   supporting PMI2 only will not operate as expected.
 - If you are using an interconnect other than standard Ethernet, are
   any required libraries for it installed or bound into the
   container? Is the MPI stack in the container configured correctly
   to use them?

We recommend using the {Singularity} Google Group or Slack Channel to
ask for MPI advice from the {Singularity} community. HPC cluster
configurations vary greatly and most MPI problems are related to MPI /
interconnect configuration, and not caused by issues in {Singularity}
itself.
