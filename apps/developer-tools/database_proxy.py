"""
数据库代理模块

负责安全地执行数据库查询，包括查询重写、数据脱敏、访问控制和审计日志。
"""

import json
import logging
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import random

logger = logging.getLogger(__name__)

# 动态导入辅助类
try:
    from .helpers import MockConnectionPool, AuditLogger
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from helpers import MockConnectionPool, AuditLogger


class DatabaseProxy:
    """数据库代理类"""
    
    def __init__(self, connection_pool=None, security_config=None):
        """
        初始化数据库代理
        
        Args:
            connection_pool: 数据库连接池
            security_config: 安全配置
        """
        self.connection_pool = connection_pool or MockConnectionPool()
        self.security_config = security_config or SecurityConfig()
        
        # 敏感数据检测规则
        self.sensitive_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
        
        # 查询缓存
        self.query_cache = {}
        
        # 审计日志
        self.audit_logger = AuditLogger()
        
        logger.info("数据库代理初始化完成")
    
    def execute_secure(self, sql_query: str, user_context: Dict = None) -> Dict:
        """
        执行安全查询
        
        Args:
            sql_query: SQL查询语句
            user_context: 用户上下文信息
            
        Returns:
            查询结果
        """
        start_time = datetime.now()
        
        try:
            # 1. 解析和验证查询
            parsed_query = self._parse_and_validate(sql_query)
            
            # 2. 应用访问控制
            controlled_query = self._apply_access_control(parsed_query, user_context)
            
            # 3. 数据脱敏
            if self._needs_masking(parsed_query):
                controlled_query = self._apply_data_masking(controlled_query)
            
            # 4. 执行查询
            result = self._execute_query(controlled_query)
            
            # 5. 应用差分隐私
            if self._needs_privacy(result, user_context):
                result = self._apply_differential_privacy(result)
            
            # 6. 记录审计日志
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._log_audit(parsed_query, result, user_context, execution_time)
            
            return {
                "success": True,
                "data": result.get("data", []),
                "row_count": result.get("row_count", 0),
                "execution_time_ms": execution_time,
                "query_hash": self._hash_query(sql_query),
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"安全查询执行失败: {e}")
            
            # 记录错误审计日志
            self._log_error_audit(sql_query, str(e), user_context, execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
                "timestamp": start_time.isoformat()
            }
    
    def _parse_and_validate(self, sql_query: str) -> Dict:
        """解析和验证SQL查询"""
        # 简化的SQL解析
        sql_lower = sql_query.lower().strip()
        
        parsed = {
            "original": sql_query,
            "operation": None,
            "tables": [],
            "columns": [],
            "conditions": [],
            "has_sensitive_data": False
        }
        
        # 提取操作类型
        if sql_lower.startswith("select"):
            parsed["operation"] = "SELECT"
        elif sql_lower.startswith("insert"):
            parsed["operation"] = "INSERT"
        elif sql_lower.startswith("update"):
            parsed["operation"] = "UPDATE"
        elif sql_lower.startswith("delete"):
            parsed["operation"] = "DELETE"
        else:
            raise ValueError(f"不支持的操作类型: {sql_query[:20]}...")
        
        # 安全检查
        self._validate_sql_security(sql_query)
        
        # 提取表名
        parsed["tables"] = self._extract_tables(sql_lower)
        
        # 提取列名
        parsed["columns"] = self._extract_columns(sql_lower)
        
        # 检查敏感数据
        parsed["has_sensitive_data"] = self._check_sensitive_data(sql_query)
        
        logger.debug(f"解析的查询: {parsed}")
        return parsed
    
    def _validate_sql_security(self, sql_query: str):
        """验证SQL安全性"""
        # 检查SQL注入风险
        dangerous_patterns = [
            r";\s*--",  # SQL注释
            r";\s*/\*",  # 多行注释
            r"union\s+select",  # UNION注入
            r"exec\s*\(",  # EXEC命令
            r"xp_cmdshell",  # 危险存储过程
            r"waitfor\s+delay",  # 时间延迟攻击
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                raise SecurityError(f"检测到潜在SQL注入风险: {pattern}")
        
        # 检查查询复杂度
        query_length = len(sql_query)
        if query_length > 10000:  # 10KB限制
            raise SecurityError(f"查询过长: {query_length}字符")
    
    def _extract_tables(self, sql_lower: str) -> List[str]:
        """提取表名"""
        tables = []
        
        # 查找FROM后面的表名
        from_match = re.search(r'from\s+(\w+)', sql_lower, re.IGNORECASE)
        if from_match:
            tables.append(from_match.group(1))
        
        # 查找JOIN后面的表名
        join_matches = re.findall(r'join\s+(\w+)', sql_lower, re.IGNORECASE)
        tables.extend(join_matches)
        
        return tables
    
    def _extract_columns(self, sql_lower: str) -> List[str]:
        """提取列名"""
        columns = []
        
        # SELECT查询的列
        if sql_lower.startswith("select"):
            select_match = re.search(r'select\s+(.*?)\s+from', sql_lower, re.IGNORECASE | re.DOTALL)
            if select_match:
                columns_str = select_match.group(1)
                # 提取列名，忽略函数和别名
                col_pattern = r'(\w+)(?:\s+as\s+\w+)?(?=\s*,|\s+from)'
                found_columns = re.findall(col_pattern, columns_str)
                columns.extend([col for col in found_columns if col != "*"])
        
        # UPDATE查询的SET列
        elif sql_lower.startswith("update"):
            set_match = re.search(r'set\s+(.*?)(?:\s+where|$)', sql_lower, re.IGNORECASE | re.DOTALL)
            if set_match:
                set_clause = set_match.group(1)
                # 提取SET中的列名
                set_columns = re.findall(r'(\w+)\s*=', set_clause)
                columns.extend(set_columns)
        
        return columns
    
    def _check_sensitive_data(self, sql_query: str) -> bool:
        """检查是否包含敏感数据"""
        for pattern_name, pattern in self.sensitive_patterns.items():
            if re.search(pattern, sql_query, re.IGNORECASE):
                logger.warning(f"检测到敏感数据模式: {pattern_name}")
                return True
        return False
    
    def _apply_access_control(self, parsed_query: Dict, user_context: Dict) -> str:
        """应用访问控制"""
        query = parsed_query["original"]
        
        if not user_context:
            return query
        
        # 获取用户权限
        permissions = user_context.get("permissions", {})
        
        # 应用行级权限
        row_filters = permissions.get("row_filters", [])
        for filter_condition in row_filters:
            query = self._add_where_condition(query, filter_condition)
        
        # 应用列级权限
        column_mask = permissions.get("column_mask", {})
        if column_mask:
            query = self._mask_columns(query, column_mask)
        
        # 应用操作限制
        allowed_operations = permissions.get("operations", ["SELECT"])
        if parsed_query["operation"] not in allowed_operations:
            raise PermissionError(f"不允许的操作: {parsed_query['operation']}")
        
        return query
    
    def _add_where_condition(self, query: str, condition: str) -> str:
        """添加WHERE条件"""
        sql_lower = query.lower()
        
        if "where" in sql_lower:
            # 已有WHERE条件，添加AND
            where_pos = sql_lower.find("where")
            before_where = query[:where_pos + 5]  # "where"长度
            after_where = query[where_pos + 5:]
            return f"{before_where} {condition} AND {after_where}"
        else:
            # 没有WHERE条件，添加WHERE
            # 查找合适的位置（在ORDER BY/LIMIT之前）
            order_by_pos = sql_lower.find("order by")
            limit_pos = sql_lower.find("limit")
            
            if order_by_pos != -1:
                before = query[:order_by_pos]
                after = query[order_by_pos:]
                return f"{before} WHERE {condition} {after}"
            elif limit_pos != -1:
                before = query[:limit_pos]
                after = query[limit_pos:]
                return f"{before} WHERE {condition} {after}"
            else:
                return f"{query} WHERE {condition}"
    
    def _mask_columns(self, query: str, column_mask: Dict) -> str:
        """掩码列"""
        # 简化实现：在实际项目中需要更复杂的SQL解析
        for column, mask_type in column_mask.items():
            if mask_type == "hash":
                # 使用哈希函数
                query = query.replace(
                    column,
                    f"MD5({column}) as {column}"
                )
            elif mask_type == "partial":
                # 部分显示
                query = query.replace(
                    column,
                    f"CONCAT(LEFT({column}, 3), '***', RIGHT({column}, 2)) as {column}"
                )
        
        return query
    
    def _needs_masking(self, parsed_query: Dict) -> bool:
        """检查是否需要数据脱敏"""
        return parsed_query.get("has_sensitive_data", False)
    
    def _apply_data_masking(self, query: str) -> str:
        """应用数据脱敏"""
        # 识别和替换敏感数据模式
        masked_query = query
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            def mask_match(match):
                original = match.group(0)
                if pattern_name == "email":
                    # 邮箱脱敏：user@domain.com -> u***@***.com
                    parts = original.split('@')
                    if len(parts) == 2:
                        username = parts[0]
                        domain = parts[1]
                        masked_username = username[0] + "***" if len(username) > 1 else "*"
                        masked_domain = "***." + domain.split('.')[-1]
                        return f"{masked_username}@{masked_domain}"
                
                elif pattern_name == "phone":
                    # 手机号脱敏：13812345678 -> 138****5678
                    if len(original) >= 7:
                        return original[:3] + "****" + original[-4:]
                
                elif pattern_name == "credit_card":
                    # 信用卡脱敏：1234 5678 9012 3456 -> **** **** **** 3456
                    digits = re.sub(r'[^0-9]', '', original)
                    if len(digits) >= 4:
                        return "**** **** **** " + digits[-4:]
                
                return "***"  # 默认脱敏
            
            masked_query = re.sub(pattern, mask_match, masked_query, flags=re.IGNORECASE)
        
        return masked_query
    
    def _execute_query(self, query: str) -> Dict:
        """执行查询"""
        # 检查缓存
        cache_key = self._hash_query(query)
        if cache_key in self.query_cache:
            logger.info(f"使用缓存查询: {cache_key}")
            cached_result = self.query_cache[cache_key]
            return {
                "data": cached_result["data"],
                "row_count": cached_result["row_count"],
                "cached": True
            }
        
        # 执行查询
        logger.info(f"执行查询: {query[:100]}...")
        
        # 使用模拟连接池执行
        result = self.connection_pool.execute(query)
        
        # 缓存结果（仅缓存SELECT查询）
        if query.lower().startswith("select"):
            self.query_cache[cache_key] = {
                "data": result.get("data", []),
                "row_count": result.get("row_count", 0)
            }
            # 限制缓存大小
            if len(self.query_cache) > 1000:
                oldest_key = next(iter(self.query_cache))
                del self.query_cache[oldest_key]
        
        return {
            "data": result.get("data", []),
            "row_count": result.get("row_count", 0),
            "cached": False
        }
    
    def _hash_query(self, query: str) -> str:
        """计算查询哈希"""
        # 规范化查询（移除多余空格）
        normalized = re.sub(r'\s+', ' ', query.strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _needs_privacy(self, result: Dict, user_context: Dict) -> bool:
        """检查是否需要差分隐私"""
        if not user_context:
            return False
        
        # 检查结果行数
        row_count = result.get("row_count", 0)
        
        # 小数据集需要差分隐私保护
        if row_count < 10:
            return True
        
        # 检查是否包含聚合数据
        data = result.get("data", [])
        if data and any(key for key in data[0] if "count" in key.lower() or "sum" in key.lower() or "avg" in key.lower()):
            return True
        
        return False
    
    def _apply_differential_privacy(self, result: Dict, epsilon: float = 1.0) -> Dict:
        """应用差分隐私"""
        data = result.get("data", [])
        if not data:
            return result
        
        # 对数值字段添加拉普拉斯噪声
        noisy_data = []
        for row in data:
            noisy_row = {}
            for key, value in row.items():
                if isinstance(value, (int, float)):
                    # 添加拉普拉斯噪声
                    scale = 1.0 / epsilon
                    noise = random.uniform(-scale, scale)
                    noisy_row[key] = value + noise
                else:
                    noisy_row[key] = value
            noisy_data.append(noisy_row)
        
        return {
            "data": noisy_data,
            "row_count": result.get("row_count", 0),
            "privacy_applied": True,
            "epsilon": epsilon
        }
    
    def _log_audit(self, parsed_query: Dict, result: Dict, user_context: Dict, execution_time: float):
        """记录审计日志"""
        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": parsed_query.get("operation"),
            "tables": parsed_query.get("tables", []),
            "row_count": result.get("row_count", 0),
            "execution_time_ms": execution_time,
            "user_id": user_context.get("user_id") if user_context else None,
            "user_address": user_context.get("user_address") if user_context else None,
            "has_sensitive_data": parsed_query.get("has_sensitive_data", False),
            "privacy_applied": result.get("privacy_applied", False),
            "query_hash": self._hash_query(parsed_query.get("original", ""))
        }
        
        self.audit_logger.log(audit_record)
        logger.info(f"审计日志: {json.dumps(audit_record, ensure_ascii=False)}")
    
    def _log_error_audit(self, sql_query: str, error: str, user_context: Dict, execution_time: float):
        """记录错误审计日志"""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "execution_time_ms": execution_time,
            "user_id": user_context.get("user_id") if user_context else None,
            "user_address": user_context.get("user_address") if user_context else None,
            "query_hash": self._hash_query(sql_query)
        }
        
        self.audit_logger.log_error(error_record)
        logger.error(f"错误审计日志: {json.dumps(error_record, ensure_ascii=False)}")
    
    def clear_cache(self):
        """清空查询缓存"""
        self.query_cache.clear()
        logger.info("查询缓存已清空")


class SecurityError(Exception):
    """安全错误异常"""
    pass


class PermissionError(Exception):
    """权限错误异常"""
    pass


class SecurityConfig:
    """安全配置类"""
    
    def __init__(self):
        self.max_query_length = 10000
        self.enable_sql_injection_check = True
        self.enable_data_masking = True
        self.enable_differential_privacy = True
        self.privacy_epsilon = 1.0
        self.max_cache_size = 1000
        self.audit_log_enabled = True
