# SingularityCE User Docs

This repository holds user-facing documentation for the
[SingularityCE](https://github.com/sylabs/singularity) container runtime.

This is a community project led by [Sylabs](https://sylabs.io), and
contributions are always welcome! If you'd like to update or improve
SingularityCE's documentation please follow the instructions below, and submit a
PR on GitHub.

## Setting up an environment to contribute

The Singularity user documentation is written in [reStructured Text (RST)
format](http://docutils.sourceforge.net/rst.html) and generated using
[Sphinx](https://pypi.org/project/Sphinx/). The
[ReadTheDocs](https://readthedocs.org/) theme for Sphinx is used.

We use RST instead of markdown as it's better at handling large documents with
many linked sections, and Sphinx makes it easy to produce online documentation
as well as PDFs.

Sphinx is written in Python. To get setup to contribute:

- Install Python 3.5 or newer, from your OS package manager or the [Python download
  site](https://www.python.org/downloads/)
- Use `pip3`to install Sphinx and the RTD theme package into your home directory:

```sh
pip3 install --user Sphinx sphinx-rtd-theme
```

If your version of python 3 does not come with `pip` / `pip3`, you may need to
install a `python3-pip`package with `apt` or `yum`, or you can install pip
follwing [the instructions here](https://pip.pypa.io/en/stable/installing/).

You're all set! After this you will only need to use your favorite editor to
work with the RST files.

## How to edit & write RST

A Sphinx documentation project has some structure that it's good to know before
you dive in and start editing or writing content.

### Structure of the project

This project maintains the following structure:

1. `index.rst` : contains the front page of the online documentation and the
   initial table of contents tree. Every documentation section is referenced by
   a tag next to its name. (e.g. ``Quick Start <quick_start>``)
2. All other `.rst`files are sections named to match reference tags described
   before. So, for the `<quick_start>` reference in `index.rst` you'll find
   a `quick_start.rst` file with the content for that section.
3. The configuration used to build the final documentations from the `.rst`
   files is set in the `conf.py` file.

### The conf.py file

This file sets the themes, extensions, variables and naming scheme for output
created when building the documentation with Sphinx. Some important elements
include:

- `version` : Describes the current version of `SingularityCE` that the
  documentation is for. We set version to the `major.minor` values, e.g. `3.5`,
  as we are not creating separate documentation for each patch release.
- `release`: Would be used to specify the current release of the software being
  documented, including patch number, alpha tags etc. We leave this the same as
  `version` as we only generate documentation for each `major.minor` version of
  singularity.
- `html_theme`: Sets the theme to be used for HTML output. We are using the RTD
  or Read The Docs theme.
- `html_context`: Options here control links back to our GitHub repository.
- `html_logo`: The logo for the sidebar
- `html_favicon`: The `favicon`for the entire project

### Cheatsheet to get started with reStructured (RST) Text

RST is similar to Markdown, but has enough differences that you are likely to be
caught out a few times until you are familiar with it. Let's look at some of the
common things you need to do when writing or editing RST.

#### 1. Create a section/subsection/subsubsection title

Sections titles are defined by surrounding or underlining them
with different characters. Each combination of overline/underline and character
used represents a different level section.

- To create a main section title: A main section title is surrounded (above and
  below) with `=` characters:

```rst
================
New Main Section
================
```

- To create a sub-section: A sub section title is surrounded (above and below)
  with `-` characters:

```rst
---------------
New Sub section
---------------
```

- To create a sub-sub-section: A sub-sub section title is underlined with ``=``
  characters:

```rst
New sub-sub section
===================
```

- If you need more levels you can keep going: A sub-sub-sub-section is
  underlined with `-` characters.

```rst
New sub-sub-sub section
-----------------------
```

RST doesn't actually set a specific order for the characters you use to
underline and overline titles, as it will pick up the method used for the first
title at each level. Following the convention above, though, will make it easy
to see what level a section is wherever you are working in the documentation.

#### 2. Reference sections

To reference a section in an RST file you need to first create the reference
above the title you need to reference, and second to reference it where you need
the link to the reference section. When you build HTML or PDF output with Sphinx
it will create the links for you, so the reader can jump around the
documentation easily.

##### Step 1: Create the reference

To create the reference on the section you need to link, you must specify a
tag:

```rst
.. _build-docker:

-------------------------
Build from a Docker Image
-------------------------
```

This example will let you refer to the section titled "Build from a Docker
Image" with the tag `build-docker`. Note that the tag here doesn't include the
`_` that you have to prefix it with when creating the reference.

##### Step 2: Reference it

To reference a section you need to use this syntax:

```rst
:ref:`read the section covering docker images <build-docker>`
```

`:ref:` tells Sphinx that this is a reference. In between the `` ` ``you should
provide text for the link, and then the tag you created above between `< >`.

### Further Reading

These are some of the basics of RST. For a more complete introduction, see the
[Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)

### Building HTML documentation

To build the HTML documentation, make sure you are in the top level of the
`singularity-userdocs` repository and run:

```sh
make html SKIPCLI=1
```

This will generate a folder called `_build/html` with the output. Open
`index.html` to browse the documentation.

The `SKIPCLI=1` option tells `make` not to generate the CLI reference, which is
created automatically from the SingularityCE source code. You can generate the CLI
documentation by running `make html` alone. This requires a Go build
environment (see below).

### Generating PDF files from RST

This is very similar to the previous step, you will need to run:

```sh
make latexpdf SKIPCLI=1
```

Output is written into `_build/latex` and the final PDF will be named
`singularity-userdocs.pdf`

### Generating EPUB from RST

Very similar to the previous command, you will just need to run:

```sh
make epub SKIPCLI=1
```

Output is written into `_build/epub` and the final EPUB will be named
`singularity-userdocs.epub`

## Generating CLI docs

The SingularityCE CLI docs are generated using the actual code from SingularityCE.
To do this, we include SingularityCE as a git submodule, and whenever a Makefile
target (like `make html`) is run, `singularity` itself is compiled and used to
generate the CLI docs.

However, you might not want to compile `singularity`, either because you can't on
your machine, or because you want to test out a quick change to the docs.  If
this is the case, you can skip the CLI doc generation using the `SKIPCLI`
argument.  For example, to rebuild the HTML docs without including the CLI docs,
just run `make html SKIPCLI=1`.

If SingularityCE has been updated and you want to synchronize the CLI docs with
the new version of SingularityCE, you'll have to update the submodule.  To do
this, just run:

```bash
git submodule update --remote --merge
git add vendor/src/github.com/sylabs/singularity
git commit
```

This will update the submodule to the latest version of the master
branch.
