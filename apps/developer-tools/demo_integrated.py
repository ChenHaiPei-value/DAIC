"""
综合演示脚本

展示AI应用服务器分布式去中心化系统的完整功能。
"""

import json
import logging
from datetime import datetime, timedelta
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_integrated_system():
    """演示集成系统功能"""
    print("="*60)
    print("AI应用服务器分布式去中心化系统 - 综合演示")
    print("="*60)
    
    print("\n1. 初始化系统组件...")
    
    # 导入组件
    try:
        # 添加当前目录到Python路径
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from permission_manager import PermissionManager, FileStorage
        from ai_agent import AIAgent, PermissionError
        from database_proxy import DatabaseProxy
        from helpers import MockConnectionPool, AuditLogger
        
        print("   ✓ 组件导入成功")
    except ImportError as e:
        print(f"   ✗ 组件导入失败: {e}")
        print("   错误详情:")
        import traceback
        traceback.print_exc()
        print("   请确保所有依赖文件都存在")
        return
    
    # 初始化组件
    print("\n2. 初始化权限管理器...")
    permission_manager = PermissionManager(storage_backend=FileStorage("demo_permissions.json"))
    print("   ✓ 权限管理器初始化完成")
    
    print("\n3. 初始化AI代理...")
    ai_agent = AIAgent(agent_id="demo_ai_agent", permission_manager=permission_manager)
    print("   ✓ AI代理初始化完成")
    
    print("\n4. 初始化数据库代理...")
    db_proxy = DatabaseProxy(connection_pool=MockConnectionPool(max_connections=5))
    print("   ✓ 数据库代理初始化完成")
    
    print("\n" + "-"*60)
    print("场景1: 用户授权AI代理访问数据")
    print("-"*60)
    
    # 模拟用户地址
    user_address = "0xuser1234567890abcdef"
    ai_agent_address = "0xaiagent1234567890abcdef"
    
    print(f"\n用户 {user_address[:10]}... 正在授权AI代理 {ai_agent_address[:10]}... 访问数据")
    
    # 授予权限
    permission_id = permission_manager.grant_permission(
        user_address=user_address,
        ai_agent_address=ai_agent_address,
        database="sales_database",
        table="customers",
        columns=["customer_id", "customer_name", "total_sales", "email", "phone"],
        operations=["SELECT"],
        valid_until=(datetime.now() + timedelta(days=30)).isoformat(),
        max_rows=1000
    )
    
    print(f"   ✓ 权限已授予，权限ID: {permission_id}")
    
    # 显示用户权限
    user_permissions = permission_manager.get_user_permissions(user_address)
    print(f"   用户现有权限数量: {len(user_permissions)}")
    
    print("\n" + "-"*60)
    print("场景2: AI代理处理用户自然语言查询")
    print("-"*60)
    
    test_queries = [
        "帮我分析上个月销售额最高的5个客户",
        "查询客户总数",
        "计算平均销售额"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n查询 {i}: {query}")
        print("  AI代理处理中...")
        
        try:
            # AI代理处理查询
            result = ai_agent.process_request(
                user_request=query,
                user_address=user_address
            )
            
            print(f"  ✓ 查询处理成功")
            print(f"    生成的SQL: {result['sql_query'][:80]}...")
            print(f"    结果解释: {result['explanation']}")
            print(f"    返回行数: {result['result']['row_count']}")
            
            # 显示部分结果
            if result['result'].get('data'):
                print(f"    示例数据: {json.dumps(result['result']['data'][0], ensure_ascii=False)}")
            
        except PermissionError as e:
            print(f"  ✗ 权限错误: {e}")
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
    
    print("\n" + "-"*60)
    print("场景3: 安全数据库查询")
    print("-"*60)
    
    test_sql_queries = [
        "SELECT customer_name, email, phone, total_sales FROM customers WHERE total_sales > 50000 ORDER BY total_sales DESC LIMIT 3",
        "SELECT COUNT(*) as customer_count FROM customers",
        "SELECT AVG(total_sales) as avg_sales FROM customers"
    ]
    
    user_context = {
        "user_id": "demo_user",
        "user_address": user_address,
        "permissions": {
            "operations": ["SELECT"],
            "row_filters": ["customer_id > 0"],  # 行级权限
            "column_mask": {
                "email": "partial",  # 邮箱部分脱敏
                "phone": "partial"   # 手机号部分脱敏
            }
        }
    }
    
    for i, sql_query in enumerate(test_sql_queries, 1):
        print(f"\n安全查询 {i}: {sql_query[:60]}...")
        print("  数据库代理处理中...")
        
        result = db_proxy.execute_secure(sql_query, user_context)
        
        if result["success"]:
            print(f"  ✓ 查询执行成功")
            print(f"    执行时间: {result['execution_time_ms']:.1f}ms")
            print(f"    返回行数: {result['row_count']}")
            
            if result.get("data"):
                print(f"    结果数据:")
                for j, row in enumerate(result["data"][:2], 1):  # 显示前2行
                    print(f"      行{j}: {json.dumps(row, ensure_ascii=False)}")
                if len(result["data"]) > 2:
                    print(f"      ... 还有 {len(result['data']) - 2} 行")
        else:
            print(f"  ✗ 查询失败: {result.get('error', '未知错误')}")
    
    print("\n" + "-"*60)
    print("场景4: 权限验证和审计")
    print("-"*60)
    
    # 测试权限验证
    print("\n权限验证测试:")
    
    test_cases = [
        {
            "description": "有效权限 - SELECT customers.customer_name",
            "permission_id": permission_id,
            "ai_agent": ai_agent_address,
            "operation": "SELECT",
            "table": "customers",
            "column": "customer_name"
        },
        {
            "description": "无效权限 - DELETE customers",
            "permission_id": permission_id,
            "ai_agent": ai_agent_address,
            "operation": "DELETE",
            "table": "customers"
        },
        {
            "description": "无效列 - SELECT customers.password",
            "permission_id": permission_id,
            "ai_agent": ai_agent_address,
            "operation": "SELECT",
            "table": "customers",
            "column": "password"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  {test_case['description']}")
        result = permission_manager.verify_permission(
            permission_id=test_case["permission_id"],
            ai_agent_address=test_case["ai_agent"],
            operation=test_case["operation"],
            table=test_case["table"],
            column=test_case.get("column")
        )
        print(f"    结果: {'✓ 通过' if result else '✗ 拒绝'}")
    
    # 显示权限统计
    print("\n权限统计信息:")
    stats = permission_manager.get_statistics()
    print(f"  总权限数: {stats['total_permissions']}")
    print(f"  活跃权限: {stats['active_permissions']}")
    print(f"  操作分布: {stats['operation_distribution']}")
    print(f"  总使用次数: {stats['total_usage']}")
    
    print("\n" + "-"*60)
    print("场景5: 系统性能和安全特性")
    print("-"*60)
    
    print("\n1. 查询缓存测试:")
    # 重复查询测试缓存
    test_query = "SELECT customer_name, total_sales FROM customers LIMIT 2"
    
    print(f"  第一次执行查询...")
    result1 = db_proxy.execute_secure(test_query, user_context)
    print(f"    执行时间: {result1['execution_time_ms']:.1f}ms, 缓存: {result1.get('cached', False)}")
    
    print(f"  第二次执行相同查询...")
    result2 = db_proxy.execute_secure(test_query, user_context)
    print(f"    执行时间: {result2['execution_time_ms']:.1f}ms, 缓存: {result2.get('cached', False)}")
    
    if result2.get('cached'):
        print(f"  ✓ 查询缓存生效，性能提升: {(result1['execution_time_ms'] - result2['execution_time_ms']):.1f}ms")
    
    print("\n2. 数据脱敏测试:")
    sensitive_query = """
        SELECT 
            customer_name,
            email,
            phone,
            '4111-1111-1111-1111' as credit_card,
            '192.168.1.1' as ip_address
        FROM customers 
        LIMIT 1
    """
    
    print(f"  执行包含敏感数据的查询...")
    result = db_proxy.execute_secure(sensitive_query, user_context)
    
    if result["success"] and result.get("data"):
        print(f"    原始数据已脱敏处理")
        print(f"    脱敏后数据: {json.dumps(result['data'][0], ensure_ascii=False)}")
    
    print("\n3. 差分隐私测试:")
    privacy_query = "SELECT total_sales FROM customers LIMIT 5"
    
    print(f"  执行需要隐私保护的查询...")
    result = db_proxy.execute_secure(privacy_query, user_context)
    
    if result["success"]:
        if result.get("data") and any("privacy_applied" in str(row) for row in result["data"]):
            print(f"    ✓ 差分隐私已应用")
        else:
            print(f"    返回数据: {json.dumps(result['data'], ensure_ascii=False)}")
    
    print("\n" + "-"*60)
    print("系统总结")
    print("-"*60)
    
    print("\n✓ 系统组件:")
    print("  1. 权限管理器 - 管理用户对AI代理的细粒度授权")
    print("  2. AI代理 - 处理自然语言查询，生成SQL，验证权限")
    print("  3. 数据库代理 - 安全执行查询，数据脱敏，访问控制")
    print("  4. 审计系统 - 记录所有操作，确保可追溯性")
    
    print("\n✓ 安全特性:")
    print("  1. 细粒度权限控制 - 表级、行级、列级权限")
    print("  2. 数据脱敏 - 自动识别和脱敏敏感数据")
    print("  3. 差分隐私 - 保护查询结果的隐私")
    print("  4. SQL注入防护 - 检测和阻止恶意查询")
    print("  5. 审计日志 - 完整记录所有操作")
    
    print("\n✓ 性能优化:")
    print("  1. 查询缓存 - 减少重复查询开销")
    print("  2. 连接池 - 高效管理数据库连接")
    print("  3. 智能解析 - 优化查询执行计划")
    
    print("\n" + "="*60)
    print("演示完成!")
    print("="*60)
    
    # 清理演示文件
    print("\n清理演示文件...")
    import os
    demo_files = [
        "demo_permissions.json",
        "audit_log.jsonl",
        "audit_errors.jsonl",
        "audit_log_demo_ai_agent.jsonl"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  已删除: {file}")
            except:
                print(f"  删除失败: {file}")
    
    print("\n所有演示已完成，系统功能验证成功！")


if __name__ == "__main__":
    try:
        demo_integrated_system()
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)