# DAIC 分布式存储系统

## 📖 概述

DAIC分布式存储系统是一个去中心化的、无需信任的存储网络，结合了IPFS、Filecoin和Sia的最佳特性，但移除了代币激励的复杂性。系统设计目标是提供安全、高效、可靠的分布式存储服务。

## 🎯 设计目标

### 核心目标
1. **完全去中心化** - 无中心控制节点
2. **数据持久性** - 99.999999%的数据持久性
3. **高可用性** - 99.99%的服务可用性
4. **隐私保护** - 端到端加密和零知识证明
5. **成本效益** - 比中心化云存储便宜50-80%

### 技术目标
- 支持EB级存储容量
- 平均读写速度 > 100MB/s
- 数据恢复时间 < 5分钟
- 支持千万级文件并发访问

## 🏗️ 系统架构

### 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                     客户端层 (Client Layer)                   │
├─────────────────────────────────────────────────────────────┤
│  文件上传 │ 文件下载 │ 文件管理 │ 加密/解密 │ 分片/重组      │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    存储协议层 (Storage Protocol)              │
├─────────────────────────────────────────────────────────────┤
│  存储证明 │ 数据冗余 │ 节点发现 │ 负载均衡 │ 故障转移        │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    网络层 (Network Layer)                    │
├─────────────────────────────────────────────────────────────┤
│  P2P网络 │ 消息路由 │ 节点通信 │ 数据同步 │ 网络拓扑         │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    存储节点层 (Storage Nodes)                 │
├─────────────────────────────────────────────────────────────┤
│  数据存储 │ 存储证明 │ 心跳检测 │ 资源管理 │ 奖励计算         │
└─────────────────────────────────────────────────────────────┘
```

### 组件说明

#### 1. 客户端 (Client)
- **文件处理**: 分片、加密、哈希计算
- **元数据管理**: 文件信息、分片位置、访问权限
- **缓存系统**: 本地缓存加速访问

#### 2. 存储协议 (Storage Protocol)
- **存储证明**: 零知识存储证明 (zk-SNARKs)
- **数据冗余**: 纠删码 (Erasure Coding) 3+2配置
- **节点选择**: 基于信誉和可用性的智能选择

#### 3. 网络层 (Network Layer)
- **P2P发现**: Kademlia DHT节点发现
- **消息协议**: libp2p消息传递
- **数据同步**: 基于Merkle树的数据同步

#### 4. 存储节点 (Storage Nodes)
- **数据存储**: 本地文件系统或对象存储
- **证明生成**: 定期生成存储证明
- **资源管理**: 存储空间、带宽、计算资源管理

## 🔧 核心技术

### 1. 数据分片和加密

#### 分片策略
```python
class DataSharding:
    """数据分片管理器"""
    
    def shard_data(self, data, redundancy=3):
        """
        将数据分片并添加冗余
        
        Args:
            data: 原始数据
            redundancy: 冗余因子 (默认3)
        
        Returns:
            shards: 数据分片列表
            metadata: 分片元数据
        """
        # 1. 数据加密
        encrypted_data = self.encrypt_data(data)
        
        # 2. 应用纠删码
        shards = self.erasure_code(encrypted_data, redundancy)
        
        # 3. 计算分片哈希
        shard_hashes = [hashlib.sha256(shard).hexdigest() for shard in shards]
        
        # 4. 生成元数据
        metadata = {
            'original_size': len(data),
            'encrypted_size': len(encrypted_data),
            'shard_count': len(shards),
            'redundancy': redundancy,
            'shard_hashes': shard_hashes,
            'encryption_key': self.generate_key_info(),
            'timestamp': time.time()
        }
        
        return shards, metadata
```

#### 加密方案
- **对称加密**: AES-256-GCM用于数据加密
- **非对称加密**: ECC (Curve25519) 用于密钥交换
- **哈希算法**: SHA-256用于数据完整性验证

### 2. 存储证明系统

#### 零知识存储证明
```python
class ZKStorageProof:
    """零知识存储证明系统"""
    
    def generate_proof(self, data_chunk, node_id, timestamp):
        """
        生成零知识存储证明
        
        Args:
            data_chunk: 数据块
            node_id: 存储节点ID
            timestamp: 时间戳
        
        Returns:
            proof: 存储证明
        """
        # 1. 计算数据承诺
        data_commitment = self.compute_commitment(data_chunk)
        
        # 2. 生成零知识证明
        zk_proof = self.generate_zk_snark({
            'data_commitment': data_commitment,
            'node_id': node_id,
            'timestamp': timestamp,
            'randomness': os.urandom(32)  # 随机数防止重放
        })
        
        # 3. 签名证明
        signature = self.sign_proof(zk_proof, node_id)
        
        return {
            'proof_id': uuid.uuid4().hex,
            'data_commitment': data_commitment,
            'zk_proof': zk_proof,
            'timestamp': timestamp,
            'signature': signature,
            'node_id': node_id
        }
    
    def verify_proof(self, proof, challenge=None):
        """
        验证存储证明
        
        Args:
            proof: 存储证明
            challenge: 可选的挑战值
        
        Returns:
            bool: 验证结果
        """
        # 1. 验证签名
        if not self.verify_signature(proof['signature'], proof['node_id']):
            return False
        
        # 2. 验证零知识证明
        if not self.verify_zk_snark(proof['zk_proof']):
            return False
        
        # 3. 验证时间有效性
        current_time = time.time()
        if current_time - proof['timestamp'] > self.proof_validity_period:
            return False
        
        # 4. 可选挑战验证
        if challenge:
            if not self.verify_challenge(proof, challenge):
                return False
        
        return True
```

### 3. 节点发现和选择

#### 基于信誉的节点选择
```python
class NodeSelector:
    """智能节点选择器"""
    
    def __init__(self):
        self.node_reputation = {}  # 节点信誉评分
        self.node_availability = {}  # 节点可用性记录
        self.node_performance = {}  # 节点性能指标
    
    def select_nodes(self, shard_count, requirements=None):
        """
        选择存储节点
        
        Args:
            shard_count: 需要选择的节点数量
            requirements: 可选的需求参数
        
        Returns:
            selected_nodes: 选中的节点列表
        """
        # 1. 获取可用节点
        available_nodes = self.get_available_nodes()
        
        # 2. 过滤符合条件的节点
        filtered_nodes = self.filter_nodes(available_nodes, requirements)
        
        # 3. 计算节点评分
        node_scores = self.calculate_node_scores(filtered_nodes)
        
        # 4. 选择最佳节点
        selected_nodes = self.select_best_nodes(node_scores, shard_count)
        
        # 5. 确保地理分布
        selected_nodes = self.ensure_geographic_distribution(selected_nodes)
        
        return selected_nodes
    
    def calculate_node_scores(self, nodes):
        """计算节点综合评分"""
        scores = {}
        for node_id in nodes:
            # 信誉评分 (40%)
            reputation_score = self.node_reputation.get(node_id, 0.5)
            
            # 可用性评分 (30%)
            availability_score = self.calculate_availability_score(node_id)
            
            # 性能评分 (20%)
            performance_score = self.calculate_performance_score(node_id)
            
            # 存储容量评分 (10%)
            capacity_score = self.calculate_capacity_score(node_id)
            
            # 综合评分
            total_score = (
                reputation_score * 0.4 +
                availability_score * 0.3 +
                performance_score * 0.2 +
                capacity_score * 0.1
            )
            
            scores[node_id] = total_score
        
        return scores
```

### 4. 数据冗余和恢复

#### 纠删码配置
```python
class ErasureCoding:
    """纠删码管理器"""
    
    def __init__(self, data_shards=3, parity_shards=2):
        """
        初始化纠删码配置
        
        Args:
            data_shards: 数据分片数
            parity_shards: 校验分片数
        """
        self.data_shards = data_shards
        self.parity_shards = parity_shards
        self.total_shards = data_shards + parity_shards
    
    def encode(self, data):
        """
        编码数据
        
        Args:
            data: 原始数据
        
        Returns:
            shards: 编码后的分片列表
        """
        # 1. 数据填充到合适大小
        padded_data = self.pad_data(data)
        
        # 2. 分割数据
        data_chunks = self.split_data(padded_data, self.data_shards)
        
        # 3. 计算校验分片
        parity_chunks = self.calculate_parity(data_chunks)
        
        # 4. 组合所有分片
        shards = data_chunks + parity_chunks
        
        return shards
    
    def decode(self, shards, shard_indices):
        """
        解码数据
        
        Args:
            shards: 可用的分片列表
            shard_indices: 分片索引列表
        
        Returns:
            data: 恢复的原始数据
        """
        # 检查是否有足够的分片
        available_shards = len([s for s in shards if s is not None])
        if available_shards < self.data_shards:
            raise ValueError(f"需要至少 {self.data_shards} 个分片，当前只有 {available_shards} 个")
        
        # 使用Reed-Solomon解码
        decoded_data = self.rs_decode(shards, shard_indices)
        
        # 移除填充
        original_data = self.unpad_data(decoded_data)
        
        return original_data
    
    def repair_shard(self, shards, missing_index):
        """
        修复丢失的分片
        
        Args:
            shards: 可用的分片列表
            missing_index: 丢失分片的索引
        
        Returns:
            repaired_shard: 修复的分片
        """
        # 确保有足够的分片进行修复
        available_count = len([s for s in shards if s is not None])
        if available_count < self.data_shards:
            raise ValueError("没有足够的分片进行修复")
        
        # 使用剩余分片计算丢失的分片
        repaired_shard = self.calculate_missing_shard(shards, missing_index)
        
        return repaired_shard
```

## 🚀 实现步骤

### 阶段1: 基础存储节点
1. **节点实现**: 基本的存储节点功能
2. **数据存储**: 本地文件系统存储
3. **心跳机制**: 节点健康检查
4. **简单API**: 基础的上传下载接口

### 阶段2: 分布式协议
1. **P2P网络**: 节点发现和通信
2. **存储证明**: 基本的存储验证
3. **数据冗余**: 纠删码实现
4. **负载均衡**: 简单的负载分配

### 阶段3: 高级功能
1. **零知识证明**: 隐私保护存储证明
2. **智能调度**: 基于AI的节点选择
3. **跨链集成**: 与其他区块链集成
4. **企业功能**: 企业级存储特性

### 阶段4: 优化和扩展
1. **性能优化**: 大规模优化
2. **安全增强**: 高级安全特性
3. **生态集成**: 与AI计算集成
4. **全球部署**: 全球节点网络

## 📊 性能指标

### 存储性能
| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| 存储容量 | 1EB | 0TB |
| 读写速度 | 100MB/s | 0MB/s |
| 数据持久性 | 99.999999% | 0% |
| 恢复时间 | <5分钟 | N/A |
| 并发连接 | 10,000+ | 0 |

### 网络性能
| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| 节点数量 | 10,000+ | 0 |
| 网络延迟 | <100ms | N/A |
| 带宽利用率 | >80% | 0% |
| 故障转移 | <10秒 | N/A |

## 🔒 安全特性

### 数据安全
1. **端到端加密**: 数据在客户端加密
2. **零知识证明**: 存储证明不泄露数据内容
3. **访问控制**: 基于属性的访问控制 (ABAC)
4. **审计日志**: 完整的操作审计

### 网络安全
1. **TLS 1.3**: 所有通信加密
2. **DDoS防护**: 分布式防护机制
3. **节点认证**: 双向TLS认证
4. **防火墙规则**: 智能防火墙

### 共识安全
1. **存储证明**: 防止虚假存储声明
2. **时间戳服务**: 防止重放攻击
3. **签名验证**: 所有消息签名验证
4. **信誉系统**: 防止恶意节点

## 📚 API文档

### 客户端API
```python
# 初始化客户端
client = DAICStorageClient(config)

# 上传文件
file_id = client.upload_file(
    file_path="/path/to/file",
    encryption_key="optional_key",
    redundancy=3
)

# 下载文件
client.download_file(
    file_id=file_id,
    output_path="/path/to/output",
    decryption_key="optional_key"
)

# 列出文件
files = client.list_files()

# 删除文件
client.delete_file(file_id)
```

### 节点API
```python
# 启动存储节点
node = StorageNode(config)
node.start()

# 获取节点状态
status = node.get_status()

# 管理存储空间
node.add_storage_path("/path/to/storage")
node.remove_storage_path("/path/to/storage")

# 停止节点
node.stop()
```

## 🧪 测试策略

### 单元测试
- 数据分片和加密测试
- 存储证明验证测试
- 节点选择算法测试
- 纠删码编解码测试

### 集成测试
- 端到端文件上传下载测试
- 多节点网络测试
- 故障恢复测试
- 性能基准测试

### 压力测试
- 大规模并发测试
- 长时间运行测试
- 网络分区测试
- 安全攻击模拟

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/daic-org/daic-storage.git
cd daic-storage

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 启动开发节点
python -m daic_storage.node --dev
```

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写完整的文档字符串
- 保持测试覆盖率>80%

### 提交流程
1. Fork仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request
5. 通过代码审查

## 📈 路线图

### Q1 2025: 基础实现
- [ ] 基础存储节点
- [ ] 简单客户端
- [ ] 基础网络协议
- [ ] 单元测试框架

### Q2 2025: 协议完善
- [ ] 完整存储协议
- [ ] 数据冗余机制
- [ ] 节点发现系统
- [ ] 集成测试

### Q3 2025: 高级功能
- [ ] 零知识证明
- [ ] 智能调度
- [ ] 企业功能
- [ ] 性能优化

### Q4 2025: 生产就绪
- [ ] 安全审计
- [ ] 大规模测试
- [ ] 文档完善
- [ ] 正式发布

---

*最后更新: 2026年2月26日*  
*版本: 1.0.0*

