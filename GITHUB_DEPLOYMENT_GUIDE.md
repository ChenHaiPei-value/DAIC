# GitHub 部署指南

## 📋 准备工作

### 1. 安装Git
如果还没有安装Git，请先安装：
- **Windows**: 下载并安装 [Git for Windows](https://gitforwindows.org/)
- **macOS**: `brew install git`
- **Linux**: `sudo apt-get install git` (Ubuntu/Debian) 或 `sudo yum install git` (CentOS/RHEL)

### 2. 配置Git
```bash
# 设置用户名
git config --global user.name "您的用户名"

# 设置邮箱
git config --global user.email "您的邮箱@example.com"

# 设置默认分支名
git config --global init.defaultBranch main
```

### 3. 创建GitHub账户
如果还没有GitHub账户，请访问 [GitHub.com](https://github.com) 注册。

## 🚀 推送到GitHub

### 步骤1: 在GitHub上创建新仓库
1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `daic-core` (或您喜欢的名称)
   - **Description**: `Decentralized AI Commons - Core Protocol`
   - **Visibility**: Public (推荐)
   - **Initialize with README**: 不要勾选（我们已经有了README）
4. 点击 "Create repository"

### 步骤2: 本地Git初始化
打开终端/命令提示符，执行以下命令：

```bash
# 进入项目目录
cd "c:\Users\aicod\Desktop\DAI\DAIC"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "初始提交: Decentralized AI Commons 完整项目"

# 添加远程仓库
# 将 YOUR_USERNAME 替换为您的GitHub用户名
# 将 REPO_NAME 替换为您的仓库名
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 推送到GitHub
git push -u origin main
```

### 步骤3: 设置分支保护（可选但推荐）
1. 在GitHub仓库页面，点击 "Settings" → "Branches"
2. 在 "Branch protection rules" 部分，点击 "Add rule"
3. 设置规则：
   - **Branch name pattern**: `main`
   - **Require pull request reviews before merging**: 启用
   - **Require status checks to pass before merging**: 启用
   - **Include administrators**: 启用
4. 点击 "Create"

## 🌐 子仓库策略

DAIC项目建议使用多个子仓库。以下是推荐的仓库结构：

### 主仓库
- **daic-core**: 核心协议和文档 (当前项目)

### 子仓库（建议后续创建）
1. **daic-storage**: 分布式存储协议
2. **daic-compute**: 分布式计算协议
3. **daic-ai**: AI框架和模型
4. **daic-hardware**: 开源硬件设计
5. **daic-governance**: 治理系统
6. **daic-website**: 官方网站

### 创建子仓库的步骤
```bash
# 克隆主仓库
git clone https://github.com/daic-org/daic-core.git

# 创建子模块（以storage为例）
cd daic-core
git submodule add https://github.com/daic-org/daic-storage.git core/storage

# 更新子模块
git submodule update --init --recursive
```

## 🔧 GitHub Actions 自动化

### 创建CI/CD工作流
在 `.github/workflows/ci.yml` 中添加：

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest
    
  build-website:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd website
        npm ci
    
    - name: Build website
      run: |
        cd website
        npm run build
```

## 📖 GitHub Pages 部署

### 部署文档网站
1. 在仓库设置中启用 GitHub Pages
2. 选择 `main` 分支和 `/docs` 文件夹
3. 访问 `https://YOUR_USERNAME.github.io/daic-core`

### 自定义域名（可选）
1. 在仓库设置 → Pages → Custom domain
2. 输入您的域名（如 `docs.daic.org`）
3. 在域名注册商处添加CNAME记录

## 🤝 协作工作流

### 标准Git工作流
```bash
# 1. Fork仓库（贡献者）
# 在GitHub上点击Fork按钮

# 2. 克隆fork的仓库
git clone https://github.com/YOUR_USERNAME/daic-core.git
cd daic-core

# 3. 添加上游仓库
git remote add upstream https://github.com/daic-org/daic-core.git

# 4. 创建功能分支
git checkout -b feature/amazing-feature

# 5. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 6. 推送到fork的仓库
git push origin feature/amazing-feature

# 7. 创建Pull Request
# 在GitHub上点击 "Compare & pull request"
```

### 代码审查流程
1. **创建PR**: 描述更改内容和原因
2. **自动检查**: CI/CD流水线自动运行测试
3. **代码审查**: 至少需要2名核心贡献者批准
4. **合并代码**: 所有检查通过后合并

## 🏷️ 版本发布

### 创建发布版本
```bash
# 1. 更新版本号
# 在 package.json 中更新版本

# 2. 创建发布分支
git checkout -b release/v1.0.0

# 3. 更新CHANGELOG.md
# 4. 提交更改
git add .
git commit -m "chore: 发布 v1.0.0"

# 5. 创建标签
git tag -a v1.0.0 -m "版本 1.0.0"

# 6. 推送到GitHub
git push origin release/v1.0.0
git push origin v1.0.0
```

### 在GitHub上创建Release
1. 点击 "Releases" → "Draft a new release"
2. 选择标签 `v1.0.0`
3. 填写发布说明
4. 上传构建产物（可选）
5. 点击 "Publish release"

## 🔒 安全设置

### 启用安全功能
1. **漏洞警报**: Settings → Security & analysis → Enable vulnerability alerts
2. **依赖图**: Settings → Security & analysis → Enable dependency graph
3. **Dependabot**: Settings → Security & analysis → Enable Dependabot security updates

### 分支保护
- 要求PR审查
- 要求状态检查通过
- 要求线性历史
- 限制推送权限

## 📊 社区管理

### 启用社区功能
1. **Issues模板**: 创建 `.github/ISSUE_TEMPLATE/`
2. **PR模板**: 创建 `.github/PULL_REQUEST_TEMPLATE.md`
3. **行为准则**: 创建 `CODE_OF_CONDUCT.md`
4. **贡献指南**: 已有 `CONTRIBUTING.md`

### 社区指标
- **Stars数量**: 项目受欢迎程度
- **Forks数量**: 项目被复制的次数
- **Issues/PRs**: 社区活跃度
- **贡献者数量**: 项目健康度

## 🚨 故障排除

### 常见问题

#### 1. 推送被拒绝
```bash
# 先拉取最新更改
git pull origin main

# 解决冲突后重新推送
git push origin main
```

#### 2. 子模块问题
```bash
# 初始化子模块
git submodule update --init --recursive

# 更新子模块
git submodule update --remote
```

#### 3. 大文件问题
```bash
# 安装git-lfs
git lfs install

# 跟踪大文件
git lfs track "*.zip"
git lfs track "*.bin"
```

## 📞 支持资源

### GitHub文档
- [GitHub Guides](https://guides.github.com/)
- [GitHub Learning Lab](https://lab.github.com/)
- [GitHub Community Forum](https://github.community/)

### 工具推荐
- **Git GUI**: [GitHub Desktop](https://desktop.github.com/)
- **CLI工具**: [GitHub CLI](https://cli.github.com/)
- **IDE集成**: VS Code Git扩展

### 社区支持
- **Discord**: https://discord.gg/daic
- **GitHub Discussions**: 在仓库中启用
- **邮件列表**: contact@daic.org

---

*最后更新: 2025年2月25日*  
*版本: 1.0.0*

**注意**: 本指南假设您已经具备基本的Git和GitHub知识。如果需要更多帮助，请参考官方文档或联系社区支持。