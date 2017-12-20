import unittest
import warnings

from sphinx_testing import with_app

from sphinxcontrib.autoyaml import AutoYAMLException

def build(app, path):
    """Build and return documents without known warnings"""
    with warnings.catch_warnings():
        # Ignore warnings emitted by docutils internals.
        warnings.filterwarnings(
            "ignore",
            "'U' mode is deprecated",
            DeprecationWarning)
        app.build()
        return (app.outdir / path).read_text()

class TestAutoYAML(unittest.TestCase):

    @with_app(
        buildername="text",
        srcdir="tests/examples/output",
        copy_srcdir_to_tmpdir=True)
    def test_output(self, app, status, warning):
        output = build(app, "index.txt")
        with open("tests/examples/output/index.txt") as f:
            correct = f.read()
        self.assertEqual(correct, output)

    @with_app(
        buildername="html",
        srcdir="tests/examples/wrong_location1",
        copy_srcdir_to_tmpdir=True)
    def test_missing_file(self, app, status, warning):
        ret = None
        try:
            build(app, "index.html")
        except Exception as e:
            ret = e
        self.assertIsInstance(ret, AutoYAMLException)

    @with_app(
        buildername="html",
        srcdir="tests/examples/wrong_location2",
        copy_srcdir_to_tmpdir=True)
    def test_catalog_argument(self, app, status, warning):
        ret = None
        try:
            build(app, "index.html")
        except Exception as e:
            ret = e
        self.assertIsInstance(ret, AutoYAMLException)
