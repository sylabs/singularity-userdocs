.. _signnverify:

################################
Signing and Verifying Containers
################################

.. _sec:signnverify:

{Singularity} supports two methods for signing and verifying container images:

- A native signature format, that can be applied to SIF and OCI-SIF images.
- Cosign-compatible signatures against an image inside an OCI-SIF file.

*********************
Native SIF Signatures
*********************

{Singularity}'s SIF images can be signed, and subsequently verified, so that a
user can be confident that an image they have obtained is a bit-for-bit
reproduction of the original container as the author intended it. The signature,
over the metadata and content of the container, is created using a private key,
and directly added to the SIF file. This means that a signed container carries
it's signature with it, avoiding the need for extra infrastructure to distribute
signatures to end users of the container.

A user verifies the container has not been modified since signing using a public
key or certificate. By default, {Singularity} uses PGP keys to sign and verify
containers. Since 3.11, signing and verifying containers with X.509 key material
/ certificates is also supported.

PGP Public keys for verification can be distributed manually, or can be upload
to and automatically retrieved from `Singularity Container Services
<https://cloud.sylabs.io/>`__ (SCS) or a `Singularity Enterprise
<https://sylabs.io/singularity-enterprise/>`__ installation. Optionally, an HKP
keyserver can also be configured.

As well as indicating a container has not been modified, a valid signature may
be used to indicate a container has undergone testing or review, and is approved
for execution. Multiple signatures can be added to a container, to document its
progress through an approval process. {Singularity}'s Execution Control List
(ECL) feature can be enable by administrators of privileged installations to
restrict execution of containers based on their signatures (see the admin guide
for more information).

.. note::

   Due to a change in signature format, containers signed by
   3.6.0 and later cannot be verified by older versions of {Singularity}.

   To verify containers signed with older versions of {Singularity}
   using 3.6.0 and above, the ``--legacy-insecure`` flag must be provided to the
   ``singularity verify`` command.

.. _verify_container_from_library:

Verifying containers from the Container Library
===============================================

The ``verify`` command will check that a SIF container image has been signed
using a PGP key, and is unchanged since it was signed.

If you are using a container image that was pulled from the SCS container
library, then it is likely that it was signed with a PGP key that has been
submitted to the SCS keystore. {Singularity} is able to automatically retrieve
the public key to perform verification.

.. code::

   $ singularity pull library://alpine:latest

   $ singularity verify alpine_latest.sif

   Container is signed by 1 key(s):

   Verifying partition: FS:
   8883491F4268F173C6E5DC49EDECE4F3F38D871E
   [REMOTE]  Sylabs Admin <support@sylabs.io>
   [OK]      Data integrity verified

   INFO:    Container verified: alpine_latest.sif

In this example you can see that **Sylabs Admin** has signed the
container.

.. note::

   ``singularity verify`` will only run against a local SIF file. You must
   ``pull`` an image from a ``library://`` source before you can verify it.

.. _sign_your_own_containers:


Signing your own containers
===========================

Generating and managing PGP keys
--------------------------------

To sign your own containers you first need to generate one or more keys. In
order to submit them to the SCS keystore, you will also need to login to SCS
with a token:

   #. Go to: https://cloud.sylabs.io/
   #. Click "Sign In" and follow the sign in steps.
   #. Click on your login id (same and updated button as the Sign in
      one).
   #. Select "Access Tokens" from the drop down menu.
   #. Enter a name for your new access token, such as "test token"
   #. Click the "Create a New Access Token" button.
   #. Click "Copy token to Clipboard" from the "New API Token" page.
   #. Run ``singularity remote login`` and paste the access token at the
      prompt.

If you attempt to sign a container before you have generated any keys,
{Singularity} will guide you through the interactive process of creating
a new key. Or you can use the ``newpair`` subcommand in the ``key``
command group like so:.

.. code::

   $ singularity key newpair

   Enter your name (e.g., John Doe) : Joe User
   Enter your email address (e.g., john.doe@example.com) : myuser@example.com
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
wish to push your public key, say ``n`` during the ``newpair`` process.

The ``list`` subcommand will show you all of the keys you have created
or saved locally.`

.. code::

   $ singularity key list

   Public key listing (/home/dave/.singularity/sypgp/pgp-public):

   0)  User:              Joe User (demo) <myuser@example.com>
       Creation time:     2019-11-15 09:54:54 -0600 CST
       Fingerprint:       E5F780B2C22F59DF748524B435C3844412EE233B
       Length (in bits):  4096

If you chose not to push your key to the keystore during the ``newpair``
process, but later wish to, you can push it to a keystore configured
using ``singularity remote`` like so:

.. code::

   $ singularity key push E5F780B2C22F59DF748524B435C3844412EE233B

   public key `E5F780B2C22F59DF748524B435C3844412EE233B` pushed to server successfully

If you delete your local public PGP key, you can always locate and
download it again like so.

.. code::

   $ singularity key search Trudgian

   Showing 1 results

   KEY ID    BITS  NAME/EMAIL
   12EE233B  4096  Joe User (demo) <myuser@example.com>

   $ singularity key pull 12EE233B

   1 key(s) added to keyring of trust /home/dave/.singularity/sypgp/pgp-public

But note that this only restores the *public* key (used for verifying)
to your local machine and does not restore the *private* key (used for
signing).

.. _searching_for_keys:

Searching for keys
------------------

{Singularity} allows you to search the keystore for public keys. You can
search for names, emails, and fingerprints (key IDs). When searching for
a fingerprint, you need to use ``0x`` before the fingerprint, check the
example:

.. code::

   # search for key ID:
   $ singularity key search 0x8883491F4268F173C6E5DC49EDECE4F3F38D871E

   # search for the sort ID:
   $ singularity key search 0xF38D871E

   # search for user:
   $ singularity key search Godlove

   # search for email:
   $ singularity key search @gmail.com

Signing and validating your own containers
------------------------------------------

Now that you have a key generated, you can use it to sign images like
so:

.. code::

   $ singularity sign my_container.sif

   Signing image: my_container.sif
   Enter key passphrase :
   Signature created and applied to my_container.sif

Because your public PGP key is saved locally you can verify the image
without needing to contact the Keystore.

.. code::

   $ singularity verify my_container.sif
   Verifying image: my_container.sif
   [LOCAL]   Signing entity: Joe User (Demo keys) <myuser@example.com>
   [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
   Objects verified:
   ID  |GROUP   |LINK    |TYPE
   ------------------------------------------------
   1   |1       |NONE    |Def.FILE
   2   |1       |NONE    |JSON.Generic
   3   |1       |NONE    |FS
   Container verified: my_container.sif

If you've pushed your key to the Keystore you can also verify this image
in the absence of a local public key. To demonstrate this, first
``remove`` your local public key, and then try to use the ``verify``
command again.

.. code::

   $ singularity key remove E5F780B2C22F59DF748524B435C3844412EE233B

   $ singularity verify my_container.sif
   Verifying image: my_container.sif
   [REMOTE]   Signing entity: Joe User (Demo keys) <myuser@example.com>
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

.. code::

   $ singularity key pull E5F780B2C22F59DF748524B435C3844412EE233B

   1 key(s) added to keyring of trust /home/dave/.singularity/sypgp/pgp-public

Advanced Signing - SIF IDs and Groups
-------------------------------------

As well as the default behaviour, which signs all objects, fine-grained
control of signing is possible.

If you ``sif list`` a SIF file you will see it is comprised of a number
of objects. Each object has an ``ID``, and belongs to a ``GROUP``.

.. code::

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

.. note:: 

   The ``singularity sif`` commands will only run against a local SIF file. You
   must ``pull`` an image from a ``library://`` source before you can examine
   it.

I can choose to sign and verify a specific object with the ``--sif-id``
option to ``sign`` and ``verify``.

.. code::

   $ singularity sign --sif-id 1 my_container.sif
   Signing image: my_container.sif
   Enter key passphrase :
   Signature created and applied to my_container.sif

   $ singularity verify --sif-id 1 my_container.sif
   Verifying image: my_container.sif
   [LOCAL]   Signing entity: Joe User (Demo keys) <myuser@example.com>
   [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
   Objects verified:
   ID  |GROUP   |LINK    |TYPE
   ------------------------------------------------
   1   |1       |NONE    |Def.FILE
   Container verified: my_container.sif

Note that running the ``verify`` command without specifying the specific
sif-id gives a fatal error. The container is not considered verified as
whole because other objects could have been changed without my
knowledge.

.. code::

   $ singularity verify my_container.sif
   Verifying image: my_container.sif
   [LOCAL]   Signing entity: Joe User (Demo keys) <myuser@example.com>
   [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448

   Error encountered during signature verification: object 2: object not signed
   FATAL:   Failed to verify container: integrity: object 2: object not signed

I can sign a group of objects with the ``--group-id`` option to
``sign``.

.. code::

   $ singularity sign --groupid 1 my_container.sif
   Signing image: my_container.sif
   Enter key passphrase :
   Signature created and applied to my_container.sif

This creates one signature over all objects in the group. I can verify
that nothing in the group has been modified by running ``verify`` with
the same ``--group-id`` option.

.. code::

   $ singularity verify --group-id 1 my_container.sif
   Verifying image: my_container.sif
   [LOCAL]   Signing entity: Joe User (Demo keys) <myuser@example.com>
   [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
   Objects verified:
   ID  |GROUP   |LINK    |TYPE
   ------------------------------------------------
   1   |1       |NONE    |Def.FILE
   2   |1       |NONE    |JSON.Generic
   3   |1       |NONE    |FS
   Container verified: my_container.sif

Because every object in the SIF file is within the signed group 1 the
entire container is signed, and the default ``verify`` behavior without
specifying ``--group-id`` can also verify the container:

.. code::

   $ singularity verify my_container.sif
   Verifying image: my_container.sif
   [LOCAL]   Signing entity: Joe User (Demo keys) <myuser@example.com>
   [LOCAL]   Fingerprint: 65833F473098C6215E750B3BDFD69E5CEE85D448
   Objects verified:
   ID  |GROUP   |LINK    |TYPE
   ------------------------------------------------
   1   |1       |NONE    |Def.FILE
   2   |1       |NONE    |JSON.Generic
   3   |1       |NONE    |FS
   Container verified: my_container.sif


PEM Key / X.509 Certificate Support
===================================

Beginning with version 3.11, {Singularity} supports signing SIF container images
using a PEM format private key, and verifying with a PEM format public key, or
X.509 certificate. Non-PGP signatures are implemented using the `Dead Simple
Signing Envelope <https://github.com/secure-systems-lab/dsse>`__ (DSSE)
standard.

Signing with a PEM key
----------------------

To sign a container using a private key in PEM format, provide the key material
to the ``sign`` command using the ``--key`` flag:

.. code::

   $ singularity sign --key mykey.pem lolcow.sif
   INFO:    Signing image with key material from 'mykey.pem'
   INFO:    Signature created and applied to image 'lolcow.sif'

The DSSE signature descriptor can now be seen by inspecting the SIF file:

.. code::

   $ singularity sif list lolcow.sif
   ------------------------------------------------------------------------------
   ID   |GROUP   |LINK    |SIF POSITION (start-end)  |TYPE
   ------------------------------------------------------------------------------
   1    |1       |NONE    |32176-32393               |Def.FILE
   2    |1       |NONE    |32393-33522               |JSON.Generic
   3    |1       |NONE    |33522-33718               |JSON.Generic
   4    |1       |NONE    |36864-84656128            |FS (Squashfs/*System/amd64)
   5    |NONE    |1   (G) |84656128-84658191         |Signature (SHA-256)

   $ singularity sif dump 5 lolcow.sif | jq
   {
   "payloadType": "application/vnd.sylabs.sif-metadata+json",
   ...

Attempting to ``verify`` the image without options will fail, as it is not
signed with a PGP key:

.. code::

   $ singularity verify lolcow.sif
   INFO:    Verifying image with PGP key material
   FATAL:   Failed to verify container: integrity: key material not provided for DSSE envelope signature

Note that the error message shows that the container image has a DSSE signature
present.

Verifying with a PEM key
------------------------

To verify a container using a PEM public key directly, provide the key material
to the ``verify`` command using the ``key`` flag:

.. code::

   $ singularity verify --key mypublic.pem lolcow.sif
   INFO:    Verifying image with key material from 'mypublic.pem'
   Objects verified:
   ID  |GROUP   |LINK    |TYPE
   ------------------------------------------------
   1   |1       |NONE    |Def.FILE
   2   |1       |NONE    |JSON.Generic
   3   |1       |NONE    |JSON.Generic
   4   |1       |NONE    |FS
   INFO:    Verified signature(s) from image 'lolcow.sif'

Verifying with an X.509 certificate
-----------------------------------

To verify a container that was signed with a PEM private key, using an X.509
certificate, pass the certificate to the ``verify`` command using the
``--certificate`` flag. If the certificate is part of a chain, provide
intermediate and valid root certificates with the
``--certificate-intermediates`` and ``--certificate-roots`` flags:

.. code::

   $ singularity verify \
      --certificate leaf.pem \
      --certificate-intermediates intermediate.pem \
      --certificate-roots root.pem \
      lolcow.sif

.. note::

   The certificate must have a usage field that allows code signing in order to
   verify container images.

OSCP Certificate Revocation Checks
----------------------------------

When verifying a container using X.509 certificates, {Singularity} can perform
online revocation checks using the Online Certificate Status Protocol (OCSP). To
enable OCSP checks, add the ``--ocsp-verify`` flag to your ``verify`` command:

.. code::

   $ singularity verify \
      --certificate leaf.pem \
      --certificate-intermediates intermediate.pem \
      --certificate-roots root.pem \
      --ocsp-verify
      lolcow.sif

{Singularity} will then attempt to contact the prescribed OCSP responder for
each certificate in the chain, in order to check that the relevant certificate
has not been revoked. In the event that an OCSP responder cannot be contacted,
or a certificate has been revoked, verification will fail with a validation
error:

.. code::

   INFO:    Validate: cert:leaf  issuer:intermediate
   FATAL:   Failed to verify container: OCSP verification has failed

************************************
Cosign Compatible OCI-SIF Signatures
************************************

When using {Singularity}'s OCI-Mode, container images are pulled or built as
OCI-SIF images. An OCI-SIF file holds an OCI image using standard OCI structures
such as an image manifest, config, and layers.

Although you can use native {Singuarity} SIF signatures (as above) to sign and
verify an OCI-SIF file, they are not supported by other tools common in OCI
workflows. Native SIF signatures sign the content and metadata of the (OCI-)SIF
file itself, rather than the container inside the file. If you push an OCI-SIF
image to an OCI registry (except via ``oras://``) then the image within the SIF
is transferred, rather than the complete SIF file. Any native SIF signature is
lost.

The `sigstore project <https://www.sigstore.dev/>`_ has defined standards for
signing and verifying software artefacts, and these have been widely adopted.
The `cosign <https://github.com/sigstore/cosign>` tool uses sigstore to sign and
verify OCI container images.

Beginning with version 4.3, {Singularity} supports signing OCI-SIF container
images with a cosign compatible signature. This signature will apply to the
image inside the OCI-SIF file, and can be pushed/pulled to/from an OCI registry
alongside the image itself.

Generating a Cosign Keypair
===========================

Cosign signatures are generated using a private key, and verified using a public
key. The private key is an ECDSA key, instead of the PGP keys used by native SIF
signatures.

To generate a cosign keypair use the ``key generate-cosign-key-pair``
subcommand. You will be prompted to supply a password that is used to encrypt
the private key, preventing its use if it is obtained by an attacker.

.. code::

   # Creates singularity-cosign.key & singularity-cosign.pub
   $ singularity key generate-cosign-key-pair
   INFO:    Creating cosign key-pair singularity-cosign.key/.pub
   Enter password for private key: 
   Enter again: 

   $ singularity key generate-cosign-key-pair --output-key-prefix test
   INFO:    Creating cosign key-pair test.key/.pub
   Enter password for private key: 
   Enter again: 

Signing an OCI-SIF Container Image
==================================

To sign a container image inside an OCI-SIF file, use the ``--cosign`` flag for
the ``sign`` command, and provide the path to your private key using the
``--key`` flag. You will be prompted for the password for the private key.

.. code::

   $ singularity sign --cosign --key singularity-cosign.key alpine_latest.oci.sif 
   INFO:    Sigstore/cosign compatible signature, using key material from 'singularity-cosign.key'
   Enter password for private key: 

A cosign signature is created as a non-executable OCI container image structure.
This is added to the OCI-SIF file, and associated with the executable container
image that it signs.

If we examine the ``RootIndex`` of the OCI-SIF file, we can see that there is
now a second manifest listed, with a ``ref.name`` indicating it is a cosign
signature for the image that was signed:

.. code::

   $ singularity sif dump 7 alpine_latest.oci.sif  | jq
   {
   "schemaVersion": 2,
   "mediaType": "application/vnd.oci.image.index.v1+json",
   "manifests": [
      {
         "mediaType": "application/vnd.oci.image.manifest.v1+json",
         "size": 901,
         "digest": "sha256:1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b"
      },
      {
         "mediaType": "application/vnd.oci.image.manifest.v1+json",
         "size": 558,
         "digest": "sha256:3ffa7ff55df0e6e7a9f5fce3a127195c3632c6bab2207617b78c1dbecd8896b5",
         "annotations": {
         "org.opencontainers.image.ref.name": "_cosign:sha256-1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b.sig"
         }
      }
   ]
   }

Verifying an OCI-SIF Container Image
====================================

To verify a signed image in an OCI-SIF container, use the ``--cosign`` flag for
the ``verify`` command, and provide the path to your public key using the
``--key`` flag.

{Singularity} will first verify that every OCI blob matches the digest recorded
in the OCI-SIF file. It will then check all cosign signatures present in the
OCI-SIF, and indicate how many are valid with the provided public key. The
output of the command is the JSON format signature payload for each valid
signature.

.. code::

   $ singularity verify --cosign --key singularity-cosign.pub alpine_latest.oci.sif  | jq
   INFO:    Verifying image with sigstore/cosign signature, using key material from 'singularity-cosign.pub'
   INFO:    Verifying digests for 6 OCI Blobs
   INFO:    Image digest: sha256:1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b
   INFO:    Image has 1 associated signatures
   INFO:    Image has 1 signatures that are valid with provided key material
   [
   {
      "critical": {
         "identity": {
         "docker-reference": ""
         },
         "image": {
         "docker-manifest-digest": "sha256:1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b"
         },
         "type": "cosign container image signature"
      },
      "optional": {
         "creator": "Singularity-Ce/4.3.0 (Linux amd64) Go/1.24.0",
         "timestamp": 1741182667
      }
   }
   ]

If no signatures are valid with the provided public key, the command will return an error.

.. code::

    $ singularity verify --cosign --key test.pub alpine_latest.oci.sif 
   INFO:    Verifying image with sigstore/cosign signature, using key material from 'test.pub'
   INFO:    Verifying digests for 6 OCI Blobs
   INFO:    Image digest: sha256:1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b
   INFO:    Image has 1 associated signatures
   INFO:    Image has 0 signatures that are valid with provided key material
   FATAL:   no valid signatures found

Pushing & Pulling Signed Images
===============================

When pushing a signed OCI-SIF image to an OCI registry use the ``--with-cosign``
flag on the ``push`` command to transfer signatures alongside the image itself:

.. code::

   $ singularity push --with-cosign alpine_latest.oci.sif docker://example/demo:signed
   INFO:    Writing cosign signatures: index.docker.io/example/demo:sha256-1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b.sig
   INFO:    Upload complete

An image that has been pushed to a registry can be verified using the upstream
``cosign`` tool:

.. code::

$ cosign verify --insecure-ignore-tlog --key singularity-cosign.pub example/demo:signed | jq
   WARNING: Skipping tlog verification is an insecure practice that lacks of transparency and auditability verification for the signature.

   Verification for index.docker.io/example/demo:signed --
   The following checks were performed on each of these signatures:
   - The cosign claims were validated
   - The signatures were verified against the specified public key
   [
   {
      "critical": {
         "identity": {
         "docker-reference": ""
         },
         "image": {
         "docker-manifest-digest": "sha256:1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b"
         },
         "type": "cosign container image signature"
      },
      "optional": {
         "creator": "Singularity-Ce/4.3.0 (Linux amd64) Go/1.24.0",
         "timestamp": 1741182667
      }
   }
   ]
   
.. note::

   {Singularity} does not currently support recording the signing of an image in
   a transparency log. Verifying a container with cosign 2.0 and above requires
   the ``--insecure-ignore-tlog`` or ``--private-infrastructure`` flag to be
   specified, as the cosign tool now expects a transparency log entry to be
   present for all images, by default.

When pulling a signed OCI-SIF image to an OCI registry use the ``--with-cosign``
flag on the ``pull`` command to transfer signatures alongside the image itself:

.. code::

   $ singularity pull --oci --with-cosign docker://dctrud/test:signed
   INFO:    cosign signature functionality does not support SIF caching, pulling directly to: test_signed.oci.sif
   3.4MiB / 3.4MiB [=====================================================================] 100 % 15.1 KiB/s 0s
   INFO:    Writing cosign signatures: _cosign:sha256-1d47bc37b15dd8ebf4d84b3be55f92aaa4da3ef6a8195393e0e1ce338c56879b.sig
   INFO:    Cleaning up.


Limitations
===========

As mentioned above, {Singuarity} does not support recording signatures in a
public transparency log. This is a default expectation of the ``cosign`` tool at
v2 and above. The ``--private-infrastructure`` or ``--insecure-ignore-tlog``
flags must be passed to ``cosign verify`` to verify an image signed by
{Singularity}.

{Singularity} only supports ECDSA keypairs for image signing and verification.
Other key material sources (e.g. KMS) supported by the ``cosign`` tool are not
currently available in {Singularity}.

When an image is pushed/pulled to/from an OCI registry, signatures can only be
transferred if the image is not mutated in any way. An OCI image with tar-format
layers cannot be pulled ``--with-cosign`` into an OCI-SIF with squashfs format
layers. The signature on the original image would not be valid as this image
manifest will change when the layers are converted.
