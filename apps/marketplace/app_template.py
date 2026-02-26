"""
AI应用模板模块

提供共创AI应用平台的基础模板，AI工程师可以基于此创建大家一起用的且不属于任何人的AI应用。
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import uuid

logger = logging.getLogger(__name__)


class AIApplicationTemplate:
    """AI应用模板类"""
    
    def __init__(self, app_id: str, name: str, description: str, version: str = "1.0.0"):
        """
        初始化AI应用模板
        
        Args:
            app_id: 应用唯一标识
            name: 应用名称
            description: 应用描述
            version: 应用版本
        """
        self.app_id = app_id
        self.name = name
        self.description = description
        self.version = version
        
        # 贡献者信息
        self.contributors: List[Dict] = []
        
        # 应用配置
        self.config: Dict = {
            "compute_requirements": {
                "gpu_memory_gb": 8,
                "cpu_cores": 4,
                "memory_gb": 16,
                "storage_gb": 50
            },
            "dependencies": [],
            "environment_variables": {},
            "api_endpoints": []
        }
        
        # 部署信息
        self.deployment_info: Dict = {}
        
        # 使用统计
        self.usage_stats: Dict = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_compute_hours": 0,
            "last_run_time": None
        }
        
        # 收益信息
        self.revenue_info: Dict = {
            "total_revenue": 0,
            "revenue_distribution": {},
            "last_payout_time": None
        }
        
        logger.info(f"AI应用模板初始化: {name} ({app_id})")
    
    def add_contributor(self, contributor_address: str, share_percentage: float, role: str = "developer"):
        """
        添加贡献者
        
        Args:
            contributor_address: 贡献者地址
            share_percentage: 收益份额百分比
            role: 角色 (developer, tester, designer, etc.)
        """
        contributor = {
            "address": contributor_address,
            "share_percentage": share_percentage,
            "role": role,
            "joined_at": datetime.now().isoformat(),
            "total_contributions": 0
        }
        
        self.contributors.append(contributor)
        
        # 更新收益分配
        self._update_revenue_distribution()
        
        logger.info(f"添加贡献者: {contributor_address} ({role}, {share_percentage}%)")
    
    def _update_revenue_distribution(self):
        """更新收益分配"""
        total_shares = sum(c["share_percentage"] for c in self.contributors)
        
        if total_shares > 100:
            logger.warning(f"总份额超过100%: {total_shares}%")
            # 按比例调整
            for contributor in self.contributors:
                contributor["share_percentage"] = (contributor["share_percentage"] / total_shares) * 100
        
        # 更新收益分配信息
        self.revenue_info["revenue_distribution"] = {
            c["address"]: c["share_percentage"] for c in self.contributors
        }
    
    def add_dependency(self, dependency_name: str, version: str, source: str = "pypi"):
        """添加依赖"""
        dependency = {
            "name": dependency_name,
            "version": version,
            "source": source
        }
        
        self.config["dependencies"].append(dependency)
        logger.info(f"添加依赖: {dependency_name}=={version}")
    
    def add_api_endpoint(self, endpoint: str, method: str, description: str, parameters: List[Dict]):
        """添加API端点"""
        api_endpoint = {
            "endpoint": endpoint,
            "method": method.upper(),
            "description": description,
            "parameters": parameters,
            "requires_auth": True
        }
        
        self.config["api_endpoints"].append(api_endpoint)
        logger.info(f"添加API端点: {method} {endpoint}")
    
    def set_compute_requirements(self, gpu_memory_gb: int = 8, cpu_cores: int = 4, 
                                memory_gb: int = 16, storage_gb: int = 50):
        """设置计算需求"""
        self.config["compute_requirements"] = {
            "gpu_memory_gb": gpu_memory_gb,
            "cpu_cores": cpu_cores,
            "memory_gb": memory_gb,
            "storage_gb": storage_gb
        }
        
        logger.info(f"设置计算需求: GPU={gpu_memory_gb}GB, CPU={cpu_cores}核, 内存={memory_gb}GB, 存储={storage_gb}GB")
    
    def deploy(self, compute_nodes: List[str], storage_nodes: List[str]) -> Dict:
        """
        部署应用到分布式网络
        
        Args:
            compute_nodes: 计算节点列表
            storage_nodes: 存储节点列表
            
        Returns:
            部署结果
        """
        deployment_id = f"deploy_{hashlib.md5(f'{self.app_id}_{datetime.now().timestamp()}'.encode()).hexdigest()[:16]}"
        
        self.deployment_info = {
            "deployment_id": deployment_id,
            "compute_nodes": compute_nodes,
            "storage_nodes": storage_nodes,
            "deployed_at": datetime.now().isoformat(),
            "status": "deploying"
        }
        
        logger.info(f"开始部署应用 {self.name} 到 {len(compute_nodes)} 个计算节点和 {len(storage_nodes)} 个存储节点")
        
        # 模拟部署过程
        # 在实际项目中，这里会调用分布式部署服务
        
        self.deployment_info["status"] = "deployed"
        self.deployment_info["deployed_at"] = datetime.now().isoformat()
        
        logger.info(f"应用 {self.name} 部署完成，部署ID: {deployment_id}")
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "app_id": self.app_id,
            "compute_nodes": len(compute_nodes),
            "storage_nodes": len(storage_nodes),
            "deployment_time": datetime.now().isoformat()
        }
    
    def execute(self, input_data: Dict, user_address: str = None) -> Dict:
        """
        执行AI应用
        
        Args:
            input_data: 输入数据
            user_address: 用户地址（可选）
            
        Returns:
            执行结果
        """
        start_time = datetime.now()
        
        try:
            # 更新使用统计
            self.usage_stats["total_runs"] += 1
            self.usage_stats["last_run_time"] = datetime.now().isoformat()
            
            # 模拟AI应用执行
            # 在实际项目中，这里会调用实际的AI模型
            
            result = self._simulate_execution(input_data)
            
            # 计算使用时间（模拟）
            execution_time = (datetime.now() - start_time).total_seconds()
            compute_hours = execution_time / 3600
            
            # 更新统计
            self.usage_stats["successful_runs"] += 1
            self.usage_stats["total_compute_hours"] += compute_hours
            
            # 计算收益（模拟）
            revenue = self._calculate_revenue(compute_hours)
            self.revenue_info["total_revenue"] += revenue
            
            logger.info(f"应用 {self.name} 执行成功，用时: {execution_time:.2f}秒，收益: ${revenue:.4f}")
            
            return {
                "success": True,
                "result": result,
                "execution_time_seconds": execution_time,
                "compute_hours": compute_hours,
                "revenue_generated": revenue,
                "app_id": self.app_id,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            # 更新失败统计
            self.usage_stats["failed_runs"] += 1
            
            logger.error(f"应用 {self.name} 执行失败: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "app_id": self.app_id,
                "timestamp": start_time.isoformat()
            }
    
    def _simulate_execution(self, input_data: Dict) -> Dict:
        """模拟AI应用执行"""
        # 根据应用类型模拟不同的执行结果
        
        if "sentiment" in self.app_id.lower() or "情感" in self.name:
            # 情感分析应用
            text = input_data.get("text", "")
            sentiment_score = self._analyze_sentiment(text)
            
            return {
                "sentiment": sentiment_score["sentiment"],
                "confidence": sentiment_score["confidence"],
                "positive_score": sentiment_score["positive"],
                "negative_score": sentiment_score["negative"],
                "neutral_score": sentiment_score["neutral"]
            }
        
        elif "translation" in self.app_id.lower() or "翻译" in self.name:
            # 翻译应用
            text = input_data.get("text", "")
            source_lang = input_data.get("source_lang", "auto")
            target_lang = input_data.get("target_lang", "en")
            
            translated_text = f"[{target_lang.upper()}] {text} (translated)"
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translation_quality": 0.95
            }
        
        elif "summary" in self.app_id.lower() or "摘要" in self.name:
            # 文本摘要应用
            text = input_data.get("text", "")
            summary_length = input_data.get("summary_length", 100)
            
            summary = text[:summary_length] + "..." if len(text) > summary_length else text
            
            return {
                "original_length": len(text),
                "summary_length": len(summary),
                "summary": summary,
                "compression_ratio": len(summary) / len(text) if text else 0
            }
        
        else:
            # 通用AI应用
            return {
                "processed_input": input_data,
                "result": "AI processing completed",
                "model_used": "generic_ai_model",
                "processing_time_ms": 150
            }
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """分析情感（模拟）"""
        # 简单的情感分析模拟
        positive_words = ["好", "优秀", "棒", "完美", "喜欢", "爱", "高兴", "开心", "满意"]
        negative_words = ["差", "糟糕", "坏", "讨厌", "恨", "伤心", "难过", "失望", "愤怒"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        
        if total == 0:
            sentiment = "neutral"
            confidence = 0.5
            positive_score = 0.33
            negative_score = 0.33
            neutral_score = 0.34
        else:
            positive_ratio = positive_count / total
            negative_ratio = negative_count / total
            
            if positive_ratio > negative_ratio:
                sentiment = "positive"
                confidence = positive_ratio
            elif negative_ratio > positive_ratio:
                sentiment = "negative"
                confidence = negative_ratio
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            positive_score = positive_ratio
            negative_score = negative_ratio
            neutral_score = 1 - positive_ratio - negative_ratio
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive": positive_score,
            "negative": negative_score,
            "neutral": neutral_score
        }
    
    def _calculate_revenue(self, compute_hours: float) -> float:
        """计算收益（模拟）"""
        # 基础收益：$0.10 per GPU hour
        base_rate = 0.10
        
        # 根据应用复杂度调整
        complexity_factor = 1.0
        if "sentiment" in self.app_id.lower():
            complexity_factor = 0.8
        elif "translation" in self.app_id.lower():
            complexity_factor = 1.2
        elif "summary" in self.app_id.lower():
            complexity_factor = 1.0
        
        revenue = base_rate * compute_hours * complexity_factor
        
        return revenue
    
    def distribute_revenue(self) -> Dict:
        """分配收益给贡献者"""
        total_revenue = self.revenue_info["total_revenue"]
        
        if total_revenue <= 0:
            return {
                "success": False,
                "message": "没有可分配的收益",
                "total_revenue": total_revenue
            }
        
        distribution = {}
        total_distributed = 0
        
        for contributor in self.contributors:
            share = contributor["share_percentage"]
            amount = total_revenue * (share / 100)
            
            distribution[contributor["address"]] = {
                "amount": amount,
                "share_percentage": share,
                "role": contributor["role"]
            }
            
            total_distributed += amount
        
        # 更新收益信息
        self.revenue_info["last_payout_time"] = datetime.now().isoformat()
        
        # 在实际项目中，这里会调用智能合约进行实际分配
        
        logger.info(f"分配收益: 总收益=${total_revenue:.4f}, 分配总额=${total_distributed:.4f}")
        
        return {
            "success": True,
            "total_revenue": total_revenue,
            "total_distributed": total_distributed,
            "distribution": distribution,
            "payout_time": datetime.now().isoformat()
        }
    
    def get_app_info(self) -> Dict:
        """获取应用信息"""
        return {
            "app_id": self.app_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "contributors": self.contributors,
            "config": self.config,
            "deployment_info": self.deployment_info,
            "usage_stats": self.usage_stats,
            "revenue_info": self.revenue_info,
            "created_at": datetime.now().isoformat()
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        app_info = self.get_app_info()
        return json.dumps(app_info, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "AIApplicationTemplate":
        """从JSON字符串创建"""
        data = json.loads(json_str)
        
        app = cls(
            app_id=data["app_id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0")
        )
        
        app.contributors = data.get("contributors", [])
        app.config = data.get("config", {})
        app.deployment_info = data.get("deployment_info", {})
        app.usage_stats = data.get("usage_stats", {})
        app.revenue_info = data.get("revenue_info", {})
        
        return app


# 演示函数
def demo_app_template():
    """演示AI应用模板功能"""
    print("="*50)
    print("共创AI应用平台 - AI应用模板演示")
    print("="*50)
    
    # 创建情感分析应用
    print("\n1. 创建情感分析AI应用...")
    sentiment_app = AIApplicationTemplate(
        app_id="sentiment-analysis-v1",
        name="中文情感分析工具",
        description="基于深度学习的中文文本情感分析工具，支持积极、消极、中性情感识别"
    )
    
    # 添加贡献者
    sentiment_app.add_contributor("0xdeveloper123...", 40, "developer")
    sentiment_app.add_contributor("0xdatascientist456...", 30, "data_scientist")
    sentiment_app.add_contributor("0xtester789...", 20, "tester")
    sentiment_app.add_contributor("0xcommunity101...", 10, "community_manager")
    
    # 设置计算需求
    sentiment_app.set_compute_requirements(
        gpu_memory_gb=4,
        cpu_cores=2,
        memory_gb=8,
        storage_gb=20
    )
    
    # 添加依赖
    sentiment_app.add_dependency("torch", "2.0.0")
    sentiment_app.add_dependency("transformers", "4.30.0")
    sentiment_app.add_dependency("numpy", "1.24.0")
    
    # 添加API端点
    sentiment_app.add_api_endpoint(
        endpoint="/api/v1/sentiment",
        method="POST",
        description="分析文本情感",
        parameters=[
            {"name": "text", "type": "string", "required": True, "description": "待分析文本"},
            {"name": "language", "type": "string", "required": False, "default": "zh", "description": "文本语言"}
        ]
    )
    
    print(f"  应用创建完成: {sentiment_app.name}")
    print(f"  贡献者数量: {len(sentiment_app.contributors)}")
    print(f"  依赖数量: {len(sentiment_app.config['dependencies'])}")
    
    # 部署应用
    print("\n2. 部署应用到分布式网络...")
    deployment_result = sentiment_app.deploy(
        compute_nodes=["node1", "node2", "node3"],
        storage_nodes=["storage1", "storage2"]
    )
    
    print(f"  部署ID: {deployment_result['deployment_id']}")
    print(f"  计算节点: {deployment_result['compute_nodes']}")
    print(f"  存储节点: {deployment_result['storage_nodes']}")
    
    # 执行应用
    print("\n3. 执行AI应用...")
    
    test_inputs = [
        {"text": "这个产品非常好用，我非常喜欢！"},
        {"text": "服务太差了，以后再也不会来了。"},
        {"text": "产品一般般，没有什么特别的感觉。"}
    ]
    
    for i, input_data in enumerate(test_inputs, 1):
        print(f"\n  执行测试 {i}: {input_data['text'][:20]}...")
        result = sentiment_app.execute(input_data)
        
        if result["success"]:
            print(f"    情感: {result['result']['sentiment']}")
            print(f"    置信度: {result['result']['confidence']:.2%}")
            print(f"    执行时间: {result['execution_time_seconds']:.2f}秒")
            print(f"    生成收益: ${result['revenue_generated']:.4f}")
        else:
            print(f"    执行失败: {result['error']}")
    
    # 显示应用统计
    print("\n4. 应用使用统计...")
    stats = sentiment_app.usage_stats
    print(f"  总执行次数: {stats['total_runs']}")
    print(f"  成功次数: {stats['successful_runs']}")
    print(f"  失败次数: {stats['failed_runs']}")
    print(f"  总计算小时: {stats['total_compute_hours']:.2f}")
    print(f"  最后执行时间: {stats['last_run_time']}")
    
    # 分配收益
    print("\n5. 分配收益给贡献者...")
    distribution_result = sentiment_app.distribute_revenue()
    
    if distribution_result["success"]:
        print(f"  总收益: ${distribution_result['total_revenue']:.4f}")
        print(f"  分配总额: ${distribution_result['total_distributed']:.4f}")
        
        print(f"  分配详情:")
        for address, info in distribution_result["distribution"].items():
            print(f"    {address[:10]}...: ${info['amount']:.4f} ({info['share_percentage']}%) - {info['role']}")
    else:
        print(f"  收益分配: {distribution_result['message']}")
    
    # 保存应用信息
    print("\n6. 保存应用信息...")
    app_json = sentiment_app.to_json()
    
    # 可以保存到文件或上传到分布式存储
    with open("sentiment_app_info.json", "w", encoding="utf-8") as f:
        f.write(app_json)
    
    print(f"  应用信息已保存到 sentiment_app_info.json")
    print(f"  文件大小: {len(app_json)} 字节")
    
    # 从JSON恢复应用
    print("\n7. 从JSON恢复应用...")
    with open("sentiment_app_info.json", "r", encoding="utf-8") as f:
        restored_json = f.read()
    
    restored_app = AIApplicationTemplate.from_json(restored_json)
    print(f"  应用恢复成功: {restored_app.name}")
    print(f"  版本: {restored_app.version}")
    print(f"  贡献者数量: {len(restored_app.contributors)}")
    
    # 清理测试文件
    import os
    if os.path.exists("sentiment_app_info.json"):
        os.remove("sentiment_app_info.json")
        print(f"\n  已清理测试文件")
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)
