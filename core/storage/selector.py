"""
节点选择器模块

基于信誉、性能和可用性智能选择存储节点。
"""

import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NodeStatus(Enum):
    """节点状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: str
    address: str
    port: int
    storage_capacity: int  # 字节
    used_storage: int  # 字节
    bandwidth: int  # Mbps
    latency: float  # 毫秒
    uptime: float  # 正常运行时间比例
    reputation: float  # 信誉评分 0-1
    last_seen: float  # 最后活跃时间戳
    status: NodeStatus
    geographic_location: Optional[Tuple[float, float]] = None  # 经纬度
    supported_protocols: List[str] = None
    
    def __post_init__(self):
        if self.supported_protocols is None:
            self.supported_protocols = ["http", "p2p"]
    
    @property
    def available_storage(self) -> int:
        """可用存储空间"""
        return self.storage_capacity - self.used_storage
    
    @property
    def storage_utilization(self) -> float:
        """存储利用率"""
        if self.storage_capacity == 0:
            return 1.0
        return self.used_storage / self.storage_capacity
    
    @property
    def is_available(self) -> bool:
        """节点是否可用"""
        return self.status == NodeStatus.ONLINE and self.available_storage > 0
    
    @property
    def age(self) -> float:
        """节点年龄（秒）"""
        return time.time() - self.last_seen


class NodeSelector:
    """智能节点选择器"""
    
    def __init__(self, min_reputation: float = 0.5, max_latency: float = 1000.0):
        """
        初始化节点选择器
        
        Args:
            min_reputation: 最小信誉评分
            max_latency: 最大延迟（毫秒）
        """
        self.min_reputation = min_reputation
        self.max_latency = max_latency
        self.nodes: Dict[str, NodeInfo] = {}
        self.node_history: Dict[str, List[Dict]] = {}  # 节点历史记录
        
        # 权重配置
        self.weights = {
            'reputation': 0.25,
            'availability': 0.20,
            'performance': 0.20,
            'storage': 0.15,
            'geographic': 0.10,
            'freshness': 0.10
        }
    
    def add_node(self, node_info: NodeInfo) -> None:
        """
        添加节点
        
        Args:
            node_info: 节点信息
        """
        self.nodes[node_info.node_id] = node_info
        if node_info.node_id not in self.node_history:
            self.node_history[node_info.node_id] = []
        
        # 记录节点状态
        self.node_history[node_info.node_id].append({
            'timestamp': time.time(),
            'status': node_info.status.value,
            'reputation': node_info.reputation,
            'available_storage': node_info.available_storage
        })
        
        # 保持历史记录大小
        if len(self.node_history[node_info.node_id]) > 100:
            self.node_history[node_info.node_id] = self.node_history[node_info.node_id][-100:]
    
    def remove_node(self, node_id: str) -> None:
        """
        移除节点
        
        Args:
            node_id: 节点ID
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
        if node_id in self.node_history:
            del self.node_history[node_id]
    
    def update_node_status(self, node_id: str, status: NodeStatus, 
                          reputation_change: float = 0.0) -> None:
        """
        更新节点状态
        
        Args:
            node_id: 节点ID
            status: 新状态
            reputation_change: 信誉变化
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.status = status
            node.last_seen = time.time()
            
            # 更新信誉评分
            new_reputation = node.reputation + reputation_change
            node.reputation = max(0.0, min(1.0, new_reputation))
            
            # 记录更新
            self.add_node(node)  # 这会更新历史记录
    
    def select_nodes(self, count: int, requirements: Optional[Dict] = None) -> List[NodeInfo]:
        """
        选择存储节点
        
        Args:
            count: 需要选择的节点数量
            requirements: 可选的需求参数
        
        Returns:
            selected_nodes: 选中的节点列表
        """
        if requirements is None:
            requirements = {}
        
        # 1. 获取可用节点
        available_nodes = self._get_available_nodes(requirements)
        
        if len(available_nodes) < count:
            raise ValueError(
                f"需要 {count} 个节点，但只有 {len(available_nodes)} 个可用节点"
            )
        
        # 2. 计算节点评分
        node_scores = self._calculate_node_scores(available_nodes, requirements)
        
        # 3. 选择最佳节点
        selected_nodes = self._select_best_nodes(node_scores, count)
        
        # 4. 确保地理分布（如果可能）
        if requirements.get('ensure_geographic_distribution', True):
            selected_nodes = self._ensure_geographic_distribution(selected_nodes)
        
        return selected_nodes
    
    def _get_available_nodes(self, requirements: Dict) -> List[NodeInfo]:
        """
        获取符合条件的可用节点
        
        Args:
            requirements: 需求参数
        
        Returns:
            available_nodes: 可用节点列表
        """
        available_nodes = []
        
        for node in self.nodes.values():
            if not node.is_available:
                continue
            
            # 检查信誉要求
            if node.reputation < self.min_reputation:
                continue
            
            # 检查延迟要求
            if node.latency > self.max_latency:
                continue
            
            # 检查存储要求
            min_storage = requirements.get('min_storage', 0)
            if node.available_storage < min_storage:
                continue
            
            # 检查带宽要求
            min_bandwidth = requirements.get('min_bandwidth', 0)
            if node.bandwidth < min_bandwidth:
                continue
            
            # 检查协议要求
            required_protocols = requirements.get('required_protocols', [])
            if required_protocols:
                if not all(proto in node.supported_protocols for proto in required_protocols):
                    continue
            
            available_nodes.append(node)
        
        return available_nodes
    
    def _calculate_node_scores(self, nodes: List[NodeInfo], requirements: Dict) -> Dict[str, float]:
        """
        计算节点综合评分
        
        Args:
            nodes: 节点列表
            requirements: 需求参数
        
        Returns:
            scores: 节点评分字典
        """
        scores = {}
        
        for node in nodes:
            # 信誉评分
            reputation_score = node.reputation
            
            # 可用性评分（基于历史记录）
            availability_score = self._calculate_availability_score(node.node_id)
            
            # 性能评分（基于延迟和带宽）
            performance_score = self._calculate_performance_score(node)
            
            # 存储评分（基于可用存储空间）
            storage_score = self._calculate_storage_score(node)
            
            # 地理分布评分
            geographic_score = self._calculate_geographic_score(node, nodes)
            
            # 新鲜度评分（基于最后活跃时间）
            freshness_score = self._calculate_freshness_score(node)
            
            # 综合评分
            total_score = (
                reputation_score * self.weights['reputation'] +
                availability_score * self.weights['availability'] +
                performance_score * self.weights['performance'] +
                storage_score * self.weights['storage'] +
                geographic_score * self.weights['geographic'] +
                freshness_score * self.weights['freshness']
            )
            
            # 应用需求权重
            if 'prefer_low_latency' in requirements and requirements['prefer_low_latency']:
                latency_factor = 1.0 - min(node.latency / self.max_latency, 1.0)
                total_score *= (1.0 + latency_factor * 0.5)
            
            if 'prefer_high_storage' in requirements and requirements['prefer_high_storage']:
                storage_factor = node.available_storage / (1024 ** 3)  # GB
                total_score *= (1.0 + min(storage_factor / 100, 1.0) * 0.3)
            
            scores[node.node_id] = total_score
        
        return scores
    
    def _calculate_availability_score(self, node_id: str) -> float:
        """
        计算可用性评分
        
        Args:
            node_id: 节点ID
        
        Returns:
            score: 可用性评分 0-1
        """
        if node_id not in self.node_history or len(self.node_history[node_id]) < 10:
            return 0.5
        
        history = self.node_history[node_id]
        
        # 计算最近100条记录中的在线比例
        recent_history = history[-100:]
        online_count = sum(1 for record in recent_history if record['status'] == 'online')
        
        return online_count / len(recent_history)
    
    def _calculate_performance_score(self, node: NodeInfo) -> float:
        """
        计算性能评分
        
        Args:
            node: 节点信息
        
        Returns:
            score: 性能评分 0-1
        """
        # 延迟评分（延迟越低越好）
        latency_score = 1.0 - min(node.latency / self.max_latency, 1.0)
        
        # 带宽评分（带宽越高越好）
        max_bandwidth = 1000  # 假设最大带宽为1000Mbps
        bandwidth_score = min(node.bandwidth / max_bandwidth, 1.0)
        
        # 正常运行时间评分
        uptime_score = node.uptime
        
        # 综合性能评分
        performance_score = (latency_score * 0.4 + bandwidth_score * 0.3 + uptime_score * 0.3)
        
        return performance_score
    
    def _calculate_storage_score(self, node: NodeInfo) -> float:
        """
        计算存储评分
        
        Args:
            node: 节点信息
        
        Returns:
            score: 存储评分 0-1
        """
        # 可用存储空间评分（空间越多越好）
        if node.storage_capacity == 0:
            return 0.0
        
        available_ratio = node.available_storage / node.storage_capacity
        
        # 存储利用率评分（利用率适中最好，避免过满或太空）
        utilization = node.storage_utilization
        if utilization < 0.3:
            # 太空，可能不稳定
            utilization_score = 0.7
        elif utilization < 0.8:
            # 适中，最佳状态
            utilization_score = 1.0
        else:
            # 过满，可能很快不可用
            utilization_score = 0.5
        
        # 综合存储评分
        storage_score = (available_ratio * 0.6 + utilization_score * 0.4)
        
        return storage_score
    
    def _calculate_geographic_score(self, node: NodeInfo, all_nodes: List[NodeInfo]) -> float:
        """
        计算地理分布评分
        
        Args:
            node: 当前节点
            all_nodes: 所有节点列表
        
        Returns:
            score: 地理分布评分 0-1
        """
        if node.geographic_location is None:
            return 0.5
        
        # 计算与其他节点的平均距离
        distances = []
        for other_node in all_nodes:
            if (other_node.node_id != node.node_id and 
                other_node.geographic_location is not None):
                distance = self._calculate_distance(
                    node.geographic_location,
                    other_node.geographic_location
                )
                distances.append(distance)
        
        if not distances:
            return 0.5
        
        # 平均距离越大，分布越好
        avg_distance = sum(distances) / len(distances)
        
        # 归一化评分（假设最大有效距离为10000公里）
        max_distance = 10000
        geographic_score = min(avg_distance / max_distance, 1.0)
        
        return geographic_score
    
    def _calculate_freshness_score(self, node: NodeInfo) -> float:
        """
        计算新鲜度评分
        
        Args:
            node: 节点信息
        
        Returns:
            score: 新鲜度评分 0-1
        """
        # 最后活跃时间越近越好
        age = node.age
        max_age = 3600  # 1小时
        
        if age < 60:  # 1分钟内
            return 1.0
        elif age < 300:  # 5分钟内
            return 0.9
        elif age < 1800:  # 30分钟内
            return 0.7
        elif age < max_age:  # 1小时内
            return 0.5
        else:
            return 0.2
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """
        计算两个地理位置之间的距离（公里）
        
        Args:
            loc1: 位置1 (纬度, 经度)
            loc2: 位置2 (纬度, 经度)
        
        Returns:
            distance: 距离（公里）
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # 地球半径（公里）
        R = 6371.0
        
        lat1, lon1 = radians(loc1[0]), radians(loc1[1])
        lat2, lon2 = radians(loc2[0]), radians(loc2[1])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _select_best_nodes(self, node_scores: Dict[str, float], count: int) -> List[NodeInfo]:
        """
        选择最佳节点
        
        Args:
            node_scores: 节点评分字典
            count: 需要选择的节点数量
        
        Returns:
            best_nodes: 最佳节点列表
        """
        # 按评分排序
        sorted_nodes = sorted(
            node_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 选择前count个节点
        selected_node_ids = [node_id for node_id, _ in sorted_nodes[:count]]
        selected_nodes = [self.nodes[node_id] for node_id in selected_node_ids]
        
        return selected_nodes
    
    def _ensure_geographic_distribution(self, nodes: List[NodeInfo]) -> List[NodeInfo]:
        """
        确保地理分布
        
        Args:
            nodes: 节点列表
        
        Returns:
            distributed_nodes: 地理分布优化的节点列表
        """
        if len(nodes) <= 1:
            return nodes
        
        # 检查是否有地理位置信息
        nodes_with_location = [n for n in nodes if n.geographic_location is not None]
        if len(nodes_with_location) < 2:
            return nodes
        
        # 使用贪心算法选择地理分布最分散的节点
        selected_nodes = []
        remaining_nodes = nodes_with_location.copy()
        
        # 选择第一个节点（评分最高）
        selected_nodes.append(remaining_nodes.pop(0))
        
        while len(selected_nodes) < len(nodes) and remaining_nodes:
            # 计算每个剩余节点与已选节点的最小距离
            best_node = None
            best_min_distance = -1
            
            for node in remaining_nodes:
                min_distance = float('inf')
                for selected in selected_nodes:
                    distance = self._calculate_distance(
                        node.geographic_location,
                        selected.geographic_location
                    )
                    min_distance = min(min_distance, distance)
                
                if min_distance > best_min_distance:
                    best_min_distance = min_distance
                    best_node = node
            
            if best_node:
                selected_nodes.append(best_node)
                remaining_nodes.remove(best_node)
        
        # 添加没有地理位置信息的节点（如果有）
        nodes_without_location = [n for n in nodes if n.geographic_location is None]
        selected_nodes.extend(nodes_without_location[:len(nodes) - len(selected_nodes)])
        
        return selected_nodes
    
    def get_node_statistics(self) -> Dict:
        """
        获取节点统计信息
        
        Returns:
            stats: 统计信息字典
        """
        total_nodes = len(self.nodes)
        online_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.ONLINE)
        available_nodes = sum(1 for n in self.nodes.values() if n.is_available)
        
        total_storage = sum(n.storage_capacity for n in self.nodes.values())
        used_storage = sum(n.used_storage for n in self.nodes.values())
        available_storage = sum(n.available_storage for n in self.nodes.values())
        
        avg_reputation = sum(n.reputation for n in self.nodes.values()) / total_nodes if total_nodes > 0 else 0
        avg_latency = sum(n.latency for n in self.nodes.values()) / total_nodes if total_nodes > 0 else 0
        
        return {
            'total_nodes': total_nodes,
            'online_nodes': online_nodes,
            'available_nodes': available_nodes,
            'online_ratio': online_nodes / total_nodes if total_nodes > 0 else 0,
            'total_storage_gb': total_storage / (1024 ** 3),
            'used_storage_gb': used_storage / (1024 ** 3),
            'available_storage_gb': available_storage / (1024 ** 3),
            'storage_utilization': used_storage / total_storage if total_storage > 0 else 0,
            'avg_reputation': avg_reputation,
            'avg_latency_ms': avg_latency,
            'node_distribution': self._get_node_distribution()
        }
    
    def _get_node_distribution(self) -> Dict:
        """
        获取节点分布信息
        
        Returns:
            distribution: 节点分布字典
        """
        distribution = {
            'by_status': {},
            'by_reputation': {
                'excellent': 0,  # >= 0.8
                'good': 0,       # >= 0.6
                'fair': 0,       # >= 0.4
                'poor': 0        # < 0.4
            },
            'by_storage': {
                'large': 0,      # >= 1TB
                'medium': 0,     # >= 100GB
                'small': 0,      # < 100GB
                'full': 0        # >= 90% utilization
            }
        }
        
        for node in self.nodes.values():
            # 按状态统计
            status = node.status.value
            distribution['by_status'][status] = distribution['by_status'].get(status, 0) + 1
            
            # 按信誉统计
            if node.reputation >= 0.8:
                distribution['by_reputation']['excellent'] += 1
            elif node.reputation >= 0.6:
                distribution['by_reputation']['good'] += 1
            elif node.reputation >= 0.4:
                distribution['by_reputation']['fair'] += 1
            else:
                distribution['by_reputation']['poor'] += 1
            
            # 按存储统计
            storage_gb = node.storage_capacity / (1024 ** 3)
            if storage_gb >= 1024:  # 1TB
                distribution['by_storage']['large'] += 1
            elif storage_gb >= 100:  # 100GB
                distribution['by_storage']['medium'] += 1
            else:
                distribution['by_storage']['small'] += 1
            
            if node.storage_utilization >= 0.9:
                distribution['by_storage']['full'] += 1
        
        return distribution
