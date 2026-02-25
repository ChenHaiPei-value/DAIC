# Decentralized AI Commons (DAIC) - 去中心化AI公地

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![GitHub stars](https://img.shields.io/github/stars/daic-org/daic-core)](https://github.com/daic-org/daic-core/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/daic-org/daic-core)](https://github.com/daic-org/daic-core/issues)

## 🌟 项目愿景

**始于大航海时代的东印度公司的公司制，是以掠夺、贩卖奴隶、低成本有限风险、超高的回报形成，而这种掠夺性的以各种变种存在着距今已有400多年...**

DAIC是一个革命性的去中心化AI生态系统，旨在打破数字寡头垄断，构建"全民数字主权"的新范式。我们拒绝需要挖矿耗能的区块链机制，倡导真正的分布式、去中心化资源共享。

## 🎯 核心目标

1. **数据存储分布式去中心化** - 大家一起提供安全的存储芯片
2. **AI应用服务器分布式去中心化** - 不同用户授权给AI，去调用、操作数据库
3. **AI大模型运行的GPU分布式去中心化** - 大家一起提供GPU算力
4. **共创AI应用平台** - AI工程师可以创建大家一起用的且不属于任何人的AI应用
5. **具身智能平台** - 创建具身智能方案，对接原材料供应商、3D打印技术
6. **减少信息不对称** - 最大程度减少信息不对称问题

## 🏗️ 技术架构

### 核心原则
- ❌ **不要挖矿机制** - 拒绝耗能的PoW共识
- ✅ **权益证明** - 使用PoS/DAG等环保共识
- ✅ **存储证明** - 提供存储空间获得奖励
- ✅ **计算证明** - 提供GPU算力获得奖励

### 技术栈
- **分布式存储**: IPFS + Filecoin (存储证明)
- **分布式计算**: Akash Network + Golem Network
- **共识机制**: DAG (有向无环图) + PoS
- **AI框架**: PyTorch + TensorFlow + Hugging Face
- **网络协议**: libp2p + WebRTC
- **容器编排**: Kubernetes + Docker Swarm
- **前端框架**: Next.js + TypeScript + Tailwind CSS

## 📁 项目结构

```
DAIC/
├── core/                    # 核心协议
│   ├── consensus/          # 共识机制 (DAG+PoS)
│   ├── storage/           # 分布式存储协议
│   ├── compute/           # 分布式计算协议
│   └── identity/          # 去中心化身份
├── ai/                     # AI相关
│   ├── models/            # 开源模型
│   ├── training/          # 分布式训练框架
│   ├── inference/         # 推理服务
│   └── agents/            # 智能体框架
├── hardware/               # 硬件相关
│   ├── open-hardware/     # 开源硬件设计
│   ├── embodied-ai/       # 具身智能
│   └── 3d-printing/       # 3D打印集成
├── apps/                   # 应用层
│   ├── marketplace/       # 应用市场
│   ├── developer-tools/   # 开发工具
│   └── user-interface/    # 用户界面
├── governance/             # 治理
│   ├── dao/               # 去中心化自治组织
│   ├── voting/            # 投票机制
│   └── treasury/          # 资金管理
├── docs/                   # 文档
└── website/                # 静态官网 (Vercel部署)
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Docker 20.10+
- Git

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/daic-org/daic-core.git
cd daic-core

# 安装依赖
pip install -r requirements.txt
npm install

# 启动本地开发环境
docker-compose up -d
npm run dev
```

## 📖 文档

- [架构设计](./docs/architecture.md)
- [技术白皮书](./docs/whitepaper.md)
- [API文档](./docs/api/)
- [开发教程](./docs/tutorials/)

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看[贡献指南](./CONTRIBUTING.md)了解如何参与。

### 贡献方式
1. **报告Bug** - 在Issues中提交问题
2. **提交功能请求** - 描述你的想法
3. **提交代码** - 遵循我们的代码规范
4. **改进文档** - 帮助完善文档
5. **分享想法** - 参与讨论

## 📄 许可证

本项目采用 [AGPL-3.0 许可证](./LICENSE) - 查看LICENSE文件了解详情。

## 🌐 官方网站

访问我们的官方网站: [https://13ddao.top](https://13ddao.top) 

## 📞 联系我们

- GitHub Issues: [问题反馈](https://github.com/daic-org/daic-core/issues)
- Discord: [加入社区](https://discord.gg/daic)
- Twitter: [@DAIC_org](https://twitter.com/DAIC_org)
- Email: aicodingquant@sina.com

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和支持者。特别感谢那些敢于挑战传统公司制度，追求更公平数字未来的思想先驱。

---

**"真正的技术革命不仅是技术的进步，更是生产关系的革新。"**