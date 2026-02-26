"""
任务调度模块

负责AI计算任务的调度、分解、分配和结果聚合。
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 等待中
    SCHEDULED = "scheduled"      # 已调度
    RUNNING = "running"          # 运行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"      # 已取消


class TaskType(Enum):
    """任务类型枚举"""
    AI_TRAINING = "ai_training"          # AI训练
    AI_INFERENCE = "ai_inference"        # AI推理
    DATA_PROCESSING = "data_processing"  # 数据处理
    MODEL_FINE_TUNING = "model_fine_tuning"  # 模型微调


@dataclass
class TaskSpec:
    """任务规格"""
    task_id: str
    task_type: TaskType
    model_name: str
    dataset: Optional[str] = None
    gpu_memory_gb: float = 8.0
    cpu_cores: int = 4
    ram_gb: float = 16.0
    storage_gb: float = 50.0
    estimated_time_hours: float = 1.0
    priority: int = 1  # 1-5，5为最高优先级
    reward_tokens: float = 100.0
    created_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "model_name": self.model_name,
            "dataset": self.dataset,
            "gpu_memory_gb": self.gpu_memory_gb,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "storage_gb": self.storage_gb,
            "estimated_time_hours": self.estimated_time_hours,
            "priority": self.priority,
            "reward_tokens": self.reward_tokens,
            "created_time": self.created_time.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TaskSpec":
        """从字典创建"""
        return cls(
            task_id=data["task_id"],
            task_type=TaskType(data["task_type"]),
            model_name=data["model_name"],
            dataset=data.get("dataset"),
            gpu_memory_gb=data.get("gpu_memory_gb", 8.0),
            cpu_cores=data.get("cpu_cores", 4),
            ram_gb=data.get("ram_gb", 16.0),
            storage_gb=data.get("storage_gb", 50.0),
            estimated_time_hours=data.get("estimated_time_hours", 1.0),
            priority=data.get("priority", 1),
            reward_tokens=data.get("reward_tokens", 100.0),
            created_time=datetime.fromisoformat(data.get("created_time", datetime.now().isoformat())),
        )


@dataclass
class Subtask:
    """子任务"""
    subtask_id: str
    parent_task_id: str
    node_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_time: Optional[datetime] = None
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "subtask_id": self.subtask_id,
            "parent_task_id": self.parent_task_id,
            "node_id": self.node_id,
            "status": self.status.value,
            "assigned_time": self.assigned_time.isoformat() if self.assigned_time else None,
            "started_time": self.started_time.isoformat() if self.started_time else None,
            "completed_time": self.completed_time.isoformat() if self.completed_time else None,
            "result": self.result,
            "error": self.error,
        }


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, node_manager):
        """
        初始化任务调度器
        
        Args:
            node_manager: 节点管理器实例
        """
        self.node_manager = node_manager
        self.tasks: Dict[str, TaskSpec] = {}
        self.subtasks: Dict[str, Subtask] = {}
        self.task_status: Dict[str, TaskStatus] = {}
        self.task_results: Dict[str, Dict] = {}
        
        # 调度策略
        self.scheduling_algorithm = "fair_share"  # fair_share, priority, fifo
        self.max_retries = 3
        self.retry_delay_seconds = 60
        
        logger.info("任务调度器初始化完成")
    
    def submit_task(self, task_data: Dict) -> str:
        """
        提交新任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            任务ID
        """
        # 生成任务ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # 创建任务规格
        task_spec = TaskSpec(
            task_id=task_id,
            task_type=TaskType(task_data.get("task_type", "ai_training")),
            model_name=task_data["model_name"],
            dataset=task_data.get("dataset"),
            gpu_memory_gb=task_data.get("gpu_memory_gb", 8.0),
            cpu_cores=task_data.get("cpu_cores", 4),
            ram_gb=task_data.get("ram_gb", 16.0),
            storage_gb=task_data.get("storage_gb", 50.0),
            estimated_time_hours=task_data.get("estimated_time_hours", 1.0),
            priority=task_data.get("priority", 1),
            reward_tokens=task_data.get("reward_tokens", 100.0),
        )
        
        # 保存任务
        self.tasks[task_id] = task_spec
        self.task_status[task_id] = TaskStatus.PENDING
        
        logger.info(f"提交新任务: {task_id} - {task_spec.model_name}")
        
        # 异步调度任务
        asyncio.create_task(self._schedule_task(task_id))
        
        return task_id
    
    async def _schedule_task(self, task_id: str):
        """调度任务"""
        try:
            task_spec = self.tasks[task_id]
            
            # 更新任务状态
            self.task_status[task_id] = TaskStatus.SCHEDULED
            
            # 根据任务类型选择调度策略
            if task_spec.task_type == TaskType.AI_TRAINING:
                await self._schedule_training_task(task_id)
            elif task_spec.task_type == TaskType.AI_INFERENCE:
                await self._schedule_inference_task(task_id)
            elif task_spec.task_type == TaskType.DATA_PROCESSING:
                await self._schedule_data_processing_task(task_id)
            elif task_spec.task_type == TaskType.MODEL_FINE_TUNING:
                await self._schedule_fine_tuning_task(task_id)
            else:
                logger.error(f"未知任务类型: {task_spec.task_type}")
                self.task_status[task_id] = TaskStatus.FAILED
            
        except Exception as e:
            logger.error(f"任务调度失败 {task_id}: {e}")
            self.task_status[task_id] = TaskStatus.FAILED
    
    async def _schedule_training_task(self, task_id: str):
        """调度AI训练任务"""
        task_spec = self.tasks[task_id]
        
        logger.info(f"调度AI训练任务: {task_id} - {task_spec.model_name}")
        
        # 分解任务为子任务
        subtasks = self._decompose_training_task(task_spec)
        
        # 分配子任务到节点
        for subtask in subtasks:
            await self._assign_subtask(subtask)
        
        # 等待所有子任务完成
        await self._wait_for_subtasks_completion(task_id)
        
        # 聚合结果
        await self._aggregate_training_results(task_id)
    
    def _decompose_training_task(self, task_spec: TaskSpec) -> List[Subtask]:
        """分解训练任务为子任务"""
        subtasks = []
        
        # 根据模型大小和资源需求决定分解策略
        model_size = self._estimate_model_size(task_spec.model_name)
        
        if model_size > 50:  # 大型模型，需要分布式训练
            # 数据并行
            num_data_shards = 4
            for i in range(num_data_shards):
                subtask_id = f"{task_spec.task_id}_data_{i}"
                subtask = Subtask(
                    subtask_id=subtask_id,
                    parent_task_id=task_spec.task_id,
                )
                subtasks.append(subtask)
            
            # 模型并行（如果需要）
            if model_size > 100:
                num_model_shards = 2
                for i in range(num_model_shards):
                    subtask_id = f"{task_spec.task_id}_model_{i}"
                    subtask = Subtask(
                        subtask_id=subtask_id,
                        parent_task_id=task_spec.task_id,
                    )
                    subtasks.append(subtask)
        else:
            # 小型模型，单节点训练
            subtask_id = f"{task_spec.task_id}_single"
            subtask = Subtask(
                subtask_id=subtask_id,
                parent_task_id=task_spec.task_id,
            )
            subtasks.append(subtask)
        
        # 保存子任务
        for subtask in subtasks:
            self.subtasks[subtask.subtask_id] = subtask
        
        return subtasks
    
    def _estimate_model_size(self, model_name: str) -> float:
        """估计模型大小（GB）"""
        # 简单的模型大小估计
        model_sizes = {
            "llama-7b": 14.0,
            "llama-13b": 26.0,
            "llama-70b": 140.0,
            "gpt-3": 350.0,
            "gpt-4": 1800.0,
            "bert-base": 0.4,
            "bert-large": 1.3,
            "vit-base": 0.3,
            "vit-large": 1.0,
        }
        
        return model_sizes.get(model_name.lower(), 10.0)
    
    async def _assign_subtask(self, subtask: Subtask):
        """分配子任务到节点"""
        max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                # 获取可用节点
                parent_task = self.tasks[subtask.parent_task_id]
                
                requirements = {
                    "gpu_memory_gb": parent_task.gpu_memory_gb,
                    "storage_gb": parent_task.storage_gb,
                    "priority": parent_task.priority,
                }
                
                available_nodes = self.node_manager.get_available_nodes(requirements)
                
                if not available_nodes:
                    logger.warning(f"没有可用节点分配子任务 {subtask.subtask_id}")
                    await asyncio.sleep(self.retry_delay_seconds)
                    continue
                
                # 选择最佳节点
                best_node = available_nodes[0]
                
                # 分配任务
                task_spec_dict = parent_task.to_dict()
                if best_node.accept_task(subtask.subtask_id, task_spec_dict):
                    subtask.node_id = best_node.node_id
                    subtask.status = TaskStatus.RUNNING
                    subtask.assigned_time = datetime.now()
                    
                    logger.info(f"子任务 {subtask.subtask_id} 分配到节点 {best_node.node_id}")
                    return
                
            except Exception as e:
                logger.error(f"分配子任务失败 {subtask.subtask_id}: {e}")
            
            # 重试前等待
            if attempt < max_retries - 1:
                await asyncio.sleep(self.retry_delay_seconds)
        
        # 所有重试都失败
        subtask.status = TaskStatus.FAILED
        subtask.error = "无法分配到节点"
        logger.error(f"子任务 {subtask.subtask_id} 分配失败")
    
    async def _wait_for_subtasks_completion(self, task_id: str):
        """等待所有子任务完成"""
        subtasks = [s for s in self.subtasks.values() if s.parent_task_id == task_id]
        
        while True:
            # 检查子任务状态
            completed = all(s.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                          for s in subtasks)
            
            if completed:
                break
            
            # 等待一段时间再检查
            await asyncio.sleep(10)
            
            # 检查是否有失败的任务需要重试
            for subtask in subtasks:
                if subtask.status == TaskStatus.FAILED and subtask.error != "无法分配到节点":
                    # 重试失败的任务
                    logger.info(f"重试失败子任务: {subtask.subtask_id}")
                    subtask.status = TaskStatus.PENDING
                    subtask.error = None
                    await self._assign_subtask(subtask)
    
    async def _aggregate_training_results(self, task_id: str):
        """聚合训练结果"""
        subtasks = [s for s in self.subtasks.values() if s.parent_task_id == task_id]
        
        # 检查是否有失败的任务
        failed_subtasks = [s for s in subtasks if s.status == TaskStatus.FAILED]
        
        if failed_subtasks:
            # 有任务失败，整个任务失败
            self.task_status[task_id] = TaskStatus.FAILED
            error_messages = [s.error for s in failed_subtasks if s.error]
            self.task_results[task_id] = {
                "status": "failed",
                "error": f"{len(failed_subtasks)}个子任务失败: {', '.join(error_messages)}",
                "completed_subtasks": len([s for s in subtasks if s.status == TaskStatus.COMPLETED]),
                "failed_subtasks": len(failed_subtasks),
            }
            logger.error(f"任务 {task_id} 失败: {self.task_results[task_id]['error']}")
            return
        
        # 所有子任务成功，聚合结果
        completed_subtasks = [s for s in subtasks if s.status == TaskStatus.COMPLETED]
        
        # 简单的结果聚合（实际需要根据任务类型实现）
        aggregated_result = {
            "status": "completed",
            "total_subtasks": len(subtasks),
            "completed_subtasks": len(completed_subtasks),
            "model_name": self.tasks[task_id].model_name,
            "completion_time": datetime.now().isoformat(),
            "subtask_results": [s.result for s in completed_subtasks if s.result],
        }
        
        self.task_results[task_id] = aggregated_result
        self.task_status[task_id] = TaskStatus.COMPLETED
        
        logger.info(f"任务 {task_id} 完成，聚合了 {len(completed_subtasks)} 个子任务的结果")
    
    async def _schedule_inference_task(self, task_id: str):
        """调度AI推理任务"""
        task_spec = self.tasks[task_id]
        
        logger.info(f"调度AI推理任务: {task_id} - {task_spec.model_name}")
        
        # 推理任务通常不需要分解
        subtask_id = f"{task_id}_inference"
        subtask = Subtask(
            subtask_id=subtask_id,
            parent_task_id=task_id,
        )
        
        self.subtasks[subtask_id] = subtask
        
        # 分配子任务
        await self._assign_subtask(subtask)
        
        # 等待完成
        await self._wait_for_subtasks_completion(task_id)
        
        # 处理结果
        if subtask.status == TaskStatus.COMPLETED:
            self.task_results[task_id] = subtask.result
            self.task_status[task_id] = TaskStatus.COMPLETED
        else:
            self.task_status[task_id] = TaskStatus.FAILED
            self.task_results[task_id] = {"error": subtask.error}
    
    async def _schedule_data_processing_task(self, task_id: str):
        """调度数据处理任务"""
        task_spec = self.tasks[task_id]
        
        logger.info(f"调度数据处理任务: {task_id}")
        
        # 数据并行处理
        num_shards = 8  # 将数据分为8个分片
        subtasks = []
        
        for i in range(num_shards):
            subtask_id = f"{task_id}_data_{i}"
            subtask = Subtask(
                subtask_id=subtask_id,
                parent_task_id=task_id,
            )
            subtasks.append(subtask)
            self.subtasks[subtask_id] = subtask
        
        # 分配所有子任务
        for subtask in subtasks:
            await self._assign_subtask(subtask)
        
        # 等待完成并聚合结果
        await self._wait_for_subtasks_completion(task_id)
        await self._aggregate_data_processing_results(task_id)
    
    async def _aggregate_data_processing_results(self, task_id: str):
        """聚合数据处理结果"""
        subtasks = [s for s in self.subtasks.values() if s.parent_task_id == task_id]
        
        # 检查失败的任务
        failed_subtasks = [s for s in subtasks if s.status == TaskStatus.FAILED]
        
        if failed_sub