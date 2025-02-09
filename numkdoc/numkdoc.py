from numkdoc.utils import REPLACES
import re
import inspect
from importlib import import_module

from mkdocs.plugins import BasePlugin

from .parser import parse_class, parse_method
from .args_parser import parse_args


class Numkdoc(BasePlugin):
    # caching classes to markdown for fast hot_reload
    _class_cache = {}
    _function_cache = {}

    def on_page_markdown(self, markdown, **kwargs):
        """hook triggering before converting markdown to html"""

        # check the documentation for all the call to a class
        # e.g {{ module.submodule.ClassName }} will render the document of 'ClassName'
        args = parse_args(markdown)

        # nothing to do here
        if len(args) == 0:
            return markdown
        classes_to_load = [arg[0] for arg in args]
        parameters = [arg[1] for arg in args]
        matches = [arg[2] for arg in args]

        for class_string, parsing_params, full_match in zip(classes_to_load, parameters, matches):
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
                        document = parse_class(data, **parsing_params)
                        for old, new in REPLACES:
                            document = document.replace(old, new)
                        self._class_cache[name] = document

                # parse and store all the functions in the module
                for name, data in inspect.getmembers(module, inspect.isfunction):
                    if name not in self._function_cache:
                        try:
                            document = parse_method(data)
                            for old, new in REPLACES:
                                document = document.replace(old, new)
                            self._function_cache[name] = document
                        except:
                            print('failed to parse function', name, "with data", data)
                            pass

            # replace the call with the documentation of the class
            if class_name in self._class_cache:
                markdown = markdown.replace(full_match, self._class_cache[class_name])
            elif class_name in self._function_cache:
                markdown = markdown.replace(full_match, self._function_cache[class_name])
            else:
                raise ValueError(f"Class {class_string} not found.")

        return markdown
