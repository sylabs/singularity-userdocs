.. _endpoint:

################
Remote Endpoints
################

********
Overview
********

The ``remote`` command group allows users to manage the remote endpoint(s) that
{Singularity} interacts with (the public Sylabs Cloud, or a local Singularity
Enterprise installation).

.. note::

   In previous versions of {Singularity}, the ``remote`` command group also
   included subcommands for interacting with OCI registries (for image storage
   services), as well as keyservers (used to locate public keys for SIF image
   verification). Beginning with version 4.0, this functionality has been moved
   to dedicated top-level command groups: :ref:`registry<registry>` and
   :ref:`keyserver<keyserver>`, respectively.

*******************
Public Sylabs Cloud
*******************

Sylabs introduced the online `Sylabs Cloud <https://cloud.sylabs.io/home>`_ to
enable users to `Create <https://cloud.sylabs.io/builder>`_ container images,
`Secure <https://cloud.sylabs.io/keystore?sign=true>`_ them, and `Share
<https://cloud.sylabs.io/library>`_ them with others.

A fresh, default installation of {Singularity} is configured to connect to the
public services available at `cloud.sylabs.io <https://cloud.sylabs.io>`__. If
you only want to use these public services, all you need to do is obtain an
authentication token, which you then provide to ``singularity remote login``:

   #. Go to: https://cloud.sylabs.io/
   #. Click "Sign In" and follow the sign-in steps.
   #. Click on your login id, which, after sign-in, should appear on the right
      side of the navigation-bar at the top of the page.
   #. Select "Access Tokens" from the drop down menu.
   #. Enter a name for your new access token, such as "test token".
   #. Click the "Create a New Access Token" button.
   #. Click "Copy token to Clipboard" from the "New API Token" page.
   #. Run ``singularity remote login`` and paste the access token when
      prompted.

Once your token is stored, you can check that you are able to connect to
the services by using the ``status`` subcommand:

.. code:: console

   $ singularity remote status
   INFO:    Checking status of default remote.
   SERVICE    STATUS  VERSION                  URI
   Builder    OK      v1.6.9-rc.4-0-g87336319  https://build.sylabs.io
   Consent    OK      v1.7.0-0-g66ba1a9        https://auth.sylabs.io/consent
   Keyserver  OK      v1.18.12-0-gab541fb      https://keys.sylabs.io
   Library    OK      v0.3.8-rc.6-0-g630cdaa   https://library.sylabs.io
   Token      OK      v1.7.0-0-g66ba1a9        https://auth.sylabs.io/token

   Logged in as: myname <myemail@example.com>

   INFO:    Access Token Verified!

   Valid authentication token set (logged in).

If you see any errors, you may need to check if your system requires the setting
of environment variables for a network proxy, or if a firewall may be blocking
access to ``*.sylabs.io``. Consult your system administrator.

You can interact with the public Sylabs Cloud using various {Singularity}
commands:

`pull
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_pull.html>`__,
`push
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_push.html>`__,
`build --remote
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_build.html#options>`__,
`key
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_key.html>`__,
`search
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_search.html>`__,
`verify
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_verify.html>`__,
`exec
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_exec.html>`__,
`shell
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_shell.html>`__,
`run
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_run.html>`__,
`instance
<https://www.sylabs.io/guides/{version}/user-guide/cli/singularity_instance.html>`__

.. note::

   Using the commands listed above will *not* interact with the Sylabs Cloud if
   given URIs beginning with ``docker://``, ``oras://`` or ``shub://``.

*************************
Managing Remote Endpoints
*************************

Users can set up and switch between multiple remote endpoints, which will be
stored in their ``~/.singularity/remote.yaml`` file. Alternatively, remote
endpoints can be set on a system-wide basis by an administrator.

A remote endpoint may be the public Sylabs Cloud, a private installation of
Singularity Enterprise, or any community-developed service that is
API-compatible.

Generally, users and administrators should manage remote endpoints using
the ``singularity remote`` command, and avoid editing ``remote.yaml``
configuration files directly.

Listing and Logging In to Remote Endpoints
==========================================

To ``list`` existing remote endpoints, run the following:

.. code:: console

   $ singularity remote list

   NAME         URI              DEFAULT?  GLOBAL?  EXCLUSIVE?  SECURE?
   SylabsCloud  cloud.sylabs.io  ✓         ✓                    ✓

The ``✓`` in the ``DEFAULT?`` column for ``SylabsCloud`` shows that this
is the current default remote endpoint.

To ``login`` to a remote for the first time, or when a token needs to be
replaced (if it has expired or been revoked), run the following:

.. code:: console

   # Login to the default remote endpoint
   $ singularity remote login

   # Login to another remote endpoint
   $ singularity remote login <remote_name>

   # example:
   $ singularity remote login SylabsCloud
   Generate an access token at https://cloud.sylabs.io/auth/tokens, and paste it here.
   Token entered will be hidden for security.
   Access Token:
   INFO:    Access Token Verified!
   INFO:    Token stored in /home/myuser/.singularity/remote.yaml

If you ``login`` to a remote that you already have a valid token for, you will
be prompted for confirmation that you indeed want to replace the current token,
and the new token will be verified before it replaces your existing credential.
If you enter an incorrect token your existing token will not be replaced,

.. code:: console

   $ singularity remote login
   An access token is already set for this remote. Replace it? [y/N] y
   Generate an access token at https://cloud.sylabs.io/auth/tokens, and paste it here.
   Token entered will be hidden for security.
   Access Token:
   FATAL:   while verifying token: error response from server: Invalid Credentials

   # Previous token is still in place

.. note::

   It is important for users to be aware that the ``remote login`` command will
   store the supplied credentials or tokens **unencrypted** in your home
   directory. Please ensure that the access permissions on your home directory
   are set accordingly, to protect your credentials from unwanted access.

Adding and Removing Remote Endpoints
====================================

To ``add`` a remote endpoint (for the current user only):

.. code:: console

   $ singularity remote add <remote_name> <remote_uri>

For example, if you have an installation of {Singularity} enterprise
hosted at enterprise.example.com:

.. code:: console

   $ singularity remote add myremote https://enterprise.example.com
   INFO:    Remote "myremote" added.
   Generate an access token at https://enterprise.example.com/auth/tokens, and paste it here.
   Token entered will be hidden for security.
   Access Token:

You will be prompted to setup an API key as the remote is added. As the example
above shows, the output of the ``add`` subcommand will provide you with the web
address you need to visit in order to generate your new access token.

To ``add`` a global remote endpoint (available to all users on the
system), an administrative user should run:

.. code:: console

   $ sudo singularity remote add --global <remote_name> <remote_uri>

   # example...
   $ sudo singularity remote add --global company-remote https://enterprise7.example.com
   INFO:    Remote "company-remote" added.
   INFO:    Global option detected. Will not automatically log into remote.

.. note::

   Global remote configurations can only be modified by the root user, and are
   stored in the ``etc/singularity/remote.yaml`` file under the {Singularity}
   installation directory.

Conversely, to ``remove`` an endpoint:

.. code:: console

   $ singularity remote remove <remote_name>

Use the ``--global`` option as the root user to remove a global
endpoint:

.. code:: console

   $ sudo singularity remote remove --global <remote_name>

Insecure (HTTP) Endpoints
-------------------------

Starting with {Singularity} 3.9, if you are using a endpoint that only exposes
its service discovery file over an insecure HTTP connection, it can be added by
specifying the ``--insecure`` flag:

.. code:: console

   $ sudo singularity remote add --global --insecure test http://test.example.com
   INFO:    Remote "test" added.
   INFO:    Global option detected. Will not automatically log into remote.

This flag causes HTTP to be used instead of HTTPS *for service discovery only*. The
protocol used to access individual library-, build- and keyservice-URLs is
determined by the contents of the service discovery file.

Set the Default Remote
======================

To use a given remote endpoint as the default for commands such as ``push``,
``pull``, etc., use the ``remote use`` command:

.. code:: console

   $ singularity remote use <remote_name>

The remote designated as default shows up with a ``YES`` under the ``ACTIVE``
column in the output of ``remote list``:

.. code:: console

   $ singularity remote list

   NAME            URI                      DEFAULT?  GLOBAL?  EXCLUSIVE?  SECURE?
   SylabsCloud     cloud.sylabs.io                    ✓                    ✓
   company-remote  enterprise7.example.com            ✓                    ✓
   myremote        enterprise.example.com   ✓                              ✓
   test            test.example.com                   ✓                    ✓

   $ singularity remote use SylabsCloud
   INFO:    Remote "SylabsCloud" now in use.

   $ singularity remote list

   NAME            URI                      DEFAULT?  GLOBAL?  EXCLUSIVE?  SECURE?
   SylabsCloud     cloud.sylabs.io          ✓         ✓                    ✓
   company-remote  enterprise7.example.com            ✓                    ✓
   myremote        enterprise.example.com                                  ✓
   test            test.example.com                   ✓                    ✓

In the example above, the default remote at the start (before being changed to
``SylabsCloud``) was ``myremote``. That is because adding a new remote endpoint
automatically makes the newly-added endpoint the default one, and the same user
had previously used the ``remote add`` command to add the ``myremote`` endpoint.
This behavior can be suppressed by passing the ``--no-default`` flag to the
``remote add`` command, which will then add a new remote endpoint but leave the
default endpoint unchanged:

.. code:: console

   $ singularity remote add --no-default myotherremote https://enterprise2.example.com
   INFO:    Remote "myotherremote" added.
   Generate an access token at https://enterprise2.example.com/auth/tokens, and paste it here.
   Token entered will be hidden for security.
   Access Token:

  $ singularity remote list

   NAME            URI                      DEFAULT?  GLOBAL?  EXCLUSIVE?  SECURE?
   SylabsCloud     cloud.sylabs.io          ✓         ✓                    ✓
   company-remote  enterprise7.example.com            ✓                    ✓
   myotherremote   enterprise2.example.com                                 ✓
   myremote        enterprise.example.com                                  ✓
   test            test.example.com                   ✓                    ✓


{Singularity} 3.7 introduces the ability for an administrator to make a remote
the only usable remote for the system, using the ``--exclusive`` flag:

.. code:: console

   $ sudo singularity remote use --exclusive company-remote
   INFO:    Remote "company-remote" now in use.

   $ singularity remote list

   NAME            URI                      DEFAULT?  GLOBAL?  EXCLUSIVE?  SECURE?
   SylabsCloud     cloud.sylabs.io                    ✓                    ✓
   company-remote  enterprise7.example.com  ✓         ✓        ✓           ✓
   myotherremote   enterprise2.example.com                                 ✓
   myremote        enterprise.example.com                                  ✓
   test            test.example.com                   ✓                    ✓

This, in turn, prevents users from changing the remote they use:

.. code:: console

   $ singularity remote use myremote
   FATAL:   could not use myremote: remote company-remote has been set exclusive by the system administrator

If you do not want to switch remote with ``remote use``, you can:

-  Instruct ``push`` and ``pull`` commands to use an alternative library server
   using the ``--library`` option (for example:
   ``singularity pull -F --library https://library.example.com library://alpine``).
   Note that the URL provided to the ``--library`` option is the URL of the
   library service itself, not the service discovery URL for the entire remote.
-  Instruct the ``build --remote`` commands to use an alternative remote builder
   using the ``--builder`` option.
-  Instruct certain subcommands of the ``key`` command to use an alternative
   keyserver using the ``--url`` option (for example:
   ``singularity key search --url https://keys.example.com foobar``).

