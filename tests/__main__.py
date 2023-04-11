import unittest
import warnings
import os
from collections import defaultdict
from pathlib import Path
from functools import wraps

from sphinx_testing import with_app
from sphinxcontrib.autoyaml import AutoYAMLException


CONFIG = {
    "master_doc": "index",
    "extensions": ["sphinxcontrib.autoyaml"],
    "autoyaml_root": ".",
    "autoyaml_level": 0,
    "autoyaml_safe_loader": True,
}


def patch_config(delta):
    r = CONFIG.copy()
    r.update(delta)
    return r


def build(app, filename, filetype):
    """Build and return documents without known warnings"""
    with open(os.path.join(app.srcdir, "index.rst"), "w") as index:
        index.write(f"Test\n========\n.. autoyaml:: {filename}.yml\n")
    with warnings.catch_warnings():
        # Ignore warnings emitted by docutils internals.
        warnings.filterwarnings("ignore", "'U' mode is deprecated", DeprecationWarning)
        app.build()
    with open(
        os.path.join(app.outdir, f"index.{filetype}"), encoding="utf-8"
    ) as rendered:
        return rendered.read()


def make_text_test(filename, directory="output", confoverrides=None):
    if confoverrides is None:
        confoverrides = {}
    @with_app(
        confoverrides=patch_config(confoverrides),
        buildername="text",
        srcdir=os.path.join("tests/examples", directory),
        copy_srcdir_to_tmpdir=True,
    )
    def test(self, app, status, warning):
        output = build(app, filename, "txt")
        correct_file = os.path.join("tests/examples", directory, f"{filename}.txt")
        if os.environ.get("TEST_GENERATE_EXAMPLES", "0") == "1":
            with open(correct_file, "w") as f:
                f.write(output)
        else:
            with open(correct_file, "r") as f:
                correct = f.read()
            self.assertEqual(correct, output)

    return test


class TestAutoYAML(unittest.TestCase):
    @with_app(
        confoverrides=CONFIG,
        buildername="html",
        srcdir="tests/examples/wrong_location1",
        copy_srcdir_to_tmpdir=True,
    )
    def test_missing_file(self, app, status, warning):
        with self.assertRaises(AutoYAMLException):
            build(app, "index", "html")

    @with_app(
        confoverrides=CONFIG,
        buildername="html",
        srcdir="tests/examples/wrong_location2",
        copy_srcdir_to_tmpdir=True,
    )
    def test_directory_argument(self, app, status, warning):
        with self.assertRaises(AutoYAMLException):
            build(app, "index", "html")


if __name__ == "__main__":
    text_examples = [
        f for f in os.listdir("tests/examples/output") if f.endswith(".yml")
    ]
    confoverrides = defaultdict(dict)
    confoverrides["capped1"] = {"autoyaml_level": 1}
    confoverrides["capped2"] = {"autoyaml_level": 2}
    for text_example in text_examples:
        filename, _ = os.path.splitext(text_example)
        test_name = filename.replace("-", "_")
        setattr(TestAutoYAML, f"test_{test_name}", make_text_test(filename, confoverrides=confoverrides[filename]))
    unittest.main()
