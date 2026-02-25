# 贡献指南

感谢您对Decentralized AI Commons (DAIC)项目的关注！我们欢迎所有形式的贡献，无论是代码、文档、设计还是想法。

## 📋 贡献方式

### 1. 报告Bug
- 在GitHub Issues中提交问题
- 描述清晰的问题现象、复现步骤和期望结果
- 提供环境信息（操作系统、版本等）
- 如果可能，提供日志或截图

### 2. 提交功能请求
- 描述你的想法和需求场景
- 说明为什么这个功能对项目重要
- 如果有技术方案建议，欢迎提出

### 3. 提交代码
- Fork项目到你的GitHub账户
- 创建功能分支 (`git checkout -b feature/amazing-feature`)
- 提交更改 (`git commit -m 'Add some amazing feature'`)
- 推送到分支 (`git push origin feature/amazing-feature`)
- 创建Pull Request

### 4. 改进文档
- 修正错别字和语法错误
- 补充缺失的文档
- 改进文档结构和可读性
- 添加示例代码和教程

### 5. 分享想法
- 参与GitHub Discussions讨论
- 在社区中分享你的见解
- 帮助回答其他用户的问题

## 🛠️ 开发环境设置

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

# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖
npm install

# 启动开发环境
docker-compose up -d
npm run dev
```

## 📝 代码规范

### Python代码规范
- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用isort进行import排序
- 使用mypy进行类型检查

```bash
# 安装开发工具
pip install black isort mypy

# 格式化代码
black .
isort .

# 类型检查
mypy .
```

### JavaScript/TypeScript代码规范
- 使用ESLint进行代码检查
- 使用Prettier进行代码格式化
- 遵循TypeScript最佳实践

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format
```

### 提交信息规范
使用约定式提交（Conventional Commits）：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具变动

示例：
```
feat: 添加分布式存储协议
fix: 修复身份验证问题
docs: 更新API文档
```

## 🧪 测试要求

### 单元测试
- 为新功能编写单元测试
- 测试覆盖率不低于80%
- 使用pytest进行Python测试
- 使用Jest进行JavaScript测试

### 集成测试
- 测试组件间的集成
- 测试API接口
- 测试分布式功能

### 运行测试
```bash
# Python测试
pytest

# JavaScript测试
npm test

# 所有测试
npm run test:all
```

## 🔍 代码审查流程

1. **创建Pull Request**
   - 确保代码符合规范
   - 添加适当的测试
   - 更新相关文档

2. **代码审查**
   - 至少需要2名核心贡献者审查
   - 审查重点：代码质量、安全性、性能
   - 可能需要多次修改和讨论

3. **合并代码**
   - 所有测试必须通过
   - 获得必要的批准
   - 由核心维护者合并

## 🏛️ 项目治理

### 决策流程
1. **提案阶段** - 在GitHub Discussions中提出想法
2. **讨论阶段** - 社区讨论和反馈
3. **草案阶段** - 形成具体方案
4. **投票阶段** - 社区投票决定
5. **实施阶段** - 执行通过的方案

### 投票机制
- 使用基于代币的治理投票
- 重大决策需要超过66%的赞成票
- 投票期通常为7天

## 🎖️ 贡献者奖励

### 奖励机制
1. **代码贡献** - 根据代码质量和重要性获得代币奖励
2. **文档贡献** - 根据文档质量和实用性获得奖励
3. **社区贡献** - 帮助回答问题、组织活动等获得奖励
4. **安全漏洞报告** - 根据漏洞严重程度获得奖励

### 贡献者等级
- **初级贡献者** - 首次贡献者
- **活跃贡献者** - 持续贡献3个月以上
- **核心贡献者** - 对项目有重大贡献
- **维护者** - 负责特定模块的维护

## 📚 学习资源

### 项目相关
- [架构设计文档](./docs/architecture.md)
- [技术白皮书](./docs/whitepaper.md)
- [API文档](./docs/api/)
- [开发教程](./docs/tutorials/)

### 技术学习
- [分布式系统原理](https://pdos.csail.mit.edu/6.824/)
- [区块链技术指南](https://blockchain.mit.edu/)
- [AI/ML基础知识](https://www.deeplearning.ai/)
- [开源硬件设计](https://www.oshwa.org/)

## 🤔 常见问题

### Q: 我是新手，从哪里开始？
A: 建议从文档改进或简单的bug修复开始，熟悉项目结构和开发流程。

### Q: 如何获得帮助？
A: 可以在GitHub Discussions提问，或者在Discord社区寻求帮助。

### Q: 贡献有报酬吗？
A: 是的，根据贡献的质量和重要性，可以获得项目代币奖励。

### Q: 需要签署CLA吗？
A: 是的，首次贡献需要签署贡献者许可协议（CLA）。

## 📞 联系我们

- GitHub Issues: [问题反馈](https://github.com/daic-org/daic-core/issues)
- GitHub Discussions: [讨论区](https://github.com/daic-org/daic-core/discussions)
- Discord: [加入社区](https://discord.gg/daic)
- Email: contributors@daic.org

---

**感谢您的贡献！让我们一起构建更公平的数字未来。**