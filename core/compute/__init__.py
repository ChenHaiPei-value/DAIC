"""
GPU分布式去中心化计算协议

本模块实现了"AI大模型运行的GPU分布式去中心化 - 大家一起提供GPU算力"的核心功能。
通过去中心化的方式，聚合全球闲置GPU资源，为AI大模型训练和推理提供分布式计算能力。
"""

__version__ = "1.0.0"
__author__ = "DAIC Team"
__license__ = "AGPL-3.0"

from .node_manager import ComputeNode, NodeManager
from .task_scheduler import TaskScheduler, TaskManager
from .compute_proof import ComputeProof, ProofVerifier
from .reward_system import RewardSystem, RewardCalculator
from .gpu_discovery import GPUDiscovery, GPUInfo
from .container_orchestrator import ContainerOrchestrator
from .security import SecurityManager, EncryptionService
from .monitoring import MonitoringSystem, MetricsCollector

__all__ = [
    # 节点管理
    "ComputeNode",
    "NodeManager",
    
    # 任务调度
    "TaskScheduler",
    "TaskManager",
    
    # 计算证明
    "ComputeProof",
    "ProofVerifier",
    
    # 奖励系统
    "RewardSystem",
    "RewardCalculator",
    
    # GPU发现
    "GPUDiscovery",
    "GPUInfo",
    
    # 容器编排
    "ContainerOrchestrator",
    
    # 安全机制
    "SecurityManager",
    "EncryptionService",
    
    # 监控系统
    "MonitoringSystem",
    "MetricsCollector",
]