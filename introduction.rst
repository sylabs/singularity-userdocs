.. _introduction:

=============================
Introduction to {Singularity}
=============================

{Singularity} is a *container* platform. It allows you to create and run
containers that package up pieces of software in a way that is
portable and reproducible. You can build a container using {Singularity}
on your laptop, and then run it on many of the largest HPC clusters in
the world, local university or company clusters, a single server, in
the cloud, or on a workstation down the hall. Your container is a
single file, and you don't have to worry about how to install all the
software you need on each different operating system.


Why use {Singularity}?
======================

{Singularity} was created to run complex applications on HPC clusters in
a simple, portable, and reproducible way. First developed at Lawrence
Berkeley National Laboratory, it quickly became popular at other HPC
sites, academic sites, and beyond. {Singularity} is an open-source
project, with a friendly community of developers and users. The user
base continues to expand, with {Singularity} now used across industry
and academia in many areas of work.

Many container platforms are available, but {Singularity} is focused on:

  - Verifiable reproducibility and security, using cryptographic
    signatures, an immutable container image format, and in-memory
    decryption.
  - Integration over isolation by default. Easily make use of GPUs, high speed
    networks, parallel filesystems on a cluster or server by default.
  - Mobility of compute. The single file SIF container format is easy
    to transport and share.
  - A simple, effective security model. You are the same user inside a
    container as outside, and cannot gain additional privilege on the
    host system by default. Read more about :ref:`security`.

Why use containers?
===================

A Unix operating system is broken into two primary components, the
kernel space, and the user space. The Kernel talks to the hardware,
and provides core system features. The user space is the environment
that most people are most familiar with. It is where applications,
libraries and system services run.

Traditionally you use an operating system that has a fixed combination
of kernel and user space. If you have access to a machine running
CentOS then you cannot install software that was packaged for Ubuntu
on it, because the user space of these distributions is not
compatible. It can also be very difficult to install multiple versions
of the same software, which might be needed to support reproducibility
in different workflows over time.

Containers change the user space into a swappable component. This
means that the entire user space portion of a Linux operating system,
including programs, custom configurations, and environment can be
independent of whether your system is running CentOS, Fedora
etc., underneath. A {Singularity} container packages up whatever you need
into a single, verifiable file.

Software developers can now build their stack onto whatever operating
system base fits their needs best, and create distributable runtime
environments so that users never have to worry about dependencies and 
requirements, that they might not be able to satisfy on their
systems.

Use Cases
=========

---------------------------------
BYOE: Bring Your Own Environment!
---------------------------------

Engineering work-flows for research computing can be a complicated and
iterative process, and even more so on a shared and somewhat
inflexible production environment. {Singularity} solves this problem by
making the environment flexible.

Additionally, it is common (especially in education) for schools to
provide a standardized pre-configured Linux distribution to the
students which includes all of the necessary tools, programs, and
configurations so they can immediately follow along.

--------------------
Reproducible science
--------------------

{Singularity} containers can be built to include all of the programs,
libraries, data and scripts such that an entire demonstration can be
contained and either archived or distributed for others to replicate
no matter what version of Linux they are presently running.

--------------------------------------------------------------
Commercially supported code requiring a particular environment
--------------------------------------------------------------

Some commercial applications are only certified to run on particular
versions of Linux. If that application was installed into a
{Singularity} container running the version of Linux that it is
certified for, that container could run on any Linux host. The
application environment, libraries, and certified stack would all
continue to run exactly as it is intended.

Additionally, {Singularity} blurs the line between container and host
such that your home directory (and other directories) exist within the
container. Applications within the container have full and direct
access to all files you own thus you can easily incorporate the
contained commercial application into your work and process flow on
the host.

-----------------------------------------
Static environments (software appliances)
-----------------------------------------

Fund once, update never software development model. While this is not
ideal, it is a common scenario for research funding. A certain amount
of money is granted for initial development, and once that has been
done the interns, grad students, post-docs, or developers are
reassigned to other projects. This leaves the software stack
un-maintained, and even rebuilds for updated compilers or Linux
distributions can not be done without unfunded effort.

------------------------------------
Legacy code on old operating systems
------------------------------------

Similar to the above example, while this is less than ideal it is a
fact of the research ecosystem. As an example, I know of one Linux
distribution which has been end of life for 15 years which is still in
production due to the software stack which is custom built for this
environment. {Singularity} has no problem running that operating system
and application stack on a current operating system and hardware.

-------------------------------------------------------
Complicated software stacks that are very host specific
-------------------------------------------------------

There are various software packages which are so complicated that it
takes much effort in order to port, update and qualify to new
operating systems or compilers. The atmospheric and weather
applications are a good example of this. Porting them to a contained
operating system will prolong the use-fullness of the development
effort considerably.

-------------------------------------------------------------------
Complicated work-flows that require custom installation and/or data
-------------------------------------------------------------------

Consolidating a work-flow into a {Singularity} container simplifies
distribution and replication of scientific results. Making containers
available along with published work enables other scientists to build
upon (and verify) previous scientific work.

