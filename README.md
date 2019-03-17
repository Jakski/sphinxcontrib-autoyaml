# sphinxcontrib-autoyaml

This Sphinx autodoc extension documents YAML files from comments. Documentation
is returned as reST definitions, e.g.:

This document:

```
###
# Enable Nginx web server.
enable_nginx: true

###
# Enable Varnish caching proxy.
enable_varnish: true
```

would be turned into text:

```
enable_nginx

   Enable Nginx web server.

enable_varnish

   Enable Varnish caching proxy.
```

See `tests/examples/output/index.yml` and `tests/examples/output/index.txt` for
more examples.

`autoyaml` will take into account only comments which first line starts with
`autoyaml_doc_delimiter`.

## Usage

You can use `autoyaml` directive, where you want to extract comments
from YAML file, e.g.:

```
Some title
==========

Documenting single YAML file.

.. autoyaml:: some_yml_file.yml
```

## Options

Options available to use in your configuration:

- *autoyaml_root*(`..`)
  Look for YAML files relatively to this directory.
- *autoyaml_doc_delimiter*(`###`)
  Character(s) which start a documentation comment.
- *autoyaml_comment*(`#`)
  Comment start character(s).

## Installing

Issue command:

```
pip install sphinxcontrib-autoyaml
```

And add extension in your project's ``conf.py``:

```
extensions = ["sphinxcontrib.autoyaml"]
```
