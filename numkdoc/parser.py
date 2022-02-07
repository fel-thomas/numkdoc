import inspect
import warnings
import re

from numpydoc.docscrape import FunctionDoc, ClassDoc

from .utils import extract_wrapped, should_parse_method

CLASS_TITLE_HEADING = 2
CLASS_METHOD_HEADING = 4
LINE_BREAK = lb = "\n"
FORCE_LINE_BREAK = flb = "\n<br>\n"
WHITE_SPACE = "&nbsp;"


def parse_class(class_object):
    markdown = ""

    # using NumpyDoc to parse the class
    doc = ClassDoc(class_object)

    markdown += heading(CLASS_TITLE_HEADING, class_object.__name__) + lb
    markdown += parse_summary(doc)
    markdown += parse_signature(class_object.__init__)
    markdown += parse_parameters(doc, class_object.__init__)
    markdown += parse_methods(class_object, doc)

    return markdown


def heading(level, name, id=None):
    markdown = ""

    if id is None:
        id = name
    markdown += f"{'#' * level} <code>{str(name)}</code> " + \
        " {: #" + str(id) + " .numkdoc " + " data-toc-label='" + str(id) + "'}"

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


def parameter_signature(parameter):
    if 'self' in parameter:
        parameter = parameter.replace('self', "<span class='parameter-self'>self</span>")
    if ':' in parameter:
        # we have a type
        try:
            p_name, p_type = parameter.split(':')
            if p_name[0] == '(':
                p_name = p_name[1:]
                line = "("
            else:
                line = " "
            line += f"<span class='parameter-name'>{p_name}</span>: <span class='parameter-type'>{p_type}</span>"
            return line
        except:
            pass
    return parameter


def parse_signature(method):
    markdown = ""

    try:
        # sanity check
        method_name = method.__name__
        method_name = "\_\_init__" if method_name == '__init__' else method_name

        signature = f"{method_name}" 
        parameters = str(inspect.signature(method))
        first_line_padding = len(method_name.replace('\\', ''))

        accumulator = ""
        for p_id, p in enumerate(re.split(r',(?![^\[]*[\]])', parameters)):
            if p_id > 0 and (('[' in p and ']' not in p) or ('(' in p and ')' not in p)):
                accumulator += p + ","
                continue
            
            line = parameter_signature(accumulator + p)
            padding = WHITE_SPACE*first_line_padding if p_id > 0 else ""
            signature += padding + line + ",<br>"
            accumulator = ""
        signature = signature[:-5]

        markdown += f"{heading(CLASS_METHOD_HEADING, signature, method_name)} {lb} {lb}"     
    except:
        raise
        warnings.warn(f"No Signature found for method {method}.")

    return markdown



def parameter_line(param):
    if param.type not in [None, '']:
        return f"{indent(1)}* **<span class='parameter-name'>{param.name}</span>**\
            : <span class='parameter-type'>{param.type}</span> {lb}{lb} {indent(3)}- {parameter_description(param)} {lb}{lb}"
    else:
        return f"{indent(1)}* **<span class='parameter-name'>{param.name}</span>**\
            {lb}{lb} {indent(3)}- {parameter_description(param)} {lb}{lb}"


def parameter_description(param):
    # keeps the line break in the documentation only when there is a period before
    line = "<p>"
    for chunk in param.desc:
        if line[-1] != '.':
            line += f" {chunk}"
        else:
            line += f"</p><p> {chunk}"
    
    line += "</p>"

    return line


def parse_parameters(doc, method=None):
    markdown = ""

    try:
        parameters = doc['Parameters']
        if len(parameters) > 0:
            markdown += f"{lb}  **Parameters**" + lb + lb

        for param in parameters:
            if param.type == '' and method is not None:
                # try to find parameter if provided by typing
                signature = inspect.signature(method)
                typing = str(signature.parameters[param.name]).split(':')[-1].strip()
                param = param._replace(type = typing)

            markdown += parameter_line(param)

    except:
        raise
        warnings.warn(f"No parameters found for {doc}.")

    return markdown


def parse_returns(doc, method):
    markdown = ""

    try:
        returns = doc['Returns']
        if len(returns) > 0:
            markdown += f"{lb} **Return**{lb}{lb}"

        for ret in returns:
            if ret.name == '':
                # the typing make the scraper confuse name and type
                # we have to find the type from the signature
                ret = ret._replace(name = ret.type)
                signature = inspect.signature(method)
                ret = ret._replace(type = '')
                if '->' in str(signature):
                    ret_type = str(signature).split('->')[-1].strip()
                    ret = ret._replace(type = ret_type)

            markdown += parameter_line(ret)

    except:
        raise
        warnings.warn(f"No return found for {doc._f.__name__}.")

    return markdown


def parse_methods(class_object, doc):
    markdown = ""

    # avoid private and builtin methods
    methods = [m for m in dir(class_object) if should_parse_method(class_object, m)]
    
    # sanity check
    if len(methods) > 0:
        markdown += f"{lb * 2}"

        for method_key in methods:
            try:
                method = getattr(class_object, method_key)

                # check if the func is wrapped (decorator)
                if hasattr(method, "__closure__") and method.__closure__ is not None:
                    wrapped_method = extract_wrapped(method)
                    method = method if wrapped_method is None else wrapped_method

                method_doc = FunctionDoc(method)
                markdown += parse_signature(method)
                markdown += parse_summary(method_doc)
                markdown += parse_parameters(method_doc, method)
                markdown += parse_returns(method_doc, method)
                markdown += flb
            except:
                raise
                warnings.warn(
                    f"Skip parsing method {class_object.__name__}.{method}.")

    return markdown
