from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class DatabaseAdapter(ABC):
    @abstractmethod
    def create(self, table: str, item_model: BaseModel) -> None:
        """Creates an item in the specified table based on the BaseModel sent"""
        pass

    @abstractmethod
    def delete(self, table: str, keys: dict[str, Any]) -> None:
        """Deletes items that matches the keys, keys must be sent in format specified by the implementation"""
        pass

    @abstractmethod
    def lookup(
        self,
        table: str,
        keys: dict[str, Any],
        model_type: Type[T],
    ) -> Optional[T]:
        """Based on the keys sent, returns (if found) an instance of the mapping model sent"""
        pass

    @abstractmethod
    def list_all(self, table: str, model_type: Type[T]) -> list[T]:
        """Returns all the items found in the table, as list of instances of the model sent"""
        pass
