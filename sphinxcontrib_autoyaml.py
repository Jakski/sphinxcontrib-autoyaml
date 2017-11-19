import os

from docutils.statemachine import StringList
from docutils.parsers.rst import Directive
from docutils import nodes

VERSION = '0.0.1'

class AutoYamlDirective(Directive):

    required_arguments = 1

    def run(self):
        self.config = self.state.document.settings.env.config
        self.record_dependencies = \
                self.state.document.settings.record_dependencies
        location = self.config.autoyaml_root + '/' + self.arguments[0]
        content = []
        if os.path.isdir(location):
            for subpath in os.listdir(location):
                if subpath.endswith(self.config.autoyaml_yaml_extension) \
                   and not os.path.isdir(subpath):
                    content.extend(self.parse_file(location + '/' + subpath))
        else:
            content = self.parse_file(location)
        self.record_dependencies.add(location)
        node = nodes.paragraph(rawsource=content)
        # parse comment internals as reST
        self.state.nested_parse(StringList(content), 0, node)
        return [node]

    def parse_file(self, f):
        lines = None
        doc_lines = []
        with open(f, 'r') as src:
            lines = src.readlines()
        in_docstring = False
        for line in lines:
            if line.startswith(self.config.autoyaml_doc_delimeter):
                in_docstring = True
                doc_lines.append(self.parse_doc_line(line.rstrip()
                    [len(self.config.autoyaml_doc_delimeter):]))
            elif line.startswith(self.config.autoyaml_comment) \
               and in_docstring:
                doc_lines.append(self.parse_doc_line(line.rstrip()
                    [len(self.config.autoyaml_comment):]))
            else:
                in_docstring = False
        return doc_lines

    def parse_doc_line(self, line):
        # strip preceding whitespace
        if line and line[0] == ' ':
            return line[1:]
        return line
                

def setup(app):
    app.add_directive('autoyaml', AutoYamlDirective)
    app.add_config_value('autoyaml_root', '..', 'env')
    app.add_config_value('autoyaml_doc_delimeter', '###', 'env')
    app.add_config_value('autoyaml_comment', '#', 'env')
    app.add_config_value('autoyaml_yaml_extension', '.yml', 'env')
    return {'version': VERSION}
