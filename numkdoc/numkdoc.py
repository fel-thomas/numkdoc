from numkdoc.utils import REPLACES
import re
import inspect
from importlib import import_module

from mkdocs.plugins import BasePlugin

from .parser import parse_class, parse_method


class Numkdoc(BasePlugin):
    # caching classes to markdown for fast hot_reload
    _class_cache = {}
    _function_cache = {}

    def on_page_markdown(self, markdown, **kwargs):
        """hook triggering before converting markdown to html"""

        # check the documentation for all the call to a class
        # e.g {{ module.submodule.ClassName }} will render the document of 'ClassName'
        classes_to_load = re.findall('{{(.+?)}}', markdown)

        # sanity check
        if len(classes_to_load) == 0:
            return markdown

        for class_string in classes_to_load:
            directory = class_string.split('.')[:-1]
            class_name = class_string.split('.')[-1]

            if class_name not in self._class_cache and class_name not in self._function_cache:
                # loading the module
                try:
                    module = import_module(str.join('.', directory))
                except:
                    raise ValueError(f"Cant load module {class_string}.")

                # parse and store all the classes in the module
                for name, data in inspect.getmembers(module, inspect.isclass):
                    if name not in self._class_cache:
                        document = parse_class(data)
                        for old, new in REPLACES:
                            document = document.replace(old, new)
                        self._class_cache[name] = document

                # parse and store all the functions in the module
                for name, data in inspect.getmembers(module, inspect.isfunction):
                    if name not in self._function_cache:
                        print('trying to parse function', name, 'with data', data)
                        try:
                            document = parse_method(data)
                            for old, new in REPLACES:
                                document = document.replace(old, new)
                            self._function_cache[name] = document
                        except:
                            print('failed to parse function', name)

            # replace the call with the documentation of the class
            if class_name in self._class_cache:
                markdown = markdown.replace(
                    "{{"+class_string+"}}", self._class_cache[class_name])
            elif class_name in self._function_cache:
                markdown = markdown.replace(
                    "{{"+class_string+"}}", self._function_cache[class_name])
            else:
                raise ValueError(f"Class {class_string} not found.")

        return markdown
