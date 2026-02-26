"""
监控模块

负责收集、记录和分析节点性能指标。
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import statistics

logger = logging.getLogger(__name__)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, node_id: str):
        """
        初始化指标收集器
        
        Args:
            node_id: 节点ID
        """
        self.node_id = node_id
        self.metrics_history: List[Dict] = []
        self.events_history: List[Dict] = []
        self.heartbeats_history: List[Dict] = []
        
        # 性能指标缓存
        self.performance_cache: Dict[str, Any] = {}
        
        # 告警配置
        self.alerts_config = {
            "gpu_temperature_threshold": 85.0,  # °C
            "gpu_utilization_threshold": 95.0,  # %
            "memory_utilization_threshold": 90.0,  # %
            "task_failure_rate_threshold": 20.0,  # %
            "heartbeat_timeout_seconds": 120,  # 秒
        }
        
        # 告警历史
        self.alerts_history: List[Dict] = []
        
        logger.info(f"指标收集器初始化完成: {node_id}")
    
    def record_metrics(self, metrics: Dict):
        """
        记录性能指标
        
        Args:
            metrics: 性能指标字典
        """
        timestamp = datetime.now()
        
        metric_record = {
            "timestamp": timestamp.isoformat(),
            "node_id": self.node_id,
            "metrics": metrics,
        }
        
        self.metrics_history.append(metric_record)
        
        # 保持历史记录大小
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # 更新性能缓存
        self._update_performance_cache(metrics)
        
        # 检查告警
        self._check_alerts(metrics, timestamp)
        
        logger.debug(f"记录指标: {len(self.metrics_history)} 条记录")
    
    def record_event(self, event_type: str, event_data: Optional[Dict] = None):
        """
        记录事件
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
        """
        timestamp = datetime.now()
        
        event_record = {
            "timestamp": timestamp.isoformat(),
            "node_id": self.node_id,
            "event_type": event_type,
            "event_data": event_data or {},
        }
        
        self.events_history.append(event_record)
        
        # 保持历史记录大小
        if len(self.events_history) > 500:
            self.events_history = self.events_history[-500:]
        
        logger.info(f"记录事件: {event_type}")
    
    def record_heartbeat(self, heartbeat_data: Optional[Dict] = None):
        """
        记录心跳
        
        Args:
            heartbeat_data: 心跳数据
        """
        timestamp = datetime.now()
        
        heartbeat_record = {
            "timestamp": timestamp.isoformat(),
            "node_id": self.node_id,
            "heartbeat_data": heartbeat_data or {},
        }
        
        self.heartbeats_history.append(heartbeat_record)
        
        # 保持历史记录大小
        if len(self.heartbeats_history) > 100:
            self.heartbeats_history = self.heartbeats_history[-100:]
        
        logger.debug(f"记录心跳: {len(self.heartbeats_history)} 条记录")
    
    def _update_performance_cache(self, metrics: Dict):
        """更新性能缓存"""
        # 更新GPU利用率
        if "gpu_utilization" in metrics:
            gpu_key = "gpu_utilization_stats"
            if gpu_key not in self.performance_cache:
                self.performance_cache[gpu_key] = []
            
            self.performance_cache[gpu_key].append(metrics["gpu_utilization"])
            if len(self.performance_cache[gpu_key]) > 100:
                self.performance_cache[gpu_key] = self.performance_cache[gpu_key][-100:]
        
        # 更新内存利用率
        if "memory_utilization" in metrics:
            memory_key = "memory_utilization_stats"
            if memory_key not in self.performance_cache:
                self.performance_cache[memory_key] = []
            
            self.performance_cache[memory_key].append(metrics["memory_utilization"])
            if len(self.performance_cache[memory_key]) > 100:
                self.performance_cache[memory_key] = self.performance_cache[memory_key][-100:]
    
    def _check_alerts(self, metrics: Dict, timestamp: datetime):
        """检查告警条件"""
        alerts = []
        
        # GPU温度告警
        if "temperature" in metrics:
            temp = metrics["temperature"]
            if temp > self.alerts_config["gpu_temperature_threshold"]:
                alerts.append({
                    "type": "gpu_temperature_high",
                    "severity": "warning",
                    "message": f"GPU温度过高: {temp}°C",
                    "threshold": self.alerts_config["gpu_temperature_threshold"],
                    "actual": temp,
                })
        
        # GPU利用率告警
        if "gpu_utilization" in metrics:
            utilization = metrics["gpu_utilization"]
            if utilization > self.alerts_config["gpu_utilization_threshold"]:
                alerts.append({
                    "type": "gpu_utilization_high",
                    "severity": "warning",
                    "message": f"GPU利用率过高: {utilization}%",
                    "threshold": self.alerts_config["gpu_utilization_threshold"],
                    "actual": utilization,
                })
        
        # 内存利用率告警
        if "memory_utilization" in metrics:
            memory_util = metrics["memory_utilization"]
            if memory_util > self.alerts_config["memory_utilization_threshold"]:
                alerts.append({
                    "type": "memory_utilization_high",
                    "severity": "critical",
                    "message": f"内存利用率过高: {memory_util}%",
                    "threshold": self.alerts_config["memory_utilization_threshold"],
                    "actual": memory_util,
                })
        
        # 记录告警
        for alert in alerts:
            alert_record = {
                "timestamp": timestamp.isoformat(),
                "node_id": self.node_id,
                **alert,
            }
            
            self.alerts_history.append(alert_record)
            
            # 保持告警历史大小
            if len(self.alerts_history) > 100:
                self.alerts_history = self.alerts_history[-100:]
            
            logger.warning(f"告警: {alert['message']}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict:
        """
        获取性能摘要
        
        Args:
            hours: 小时数
            
        Returns:
            性能摘要
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 过滤指定时间范围内的指标
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "node_id": self.node_id,
                "period_hours": hours,
                "metrics_count": 0,
                "message": "没有找到指定时间范围内的指标",
            }
        
        # 提取各项指标
        gpu_utilizations = []
        memory_utilizations = []
        temperatures = []
        
        for metric_record in recent_metrics:
            metrics = metric_record["metrics"]
            
            if "gpu_utilization" in metrics:
                gpu_utilizations.append(metrics["gpu_utilization"])
            
            if "memory_utilization" in metrics:
                memory_utilizations.append(metrics["memory_utilization"])
            
            if "temperature" in metrics:
                temperatures.append(metrics["temperature"])
        
        # 计算统计信息
        summary = {
            "node_id": self.node_id,
            "period_hours": hours,
            "metrics_count": len(recent_metrics),
            "gpu_utilization": self._calculate_stats(gpu_utilizations, "GPU利用率"),
            "memory_utilization": self._calculate_stats(memory_utilizations, "内存利用率"),
            "temperature": self._calculate_stats(temperatures, "温度"),
            "events_count": len([
                e for e in self.events_history
                if datetime.fromisoformat(e["timestamp"]) > cutoff_time
            ]),
            "heartbeats_count": len([
                h for h in self.heartbeats_history
                if datetime.fromisoformat(h["timestamp"]) > cutoff_time
            ]),
            "alerts_count": len([
                a for a in self.alerts_history
                if datetime.fromisoformat(a["timestamp"]) > cutoff_time
            ]),
        }
        
        return summary
    
    def _calculate_stats(self, values: List[float], name: str) -> Dict:
        """计算统计信息"""
        if not values:
            return {
                "name": name,
                "count": 0,
                "message": "没有数据",
            }
        
        try:
            return {
                "name": name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "latest": values[-1],
            }
        except Exception as e:
            logger.error(f"计算统计信息失败 {name}: {e}")
            return {
                "name": name,
                "count": len(values),
                "error": str(e),
            }
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """
        获取最近事件
        
        Args:
            limit: 限制数量
            
        Returns:
            事件列表
        """
        return self.events_history[-limit:]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """
        获取最近告警
        
        Args:
            limit: 限制数量
            
        Returns:
            告警列表
        """
        return self.alerts_history[-limit:]
    
    def get_heartbeat_status(self) -> Dict:
        """
        获取心跳状态
        
        Returns:
            心跳状态
        """
        if not self.heartbeats_history:
            return {
                "status": "unknown",
                "last_heartbeat": None,
                "message": "没有心跳记录",
            }
        
        last_heartbeat = self.heartbeats_history[-1]
        last_time = datetime.fromisoformat(last_heartbeat["timestamp"])
        time_diff = (datetime.now() - last_time).total_seconds()
        
        if time_diff > self.alerts_config["heartbeat_timeout_seconds"]:
            status = "stale"
            message = f"心跳超时: {time_diff:.1f}秒"
        elif time_diff > self.alerts_config["heartbeat_timeout_seconds"] / 2:
            status = "warning"
            message = f"心跳延迟: {time_diff:.1f}秒"
        else:
            status = "healthy"
            message = f"心跳正常: {time_diff:.1f}秒前"
        
        return {
            "status": status,
            "last_heartbeat": last_heartbeat["timestamp"],
            "time_diff_seconds": time_diff,
            "message": message,
            "heartbeat_count": len(self.heartbeats_history),
        }
    
    def get_health_score(self) -> float:
        """
        计算健康度评分
        
        Returns:
            健康度评分 (0-100)
        """
        score = 100.0
        
        # 检查心跳状态
        heartbeat_status = self.get_heartbeat_status()
        if heartbeat_status["status"] == "stale":
            score -= 30
        elif heartbeat_status["status"] == "warning":
            score -= 15
        
        # 检查最近告警
        recent_alerts = self.get_recent_alerts(limit=20)
        critical_alerts = [a for a in recent_alerts if a.get("severity") == "critical"]
        warning_alerts = [a for a in recent_alerts if a.get("severity") == "warning"]
        
        score -= len(critical_alerts) * 10
        score -= len(warning_alerts) * 5
        
        # 检查性能指标
        if self.performance_cache.get("gpu_utilization_stats"):
            avg_gpu_util = statistics.mean(self.performance_cache["gpu_utilization_stats"][-10:])
            if avg_gpu_util > 90:
                score -= 10
            elif avg_gpu_util > 80:
                score -= 5
        
        return max(0.0, min(100.0, score))
    
    def export_metrics(self, format: str = "json") -> str:
        """
        导出指标
        
        Args:
            format: 导出格式 (json, csv)
            
        Returns:
            导出的数据
        """
        if format == "json":
            export_data = {
                "node_id": self.node_id,
                "export_time": datetime.now().isoformat(),
                "metrics_count": len(self.metrics_history),
                "events_count": len(self.events_history),
                "heartbeats_count": len(self.heartbeats_history),
                "alerts_count": len(self.alerts_history),
                "performance_summary_24h": self.get_performance_summary(24),
                "recent_events": self.get_recent_events(10),
                "recent_alerts": self.get_recent_alerts(10),
                "heartbeat_status": self.get_heartbeat_status(),
                "health_score": self.get_health_score(),
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            # 简化的CSV导出
            csv_lines = ["timestamp,node_id,metric_type,value"]
            
            for metric in self.metrics_history[-100:]:  # 限制数量
                timestamp = metric["timestamp"]
                node_id = metric["node_id"]
                
                for key, value in metric["metrics"].items():
                    if isinstance(value, (int, float)):
                        csv_lines.append(f"{timestamp},{node_id},{key},{value}")
            
            return "\n".join(csv_lines)
        
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def clear_old_data(self, days: int = 7):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 清理指标历史
        self.metrics_history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        # 清理事件历史
        self.events_history = [
            e for e in self.events_history
            if datetime.fromisoformat(e["timestamp"]) > cutoff_time
        ]
        
        # 清理心跳历史
        self.heartbeats_history = [
            h for h in self.heartbeats_history
            if datetime.fromisoformat(h["timestamp"]) > cutoff_time
        ]
        
        # 清理告警历史
        self.alerts_history = [
            a for a in self.alerts_history
            if datetime.fromisoformat(a["timestamp"]) > cutoff_time
        ]
        
        logger.info(f"清理了 {days} 天前的数据")


# 演示函数
def demo_monitoring():
    """演示监控模块"""
    print("="*50)
    print("监控模块演示")
    print("="*50)
    
    # 创建指标收集器
    collector = MetricsCollector("node_demo_001")
    
    # 记录一些指标
    for i in range(10):
        metrics = {
            "gpu_utilization": 30.0 + i * 5,
            "memory_utilization": 40.0 + i * 3,
            "temperature": 50.0 + i * 2,
            "power_consumption": 200.0 + i * 10,
        }
        
        collector.record_metrics(metrics)
        
        # 记录事件
        if i % 3 == 0:
            collector.record_event("task_started", {"task_id": f"task_{i}"})
        
        # 记录心跳
        if i % 2 == 0:
            collector.record_heartbeat({"sequence": i})
    
    # 记录一个告警
    collector.record_metrics({"temperature": 90.0, "gpu_utilization": 98.0})
    
    # 获取性能摘要
    summary = collector.get_performance_summary(hours=1)
    print(f"性能摘要:")
    print(f"  指标数量: {summary['metrics_count']}")
    print(f"  事件数量: {summary['events_count']}")
    print(f"  心跳数量: {summary['heartbeats_count']}")
    print(f"  告警数量: {summary['alerts_count']}")
    
    # GPU利用率统计
    gpu_stats = summary.get("gpu_utilization", {})
    if "mean" in gpu_stats:
        print(f"  GPU利用率: 平均 {gpu_stats['mean']:.1f}%, 最新 {gpu_stats.get('latest', 0):.1f}%")
    
    # 获取心跳状态
    heartbeat_status = collector.get_heartbeat_status()
    print(f"心跳状态: {heartbeat_status['status']} - {heartbeat_status['message']}")
    
    # 获取健康度评分
    health_score = collector.get_health_score()
    print(f"健康度评分: {health_score:.1f}/100")
    
    # 获取最近事件
    recent_events = collector.get_recent_events(limit=3)
    print(f"最近事件 ({len(recent_events)} 个):")
    for event in recent_events:
        print(f"  - {event['event_type']} at {event['timestamp']}")
    
    # 获取最近告警
    recent_alerts = collector.get_recent_alerts(limit=2)
    print(f"最近告警 ({len(recent_alerts)} 个):")
    for alert in recent_alerts:
        print(f"  - {alert['type']}: {alert['message']}")
    
    # 导出指标
    json_export = collector.export_metrics("json")
    print(f"JSON导出长度: {len(json_export)} 字符")
    
    # 清理旧数据
    collector.clear_old_data(days=0)  # 清理所有数据
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)


if __name__ == "__main__":
    demo_monitoring()
