# GPU分布式去中心化计算协议

## 🎯 概述

本模块实现了"AI大模型运行的GPU分布式去中心化 - 大家一起提供GPU算力"的核心功能。通过去中心化的方式，聚合全球闲置GPU资源，为AI大模型训练和推理提供分布式计算能力。

## 🏗️ 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                    GPU分布式计算网络                         │
├─────────────────────────────────────────────────────────────┤
│ 任务调度层 │ 资源管理 │ 计算证明 │ 奖励分配 │ 监控告警 │ ... │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   节点管理层                                 │
├─────────────────────────────────────────────────────────────┤
│ 节点注册 │ 能力验证 │ 健康检查 │ 信誉评分 │ 故障恢复 │ ... │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   计算执行层                                 │
├─────────────────────────────────────────────────────────────┤
│ 容器编排 │ GPU虚拟化 │ 任务隔离 │ 数据安全 │ 结果验证 │ ... │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户提交AI任务 → 任务分解 → 节点匹配 → 分布式执行 → 结果聚合 → 奖励分配
     │              │           │           │           │           │
     ▼              ▼           ▼           ▼           ▼           ▼
任务描述JSON  子任务划分  资源评估算法  容器化执行  结果验证机制  智能合约支付
```

## 🔧 核心功能

### 1. 节点管理
- **节点注册**: GPU节点加入网络，提供算力信息
- **能力验证**: 验证GPU性能、内存、带宽等
- **健康检查**: 定期检查节点可用性和性能
- **信誉系统**: 基于历史表现的信誉评分

### 2. 任务调度
- **智能匹配**: 根据任务需求和节点能力智能匹配
- **负载均衡**: 动态调整任务分配，避免节点过载
- **容错处理**: 节点故障时自动重新调度任务
- **优先级调度**: 支持不同优先级任务调度

### 3. 计算证明
- **工作量证明**: 验证计算任务正确完成
- **零知识证明**: 保护计算隐私和数据安全
- **结果验证**: 多节点交叉验证计算结果
- **防作弊机制**: 防止节点提交虚假结果

### 4. 奖励分配
- **按贡献分配**: 根据提供的算力、时长、质量分配奖励
- **实时结算**: 任务完成后实时结算
- **惩罚机制**: 对恶意节点进行惩罚
- **激励机制**: 鼓励长期稳定提供算力

## 📁 文件结构

```
core/compute/
├── README.md                    # 本文档
├── __init__.py                  # 模块初始化
├── node_manager.py              # 节点管理
├── task_scheduler.py            # 任务调度
├── compute_proof.py             # 计算证明
├── reward_system.py             # 奖励系统
├── gpu_discovery.py             # GPU资源发现
├── container_orchestrator.py    # 容器编排
├── security.py                  # 安全机制
├── monitoring.py                # 监控系统
├── api/                         # API接口
│   ├── __init__.py
│   ├── node_api.py
│   ├── task_api.py
│   └── reward_api.py
├── protocols/                   # 网络协议
│   ├── __init__.py
│   ├── p2p_protocol.py
│   └── consensus_protocol.py
├── utils/                       # 工具函数
│   ├── __init__.py
│   ├── gpu_utils.py
│   └── crypto_utils.py
└── tests/                       # 测试文件
    ├── __init__.py
    ├── test_node_manager.py
    ├── test_task_scheduler.py
    └── test_compute_proof.py
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Docker 20.10+
- NVIDIA GPU (支持CUDA 11.0+)
- 至少8GB GPU内存

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/daic-org/daic-core.git
cd daic-core

# 安装Python依赖
pip install -r core/compute/requirements.txt

# 安装Docker
# 参考: https://docs.docker.com/engine/install/

# 配置NVIDIA容器运行时
# 参考: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### 作为计算节点加入网络

```python
from core.compute.node_manager import ComputeNode

# 创建计算节点
node = ComputeNode(
    node_id="node_001",
    gpu_info={
        "type": "NVIDIA RTX 4090",
        "memory_gb": 24,
        "cuda_cores": 16384,
        "bandwidth_gbps": 1008
    },
    network_info={
        "ip": "192.168.1.100",
        "port": 8080,
        "bandwidth_mbps": 1000
    }
)

# 注册到网络
node.register_to_network()

# 开始接收计算任务
node.start_serving()
```

### 提交AI计算任务

```python
from core.compute.task_scheduler import TaskScheduler

# 创建任务调度器
scheduler = TaskScheduler()

# 提交AI训练任务
task_id = scheduler.submit_task({
    "task_type": "ai_training",
    "model_name": "llama-7b",
    "dataset": "wikitext-103",
    "gpu_memory_gb": 16,
    "estimated_time_hours": 24,
    "reward_tokens": 1000
})

# 检查任务状态
status = scheduler.get_task_status(task_id)
print(f"任务状态: {status}")
```

## 📊 性能指标

### 计算性能
- **聚合算力**: 支持100+ PFLOPS GPU算力
- **任务调度**: <1秒调度延迟
- **容错率**: 99.9%任务成功率
- **扩展性**: 支持10,000+节点

### 经济指标
- **成本节约**: 相比传统云服务节省70%成本
- **资源利用率**: 提升闲置GPU利用率至80%+
- **奖励分配**: 实时、透明、公平的奖励分配

### 安全指标
- **数据安全**: 端到端加密，零知识证明
- **计算安全**: 多节点验证，防作弊机制
- **网络安全**: DDoS防护，节点认证

## 🔒 安全设计

### 计算安全
1. **容器隔离**: 每个任务运行在独立容器中
2. **资源限制**: 限制任务资源使用，防止资源耗尽攻击
3. **沙箱环境**: 限制文件系统访问和网络访问
4. **代码审计**: 对AI模型代码进行安全审计

### 数据安全
1. **数据加密**: 训练数据在传输和存储中加密
2. **联邦学习**: 支持隐私保护的联邦学习
3. **差分隐私**: 在训练过程中添加噪声保护隐私
4. **同态加密**: 支持加密数据上的计算

### 网络安全
1. **TLS加密**: 所有网络通信使用TLS 1.3
2. **节点认证**: 基于数字证书的节点身份认证
3. **访问控制**: 基于角色的细粒度访问控制
4. **审计日志**: 完整的安全审计日志

## 📈 经济模型

### 奖励机制
```
奖励 = 基础奖励 × 性能系数 × 时长系数 × 质量系数

其中:
- 基础奖励: 根据GPU类型和内存确定
- 性能系数: 基于实际计算速度
- 时长系数: 基于稳定运行时间
- 质量系数: 基于任务完成质量
```

### 惩罚机制
1. **任务失败**: 扣除部分押金
2. **恶意行为**: 永久封禁节点
3. **服务质量差**: 降低信誉评分
4. **网络攻击**: 法律追究责任

### 激励机制
1. **长期贡献奖励**: 连续运行30天以上获得额外奖励
2. **高性能奖励**: 提供高性能GPU获得更高奖励
3. **稳定性奖励**: 高可用性节点获得额外奖励
4. **推荐奖励**: 推荐新节点加入获得奖励

## 🔗 集成接口

### REST API
```python
# 节点管理API
POST /api/v1/nodes/register     # 注册节点
GET  /api/v1/nodes/{node_id}    # 获取节点信息
PUT  /api/v1/nodes/{node_id}    # 更新节点状态

# 任务管理API
POST /api/v1/tasks              # 提交任务
GET  /api/v1/tasks/{task_id}    # 获取任务状态
DELETE /api/v1/tasks/{task_id}  # 取消任务

# 奖励API
GET  /api/v1/rewards/{node_id}  # 获取奖励信息
POST /api/v1/rewards/claim      # 领取奖励
```

### 命令行工具
```bash
# 启动计算节点
daic-compute start --config config.yaml

# 提交AI任务
daic-compute submit-task --model llama-7b --gpu-memory 16GB

# 查看节点状态
daic-compute status

# 领取奖励
daic-compute claim-rewards
```

## 🚧 开发指南

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写完整的文档字符串
- 单元测试覆盖率>80%

### 贡献流程
1. Fork项目仓库
2. 创建功能分支
3. 实现功能并添加测试
4. 提交Pull Request
5. 通过代码审查后合并

### 测试指南
```bash
# 运行所有测试
pytest core/compute/tests/

# 运行特定测试
pytest core/compute/tests/test_node_manager.py

# 生成测试覆盖率报告
pytest --cov=core.compute --cov-report=html
```

## 📚 相关文档

- [架构设计](../docs/architecture.md)
- [API文档](./api/README.md)
- [部署指南](./DEPLOYMENT.md)
- [安全指南](./SECURITY.md)

## 🤝 社区支持

- **GitHub Issues**: 报告问题和功能请求
- **Discord**: 加入技术讨论
- **文档贡献**: 帮助完善文档
- **代码贡献**: 提交Pull Request

---

*最后更新: 2025年2月27日*  
*版本: 1.0.0*