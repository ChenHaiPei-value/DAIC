#!/usr/bin/env python3
"""
GPU分布式去中心化计算演示运行脚本

运行演示场景，展示DAIC GPU分布式计算系统的功能。
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """主函数"""
    print("="*70)
    print("DAIC GPU分布式去中心化计算系统演示")
    print("="*70)
    print("\n系统概述:")
    print("  • 去中心化GPU算力共享网络")
    print("  • AI大模型分布式训练和推理")
    print("  • 公平透明的奖励分配机制")
    print("  • 安全可靠的计算证明系统")
    
    try:
        # 导入演示模块
        from core.compute.demo import (
            demo_scenario_1,
            demo_scenario_2,
            demo_scenario_3
        )
        
        print("\n" + "="*70)
        print("开始演示...")
        print("="*70)
        
        # 运行演示场景1
        print("\n>>> 运行演示场景1: 单个AI训练任务")
        scheduler1, reward_system1 = await demo_scenario_1()
        
        # 运行演示场景2
        print("\n>>> 运行演示场景2: 多个并发任务")
        scheduler2, reward_system2 = await demo_scenario_2()
        
        # 运行演示场景3
        print("\n>>> 运行演示场景3: 节点网络统计")
        await demo_scenario_3()
        
        print("\n" + "="*70)
        print("演示完成!")
        print("="*70)
        
        # 显示系统总结
        print("\n系统功能总结:")
        print("1. ✅ 节点管理: 支持GPU节点的注册、验证和监控")
        print("2. ✅ 任务调度: 智能任务分解和节点匹配")
        print("3. ✅ 奖励系统: 公平透明的奖励分配机制")
        print("4. ✅ 容错处理: 节点故障自动重新调度")
        print("5. ✅ 扩展性: 支持大规模节点网络")
        
        print("\n技术特点:")
        print("  • 去中心化架构: 无单点故障，抗审查")
        print("  • 隐私保护: 支持联邦学习和差分隐私")
        print("  • 经济激励: 按贡献分配奖励，激励参与")
        print("  • 开放标准: 兼容主流AI框架和硬件")
        
        print("\n应用场景:")
        print("  • AI大模型训练: 分布式训练LLaMA、GPT等模型")
        print("  • AI推理服务: 提供实时推理API服务")
        print("  • 数据处理: 大规模数据预处理和分析")
        print("  • 科学研究: 分布式科学计算")
        
        print("\n下一步:")
        print("1. 查看详细文档: docs/gpu_distributed_computing.md")
        print("2. 运行完整测试: pytest core/compute/tests/")
        print("3. 部署测试网络: 参考部署指南")
        print("4. 加入社区: https://discord.gg/daic")
        
    except ImportError as e:
        print(f"\n错误: 无法导入演示模块 - {e}")
        print("请确保在项目根目录运行此脚本")
        return 1
    except Exception as e:
        print(f"\n错误: 演示运行失败 - {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # 运行异步主函数
    exit_code = asyncio.run(main())
    sys.exit(exit_code)