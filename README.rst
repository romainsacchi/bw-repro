.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/bw-repro.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/bw-repro
    .. image:: https://readthedocs.org/projects/bw-repro/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://bw-repro.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/bw-repro/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/bw-repro
    .. image:: https://img.shields.io/pypi/v/bw-repro.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/bw-repro/
    .. image:: https://img.shields.io/conda/vn/conda-forge/bw-repro.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/bw-repro
    .. image:: https://pepy.tech/badge/bw-repro/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/bw-repro
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/bw-repro

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

========
bw-repro
========


    A brightway2 wrapper that records parameters and relevant information to replicate LCA-related experiments

To install:

.. code-block:: bash

   $ pip install git+https://github.com/romainsacchi/bw-repro.git

Package divided in two main modules: ``recordtools`` and ``reproducer``.
To test ``recordtools`` and generate an example `output.zip`:

.. code-block:: bash

   $ cd ~/bw-repro
   $ python testing_recorder.py


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
