from pydantic.main import ModelMetaclass as _PyModelMetaclass


class ModelMetaclass(_PyModelMetaclass):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        return obj.__post_init__()
