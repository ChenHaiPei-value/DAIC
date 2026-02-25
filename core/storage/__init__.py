"""
DAIC 分布式存储系统

一个去中心化的、无需信任的存储网络，结合了IPFS、Filecoin和Sia的最佳特性。
"""

__version__ = "1.0.0"
__author__ = "DAIC Team"
__license__ = "AGPL-3.0"

from .client import DAICStorageClient
from .sharding import DataSharding
from .erasure_coding import ErasureCoding
from .proof import ZKStorageProof
from .selector import NodeSelector

__all__ = [
    "DAICStorageClient",
    "DataSharding",
    "ErasureCoding",
    "ZKStorageProof",
    "NodeSelector",
]
