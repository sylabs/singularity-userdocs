.. _plugins:

#######
Plugins
#######

********
Overview
********

A {Singularity} plugin is a package that can be dynamically loaded by the
{Singularity} runtime, augmenting {Singularity} with experimental, non-standard
and/or vendor-specific functionality.

Plugins can influence the behaviour of {Singularity} in specific ways:

* A cli plugin can use the ``Command`` callback to add or modify CLI
  subcommands and/or flags.
* A cli plugin can use the ``SingularityEngineConfig`` callback to change the
  container configuration before it is passed to the runtime, e.g. adding bind
  mounts etc.
* A runtime plugin can use the ``MonitorContainer`` callback to watch the
  container process as it is executing.
* A runtime plugin can use the ``PostStartProcess`` callback to carry out a task
  after the container has been started.
* A runtime plugin can use the ``RegisterImageDriver`` callback to implement an
  alternative way of providing a container image to execute.

**************************
Limitations / Requirements
**************************

The way that plugin functionality is implemented in the Go language, which
{Singularity} is written with, is quite restrictive.

Go plugins must be built with the same Go version, and set of dependencies, as
the main program they will be loaded into. This means it is generally
impractical to develop and build plugins except in lock-step with the main
{Singularity} source tree.

Functionality that can be implemented with plugins is limited to the scope of
the exposed plugin callbacks. Container runtimes such as {Singularity} execute
using multiple processes, with distinct boundaries that limit the influence a
plugin can have.

If you are considering writing a plugin for {Singularity} you may wish to
investigate whether the feature can be contributed to the main source tree
directly via a PR. This simplifies future maintenance, and avoids the
limitations of Go plugins.

*************
Using Plugins
*************

The ``list`` command prints the currently installed plugins.

.. code::

   $ singularity plugin list
   There are no plugins installed.

Plugins are packaged and distributed as binaries encoded with the versatile
Singularity Image Format (SIF). However, plugin authors may also distribute the
source code of their plugins. A plugin can be compiled from its source code with
the ``compile`` command. A number of example plugins are included in the
``examples/plugins`` directory of the {Singularity} source.

.. code::

   $ singularity plugin compile examples/plugins/cli-plugin/
   INFO:    Plugin built to: /home/dtrudg/Git/singularity/examples/plugins/cli-plugin/cli-plugin.sif

Upon successful compilation, a SIF file will appear in the directory of the
plugin's source code.

.. code::

   $ ls examples/plugins/cli-plugin/ | grep sif
   cli-plugin.sif

.. note::

   Due to the structure of the {Singularity} project, and the strict
   requirements of Go plugin compilation, **all** plugins must be compiled from
   within the {Singularity} source code tree.

   The ability to compile plugins outside of the {Singularity} tree, that
   previously existed, has been removed due to incompatible changes in Go 1.18.

Every plugin encapsulates various information such as the plugin's
author, the plugin's version, etc. To view this information about a
plugin, use the ``inspect`` command.

.. code::

   $ singularity plugin inspect examples/plugins/cli-plugin/cli-plugin.sif
   Name: github.com/sylabs/singularity/cli-example-plugin
   Description: This is a short example CLI plugin for Singularity
   Author: Sylabs Team
   Version: 0.1.0

To compile a plugin, use the ``compile`` command.

.. code::

    $ singularity plugin compile examples/plugins/log-plugin/
    INFO:    Plugin built to: /home/myuser/singularity/examples/plugins/log-plugin/log-plugin.sif

.. note::

    Before using the ``plugin compile`` subcommand, make sure that you trust the
    origin of the plugin, and that you are certain it does not contain any
    malicious code.

To install a plugin, use the ``install`` command. This operation
requires root privilege.

.. code::

   $ sudo singularity plugin install examples/plugins/cli-plugin/cli-plugin.sif
   $ singularity plugin list
   ENABLED  NAME
       yes  sylabs.io/cli-plugin

.. note::

    Before using the ``plugin install`` subcommand, make sure that you trust the
    origin of the plugin, and that you are certain it does not contain any
    malicious code.

    For further information on verifying the contents of SIF files using
    cryptographic signatures, see the :ref:`Sign and Verify section <signNverify>`.

After successful installation, the plugin will automatically be enabled.
Any plugin can be disabled with the ``disable`` command and re-enabled
with the ``enable`` command. Both of these operations require root
privilege.

.. code::

   $ sudo singularity plugin disable sylabs.io/cli-plugin
   $ singularity plugin list
   ENABLED  NAME
        no  sylabs.io/cli-plugin

   $ sudo singularity plugin enable sylabs.io/cli-plugin
   $ singularity plugin list
   ENABLED  NAME
       yes  sylabs.io/cli-plugin

Finally, to uninstall a plugin, use the ``uninstall`` command. This
operation requires root privilege.

.. code::

   $ sudo singularity plugin uninstall sylabs.io/cli-plugin
   Uninstalled plugin "sylabs.io/cli-plugin".

   $ singularity plugin list
   There are no plugins installed.

****************
Writing a Plugin
****************

Developers interested in writing {Singularity} plugins can get started
by reading the `Go documentation
<https://godoc.org/github.com/sylabs/singularity/pkg/plugin>`_ for the
plugin package.

Example plugins can be found in the {Singularity} `source code
<https://github.com/sylabs/singularity/tree/main/examples/plugins>`_.
