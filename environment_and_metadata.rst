.. _environment-and-metadata:

========================
Environment and Metadata
========================

.. _sec:envandmetadata:

Environment variables are values you can set in a session, which can
be used to influence the behavior of programs. It's often considered
best practice to use environment variables to pass settings to a
program in a container, because they are easily set and don't rely on
writing and binding in program-specific configuration files. When
building a container you may need to set fixed or default environment
variables. When running containers you may need to set or override
environment variables.

The :ref:`metadata <sec:metadata>` of a container is information that
describes the container. {Singularity} automatically records important
information such as the definition file used to build a
container. Other details such as the version of {Singularity} used are
present as :ref:`labels <sec:labels>` on a container. You can also
specify your own to be recorded against your container.

----------------------------
Changes in {Singularity} 3.6
----------------------------

{Singularity} 3.6 modified the ways in which environment variables
are handled to allow long-term stability and consistency that has
been lacking in prior versions. It also introduced new ways of setting
environment variables, such as the ``--env`` and ``--env-file``
options.

.. warning::

   If you have containers built with {Singularity} <3.6, and frequently
   set and override environment variables, please review this section
   carefully. Some behavior has changed.

Summary of changes
------------------

 - When building a container, the environment defined in the base
   image (e.g. a Docker image) is available during the ``%post``
   section of the build.
 - An environment variable set in a container image, from the
   bootstrap base image, or in the ``%environment`` section of a
   definition file *will not* be overridden by a host environment
   variable of the same name. The ``--env``, ``--env-file``, or
   ``SINGULARITYENV_`` methods must be used to explicitly override a
   environment variable set by the container image.


--------------------
Environment Overview
--------------------

When you run a program in a container with {Singularity}, the
environment variables that the program sees are a combination of:

 - The environment variables set in the base image (e.g. Docker image)
   used to build the container.
 - The environment variables set in the ``%environment`` section of
   the definition file used to build the container.
 - *Most* of the environment variables set on your host, which are
   passed into the container.
 - Any variables you set specifically for the container at runtime,
   using the ``--env``, ``--env-file`` options, or by setting
   ``SINGULARITYENV_`` variables outside of the container.
 - The ``PATH`` variable can be manipulated to add entries.
 - Runtime variables ``SINGULARITY_xxx`` set by {Singularity} to provide
   information about the container.

The environment variables from the base image or definition file used
to build a container always apply, but can be overridden.

You can choose to exclude passing environment variables from the host
into the container with the ``-e`` or ``--cleanenv``
option.

We'll go through each place environment variables can be defined, so
that you can understand how the final environment in a container is
created, and can be manipulated.

If you are interested in variables available when you are *building* a
container, rather than when running a container, see :ref:`build
environment section <build-environment>`.

-----------------------------
Environment from a base image
-----------------------------

When you build a container with {Singularity} you might *bootstrap* from
a library or Docker image, or using Linux distribution bootstrap tools
such as ``debootstrap``, ``yum`` etc.

When using ``debootstrap``, ``yum`` etc. you are starting from a fresh
install of a Linux distribution into your container. No specific
environment variables will be set. If you are using a ``library`` or
``Docker`` source then you may inherit environment variables from your
base image.

If I build a singularity container from the image
``docker://python:3.7`` then when I run the container I can see that
the ``PYTHON_VERSION`` variable is set in the container:

.. code-block::

   $ singularity exec python.sif env | grep PYTHON_VERSION
   PYTHON_VERSION=3.7.7

This happens because  the ``Dockerfile`` used to build  that container has
``ENV PYTHON_VERSION 3.7.7`` set inside it.

You can always override the value of these base image environment
variables, if needed. See below.

----------------------------------
Environment from a definition file
----------------------------------

Environment variables can be included in your container by adding them
to your definition file. Use ``export`` in the ``%environment``
section of a definition file to set a container environment variable:

.. code-block:: singularity

        Bootstrap: library
        From: default/alpine

        %environment
            export MYVAR="Hello"

        %runscript
            echo $MYVAR


Now the value of ``MYVAR`` is ``Hello`` when the container
is launched. The ``%runscript`` is set to echo the value.

.. code-block::

   $ singularity run env.sif 
   Hello

.. warning::
   {Singularity} 3.6 uses an embedded shell interpreter to evaluate and setup container
   environments, therefore all commands executed from the ``%environment`` section have
   an execution timeout of **5 seconds** for {Singularity} 3.6 and a **1 minute** timeout since
   {Singularity} 3.7. While it is fine to source a script from there, it is not recommended
   to use this section to run potentially long initialization tasks because this would
   impact users running the image and the execution could abort due to timeout.

-------------------------
Environment from the host
-------------------------

If you have environment variables set outside of your container, on
the host, then by default they will be available inside the
container. Except that:

 - The ``PS1`` shell prompt is reset for a container specific prompt.
 - The ``PATH`` environment variable will be modified to contain default values.
 - The ``LD_LIBRARY_PATH`` is modified to a default
   ``/.singularity.d/libs``, that will include NVIDIA / ROCm libraries
   if applicable.

Also, an environment variable set on the host *will not* override a
variable of the same name that has been set inside the container image.
   
If you *do not want* the host environment variables to pass into the
container you can use the ``-e`` or ``--cleanenv`` option. This gives
a clean environment inside the container, with a minimal set of
environment variables for correct operation of most software.

.. code-block::

   $ singularity exec --cleanenv env.sif env
   HOME=/home/dave
   LANG=C
   LD_LIBRARY_PATH=/.singularity.d/libs
   PATH=/startpath:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   PROMPT_COMMAND=PS1="Singularity> "; unset PROMPT_COMMAND
   PS1=Singularity> 
   PWD=/home/dave/doc-tesrts
   SINGULARITY_COMMAND=exec
   SINGULARITY_CONTAINER=/home/dave/doc-tesrts/env.sif
   SINGULARITY_ENVIRONMENT=/.singularity.d/env/91-environment.sh
   SINGULARITY_NAME=env.sif
   TERM=xterm-256color


.. warning::

   If you work on a host system that sets a lot of environment
   variables, e.g. because you use software made available through
   environment modules / lmod, you may see strange behavior in your
   container. Check your host environment with ``env`` for variables
   such as ``PYTHONPATH`` that can change the way code runs, and
   consider using ``--cleanenv``.

------------------------------------------
Environment from the {Singularity} runtime
------------------------------------------

It can be useful for a program to know when it is running in a
{Singularity} container, and some basic information about the container
environment. {Singularity} will automatically set a number of
environment variables in a container that can be inspected by any
program running in the container.

  - ``SINGULARITY_COMMAND`` - how the container was started,
    e.g. ``exec`` / ``run`` / ``shell``.
  - ``SINGULARITY_CONTAINER`` - the full path to the container image.
  - ``SINGULARITY_ENVIRONMENT`` - path inside the container to the
    shell script holding the container image environment settings.
  - ``SINGULARITY_NAME`` - name of the container image,
    e.g. ``myfile.sif`` or ``docker://ubuntu``.
  - ``SINGULARITY_BIND`` - a list of bind paths that the user
    requested, via flags or environment variables, when running the
    container.

   
--------------------------------
Overriding environment variables
--------------------------------

You can override variables that have been set in the container image,
or define additional variables, in various ways as appropriate for
your workflow.

``--env`` option
----------------

*New in {Singularity} 3.6*

The ``--env`` option on the ``run/exec/shell`` commands allows you to
specify environment variables as ``NAME=VALUE`` pairs:

.. code-block::

   $ singularity run env.sif 
   Hello
   
   $ singularity run --env MYVAR=Goodbye env.sif
   Goodbye

Separate multiple variables with commas, e.g. ``--env
MYVAR=A,MYVAR2=B``, and use shell quoting / shell escape if your
variables include special characters.


``--env-file`` option
---------------------

*New in {Singularity} 3.6*

The ``--env-file`` option lets you provide a file that contains
environment variables as ``NAME=VALUE`` pairs, e.g.:


.. code-block::

  $ cat myenvs 
  MYVAR="Hello from a file"

  $ singularity run --env-file myenvs env.sif 
  Hello from a file


``SINGULARITYENV_`` prefix
--------------------------

If you export an environment variable on your host called
``SINGULARITYENV_xxx`` *before* you run a container, then it will set
the environment variable ``xxx`` inside the container:

.. code-block::

   $ singularity run env.sif
   Hello

   $ export SINGULARITYENV_MYVAR="Overridden"
   $ singularity run env.sif
   Overridden


Manipulating ``PATH``
---------------------

``PATH`` is a special environment variable that tells a system where
to look for programs that can be run. ``PATH`` contains multiple
filesytem locations (paths) separated by colons. When you ask to run a
program ``myprog``, the system looks through these locations one by
one, until it finds ``myprog``.

To ensure containers work correctly, when a host ``PATH`` might
contain a lot of host-specific locations that are not present in the
container, {Singularity} will ensure ``PATH`` in the container is set to
a default.

.. code-block::

   /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

This covers the standard locations for software installed using a
system package manager in most Linux distributions. If you have
software installed elsewhere in the container, then you can override
this by setting ``PATH`` in the container definition ``%environment``
block.

If your container depends on things that are bind mounted into it, or
you have another need to modify the ``PATH`` variable when starting a
container, you can do so with ``SINGULARITYENV_APPEND_PATH`` or
``SINGULARITYENV_PREPEND_PATH``.

If you set a variable on your host called
``SINGULARITYENV_APPEND_PATH`` then its value will be appended
(added to the end) of the ``PATH`` variable in the container.

.. code-block::

   $ singularity exec env.sif sh -c 'echo $PATH'
   /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

   $ export SINGULARITYENV_APPEND_PATH="/endpath"
   $ singularity exec env.sif sh -c 'echo $PATH'
   /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/endpath

Alternatively you could use the ``--env`` option to set a
``APPEND_PATH`` variable, e.g. ``--env APPEND_PATH=/endpath``.

If you set a variable on your host called
``SINGULARITYENV_PREPEND_PATH`` then its value will be prepended
(added to the start) of the ``PATH`` variable in the container.

.. code-block::

   $ singularity exec env.sif sh -c 'echo $PATH'
   /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

   $ export SINGULARITYENV_PREPEND_PATH="/startpath"
   $ singularity exec env.sif sh -c 'echo $PATH'
   /startpath:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

Alternatively you could use the ``--env`` option to set a
``PREPEND_PATH`` variable, e.g. ``--env PREPEND_PATH=/startpath``.


Evaluating container variables
------------------------------

When setting environment variables with ``--env`` etc. you can specify
an escaped variable name, e.g. ``\$PATH`` to evaluate the value of
that variable in the container.

For example, ``--env PATH="\$PATH:/endpath"`` would have the same
effect as ``--env APPEND_PATH="/endpath"``.



Environment Variable Precedence
-------------------------------

When a container is run with {Singularity} 3.6, the container
environment is constructed in the following order:

  - Clear the environment, keeping just ``HOME`` and ``SINGULARITY_APPNAME``.
  - Take Docker defined environment variables, where Docker was the base image source.
  - If ``PATH`` is not defined set the {Singularity} default ``PATH`` *or*
  - If ``PATH`` is defined, add any missing path parts from {Singularity} defaults
  - Take environment variables defined explicitly in the image
    (``%environment``). These can override any previously set values.
  - Set SCIF (``--app``) environment variables
  - Set base environment essential vars (``PS1`` and ``LD_LIBRARY_PATH``)
  - Inject ``SINGULARITYENV_`` / ``--env`` / ``--env-file`` variables
    so they can override or modify any previous values:
  - Source any remaining scripts from ``/singularity.d/env`` 


.. _sec:umask:


--------------------------------
Umask / Default File Permissions
--------------------------------

The ``umask`` value on a Linux system controls the default permissions
for newly created files. It is not an environment variable, but
influences the behavior of programs in the container when they create
new files.

.. note::

   A detailed description of what the ``umask`` is, and how it works
   can be found at `Wikipedia
   <https://en.wikipedia.org/wiki/Umask>`__.

   
{Singularity} 3.7 and above set the ``umask`` in the container to match
the value outside, unless:

  - The ``--fakeroot`` option is used, in which case a ``0022`` umask
    is set so that ``root`` owned newly created files have expected
    'system default' permissions, and can be accessed by other
    non-root users who may use the same container later.
  - The ``--no-umask`` option is used, in which case a ``0022`` umask
    is set.

.. note::

   In {Singularity} 3.6 and below a default ``0022`` umask was always applied.


.. _sec:metadata:

------------------
Container Metadata
------------------

Each {Singularity} container has metadata describing the container, how
it was built, etc. This metadata includes the definition file used to
build the container and labels, which are specific pieces of
information set automatically or explicitly when the container is
built.

For containers that are generated with {Singularity} version 3.0 and
later, default labels are represented using the `rc1 Label Schema
<http://label-schema.org/rc1/>`_.

.. _sec:labels:

Custom Labels
-------------

You can add custom labels to your container using the ``%labels``
section in a definition file:

.. code-block:: singularity

    Bootstrap: library
    From: ubuntu:latest

    %labels
      OWNER Joana

      
Dynamic Build Time Labels
-------------------------

You may wish to set a label to a value that is not known in advance,
when you are writing the definition file, but can be obtained in the
``%post`` section of your definition file while the container is
building.

{Singularity} 3.7 and above allow this, through adding labels to the
file defined by the ``SINGULARITY_LABELS`` environment variable in the
``%post`` section:

.. code-block:: singularity
               
    Bootstrap: library
    From: ubuntu:latest

    # These labels take a fixed value in the definition
    %labels
      OWNER Joana

    # We can now also set labels to a value at build time
    %post
      VAL="$(myprog --version)"
      echo "my.label $VAL" >> "$SINGULARITY_LABELS"

Labels must be added to the file one per line, in a ``NAME VALUE`` format,
where the name and value are separated by a space.


Inspecting Metadata
-------------------

.. _inspect-command:

The ``inspect`` command gives you the ability to view the labels and/or
other metadata that were added to your container when it was built.

^^^^^^^^^^^^^^^^^^^^^
``-l``/  ``--labels``
^^^^^^^^^^^^^^^^^^^^^

Running inspect without any options, or with the ``-l`` or
``--labels`` options will display any labels set on the container

.. code-block:: console

    $ singularity inspect ubuntu.sif 
    my.label: version 1.2.3
    OWNER: Joana
    org.label-schema.build-arch: amd64
    org.label-schema.build-date: Thursday_12_November_2020_10:51:59_CST
    org.label-schema.schema-version: 1.0
    org.label-schema.usage.singularity.deffile.bootstrap: library
    org.label-schema.usage.singularity.deffile.from: ubuntu:latest
    org.label-schema.usage.singularity.version: 3.7.0-rc.1
                
We can easily see when the container was built, the source of the base
image, and the exact version of {Singularity} that was used to build it.

The custom label ``OWNER`` that we set in our definition file is also visible.

^^^^^^^^^^^^^^^^^^^^^^
``-d`` / ``--deffile``
^^^^^^^^^^^^^^^^^^^^^^

The ``-d`` or ``-deffile`` flag shows the definition file(s) that were
used to build the container.

.. code-block:: none

    $ singularity inspect --deffile jupyter.sif

And the output would look like:

.. code-block:: singularity

    Bootstrap: library
    From: debian:9

    %help
        Container with Anaconda 2 (Conda 4.5.11 Canary) and Jupyter Notebook 5.6.0 for Debian 9.x (Stretch).
        This installation is based on Python 2.7.15

    %environment
        JUP_PORT=8888
        JUP_IPNAME=localhost
        export JUP_PORT JUP_IPNAME

    %startscript
        PORT=""
        if [ -n "$JUP_PORT" ]; then
        PORT="--port=${JUP_PORT}"
        fi

        IPNAME=""
        if [ -n "$JUP_IPNAME" ]; then
        IPNAME="--ip=${JUP_IPNAME}"
        fi

        exec jupyter notebook --allow-root ${PORT} ${IPNAME}

    %setup
        #Create the .condarc file where the environments/channels from conda are specified, these are pulled with preference to root
        cd /
        touch .condarc

    %post
        echo 'export RANDOM=123456' >>$SINGULARITY_ENVIRONMENT
        #Installing all dependencies
        apt-get update && apt-get -y upgrade
        apt-get -y install \
        build-essential \
        wget \
        bzip2 \
        ca-certificates \
        libglib2.0-0 \
        libxext6 \
        libsm6 \
        libxrender1 \
        git
        rm -rf /var/lib/apt/lists/*
        apt-get clean
        #Installing Anaconda 2 and Conda 4.5.11
        wget -c https://repo.continuum.io/archive/Anaconda2-5.3.0-Linux-x86_64.sh
        /bin/bash Anaconda2-5.3.0-Linux-x86_64.sh -bfp /usr/local
        #Conda configuration of channels from .condarc file
        conda config --file /.condarc --add channels defaults
        conda config --file /.condarc --add channels conda-forge
        conda update conda
        #List installed environments
        conda list

Which is the definition file for the ``jupyter.sif`` container.

^^^^^^^^^^^^^^^^^^^^^^^^
``-r`` / ``--runscript``
^^^^^^^^^^^^^^^^^^^^^^^^

The ``-r`` or ``--runscript`` option shows the runscript for the image.

.. code-block:: none

    $ singularity inspect --runscript jupyter.sif

And the output would look like:

.. code-block:: bash

    #!/bin/sh
    OCI_ENTRYPOINT=""
    OCI_CMD="bash"
    # ENTRYPOINT only - run entrypoint plus args
    if [ -z "$OCI_CMD" ] && [ -n "$OCI_ENTRYPOINT" ]; then
    SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT} $@"
    fi

    # CMD only - run CMD or override with args
    if [ -n "$OCI_CMD" ] && [ -z "$OCI_ENTRYPOINT" ]; then
    if [ $# -gt 0 ]; then
        SINGULARITY_OCI_RUN="$@"
    else
        SINGULARITY_OCI_RUN="${OCI_CMD}"
    fi
    fi

    # ENTRYPOINT and CMD - run ENTRYPOINT with CMD as default args
    # override with user provided args
    if [ $# -gt 0 ]; then
        SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT} $@"
    else
        SINGULARITY_OCI_RUN="${OCI_ENTRYPOINT} ${OCI_CMD}"
    fi

    exec $SINGULARITY_OCI_RUN

^^^^^^^^^^^^^^^^^^^
``-t`` / ``--test``
^^^^^^^^^^^^^^^^^^^

The ``-t`` or ``--test`` flag shows the test script for the image.

.. code-block:: none

    $ singularity inspect --test jupyter.sif

This will output the corresponding ``%test`` section from the definition file.

^^^^^^^^^^^^^^^^^^^^^^^^^^
``-e`` / ``--environment``
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``-e`` or ``--environment`` flag shows the environment variables
that are defined in the container image. These may be set from
one or more environment files, depending on how the container was built.

.. code-block:: none

    $ singularity inspect --environment jupyter.sif

And the output would look like:

.. code-block:: bash

    ==90-environment.sh==
    #!/bin/sh

    JUP_PORT=8888
    JUP_IPNAME=localhost
    export JUP_PORT JUP_IPNAME


^^^^^^^^^^^^^^^^^^^^^^^
``-h`` / ``--helpfile``
^^^^^^^^^^^^^^^^^^^^^^^

The ``-h`` or ``-helpfile`` flag will show the container's description
in the ``%help`` section of its definition file.

You can call it this way:

.. code-block:: none

    $ singularity inspect --helpfile jupyter.sif

And the output would look like:

.. code-block:: none

    Container with Anaconda 2 (Conda 4.5.11 Canary) and Jupyter Notebook 5.6.0 for Debian 9.x (Stretch).
    This installation is based on Python 2.7.15

^^^^^^^^^^^^^^^^^^^
``-j`` / ``--json``
^^^^^^^^^^^^^^^^^^^

This flag gives you the possibility to output your labels in a JSON format.

You can call it this way:

.. code-block:: console

    $ singularity inspect --json ubuntu.sif

And the output would look like:

.. code-block:: json

    {
            "data": {
                    "attributes": {
                            "labels": {
                                    "my.label": "version 1.2.3",
                                    "OWNER": "Joana",
                                    "org.label-schema.build-arch": "amd64",
                                    "org.label-schema.build-date": "Thursday_12_November_2020_10:51:59_CST",
                                    "org.label-schema.schema-version": "1.0",
                                    "org.label-schema.usage.singularity.deffile.bootstrap": "library",
                                    "org.label-schema.usage.singularity.deffile.from": "ubuntu:latest",
                                    "org.label-schema.usage.singularity.version": "3.7.0-rc.1"
                            }
                    }
            },
            "type": "container"
    }


-------------------------
/.singularity.d directory
-------------------------

The ``/.singularity.d`` directory in a container contains scripts and
environment files that are used when a container is executed.

*You should not manually modify* files under ``/.singularity.d``, from
your definition file during builds, or directly within your container
image. Recent 3.x versions of {Singularity} replace older action scripts
dynamically, at runtime, to support new features. In the longer term,
metadata will be moved outside of the container, and stored only in
the SIF file metadata descriptor.

.. code-block:: none

    /.singularity.d/

    ├── actions
    │   ├── exec
    │   ├── run
    │   ├── shell
    │   ├── start
    │   └── test
    ├── env
    │   ├── 01-base.sh
    |   ├── 10-docker2singularity.sh
    │   ├── 90-environment.sh
    │   ├── 91-environment.sh
    |   ├── 94-appsbase.sh
    │   ├── 95-apps.sh
    │   └── 99-base.sh
    ├── labels.json
    ├── libs
    ├── runscript
    ├── runscript.help
    ├── Singularity
    └── startscript

-  **actions**: This directory contains helper scripts to allow the container to
   carry out the action commands. (e.g. ``exec`` , ``run`` or ``shell``). In
   later versions of {Singularity}, these files may be dynamically written at
   runtime, *and should not be modified* in the container.

-  **env**: All ``*.sh`` files in this directory are sourced in
   alpha-numeric order when the container is started. For legacy
   purposes there is a symbolic link called ``/environment`` that
   points to ``/.singularity.d/env/90-environment.sh``. Whenever
   possible, avoid modifying or creating environment files manually to
   prevent potential issues building & running containers with future
   versions of {Singularity}. Beginning with {Singularity} 3.6, additional
   facilities such as ``--env`` and ``--env-file`` are available to
   allow manipulation of the container environment at runtime.

-  **labels.json**: The json file that stores a containers labels described
   above. 

-  **libs**: At runtime the user may request some host-system libraries to be
   mapped into the container (with the ``--nv`` option for example). If so, this
   is their destination.

-  **runscript**: The commands in this file will be executed when the container
   is invoked with the ``run`` command or called as an executable. For legacy
   purposes there is a symbolic link called ``/singularity`` that points to this
   file.

-  **runscript.help**: Contains the description that was added in the ``%help``
   section.

-  **{Singularity}**: This is the definition file that was used to generate the
   container. If more than 1 definition file was used to generate the container
   additional {Singularity} files will appear in numeric order in a sub-directory
   called ``bootstrap_history``.

-  **startscript**: The commands in this file will be executed when the
   container is invoked with the ``instance start`` command.
