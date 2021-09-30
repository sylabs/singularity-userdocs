
.. _definition-files:

================
Definition Files
================

.. _sec:deffiles:

A {Singularity} Definition File (or "def file" for short) is like a set of
blueprints explaining how to build a custom container. It includes specifics
about the base OS to build or the base container to start from, software to
install, environment variables to set at runtime, files to add from the host
system, and container metadata.

--------
Overview
--------


A {Singularity} Definition file is divided into two parts:

#. **Header**: The Header describes the core operating system to build within
   the container. Here you will configure the base operating system features
   needed within the container. You can specify, the Linux distribution, the
   specific version, and the packages that must be part of the core install
   (borrowed from the host system).

#. **Sections**: The rest of the definition is comprised of sections, (sometimes
   called scriptlets or blobs of data). Each section is defined by a ``%``
   character followed by the name of the particular section. All sections are
   optional, and a def file may contain more than one instance of a given
   section. Sections that are executed at build time are executed with the
   ``/bin/sh`` interpreter and can accept ``/bin/sh`` options. Similarly,
   sections that produce scripts to be executed at runtime can accept options
   intended for ``/bin/sh``

For more in-depth and practical examples of def files, see the `Sylabs examples
repository <https://github.com/sylabs/examples>`_

For a comparison between Dockerfile and {Singularity} definition file,
please see: :ref:`this section <sec:deffile-vs-dockerfile>`.

------
Header
------

The header should be written at the top of the def file. It tells {Singularity}
about the base operating system that it should use to build the container. It is
composed of several keywords.

The only keyword that is required for every type of build is ``Bootstrap``.
It determines the *bootstrap agent*  that will be used to create the base
operating system you want to use. For example, the ``library`` bootstrap agent
will pull a container from the `Container Library
<https://cloud.sylabs.io/library>`_ as a base. Similarly, the ``docker``
bootstrap agent will pull docker layers from `Docker Hub
<https://hub.docker.com/>`_ as a base OS to start your image.

Starting with {Singularity} 3.2, the ``Bootstrap`` keyword needs to be the first
entry in the header section.  This breaks compatibility with older versions
that allow the parameters of the header to appear in any order.

Depending on the value assigned to ``Bootstrap``, other keywords may also be
valid in the header. For example, when using the ``library`` bootstrap agent,
the ``From`` keyword becomes valid. Observe the following example for building a
Debian container from the Container Library:

.. code-block:: singularity

    Bootstrap: library
    From: debian:7

A def file that uses an official mirror to install Centos-7 might look like
this:

.. code-block:: singularity

    Bootstrap: yum
    OSVersion: 7
    MirrorURL: http://mirror.centos.org/centos-%{OSVERSION}/%{OSVERSION}/os/$basearch/
    Include: yum

Each bootstrap agent enables its own options and keywords. You can read about
them and see examples in the :ref:`appendix section<buildmodules>`:


Preferred bootstrap agents
==========================

-  :ref:`library <build-library-module>` (images hosted on the `Container Library <https://cloud.sylabs.io/library>`_)

-  :ref:`docker <build-docker-module>` (images hosted on Docker Hub)

-  :ref:`shub <build-shub>` (images hosted on Singularity Hub)

-  :ref:`oras <build-oras>` (images from supporting OCI registries)

-  :ref:`scratch <scratch-agent>` (a flexible option for building a container from scratch)

Other bootstrap agents
======================

-  :ref:`localimage <build-localimage>` (images saved on your machine)

-  :ref:`yum <build-yum>` (yum based systems such as CentOS and Scientific Linux)

-  :ref:`debootstrap <build-debootstrap>` (apt based systems such as Debian and Ubuntu)

-  :ref:`oci <cli-oci-bootstrap-agent>` (bundle compliant with OCI Image Specification)

-  :ref:`oci-archive <cli-oci-archive-bootstrap-agent>` (tar files obeying the OCI Image Layout Specification)

-  :ref:`docker-daemon <docker-daemon-archive>` (images managed by the locally running docker daemon)

-  :ref:`docker-archive <docker-daemon-archive>` (archived docker images)

-  :ref:`arch <build-arch>` (Arch Linux)

-  :ref:`busybox <build-busybox>` (BusyBox)

-  :ref:`zypper <build-zypper>` (zypper based systems such as Suse and OpenSuse)


SIF Image Verification / Fingerprints Header
============================================

If the bootstrap image is in the SIF format, then verification will
be performed at build time. This verification checks whether the image
has been signed. If it has been signed the integrity of the image is
checked, and the signatures matched to public keys if available. This
process is equivalent to running ``singularity verify`` on the
bootstrap image.

By default a failed verification, e.g. against an unsigned image, or
one that has been modified after signing, will produce a warning but
the build will continue.

To enforce that the bootstrap image verifies correctly and has been
signed by one or more keys, you can use the ``Fingerprints:`` header
introduced in {Singularity} 3.7.

.. code-block:: singularity

    Bootstrap: localimage
    From: test.sif
    Fingerprints: 12045C8C0B1004D058DE4BEDA20C27EE7FF7BA84,22045C8C0B1004D058DE4BEDA20C27EE7FF7BA84

If, at build time, the image is not signed with keys corresponding to
*all* of the listed fingerprints, the build will fail.

The ``Fingerprints:`` header can be used with bootstrap agents that
provide a SIF image. The ``library`` agent always retrieves a SIF
image. The ``localimage`` agent can be used to refer to SIF or other
types of images.

The ``Fingerprints:`` header has no effect if the bootstrap image is
not in SIF format.


.. note::

   The verification occurs before the bootstrap image is extracted
   into a temporary directory for the build process. The fingerprint
   check ensures the correct image was retrieved for the build, but
   does not protect against malicious changes that could be made
   during the build process on a compromised machine.


--------
Sections
--------

The main content of the bootstrap file is broken into sections. Different
sections add different content or execute commands at different times during the
build process. Note that if any command fails, the build process will halt.

Here is an example definition file that uses every available section. We will
discuss each section in turn. It is not necessary to include every section (or
any sections at all) within a def file. Furthermore, multiple sections of the
same name can be included and will be appended to one another during the build
process.

.. code-block:: singularity

    Bootstrap: library
    From: ubuntu:18.04
    Stage: build

    %setup
        touch /file1
        touch ${SINGULARITY_ROOTFS}/file2

    %files
        /file1
        /file1 /opt

    %environment
        export LISTEN_PORT=12345
        export LC_ALL=C

    %post
        apt-get update && apt-get install -y netcat
        NOW=`date`
        echo "export NOW=\"${NOW}\"" >> $SINGULARITY_ENVIRONMENT

    %runscript
        echo "Container was created $NOW"
        echo "Arguments received: $*"
        exec echo "$@"

    %startscript
        nc -lp $LISTEN_PORT

    %test
        grep -q NAME=\"Ubuntu\" /etc/os-release
        if [ $? -eq 0 ]; then
            echo "Container base is Ubuntu as expected."
        else
            echo "Container base is not Ubuntu."
            exit 1
        fi

    %labels
        Author d@sylabs.io
        Version v0.0.1

    %help
        This is a demo container used to illustrate a def file that uses all
        supported sections.

Although the order of the sections in the def file is unimportant, they have
been documented below in the order of their execution during the build process
for logical understanding.

%setup
======

During the build process, commands in the ``%setup`` section are first executed
on the host system outside of the container after the base OS has been installed.
You can reference the container file system with the ``$SINGULARITY_ROOTFS``
environment variable in the ``%setup`` section.

.. note::

    Be careful with the ``%setup`` section! This scriptlet is executed outside
    of the container on the host system itself, and is executed with elevated
    privileges when you run the build as ``root`` or with ``sudo``. Commands in
    ``%setup`` can alter and potentially damage the host.

    You should avoid ``%setup`` wherever possible, and work inside the container
    in the ``%post`` block instead.

Consider the example from the definition file above:

.. code-block:: singularity

    %setup
        touch /file1
        touch ${SINGULARITY_ROOTFS}/file2

Here, ``file1`` is created at the root of the file system **on the host**.
We'll use ``file1`` to demonstrate the usage of the ``%files`` section below.
The ``file2`` is created at the root of the file system **within the
container**.

In later versions of {Singularity} the ``%files`` section is provided as a safer
alternative to copying files from the host system into the container during the
build. Because of the potential danger involved in running the ``%setup``
scriptlet with elevated privileges on the host system during the build, it's
use is generally discouraged.

%files
======

The ``%files`` section allows you to copy files into the container with greater
safety than using the ``%setup`` section. Its general form is:

.. code-block:: singularity

    %files [from <stage>]
        <source> [<destination>]
        ...

Each line is a ``<source>`` and ``<destination>`` pair. The ``<source>`` is either:

  1. A valid path to a file or directory on your host system
  2. A valid glob pattern matching one or more files or directories on your host system
  3. A valid path in a previous stage of the build

The ``<destination>`` is a path inside the current container. If the
``<destination>`` path is omitted it will be assumed to be the same as ``<source>``.
To show how copying from your host system works, let's consider the example from
the definition file above:

.. code-block:: singularity

    %files
        /file1
        /file1 /opt

This ``%files`` scriptlet will copy ``/file1`` to the root of the container file
system and then make a second copy of ``file1`` within the container, inside
``/opt``, at ``/opt/file1``.

Copying Multiple Files with Patterns
------------------------------------

To copy multiple files or directories at a time you can specify a pattern as the
``<source>`` for a ``%files`` line. {Singularity} matches patterns to filenames
using the Go ``file.Match`` syntax:

.. code-block:: none

    '*'         matches any sequence of non-Separator characters
    '?'         matches any single non-Separator character
    '[' [ '^' ] { character-range } ']'
                character class (must be non-empty)
    c           matches character c (c != '*', '?', '\\', '[')
    '\\' c      matches character c

    character-range:
    c           matches character c (c != '\\', '-', ']')
    '\\' c      matches character c
    lo '-' hi   matches character c for lo <= c <= hi

(See: https://pkg.go.dev/path/filepath#Match)

Some simple examples:

* ``myfile*`` will match all files that have a name beginning with ``myfile``.
  E.g. ``myfile-blue`` and ``myfile-red``. 

* ``experiment???`` will match all files that have a name beginning with
  ``experiment`` and followed by any three characters. It will match
  ``experiment001``,``experiment002``, and ``experimentABC``, but not ``experimentA``.

* ``document[0-9]`` will match ``document1``, but not ``documentA`` nor ``document01``.

Copying Files Between stages
----------------------------

Files can also be copied from other stages, in a multi stage build, by providing
the source location in the previous stage and the destination in the current
container.

.. code-block:: singularity

  %files from stage_name
    /root/hello /bin/hello

The only difference in behavior between copying files from your host system and copying them
from previous stages is that in the former case symbolic links are always followed
during the copy to the container, while in the latter symbolic links are preserved.

Files in the ``%files`` section are always copied before the ``%post`` section is
executed so that they are available during the build and configuration process.

%app*
=====

In some circumstances, it may be redundant to build different containers for
each app with nearly equivalent dependencies. {Singularity} supports installing
apps within internal modules based on the concept of the `Scientific Filesystem (SCIF) <https://sci-f.github.io/>`_.
More information on defining and using SCIF Apps :ref:`here <apps>`.

%post
=====

This section is where you can download files from the internet with tools like ``git``
and ``wget``, install new software and libraries, write configuration files,
create new directories, etc.

Consider the example from the definition file above:

.. code-block:: singularity

    %post
        apt-get update && apt-get install -y netcat
        NOW=`date`
        echo "export NOW=\"${NOW}\"" >> $SINGULARITY_ENVIRONMENT


This ``%post`` scriptlet uses the Ubuntu package manager ``apt`` to update the
container and install the program ``netcat`` (that will be used in the
``%startscript`` section below).

The script is also setting an environment variable at build time.  Note that the
value of this variable cannot be anticipated, and therefore cannot be set during
the ``%environment`` section. For situations like this, the ``$SINGULARITY_ENVIRONMENT``
variable is provided. Redirecting text to this variable will cause it to be
written to a file called ``/.singularity.d/env/91-environment.sh`` that will be
sourced at runtime.

%test
=====

The ``%test`` section runs at the very end of the build process to
validate the container using a method of your choice. You can also
execute this scriptlet through the container itself, using the
``test`` command.

Consider the example from the def file above:

.. code-block:: singularity

    %test
        grep -q NAME=\"Ubuntu\" /etc/os-release
        if [ $? -eq 0 ]; then
            echo "Container base is Ubuntu as expected."
        else
            echo "Container base is not Ubuntu."
            exit 1
        fi


This (somewhat silly) script tests if the base OS is Ubuntu. You could
also write a script to test that binaries were appropriately
downloaded and built, or that software works as expected on custom
hardware. If you want to build a container without running the
``%test`` section (for example, if the build system does not have the
same hardware that will be used on the production system), you can do
so with the ``--notest`` build option:

.. code-block:: none

    $ sudo singularity build --notest my_container.sif my_container.def

Running the test command on a container built with this def file yields the
following:

.. code-block:: none

    $ singularity test my_container.sif
    Container base is Ubuntu as expected.

One common use of the ``%test`` section is to run a quick check that
the programs you intend to install in the container are present. If
you installed the program ``samtools``, which shows a usage screen when
run without any options, you might test it can be run with:

.. code-block:: singularity

    %test
        # Run samtools - exits okay with usage screen if installed
        samtools

If ``samtools`` is not successfully installed in the container then the
``singularity test`` will exit with an error such as ``samtools:
command not found``.

Some programs return an error code when run without mandatory
options. If you want to ignore this, and just check the program is
present and can be called, you can run it as ``myprog || true`` in
your test:

.. code-block:: singularity

    %test
        # Run bwa - exits with error code if installed and run without
        # options
        bwa || true

The ``|| true`` means that if the command before it is found but
returns an error code it will be ignored, and replaced with the error
code from ``true`` - which is always ``0`` indicating success.

Because the ``%test`` section is a shell scriptlet, complex tests are
possible. Your scriptlet should usually be written so it will exit
with a non-zero error code if there is a problem during the tests.

Now, the following sections are all inserted into the container filesystem in
single step:

%environment
============

The ``%environment`` section allows you to define environment variables that
will be set at runtime. Note that these variables are not made available at
build time by their inclusion in the ``%environment`` section. This means that
if you need the same variables during the build process, you should also define
them in your ``%post`` section. Specifically:

-  **during build**: The ``%environment`` section is written to a file in the
   container metadata directory. This file is not sourced.

-  **during runtime**: The file in the container metadata directory is sourced.

You should use the same conventions that you would use in a ``.bashrc`` or
``.profile`` file. Consider this example from the def file above:

.. code-block:: singularity

    %environment
        export LISTEN_PORT=12345
        export LC_ALL=C

The ``$LISTEN_PORT`` variable will be used in the ``%startscript`` section
below. The ``$LC_ALL`` variable is useful for many programs (often written in
Perl) that complain when no locale is set.

After building this container, you can verify that the environment variables are
set appropriately at runtime with the following command:

.. code-block:: none

    $ singularity exec my_container.sif env | grep -E 'LISTEN_PORT|LC_ALL'
    LISTEN_PORT=12345
    LC_ALL=C

In the special case of variables generated at build time, you can also add
environment variables to your container in the ``%post`` section.

At build time, the content of the ``%environment`` section is written to a file
called ``/.singularity.d/env/90-environment.sh`` inside of the container.  Text
redirected to the ``$SINGULARITY_ENVIRONMENT`` variable during ``%post`` is
added to a file called ``/.singularity.d/env/91-environment.sh``.

At runtime, scripts in ``/.singularity/env`` are sourced in order. This means
that variables in the ``%post`` section take precedence over those added  via
``%environment``.

See :ref:`Environment and Metadata <environment-and-metadata>` for more
information about the {Singularity} container environment.

.. _startscript:

%startscript
============

Similar to the ``%runscript`` section, the contents of the ``%startscript``
section is written to a file within the container at build time.  This file is
executed when the ``instance start`` command is issued.

Consider the example from the def file above.

.. code-block:: singularity

    %startscript
        nc -lp $LISTEN_PORT

Here the netcat program is used to listen for TCP traffic on the port indicated
by the ``$LISTEN_PORT`` variable (set in the ``%environment`` section above).
The script can be invoked like so:

.. code-block:: none

    $ singularity instance start my_container.sif instance1
    INFO:    instance started successfully

    $ lsof | grep LISTEN
    nc        19061               vagrant    3u     IPv4             107409      0t0        TCP *:12345 (LISTEN)

    $ singularity instance stop instance1
    Stopping instance1 instance of /home/vagrant/my_container.sif (PID=19035)


.. _runscript:

%runscript
==========

The contents of the ``%runscript`` section are written to a file within the
container that is executed when the container image is run (either via the
``singularity run`` command or by executing the container directly as a
command). When the container is invoked, arguments following the container name
are passed to the runscript. This means that you can (and should) process
arguments within your runscript.

Consider the example from the def file above:

.. code-block:: singularity

    %runscript
        echo "Container was created $NOW"
        echo "Arguments received: $*"
        exec echo "$@"

In this runscript, the time that the container was created is echoed via the
``$NOW`` variable (set in the ``%post`` section above). The options passed to
the container at runtime are printed as a single string (``$*``) and then they
are passed to echo via a quoted array (``$@``) which ensures that all of the
arguments are properly parsed by the executed command. The ``exec`` preceding
the final ``echo`` command replaces the current entry in the process table
(which originally was the call to {Singularity}). Thus the runscript shell process
ceases to exist, and only the process running within the container remains.

Running the container built using this def file will yield the following:

.. code-block:: none

    $ ./my_container.sif
    Container was created Thu Dec  6 20:01:56 UTC 2018
    Arguments received:

    $ ./my_container.sif this that and the other
    Container was created Thu Dec  6 20:01:56 UTC 2018
    Arguments received: this that and the other
    this that and the other


%labels
=======

The ``%labels`` section is used to add metadata to the file
``/.singularity.d/labels.json`` within your container. The general format is a
name-value pair.

Consider the example from the def file above:

.. code-block:: singularity

    %labels
        Author d@sylabs.io
        Version v0.0.1
        MyLabel Hello World


Note that labels are defined by key-value pairs. To define a label just add it
on the labels section and after the first space character add the correspondent value to the label.

In the previous example, the first label name is ``Author``` with a
value of ``d@sylabs.io``. The second label name is ``Version`` with a value of ``v0.0.1``.
Finally, the last label named ``MyLabel`` has the value of ``Hello World``.

To inspect the available labels on your image you can do so by running the following command:

.. code-block:: none

    $ singularity inspect my_container.sif

    {
      "Author": "d@sylabs.io",
      "Version": "v0.0.1",
      "MyLabel": "Hello World",
      "org.label-schema.build-date": "Thursday_6_December_2018_20:1:56_UTC",
      "org.label-schema.schema-version": "1.0",
      "org.label-schema.usage": "/.singularity.d/runscript.help",
      "org.label-schema.usage.singularity.deffile.bootstrap": "library",
      "org.label-schema.usage.singularity.deffile.from": "ubuntu:18.04",
      "org.label-schema.usage.singularity.runscript.help": "/.singularity.d/runscript.help",
      "org.label-schema.usage.singularity.version": "3.0.1"
    }

Some labels that are captured automatically from the build process. You can read
more about labels and metadata :ref:`here <environment-and-metadata>`.

%help
=====

Any text in the ``%help`` section is transcribed into a metadata file in the
container during the build. This text can then be displayed using the
``run-help`` command.

Consider the example from the def file above:

.. code-block:: singularity

    %help
        This is a demo container used to illustrate a def file that uses all
        supported sections.

After building the help can be displayed like so:

.. code-block:: none

    $ singularity run-help my_container.sif
        This is a demo container used to illustrate a def file that uses all
        supported sections.

------------------
Multi-Stage Builds
------------------

Starting with {Singularity} v3.2 multi-stage builds are supported where one environment
can be used for compilation, then the resulting binary can be copied into a final
environment. This allows a slimmer final image that does not require the entire
development stack.

.. code-block:: singularity

    Bootstrap: docker
    From: golang:1.12.3-alpine3.9
    Stage: devel

    %post
      # prep environment
      export PATH="/go/bin:/usr/local/go/bin:$PATH"
      export HOME="/root"
      cd /root

      # insert source code, could also be copied from the host with %files
      cat << EOF > hello.go
      package main
      import "fmt"

      func main() {
        fmt.Printf("Hello World!\n")
      }
    EOF

      go build -o hello hello.go


    # Install binary into the final image
    Bootstrap: library
    From: alpine:3.9
    Stage: final

    # install binary from stage one
    %files from devel
      /root/hello /bin/hello

The names of stages are arbitrary. Each of these sections will be executed in
the same order as described for a single stage build except the files from the
previous stage are copied before ``%setup`` section of the next stage. Files
can only be copied from stages declared before the current stage in the definition.
E.g., the ``devel`` stage in the above definition cannot copy files from the
``final`` stage, but the ``final`` stage can copy files from the ``devel`` stage.

.. _apps:

---------
SCIF Apps
---------

SCIF is a standard for encapsulating multiple apps into a container. A
container with SCIF apps has multiple entry points, and you can choose
which to run easily. Each entry point can carry out a different task
with its own environment, metadata etc., without the need for a
collection of different containers.

{Singularity} implements SCIF, and you can read more about how to use it
below.

SCIF is not specific to {Singularity}. You can learn more about it at the
project's site: `<https://sci-f.github.io/>`_ which includes extended
tutorials, the specification, and other information.

SCIF %app* sections
===================

SCIF apps within a {Singularity} container are created using ``%app*``
sections in a definition file. These ``%app*`` sections, which will impact the
way the container runs a specific ``--app`` can exist alongside any of the 
primary sections (i.e.  ``%post``,``%runscript``, ``%environment``, etc.).  As
with the other sections, the ordering of the ``%app*`` sections isn’t important.

The following runscript demonstrates how to build 2 different apps into the
same container using SCIF modules:

.. code-block:: singularity

    Bootstrap: docker
    From: ubuntu

    %environment
        GLOBAL=variables
        AVAILABLE="to all apps"

    ##############################
    # foo
    ##############################

    %apprun foo
        exec echo "RUNNING FOO"

    %applabels foo
       BESTAPP FOO

    %appinstall foo
       touch foo.exec

    %appenv foo
        SOFTWARE=foo
        export SOFTWARE

    %apphelp foo
        This is the help for foo.

    %appfiles foo
       foo.txt

    ##############################
    # bar
    ##############################

    %apphelp bar
        This is the help for bar.

    %applabels bar
       BESTAPP BAR

    %appinstall bar
        touch bar.exec

    %appenv bar
        SOFTWARE=bar
        export SOFTWARE

An ``%appinstall`` section is the equivalent of ``%post`` but for a particular
app. Similarly, ``%appenv`` equates to the app version of ``%environment`` and
so on.

After installing apps into modules using the ``%app*`` sections, the ``--app``
option becomes available allowing the following functions:

To run a specific app within the container:

.. code-block:: none

    % singularity run --app foo my_container.sif
    RUNNING FOO

The same environment variable, ``$SOFTWARE`` is defined for both apps in the def
file above. You can execute the following command to search the list of active
environment variables and ``grep`` to determine if the variable changes
depending on the app we specify:

.. code-block:: none

    $ singularity exec --app foo my_container.sif env | grep SOFTWARE
    SOFTWARE=foo

    $ singularity exec --app bar my_container.sif env | grep SOFTWARE
    SOFTWARE=bar

--------------------------------
Best Practices for Build Recipes
--------------------------------

When crafting your recipe, it is best to consider the following:

#. Always install packages, programs, data, and files into operating system
   locations (e.g. not ``/home``, ``/tmp`` , or any other directories that might
   get commonly binded on).

#. Document your container. If your runscript doesn’t supply help, write a
   ``%help`` or ``%apphelp`` section. A good container tells the user how to
   interact with it.

#. If you require any special environment variables to be defined, add them to
   the ``%environment`` and ``%appenv`` sections of the build recipe.

#. Files should always be owned by a system account (UID less than 500).

#. Ensure that sensitive files like ``/etc/passwd``, ``/etc/group``, and
   ``/etc/shadow`` do not contain secrets.

#. Build production containers from a definition file instead of a sandbox that
   has been manually changed. This ensures the greatest possibility of
   reproducibility and mitigates the "black box" effect.
