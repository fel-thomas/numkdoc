import inspect
from types import FunctionType

REPLACES = [
    ("tensorflow.python.data.ops.dataset_ops.DatasetV2", "tf.Dataset"),
    ("tensorflow.python.framework.ops.Tensor", "tf.Tensor"),
    ("tensorflow.python.keras.engine.training.Model", "tf.keras.Model"),
    ("tensorflow.python.keras.engine.base_layer.Layer", "tf.keras.layers.Layer"),
    ("NoneType", "None")
]


def extract_wrapped(decorated):
    closure = (c.cell_contents for c in decorated.__closure__)
    return next((c for c in closure if isinstance(c, FunctionType)), None)


def should_parse_method(class_object, method_key):
    # only if public and valid method
    try:
        method = getattr(class_object, method_key)

        is_method  = inspect.ismethod(method)
        is_wrapped = hasattr(method, '__closure__') or hasattr(method, '__wrapped__')
        is_private = method_key.startswith('_')
        
        return (is_method or is_wrapped) and not is_private
    except:
        return False
