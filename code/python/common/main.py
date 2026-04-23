from abc import ABCMeta
from typing import Any, Type


class Singleton(ABCMeta):
    _instances = {}

    def __call__(cls: Type, *args: Any, **kwargs: Any) -> Type:
        if cls not in cls._instances:
            cls._instances[cls] = ABCMeta.__call__(cls, *args, **kwargs)
        return cls._instances[cls]
