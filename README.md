# sphinxcontrib-autoyaml

This Sphinx autodoc extension documents YAML files from comments. Documentation
is returned as reST definitions, e.g.:

This document:

```yaml
###
# Enable Nginx web server.
enable_nginx: true

###
# Enable Varnish caching proxy.
enable_varnish: true
```

would be turned into text:

```rst
enable_nginx

   Enable Nginx web server.

enable_varnish

   Enable Varnish caching proxy.
```

See `tests/examples/output/*.yml` and `tests/examples/output/*.txt` for
more examples.

`autoyaml` will take into account only comments which first line starts with
`autoyaml_doc_delimiter`.

## Usage

You can use `autoyaml` directive, where you want to extract comments
from YAML file, e.g.:

```rst
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
- *autoyaml_level*(`1`)
  Parse comments from nested structures n-levels deep.
- *autoyaml_safe_loader*(`False`)
  Whether to use YAML SafeLoader

### Default options

```python
autoyaml_root = ".."
autoyaml_doc_delimiter = "###"
autoyaml_comment = "#"
autoyaml_level = 1
autoyaml_safe_loader = False
```

## Installing

Issue command:

```sh
pip install sphinxcontrib-autoyaml
```

And add extension in your project's ``conf.py``:

```python
extensions = ["sphinxcontrib.autoyaml"]
```

## Caveats

### Mapping keys nested in sequences

Sequences are traversed as well, but they are not represented in output
documentation. This extension focuses only on documenting mapping keys. It means
that structure like this:

```yaml
key:
  ###
  # comment1
  - - inner_key1: value
      ###
      # comment2
      inner_key2: value
  ###
  # comment3
  - inner_key3: value
```

will be flattened, so it will appear as though inner keys exist directly under
`key`. Duplicated key documentation will be duplicated in output as well. See
`tests/examples/output/comment-in-nested-sequence.txt` and
`tests/examples/output/comment-in-nested-sequence.yml` to get a better
understanding how sequences are processed.

### Complex mapping keys

YAML allows for complex mapping keys like so:

```yaml
[1, 2]: value
```

These kind of keys won't be documented in output, because it's unclear how they
should be represented as a string.

### Flow-style entries

YAML allows writing complex data structures in single line like JSON.
Documentation is generated only for the first key in such entry, so this:

```yaml
###
# comment
key: {key1: value, key2: value, key3: value}
```

would yield documentation only for `key`.
