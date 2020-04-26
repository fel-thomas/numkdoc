import inspect
import warnings

from numpydoc.docscrape import FunctionDoc, ClassDoc

CLASS_TITLE_HEADING = 2
CLASS_METHOD_HEADING = 4
LINE_BREAK = lb = "\n"
FORCE_LINE_BREAK = flb = "\n<br>\n"


def parse_class(class_object):
    markdown = ""

    # using NumpyDoc to parse the class
    doc = ClassDoc(class_object)

    # start with the title, we use the class name
    markdown += heading(CLASS_TITLE_HEADING, class_object.__name__) + lb
    # inserting summary
    markdown += parse_summary(doc)
    # inserting signature
    markdown += parse_init_method(class_object)
    # inserting parameters
    markdown += parse_parameters(doc)
    # inserting methods
    markdown += parse_methods(class_object, doc)

    return markdown


def heading(level, name, id = None):
    markdown = ""

    if id is None:
        id = name
    markdown += f"{'#' * level} ```{name}``` " + " {: #" + str(id) + " data-toc-label='" + str(id) + "'}"

    return markdown

def indent(level):
    return " " * level


def parse_summary(doc):
    markdown = ""

    try:
        summary = lb.join(doc['Summary']) + flb
        markdown += summary
    except:
        raise
        warnings.warn(f"No summary found for class {doc._cls.__name__}.")

    return markdown

def parse_enum_in_signature(signature):
    if "<" in signature and ":" in signature:
        end_index = signature.index('>')
        signature = signature[:end_index - 3] + signature[end_index + 1:]
        signature = signature.replace('<', '')
    return signature

def parse_init_method(class_object):
    markdown = ""

    try:
        signature = "__init__" + str(inspect.signature(class_object.__init__))
        # sanity check if enum variable in the signature
        if "<" in signature and ":" in signature:
            signature = parse_enum_in_signature(signature)

        markdown += heading(CLASS_METHOD_HEADING, signature, "\_\_init__")
    except:
        raise
        warnings.warn(f"No signature found for class {class_object.__name__}.")

    return markdown


def parse_signature(doc, method):
    markdown = ""

    try:
        method_signature = doc['Signature']
        # sanity check if enum variable in the signature
        if "<" in method_signature and ":" in method_signature:
            method_signature = parse_enum_in_signature(method_signature)
        markdown += f"{heading(CLASS_METHOD_HEADING, method_signature, method)} {lb}{lb}"
    except:
        raise
        warnings.warn(f"No Signature found for method {method}.")

    return markdown


def parameter_line(param):
    return f"{indent(1)}* **{param.name}** : {param.type} {lb}{lb} {indent(3)}- {' '.join(param.desc)} {lb}{lb}"


def parse_parameters(doc):
    markdown = ""

    try:
        parameters = doc['Parameters']
        if len(parameters) > 0:
            markdown += f"{lb}  **Parameters**{lb}{lb}"

        for param in parameters:
            markdown += parameter_line(param)

    except:
        raise
        warnings.warn(f"No parameters found for {doc}.")

    return markdown


def parse_returns(doc):
    markdown = ""

    try:
        returns = doc['Returns']
        if len(returns) > 0:
            markdown += f"{lb} **Return**{lb}{lb}"

        for ret in returns:
            markdown += parameter_line(ret)

    except:
        raise
        warnings.warn(f"No return found for {doc._f.__name__}.")

    return markdown


def parse_methods(class_object, doc):
    markdown = ""

    # avoid private and builtin methods
    methods = [m for m in dir(class_object) if not m.startswith('_')]
    # sanity check
    if len(methods) > 0:
        markdown += f"{lb * 2}"

        for method in methods:
            try:
                # using NumpyDoc for function
                method_doc = FunctionDoc(getattr(class_object, method))
                # inserting the signature
                markdown += parse_signature(method_doc, method)
                # inserting the summary
                markdown += parse_summary(method_doc)
                # inserting the parameters
                markdown += parse_parameters(method_doc)
                # inserting return parameters
                markdown += parse_returns(method_doc)
                # leave a blank line
                markdown += flb
            except:
                raise
                warnings.warn(f"Skip parsing method {class_object.__name__}.{method}.")

    return markdown