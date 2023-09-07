"""
Simple YAML templating engine that supports variables, including other
YAML files, text files, and Jinja2 templates. The context passed is universally
available across all file types - YAML, text files, and Jinja2 templates.

Usage
-----

# Reading to Python - does yaml.load() under the hood:
python_object = load_yaml_template('my_template.yaml', context={
    'variable1': 'gav',
    'variable2': 42,
})

# Resulting Python objects can be written back to YAML, as usual:
with open(filename, 'w') as f:
    f.write(yaml.dump(python_object))


Syntax reference
----------------

YAML:
  SimpleVariable: !var var_name
  IncludeOtherYAMLTemplate: !include other-template.yaml
  UsingVariableInAString: !format "string with a {var_name} inside"
  StringFromATextFile: !file file_name
  StringFromJinja2Template: !template file_name

Jinja2:

Use {{ var_name }} variables and {% include 'other_templates.j2' %} as
usual. All other Jinja2 features are also available, like macros, etc.
You can also include rendered YAML templates, like this:
{{ yaml('filename.yaml') }}
And, of course, text files, like this: {{ file('filename.ini') }}

Text files:

You can use any {var_name} in the file contents. It'll be rendered with
built-in Python str.format() function, so you can use any syntax that it
supports: https://docs.python.org/3/library/string.html#format-string-syntax
If you need to escape curly brackets, write them twice, like this: {{ or }}


File paths
----------

Included file paths (YAML, text, Jinja2) are relative to the directory of
the YAML template passed to load_yaml_template() function.


Credits
-------

The implementation idea is borrowed from https://stackoverflow.com/a/9577670

"""
from pathlib import Path

import jinja2
import yaml


class YamlTemplateLoader(yaml.SafeLoader):
    _context = {}

    def __init__(self, stream):
        self._root = Path(stream.name).parent
        self._jinja = jinja2.Environment(  # nosec
            loader=jinja2.FileSystemLoader(self._root),
        )
        self._jinja.globals.update(
            {
                "file": self._file,
                "yaml": self._yaml_dump,
            }
        )
        super().__init__(stream)

    def _yaml(self, filename):
        with (self._root / filename).open() as f:
            return yaml.load(f, self.__class__)  # nosec

    def _yaml_dump(self, filename):
        ret = yaml.dump(self._yaml(filename), sort_keys=False)
        return ret

    def include(self, node):
        """
        Usage: !include <another-template.yaml>
        """
        return self._yaml(self.construct_scalar(node))

    def var(self, node):
        """
        Usage: !var <name>
        """
        return self._context[self.construct_scalar(node)]

    def format(self, node):
        """
        Usage: !format "string with a {variable} included"
        """
        return self.construct_scalar(node).format(**self._context)

    def _file(self, filename):
        with (self._root / filename).open() as f:
            return f.read().format(**self._context)

    def file(self, node):
        """
        Usage: !file <filename>
        """
        return self._file(self.construct_scalar(node))

    def template(self, node):
        """
        Usage: !template <filename>
        """
        template_name = self.construct_scalar(node)
        result = self._jinja.get_template(template_name).render(self._context)
        return result


YamlTemplateLoader.add_constructor("!include", YamlTemplateLoader.include)
YamlTemplateLoader.add_constructor("!var", YamlTemplateLoader.var)
YamlTemplateLoader.add_constructor("!format", YamlTemplateLoader.format)
YamlTemplateLoader.add_constructor("!file", YamlTemplateLoader.file)
YamlTemplateLoader.add_constructor("!template", YamlTemplateLoader.template)


def load_yaml_template(path, context):
    class Loader(YamlTemplateLoader):
        _context = context

    with path.open() as f:
        return yaml.load(f, Loader)  # nosec
