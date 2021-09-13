.. _signNverify:

================================
Signing and Verifying Containers
================================


.. _sec:signNverify:

{Singularity} 3.0 introduced the ability to create and manage PGP keys and use
them to sign and verify containers. This provides a trusted method for
{Singularity} users to share containers. It ensures a bit-for-bit reproduction
of the original container as the author intended it.

.. note::

    {Singularity} 3.6.0 uses a new signature format. Containers signed
    by 3.6.0 cannot be verifed by older versions of {Singularity}.

    To verify containers signed with older versions of {Singularity} using 3.6.0
    the ``--legacy-insecure`` flag must be provided to the ``singularity verify`` command.


.. _verify_container_from_library:

-----------------------------------------------
Verifying containers from the Container Library
-----------------------------------------------

The ``verify`` command will allow you to verify that a container has been
signed using a PGP key. To use this feature with images that you pull from the
container library, you must first generate an access token to the Sylabs Cloud.
If you don't already have a valid access token, follow these steps:

  1) Go to: https://cloud.sylabs.io/
  2) Click "Sign In" and follow the sign in steps.
  3) Click on your login id (same and updated button as the Sign in one).
  4) Select "Access Tokens" from the drop down menu.
  5) Enter a name for your new access token, such as "test token"
  6) Click the "Create a New Access Token" button.
  7) Click "Copy token to Clipboard" from the "New API Token" page.
  8) Run ``singularity remote login`` and paste the access token at the prompt.

Now you can verify containers that you pull from the library, ensuring they are
bit-for-bit reproductions of the original image.

.. code-block:: none

    $ singularity verify alpine_latest.sif 

    Container is signed by 1 key(s):

    Verifying partition: FS:
    8883491F4268F173C6E5DC49EDECE4F3F38D871E
    [REMOTE]  Sylabs Admin <support@sylabs.io>
    [OK]      Data integrity verified

    INFO:    Container verified: alpine_latest.sif

In this example you can see that **Sylabs Admin** has signed the container.

.. _sign_your_own_containers:

---------------------------
Signing your own containers
---------------------------

Generating and managing PGP keys
================================

To sign your own containers you first need to generate one or more keys.

If you attempt to sign a container before you have generated any keys,
{Singularity} will guide you through the interactive process of creating a new
key. Or you can use the ``newpair`` subcommand in the ``key`` command group
like so:.

.. code-block:: none

    $ singularity key newpair
    
    Enter your name (e.g., John Doe) : David Trudgian
    Enter your email address (e.g., john.doe@example.com) : david.trudgian@sylabs.io
    Enter optional comment (e.g., development keys) : demo
    Enter a passphrase : 
    Retype your passphrase : 
    Would you like to push it to the keystore? [Y,n] Y
    Generating Entity and OpenPGP Key Pair... done
    Key successfully pushed to: https://keys.sylabs.io

Note that I chose ``Y`` when asked if I wanted to push my key to the
keystore. This will push my public key to whichever keystore has been
configured by the ``singularity remote`` command, so that it can be
retrieved by other users running ``singularity verify``. If you do not
wish to push your public key, say ``n`` during the ``newpair``
process.
    

The ``list`` subcommand will show you all of the keys you have created or saved
locally.`

.. code-block:: none

    $ singularity key list

    Public key listing (/home/dave/.singularity/sypgp/pgp-public):

    0) U: David Trudgian (demo) <david.trudgian@sylabs.io>
       C: 2019-11-15 09:54:54 -0600 CST
       F: E5F780B2C22F59DF748524B435C3844412EE233B
       L: 4096
       --------

In the output above the index of my key is ``0`` and the letters stand
for the following:

       - U: User
       - C: Creation date and time
       - F: Fingerprint
       - L: Key length

If you chose not to push your key to the keystore during the ``newpair`` process, but later wish to, you can push it to a keystore configured using ``singularity remote`` like so:

.. code-block:: none

    $ singularity key push E5F780B2C22F59DF748524B435C3844412EE233B
    
    public key `E5F780B2C22F59DF748524B435C3844412EE233B` pushed to server successfully

If you delete your local public PGP key, you can always locate and download it
again like so.

.. code-block:: none

    $ singularity key search Trudgian

    Showing 1 results

    KEY ID    BITS  NAME/EMAIL
    12EE233B  4096  David Trudgian (demo) <david.trudgian@sylabs.io>  

    $ singularity key pull 12EE233B
    
    1 key(s) added to keyring of trust /home/dave/.singularity/sypgp/pgp-public

But note that this only restores the *public* key (used for verifying) to your
local machine and does not restore the *private* key (used for signing).

.. _searching_for_keys:

Searching for keys
==================

{Singularity} allows you to search the keystore for public keys. You can search for names,
emails, and fingerprints (key IDs). When searching for a fingerprint, you need to use ``0x``
before the fingerprint, check the example:

.. code-block:: none

    # search for key ID:
    $ singularity key search 0x8883491F4268F173C6E5DC49EDECE4F3F38D871E

    # search for the sort ID:
    $ singularity key search 0xF38D871E

    # search for user:
    $ singularity key search Godlove

    # search for email:
    $ singularity key search @gmail.com

Signing and validating your own containers
==========================================

Now that you have a key generated, you can use it to sign images like so:

.. code-block:: none

    $ singularity sign my_container.sif 

    Signing image: my_container.sif
    Enter key passphrase : 
    Signature created and applied to my_container.sif

Because your public PGP key is saved locally you can verify the image without
needing to contact the Keystore.

.. code-block:: none

    $ singularity verify my_container.sif
    Verifying image: my_container.sif
    [LOCAL]   Signing entity: David Trudgian (Demo keys) <david.trudgian@sylabs.io>
    [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
    Objects verified:
    ID  |GROUP   |LINK    |TYPE
    ------------------------------------------------
    1   |1       |NONE    |Def.FILE
    2   |1       |NONE    |JSON.Generic
    3   |1       |NONE    |FS
    Container verified: my_container.sif


If you've pushed your key to the Keystore you can also verify this
image in the absence of a local public key.  To demonstrate this,
first ``remove`` your local public key, and then try to use the
``verify`` command again.

.. code-block:: none

    $ singularity key remove E5F780B2C22F59DF748524B435C3844412EE233B

    $ singularity verify my_container.sif
    Verifying image: my_container.sif
    [REMOTE]   Signing entity: David Trudgian (Demo keys) <david.trudgian@sylabs.io>
    [REMOTE]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
    Objects verified:
    ID  |GROUP   |LINK    |TYPE
    ------------------------------------------------
    1   |1       |NONE    |Def.FILE
    2   |1       |NONE    |JSON.Generic
    3   |1       |NONE    |FS
    Container verified: my_container.sif


Note that the ``[REMOTE]`` message shows the key used for verification
was obtained from the keystore, and is not present on your local
computer. You can retrieve it, so that you can verify even if you are
offline with ``singularity key pull``

.. code-block:: none

    $ singularity key pull E5F780B2C22F59DF748524B435C3844412EE233B

    1 key(s) added to keyring of trust /home/dave/.singularity/sypgp/pgp-public


Advanced Signing - SIF IDs and Groups
=====================================

As well as the default behaviour, which signs all objects,
fine-grained control of signing is possible.

If you ``sif list`` a SIF file you will see it is comprised of a
number of objects. Each object has an ``ID``, and belongs to a
``GROUP``.

.. code-block:: none

    $ singularity sif list my_container.sif 

    Container id: e455d2ae-7f0b-4c79-b3ef-315a4913d76a
    Created on:   2019-11-15 10:11:58 -0600 CST
    Modified on:  2019-11-15 10:11:58 -0600 CST
    ----------------------------------------------------
    Descriptor list:
    ID   |GROUP   |LINK    |SIF POSITION (start-end)  |TYPE
    ------------------------------------------------------------------------------
    1    |1       |NONE    |32768-32800               |Def.FILE
    2    |1       |NONE    |36864-36961               |JSON.Generic
    3    |1       |NONE    |40960-25890816            |FS (Squashfs/*System/amd64)


I can choose to sign and verify a specific object with the ``--sif-id`` option
to ``sign`` and ``verify``.

.. code-block:: none

    $ singularity sign --sif-id 1 my_container.sif 
    Signing image: my_container.sif
    Enter key passphrase : 
    Signature created and applied to my_container.sif 

    $ singularity verify --sif-id 1 my_container.sif
    Verifying image: my_container.sif
    [LOCAL]   Signing entity: David Trudgian (Demo keys) <david.trudgian@sylabs.io>
    [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
    Objects verified:
    ID  |GROUP   |LINK    |TYPE
    ------------------------------------------------
    1   |1       |NONE    |Def.FILE
    Container verified: my_container.sif


Note that running the ``verify`` command without specifying the specific sif-id
gives a fatal error. The container is not considered verified as whole because
other objects could have been changed without my knowledge.

.. code-block:: none

    $ singularity verify my_container.sif
    Verifying image: my_container.sif
    [LOCAL]   Signing entity: David Trudgian (Demo keys) <david.trudgian@sylabs.io>
    [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448

    Error encountered during signature verification: object 2: object not signed
    FATAL:   Failed to verify container: integrity: object 2: object not signed


I can sign a group of objects with the ``--group-id`` option to ``sign``.

.. code-block:: none

    $ singularity sign --groupid 1 my_container.sif 
    Signing image: my_container.sif
    Enter key passphrase : 
    Signature created and applied to my_container.sif


This creates one signature over all objects in the
group. I can verify that nothing in the group has been modified by
running ``verify`` with the same ``--group-id`` option.

.. code-block:: none

    $ singularity verify --group-id 1 my_container.sif 
    Verifying image: my_container.sif
    [LOCAL]   Signing entity: David Trudgian (Demo keys) <david.trudgian@sylabs.io>
    [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
    Objects verified:
    ID  |GROUP   |LINK    |TYPE
    ------------------------------------------------
    1   |1       |NONE    |Def.FILE
    2   |1       |NONE    |JSON.Generic
    3   |1       |NONE    |FS
    Container verified: my_container.sif


Because every object in the SIF file is within the signed group 1 the entire
container is signed, and the default ``verify`` behavior without specifying
``--group-id`` can also verify the container:

.. code-block:: none

    $ singularity verify my_container.sif
    Verifying image: my_container.sif
    [LOCAL]   Signing entity: David Trudgian (Demo keys) <david.trudgian@sylabs.io>
    [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
    Objects verified:
    ID  |GROUP   |LINK    |TYPE
    ------------------------------------------------
    1   |1       |NONE    |Def.FILE
    2   |1       |NONE    |JSON.Generic
    3   |1       |NONE    |FS
    Container verified: my_container.sif
