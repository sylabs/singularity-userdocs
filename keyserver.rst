.. _keyserver:

####################
Keyserver Management
####################

By default, {Singularity} will use the keyserver defined by the active
:ref:`remote endpoint<endpoint>`'s service discovery file. This behavior can be
changed or supplemented using the ``key`` command and, in particular, its
subcommands ``add`` and ``remove``. These allow an administrator to create a
global list of keyservers that will be used to verify container signatures by
default. When verifying container signatures, {Singularity} consults them
according to a configured *order* (with the keyserver whose order is ``1``
consulted first, then the one whose order is ``2``, and so forth). Other
operations performed by {Singularity} that reach out to a keyserver will only
use the first one (whose order is ``1``).

.. note::

   In previous versions of {Singularity}, the functionality described here was
   grouped together with :ref:`remote endpoint management<endpoint>` under the
   ``remote`` command group. Beginning with version 4.0, this functionality has
   been given its own top-level command group, ``keyserver``.

The ``list`` subcommand allows the user to examine the set of currently
configured keyservers:

.. code:: console

   $ singularity keyserver list

   SylabsCloud*^
      #1  https://keys.sylabs.io  🔒

   (* = system endpoint, ^ = default endpoint,
    + = user is logged in directly to this keyserver)

We can see in the output of the ``list`` subcommand that "SylabsCloud" is the
*default* remote endpoint (in other words, the endpoint that will be used by all
{SingularityCE} commands unless otherwise specified), and that it is a *global*
(in other words, system-level) endpoint. Furthermore, the lock icon next to
``https://keys.sylabs.io`` indicates that TLS will be used when communicating
with this keyserver.

We can add a key server to list of keyservers as follows:

.. code:: console

   $ sudo singularity keyserver add https://pgp.example.com
   $ singularity keyserver list

   SylabsCloud*^
      #1  https://keys.sylabs.io   🔒
      #2  https://pgp.example.com  🔒

   (* = system endpoint, ^ = default endpoint,
    + = user is logged in directly to this keyserver)

Here, we see that the ``https://pgp.example.com`` keyserver was
added to the list. We can specify the order in the list in which this keyserver
should be added, by using the ``--order`` flag:

.. code:: console

   $ sudo singularity keyserver add --order 1 https://pgp.example.com
   $ singularity keyserver list

   SylabsCloud*^
      #1  https://pgp.example.com  🔒
      #2  https://keys.sylabs.io   🔒

   (* = system endpoint, ^ = default endpoint,
    + = user is logged in directly to this keyserver)

Since we specified ``--order 1``, the ``https://pgp.example.com`` keyserver was
added as the first entry in the list, and the default keyserver was moved to
second in the list. With this keyserver configuration, all default image
verification performed by {Singularity} will, when searching for public keys,
reach out to ``https://pgp.example.com`` first, and only then to
``https://keys.sylabs.io``.

If a keyserver requires authentication prior to being used, users can login
as follows, supplying the password or an API token at the prompt:

.. code:: console

   $ singularity keyserver login --username myname https://pgp.example.com
   Password / Token:
   INFO:    Token stored in /home/myuser/.singularity/remote.yaml

The output of `keyserver list` will now show that we are logged in to
``https://pgp.example.com``:

.. code:: console

   $ singularity keyserver list

   SylabsCloud *^
      #1  https://pgp.example.com          🔒  +
      #2  https://keys.sylabs.io           🔒

   (* = system endpoint, ^ = default endpoint,
    + = user is logged in directly to this keyserver)

.. note::

   It is important for users to be aware that the ``keyserver login`` command
   will store the supplied credentials or tokens unencrypted in your home
   directory.

