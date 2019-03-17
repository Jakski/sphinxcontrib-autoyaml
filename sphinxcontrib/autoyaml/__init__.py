import os

from ruamel.yaml.reader import Reader
from ruamel.yaml.scanner import Scanner
from ruamel.yaml.resolver import VersionedResolver
from ruamel.yaml import tokens
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import switch_source_input
from sphinx.errors import ExtensionError


logger = logging.getLogger(__name__)


class Loader(Reader, Scanner, VersionedResolver):

    def __init__(self, stream, version=None):
        Reader.__init__(self, stream, loader=self)
        Scanner.__init__(self, loader=self)
        VersionedResolver.__init__(self, version, loader=self)


class AutoYAMLException(ExtensionError):

    category = 'AutoYAML error'


class AutoYAMLDirective(Directive):

    required_arguments = 1

    def run(self):
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = \
            self.state.document.settings.record_dependencies
        nodes = []
        location = os.path.normpath(
            os.path.join(self.env.srcdir,
                         self.config.autoyaml_root
                         + '/' + self.arguments[0]))
        if os.path.isfile(location):
            logger.debug('[autoyaml] parsing file: %s', location)
            try:
                nodes.extend(self._parse_file(location))
            except Exception as e:
                raise AutoYAMLException(
                        'Failed to parse YAML file: %s' % (location)) from e
        else:
            raise AutoYAMLException('%s:%s: location "%s" is not a file.' % (
                                    self.env.doc2path(self.env.docname, None),
                                    self.content_offset - 1,
                                    location))
        self.record_dependencies.add(location)
        return nodes

    def _parse_file(self, source):
        comments = {}
        with open(source, 'r') as src:
            doc = src.read()
        in_docstring = False
        for linenum, line in enumerate(doc.splitlines(), start=1):
            line = line.lstrip()
            if line.startswith(self.config.autoyaml_doc_delimiter):
                in_docstring = True
                comment = ViewList()
            elif line.startswith(self.config.autoyaml_comment) \
                    and in_docstring:
                line = line[len(self.config.autoyaml_comment):]
                # strip preceding whitespace
                if line and line[0] == ' ':
                    line = line[1:]
                comment.append(line, source, linenum)
            elif in_docstring:
                comments[linenum] = comment
                in_docstring = False
        loader = Loader(doc)
        token = None
        while True:
            last_token, token = token, loader.get_token()
            if token is None:
                break
            end_line = token.end_mark.line
            if isinstance(last_token, tokens.KeyToken) \
                    and isinstance(token, tokens.ScalarToken):
                comment = comments.get(end_line + 1)
                if comment:
                    with switch_source_input(self.state, comment):
                        node = nodes.paragraph(text=token.value)
                        definition = nodes.definition()
                        node += definition
                        self.state.nested_parse(comment, 0, definition)
                        yield node


def setup(app):
    app.add_directive('autoyaml', AutoYAMLDirective)
    app.add_config_value('autoyaml_root', '..', 'env')
    app.add_config_value('autoyaml_doc_delimiter', '###', 'env')
    app.add_config_value('autoyaml_comment', '#', 'env')
