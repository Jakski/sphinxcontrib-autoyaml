sphinxcontrib-autoyaml
================================================================================

This Sphinx autodoc extension documents YAML files from comments. It looks for
documentation comment delimeter(default: ``###``) and adds it with all further
comments as reST documentation till it finds end of comment.

Options
--------------------------------------------------------------------------------

Options available to use in your configuration:

``autoyaml_root``
   Look for YAML files relatively to this directory.
   **DEFAULT**: ..

``autoyaml_doc_delimeter``
   Character(s) which start a documentation comment.
   **DEFAULT**: ###

``autoyaml_comment``
   Comment start character(s).
   **DEFAULT**: #

Installing
--------------------------------------------------------------------------------

Issue command:

``pip install sphinxcontrib-autoyaml``

and add ``sphinxcontrib-autoyaml`` to ``extensions`` variable in ``conf.py``
file of Sphinx setup.

Example
--------------------------------------------------------------------------------

.. code-block:: rst

   Some title
   ==========

   Documenting all YAML files from directory recursively.

   .. autoyaml:: some_yml_dir

   Documenting single YAML file.

   .. autoyaml:: some_yml_file.yml

