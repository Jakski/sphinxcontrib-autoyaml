import os

from ruamel.yaml.main import compose_all
from ruamel.yaml.nodes import (
    MappingNode,
    ScalarNode,
)
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import switch_source_input
from sphinx.errors import ExtensionError


logger = logging.getLogger(__name__)


class TreeNode:

    def __init__(self, value, comments, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.comments = comments
        if value is None:
            self.comment = None
        else:
            # Flow-style entries may attempt to incorrectly reuse comments
            self.comment = self.comments.pop(value.start_mark.line + 1, None)

    def add_child(self, value):
        node = TreeNode(value, self.comments, self)
        self.children.append(node)
        return node

    def remove_child(self):
        return self.children.pop(0)


class AutoYAMLException(ExtensionError):

    category = 'AutoYAML error'


class AutoYAMLDirective(Directive):

    required_arguments = 1

    def run(self):
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = \
            self.state.document.settings.record_dependencies
        output_nodes = []
        location = os.path.normpath(
            os.path.join(self.env.srcdir,
                         self.config.autoyaml_root
                         + '/' + self.arguments[0]))
        if os.path.isfile(location):
            logger.debug('[autoyaml] parsing file: %s', location)
            try:
                output_nodes.extend(self._parse_file(location))
            except Exception as e:
                raise AutoYAMLException(
                        'Failed to parse YAML file: %s' % (location)) from e
        else:
            raise AutoYAMLException('%s:%s: location "%s" is not a file.' % (
                                    self.env.doc2path(self.env.docname, None),
                                    self.content_offset - 1,
                                    location))
        self.record_dependencies.add(location)
        return output_nodes

    def _get_comments(self, source, source_file):
        comments = {}
        in_docstring = False
        for linenum, line in enumerate(source.splitlines(), start=1):
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
                comment.append(line, source_file, linenum)
            elif in_docstring:
                comments[linenum] = comment
                in_docstring = False
        return comments

    def _parse_document(self, doc, comments):
        tree = TreeNode(None, comments)
        if not isinstance(doc, MappingNode):
            return tree
        unvisited = [(doc, 0)]
        while len(unvisited) > 0:
            node, index = unvisited[-1]
            if index == len(node.value):
                if tree.parent is not None:
                    tree = tree.parent
                unvisited.pop()
                continue
            for key, value in node.value[index:]:
                index += 1
                unvisited[-1] = (node, index)
                if not isinstance(key, ScalarNode):
                    continue
                subtree = tree.add_child(key)
                if isinstance(value, MappingNode) and (
                            len(unvisited) + 1 <= self.config.autoyaml_level
                            or self.config.autoyaml_level == 0
                        ):
                    unvisited.append((value, 0))
                    tree = subtree
                    break
        return tree

    def _generate_documentation(self, tree):
        unvisited = [tree]
        while len(unvisited) > 0:
            node = unvisited[-1]
            if len(node.children) > 0:
                unvisited.append(node.remove_child())
                continue
            if node.parent is None or node.comment is None:
                unvisited.pop()
                continue
            with switch_source_input(self.state, node.comment):
                definition = nodes.definition()
                if isinstance(node.comment, ViewList):
                    self.state.nested_parse(node.comment, 0, definition)
                else:
                    definition += node.comment
                node.comment = nodes.definition_list_item(
                    '',
                    nodes.term('', node.value.value),
                    definition,
                )
                if node.parent.comment is None:
                    node.parent.comment = nodes.definition_list()
                elif not isinstance(
                        node.parent.comment,
                        nodes.definition_list):
                    with switch_source_input(self.state, node.parent.comment):
                        dlist = nodes.definition_list()
                        self.state.nested_parse(node.parent.comment, 0, dlist)
                        node.parent.comment = dlist
                node.parent.comment += node.comment
            unvisited.pop()
        return tree.comment

    def _parse_file(self, source_file):
        with open(source_file, 'r') as f:
            source = f.read()
        comments = self._get_comments(source, source_file)
        for doc in compose_all(source):
            docs = self._generate_documentation(
                self._parse_document(doc, comments)
            )
            if docs is not None:
                yield docs


def setup(app):
    app.add_directive('autoyaml', AutoYAMLDirective)
    app.add_config_value('autoyaml_root', '..', 'env')
    app.add_config_value('autoyaml_doc_delimiter', '###', 'env')
    app.add_config_value('autoyaml_comment', '#', 'env')
    app.add_config_value('autoyaml_level', 1, 'env')
