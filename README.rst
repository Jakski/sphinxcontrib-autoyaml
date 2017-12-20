sphinxcontrib-autoyaml
================================================================================

This Sphinx autodoc extension documents YAML files from comments. It looks for
documentation comment delimiter(default: ``###``) and adds it with all further
comments as reST documentation till it finds end of comment.

Options
--------------------------------------------------------------------------------

Options available to use in your configuration:

autoyaml_root
   Look for YAML files relatively to this directory.

   **DEFAULT**: ..

autoyaml_doc_delimiter
   Character(s) which start a documentation comment.

   **DEFAULT**: ###

autoyaml_comment
   Comment start character(s).

   **DEFAULT**: #

Installing
--------------------------------------------------------------------------------

Issue command:

``pip install sphinxcontrib-autoyaml``

And add extension in your project's ``conf.py``:

.. code-block:: py

   extensions = ["sphinxcontrib.autoyaml"]

Example
--------------------------------------------------------------------------------

.. code-block:: rst

   Some title
   ==========

   Documenting single YAML file.

   .. autoyaml:: some_yml_file.yml
