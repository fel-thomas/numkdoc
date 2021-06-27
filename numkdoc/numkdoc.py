from numkdoc.utils import REPLACES
import os
import re
import inspect
from importlib import import_module

from mkdocs.plugins import BasePlugin

from .parser import parse_class


class Numkdoc(BasePlugin):
    # caching classes to markdown for fast hot_reload
    _cache = {}

    def on_page_markdown(self, markdown, **kwargs):
        """hook triggering before converting markdown to html"""

        # get the current directory
        cwd = os.getcwd()

        # check the documentation for all the call to a class
        # e.g {{ module.submodule.ClassName }} will render the document of 'ClassName'
        classes_to_load = re.findall('{{(.+?)}}', markdown)

        # sanity check
        if len(classes_to_load) == 0:
            return markdown

        for class_string in classes_to_load:
            directory = class_string.split('.')[:-1]
            class_name = class_string.split('.')[-1]

            if class_name not in self._cache:
                # loading the module
                try:
                    module = import_module(str.join('.', directory))
                except:
                    raise ValueError(f"Cant load module {class_string}.")

                # parse and store all the classes in the module
                for name, data in inspect.getmembers(module, inspect.isclass):
                    if name not in self._cache:
                        document = parse_class(data)
                        for old, new in REPLACES:
                            document = document.replace(old, new)
                        self._cache[name] = document
                        
            # replace the call with the documentation of the class            
            markdown = markdown.replace(
                "{{"+class_string+"}}", self._cache[class_name])

        return markdown
