.. _gpu:

====================================
GPU Support (NVIDIA CUDA & AMD ROCm)
====================================

{Singularity} natively supports running application containers that use NVIDIA's
CUDA GPU compute framework, or AMD's ROCm solution. This allows easy access to
users of GPU-enabled machine learning frameworks such as tensorflow, regardless
of the host operating system. As long as the host has a driver and library
installation for CUDA/ROCm then it's possible to e.g. run tensorflow in an
up-to-date Ubuntu 18.04 container, from an older RHEL 6 host.

Applications that support OpenCL for compute acceleration can also be used
easily, with an additional bind option.

------------------
NVIDIA GPUs & CUDA
------------------

Commands that ``run``, or otherwise execute containers (``shell``, ``exec``) can
take an ``--nv`` option, which will setup the container's environment to use an
NVIDIA GPU and the basic CUDA libraries to run a CUDA enabled application.
The ``--nv`` flag will:

* Ensure that the ``/dev/nvidiaX`` device entries are available inside the
  container, so that the GPU cards in the host are accessible.
* Locate and bind the basic CUDA libraries from the host into the container, so
  that they are available to the container, and match the kernel GPU driver on
  the host.
* Set the ``LD_LIBRARY_PATH`` inside the container so that the bound-in version
  of the CUDA libraries are used by applications run inside the container.

Requirements
============

To use the ``--nv`` flag to run a CUDA application inside a container you must
ensure that:

* The host has a working installation of the NVIDIA GPU driver, and a matching
  version of the basic NVIDIA/CUDA libraries. The host *does not* need to have an X
  server running, unless you want to run graphical apps from the container.
* Either a working installation of the ``nvidia-container-cli`` tool is available
  on the ``PATH`` when you run ``singularity``, or the NVIDIA libraries are in
  the system's library search path.
* The application inside your container was compiled for a CUDA version, and
  device capability level, that is supported by the host card and driver.

These requirements are usually satisfied by installing the NVIDIA drivers and
CUDA packages directly from the NVIDIA website. Linux distributions may provide
NVIDIA drivers and CUDA libraries, but they are often outdated which can lead to
problems running applications compiled for the latest versions of CUDA.

Library Search Options
----------------------

{Singularity} will find the NVIDIA/CUDA libraries on your host either using the
``nvidia-container-cli`` tool, or, if it is not available, a list of libraries
in the configuration file ``etc/singularity/nvbliblist``.

If possible we recommend installing the ``nvidia-container-cli`` tool from the
`NVIDIA libnvidia-container website <https://nvidia.github.io/libnvidia-container/>`__

The fall-back ``etc/singularity/nvbliblist`` library list is correct at time of 
release for CUDA 10.1. However, if future CUDA versions split or add library files
you may need to edit it. The ``nvidia-container-cli`` tool will be updated by
NVIDIA to always return the appropriate list of libraries.

Example - tensorflow-gpu
========================

Tensorflow is commonly used for machine learning projects but can be diffficult
to install on older systems, and is updated frequently. Running tensorflow from
a container removes installation problems and makes trying out new versions easy.

The official tensorflow repository on Docker Hub contains NVIDA GPU supporting
containers, that will use CUDA for processing. You can view the available
versions on the `tags page on Docker Hub <https://hub.docker.com/r/tensorflow/tensorflow/tags>`__

The container is large, so it's best to build or pull the docker image to a SIF
before you start working with it:

.. code-block:: none

    $ singularity pull docker://tensorflow/tensorflow:latest-gpu
    ...
    INFO:    Creating SIF file...
    INFO:    Build complete: tensorflow_latest-gpu.sif


Then run the container with GPU support:

.. code-block:: none

    $ singularity run --nv tensorflow_latest-gpu.sif

    ________                               _______________                
    ___  __/__________________________________  ____/__  /________      __
    __  /  _  _ \_  __ \_  ___/  __ \_  ___/_  /_   __  /_  __ \_ | /| / /
    _  /   /  __/  / / /(__  )/ /_/ /  /   _  __/   _  / / /_/ /_ |/ |/ / 
    /_/    \___//_/ /_//____/ \____//_/    /_/      /_/  \____/____/|__/


    You are running this container as user with ID 1000 and group 1000,
    which should map to the ID and group for your user on the Docker host. Great!

    Singularity>

You can verify the GPU is available within the container by using the
tensorflow ``list_local_devices()`` function:

.. code-block:: none

    Singularity> python
    Python 2.7.15+ (default, Jul  9 2019, 16:51:35) 
    [GCC 7.4.0] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from tensorflow.python.client import device_lib
    >>> print(device_lib.list_local_devices())
    2019-11-14 15:32:09.743600: I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
    2019-11-14 15:32:09.784482: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 3292620000 Hz
    2019-11-14 15:32:09.787911: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x565246634360 executing computations on platform Host. Devices:
    2019-11-14 15:32:09.787939: I tensorflow/compiler/xla/service/service.cc:175]   StreamExecutor device (0): Host, Default Version
    2019-11-14 15:32:09.798428: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcuda.so.1
    2019-11-14 15:32:09.842683: I tensorflow/stream_executor/cuda/cuda_gpu_executor.cc:1006] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero
    2019-11-14 15:32:09.843252: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x5652469263d0 executing computations on platform CUDA. Devices:
    2019-11-14 15:32:09.843265: I tensorflow/compiler/xla/service/service.cc:175]   StreamExecutor device (0): GeForce GT 730, Compute Capability 3.5
    2019-11-14 15:32:09.843380: I tensorflow/stream_executor/cuda/cuda_gpu_executor.cc:1006] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero
    2019-11-14 15:32:09.843984: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1618] Found device 0 with properties: 
    name: GeForce GT 730 major: 3 minor: 5 memoryClockRate(GHz): 0.9015
    ...   


Multiple GPUs
=============

By default, {Singularity} makes all host devices available in the container. When
the ``--contain`` option is used a minimal ``/dev`` tree is created in the
container, but the ``--nv`` option will ensure that all nvidia devices on the
host are present in the container.

This behaviour is different to ``nvidia-docker`` where an ``NVIDIA_VISIBLE_DEVICES``
environment variable is used to control whether some or all host GPUs are visible
inside a container. The ``nvidia-container-runtime`` explicitly binds the devices
into the container dependent on the value of ``NVIDIA_VISIBLE_DEVICES``.

To control which GPUs are used in a {Singularity} container that is run with
``--nv`` you can set ``SINGULARITYENV_CUDA_VISIBLE_DEVICES`` before running the
container, or ``CUDA_VISIBLE_DEVICES`` inside the container.  This variable will
limit the GPU devices that CUDA programs see.

E.g. to run the tensorflow container, but using only the first GPU in the host,
we could do:

.. code-block:: none

    $ SINGULARITYENV_CUDA_VISIBLE_DEVICES=0 singularity run --nv tensorflow_latest-gpu.sif

    # or

    $ export SINGULARITYENV_CUDA_VISIBLE_DEVICES=0
    $ singularity run tensorflow_latest-gpu.sif


Troubleshooting
===============

If the host installation of the NVIDIA / CUDA driver and libraries is working
and up-to-date there are rarely issues running CUDA programs inside of
{Singularity} containers. The most common issue seen is:

CUDA_ERROR_UNKNOWN when everything seems to be correctly configured
-------------------------------------------------------------------

CUDA depends on multiple kernel modules being loaded. Not all of the modules are
loaded at system startup. Some portions of the NVIDA driver stack are initialized
when first needed. This is done using a setuid root binary, so initializing can
be triggered by any user on the host. In {Singularity} containers, privilege
escalation is blocked, so the setuid root binary cannot initialize the driver
stack fully.

If you experience ``CUDA_ERROR_UNKNOWN`` in a container, initialize the driver
stack on the host first, by running a CUDA program there or 
``modprobe nvidia_uvm`` as root, and using ``nvidia-persistenced`` to avoid
driver unload.


---------------
AMD GPUs & ROCm
---------------

{Singularity} 3.5 adds a ``--rocm`` flag to support GPU compute with the ROCm
framework using AMD Radeon GPU cards.

Commands that ``run``, or otherwise execute containers (``shell``, ``exec``) can
take an ``--rocm`` option, which will setup the container's environment to use a
Radeon GPU and the basic ROCm libraries to run a ROCm enabled application.
The ``--rocm`` flag will:

* Ensure that the ``/dev/dri/`` device entries are available inside the
  container, so that the GPU cards in the host are accessible.
* Locate and bind the basic ROCm libraries from the host into the container, so
  that they are available to the container, and match the kernel GPU driver on
  the host.
* Set the ``LD_LIBRARY_PATH`` inside the container so that the bound-in version
  of the ROCm libraries are used by application run inside the container.

Requirements
============

To use the ``--rocm`` flag to run a CUDA application inside a container you must
ensure that:

* The host has a working installation of the ``amdgpu`` driver, and a compatible
  version of the basic ROCm libraries. The host *does not* need to have an X
  server running, unless you want to run graphical apps from the container.
* The ROCm libraries are in the system's library search path.
* The application inside your container was compiled for a ROCm version that is
  compatible with the ROCm version on your host.

These requirements can be satisfied by following the requirements on the 
`ROCm web site <https://rocm.github.io/ROCmInstall.html>`__

At time of release, {Singularity} was tested successfully on Debian 10 with ROCm
2.8/2.9 and the upstream kernel driver, and Ubuntu 18.04 with ROCm 2.9 and the
DKMS driver.


Example - tensorflow-rocm
=========================

Tensorflow is commonly used for machine learning projects, but can be difficult
to install on older systems, and is updated frequently. Running tensorflow from
a container removes installation problems and makes trying out new versions easy.

The rocm tensorflow repository on Docker Hub contains Radeon GPU supporting
containers, that will use ROCm for processing. You can view the available
versions on the `tags page on Docker Hub <https://hub.docker.com/r/rocm/tensorflow/tags>`__

The container is large, so it's best to build or pull the docker image to a SIF
before you start working with it:

.. code-block:: none

    $ singularity pull docker://rocm/tensorflow:latest
    ...
    INFO:    Creating SIF file...
    INFO:    Build complete: tensorflow_latest.sif


Then run the container with GPU support:

.. code-block:: none

    $ singularity run --rocm tensorflow_latest.sif


You can verify the GPU is available within the container by using the
tensorflow ``list_local_devices()`` function:

.. code-block:: none

    Singularity> ipython
    Python 3.5.2 (default, Jul 10 2019, 11:58:48) 
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.8.0 -- An enhanced Interactive Python. Type '?' for help.
    >>> from tensorflow.python.client import device_lib
    ...
    >>> print(device_lib.list_local_devices())
    ...
    2019-11-14 16:33:42.750509: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1651] Found device 0 with properties: 
    name: Lexa PRO [Radeon RX 550/550X]
    AMDGPU ISA: gfx803
    memoryClockRate (GHz) 1.183
    pciBusID 0000:09:00.0
    ...   

-------------------
OpenCL Applications
-------------------

Both the ``--rocm`` and ``--nv`` flags will bind the vendor OpenCL implementation
libraries into a container that is being run. However, these libraries will not
be used by OpenCL applications unless a vendor icd file is available under
``/etc/OpenCL/vendors`` that directs OpenCL to use the vendor library.

The simplest way to use OpenCL in a container is to ``--bind /etc/OpenCL`` so
that the icd files from the host (which match the bound-in libraries) are
present in the container. 

Example - Blender OpenCL
========================

The `Sylabs examples repository <https://github.com/sylabs/examples>`__ contains
an example container definition for the 3D modelling application 'Blender'.

The latest versions of Blender supports OpenCL rendering. You can run Blender
as a graphical application that will make use of a local Radeon GPU for OpenCL
compute using the container that has been published to the Sylabs library:

.. code-block:: none

    $ singularity exec --rocm --bind /etc/OpenCL library://sylabs/examples/blender blender

Note the *exec* used as the *runscript* for this container is setup for batch
rendering (which can also use OpenCL).
