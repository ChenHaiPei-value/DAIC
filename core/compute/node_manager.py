"""
节点管理模块

负责GPU计算节点的注册、验证、健康检查和信誉评分。
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import json

from .security import SecurityManager
from .monitoring import MetricsCollector

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """节点状态枚举"""
    OFFLINE = "offline"          # 离线
    REGISTERING = "registering"  # 注册中
    ONLINE = "online"            # 在线
    BUSY = "busy"               # 忙碌
    MAINTENANCE = "maintenance"  # 维护中
    SUSPENDED = "suspended"      # 暂停


class GPUType(Enum):
    """GPU类型枚举"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    APPLE = "apple"
    OTHER = "other"


@dataclass
class GPUInfo:
    """GPU硬件信息"""
    gpu_id: str
    type: GPUType
    model: str
    memory_gb: float
    cuda_cores: Optional[int] = None
    tensor_cores: Optional[int] = None
    bandwidth_gbps: Optional[float] = None
    clock_speed_mhz: Optional[float] = None
    power_limit_w: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "gpu_id": self.gpu_id,
            "type": self.type.value,
            "model": self.model,
            "memory_gb": self.memory_gb,
            "cuda_cores": self.cuda_cores,
            "tensor_cores": self.tensor_cores,
            "bandwidth_gbps": self.bandwidth_gbps,
            "clock_speed_mhz": self.clock_speed_mhz,
            "power_limit_w": self.power_limit_w,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "GPUInfo":
        """从字典创建"""
        return cls(
            gpu_id=data["gpu_id"],
            type=GPUType(data["type"]),
            model=data["model"],
            memory_gb=data["memory_gb"],
            cuda_cores=data.get("cuda_cores"),
            tensor_cores=data.get("tensor_cores"),
            bandwidth_gbps=data.get("bandwidth_gbps"),
            clock_speed_mhz=data.get("clock_speed_mhz"),
            power_limit_w=data.get("power_limit_w"),
        )


@dataclass
class NetworkInfo:
    """网络信息"""
    ip_address: str
    port: int
    bandwidth_mbps: float
    latency_ms: Optional[float] = None
    public_key: Optional[str] = None
    certificate: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "ip_address": self.ip_address,
            "port": self.port,
            "bandwidth_mbps": self.bandwidth_mbps,
            "latency_ms": self.latency_ms,
            "public_key": self.public_key,
            "certificate": self.certificate,
        }


@dataclass
class NodeMetrics:
    """节点性能指标"""
    uptime_hours: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_task_duration_seconds: float = 0.0
    gpu_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0
    network_throughput_mbps: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_utilization(self, gpu_util: float, memory_util: float):
        """更新利用率指标"""
        self.gpu_utilization_percent = gpu_util
        self.memory_utilization_percent = memory_util
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "uptime_hours": self.uptime_hours,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_task_duration_seconds": self.avg_task_duration_seconds,
            "gpu_utilization_percent": self.gpu_utilization_percent,
            "memory_utilization_percent": self.memory_utilization_percent,
            "network_throughput_mbps": self.network_throughput_mbps,
            "last_updated": self.last_updated.isoformat(),
        }


class ComputeNode:
    """计算节点类"""
    
    def __init__(
        self,
        node_id: str,
        gpu_info: List[GPUInfo],
        network_info: NetworkInfo,
        storage_capacity_gb: float = 100.0,
        max_concurrent_tasks: int = 1,
    ):
        """
        初始化计算节点
        
        Args:
            node_id: 节点唯一标识
            gpu_info: GPU硬件信息列表
            network_info: 网络信息
            storage_capacity_gb: 存储容量(GB)
            max_concurrent_tasks: 最大并发任务数
        """
        self.node_id = node_id
        self.gpu_info = gpu_info
        self.network_info = network_info
        self.storage_capacity_gb = storage_capacity_gb
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # 状态信息
        self.status = NodeStatus.REGISTERING
        self.registration_time = datetime.now()
        self.last_heartbeat = datetime.now()
        
        # 性能指标
        self.metrics = NodeMetrics()
        
        # 安全组件
        self.security_manager = SecurityManager()
        
        # 监控组件
        self.metrics_collector = MetricsCollector(node_id)
        
        # 任务队列
        self.current_tasks: Set[str] = set()
        self.task_history: List[Dict] = []
        
        # 信誉评分
        self.reputation_score = 100.0  # 初始信誉分100
        self.reputation_history: List[Tuple[datetime, float]] = []
        
        logger.info(f"计算节点 {node_id} 初始化完成")
    
    def register_to_network(self, network_address: str) -> bool:
        """
        注册到计算网络
        
        Args:
            network_address: 网络地址
            
        Returns:
            注册是否成功
        """
        try:
            # 生成节点证书
            certificate = self.security_manager.generate_node_certificate(
                node_id=self.node_id,
                public_key=self.network_info.public_key,
            )
            
            # 更新网络信息
            self.network_info.certificate = certificate
            
            # 发送注册请求
            registration_data = {
                "node_id": self.node_id,
                "gpu_info": [gpu.to_dict() for gpu in self.gpu_info],
                "network_info": self.network_info.to_dict(),
                "storage_capacity_gb": self.storage_capacity_gb,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "certificate": certificate,
                "timestamp": datetime.now().isoformat(),
            }
            
            # 签名注册数据
            signature = self.security_manager.sign_data(
                json.dumps(registration_data, sort_keys=True)
            )
            
            # TODO: 实际发送注册请求到网络
            # 这里模拟注册成功
            logger.info(f"节点 {self.node_id} 注册到网络 {network_address}")
            
            # 更新状态
            self.status = NodeStatus.ONLINE
            self.metrics_collector.record_event("node_registered")
            
            return True
            
        except Exception as e:
            logger.error(f"节点注册失败: {e}")
            return False
    
    def start_serving(self):
        """开始接收计算任务"""
        if self.status != NodeStatus.ONLINE:
            logger.warning(f"节点 {self.node_id} 状态为 {self.status.value}，无法开始服务")
            return
        
        logger.info(f"节点 {self.node_id} 开始接收计算任务")
        
        # 启动心跳任务
        asyncio.create_task(self._heartbeat_task())
        
        # 启动监控任务
        asyncio.create_task(self._monitoring_task())
        
        # 更新状态
        self.status = NodeStatus.ONLINE
        self.metrics_collector.record_event("node_started_serving")
    
    async def _heartbeat_task(self):
        """心跳任务"""
        while self.status in [NodeStatus.ONLINE, NodeStatus.BUSY]:
            try:
                # 发送心跳
                heartbeat_data = {
                    "node_id": self.node_id,
                    "status": self.status.value,
                    "timestamp": datetime.now().isoformat(),
                    "metrics": self.metrics.to_dict(),
                    "current_tasks": list(self.current_tasks),
                }
                
                # TODO: 实际发送心跳到网络
                # 这里模拟心跳发送
                
                # 更新最后心跳时间
                self.last_heartbeat = datetime.now()
                
                # 记录心跳
                self.metrics_collector.record_heartbeat()
                
                # 等待下一次心跳
                await asyncio.sleep(30)  # 30秒一次心跳
                
            except Exception as e:
                logger.error(f"心跳任务异常: {e}")
                await asyncio.sleep(5)
    
    async def _monitoring_task(self):
        """监控任务"""
        while self.status in [NodeStatus.ONLINE, NodeStatus.BUSY]:
            try:
                # 收集GPU利用率
                gpu_util = await self._get_gpu_utilization()
                memory_util = await self._get_memory_utilization()
                
                # 更新指标
                self.metrics.update_utilization(gpu_util, memory_util)
                
                # 更新运行时间
                uptime = (datetime.now() - self.registration_time).total_seconds() / 3600
                self.metrics.uptime_hours = uptime
                
                # 记录监控数据
                self.metrics_collector.record_metrics({
                    "gpu_utilization": gpu_util,
                    "memory_utilization": memory_util,
                    "uptime_hours": uptime,
                })
                
                # 检查是否需要调整状态
                if len(self.current_tasks) >= self.max_concurrent_tasks:
                    self.status = NodeStatus.BUSY
                else:
                    self.status = NodeStatus.ONLINE
                
                # 等待下一次监控
                await asyncio.sleep(10)  # 10秒一次监控
                
            except Exception as e:
                logger.error(f"监控任务异常: {e}")
                await asyncio.sleep(5)
    
    async def _get_gpu_utilization(self) -> float:
        """获取GPU利用率"""
        # TODO: 实际获取GPU利用率
        # 这里模拟返回一个随机值
        import random
        return random.uniform(0.0, 100.0)
    
    async def _get_memory_utilization(self) -> float:
        """获取内存利用率"""
        # TODO: 实际获取内存利用率
        # 这里模拟返回一个随机值
        import random
        return random.uniform(0.0, 100.0)
    
    def accept_task(self, task_id: str, task_spec: Dict) -> bool:
        """
        接受计算任务
        
        Args:
            task_id: 任务ID
            task_spec: 任务规格
            
        Returns:
            是否接受任务
        """
        if self.status not in [NodeStatus.ONLINE, NodeStatus.BUSY]:
            logger.warning(f"节点 {self.node_id} 状态为 {self.status.value}，无法接受任务")
            return False
        
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            logger.warning(f"节点 {self.node_id} 已达到最大并发任务数")
            return False
        
        # 检查任务资源需求
        if not self._check_task_resources(task_spec):
            logger.warning(f"节点 {self.node_id} 资源不足，无法接受任务")
            return False
        
        # 接受任务
        self.current_tasks.add(task_id)
        
        # 记录任务历史
        self.task_history.append({
            "task_id": task_id,
            "accept_time": datetime.now().isoformat(),
            "task_spec": task_spec,
        })
        
        # 更新状态
        self.status = NodeStatus.BUSY
        
        logger.info(f"节点 {self.node_id} 接受任务 {task_id}")
        self.metrics_collector.record_event("task_accepted", {"task_id": task_id})
        
        return True
    
    def _check_task_resources(self, task_spec: Dict) -> bool:
        """检查任务资源需求"""
        required_gpu_memory = task_spec.get("gpu_memory_gb", 0)
        required_storage = task_spec.get("storage_gb", 0)
        
        # 检查GPU内存
        available_gpu_memory = sum(gpu.memory_gb for gpu in self.gpu_info)
        if required_gpu_memory > available_gpu_memory:
            return False
        
        # 检查存储空间
        if required_storage > self.storage_capacity_gb:
            return False
        
        return True
    
    def complete_task(self, task_id: str, result: Dict) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            result: 任务结果
            
        Returns:
            是否成功完成任务
        """
        if task_id not in self.current_tasks:
            logger.warning(f"任务 {task_id} 不在当前任务列表中")
            return False
        
        # 从当前任务中移除
        self.current_tasks.remove(task_id)
        
        # 更新任务历史
        for task in self.task_history:
            if task["task_id"] == task_id:
                task["complete_time"] = datetime.now().isoformat()
                task["result"] = result
                break
        
        # 更新性能指标
        self.metrics.tasks_completed += 1
        
        # 更新信誉评分
        self._update_reputation_score(True)
        
        # 更新状态
        if len(self.current_tasks) == 0:
            self.status = NodeStatus.ONLINE
        
        logger.info(f"节点 {self.node_id} 完成任务 {task_id}")
        self.metrics_collector.record_event("task_completed", {"task_id": task_id})
        
        return True
    
    def fail_task(self, task_id: str, error_message: str):
        """
        任务失败
        
        Args:
            task_id: 任务ID
            error_message: 错误信息
        """
        if task_id not in self.current_tasks:
            logger.warning(f"任务 {task_id} 不在当前任务列表中")
            return
        
        # 从当前任务中移除
        self.current_tasks.remove(task_id)
        
        # 更新任务历史
        for task in self.task_history:
            if task["task_id"] == task_id:
                task["fail_time"] = datetime.now().isoformat()
                task["error"] = error_message
                break
        
        # 更新性能指标
        self.metrics.tasks_failed += 1
        
        # 更新信誉评分
        self._update_reputation_score(False)
        
        # 更新状态
        if len(self.current_tasks) == 0:
            self.status = NodeStatus.ONLINE
        
        logger.error(f"节点 {self.node_id} 任务 {task_id} 失败: {error_message}")
        self.metrics_collector.record_event("task_failed", {
            "task_id": task_id,
            "error": error_message,
        })
    
    def _update_reputation_score(self, success: bool):
        """更新信誉评分"""
        if success:
            # 任务成功，信誉分增加
            increase = 1.0
            # 连续成功有额外加成
            recent_failures = sum(1 for t in self.task_history[-10:] if "error" in t)
            if recent_failures == 0:
                increase *= 1.5
            self.reputation_score = min(100.0, self.reputation_score + increase)
        else:
            # 任务失败，信誉分减少
            decrease = 5.0
            # 连续失败有额外惩罚
            recent_failures = sum(1 for t in self.task_history[-5:] if "error" in t)
            if recent_failures > 2:
                decrease *= 2.0
            self.reputation_score = max(0.0, self.reputation_score - decrease)
        
        # 记录信誉历史
        self.reputation_history.append((datetime.now(), self.reputation_score))
        
        # 如果信誉分过低，暂停节点
        if self.reputation_score < 30.0:
            self.status = NodeStatus.SUSPENDED
            logger.warning(f"节点 {self.node_id} 信誉分过低({self.reputation_score})，已暂停")
    
    def get_node_info(self) -> Dict:
        """获取节点信息"""
        return {
            "node_id": self.node_id,
            "status": self.status.value,
            "gpu_info": [gpu.to_dict() for gpu in self.gpu_info],
            "network_info": self.network_info.to_dict(),
            "storage_capacity_gb": self.storage_capacity_gb,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "current_tasks": list(self.current_tasks),
            "metrics": self.metrics.to_dict(),
            "reputation_score": self.reputation_score,
            "registration_time": self.registration_time.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
        }
    
    def schedule_maintenance(self, maintenance_time: datetime = None):
        """安排维护"""
        if not maintenance_time:
            maintenance_time = datetime.now() + timedelta(hours=1)
        
        self.status = NodeStatus.MAINTENANCE
        logger.info(f"节点 {self.node_id} 安排维护: {maintenance_time.isoformat()}")


class NodeManager:
    """节点管理器"""
    
    def __init__(self):
        self.nodes: Dict[str, ComputeNode] = {}
        self.node_registry: Dict[str, Dict] = {}  # 节点注册表
        
        logger.info("节点管理器初始化完成")
    
    def register_node(self, node: ComputeNode):
        """注册节点"""
        self.nodes[node.node_id] = node
        self.node_registry[node.node_id] = node.get_node_info()
        
        logger.info(f"注册节点: {node.node_id}")
    
    def unregister_node(self, node_id: str):
        """注销节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            del self.node_registry[node_id]
            logger.info(f"注销节点: {node_id}")
    
    def get_node(self, node_id: str) -> Optional[ComputeNode]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_available_nodes(self, requirements: Dict) -> List[ComputeNode]:
        """获取可用节点"""
        available = []
        
        for node in self.nodes.values():
            # 检查节点状态
            if node.status not in [NodeStatus.ONLINE, NodeStatus.BUSY]:
                continue
            
            # 检查资源需求
            if not node._check_task_resources(requirements):
                continue
            
            available.append(node)
        
        # 按信誉评分排序
        available.sort(key=lambda n: n.reputation_score, reverse=True)
        
        return available
    
    def get_node_statistics(self) -> Dict:
        """获取节点统计信息"""
        total_nodes = len(self.nodes)
        
        # 按状态统计
        status_stats = {}
        for status in NodeStatus:
            status_stats[status.value] = 0
        
        # 计算统计信息
        total_gpu_memory = 0
        total_reputation = 0
        
        for node in self.nodes.values():
            status_stats[node.status.value] += 1
            total_gpu_memory += sum(gpu.memory_gb for gpu in node.gpu_info)
            total_reputation += node.reputation_score
        
        # 计算平均值
        avg_reputation = total_reputation / total_nodes if total_nodes > 0 else 0
        
        return {
            "total_nodes": total_nodes,
            "status_distribution": status_stats,
            "total_gpu_memory_gb": total_gpu_memory,
            "average_reputation_score": avg_reputation,
        }


# 演示函数
async def demo_node_manager():
    """演示节点管理器"""
    print("="*50)
    print("节点管理器演示")
    print("="*50)
    
    # 创建节点管理器
    node_manager = NodeManager()
    
    # 创建GPU信息
    gpu_info = GPUInfo(
        gpu_id="gpu1",
        type=GPUType.NVIDIA,
        model="RTX 4090",
        memory_gb=24.0,
        cuda_cores=16384,
        tensor_cores=512,
        bandwidth_gbps=1008,
    )
    
    # 创建网络信息
    network_info = NetworkInfo(
        ip_address="192.168.1.100",
        port=8080,
        bandwidth_mbps=1000,
        latency_ms=5.0,
    )
    
    # 创建节点
    node = ComputeNode(
        node_id="node_001",
        gpu_info=[gpu_info],
        network_info=network_info,
        storage_capacity_gb=500.0,
        max_concurrent_tasks=4,
    )
    
    # 注册节点
    node_manager.register_node(node)
    
    # 注册到网络
    success = node.register_to_network("daic-network.example.com")
    print(f"节点注册到网络: {'成功' if success else '失败'}")
    
    if success:
        # 开始服务
        node.start_serving()
        
        # 等待节点启动
        await asyncio.sleep(1)
        
        # 创建任务
        task = {
            "task_id": "task_001",
            "gpu_memory_gb": 8.0,
            "storage_gb": 50.0,
        }
        
        # 接受任务
        if node.accept_task(task["task_id"], task):
            print(f"任务 {task['task_id']} 已接受")
            
            # 模拟任务执行
            await asyncio.sleep(2)
            
            # 完成任务
            result = {"status": "success", "accuracy": 0.95}
            node.complete_task(task["task_id"], result)
            print(f"任务 {task['task_id']} 已完成")
        
        # 获取节点信息
        node_info = node.get_node_info()
        print(f"\n节点信息:")
        print(f"  节点ID: {node_info['node_id']}")
        print(f"  状态: {node_info['status']}")
        print(f"  GPU内存: {sum(gpu['memory_gb'] for gpu in node_info['gpu_info'])} GB")
        print(f"  信誉分: {node_info['reputation_score']:.1f}")
        print(f"  任务完成数: {node_info['metrics']['tasks_completed']}")
    
    # 获取节点统计
    stats = node_manager.get_node_statistics()
    print(f"\n节点统计:")
    print(f"  总节点数: {stats['total_nodes']}")
    print(f"  状态分布: {stats['status_distribution']}")
    print(f"  总GPU内存: {stats['total_gpu_memory_gb']:.1f} GB")
    print(f"  平均信誉分: {stats['average_reputation_score']:.1f}")
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_node_manager())
