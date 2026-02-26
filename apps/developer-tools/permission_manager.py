"""
权限管理模块

负责管理用户对AI代理的授权，验证AI代理对数据库的访问权限。
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import hashlib
import uuid

logger = logging.getLogger(__name__)


class Permission:
    """权限类"""
    
    def __init__(
        self,
        permission_id: str,
        user_address: str,
        ai_agent_address: str,
        database: str,
        table: str,
        columns: List[str],
        operations: List[str],
        valid_from: datetime,
        valid_until: datetime,
        max_rows: int = 1000,
        usage_count: int = 0,
        is_active: bool = True
    ):
        """
        初始化权限
        
        Args:
            permission_id: 权限唯一标识
            user_address: 用户地址
            ai_agent_address: AI代理地址
            database: 数据库名
            table: 表名
            columns: 允许访问的列
            operations: 允许的操作 (SELECT, INSERT, UPDATE, DELETE)
            valid_from: 权限生效时间
            valid_until: 权限过期时间
            max_rows: 最大返回行数
            usage_count: 使用次数
            is_active: 是否激活
        """
        self.permission_id = permission_id
        self.user_address = user_address
        self.ai_agent_address = ai_agent_address
        self.database = database
        self.table = table
        self.columns = set(columns)  # 使用集合便于查找
        self.operations = set(operations)  # 使用集合便于查找
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.max_rows = max_rows
        self.usage_count = usage_count
        self.is_active = is_active
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 使用历史记录
        self.usage_history: List[Dict] = []
    
    def is_valid(self) -> bool:
        """检查权限是否有效"""
        now = datetime.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until
        )
    
    def has_permission(self, operation: str, column: str = None) -> bool:
        """
        检查是否有特定操作的权限
        
        Args:
            operation: 操作类型 (SELECT, INSERT, UPDATE, DELETE)
            column: 列名 (可选)
            
        Returns:
            是否有权限
        """
        if not self.is_valid():
            return False
        
        # 检查操作权限
        if operation.upper() not in self.operations:
            return False
        
        # 检查列权限
        if column and column not in self.columns:
            return False
        
        return True
    
    def record_usage(self, operation: str, rows_affected: int = 1) -> bool:
        """
        记录权限使用
        
        Args:
            operation: 操作类型
            rows_affected: 影响的行数
            
        Returns:
            是否允许继续使用
        """
        if not self.is_valid():
            return False
        
        # 检查行数限制
        if self.usage_count + rows_affected > self.max_rows:
            logger.warning(f"权限 {self.permission_id} 已达到最大行数限制")
            return False
        
        # 记录使用
        self.usage_count += rows_affected
        self.usage_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "rows_affected": rows_affected,
            "total_usage": self.usage_count
        })
        self.updated_at = datetime.now()
        
        logger.info(f"权限 {self.permission_id} 使用记录: {operation} ({rows_affected}行)")
        return True
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "permission_id": self.permission_id,
            "user_address": self.user_address,
            "ai_agent_address": self.ai_agent_address,
            "database": self.database,
            "table": self.table,
            "columns": list(self.columns),
            "operations": list(self.operations),
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "max_rows": self.max_rows,
            "usage_count": self.usage_count,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_valid": self.is_valid()
        }


class PermissionManager:
    """权限管理器"""
    
    def __init__(self, storage_backend=None):
        """
        初始化权限管理器
        
        Args:
            storage_backend: 存储后端 (默认为内存存储)
        """
        self.permissions: Dict[str, Permission] = {}
        self.storage_backend = storage_backend or MemoryStorage()
        
        # 加载权限数据
        self._load_permissions()
        
        logger.info("权限管理器初始化完成")
    
    def _load_permissions(self):
        """加载权限数据"""
        try:
            permissions_data = self.storage_backend.load_permissions()
            for perm_data in permissions_data:
                permission = self._create_permission_from_dict(perm_data)
                self.permissions[permission.permission_id] = permission
            
            logger.info(f"加载了 {len(permissions_data)} 个权限")
        except Exception as e:
            logger.error(f"加载权限数据失败: {e}")
    
    def _create_permission_from_dict(self, data: Dict) -> Permission:
        """从字典创建权限"""
        return Permission(
            permission_id=data["permission_id"],
            user_address=data["user_address"],
            ai_agent_address=data["ai_agent_address"],
            database=data["database"],
            table=data["table"],
            columns=data["columns"],
            operations=data["operations"],
            valid_from=datetime.fromisoformat(data["valid_from"]),
            valid_until=datetime.fromisoformat(data["valid_until"]),
            max_rows=data["max_rows"],
            usage_count=data.get("usage_count", 0),
            is_active=data.get("is_active", True)
        )
    
    def grant_permission(
        self,
        user_address: str,
        ai_agent_address: str,
        database: str,
        table: str,
        columns: List[str],
        operations: List[str],
        valid_until: str,
        max_rows: int = 1000
    ) -> str:
        """
        授予权限
        
        Args:
            user_address: 用户地址
            ai_agent_address: AI代理地址
            database: 数据库名
            table: 表名
            columns: 允许访问的列
            operations: 允许的操作
            valid_until: 过期时间 (ISO格式字符串)
            max_rows: 最大返回行数
            
        Returns:
            权限ID
        """
        # 生成权限ID
        permission_id = self._generate_permission_id(
            user_address, ai_agent_address, database, table
        )
        
        # 解析时间
        valid_from = datetime.now()
        valid_until_dt = datetime.fromisoformat(valid_until)
        
        # 创建权限
        permission = Permission(
            permission_id=permission_id,
            user_address=user_address,
            ai_agent_address=ai_agent_address,
            database=database,
            table=table,
            columns=columns,
            operations=operations,
            valid_from=valid_from,
            valid_until=valid_until_dt,
            max_rows=max_rows
        )
        
        # 保存权限
        self.permissions[permission_id] = permission
        self.storage_backend.save_permission(permission.to_dict())
        
        logger.info(f"授予权限: {permission_id}")
        logger.info(f"  用户: {user_address}")
        logger.info(f"  AI代理: {ai_agent_address}")
        logger.info(f"  表: {database}.{table}")
        logger.info(f"  操作: {operations}")
        logger.info(f"  有效期: {valid_from} 至 {valid_until_dt}")
        
        return permission_id
    
    def _generate_permission_id(
        self,
        user_address: str,
        ai_agent_address: str,
        database: str,
        table: str
    ) -> str:
        """生成权限ID"""
        # 使用哈希生成唯一ID
        content = f"{user_address}:{ai_agent_address}:{database}:{table}:{datetime.now().timestamp()}"
        hash_obj = hashlib.sha256(content.encode())
        return f"perm_{hash_obj.hexdigest()[:16]}"
    
    def verify_permission(
        self,
        permission_id: str,
        ai_agent_address: str,
        operation: str,
        table: str,
        column: str = None
    ) -> bool:
        """
        验证权限
        
        Args:
            permission_id: 权限ID
            ai_agent_address: AI代理地址
            operation: 操作类型
            table: 表名
            column: 列名 (可选)
            
        Returns:
            是否有权限
        """
        # 查找权限
        permission = self.permissions.get(permission_id)
        if not permission:
            logger.warning(f"权限不存在: {permission_id}")
            return False
        
        # 检查AI代理地址
        if permission.ai_agent_address != ai_agent_address:
            logger.warning(f"AI代理地址不匹配: {ai_agent_address} != {permission.ai_agent_address}")
            return False
        
        # 检查表名
        if permission.table != table:
            logger.warning(f"表名不匹配: {table} != {permission.table}")
            return False
        
        # 检查权限
        if not permission.has_permission(operation, column):
            logger.warning(f"权限不足: {operation} {column or ''}")
            return False
        
        # 记录使用
        if not permission.record_usage(operation):
            logger.warning(f"权限使用记录失败: {permission_id}")
            return False
        
        # 更新存储
        self.storage_backend.save_permission(permission.to_dict())
        
        logger.info(f"权限验证通过: {permission_id} - {operation} {table}.{column or '*'}")
        return True
    
    def revoke_permission(self, permission_id: str, user_address: str) -> bool:
        """
        撤销权限
        
        Args:
            permission_id: 权限ID
            user_address: 用户地址
            
        Returns:
            是否成功撤销
        """
        permission = self.permissions.get(permission_id)
        if not permission:
            logger.warning(f"权限不存在: {permission_id}")
            return False
        
        # 检查用户权限
        if permission.user_address != user_address:
            logger.warning(f"用户无权撤销此权限: {user_address}")
            return False
        
        # 撤销权限
        permission.is_active = False
        permission.updated_at = datetime.now()
        
        # 更新存储
        self.storage_backend.save_permission(permission.to_dict())
        
        logger.info(f"权限已撤销: {permission_id}")
        return True
    
    def get_user_permissions(self, user_address: str) -> List[Dict]:
        """获取用户的所有权限"""
        user_perms = []
        for permission in self.permissions.values():
            if permission.user_address == user_address:
                user_perms.append(permission.to_dict())
        
        return user_perms
    
    def get_agent_permissions(self, ai_agent_address: str) -> List[Dict]:
        """获取AI代理的所有权限"""
        agent_perms = []
        for permission in self.permissions.values():
            if permission.ai_agent_address == ai_agent_address and permission.is_valid():
                agent_perms.append(permission.to_dict())
        
        return agent_perms
    
    def cleanup_expired_permissions(self) -> int:
        """清理过期权限"""
        expired_count = 0
        now = datetime.now()
        
        for permission_id, permission in list(self.permissions.items()):
            if permission.valid_until < now:
                # 标记为不活跃
                permission.is_active = False
                permission.updated_at = now
                self.storage_backend.save_permission(permission.to_dict())
                expired_count += 1
                
                logger.info(f"清理过期权限: {permission_id}")
        
        return expired_count
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.permissions)
        active = sum(1 for p in self.permissions.values() if p.is_active and p.is_valid())
        expired = sum(1 for p in self.permissions.values() if not p.is_valid())
        
        # 按操作类型统计
        operation_stats = {}
        for permission in self.permissions.values():
            for operation in permission.operations:
                operation_stats[operation] = operation_stats.get(operation, 0) + 1
        
        return {
            "total_permissions": total,
            "active_permissions": active,
            "expired_permissions": expired,
            "operation_distribution": operation_stats,
            "total_usage": sum(p.usage_count for p in self.permissions.values())
        }


class MemoryStorage:
    """内存存储后端"""
    
    def __init__(self):
        self.permissions_data = []
    
    def load_permissions(self) -> List[Dict]:
        """加载权限数据"""
        return self.permissions_data
    
    def save_permission(self, permission_data: Dict):
        """保存权限数据"""
        # 查找是否已存在
        for i, perm in enumerate(self.permissions_data):
            if perm["permission_id"] == permission_data["permission_id"]:
                self.permissions_data[i] = permission_data
                return
        
        # 新增
        self.permissions_data.append(permission_data)


class FileStorage:
    """文件存储后端"""
    
    def __init__(self, filepath: str = "permissions.json"):
        self.filepath = filepath
    
    def load_permissions(self) -> List[Dict]:
        """从文件加载权限数据"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"加载权限文件失败: {e}")
            return []
    
    def save_permission(self, permission_data: Dict):
        """保存权限数据到文件"""
        try:
            # 加载现有数据
            permissions = self.load_permissions()
            
            # 更新或添加
            found = False
            for i, perm in enumerate(permissions):
                if perm["permission_id"] == permission_data["permission_id"]:
                    permissions[i] = permission_data
                    found = True
                    break
            
            if not found:
                permissions.append(permission_data)
            
            # 保存到文件
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(permissions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存权限文件失败: {e}")


# 演示函数
def demo_permission_manager():
    """演示权限管理器功能"""
    print("="*50)
    print("权限管理器演示")
    print("="*50)
    
    # 创建权限管理器
    pm = PermissionManager()
    
    # 授予权限
    permission_id = pm.grant_permission(
        user_address="0xuser123...",
        ai_agent_address="0xaiagent456...",
        database="sales_db",
        table="customers",
        columns=["id", "name", "email", "total_purchases"],
        operations=["SELECT"],
        valid_until="2025-12-31T23:59:59",
        max_rows=1000
    )
    
    print(f"授予的权限ID: {permission_id}")
    
    # 验证权限
    print("\n权限验证测试:")
    
    # 有效权限
    valid = pm.verify_permission(
        permission_id=permission_id,
        ai_agent_address="0xaiagent456...",
        operation="SELECT",
        table="customers",
        column="name"
    )
    print(f"  有效权限测试: {'通过' if valid else '失败'}")
    
    # 无效操作
    invalid_op = pm.verify_permission(
        permission_id=permission_id,
        ai_agent_address="0xaiagent456...",
        operation="DELETE",  # 没有DELETE权限
        table="customers"
    )
    print(f"  无效操作测试: {'应失败' if not invalid_op else '错误'}")
    
    # 无效列
    invalid_col = pm.verify_permission(
        permission_id=permission_id,
        ai_agent_address="0xaiagent456...",
        operation="SELECT",
        table="customers",
        column="password"  # 没有password列权限
    )
    print(f"  无效列测试: {'应失败' if not invalid_col else '错误'}")
    
    # 获取用户权限
    user_perms = pm.get_user_permissions("0xuser123...")
    print(f"\n用户权限数量: {len(user_perms)}")
    
    # 获取统计信息
    stats = pm.get_statistics()
    print(f"\n统计信息:")
    print(f"  总权限数: {stats['total_permissions']}")
    print(f"  活跃权限: {stats['active_permissions']}")
    print(f"  过期权限: {stats['expired_permissions']}")
    print(f"  操作分布: {stats['operation_distribution']}")
    print(f"  总使用次数: {stats['total_usage']}")
    
    # 清理过期权限
    expired_count = pm.cleanup_expired_permissions()
    print(f"\n清理的过期权限: {expired_count}")
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)


if __name__ == "__main__":
    demo_permission_manager()