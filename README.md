# NumKdoc

NumKdoc is a plugin for Mkdoc allowing you to automatically generate documentation from your Numpy style docstring, by making a simple call to classes.

This project is not maintained, and the parsing is not complete. It is based on the NumpyDoc parser.


## Quick start

If you want to try this plugin as-it-is, follow these steps:

1. Download this repo and (eventually) unzip it in a folder

2. Inside the project folder, execute the command 
   `python setup.py develop` to install 
   the plugin on your local machine. 

3. Go to your mkdocs project folder, edit the `mkdocs.yml` file 
   and add these few lines at the end:

   ```yaml
   plugins:
       - numkdoc
   ```

That's it.
Now you can call the parsing of a class using the tag `{{ module.ClassName }}`,
Numkdoc will automatically substitue that tag with the class documentation.

### Example

For example, you could edit the `docs/api/core.md`
file and insert the tag in any place, like this:

````markdown
# Core Api

[...]

{{ src.module.Class }}

[...]

````