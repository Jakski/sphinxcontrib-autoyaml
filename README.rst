sphinxcontrib-yaml
================================================================================

This Sphinx autodoc extension documents YAML files from comments. It looks for
documentation comment delimeter(default: ``###``) and adds all further comments
as reST documentation till it finds another delimeter or non-comment line.

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

Example
--------------------------------------------------------------------------------

.. code-block:: rst

   Some title
   ==========

   Documenting all YAML files from directory recursively.

   .. autoyaml:: some_yml_dir

   Documenting single YAML file.

   .. autoyaml:: some_yml_file.yml

