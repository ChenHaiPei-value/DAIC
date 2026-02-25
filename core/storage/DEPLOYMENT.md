# DAIC分布式存储系统部署指南

## 📋 概述

本文档提供了DAIC分布式存储系统的部署和配置指南。系统设计为模块化、可扩展的分布式存储解决方案。

## 🚀 快速开始

### 环境要求

#### 系统要求
- **操作系统**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+ (WSL2)
- **Python**: 3.8+
- **内存**: 至少4GB RAM
- **存储**: 至少10GB可用空间
- **网络**: 稳定的互联网连接

#### Python依赖
```bash
# 核心依赖
pip install cryptography numpy

# 可选依赖（用于高级功能）
pip install aiohttp websockets redis
```

### 安装步骤

#### 1. 克隆代码库
```bash
git clone https://github.com/daic-org/daic-storage.git
cd daic-storage
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 验证安装
```bash
python -c "from core.storage import DAICStorageClient; print('安装成功!')"
```

## 🔧 配置

### 客户端配置

创建配置文件 `config.yaml`:

```yaml
# DAIC存储客户端配置
storage:
  # 本地存储设置
  local_storage_dir: "~/.daic/storage"
  cache_size: 1000  # 缓存条目数
  
  # 分片设置
  chunk_size: 1048576  # 1MB分片
  data_shards: 3       # 数据分片数
  parity_shards: 2     # 校验分片数
  
  # 节点选择设置
  min_reputation: 0.6   # 最小信誉评分
  max_latency: 500.0    # 最大延迟(ms)
  
  # 存储证明设置
  proof_validity_period: 3600  # 证明有效期(秒)
  
  # 网络设置
  network_timeout: 30   # 网络超时(秒)
  max_retries: 3        # 最大重试次数
  
  # 加密设置
  encryption_algorithm: "aes-256-gcm"
  hash_algorithm: "sha256"
  
  # 日志设置
  log_level: "INFO"
  log_file: "~/.daic/logs/storage.log"
```

### 环境变量配置

```bash
# 基本配置
export DAIC_STORAGE_DIR="$HOME/.daic/storage"
export DAIC_LOG_LEVEL="INFO"

# 网络配置
export DAIC_NETWORK_TIMEOUT="30"
export DAIC_MAX_RETRIES="3"

# 安全配置
export DAIC_ENCRYPTION_KEY="your-encryption-key-here"
```

## 🏗️ 部署架构

### 单节点部署

适用于开发和测试环境：

```python
from core.storage import DAICStorageClient

# 创建客户端
client = DAICStorageClient({
    'local_storage_dir': '/path/to/storage',
    'data_shards': 3,
    'parity_shards': 2
})

# 添加本地节点
client.add_test_nodes(3)

# 开始使用
file_id = client.upload_file("/path/to/file.txt")
```

### 多节点部署

#### 节点配置

创建节点配置文件 `node_config.yaml`:

```yaml
# 存储节点配置
node:
  # 节点标识
  node_id: "node-001"
  node_name: "Storage Node 1"
  
  # 网络设置
  host: "0.0.0.0"
  port: 8000
  public_address: "your-public-ip:8000"
  
  # 存储设置
  storage_path: "/data/daic/storage"
  max_storage_gb: 1000
  min_free_space_gb: 10
  
  # 性能设置
  max_connections: 100
  max_bandwidth_mbps: 1000
  max_files_per_dir: 10000
  
  # 安全设置
  ssl_enabled: true
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
  
  # 监控设置
  metrics_enabled: true
  metrics_port: 9090
  health_check_interval: 60
```

#### 启动节点

```bash
# 启动存储节点
python -m core.storage.node --config node_config.yaml

# 或使用Docker
docker run -d \
  --name daic-storage-node \
  -p 8000:8000 \
  -p 9090:9090 \
  -v /data/daic/storage:/storage \
  -v /path/to/config:/config \
  daic/storage-node:latest
```

### 集群部署

#### 使用Docker Compose

创建 `docker-compose.yaml`:

```yaml
version: '3.8'

services:
  # 存储节点1
  storage-node-1:
    image: daic/storage-node:latest
    container_name: daic-storage-node-1
    ports:
      - "8001:8000"
      - "9091:9090"
    volumes:
      - ./data/node1:/storage
      - ./config/node1.yaml:/config/config.yaml
    environment:
      - NODE_ID=node-001
      - NODE_NAME=Storage Node 1
    networks:
      - daic-network
    restart: unless-stopped

  # 存储节点2
  storage-node-2:
    image: daic/storage-node:latest
    container_name: daic-storage-node-2
    ports:
      - "8002:8000"
      - "9092:9090"
    volumes:
      - ./data/node2:/storage
      - ./config/node2.yaml:/config/config.yaml
    environment:
      - NODE_ID=node-002
      - NODE_NAME=Storage Node 2
    networks:
      - daic-network
    restart: unless-stopped

  # 存储节点3
  storage-node-3:
    image: daic/storage-node:latest
    container_name: daic-storage-node-3
    ports:
      - "8003:8000"
      - "9093:9090"
    volumes:
      - ./data/node3:/storage
      - ./config/node3.yaml:/config/config.yaml
    environment:
      - NODE_ID=node-003
      - NODE_NAME=Storage Node 3
    networks:
      - daic-network
    restart: unless-stopped

  # 客户端服务
  storage-client:
    image: daic/storage-client:latest
    container_name: daic-storage-client
    ports:
      - "8080:8080"
    volumes:
      - ./client/config.yaml:/config/config.yaml
      - ./client/data:/data
    environment:
      - STORAGE_NODES=node-001:8001,node-002:8002,node-003:8003
    networks:
      - daic-network
    depends_on:
      - storage-node-1
      - storage-node-2
      - storage-node-3
    restart: unless-stopped

  # 监控服务
  monitoring:
    image: prom/prometheus:latest
    container_name: daic-monitoring
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/data:/prometheus
    networks:
      - daic-network
    restart: unless-stopped

networks:
  daic-network:
    driver: bridge
```

#### 启动集群

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🔒 安全配置

### TLS/SSL配置

```yaml
# SSL配置示例
ssl:
  enabled: true
  # 证书文件
  cert_file: "/path/to/fullchain.pem"
  key_file: "/path/to/privkey.pem"
  # 可选：CA证书
  ca_file: "/path/to/ca.pem"
  # 协议版本
  protocol: "TLSv1.3"
  # 密码套件
  ciphers: "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
```

### 访问控制

```yaml
# 访问控制配置
access_control:
  # 认证方式
  authentication:
    enabled: true
    method: "jwt"  # jwt, api_key, oauth2
    jwt_secret: "your-jwt-secret"
    
  # 授权规则
  authorization:
    enabled: true
    rules:
      - path: "/api/v1/files/*"
        methods: ["GET", "POST", "DELETE"]
        roles: ["user", "admin"]
      - path: "/api/v1/admin/*"
        methods: ["*"]
        roles: ["admin"]
```

### 数据加密

```python
from core.storage import DAICStorageClient
from cryptography.fernet import Fernet

# 生成加密密钥
key = Fernet.generate_key()

# 使用加密密钥创建客户端
client = DAICStorageClient({
    'encryption_key': key,
    'encryption_algorithm': 'aes-256-gcm'
})

# 上传加密文件
file_id = client.upload_file(
    "/path/to/sensitive/file.txt",
    encryption_key=key
)
```

## 📊 监控和日志

### 监控配置

创建Prometheus配置 `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'daic-storage'
    static_configs:
      - targets:
        - 'storage-node-1:9090'
        - 'storage-node-2:9090'
        - 'storage-node-3:9090'
        - 'storage-client:9090'
    
  - job_name: 'daic-system'
    static_configs:
      - targets:
        - 'node-exporter:9100'
        - 'cadvisor:8080'
```

### 日志配置

```python
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/daic/storage.log',
            'formatter': 'standard',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
    },
    'loggers': {
        'core.storage': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 健康检查

```bash
# 检查节点健康状态
curl http://localhost:8000/health

# 检查存储状态
curl http://localhost:8000/storage/status

# 检查网络连接
curl http://localhost:8000/network/status
```

## 🔄 备份和恢复

### 数据备份

```python
from core.storage import DAICStorageClient
import json

def backup_metadata(client, backup_dir):
    """备份元数据"""
    files = client.list_files()
    
    backup_data = {
        'timestamp': time.time(),
        'file_count': len(files),
        'files': files
    }
    
    backup_file = os.path.join(backup_dir, f"backup_{int(time.time())}.json")
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    return backup_file

def restore_metadata(client, backup_file):
    """恢复元数据"""
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    # 实现恢复逻辑
    # ...
```

### 自动化备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/daic"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR/$DATE"

# 备份元数据
python -c "
from core.storage import DAICStorageClient
client = DAICStorageClient()
files = client.list_files()
import json
with open('$BACKUP_DIR/$DATE/metadata.json', 'w') as f:
    json.dump(files, f)
"

# 备份配置文件
cp /etc/daic/config.yaml "$BACKUP_DIR/$DATE/"

# 压缩备份
tar -czf "$BACKUP_DIR/daic_backup_$DATE.tar.gz" -C "$BACKUP_DIR/$DATE" .

# 清理旧备份（保留最近7天）
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR/daic_backup_$DATE.tar.gz"
```

## 🚨 故障排除

### 常见问题

#### 1. 节点无法启动
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 检查日志
tail -f /var/log/daic/storage.log

# 检查依赖
python -c "import cryptography; print(cryptography.__version__)"
```

#### 2. 上传失败
```python
# 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查网络连接
import socket
socket.create_connection(("storage-node", 8000), timeout=5)
```

#### 3. 下载失败
```bash
# 检查存储空间
df -h /data/daic/storage

# 检查文件权限
ls -la /data/daic/storage/

# 检查防火墙
sudo ufw status
```

### 性能调优

#### 调整分片大小
```python
# 根据文件大小动态调整分片大小
client = DAICStorageClient({
    'chunk_size': 1024 * 1024,  # 1MB for large files
    # 或
    'chunk_size': 64 * 1024,    # 64KB for small files
})
```

#### 优化网络设置
```python
client = DAICStorageClient({
    'network_timeout': 60,      # 增加超时时间
    'max_retries': 5,           # 增加重试次数
    'max_latency': 1000,        # 增加最大延迟
})
```

#### 调整缓存大小
```python
client = DAICStorageClient({
    'cache_size': 5000,         # 增加缓存大小
})

# 定期清理缓存
client.clear_cache()
```

## 📈 扩展和升级

### 水平扩展

#### 添加新节点
1. 准备新服务器
2. 安装DAIC存储节点
3. 配置节点加入现有集群
4. 更新客户端配置

#### 负载均衡
```yaml
# 使用负载均衡器
load_balancer:
  type: "nginx"  # 或 haproxy, traefik
  upstreams:
    - "storage-node-1:8000"
    - "storage-node-2:8000"
    - "storage-node-3:8000"
  health_check: "/health"
```

### 垂直扩展

#### 升级硬件
- 增加存储容量
- 增加内存
- 升级CPU
- 优化网络带宽

#### 软件升级
```bash
# 备份当前版本
cp -r /opt/daic /opt/daic_backup_$(date +%Y%m%d)

# 停止服务
systemctl stop daic-storage

# 升级软件
pip install --upgrade daic-storage

# 启动服务
systemctl start daic-storage

# 验证升级
systemctl status daic-storage
```

## 🤝 社区和支持

### 获取帮助
- **文档**: https://docs.daic.org/storage
- **GitHub**: https://github.com/daic-org/daic-storage
- **论坛**: https://forum.daic.org
- **Discord**: https://discord.gg/daic

### 报告问题
```bash
# 收集调试信息
python -m core.storage.debug --collect

# 提交Issue
# 包括：版本号、错误日志、复现步骤、系统信息
```

### 贡献代码
1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

---

*最后更新: 2026年2月26日*  
*版本: 1.0.0*