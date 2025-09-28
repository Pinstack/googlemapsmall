"""Models package for Google Maps mall scraping dataclasses."""

from .brand import Brand
from .category import Category
from .mall import Mall
from .network_request import NetworkRequest
from .protobuf_message import ProtobufMessage

__all__ = [
    "Brand",
    "Category",
    "Mall",
    "NetworkRequest",
    "ProtobufMessage",
]
