import re


def parse_args(markdown):
    """ Retrieve the module called as well as any parameters passed.
    our pattern:
    - It starts with '{{' and ends with '}}', allowing for extra whitespace.
    - It captures the class/module path up to an optional pipe '|' character.
    - If a pipe is present, it captures everything after it as a parameters string.

    e.g. {{ module.submodule.ClassName | param1=value1, param2=value2 }}
    """
    pattern = re.compile(r'{{\s*([^|}]+?)\s*(?:\|\s*(.+?))?\s*}}')
    results = []

    for match in pattern.finditer(markdown):
        full_match = match.group(0)

        # extract the class path and strip any extra whitespace.
        class_path = match.group(1).strip()

        # initialize an empty dictionary for parameters.
        params = {}

        # if a parameters string is present, process it.
        params_str = match.group(2)
        if params_str:
            # split the string by commas to separate each key-value pair.
            # this simple split assumes parameter values do not include commas.
            pairs = params_str.split(',')
            for pair in pairs:
                # for each pair, split by '='. We only split once in case the value contains '='.
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip()] = value.strip()
                else:
                    # case where a pair does not have an '='.
                    # @tfel we might want to handle something here, leaving it as is for now.
                    pass

        results.append((class_path, params, full_match))

    return results
