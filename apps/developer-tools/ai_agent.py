"""
AI代理模块

负责处理用户自然语言请求，转换为SQL查询，验证权限，并执行安全查询。
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class PermissionError(Exception):
    """权限错误异常"""
    pass


class AIAgent:
    """AI代理类"""
    
    def __init__(self, agent_id: str, permission_manager):
        """
        初始化AI代理
        
        Args:
            agent_id: 代理唯一标识
            permission_manager: 权限管理器实例
        """
        self.agent_id = agent_id
        self.permission_manager = permission_manager
        self.llm = self._load_llm()
        self.query_cache = {}  # 查询缓存
        
        logger.info(f"AI代理 {agent_id} 初始化完成")
    
    def _load_llm(self):
        """加载语言模型"""
        # 这里可以集成各种LLM，如OpenAI GPT、Claude、本地模型等
        # 暂时使用模拟实现
        class MockLLM:
            def generate_sql(self, natural_language: str) -> str:
                """模拟生成SQL"""
                # 简单的规则匹配
                if "销售额" in natural_language and "最高" in natural_language:
                    return """
                        SELECT customer_id, customer_name, SUM(amount) as total_sales
                        FROM sales
                        WHERE sale_date >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
                        GROUP BY customer_id, customer_name
                        ORDER BY total_sales DESC
                        LIMIT 10
                    """
                elif "客户数量" in natural_language:
                    return "SELECT COUNT(*) as customer_count FROM customers"
                elif "平均订单金额" in natural_language:
                    return "SELECT AVG(amount) as avg_order_amount FROM orders"
                else:
                    return "SELECT * FROM data LIMIT 10"
            
            def explain_result(self, result: Dict, original_query: str) -> str:
                """解释查询结果"""
                if "total_sales" in str(result):
                    return "这是上个月销售额最高的10个客户"
                elif "customer_count" in str(result):
                    return f"总客户数量为: {result.get('customer_count', 0)}"
                elif "avg_order_amount" in str(result):
                    return f"平均订单金额为: {result.get('avg_order_amount', 0):.2f}"
                else:
                    return "查询完成"
        
        return MockLLM()
    
    def process_request(self, user_request: str, user_address: str) -> Dict:
        """
        处理用户请求
        
        Args:
            user_request: 用户自然语言请求
            user_address: 用户地址
            
        Returns:
            处理结果
            
        Raises:
            PermissionError: 权限验证失败
        """
        logger.info(f"处理用户请求: {user_request}")
        
        # 1. 理解用户意图
        intent = self._understand_intent(user_request)
        
        # 2. 生成SQL查询
        sql_query = self._generate_sql(intent, user_request)
        
        # 3. 验证权限
        if not self._verify_permission(user_address, sql_query):
            raise PermissionError(f"AI代理 {self.agent_id} 没有执行此操作的权限")
        
        # 4. 执行安全查询
        result = self._execute_secure_query(sql_query)
        
        # 5. 解释结果
        explanation = self._explain_result(result, user_request)
        
        # 6. 记录审计日志
        self._log_audit(user_address, sql_query, result)
        
        return {
            "result": result,
            "explanation": explanation,
            "sql_query": sql_query,
            "permission_verified": True,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
    
    def _understand_intent(self, user_request: str) -> Dict:
        """理解用户意图"""
        # 这里可以使用更复杂的NLP技术
        # 暂时使用简单的关键词匹配
        
        intent = {
            "type": "query",
            "entities": [],
            "operations": ["SELECT"],  # 默认只查询
            "tables": self._extract_tables(user_request),
            "conditions": self._extract_conditions(user_request)
        }
        
        # 检测操作类型
        if any(word in user_request.lower() for word in ["添加", "插入", "新增"]):
            intent["operations"] = ["INSERT"]
        elif any(word in user_request.lower() for word in ["更新", "修改", "改变"]):
            intent["operations"] = ["UPDATE"]
        elif any(word in user_request.lower() for word in ["删除", "移除"]):
            intent["operations"] = ["DELETE"]
        
        return intent
    
    def _extract_tables(self, user_request: str) -> List[str]:
        """提取表名"""
        # 简单的关键词匹配
        tables = []
        
        table_keywords = {
            "客户": "customers",
            "订单": "orders",
            "销售": "sales",
            "产品": "products",
            "用户": "users"
        }
        
        for keyword, table in table_keywords.items():
            if keyword in user_request:
                tables.append(table)
        
        return tables if tables else ["data"]  # 默认表
    
    def _extract_conditions(self, user_request: str) -> List[Dict]:
        """提取查询条件"""
        conditions = []
        
        # 时间条件
        if "上个月" in user_request:
            conditions.append({
                "column": "sale_date",
                "operator": ">=",
                "value": "DATE_SUB(NOW(), INTERVAL 1 MONTH)"
            })
        elif "上周" in user_request:
            conditions.append({
                "column": "sale_date",
                "operator": ">=",
                "value": "DATE_SUB(NOW(), INTERVAL 1 WEEK)"
            })
        
        # 数值条件
        if "最高" in user_request:
            conditions.append({
                "type": "ordering",
                "column": "total_sales",
                "direction": "DESC",
                "limit": 10
            })
        elif "最低" in user_request:
            conditions.append({
                "type": "ordering",
                "column": "total_sales",
                "direction": "ASC",
                "limit": 10
            })
        
        return conditions
    
    def _generate_sql(self, intent: Dict, user_request: str) -> str:
        """生成SQL查询"""
        # 检查缓存
        cache_key = hashlib.md5(user_request.encode()).hexdigest()
        if cache_key in self.query_cache:
            logger.info(f"使用缓存的SQL查询: {cache_key}")
            return self.query_cache[cache_key]
        
        # 使用LLM生成SQL
        sql_query = self.llm.generate_sql(user_request)
        
        # 缓存查询
        self.query_cache[cache_key] = sql_query
        
        logger.info(f"生成的SQL查询: {sql_query}")
        return sql_query
    
    def _verify_permission(self, user_address: str, sql_query: str) -> bool:
        """验证权限"""
        try:
            # 解析SQL查询
            parsed_query = self._parse_sql(sql_query)
            
            # 获取权限ID
            permission_id = self._get_permission_id(user_address, self.agent_id)
            
            # 验证权限
            for operation in parsed_query.get("operations", []):
                for table in parsed_query.get("tables", []):
                    for column in parsed_query.get("columns", []):
                        if not self.permission_manager.verify_permission(
                            permission_id,
                            self.agent_id,
                            operation,
                            table,
                            column
                        ):
                            logger.warning(f"权限验证失败: {operation} {table}.{column}")
                            return False
            
            logger.info("权限验证通过")
            return True
            
        except Exception as e:
            logger.error(f"权限验证异常: {e}")
            return False
    
    def _parse_sql(self, sql_query: str) -> Dict:
        """解析SQL查询"""
        # 简化的SQL解析
        # 实际项目中应该使用SQL解析库如sqlparse
        
        sql_lower = sql_query.lower().strip()
        
        parsed = {
            "original": sql_query,
            "operations": [],
            "tables": [],
            "columns": [],
            "conditions": []
        }
        
        # 提取操作类型
        if sql_lower.startswith("select"):
            parsed["operations"].append("SELECT")
        elif sql_lower.startswith("insert"):
            parsed["operations"].append("INSERT")
        elif sql_lower.startswith("update"):
            parsed["operations"].append("UPDATE")
        elif sql_lower.startswith("delete"):
            parsed["operations"].append("DELETE")
        
        # 提取表名（简化版）
        import re
        
        # 查找FROM后面的表名
        from_match = re.search(r'from\s+(\w+)', sql_lower, re.IGNORECASE)
        if from_match:
            parsed["tables"].append(from_match.group(1))
        
        # 查找JOIN后面的表名
        join_matches = re.findall(r'join\s+(\w+)', sql_lower, re.IGNORECASE)
        parsed["tables"].extend(join_matches)
        
        # 提取列名（简化版）
        select_match = re.search(r'select\s+(.*?)\s+from', sql_lower, re.IGNORECASE | re.DOTALL)
        if select_match:
            columns_str = select_match.group(1)
            # 简单的列名提取
            columns = re.findall(r'(\w+)(?:\s+as\s+\w+)?', columns_str)
            parsed["columns"].extend([col for col in columns if col != "*"])
        
        return parsed
    
    def _get_permission_id(self, user_address: str, agent_id: str) -> str:
        """获取权限ID"""
        # 这里应该从智能合约或数据库中获取
        # 暂时使用模拟实现
        return f"permission_{user_address}_{agent_id}"
    
    def _execute_secure_query(self, sql_query: str) -> Dict:
        """执行安全查询"""
        # 这里应该通过数据库代理执行查询
        # 暂时使用模拟实现
        
        logger.info(f"执行安全查询: {sql_query}")
        
        # 模拟查询结果
        if "total_sales" in sql_query.lower():
            return {
                "data": [
                    {"customer_id": 1, "customer_name": "客户A", "total_sales": 150000},
                    {"customer_id": 2, "customer_name": "客户B", "total_sales": 120000},
                    {"customer_id": 3, "customer_name": "客户C", "total_sales": 98000},
                ],
                "row_count": 3,
                "execution_time_ms": 45
            }
        elif "customer_count" in sql_query.lower():
            return {
                "data": [{"customer_count": 150}],
                "row_count": 1,
                "execution_time_ms": 12
            }
        elif "avg_order_amount" in sql_query.lower():
            return {
                "data": [{"avg_order_amount": 1250.75}],
                "row_count": 1,
                "execution_time_ms": 18
            }
        else:
            return {
                "data": [{"id": 1, "name": "示例数据"}],
                "row_count": 1,
                "execution_time_ms": 10
            }
    
    def _explain_result(self, result: Dict, original_query: str) -> str:
        """解释结果"""
        return self.llm.explain_result(result, original_query)
    
    def _log_audit(self, user_address: str, sql_query: str, result: Dict):
        """记录审计日志"""
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "user_address": user_address,
            "agent_id": self.agent_id,
            "sql_query": sql_query,
            "result_row_count": result.get("row_count", 0),
            "execution_time_ms": result.get("execution_time_ms", 0)
        }
        
        logger.info(f"审计日志: {json.dumps(audit_log, ensure_ascii=False)}")
        
        # 这里应该将审计日志保存到数据库或文件
        with open(f"audit_log_{self.agent_id}.jsonl", "a") as f:
            f.write(json.dumps(audit_log) + "\n")
    
    def clear_cache(self):
        """清空查询缓存"""
        self.query_cache.clear()
        logger.info("查询缓存已清空")


# 演示函数
def demo_ai_agent():
    """演示AI代理功能"""
    print("="*50)
    print("AI代理演示")
    print("="*50)
    
    # 创建模拟权限管理器
    class MockPermissionManager:
        def verify_permission(self, permission_id, agent_id, operation, table, column):
            return True  # 模拟所有权限都通过
    
    # 创建AI代理
    permission_manager = MockPermissionManager()
    agent = AIAgent(agent_id="demo_agent", permission_manager=permission_manager)
    
    # 测试查询
    test_queries = [
        "帮我分析上个月销售额最高的10个客户",
        "查询客户数量",
        "计算平均订单金额"
    ]
    
    for query in test_queries:
        print(f"\n用户请求: {query}")
        try:
            result = agent.process_request(query, "0xuser123...")
            print(f"SQL查询: {result['sql_query']}")
            print(f"解释: {result['explanation']}")
            print(f"结果: {result['result']['data']}")
        except PermissionError as e:
            print(f"权限错误: {e}")
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)


if __name__ == "__main__":
    demo_ai_agent()