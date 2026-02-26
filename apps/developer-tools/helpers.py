"""
辅助类模块

包含数据库代理需要的辅助类：MockConnectionPool、AuditLogger等。
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class MockConnectionPool:
    """模拟数据库连接池"""
    
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.active_connections = 0
        self.query_history = []
        
        logger.info(f"模拟连接池初始化，最大连接数: {max_connections}")
    
    def execute(self, query: str) -> Dict:
        """执行查询"""
        self.active_connections += 1
        
        try:
            # 模拟查询执行
            result = self._simulate_query_execution(query)
            
            # 记录查询历史
            self.query_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query[:100] + "..." if len(query) > 100 else query,
                "execution_time_ms": result.get("execution_time_ms", 0),
                "row_count": result.get("row_count", 0)
            })
            
            # 限制历史记录大小
            if len(self.query_history) > 1000:
                self.query_history.pop(0)
            
            return result
            
        finally:
            self.active_connections -= 1
    
    def _simulate_query_execution(self, query: str) -> Dict:
        """模拟查询执行"""
        query_lower = query.lower()
        
        # 模拟执行时间（10-500ms）
        execution_time = random.uniform(10, 500)
        
        # 根据查询类型返回模拟数据
        if "select" in query_lower:
            if "customer" in query_lower and "sales" in query_lower:
                # 客户销售数据
                return {
                    "data": [
                        {"customer_id": 1, "customer_name": "客户A", "total_sales": 150000, "email": "customer_a@example.com", "phone": "13812345678"},
                        {"customer_id": 2, "customer_name": "客户B", "total_sales": 120000, "email": "customer_b@example.com", "phone": "13987654321"},
                        {"customer_id": 3, "customer_name": "客户C", "total_sales": 98000, "email": "customer_c@example.com", "phone": "13711223344"},
                        {"customer_id": 4, "customer_name": "客户D", "total_sales": 85000, "email": "customer_d@example.com", "phone": "13644556677"},
                        {"customer_id": 5, "customer_name": "客户E", "total_sales": 72000, "email": "customer_e@example.com", "phone": "13577889900"},
                    ],
                    "row_count": 5,
                    "execution_time_ms": execution_time
                }
            elif "count" in query_lower:
                # 计数查询
                return {
                    "data": [{"count": random.randint(100, 1000)}],
                    "row_count": 1,
                    "execution_time_ms": execution_time
                }
            elif "avg" in query_lower or "average" in query_lower:
                # 平均值查询
                return {
                    "data": [{"avg_value": random.uniform(1000, 5000)}],
                    "row_count": 1,
                    "execution_time_ms": execution_time
                }
            else:
                # 通用查询
                return {
                    "data": [
                        {"id": 1, "name": "示例数据1", "value": 100},
                        {"id": 2, "name": "示例数据2", "value": 200},
                        {"id": 3, "name": "示例数据3", "value": 300},
                    ],
                    "row_count": 3,
                    "execution_time_ms": execution_time
                }
        elif "insert" in query_lower:
            # 插入操作
            return {
                "data": [],
                "row_count": 1,
                "insert_id": random.randint(1000, 9999),
                "execution_time_ms": execution_time
            }
        elif "update" in query_lower:
            # 更新操作
            return {
                "data": [],
                "row_count": random.randint(1, 10),
                "execution_time_ms": execution_time
            }
        elif "delete" in query_lower:
            # 删除操作
            return {
                "data": [],
                "row_count": random.randint(1, 5),
                "execution_time_ms": execution_time
            }
        else:
            # 默认返回
            return {
                "data": [{"message": "查询执行成功"}],
                "row_count": 1,
                "execution_time_ms": execution_time
            }
    
    def get_stats(self) -> Dict:
        """获取连接池统计信息"""
        return {
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "total_queries_executed": len(self.query_history),
            "recent_queries": self.query_history[-10:] if self.query_history else []
        }


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, log_file="audit_log.jsonl", max_file_size_mb=100):
        self.log_file = log_file
        self.max_file_size_mb = max_file_size_mb
        self.error_log_file = "audit_errors.jsonl"
        
        logger.info(f"审计日志记录器初始化，日志文件: {log_file}")
    
    def log(self, audit_record: Dict):
        """记录审计日志"""
        try:
            # 添加时间戳
            if "timestamp" not in audit_record:
                audit_record["timestamp"] = datetime.now().isoformat()
            
            # 写入日志文件
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_record, ensure_ascii=False) + '\n')
            
            # 检查文件大小
            self._check_file_size()
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {e}")
            # 尝试记录错误
            self._log_error({"error": str(e), "original_record": audit_record})
    
    def log_error(self, error_record: Dict):
        """记录错误日志"""
        try:
            # 添加时间戳
            if "timestamp" not in error_record:
                error_record["timestamp"] = datetime.now().isoformat()
            
            # 写入错误日志文件
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_record, ensure_ascii=False) + '\n')
            
        except Exception as e:
            logger.error(f"记录错误日志失败: {e}")
    
    def _log_error(self, error_data: Dict):
        """内部错误记录"""
        try:
            error_data["log_timestamp"] = datetime.now().isoformat()
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_data, ensure_ascii=False) + '\n')
        except:
            pass  # 如果连错误日志都写不了，只能放弃了
    
    def _check_file_size(self):
        """检查文件大小"""
        try:
            import os
            if os.path.exists(self.log_file):
                file_size_mb = os.path.getsize(self.log_file) / (1024 * 1024)
                if file_size_mb > self.max_file_size_mb:
                    self._rotate_log_file()
        except Exception as e:
            logger.error(f"检查日志文件大小失败: {e}")
    
    def _rotate_log_file(self):
        """轮转日志文件"""
        try:
            import os
            import shutil
            from datetime import datetime
            
            # 创建备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.log_file}.{timestamp}.bak"
            
            # 备份当前日志文件
            if os.path.exists(self.log_file):
                shutil.move(self.log_file, backup_file)
                logger.info(f"日志文件已轮转: {backup_file}")
            
            # 创建新的日志文件
            open(self.log_file, 'w').close()
            
        except Exception as e:
            logger.error(f"轮转日志文件失败: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """获取最近的审计日志"""
        try:
            logs = []
            if not os.path.exists(self.log_file):
                return logs
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 读取最后limit行
            for line in lines[-limit:]:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except:
                    continue
            
            return logs
            
        except Exception as e:
            logger.error(f"读取审计日志失败: {e}")
            return []
    
    def search_logs(self, criteria: Dict) -> List[Dict]:
        """搜索审计日志"""
        try:
            all_logs = self.get_recent_logs(1000)  # 限制搜索范围
            filtered_logs = []
            
            for log in all_logs:
                match = True
                for key, value in criteria.items():
                    if key not in log or log[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_logs.append(log)
            
            return filtered_logs
            
        except Exception as e:
            logger.error(f"搜索审计日志失败: {e}")
            return []


# 导入os模块用于helpers.py内部使用
import os


# 演示函数
def demo_helpers():
    """演示辅助类功能"""
    print("="*50)
    print("辅助类演示")
    print("="*50)
    
    # 测试模拟连接池
    print("\n1. 模拟连接池测试:")
    pool = MockConnectionPool(max_connections=5)
    
    test_queries = [
        "SELECT * FROM customers WHERE total_sales > 100000",
        "SELECT COUNT(*) as customer_count FROM customers",
        "INSERT INTO orders (customer_id, amount) VALUES (1, 500)",
        "UPDATE customers SET status = 'active' WHERE id = 1",
        "DELETE FROM temp_data WHERE created_at < '2024-01-01'"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n  查询 {i}: {query[:50]}...")
        result = pool.execute(query)
        print(f"    结果行数: {result.get('row_count', 0)}")
        print(f"    执行时间: {result.get('execution_time_ms', 0):.1f}ms")
        if result.get('data'):
            print(f"    示例数据: {result['data'][0]}")
    
    # 获取连接池统计
    stats = pool.get_stats()
    print(f"\n  连接池统计:")
    print(f"    最大连接数: {stats['max_connections']}")
    print(f"    活跃连接数: {stats['active_connections']}")
    print(f"    总查询数: {stats['total_queries_executed']}")
    
    # 测试审计日志记录器
    print("\n2. 审计日志记录器测试:")
    auditor = AuditLogger(log_file="test_audit.log")
    
    test_logs = [
        {
            "operation": "SELECT",
            "tables": ["customers"],
            "row_count": 5,
            "user_id": "user_123",
            "execution_time_ms": 45.2
        },
        {
            "operation": "UPDATE",
            "tables": ["orders"],
            "row_count": 1,
            "user_id": "user_456",
            "execution_time_ms": 23.7
        }
    ]
    
    for log in test_logs:
        auditor.log(log)
        print(f"  记录审计日志: {log['operation']} {log['tables'][0]}")
    
    # 读取最近的日志
    recent_logs = auditor.get_recent_logs(5)
    print(f"\n  最近 {len(recent_logs)} 条审计日志:")
    for log in recent_logs:
        print(f"    {log.get('timestamp', '')}: {log.get('operation', '')} {log.get('tables', [])}")
    
    # 清理测试文件
    try:
        if os.path.exists("test_audit.log"):
            os.remove("test_audit.log")
        if os.path.exists("audit_errors.jsonl"):
            os.remove("audit_errors.jsonl")
    except:
        pass
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)


if __name__ == "__main__":
    demo_helpers()