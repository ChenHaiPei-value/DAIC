"""
AI应用服务器分布式去中心化系统

一个允许不同用户授权给AI，去调用、操作数据库的分布式系统。
基于零信任架构，确保数据安全和隐私保护。
"""

__version__ = "1.0.0"
__author__ = "DAIC Team"
__description__ = "AI应用服务器分布式去中心化系统"

# 导出主要组件
from .ai_agent import AIAgent, PermissionError
from .permission_manager import PermissionManager, Permission, MemoryStorage, FileStorage
from .database_proxy import DatabaseProxy, SecurityError
from .helpers import MockConnectionPool, AuditLogger
from .demo_integrated import demo_integrated_system

__all__ = [
    # 主要组件
    "AIAgent",
    "PermissionManager",
    "DatabaseProxy",
    
    # 异常类
    "PermissionError",
    "SecurityError",
    
    # 数据类
    "Permission",
    
    # 存储后端
    "MemoryStorage",
    "FileStorage",
    
    # 辅助类
    "MockConnectionPool",
    "AuditLogger",
    
    # 演示函数
    "demo_integrated_system",
    
    # 元数据
    "__version__",
    "__author__",
    "__description__",
]