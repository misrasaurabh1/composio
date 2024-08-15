"""
Composio client base.
"""

import typing as t

import requests

from composio.client.endpoints import Endpoint
from composio.client.exceptions import HTTPError, NoItemsFound
from composio.client.http import HttpClient
from composio.utils import logging


ModelType = t.TypeVar("ModelType")
CollectionType = t.TypeVar("CollectionType", list, dict)


class Collection(t.Generic[ModelType], logging.WithLogger):
    """Data model collection for representing server objects."""

    endpoint: Endpoint
    model: t.Type[ModelType]

    _list_key: str = "items"

    def __init__(self, client: "BaseClient") -> None:
        """Initialize conntected accounts models namespace."""
        logging.WithLogger.__init__(self)
        self.client = client

    def _raise_if_required(
        self,
        response: requests.Response,
        status_code: int = 200,
    ) -> requests.Response:
        """
        Raise if HTTP response is not expected.

        :param response: Http response
        :param status_code: Expected status code
        :raises composio.client.exceptions.HTTPError: If the status code does
                not match with the expected status code
        """
        if response.status_code != status_code:
            raise HTTPError(
                message=response.content.decode(encoding="utf-8"),
                status_code=response.status_code,
            )

    def _raise_if_empty(self, collection: CollectionType) -> CollectionType:
        """Raise if provided colleciton is empty."""
        if len(collection) > 0:
            return collection
        raise NoItemsFound(message="No items found")

    def get(self, queries: t.Optional[t.Dict[str, str]] = None) -> t.List[ModelType]:
        """List available models."""
        response = self.client.http.get(url=str(self.endpoint(queries=queries or {})))
        self._raise_if_required(response)

        data = response.json()
        list_key = getattr(self, "_list_key", None)

        if isinstance(data, list):
            return [self.model(**item) for item in data]
        elif list_key and list_key in data:
            return [self.model(**item) for item in data[list_key]]
        else:
            raise HTTPError(
                message=f"Received invalid data object: {response.content.decode()}",
                status_code=response.status_code,
            )


class BaseClient:
    """Composio client abstraction."""

    http: HttpClient
    local: t.Any
    api_key: str
