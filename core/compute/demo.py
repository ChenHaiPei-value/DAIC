"""
GPU分布式去中心化计算演示

展示如何使用DAIC的GPU分布式计算系统。
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleGPUInfo:
    """简化的GPU信息类"""
    def __init__(self, gpu_id: str, model: str, memory_gb: float):
        self.gpu_id = gpu_id
        self.model = model
        self.memory_gb = memory_gb
    
    def to_dict(self) -> Dict:
        return {
            "gpu_id": self.gpu_id,
            "model": self.model,
            "memory_gb": self.memory_gb,
        }


class SimpleComputeNode:
    """简化的计算节点"""
    def __init__(self, node_id: str, gpu_info: List[SimpleGPUInfo]):
        self.node_id = node_id
        self.gpu_info = gpu_info
        self.status = "online"
        self.current_tasks = set()
        self.reputation_score = 100.0
        logger.info(f"创建计算节点: {node_id}")
    
    def accept_task(self, task_id: str, task_spec: Dict) -> bool:
        """接受任务"""
        if self.status != "online":
            return False
        
        # 检查GPU内存
        required_memory = task_spec.get("gpu_memory_gb", 0)
        available_memory = sum(gpu.memory_gb for gpu in self.gpu_info)
        
        if required_memory > available_memory:
            return False
        
        self.current_tasks.add(task_id)
        logger.info(f"节点 {self.node_id} 接受任务 {task_id}")
        return True
    
    def complete_task(self, task_id: str, result: Dict):
        """完成任务"""
        if task_id in self.current_tasks:
            self.current_tasks.remove(task_id)
            logger.info(f"节点 {self.node_id} 完成任务 {task_id}")
    
    def get_info(self) -> Dict:
        """获取节点信息"""
        return {
            "node_id": self.node_id,
            "status": self.status,
            "gpu_info": [gpu.to_dict() for gpu in self.gpu_info],
            "current_tasks": list(self.current_tasks),
            "reputation_score": self.reputation_score,
        }


class SimpleNodeManager:
    """简化的节点管理器"""
    def __init__(self):
        self.nodes = {}
        logger.info("节点管理器初始化")
    
    def register_node(self, node: SimpleComputeNode):
        """注册节点"""
        self.nodes[node.node_id] = node
        logger.info(f"注册节点: {node.node_id}")
    
    def get_available_nodes(self, requirements: Dict) -> List[SimpleComputeNode]:
        """获取可用节点"""
        available = []
        
        for node in self.nodes.values():
            if node.status != "online":
                continue
            
            # 检查GPU内存
            required_memory = requirements.get("gpu_memory_gb", 0)
            available_memory = sum(gpu.memory_gb for gpu in node.gpu_info)
            
            if required_memory <= available_memory:
                available.append(node)
        
        # 按信誉分排序
        available.sort(key=lambda n: n.reputation_score, reverse=True)
        return available


class SimpleTaskScheduler:
    """简化的任务调度器"""
    def __init__(self, node_manager: SimpleNodeManager):
        self.node_manager = node_manager
        self.tasks = {}
        logger.info("任务调度器初始化")
    
    def submit_task(self, task_spec: Dict) -> str:
        """提交任务"""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        self.tasks[task_id] = {
            "spec": task_spec,
            "status": "pending",
            "created_time": datetime.now().isoformat(),
        }
        
        logger.info(f"提交任务: {task_id} - {task_spec.get('model_name', 'unknown')}")
        
        # 异步调度任务
        asyncio.create_task(self._schedule_task(task_id))
        
        return task_id
    
    async def _schedule_task(self, task_id: str):
        """调度任务"""
        task = self.tasks[task_id]
        task_spec = task["spec"]
        
        logger.info(f"开始调度任务: {task_id}")
        
        # 获取可用节点
        requirements = {
            "gpu_memory_gb": task_spec.get("gpu_memory_gb", 8.0),
        }
        
        available_nodes = self.node_manager.get_available_nodes(requirements)
        
        if not available_nodes:
            logger.warning(f"没有可用节点执行任务 {task_id}")
            task["status"] = "failed"
            task["error"] = "没有可用节点"
            return
        
        # 选择最佳节点
        best_node = available_nodes[0]
        
        # 分配任务
        if best_node.accept_task(task_id, task_spec):
            task["status"] = "running"
            task["assigned_node"] = best_node.node_id
            task["assigned_time"] = datetime.now().isoformat()
            
            logger.info(f"任务 {task_id} 分配到节点 {best_node.node_id}")
            
            # 模拟任务执行
            await self._execute_task(task_id, best_node)
        else:
            task["status"] = "failed"
            task["error"] = "节点无法接受任务"
            logger.error(f"任务 {task_id} 分配失败")
    
    async def _execute_task(self, task_id: str, node: SimpleComputeNode):
        """执行任务"""
        task = self.tasks[task_id]
        task_spec = task["spec"]
        
        # 模拟任务执行时间
        estimated_hours = task_spec.get("estimated_time_hours", 1.0)
        execution_seconds = min(estimated_hours * 0.1, 5)  # 加速演示
        
        logger.info(f"任务 {task_id} 开始执行，预计 {execution_seconds} 秒")
        
        await asyncio.sleep(execution_seconds)
        
        # 模拟任务完成
        result = {
            "task_id": task_id,
            "model_name": task_spec.get("model_name"),
            "completion_time": datetime.now().isoformat(),
            "execution_time_seconds": execution_seconds,
            "accuracy": 0.95,  # 模拟准确率
            "loss": 0.05,      # 模拟损失
        }
        
        node.complete_task(task_id, result)
        
        task["status"] = "completed"
        task["result"] = result
        task["completed_time"] = datetime.now().isoformat()
        
        logger.info(f"任务 {task_id} 完成")


class RewardSystem:
    """简化的奖励系统"""
    def __init__(self):
        self.rewards = {}
        logger.info("奖励系统初始化")
    
    def calculate_reward(self, node_id: str, task_spec: Dict, execution_time: float) -> float:
        """计算奖励"""
        base_reward = task_spec.get("reward_tokens", 100.0)
        
        # 根据执行时间调整奖励
        estimated_hours = task_spec.get("estimated_time_hours", 1.0)
        time_factor = estimated_hours / max(execution_time / 3600, 0.1)
        
        # 根据GPU性能调整奖励
        gpu_memory = task_spec.get("gpu_memory_gb", 8.0)
        memory_factor = gpu_memory / 8.0
        
        reward = base_reward * time_factor * memory_factor
        
        # 记录奖励
        if node_id not in self.rewards:
            self.rewards[node_id] = []
        
        reward_record = {
            "task_id": task_spec.get("task_id", "unknown"),
            "reward": reward,
            "time": datetime.now().isoformat(),
        }
        
        self.rewards[node_id].append(reward_record)
        
        logger.info(f"节点 {node_id} 获得奖励: {reward:.2f} tokens")
        
        return reward
    
    def get_total_rewards(self, node_id: str) -> float:
        """获取总奖励"""
        if node_id not in self.rewards:
            return 0.0
        
        return sum(record["reward"] for record in self.rewards[node_id])


async def demo_scenario_1():
    """演示场景1：单个AI训练任务"""
    print("\n" + "="*60)
    print("演示场景1：单个AI训练任务")
    print("="*60)
    
    # 创建节点管理器
    node_manager = SimpleNodeManager()
    
    # 创建3个计算节点
    nodes = [
        SimpleComputeNode("node_001", [SimpleGPUInfo("gpu1", "RTX 4090", 24.0)]),
        SimpleComputeNode("node_002", [SimpleGPUInfo("gpu1", "RTX 3090", 24.0)]),
        SimpleComputeNode("node_003", [SimpleGPUInfo("gpu1", "RTX 3080", 10.0)]),
    ]
    
    for node in nodes:
        node_manager.register_node(node)
    
    # 创建任务调度器
    scheduler = SimpleTaskScheduler(node_manager)
    
    # 创建奖励系统
    reward_system = RewardSystem()
    
    # 提交AI训练任务
    task_spec = {
        "task_type": "ai_training",
        "model_name": "llama-7b",
        "gpu_memory_gb": 16.0,
        "estimated_time_hours": 24.0,
        "reward_tokens": 1000.0,
    }
    
    task_id = scheduler.submit_task(task_spec)
    
    print(f"提交任务: {task_id}")
    print(f"任务规格: {task_spec}")
    
    # 等待任务完成
    while scheduler.tasks[task_id]["status"] not in ["completed", "failed"]:
        await asyncio.sleep(1)
    
    task_result = scheduler.tasks[task_id]
    print(f"\n任务结果:")
    print(f"  状态: {task_result['status']}")
    print(f"  分配节点: {task_result.get('assigned_node', 'N/A')}")
    
    if task_result["status"] == "completed":
        result = task_result["result"]
        print(f"  完成时间: {result['completion_time']}")
        print(f"  执行时间: {result['execution_time_seconds']:.2f} 秒")
        print(f"  准确率: {result['accuracy']:.4f}")
        
        # 计算奖励
        assigned_node = task_result.get('assigned_node')
        if assigned_node:
            reward = reward_system.calculate_reward(
                assigned_node, 
                task_spec, 
                result['execution_time_seconds']
            )
            print(f"  节点奖励: {reward:.2f} tokens")
    
    return scheduler, reward_system


async def demo_scenario_2():
    """演示场景2：多个并发任务"""
    print("\n" + "="*60)
    print("演示场景2：多个并发任务")
    print("="*60)
    
    # 创建节点管理器
    node_manager = SimpleNodeManager()
    
    # 创建5个计算节点
    nodes = []
    for i in range(5):
        gpu_memory = 8.0 + i * 4.0  # 8GB到24GB
        node = SimpleComputeNode(
            f"node_{i+1:03d}",
            [SimpleGPUInfo(f"gpu1", f"RTX {3000 + i*100}", gpu_memory)]
        )
        nodes.append(node)
        node_manager.register_node(node)
    
    # 创建任务调度器
    scheduler = SimpleTaskScheduler(node_manager)
    
    # 创建奖励系统
    reward_system = RewardSystem()
    
    # 提交多个任务
    tasks = [
        {
            "task_type": "ai_training",
            "model_name": "bert-base",
            "gpu_memory_gb": 4.0,
            "estimated_time_hours": 12.0,
            "reward_tokens": 500.0,
        },
        {
            "task_type": "ai_inference",
            "model_name": "llama-7b",
            "gpu_memory_gb": 16.0,
            "estimated_time_hours": 2.0,
            "reward_tokens": 200.0,
        },
        {
            "task_type": "data_processing",
            "model_name": "data-clean",
            "gpu_memory_gb": 8.0,
            "estimated_time_hours": 6.0,
            "reward_tokens": 300.0,
        },
    ]
    
    task_ids = []
    for task_spec in tasks:
        task_id = scheduler.submit_task(task_spec)
        task_ids.append(task_id)
        print(f"提交任务 {task_id}: {task_spec['model_name']}")
    
    # 等待所有任务完成
    while True:
        completed = all(
            scheduler.tasks[task_id]["status"] in ["completed", "failed"]
            for task_id in task_ids
        )
        
        if completed:
            break
        
        # 显示进度
        print("\n任务进度:")
        for task_id in task_ids:
            task = scheduler.tasks[task_id]
            print(f"  {task_id}: {task['status']} - {task.get('assigned_node', '等待分配')}")
        
        await asyncio.sleep(2)
    
    # 显示结果
    print("\n所有任务完成!")
    print("\n任务结果汇总:")
    
    total_rewards = 0
    for task_id in task_ids:
        task = scheduler.tasks[task_id]
        print(f"\n{task_id}:")
        print(f"  模型: {task['spec'].get('model_name')}")
        print(f"  状态: {task['status']}")
        
        if task['status'] == 'completed':
            result = task['result']
            print(f"  执行时间: {result['execution_time_seconds']:.2f}秒")
            
            # 计算奖励
            assigned_node = task.get('assigned_node')
            if assigned_node:
                reward = reward_system.calculate_reward(
                    assigned_node,
                    task['spec'],
                    result['execution_time_seconds']
                )
                total_rewards += reward
                print(f"  奖励: {reward:.2f} tokens")
    
    print(f"\n总奖励分配: {total_rewards:.2f} tokens")
    
    return scheduler, reward_system


async def demo_scenario_3():
    """演示场景3：节点网络统计"""
    print("\n" + "="*60)
    print("演示场景3：节点网络统计")
    print("="*60)
    
    # 创建大规模节点网络
    node_manager = SimpleNodeManager()
    
    # 创建20个不同配置的节点
    gpu_configs = [
        ("RTX 4090", 24.0),
        ("RTX 3090", 24.0),
        ("RTX 3080", 10.0),
        ("RTX 4070", 12.0),
        ("RTX 4060", 8.0),
        ("A100", 40.0),
        ("A6000", 48.0),
        ("V100", 32.0),
    ]
    
    for i in range(20):
        gpu_model, gpu_memory = gpu_configs[i % len(gpu_configs)]
        node = SimpleComputeNode(
            f"node_{i+1:03d}",
            [SimpleGPUInfo(f"gpu1", gpu_model, gpu_memory)]
        )
        node_manager.register_node(node)
    
    # 统计节点网络
    print("节点网络统计:")
    print(f"  总节点数: {len(node_manager.nodes)}")
    
    # 按GPU类型统计
    gpu_stats = {}
    total_gpu_memory = 0
    
    for node in node_manager.nodes.values():
        for gpu in node.gpu_info:
            gpu_type = gpu.model
            if gpu_type not in gpu_stats:
                gpu_stats[gpu_type] = {"count": 0, "total_memory": 0}
            
            gpu_stats[gpu_type]["count"] += 1
            gpu_stats[gpu_type]["total_memory"] += gpu.memory_gb
            total_gpu_memory += gpu.memory_gb
    
    print(f"  总GPU内存: {total_gpu_memory:.1f} GB")
    print("\n  GPU类型分布:")
    for gpu_type, stats in gpu_stats.items():
        print(f"    {gpu_type}: {stats['count']}个节点, {stats['total_memory']:.1f}GB")
    
    # 模拟任务负载
    scheduler = SimpleTaskScheduler(node_manager)
    
    # 提交一些任务
    tasks = []
    for i in range(10):
        task_spec = {
            "task_type": "ai_training",
            "model_name": f"model-{i}",
            "gpu_memory_gb": 4.0 + (i % 3) * 4.0,
            "estimated_time_hours": 1.0 + (i % 5),
            "reward_tokens": 100.0 * (i + 1),
        }
        
        task_id = scheduler.submit_task(task_spec)
        tasks.append(task_id)
    
    print(f"\n  提交了 {len(tasks)} 个任务")
    
    # 等待一段时间
    await asyncio.sleep(3)
    
    # 统计任务分配
    node_task_count = {}
    for task_id