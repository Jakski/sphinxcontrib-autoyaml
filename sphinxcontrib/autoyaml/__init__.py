import os

from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.ext.autodoc import AutodocReporter

VERSION = '0.0.1'

class AutoYamlException(Exception): pass

class AutoYamlDirective(Directive):

    required_arguments = 1

    def run(self):
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = \
                self.state.document.settings.record_dependencies
        location = self.config.autoyaml_root + '/' + self.arguments[0]
        self.result = ViewList()
        if os.path.isfile(location):
            self.parse_file(location)
        else:
            raise AutoYamlException('%s:%s: location "%s" is not a file.' %
                (
                    self.env.doc2path(self.env.docname, None),
                    self.content_offset - 1,
                    self.arguments[0]
                ))
        self.record_dependencies.add(location)
        node = nodes.paragraph()
        # parse comment internals as reST
        old_reporter = self.state.memo.reporter
        self.state.memo.reporter = AutodocReporter(
            self.result, self.state.memo.reporter)
        nested_parse_with_titles(self.state, self.result, node)
        self.state.memo.reporter = old_reporter
        return [node]

    def parse_file(self, source):
        with open(source, 'r') as src:
            lines = src.read().splitlines()
        in_docstring = False
        for linenum, line in enumerate(lines, start=1):
            if line.startswith(self.config.autoyaml_doc_delimeter):
                in_docstring = True
                self._parse_line(line, source, linenum)
            elif line.startswith(self.config.autoyaml_comment) \
               and in_docstring:
                self._parse_line(line, source, linenum)
            else:
                in_docstring = False
                # add terminating newline
                self._parse_line('', source, linenum)

    def _parse_line(self, line, source, linenum):
        # strip preceding whitespace
        if line and line[0] == ' ':
            line = line[1:]
        docstring = line[len(self.config.autoyaml_doc_delimeter):]
        self.result.append(docstring, source, linenum)

def setup(app):
    app.add_directive('autoyaml', AutoYamlDirective)
    app.add_config_value('autoyaml_root', '..', 'env')
    app.add_config_value('autoyaml_doc_delimeter', '###', 'env')
    app.add_config_value('autoyaml_comment', '#', 'env')
    return {'version': VERSION}
