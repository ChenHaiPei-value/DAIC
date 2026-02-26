"""
增强版节点管理模块

基于现有node_manager.py进行增强，添加更多功能和改进。
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
import hashlib
import json
import random

from .security import SecurityManager
from .monitoring import MetricsCollector

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """节点状态枚举（增强版）"""
    OFFLINE = "offline"          # 离线
    REGISTERING = "registering"  # 注册中
    ONLINE = "online"            # 在线
    BUSY = "busy"               # 忙碌
    MAINTENANCE = "maintenance"  # 维护中
    SUSPENDED = "suspended"      # 暂停
    DEGRADED = "degraded"        # 性能降级
    OVERLOADED = "overloaded"    # 过载


class NodeType(Enum):
    """节点类型枚举"""
    HIGH_PERFORMANCE = "high_performance"  # 高性能节点
    EDGE_NODE = "edge_node"                # 边缘节点
    MOBILE_NODE = "mobile_node"            # 移动节点
    CLOUD_NODE = "cloud_node"              # 云节点


class GPUType(Enum):
    """GPU类型枚举（增强版）"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    APPLE = "apple"
    QUALCOMM = "qualcomm"
    OTHER = "other"


@dataclass
class EnhancedGPUInfo:
    """增强版GPU硬件信息"""
    gpu_id: str
    type: GPUType
    model: str
    memory_gb: float
    cuda_cores: Optional[int] = None
    tensor_cores: Optional[int] = None
    rt_cores: Optional[int] = None
    bandwidth_gbps: Optional[float] = None
    clock_speed_mhz: Optional[float] = None
    power_limit_w: Optional[float] = None
    temperature_limit_c: Optional[float] = None
    supported_frameworks: List[str] = field(default_factory=lambda: ["pytorch", "tensorflow"])
    
    def calculate_performance_score(self) -> float:
        """计算GPU性能评分"""
        score = 0.0
        
        # 基础分：内存大小
        score += self.memory_gb * 10
        
        # CUDA核心加分
        if self.cuda_cores:
            score += self.cuda_cores * 0.1
        
        # Tensor核心加分
        if self.tensor_cores:
            score += self.tensor_cores * 0.5
        
        # RT核心加分
        if self.rt_cores:
            score += self.rt_cores * 0.3
        
        # 带宽加分
        if self.bandwidth_gbps:
            score += self.bandwidth_gbps * 2
        
        return score
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "gpu_id": self.gpu_id,
            "type": self.type.value,
            "model": self.model,
            "memory_gb": self.memory_gb,
            "cuda_cores": self.cuda_cores,
            "tensor_cores": self.tensor_cores,
            "rt_cores": self.rt_cores,
            "bandwidth_gbps": self.bandwidth_gbps,
            "clock_speed_mhz": self.clock_speed_mhz,
            "power_limit_w": self.power_limit_w,
            "temperature_limit_c": self.temperature_limit_c,
            "supported_frameworks": self.supported_frameworks,
            "performance_score": self.calculate_performance_score(),
        }


@dataclass
class EnhancedNetworkInfo:
    """增强版网络信息"""
    ip_address: str
    port: int
    bandwidth_mbps: float
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    public_key: Optional[str] = None
    certificate: Optional[str] = None
    nat_type: Optional[str] = None  # 全锥形、受限锥形、端口受限锥形、对称
    
    def calculate_network_score(self) -> float:
        """计算网络质量评分"""
        score = 100.0
        
        # 带宽加分
        score += min(self.bandwidth_mbps / 10, 50)  # 每10Mbps加1分，最多50分
        
        # 延迟扣分
        if self.latency_ms:
            if self.latency_ms > 100:
                score -= 30
            elif self.latency_ms > 50:
                score -= 15
            elif self.latency_ms > 20:
                score -= 5
        
        # 抖动扣分
        if self.jitter_ms and self.jitter_ms > 10:
            score -= 10
        
        # 丢包扣分
        if self.packet_loss_percent and self.packet_loss_percent > 1:
            score -= 20
        
        # NAT类型影响
        if self.nat_type == "symmetric":
            score -= 20  # 对称NAT连接性较差
        
        return max(score, 0)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "ip_address": self.ip_address,
            "port": self.port,
            "bandwidth_mbps": self.bandwidth_mbps,
            "latency_ms": self.latency_ms,
            "jitter_ms": self.jitter_ms,
            "packet_loss_percent": self.packet_loss_percent,
            "public_key": self.public_key,
            "certificate": self.certificate,
            "nat_type": self.nat_type,
            "network_score": self.calculate_network_score(),
        }


@dataclass
class EnhancedNodeMetrics:
    """增强版节点性能指标"""
    uptime_hours: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_task_duration_seconds: float = 0.0
    gpu_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0
    network_throughput_mbps: float = 0.0
    power_consumption_w: float = 0.0
    temperature_c: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # 新增指标
    task_success_rate: float = 100.0
    avg_response_time_ms: float = 0.0
    energy_efficiency: float = 0.0  # 性能/功耗比
    reliability_score: float = 100.0
    
    def update_metrics(self, gpu_util: float, memory_util: float, power_w: float, temp_c: float):
        """更新指标"""
        self.gpu_utilization_percent = gpu_util
        self.memory_utilization_percent = memory_util
        self.power_consumption_w = power_w
        self.temperature_c = temp_c
        self.last_updated = datetime.now()
        
        # 计算任务成功率
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.task_success_rate = (self.tasks_completed / total_tasks) * 100
        
        # 计算能源效率（每瓦性能）
        if power_w > 0:
            self.energy_efficiency = (gpu_util * memory_util) / power_w
        
        # 更新可靠性评分
        self._update_reliability_score()
    
    def _update_reliability_score(self):
        """更新可靠性评分"""
        score = 100.0
        
        # 任务失败扣分
        if self.tasks_failed > 0:
            failure_rate = self.tasks_failed / max(self.tasks_completed + self.tasks_failed, 1)
            score -= failure_rate * 50
        
        # 高温扣分
        if self.temperature_c > 80:
            score -= 20
        elif self.temperature_c > 70:
            score -= 10
        
        # 高功耗扣分
        if self.power_consumption_w > 300:
            score -= 15
        
        self.reliability_score = max(score, 0)
    
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
            "power_consumption_w": self.power_consumption_w,
            "temperature_c": self.temperature_c,
            "task_success_rate": self.task_success_rate,
            "avg_response_time_ms": self.avg_response_time_ms,
            "energy_efficiency": self.energy_efficiency,
            "reliability_score": self.reliability_score,
            "last_updated": self.last_updated.isoformat(),
        }


class EnhancedComputeNode:
    """增强版计算节点"""
    
    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        gpu_info: List[EnhancedGPUInfo],
        network_info: EnhancedNetworkInfo,
        storage_capacity_gb: float = 100.0,
        max_concurrent_tasks: int = 1,
        location: Optional[Dict] = None,
    ):
        """
        初始化增强版计算节点
        
        Args:
            node_id: 节点唯一标识
            node_type: 节点类型
            gpu_info: GPU硬件信息列表
            network_info: 网络信息
            storage_capacity_gb: 存储容量(GB)
            max_concurrent_tasks: 最大并发任务数
            location: 地理位置信息
        """
        self.node_id = node_id
        self.node_type = node_type
        self.gpu_info = gpu_info
        self.network_info = network_info
        self.storage_capacity_gb = storage_capacity_gb
        self.max_concurrent_tasks = max_concurrent_tasks
        self.location = location or {}
        
        # 状态信息
        self.status = NodeStatus.REGISTERING
        self.registration_time = datetime.now()
        self.last_heartbeat = datetime.now()
        self.last_maintenance = datetime.now()
        
        # 性能指标
        self.metrics = EnhancedNodeMetrics()
        
        # 安全组件
        self.security_manager = SecurityManager()
        
        # 监控组件
        self.metrics_collector = MetricsCollector(node_id)
        
        # 任务队列
        self.current_tasks: Set[str] = set()
        self.task_history: List[Dict] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        
        # 信誉系统
        self.reputation_score = 100.0  # 初始信誉分100
        self.reputation_history: List[Tuple[datetime, float]] = []
        self.contribution_score = 0.0  # 贡献度评分
        
        # 健康度评分
        self.health_score = 100.0
        
        # 节点标签
        self.tags: Set[str] = set()
        
        logger.info(f"增强版计算节点 {node_id} ({node_type.value}) 初始化完成")
    
    def calculate_node_score(self) -> float:
        """计算节点综合评分"""
        # GPU性能评分
        gpu_score = sum(gpu.calculate_performance_score() for gpu in self.gpu_info)
        
        # 网络质量评分
        network_score = self.network_info.calculate_network_score()
        
        # 信誉评分
        reputation_factor = self.reputation_score / 100.0
        
        # 健康度因子
        health_factor = self.health_score / 100.0
        
        # 节点类型权重
        type_weights = {
            NodeType.HIGH_PERFORMANCE: 1.5,
            NodeType.CLOUD_NODE: 1.2,
            NodeType.EDGE_NODE: 1.0,
            NodeType.MOBILE_NODE: 0.8,
        }
        type_weight = type_weights.get(self.node_type, 1.0)
        
        # 综合评分
        total_score = (
            gpu_score * 0.4 +
            network_score * 0.3 +
            self.reputation_score * 0.2 +
            self.health_score * 0.1
        ) * type_weight * reputation_factor * health_factor
        
        return total_score
    
    async def register_to_network(self, network_address: str, bootstrap_nodes: List[str] = None) -> bool:
        """
        注册到计算网络（增强版）
        
        Args:
            network_address: 网络地址
            bootstrap_nodes: 引导节点列表
            
        Returns:
            注册是否成功
        """
        try:
            # 生成增强版节点证书
            certificate = self.security_manager.generate_enhanced_certificate(
                node_id=self.node_id,
                node_type=self.node_type.value,
                public_key=self.network_info.public_key,
                gpu_info=[gpu.to_dict() for gpu in self.gpu_info],
            )
            
            # 更新网络信息
            self.network_info.certificate = certificate
            
            # 构建注册数据
            registration_data = {
                "node_id": self.node_id,
                "node_type": self.node_type.value,
                "gpu_info": [gpu.to_dict() for gpu in self.gpu_info],
                "network_info": self.network_info.to_dict(),
                "storage_capacity_gb": self.storage_capacity_gb,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "location": self.location,
                "certificate": certificate,
                "node_score": self.calculate_node_score(),
                "timestamp": datetime.now().isoformat(),
            }
            
            # 签名注册数据
            signature = self.security_manager.sign_data(
                json.dumps(registration_data, sort_keys=True)
            )
            
            # TODO: 实际发送注册请求到网络，包括引导节点
            logger.info(f"节点 {self.node_id} 注册到网络 {network_address}")
            logger.info(f"引导节点: {bootstrap_nodes}")
            
            # 更新状态
            self.status = NodeStatus.ONLINE
            self.metrics_collector.record_event("node_registered_enhanced")
            
            # 启动增强版服务
            await self.start_enhanced_serving(bootstrap_nodes)
            
            return True
            
        except Exception as e:
            logger.error(f"节点注册失败: {e}")
            self.status = NodeStatus.OFFLINE
            return False
    
    async def start_enhanced_serving(self, bootstrap_nodes: List[str] = None):
        """启动增强版服务"""
        if self.status != NodeStatus.ONLINE:
            logger.warning(f"节点 {self.node_id} 状态为 {self.status.value}，无法开始服务")
            return
        
        logger.info(f"节点 {self.node_id} 启动增强版服务")
        
        # 启动多个后台任务
        tasks = [
            asyncio.create_task(self._enhanced_heartbeat_task()),
            asyncio.create_task(self._enhanced_monitoring_task()),
            asyncio.create_task(self._task_processing_loop()),
            asyncio.create_task(self._health_check_loop()),
        ]
        
        # 如果有引导节点，启动节点发现
        if bootstrap_nodes:
            tasks.append(asyncio.create_task(self._node_discovery_task(bootstrap_nodes)))
        
        # 记录事件
        self.metrics_collector.record_event("node_started_enhanced_serving")
        
        return tasks
    
    async def _enhanced_heartbeat_task(self):
        """增强版心跳任务"""
        heartbeat_count = 0
        
        while self.status in [NodeStatus.ONLINE, NodeStatus.BUSY, NodeStatus.DEGRADED]:
            try:
                # 构建增强版心跳数据
                heartbeat_data = {
                    "node_id": self.node_id,
                    "status": self.status.value,
                    "timestamp": datetime.now().isoformat(),
                    "metrics": self.metrics.to_dict(),
                    "current_tasks": list(self.current_tasks),
                    "node_score": self.calculate_node_score(),
                    "health_score": self.health_score,
                    "reputation_score": self.reputation_score,
                    "sequence": heartbeat_count,
                }
                
                # TODO: 实际发送心跳到网络
                # 这里可以添加P2P广播或发送到特定节点
                
                # 更新最后心跳时间
                self.last_heartbeat = datetime.now()
                heartbeat_count += 1
                
                # 记录心跳
                self.metrics_collector.record_heartbeat(heartbeat_data)
                
                # 动态调整心跳间隔
                heartbeat_interval = self._calculate_heartbeat_interval()
                await asyncio.sleep(heartbeat_interval)
                
            except Exception as e:
                logger.error(f"心跳任务异常: {e}")
                await asyncio.sleep(5)
    
    def _calculate_heartbeat_interval(self) -> float:
        """动态计算心跳间隔"""
        base_interval = 30.0  # 基础30秒
        
        # 根据节点状态调整
        if self.status == NodeStatus.BUSY:
            base_interval = 60.0  # 忙碌时60秒
        elif self.status == NodeStatus.OVERLOADED:
            base_interval = 90.0  # 过载时90秒
        elif self.status == NodeStatus.DEGRADED:
            base_interval = 45.0  # 降级时45秒
        
        # 根据网络质量调整
        network_score = self.network_info.calculate_network_score()
        if network_score < 50:
            base_interval *= 1.5  # 网络差时延长间隔
        
        # 根据健康度调整
        if self.health_score < 70:
            base_interval *= 1.2
        
        return max(base_interval, 15.0)  # 最小15秒
    
    async def _enhanced_monitoring_task(self):
        """增强版监控任务"""
        while self.status in [NodeStatus.ONLINE, NodeStatus.BUSY, NodeStatus.DEGRADED]:
            try:
                # 收集增强版指标
                gpu_util = await self._get_enhanced_gpu_utilization()
                memory_util = await self._get_memory_utilization()
                power_w = await self._get_power_consumption()
                temp_c = await self._get_temperature()
                
                # 更新指标
                self.metrics.update_metrics(gpu_util, memory_util, power_w, temp_c)
                
                # 更新运行时间
                uptime = (datetime.now() - self.registration_time).total_seconds() / 3600
                self.metrics.uptime_hours = uptime
                
                # 记录监控数据
                self.metrics_collector.record_metrics({
                    "gpu_utilization": gpu_util,
                    "memory_utilization": memory_util,
                    "power_consumption": power_w,
                    "temperature": temp_c,
                    "uptime_hours": uptime,
                    "node_score": self.calculate_node_score(),
                })
                
                # 检查并更新节点状态
                await self._update_node_status()
                
                # 等待下一次监控
                await asyncio.sleep(15)  # 15秒一次监控
                
            except Exception as e:
                logger.error(f"监控任务异常: {e}")
                await asyncio.sleep(10)
    
    async def _get_enhanced_gpu_utilization(self) -> float:
        """获取增强版GPU利用率"""
        # TODO: 实际获取GPU利用率，支持多GPU
        # 这里模拟返回一个值
        import random
        
        # 模拟多GPU的平均利用率
        if len(self.gpu_info) > 1:
            utilizations = [random.uniform(0.0, 100.0) for _ in range(len(self.gpu_info))]
            return sum(utilizations) / len(utilizations)
        else:
            return random.uniform(0.0, 100.0)
    
    async def _get_power_consumption(self) -> float:
        """获取功耗"""
        # TODO: 实际获取功耗
        import random
        
        # 根据GPU类型模拟功耗
        total_power = 0.0
        for gpu in self.gpu_info:
            if gpu.type == GPUType.NVIDIA:
                if "4090" in gpu.model:
                    total_power += random.uniform(300.0, 450.0)
                elif "3090" in gpu.model:
                    total_power += random.uniform(250.0, 350.0)
                else:
                    total_power += random.uniform(100.0, 250.0)
            else:
                total_power += random.uniform(50.0, 200.0)
        
        return total_power
    
    async def _get_temperature(self) -> float:
        """获取温度"""
        # TODO: 实际获取温度
        import random
        
        # 模拟温度，考虑负载
        base_temp = 40.0
        load_factor = self.metrics.gpu_utilization_percent / 100.0
        temp_increase = load_factor * 30.0  # 满载时增加30度
        
        return base_temp + temp_increase + random.uniform(-5.0, 5.0)
    
    async def _update_node_status(self):
        """更新节点状态"""
        old_status = self.status
        
        # 检查并发任务数
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            self.status = NodeStatus.BUSY
        elif len(self.current_tasks) == 0:
            self.status = NodeStatus.ONLINE
        
        # 检查温度
        if self.metrics.temperature_c > 85:
            self.status = NodeStatus.DEGRADED
            logger.warning(f"节点 {self.node_id} 温度过高: {self.metrics.temperature_c}°C")
        
        # 检查健康度
        if self.health_score < 60:
            self.status = NodeStatus.DEGRADED
        
        # 检查负载
        if self.metrics.gpu_utilization_percent > 90 and len(self.current_tasks) > 0:
            self.status = NodeStatus.OVERLOADED
        
        # 如果状态变化，记录事件
        if old_status != self.status:
            logger.info(f"节点 {self.node_id} 状态变化: {old_status.value} -> {self.status.value}")
            self.metrics_collector.record_event("node_status_changed", {
                "old_status": old_status.value,
                "new_status": self.status.value,
                "reason": "automatic_update",
            })
    
    async def _task_processing_loop(self):
        """任务处理循环"""
        while self.status in [NodeStatus.ONLINE, NodeStatus.BUSY, NodeStatus.DEGRADED]:
            try:
                # 从队列获取任务
                task_data = await asyncio.wait_for(self.task_queue.get(), timeout=60.0)
                
                task_id = task_data.get("task_id")
                task_spec = task_data.get("spec")
                
                if not task_id or not task_spec:
                    logger.warning(f"无效的任务数据: {task_data}")
                    continue
                
                # 接受任务
                if self.accept_task(task_id, task_spec):
                    # 执行任务
                    await self._execute_enhanced_task(task_id, task_spec)
                else:
                    logger.warning(f"节点 {self.node_id} 无法接受任务 {task_id}")
                
            except asyncio.TimeoutError:
                # 队列为空，继续等待
                continue
            except Exception as e:
                logger.error(f"任务处理循环异常: {e}")
                await asyncio.sleep(5)
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.status != NodeStatus.OFFLINE:
            try:
                # 执行健康检查
                health_ok = await self._perform_health_check()
                
                if health_ok:
                    # 健康度恢复
                    self.health_score = min(100.0, self.health_score + 5.0)
                else:
                    # 健康度下降
                    self.health_score = max(0.0, self.health_score - 10.0)
                    logger.warning(f"节点 {self.node_id} 健康检查失败，健康度: {self.health_score}")
                
                # 如果需要维护
                if self.health_score < 40:
                    self.status = NodeStatus.MAINTENANCE
                    logger.error(f"节点 {self.node_id} 健康度过低，进入维护模式")
                
                # 等待下一次健康检查
                await asyncio.sleep(300)  # 5分钟一次
                
            except Exception as e:
                logger.error(f"健康检查循环异常: {e}")
                await asyncio.sleep(60)
    
    async def _node_discovery_task(self, bootstrap_nodes: List[str]):
        """节点发现任务"""
        logger.info(f"启动节点发现，引导节点: {bootstrap_nodes}")
        
        discovered_nodes = set()
        
        while self.status in [NodeStatus.ONLINE, NodeStatus.BUSY]:
            try:
                # TODO: 实现实际的节点发现逻辑
                # 这里模拟发现新节点
                
                # 记录发现的节点
                if discovered_nodes:
                    logger.info(f"已发现 {len(discovered_nodes)} 个节点")
                
                # 等待下一次发现
                await asyncio.sleep(180)  # 3分钟一次
                
            except Exception as e:
                logger.error(f"节点发现任务异常: {e}")
                await asyncio.sleep(30)
    
    async def _perform_health_check(self) -> bool:
        """执行健康检查"""
        try:
            # 检查GPU
            gpu_ok = await self._check_gpu_health()
            
            # 检查内存
            memory_ok = await self._check_memory_health()
            
            # 检查网络
            network_ok = await self._check_network_health()
            
            # 检查存储
            storage_ok = await self._check_storage_health()
            
            return gpu_ok and memory_ok and network_ok and storage_ok
            
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
            return False
    
    async def _check_gpu_health(self) -> bool:
        """检查GPU健康状态"""
        # TODO: 实际检查GPU健康状态
        import random
        return random.random() > 0.1  # 90%通过率
    
    async def _check_memory_health(self) -> bool:
        """检查内存健康状态"""
        # TODO: 实际检查内存健康状态
        import random
        return random.random() > 0.05  # 95%通过率
    
    async def _check_network_health(self) -> bool:
        """检查网络健康状态"""
        # TODO: 实际检查网络健康状态
        import random
        return random.random() > 0.2  # 80%通过率
    
    async def _check_storage_health(self) -> bool:
        """检查存储健康状态"""
        # TODO: 实际检查存储健康状态
        import random
        return random.random() > 0.15  # 85%通过率
    
    def accept_task(self, task_id: str, task_spec: Dict) -> bool:
        """
        接受计算任务（增强版）
        
        Args:
            task_id: 任务ID
            task_spec: 任务规格
            
        Returns:
            是否接受任务
        """
        if self.status not in [NodeStatus.ONLINE, NodeStatus.BUSY, NodeStatus.DEGRADED]:
            logger.warning(f"节点 {self.node_id} 状态为 {self.status.value}，无法接受任务")
            return False
        
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            logger.warning(f"节点 {self.node_id} 已达到最大并发任务数")
            return False
        
        # 检查任务资源需求
        if not self._check_enhanced_task_resources(task_spec):
            logger.warning(f"节点 {self.node_id} 资源不足，无法接受任务")
            return False
        
        # 检查任务兼容性
        if not self._check_task_compatibility(task_spec):
            logger.warning(f"节点 {self.node_id} 不兼容任务要求")
            return False
        
        # 接受任务
        self.current_tasks.add(task_id)
        
        # 记录任务历史
        self.task_history.append({
            "task_id": task_id,
            "accept_time": datetime.now().isoformat(),
            "task_spec": task_spec,
            "node_status": self.status.value,
            "node_score": self.calculate_node_score(),
        })
        
        # 更新状态
        if len(self.current_tasks) >= self.max_concurrent_tasks * 0.8:  # 达到80%负载
            self.status = NodeStatus.BUSY
        
        logger.info(f"节点 {self.node_id} 接受任务 {task_id}")
        self.metrics_collector.record_event("task_accepted_enhanced", {
            "task_id": task_id,
            "task_type": task_spec.get("task_type", "unknown"),
            "node_score": self.calculate_node_score(),
        })
        
        return True
    
    def _check_enhanced_task_resources(self, task_spec: Dict) -> bool:
        """检查增强版任务资源需求"""
        required_gpu_memory = task_spec.get("gpu_memory_gb", 0)
        required_storage = task_spec.get("storage_gb", 0)
        required_bandwidth = task_spec.get("network_bandwidth_mbps", 0)
        
        # 检查GPU内存
        available_gpu_memory = sum(gpu.memory_gb for gpu in self.gpu_info)
        if required_gpu_memory > available_gpu_memory:
            return False
        
        # 检查存储空间
        if required_storage > self.storage_capacity_gb:
            return False
        
        # 检查网络带宽
        if required_bandwidth > self.network_info.bandwidth_mbps * 0.8:  # 不超过80%带宽
            return False
        
        # 检查GPU类型兼容性
        required_gpu_type = task_spec.get("gpu_type")
        if required_gpu_type:
            supported = any(gpu.type.value == required_gpu_type for gpu in self.gpu_info)
            if not supported:
                return False
        
        # 检查框架兼容性
        required_frameworks = task_spec.get("required_frameworks", [])
        if required_frameworks:
            for framework in required_frameworks:
                supported = any(framework in gpu.supported_frameworks for gpu in self.gpu_info)
                if not supported:
                    return False
        
        return True
    
    def _check_task_compatibility(self, task_spec: Dict) -> bool:
        """检查任务兼容性"""
        # 检查隐私级别
        privacy_level = task_spec.get("privacy_level", "low")
        if privacy_level == "maximum" and self.node_type == NodeType.MOBILE_NODE:
            return False  # 移动节点不支持最高隐私级别
        
        # 检查地理位置要求
        required_location = task_spec.get("required_location")
        if required_location and self.location:
            # 简单的地理位置检查
            country_match = required_location.get("country") == self.location.get("country")
            if required_location.get("country") and not country_match:
                return False
        
        # 检查延迟要求
        max_latency = task_spec.get("max_latency_ms")
        if max_latency and self.network_info.latency_ms:
            if self.network_info.latency_ms > max_latency:
                return False
        
        return True
    
    async def _execute_enhanced_task(self, task_id: str, task_spec: Dict):
        """执行增强版任务"""
        try:
            logger.info(f"节点 {self.node_id} 开始执行任务 {task_id}")
            
            # 记录开始时间
            start_time = datetime.now()
            
            # 模拟任务执行
            estimated_hours = task_spec.get("estimated_time_hours", 1.0)
            execution_seconds = min(estimated_hours * 0.1, 10)  # 加速演示
            
            # 根据任务类型执行不同的逻辑
            task_type = task_spec.get("task_type", "ai_training")
            
            if task_type == "federated_learning":
                result = await self._execute_federated_learning(task_spec, execution_seconds)
            elif task_type == "ai_training":
                result = await self._execute_ai_training(task_spec, execution_seconds)
            elif task_type == "ai_inference":
                result = await self._execute_ai_inference(task_spec, execution_seconds)
            else:
                result = await self._execute_general_task(task_spec, execution_seconds)
            
            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 完成任务
            self.complete_task(task_id, result)
            
            logger.info(f"节点 {self.node_id} 完成任务 {task_id}，耗时 {execution_time:.2f} 秒")
            
        except Exception as e:
            logger.error(f"任务执行失败 {task_id}: {e}")
            self.fail_task(task_id, str(e))
    
    async def _execute_federated_learning(self, task_spec: Dict, execution_seconds: float):
        """执行联邦学习任务"""
        await asyncio.sleep(execution_seconds)
        
        # 模拟联邦学习结果
        return {
            "task_type": "federated_learning",
            "model_name": task_spec.get("model_name", "unknown"),
            "rounds_completed": task_spec.get("federation", {}).get("rounds", 10),
            "accuracy": 0.92 + random.uniform(-0.05, 0.05),
            "privacy_level": task_spec.get("privacy_level", "medium"),
            "differential_privacy": {
                "epsilon": task_spec.get("privacy", {}).get("differential_privacy", {}).get("epsilon", 0.1),
                "delta": task_spec.get("privacy", {}).get("differential_privacy", {}).get("delta", 1e-5),
            },
        }
    
    async def _execute_ai_training(self, task_spec: Dict, execution_seconds: float):
        """执行AI训练任务"""
        await asyncio.sleep(execution_seconds)
        
        # 模拟AI训练结果
        return {
            "task_type": "ai_training",
            "model_name": task_spec.get("model_name", "unknown"),
            "epochs_completed": task_spec.get("epochs", 10),
            "accuracy": 0.88 + random.uniform(-0.08, 0.08),
            "loss": 0.15 + random.uniform(-0.05, 0.05),
            "training_time_seconds": execution_seconds,
            "gpu_utilization": self.metrics.gpu_utilization_percent,
        }
    
    async def _execute_ai_inference(self, task_spec: Dict, execution_seconds: float):
        """执行AI推理任务"""
        await asyncio.sleep(execution_seconds)
        
        # 模拟AI推理结果
        return {
            "task_type": "ai_inference",
            "model_name": task_spec.get("model_name", "unknown"),
            "inference_count": task_spec.get("batch_size", 1),
            "avg_latency_ms": 50 + random.uniform(-20, 20),
            "throughput_rps": 100 + random.uniform(-30, 30),
            "accuracy": 0.95 + random.uniform(-0.03, 0.03),
        }
    
    async def _execute_general_task(self, task_spec: Dict, execution_seconds: float):
        """执行通用任务"""
        await asyncio.sleep(execution_seconds)
        
        # 模拟通用任务结果
        return {
            "task_type": task_spec.get("task_type", "general"),
            "status": "completed",
            "execution_time_seconds": execution_seconds,
            "result_data": {"message": "任务执行成功"},
        }
    
    def complete_task(self, task_id: str, result: Dict) -> bool:
        """
        完成任务（增强版）
        
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
                task["completion_status"] = "success"
                break
        
        # 更新性能指标
        self.metrics.tasks_completed += 1
        
        # 更新信誉评分
        self._update_reputation_score(True, result)
        
        # 更新贡献度
        self._update_contribution_score(result)
        
        # 更新状态
        if len(self.current_tasks) == 0:
            self.status = NodeStatus.ONLINE
        elif len(self.current_tasks) < self.max_concurrent_tasks * 0.5:
            self.status = NodeStatus.ONLINE
        
        logger.info(f"节点 {self.node_id} 完成任务 {task_id}")
        self.metrics_collector.record_event("task_completed_enhanced", {
            "task_id": task_id,
            "task_type": result.get("task_type", "unknown"),
            "execution_time": result.get("execution_time_seconds", 0),
        })
        
        return True
    
    def fail_task(self, task_id: str, error_message: str):
        """
        任务失败（增强版）
        
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
                task["completion_status"] = "failed"
                break
        
        # 更新性能指标
        self.metrics.tasks_failed += 1
        
        # 更新信誉评分
        self._update_reputation_score(False, {"error": error_message})
        
        # 更新健康度
        self.health_score = max(0.0, self.health_score - 5.0)
        
        # 更新状态
        if len(self.current_tasks) == 0:
            self.status = NodeStatus.ONLINE
        
        logger.error(f"节点 {self.node_id} 任务 {task_id} 失败: {error_message}")
        self.metrics_collector.record_event("task_failed_enhanced", {
            "task_id": task_id,
            "error": error_message,
            "health_score": self.health_score,
        })
    
    def _update_reputation_score(self, success: bool, result: Dict):
        """更新信誉评分（增强版）"""
        if success:
            # 任务成功，信誉分增加
            base_increase = 2.0
            
            # 根据任务质量调整
            accuracy = result.get("accuracy", 0.5)
            quality_factor = accuracy * 2.0  # 0-2倍
            
            # 根据执行效率调整
            expected_time = result.get("expected_time_seconds", 3600)
            actual_time = result.get("execution_time_seconds", 3600)
            if actual_time > 0:
                efficiency_factor = expected_time / actual_time
                efficiency_factor = min(efficiency_factor, 2.0)  # 最多2倍
            else:
                efficiency_factor = 1.0
            
            increase = base_increase * quality_factor * efficiency_factor
            
            # 连续成功有额外加成
            recent_successes = sum(1 for t in self.task_history[-20:] 
                                 if t.get("completion_status") == "success")
            if recent_successes > 15:
                increase *= 1.5  # 连续成功加成
            
            self.reputation_score = min(200.0, self.reputation_score + increase)
        else:
            # 任务失败，信誉分减少
            base_decrease = 10.0
            
            # 根据错误严重性调整
            error = result.get("error", "")
            if "timeout" in error.lower():
                base_decrease *= 0.5  # 超时惩罚较轻
            elif "resource" in error.lower():
                base_decrease *= 0.8  # 资源不足惩罚较轻
            elif "security" in error.lower():
                base_decrease *= 2.0  # 安全错误惩罚较重
            
            # 连续失败有额外惩罚
            recent_failures = sum(1 for t in self.task_history[-10:] 
                                if t.get("completion_status") == "failed")
            if recent_failures > 3:
                base_decrease *= 2.0
            
            self.reputation_score = max(0.0, self.reputation_score - base_decrease)
        
        # 记录信誉历史
        self.reputation_history.append((datetime.now(), self.reputation_score))
        
        # 如果信誉分过低，暂停节点
        if self.reputation_score < 20.0:
            self.status = NodeStatus.SUSPENDED
            logger.warning(f"节点 {self.node_id} 信誉分过低({self.reputation_score})，已暂停")
    
    def _update_contribution_score(self, result: Dict):
        """更新贡献度评分"""
        # 基础贡献
        base_contribution = 10.0
        
        # 根据任务类型调整
        task_type = result.get("task_type", "general")
        if task_type == "federated_learning":
            base_contribution *= 1.5  # 联邦学习贡献更高
        elif task_type == "ai_training":
            base_contribution *= 1.2  # AI训练贡献较高
        
        # 根据任务复杂度调整
        complexity = result.get("complexity", 1.0)
        base_contribution *= complexity
        
        # 根据执行质量调整
        accuracy = result.get("accuracy", 0.5)
        base_contribution *= accuracy
        
        self.contribution_score += base_contribution
        
        logger.debug(f"节点 {self.node_id} 贡献度增加: {base_contribution:.2f}, 总贡献: {self.contribution_score:.2f}")
    
    def get_enhanced_node_info(self) -> Dict:
        """获取增强版节点信息"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "status": self.status.value,
            "gpu_info": [gpu.to_dict() for gpu in self.gpu_info],
            "network_info": self.network_info.to_dict(),
            "storage_capacity_gb": self.storage_capacity_gb,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "location": self.location,
            "current_tasks": list(self.current_tasks),
            "metrics": self.metrics.to_dict(),
            "reputation_score": self.reputation_score,
            "contribution_score": self.contribution_score,
            "health_score": self.health_score,
            "node_score": self.calculate_node_score(),
            "registration_time": self.registration_time.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "last_maintenance": self.last_maintenance.isoformat(),
            "tags": list(self.tags),
        }
    
    def add_tag(self, tag: str):
        """添加节点标签"""
        self.tags.add(tag)
        logger.info(f"节点 {self.node_id} 添加标签: {tag}")
    
    def remove_tag(self, tag: str):
        """移除节点标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            logger.info(f"节点 {self.node_id} 移除标签: {tag}")
    
    def schedule_maintenance(self, maintenance_time: datetime = None):
        """安排维护"""
        if not maintenance_time:
            maintenance_time = datetime.now() + timedelta(hours=1)
        
        self.last_maintenance = maintenance_time
        self.status = NodeStatus.MAINTENANCE
        
        logger.info(f"节点 {self.node_id} 安排维护: {maintenance_time.isoformat()}")
    
    async def _get_memory_utilization(self) -> float:
        """获取内存利用率（占位方法）"""
        # TODO: 实际获取内存利用率
        import random
        return random.uniform(0.0, 100.0)


class EnhancedNodeManager:
    """增强版节点管理器"""
    
    def __init__(self):
        self.nodes: Dict[str, EnhancedComputeNode] = {}
        self.node_registry: Dict[str, Dict] = {}  # 节点注册表
        self.network_topology: Dict = {}
        
        logger.info("增强版节点管理器初始化完成")
    
    def register_node(self, node: EnhancedComputeNode):
        """注册节点"""
        self.nodes[node.node_id] = node
        self.node_registry[node.node_id] = node.get_enhanced_node_info()
        
        logger.info(f"注册增强版节点: {node.node_id} ({node.node_type.value})")
        
        # 更新网络拓扑
        self._update_network_topology()
    
    def unregister_node(self, node_id: str):
        """注销节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            del self.node_registry[node_id]
            logger.info(f"注销节点: {node_id}")
            
            # 更新网络拓扑
            self._update_network_topology()
    
    def get_node(self, node_id: str) -> Optional[EnhancedComputeNode]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_available_nodes(self, requirements: Dict) -> List[EnhancedComputeNode]:
        """获取可用节点（增强版）"""
        available = []
        
        for node in self.nodes.values():
            # 检查节点状态
            if node.status not in [NodeStatus.ONLINE, NodeStatus.BUSY, NodeStatus.DEGRADED]:
                continue
            
            # 检查节点类型要求
            required_node_type = requirements.get("node_type")
            if required_node_type and node.node_type.value != required_node_type:
                continue
            
            # 检查资源需求
            if not node._check_enhanced_task_resources(requirements):
                continue
            
            # 检查兼容性
            if not node._check_task_compatibility(requirements):
                continue
            
            # 检查信誉要求
            min_reputation = requirements.get("min_reputation_score", 0)
            if node.reputation_score < min_reputation:
                continue
            
            # 检查健康度要求
            min_health = requirements.get("min_health_score", 0)
            if node.health_score < min_health:
                continue
            
            available.append(node)
        
        # 按节点评分排序
        available.sort(key=lambda n: n.calculate_node_score(), reverse=True)
        
        return available
    
    def get_node_statistics(self) -> Dict:
        """获取节点统计信息"""
        total_nodes = len(self.nodes)
        
        # 按状态统计
        status_stats = {}
        for status in NodeStatus:
            status_stats[status.value] = 0
        
        # 按类型统计
        type_stats = {}
        for node_type in NodeType:
            type_stats[node_type.value] = 0
        
        # 计算统计信息
        total_gpu_memory = 0
        total_reputation = 0
        total_health = 0
        
        for node in self.nodes.values():
            status_stats[node.status.value] += 1
            type_stats[node.node_type.value] += 1
            
            # GPU内存
            total_gpu_memory += sum(gpu.memory_gb for gpu in node.gpu_info)
            
            # 信誉分
            total_reputation += node.reputation_score
            
            # 健康度
            total_health += node.health_score
        
        # 计算平均值
        avg_reputation = total_reputation / total_nodes if total_nodes > 0 else 0
        avg_health = total_health / total_nodes if total_nodes > 0 else 0
        
        return {
            "total_nodes": total_nodes,
            "status_distribution": status_stats,
            "type_distribution": type_stats,
            "total_gpu_memory_gb": total_gpu_memory,
            "average_reputation_score": avg_reputation,
            "average_health_score": avg_health,
            "network_topology": self.network_topology,
        }
    
    def _update_network_topology(self):
        """更新网络拓扑"""
        # 简单的拓扑信息
        self.network_topology = {
            "total_nodes": len(self.nodes),
            "node_ids": list(self.nodes.keys()),
            "last_updated": datetime.now().isoformat(),
        }
    
    def find_nodes_by_tags(self, tags: List[str]) -> List[EnhancedComputeNode]:
        """根据标签查找节点"""
        matching_nodes = []
        
        for node in self.nodes.values():
            if all(tag in node.tags for tag in tags):
                matching_nodes.append(node)
        
        return matching_nodes
    
    def get_high_performance_nodes(self, min_score: float = 150.0) -> List[EnhancedComputeNode]:
        """获取高性能节点"""
        high_perf_nodes = []
        
        for node in self.nodes.values():
            if node.calculate_node_score() >= min_score:
                high_perf_nodes.append(node)
        
        # 按评分排序
        high_perf_nodes.sort(key=lambda n: n.calculate_node_score(), reverse=True)
        
        return high_perf_nodes
    
    def schedule_global_maintenance(self, percentage: float = 0.1):
        """安排全局维护（随机选择一定比例的节点）"""
        import random
        
        node_ids = list(self.nodes.keys())
        num_to_maintain = max(1, int(len(node_ids) * percentage))
        nodes_to_maintain = random.sample(node_ids, num_to_maintain)
        
        for node_id in nodes_to_maintain:
            node = self.nodes.get(node_id)
            if node and node.status in [NodeStatus.ONLINE, NodeStatus.BUSY]:
                node.schedule_maintenance()
        
        logger.info(f"安排了 {len(nodes_to_maintain)} 个节点的维护")
        return nodes_to_maintain


# 演示函数
async def demo_enhanced_node_manager():
    """演示增强版节点管理器"""
    print("="*70)
    print("增强版节点管理器演示")
    print("="*70)
    
    # 创建节点管理器
    node_manager = EnhancedNodeManager()
    
    # 创建不同类型的节点
    nodes = []
    
    # 高性能节点
    high_perf_gpu = EnhancedGPUInfo(
        gpu_id="gpu1",
        type=GPUType.NVIDIA,
        model="RTX 4090",
        memory_gb=24.0,
        cuda_cores=16384,
        tensor_cores=512,
        rt_cores=128,
        bandwidth_gbps=1008,
        power_limit_w=450,
    )
    
    high_perf_network = EnhancedNetworkInfo(
        ip_address="192.168.1.100",
        port=8080,
        bandwidth_mbps=1000,
        latency_ms=5.0,
        jitter_ms=1.0,
        packet_loss_percent=0.1,
        nat_type="full_cone",
    )
    
    high_perf_node = EnhancedComputeNode(
        node_id="node_hp_001",
        node_type=NodeType.HIGH_PERFORMANCE,
        gpu_info=[high_perf_gpu],
        network_info=high_perf_network,
        storage_capacity_gb=500.0,
        max_concurrent_tasks=4,
        location={"country": "CN", "region": "Beijing", "city": "Beijing"},
    )
    
    # 边缘节点
    edge_gpu = EnhancedGPUInfo(
        gpu_id="gpu2",
        type=GPUType.NVIDIA,
        model="RTX 3060",
        memory_gb=12.0,
        cuda_cores=3584,
        tensor_cores=112,
        bandwidth_gbps=360,
        power_limit_w=170,
    )
    
    edge_network = EnhancedNetworkInfo(
        ip_address="192.168.1.101",
        port=8081,
        bandwidth_mbps=500,
        latency_ms=15.0,
        jitter_ms=3.0,
        packet_loss_percent=0.5,
        nat_type="restricted_cone",
    )
    
    edge_node = EnhancedComputeNode(
        node_id="node_edge_001",
        node_type=NodeType.EDGE_NODE,
        gpu_info=[edge_gpu],
        network_info=edge_network,
        storage_capacity_gb=250.0,
        max_concurrent_tasks=2,
        location={"country": "CN", "region": "Shanghai", "city": "Shanghai"},
    )
    
    # 移动节点
    mobile_gpu = EnhancedGPUInfo(
        gpu_id="gpu3",
        type=GPUType.QUALCOMM,
        model="Adreno 740",
        memory_gb=8.0,
        bandwidth_gbps=68,
        power_limit_w=10,
    )
    
    mobile_network = EnhancedNetworkInfo(
        ip_address="192.168.1.102",
        port=8082,
        bandwidth_mbps=100,
        latency_ms=30.0,
        jitter_ms=10.0,
        packet_loss_percent=1.0,
        nat_type="symmetric",
    )
    
    mobile_node = EnhancedComputeNode(
        node_id="node_mobile_001",
        node_type=NodeType.MOBILE_NODE,
        gpu_info=[mobile_gpu],
        network_info=mobile_network,
        storage_capacity_gb=100.0,
        max_concurrent_tasks=1,
        location={"country": "CN", "region": "Guangdong", "city": "Shenzhen"},
    )
    
    # 云节点
    cloud_gpu1 = EnhancedGPUInfo(
        gpu_id="gpu4",
        type=GPUType.NVIDIA,
        model="A100",
        memory_gb=40.0,
        cuda_cores=6912,
        tensor_cores=432,
        bandwidth_gbps=1555,
        power_limit_w=300,
    )
    
    cloud_gpu2 = EnhancedGPUInfo(
        gpu_id="gpu5",
        type=GPUType.NVIDIA,
        model="A100",
        memory_gb=40.0,
        cuda_cores=6912,
        tensor_cores=432,
        bandwidth_gbps=1555,
        power_limit_w=300,
    )
    
    cloud_network = EnhancedNetworkInfo(
        ip_address="10.0.0.100",
        port=8083,
        bandwidth_mbps=2000,
        latency_ms=2.0,
        jitter_ms=0.5,
        packet_loss_percent=0.05,
        nat_type="full_cone",
    )
    
    cloud_node = EnhancedComputeNode(
        node_id="node_cloud_001",
        node_type=NodeType.CLOUD_NODE,
        gpu_info=[cloud_gpu1, cloud_gpu2],
        network_info=cloud_network,
        storage_capacity_gb=1000.0,
        max_concurrent_tasks=8,
        location={"country": "US", "region": "California", "city": "San Francisco"},
    )
    
    # 注册所有节点
    nodes = [high_perf_node, edge_node, mobile_node, cloud_node]
    for node in nodes:
        node_manager.register_node(node)
    
    print(f"已注册 {len(nodes)} 个节点:")
    for node in nodes:
        print(f"  - {node.node_id} ({node.node_type.value})")
    
    # 模拟节点注册到网络
    print("\n模拟节点注册到网络...")
    network_address = "daic-network.example.com"
    bootstrap_nodes = ["bootstrap1.daic.com", "bootstrap2.daic.com"]
    
    registration_tasks = []
    for node in nodes:
        task = asyncio.create_task(node.register_to_network(network_address, bootstrap_nodes))
        registration_tasks.append(task)
    
    # 等待注册完成
    registration_results = await asyncio.gather(*registration_tasks, return_exceptions=True)
    
    successful_registrations = sum(1 for result in registration_results if result is True)
    print(f"成功注册 {successful_registrations}/{len(nodes)} 个节点")
    
    # 获取节点统计信息
    print("\n节点统计信息:")
    stats = node_manager.get_node_statistics()
    print(f"总节点数: {stats['total_nodes']}")
    print(f"状态分布: {stats['status_distribution']}")
    print(f"类型分布: {stats['type_distribution']}")
    print(f"总GPU内存: {stats['total_gpu_memory_gb']:.1f} GB")
    print(f"平均信誉分: {stats['average_reputation_score']:.1f}")
    print(f"平均健康度: {stats['average_health_score']:.1f}")
    
    # 演示任务调度
    print("\n演示任务调度...")
    
    # 创建不同类型的任务
    tasks = [
        {
            "task_id": "task_ai_train_001",
            "task_type": "ai_training",
            "model_name": "resnet50",
            "gpu_memory_gb": 8.0,
            "storage_gb": 50.0,
            "network_bandwidth_mbps": 100,
            "epochs": 100,
            "estimated_time_hours": 2.0,
            "privacy_level": "medium",
        },
        {
            "task_id": "task_fed_learn_001",
            "task_type": "federated_learning",
            "model_name": "bert-base",
            "gpu_memory_gb": 12.0,
            "storage_gb": 100.0,
            "network_bandwidth_mbps": 50,
            "federation": {"rounds": 20, "clients": 10},
            "privacy_level": "high",
            "privacy": {
                "differential_privacy": {"epsilon": 0.1, "delta": 1e-5},
                "secure_aggregation": True,
            },
            "estimated_time_hours": 1.5,
        },
        {
            "task_id": "task_inference_001",
            "task_type": "ai_inference",
            "model_name": "stable-diffusion",
            "gpu_memory_gb": 16.0,
            "storage_gb": 30.0,
            "network_bandwidth_mbps": 200,
            "batch_size": 4,
            "estimated_time_hours": 0.5,
            "max_latency_ms": 100,
        },
    ]
    
    # 为每个任务寻找合适的节点
    for task in tasks:
        print(f"\n为任务 {task['task_id']} 寻找节点...")
        
        # 构建任务需求
        requirements = {
            "gpu_memory_gb": task["gpu_memory_gb"],
            "storage_gb": task["storage_gb"],
            "network_bandwidth_mbps": task["network_bandwidth_mbps"],
            "task_type": task["task_type"],
            "privacy_level": task.get("privacy_level", "low"),
        }
        
        # 获取可用节点
        available_nodes = node_manager.get_available_nodes(requirements)
        
        if available_nodes:
            # 选择最佳节点
            best_node = available_nodes[0]
            print(f"  选择节点: {best_node.node_id} (评分: {best_node.calculate_node_score():.1f})")
            
            # 接受任务
            if best_node.accept_task(task["task_id"], task):
                print(f"  任务 {task['task_id']} 已接受")
                
                # 将任务添加到队列
                await best_node.task_queue.put({
                    "task_id": task["task_id"],
                    "spec": task,
                })
            else:
                print(f"  任务 {task['task_id']} 被拒绝")
        else:
            print(f"  没有可用节点满足任务需求")
    
    # 等待任务执行
    print("\n等待任务执行...")
    await asyncio.sleep(3)
    
    # 显示节点状态更新
    print("\n任务执行后的节点状态:")
    for node in nodes:
        node_info = node.get_enhanced_node_info()
        print(f"\n节点 {node.node_id}:")
        print(f"  状态: {node_info['status']}")
        print(f"  当前任务: {len(node_info['current_tasks'])} 个")
        print(f"  信誉分: {node_info['reputation_score']:.1f}")
        print(f"  健康度: {node_info['health_score']:.1f}")
        print(f"  节点评分: {node_info['node_score']:.1f}")
        
        # 显示任务历史
        if node.task_history:
            print(f"  最近任务:")
            for task in node.task_history[-2:]:  # 显示最近2个任务
                status = task.get("completion_status", "unknown")
                task_id = task.get("task_id", "unknown")
                print(f"    - {task_id}: {status}")
    
    # 演示高级功能
    print("\n" + "="*70)
    print("高级功能演示")
    print("="*70)
    
    # 1. 根据标签查找节点
    print("\n1. 标签系统演示:")
    
    # 为节点添加标签
    high_perf_node.add_tag("high-performance")
    high_perf_node.add_tag("ai-training")
    edge_node.add_tag("edge-computing")
    cloud_node.add_tag("cloud")
    cloud_node.add_tag("multi-gpu")
    
    # 查找具有特定标签的节点
    ai_training_nodes = node_manager.find_nodes_by_tags(["ai-training"])
    print(f"  具有 'ai-training' 标签的节点: {[n.node_id for n in ai_training_nodes]}")
    
    multi_gpu_nodes = node_manager.find_nodes_by_tags(["multi-gpu"])
    print(f"  具有 'multi-gpu' 标签的节点: {[n.node_id for n in multi_gpu_nodes]}")
    
    # 2. 获取高性能节点
    print("\n2. 高性能节点筛选:")
    high_perf_nodes = node_manager.get_high_performance_nodes(min_score=100.0)
    print(f"  评分 > 100 的高性能节点:")
    for node in high_perf_nodes:
        print(f"    - {node.node_id}: 评分 {node.calculate_node_score():.1f}")
    
    # 3. 全局维护调度
    print("\n3. 全局维护调度演示:")
    nodes_to_maintain = node_manager.schedule_global_maintenance(percentage=0.25)
    print(f"  安排了 {len(nodes_to_maintain)} 个节点的维护:")
    for node_id in nodes_to_maintain:
        node = node_manager.get_node(node_id)
        if node:
            print(f"    - {node_id}: 状态 -> {node.status.value}")
    
    # 4. 节点详细信息
    print("\n4. 节点详细信息示例:")
    sample_node = high_perf_node
    node_details = sample_node.get_enhanced_node_info()
    
    print(f"  节点ID: {node_details['node_id']}")
    print(f"  类型: {node_details['node_type']}")
    print(f"  GPU信息:")
    for gpu in node_details['gpu_info']:
        print(f"    - {gpu['model']}: {gpu['memory_gb']}GB, 评分: {gpu['performance_score']:.1f}")
    
    print(f"  网络评分: {node_details['network_info']['network_score']:.1f}")
    print(f"  性能指标:")
    metrics = node_details['metrics']
    print(f"    GPU利用率: {metrics['gpu_utilization_percent']:.1f}%")
    print(f"    内存利用率: {metrics['memory_utilization_percent']:.1f}%")
    print(f"    功耗: {metrics['power_consumption_w']:.1f}W")
    print(f"    温度: {metrics['temperature_c']:.1f}°C")
    print(f"    任务成功率: {metrics['task_success_rate']:.1f}%")
    print(f"    能源效率: {metrics['energy_efficiency']:.3f}")
    
    print("\n" + "="*70)
    print("演示完成!")
    print("="*70)
    
    return node_manager


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_enhanced_node_manager())
