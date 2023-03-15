.. _key_commands:

############
Key commands
############

.. _sec:key_commands:

{Singularity} 3.2 introduces the abilities to import, export and remove
PGP keys following the OpenPGP standard via `GnuPGP (GPG)
<https://www.gnupg.org/gph/en/manual.html>`_. These commands only modify
the local keyring and are not related to the cloud keystore.

.. _key_import:

****************************
Changes in {Singularity} 3.7
****************************

{Singularity} 3.7 introduces a global keyring which can be managed by
administrators with the new ``--global`` option. This global keyring is
used by ECL
(https://sylabs.io/guides/{adminversion}/admin-guide/configfiles.html#ecl-toml)
and allows administrators to manage public keys used during ECL image
verification.

******************
Key import command
******************

{Singularity} 3.2 allows you import keys reading either from binary or
armored key format and automatically detect if it is a private or public
key and add it to the correspondent local keystore.

To give a quick view on how it works, we will first consider the case in
which a user wants to import a secret (private) key to the local
keystore.

First we will check what's the status of the local keystore (which keys
are stored by the moment before importing a new key).

.. code:: singularity

   $ singularity key list --secret

.. note::

   Remember that using ``--secret`` flag will return the
   secret or private local keyring as output.

.. note::

   The ``--private`` flag is available as a synonym for ``--secret``, as is the
   shorthand ``-s``.

The output will look as it follows:

.. code:: singularity

   Private key listing (/home/joana/.singularity/sypgp/pgp-secret):

   0) U: Johnny Cash (none) <cash@sylabs.io>
   C: 2019-04-11 22:22:28 +0200 CEST
   F: 47282BDC661F58FA4BEBEF47CA576CBD8EF1A2B4
   L: 3072
   --------
   1) U: John Green (none) <john@sylabs.io>
   C: 2019-04-11 13:08:45 +0200 CEST
   F: 5720799FE7B048CF36FAB8445EE1E2BD7B6342C5
   L: 1024
   --------

.. note::

   Remember that running that same command but with sudo privilege, will
   give you a totally different list since it will be the correspondent
   keystore from user ``root``

After this, you can simply import the key you need by adding the exact
location to the file, let's say you own a gpg key file named
``pinkie-pie.asc`` which is a secret GPG key you want to import. Then
you will just need to run the following command to import your key:

.. code:: singularity

   $ singularity key import $HOME/pinkie-pie.asc

.. note::

   This location is considering your key was located on the ``$HOME``
   directory. You can specify any location to the file.

Since you're importing a private (secret) key, you will need to specify
the passphrase related to it and then a new passphrase to be added on
your local keystore.

.. code:: singularity

   Enter your old password :
   Enter a new password for this key :
   Retype your passphrase :
   Key with fingerprint 8C10B902F438E4D504C3ACF689FCFFAED5F34A77 successfully added to the keyring

After this you can see if that key was correctly added to your local
keystore by running ``singularity key list -s`` command:

.. code:: singularity

   Private key listing (/home/joana/.singularity/sypgp/pgp-secret):

     0) U: Johnny Cash (none) <cash@sylabs.io>
     C: 2019-04-11 22:22:28 +0200 CEST
     F: 47282BDC661F58FA4BEBEF47CA576CBD8EF1A2B4
     L: 3072
     --------
     1) U: John Green (none) <john@sylabs.io>
     C: 2019-04-11 13:08:45 +0200 CEST
     F: 5720799FE7B048CF36FAB8445EE1E2BD7B6342C5
     L: 1024
     --------
     2) U: Pinkie Pie (Eternal chaos comes with chocolate rain!) <balloons@sylabs.io>
     C: 2019-04-26 12:07:07 +0200 CEST
     F: 8C10B902F438E4D504C3ACF689FCFFAED5F34A77
     L: 1024
     --------

You will see the imported key at the bottom of the list. Remember you
can also import an ``ascii`` armored key and this will be automatically
detected by the ``key import`` command (no need to specify the format).

.. note::

   In case you would like to import a public key the process remains the
   same, as the import command will automatically detect whether this
   key to be imported is either public or private.

.. _key_export:

******************
Key export command
******************

The key export command allows you to export a key that is on your local
keystore. This key could be either private or public, and the key can be
exported on ``ASCII`` armored format or on binary format. Of course to
identify the keystore and the format the syntax varies from the ``key
import`` command.

For example to export a public key in binary format you can run:

.. code:: singularity

   $ singularity key export 8C10B902F438E4D504C3ACF689FCFFAED5F34A77 $HOME/mykey.asc

This will export a public binary key named ``mykey.asc`` and will save
it under the home folder. If you would like to export the same public
key but in an ``ASCII`` armored format, you would need to run the
following command:

.. code:: singularity

   $ singularity key export --armor 8C10B902F438E4D504C3ACF689FCFFAED5F34A77 $HOME/mykey.asc

And in the case in which you may need to export a secret key on
``ASCII`` armored format, you would need to specify from where to find
the key, since the fingerprint is the same.

.. code:: singularity

   $ singularity key export --armor --secret 8C10B902F438E4D504C3ACF689FCFFAED5F34A77 $HOME/mykey.asc

and on binary format instead:

.. code:: singularity

   $ singularity key export --secret 8C10B902F438E4D504C3ACF689FCFFAED5F34A77 $HOME/mykey.asc

.. note::

   Exporting keys will not change the status of your local keystore or
   keyring. This will just obtain the content of the keys and save it on
   a local file on your host.

.. note::

   The ``--private`` flag is available as a synonym for ``--secret``, as is the
   shorthand ``-s``.

.. _key_remove:

******************
Key remove command
******************

In case you would want to remove a public key from your public local
keystore, you can do so by running the following command:

.. code:: singularity

   $ singularity key remove 8C10B902F438E4D504C3ACF689FCFFAED5F34A77

.. note::

   Remember that this will only delete the public key and not the
   private one with the same matching fingerprint.

If you want to remove a private key from your local keystore, you can do so by
passing the `--secret` flag to `key remove`:

.. code:: singularity

   $ singularity key remove --secret 8C10B902F438E4D504C3ACF689FCFFAED5F34A77

.. note::

   Remember that this will only delete the private key and not the
   public one with the same matching fingerprint.

.. note::

   The ``--private`` flag is available as a synonym for ``--secret``, as is the
   shorthand ``-s``.

