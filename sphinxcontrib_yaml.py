import os
import re

import sphinx
from sphinx.ext.autodoc import Documenter


class YAMLDocumenter(Documenter):
    """Class to retrieve documentation from YAML and convert to reST.
    Only YAML comments started with *self.autoyaml_doc_delimeter* are
    being used for documentation. If comment is multi-line, only the
    first line has to be started with *self.autoyaml_doc_delimeter*"""

    objtype = 'yaml'

    def get_yaml_comment_docs(self, yml_file):
        with open(yml_file) as src:
            doc_enabled = False
            for line in src.readlines():
                if line.startswith(self.autoyaml_doc_delimeter):
                    doc_enabled = not doc_enabled
                    if len(self.autoyaml_doc_delimeter) + 1 < len(line):
                        # insert comment after delimeter, if it exists
                        yield line[len(self.autoyaml_doc_delimeter)+1:]
                elif line.startswith(self.autoyaml_comment) and doc_enabled:
                    yield line[len(self.autoyaml_comment):]
                elif not line.startswith(self.autoyaml_comment) \
                        and doc_enabled:
                    doc_enabled = False
                    yield ''

    def add_lines(self, lines, src):
        content = '\n'.join([i for i in lines])
        self.directive.result.append(content, src)

    def generate(self, more_content=None, real_modname=None,
                 check_module=False, all_members=False):
        """Generate reST for the file given by *self.name* or all *.yaml and
        *.yml files in directory *self.name*"""
        self.autoyaml_root = self.options.autoyaml_root \
                    or self.env.config.autoyaml_root
        self.autoyaml_doc_delimeter = self.options.autoyaml_doc_delimeter \
                    or self.env.config.autoyaml_doc_delimeter
        self.autoyaml_comment = self.options.autoyaml_comment \
                    or self.env.config.autoyaml_comment
        self.fullpath = self.autoyaml_root + '/' + self.name
        if not os.path.exists(self.fullpath):
            raise ValueError('autoyaml path not found: %s' % (self.fullpath))
        if os.path.isdir(self.fullpath):
            # recurse through all directories and document every YAML file
            for cur_dir, dirs, files in os.walk(self.fullpath):
                for f in [i for i in files if i.endswith('.yml') \
                          or i.endswith('.yaml')]:
                    yml_path = cur_dir + '/' + f
                    self.directive.filename_set.add(yml_path)
                    self.add_lines(
                        self.get_yaml_comment_docs(yml_path),
                        yml_path)
        else:
            self.directive.filename_set.add(self.fullpath)
            self.add_lines(
                self.get_yaml_comment_docs(self.fullpath),
                self.fullpath)

def setup(app):
    app.add_autodocumenter(YAMLDocumenter)
    app.add_config_value('autoyaml_root', '..', True)
    app.add_config_value('autoyaml_doc_delimeter', '###', True)
    app.add_config_value('autoyaml_comment', '# ', True)

    return {'version': sphinx.__display_version__}
