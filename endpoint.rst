================
Remote Endpoints
================

--------
Overview
--------

The ``remote`` command group allows users to manage the service endpoints
{Singularity} will interact with for many common command flows. This includes
managing credentials for image storage services, remote builders, and key 
servers used to locate public keys for SIF image verification. Currently,
there are three main types of remote endpoints managed by this command group:
the public Sylabs Cloud (or local {Singularity} Enterprise installation), OCI 
registries and keyservers.

-------------------
Public Sylabs Cloud
-------------------

Sylabs introduced the online `Sylabs Cloud
<https://cloud.sylabs.io/home>`_ to enable users to `Create
<https://cloud.sylabs.io/builder>`_, `Secure
<https://cloud.sylabs.io/keystore?sign=true>`_, and `Share
<https://cloud.sylabs.io/library>`_ their container
images with others.

A fresh, default installation of {Singularity} is configured to connect
to the public `cloud.sylabs.io <https://cloud.sylabs.io>`__
services. If you only want to use the public services you just need to
obtain an authentication token, and then ``singularity remote login``:

  1) Go to: https://cloud.sylabs.io/
  2) Click "Sign In" and follow the sign in steps.
  3) Click on your login id (same and updated button as the Sign in one).
  4) Select "Access Tokens" from the drop down menu.
  5) Enter a name for your new access token, such as "test token"
  6) Click the "Create a New Access Token" button.
  7) Click "Copy token to Clipboard" from the "New API Token" page.
  8) Run ``singularity remote login`` and paste the access token at the prompt.

Once your token is stored, you can check that you are able to connect
to the services with the ``status`` subcommand:

.. code:: console

    $ singularity remote status
    INFO:    Checking status of default remote.
    SERVICE    STATUS  VERSION             URI
    Builder    OK      v1.1.14-0-gc7a68c1  https://build.sylabs.io
    Consent    OK      v1.0.2-0-g2a24b4a   https://auth.sylabs.io/consent
    Keyserver  OK      v1.13.0-0-g13c778b  https://keys.sylabs.io
    Library    OK      v1.0.16-0-gb7eeae4  https://library.sylabs.io
    Token      OK      v1.0.2-0-g2a24b4a   https://auth.sylabs.io/token
    INFO:    Access Token Verified!

    Valid authentication token set (logged in).

If you see any errors you may need to check if your system requires
proxy environment variables to be set, or if a firewall is blocking
access to ``*.sylabs.io``. Talk to your system administrator.

You can interact with the public Sylabs Cloud using various {Singularity} commands:

`pull <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_pull.html>`_,
`push <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_push.html>`_,
`build --remote <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_build.html#options>`_,
`key <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_key.html>`_,
`search <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_search.html>`_,
`verify <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_verify.html>`_,
`exec <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_exec.html>`_,
`shell <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_shell.html>`_,
`run <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_run.html>`_,
`instance <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_instance.html>`_

.. note::

   Using ``docker://``, ``oras://`` and ``shub://`` URIs with these commands
   does not interact with the Sylabs Cloud.

-------------------------
Managing Remote Endpoints
-------------------------

Users can setup and switch between multiple remote endpoints, which
are stored in their ``~/.singularity/remote.yaml``
file. Alternatively, remote endpoints can be set system-wide by an
administrator.

Generally, users and administrators should manage remote endpoints
using the ``singularity remote`` command, and avoid editing
``remote.yaml`` configuration files directly.

.. note::

   The following commands in this section configures {Singularity} to use
   and authenticate to the public Sylabs Cloud, a private installation
   of {Singularity} Enterprise, or community-developed services that are
   API compatible.

List and Login to Remotes
=========================

To ``list`` existing remote endpoints, run this:

.. code-block:: none

    $ singularity remote list

    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                     GLOBAL  INSECURE  ORDER
    https://keys.sylabs.io  YES     NO        1*


The ``YES`` in the ``ACTIVE`` column for ``SylabsCloud`` shows that this is the
current default remote endpoint.
   
To ``login`` to a remote, for the first time or if your token expires
or was revoked:

.. code-block:: console

    # Login to the default remote endpoint
    $ singularity remote login
                
    # Login to another remote endpoint                
    $ singularity remote login <remote_name>

    # example...
    $ singularity remote login SylabsCloud
    singularity remote login SylabsCloud
    INFO:    Authenticating with remote: SylabsCloud
    Generate an API Key at https://cloud.sylabs.io/auth/tokens, and paste here:
    API Key: 
    INFO:    API Key Verified!

    
If you ``login`` to a remote that you already have a valid token for,
you will be prompted, and the new token will be verified, before it
replaces your existing credential. If you enter an incorrect token
your existing token will not be replaced:

.. code-block:: console
   
    $ singularity remote login
    An access token is already set for this remote. Replace it? [N/y]y
    Generate an access token at https://cloud.sylabs.io/auth/tokens, and paste it here.
    Token entered will be hidden for security.
    Access Token: 
    FATAL:   while verifying token: error response from server: Invalid Credentials

    # Previous token is still in place

.. note::

    It is important for users to be aware that the login command will store the
    supplied credentials or tokens unencrypted in your home directory.
    
Add & Remove Remotes
====================

To ``add`` a remote endpoint (for the current user only):

.. code-block:: none

    $ singularity remote add <remote_name> <remote_uri>

For example, if you have an installation of {Singularity} enterprise
hosted at enterprise.example.com:

.. code-block:: none

    $ singularity remote add myremote https://enterprise.example.com
   
    INFO:    Remote "myremote" added.
    INFO:    Authenticating with remote: myremote
    Generate an API Key at https://enterprise.example.com/auth/tokens, and paste here:
    API Key:

You will be prompted to setup an API key as the remote is added. The
web address needed to do this will always be given.

To ``add`` a global remote endpoint (available to all users on the
system) an administrative user should run:

.. code-block:: none

    $ sudo singularity remote add --global <remote_name> <remote_uri>

    # example..

    $ sudo singularity remote add --global company-remote https://enterprise.example.com
    [sudo] password for dave: 
    INFO:    Remote "company-remote" added.
    INFO:    Global option detected. Will not automatically log into remote.
   
.. note:: Global remote configurations can only be modified by the
     root user and are stored in the ``etc/singularity/remote.yaml``
     file, at the {Singularity} installation location.

Conversely, to ``remove`` an endpoint:

.. code-block:: none

    $ singularity remote remove <remote_name>

Use the ``--global`` option as the root user to remove a global
endpoint:

.. code-block:: none

    $ sudo singularity remote remove --global <remote_name>


Set the Default Remote
======================
    
A remote endpoint can be set as the default to use with commands such
as ``push``, ``pull`` etc. via ``remote use``:

.. code-block:: none

    $ singularity remote use <remote_name>

The default remote shows up with a ``YES`` under the ``ACTIVE`` column in the output of ``remote list``:

.. code-block:: none

    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME            URI                     ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud     cloud.sylabs.io         YES     YES     NO
    company-remote  enterprise.example.com  NO      YES     NO
    myremote        enterprise.example.com  NO      NO      NO

    Keyservers
    ==========

    URI                     GLOBAL  INSECURE  ORDER
    https://keys.sylabs.io  YES     NO        1*

    * Active cloud services keyserver

    $ singularity remote use myremote
    INFO:    Remote "myremote" now in use.

    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME            URI                     ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud     cloud.sylabs.io         NO      YES     NO
    company-remote  enterprise.example.com  NO      YES     NO
    myremote        enterprise.example.com  YES     NO      NO

    Keyservers
    ==========

    URI                       GLOBAL  INSECURE  ORDER
    https://keys.example.com  YES     NO        1*

    * Active cloud services keyserver


{Singularity} 3.7 introduces the ability for an administrator to make a remote
the only usable remote for the system by using the ``--exclusive`` flag:

.. code-block:: none

    $ sudo singularity remote use --exclusive company-remote
    INFO:    Remote "company-remote" now in use.
    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME            URI                     ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud     cloud.sylabs.io         NO      YES     NO
    company-remote  enterprise.example.com  YES     YES     YES
    myremote        enterprise.example.com  NO      NO      NO

    Keyservers
    ==========

    URI                       GLOBAL  INSECURE  ORDER
    https://keys.example.com  YES     NO        1*

    * Active cloud services keyserver

This, in turn, prevents users from changing the remote they use:

.. code-block:: none

    $ singularity remote use myremote
    FATAL:   could not use myremote: remote company-remote has been set exclusive by the system administrator

If you do not want to switch remote with ``remote use`` you can:

* Make ``push`` and ``pull`` use an alternative library server with
  the ``--library`` option.
* Make ``build --remote`` use an alternative remote builder with the
  ``--builder`` option.
* Make ``keys`` use an alternative keyserver with the ``-url`` option.

------------------------
Keyserver Configurations
------------------------

By default, {Singularity} will use the keyserver correlated to the active cloud
service endpoint. This behavior can be changed or supplemented via the
``add-keyserver`` and ``remove-keyserver`` commands. These commands allow an
administrator to create a global list of key servers used to verify container
signatures by default, where ``order 1`` is the first in the list. Other 
operations performed by {Singularity} that reach out to a keyserver will only
use the first entry, or ``order 1``, keyserver.

When we list our default remotes, we can see that the default keyserver is
``https://keys.sylabs.io`` and the asterisk next to its order indicates that
it is the keyserver associated to the current remote endpoint. We can also see
the ``INSECURE`` column indicating that {Singularity} will use TLS when
communicating with the keyserver.

.. code-block:: none

    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                     GLOBAL  INSECURE  ORDER
    https://keys.sylabs.io  YES     NO        1*

    * Active cloud services keyserver

We can add a key server to list of keyservers with:

.. code-block:: none

    $ sudo singularity remote add-keyserver https://pgp.example.com
    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                      GLOBAL  INSECURE  ORDER
    https://keys.sylabs.io   YES     NO        1*
    https://pgp.example.com  YES     NO        2

    * Active cloud services keyserver

Here we can see that the ``https://pgp.example.com`` keyserver was appended to
our list. If we would like to specify the order in the list that this key is
placed, we can use the ``--order`` flag:

.. code-block:: none

    $ sudo singularity remote add-keyserver --order 1 https://pgp.example.com
    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                      GLOBAL  INSECURE  ORDER
    https://pgp.example.com  YES     NO        1
    https://keys.sylabs.io   YES     NO        2*

    * Active cloud services keyserver

Since we specified ``--order 1``, the ``https://pgp.example.com`` keyserver was
placed as the first entry in the list and the default keyserver was moved to
second in the list. With the keyserver configuration above, all image default
image verification performed by {Singularity} will first reach out to
``https://pgp.example.com`` and then to ``https://keys.sylabs.io`` when
searching for public keys.

If a keyserver requires authentication before usage, users can login before
using it:

.. code-block:: none

    $ singularity remote login --username ian https://pgp.example.com
    Password (or token when username is empty): 
    INFO:    Token stored in /home/ian/.singularity/remote.yaml

Now we can see that ``https://pgp.example.com`` is logged in:

.. code-block:: none

    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                      GLOBAL  INSECURE  ORDER
    https://pgp.example.com  YES     NO        1
    https://keys.sylabs.io   YES     NO        2*

    * Active cloud services keyserver

    Authenticated Logins
    =================================

    URI                     INSECURE
    https://pgp.example.com NO

.. note::
    It is important for users to be aware that the login command will store the
    supplied credentials or tokens unencrypted in your home directory.

.. _sec:managing_oci_registries:

-----------------------
Managing OCI Registries
-----------------------

It is common for users of {Singularity} to use OCI registries as sources for
their container images. Some registries require credentials to access certain
images or the registry itself. Previously, the only methods in {Singularity} to
supply credentials to registries were to supply credentials for each command or
set environment variables for a single registry.
See :ref:`Authentication via Interactive Login <sec:authentication_via_docker_login>`
and :ref:`Authentication via Environment Variables <sec:authentication_via_environment_variables>`

{Singularity} 3.7 introduces the ability for users to supply credentials on a per
registry basis with the ``remote`` command group.

Users can login to an oci registry with the ``remote login`` command by
specifying a ``docker://`` prefix to the registry hostname:

.. code-block:: none

    $ singularity remote login --username ian docker://docker.io
    Password (or token when username is empty): 
    INFO:    Token stored in /home/ian/.singularity/remote.yaml

    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                     GLOBAL  INSECURE  ORDER
    https://keys.sylabs.io  YES     NO        1*

    * Active cloud services keyserver

    Authenticated Logins
    =================================

    URI                 INSECURE
    docker://docker.io  NO

Now we can see that ``docker://docker.io`` shows up under
``Authenticated Logins`` and {Singularity} will automatically supply the
configured credentials when interacting with DockerHub. We can also see
the ``INSECURE`` column indicating that {Singularity} will use TLS when
communicating with the registry.

We can login to multiple OCI registries at the same time:

.. code-block:: none

    $ singularity remote login --username ian docker://registry.example.com
    Password (or token when username is empty): 
    INFO:    Token stored in /home/ian/.singularity/remote.yaml

    $ singularity remote list
    Cloud Services Endpoints
    ========================

    NAME         URI              ACTIVE  GLOBAL  EXCLUSIVE
    SylabsCloud  cloud.sylabs.io  YES     YES     NO

    Keyservers
    ==========

    URI                     GLOBAL  INSECURE  ORDER
    https://keys.sylabs.io  YES     NO        1*

    * Active cloud services keyserver

    Authenticated Logins
    =================================

    URI                            INSECURE
    docker://docker.io             NO
    docker://registry.example.com  NO

{Singularity} will supply the correct credentials for the registry based off of
the hostname when using the following commands with a ``docker://`` or 
``oras://`` URI:

`pull <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_pull.html>`_,
`push <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_push.html>`_,
`build <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_build.html>`_,
`exec <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_exec.html>`_,
`shell <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_shell.html>`_,
`run <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_run.html>`_,
`instance <https://www.sylabs.io/guides/\{version\}/user-guide/cli/singularity_instance.html>`_


.. note::

    It is important for users to be aware that the login command will store the
    supplied credentials or tokens unencrypted in your home directory.
