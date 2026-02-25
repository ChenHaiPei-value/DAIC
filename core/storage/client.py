"""
客户端模块

提供用户友好的API来与分布式存储系统交互。
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Optional, Tuple, BinaryIO
from pathlib import Path
from dataclasses import dataclass, asdict
from .sharding import DataSharding
from .erasure_coding import ErasureCoding
from .selector import NodeSelector, NodeInfo, NodeStatus
from .proof import ZKStorageProof


@dataclass
class FileMetadata:
    """文件元数据"""
    file_id: str
    filename: str
    original_size: int
    encrypted_size: int
    shard_count: int
    redundancy: int
    shard_hashes: List[str]
    encryption_info: Dict
    timestamp: float
    chunk_size: int
    hash_algorithm: str = "sha256"
    encryption_algorithm: str = "aes-256-gcm"
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileMetadata':
        """从字典创建FileMetadata"""
        return cls(**data)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class StorageLocation:
    """存储位置信息"""
    node_id: str
    shard_index: int
    shard_hash: str
    node_address: str
    node_port: int
    stored_at: float
    last_verified: Optional[float] = None
    verification_status: str = "pending"  # pending, verified, failed


class DAICStorageClient:
    """DAIC存储客户端"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化存储客户端
        
        Args:
            config: 配置字典
        """
        if config is None:
            config = {}
        
        self.config = config
        
        # 初始化组件
        self.sharding = DataSharding(
            chunk_size=config.get('chunk_size', 1024 * 1024)  # 默认1MB
        )
        self.erasure_coding = ErasureCoding(
            data_shards=config.get('data_shards', 3),
            parity_shards=config.get('parity_shards', 2)
        )
        self.node_selector = NodeSelector(
            min_reputation=config.get('min_reputation', 0.5),
            max_latency=config.get('max_latency', 1000.0)
        )
        self.proof_system = ZKStorageProof(
            proof_validity_period=config.get('proof_validity_period', 3600)
        )
        
        # 本地存储目录
        self.local_storage_dir = Path(config.get('local_storage_dir', '~/.daic/storage'))
        self.local_storage_dir = Path(os.path.expanduser(str(self.local_storage_dir)))
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 元数据存储
        self.metadata_dir = self.local_storage_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # 缓存
        self.file_cache = {}
        self.node_cache = {}
        
        # 统计信息
        self.stats = {
            'files_uploaded': 0,
            'files_downloaded': 0,
            'total_bytes_uploaded': 0,
            'total_bytes_downloaded': 0,
            'failed_operations': 0,
            'last_operation': None
        }
    
    def upload_file(self, file_path: str, encryption_key: Optional[bytes] = None, 
                   redundancy: int = 3, optimize_for: str = "balanced") -> str:
        """
        上传文件到分布式存储
        
        Args:
            file_path: 文件路径
            encryption_key: 加密密钥
            redundancy: 冗余因子
            optimize_for: 优化目标 (speed, security, balanced)
        
        Returns:
            file_id: 文件ID
        
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果参数无效
        """
        # 验证文件存在
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # 更新统计信息
        self.stats['last_operation'] = time.time()
        
        try:
            # 1. 数据分片和加密
            shards, metadata_dict = self.sharding.shard_data(
                file_data, redundancy, encryption_key
            )
            
            # 创建文件元数据
            metadata = FileMetadata(
                file_id=metadata_dict['file_id'],
                filename=file_path_obj.name,
                original_size=metadata_dict['original_size'],
                encrypted_size=metadata_dict['encrypted_size'],
                shard_count=metadata_dict['shard_count'],
                redundancy=metadata_dict['redundancy'],
                shard_hashes=metadata_dict['shard_hashes'],
                encryption_info=metadata_dict['encryption_info'],
                timestamp=metadata_dict['timestamp'],
                chunk_size=metadata_dict['chunk_size']
            )
            
            # 2. 应用纠删码
            encoded_shards = self.erasure_coding.encode(b''.join(shards))
            
            # 3. 选择存储节点
            node_requirements = self._get_node_requirements(optimize_for, len(encoded_shards))
            selected_nodes = self.node_selector.select_nodes(
                count=len(encoded_shards),
                requirements=node_requirements
            )
            
            # 4. 分发分片到节点
            storage_locations = []
            for i, (shard, node) in enumerate(zip(encoded_shards, selected_nodes)):
                location = self._store_shard_on_node(shard, i, node, metadata.file_id)
                storage_locations.append(location)
            
            # 5. 保存元数据
            self._save_file_metadata(metadata, storage_locations)
            
            # 6. 更新缓存
            self.file_cache[metadata.file_id] = {
                'metadata': metadata,
                'locations': storage_locations,
                'cached_at': time.time()
            }
            
            # 更新统计信息
            self.stats['files_uploaded'] += 1
            self.stats['total_bytes_uploaded'] += metadata.original_size
            
            print(f"文件上传成功: {metadata.filename} (ID: {metadata.file_id})")
            print(f"文件大小: {metadata.original_size / 1024 / 1024:.2f} MB")
            print(f"分片数量: {metadata.shard_count}")
            print(f"冗余因子: {metadata.redundancy}")
            print(f"存储节点: {len(selected_nodes)} 个")
            
            return metadata.file_id
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            raise RuntimeError(f"文件上传失败: {str(e)}") from e
    
    def download_file(self, file_id: str, output_path: str, 
                     decryption_key: Optional[bytes] = None) -> None:
        """
        从分布式存储下载文件
        
        Args:
            file_id: 文件ID
            output_path: 输出文件路径
            decryption_key: 解密密钥
        
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果无法恢复文件
        """
        # 更新统计信息
        self.stats['last_operation'] = time.time()
        
        try:
            # 1. 加载元数据
            metadata, storage_locations = self._load_file_metadata(file_id)
            
            # 2. 从节点获取分片
            shards = []
            shard_indices = []
            
            for location in storage_locations:
                try:
                    shard = self._retrieve_shard_from_node(location)
                    shards.append(shard)
                    shard_indices.append(location.shard_index)
                    
                    # 更新验证状态
                    location.last_verified = time.time()
                    location.verification_status = "verified"
                    
                except Exception as e:
                    print(f"警告: 无法从节点 {location.node_id} 获取分片 {location.shard_index}: {str(e)}")
                    shards.append(None)
                    shard_indices.append(location.shard_index)
            
            # 3. 检查是否有足够的分片
            available_shards = len([s for s in shards if s is not None])
            if available_shards < self.erasure_coding.data_shards:
                raise ValueError(
                    f"没有足够的分片进行恢复: 需要 {self.erasure_coding.data_shards} 个, "
                    f"当前只有 {available_shards} 个"
                )
            
            # 4. 使用纠删码恢复数据
            encoded_data = self.erasure_coding.decode(shards, shard_indices)
            
            # 5. 重建原始数据
            # 首先需要将编码数据分割回原始分片
            # 这里简化处理，实际需要根据编码方式调整
            reconstructed_shards = self._reconstruct_shards_from_encoded(encoded_data, metadata)
            
            # 6. 解密和合并数据
            file_data = self.sharding.reconstruct_data(reconstructed_shards, metadata.to_dict(), decryption_key)
            
            # 7. 保存文件
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            # 8. 更新缓存
            if file_id in self.file_cache:
                self.file_cache[file_id]['locations'] = storage_locations
                self.file_cache[file_id]['cached_at'] = time.time()
            
            # 更新统计信息
            self.stats['files_downloaded'] += 1
            self.stats['total_bytes_downloaded'] += metadata.original_size
            
            print(f"文件下载成功: {metadata.filename}")
            print(f"保存到: {output_path}")
            print(f"文件大小: {metadata.original_size / 1024 / 1024:.2f} MB")
            print(f"使用的分片: {available_shards}/{len(shards)}")
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            raise RuntimeError(f"文件下载失败: {str(e)}") from e
    
    def list_files(self) -> List[Dict]:
        """
        列出所有文件
        
        Returns:
            files: 文件信息列表
        """
        files = []
        
        # 扫描元数据目录
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                
                metadata = FileMetadata.from_dict(data['metadata'])
                
                file_info = {
                    'file_id': metadata.file_id,
                    'filename': metadata.filename,
                    'size': metadata.original_size,
                    'uploaded_at': metadata.timestamp,
                    'shard_count': metadata.shard_count,
                    'redundancy': metadata.redundancy,
                    'locations': len(data.get('locations', []))
                }
                
                files.append(file_info)
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        return files
    
    def delete_file(self, file_id: str) -> None:
        """
        删除文件
        
        Args:
            file_id: 文件ID
        
        Raises:
            FileNotFoundError: 如果文件不存在
        """
        # 1. 加载元数据
        try:
            metadata, storage_locations = self._load_file_metadata(file_id)
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {file_id}")
        
        # 2. 从所有节点删除分片
        for location in storage_locations:
            try:
                self._delete_shard_from_node(location)
            except Exception as e:
                print(f"警告: 无法从节点 {location.node_id} 删除分片: {str(e)}")
        
        # 3. 删除本地元数据
        metadata_file = self.metadata_dir / f"{file_id}.json"
        if metadata_file.exists():
            metadata_file.unlink()
        
        # 4. 从缓存中移除
        if file_id in self.file_cache:
            del self.file_cache[file_id]
        
        print(f"文件删除成功: {metadata.filename} (ID: {file_id})")
    
    def verify_file_integrity(self, file_id: str) -> Dict:
        """
        验证文件完整性
        
        Args:
            file_id: 文件ID
        
        Returns:
            verification_result: 验证结果
        """
        try:
            # 加载元数据
            metadata, storage_locations = self._load_file_metadata(file_id)
            
            # 检查每个分片
            verification_results = []
            all_valid = True
            
            for location in storage_locations:
                try:
                    # 获取分片
                    shard = self._retrieve_shard_from_node(location)
                    
                    # 验证哈希
                    shard_hash = hashlib.sha256(shard).hexdigest()
                    is_valid = shard_hash == location.shard_hash
                    
                    # 生成存储证明
                    proof = self.proof_system.generate_proof(shard, location.node_id)
                    proof_valid = self.proof_system.verify_proof(proof)
                    
                    result = {
                        'node_id': location.node_id,
                        'shard_index': location.shard_index,
                        'hash_valid': is_valid,
                        'proof_valid': proof_valid,
                        'last_verified': location.last_verified,
                        'status': 'valid' if is_valid and proof_valid else 'invalid'
                    }
                    
                    if not (is_valid and proof_valid):
                        all_valid = False
                    
                    verification_results.append(result)
                    
                    # 更新位置信息
                    location.last_verified = time.time()
                    location.verification_status = 'verified' if is_valid else 'failed'
                    
                except Exception as e:
                    result = {
                        'node_id': location.node_id,
                        'shard_index': location.shard_index,
                        'hash_valid': False,
                        'proof_valid': False,
                        'error': str(e),
                        'status': 'error'
                    }
                    verification_results.append(result)
                    all_valid = False
            
            # 保存更新的位置信息
            self._save_file_metadata(metadata, storage_locations)
            
            return {
                'file_id': file_id,
                'filename': metadata.filename,
                'overall_status': 'valid' if all_valid else 'degraded',
                'shards_checked': len(verification_results),
                'valid_shards': sum(1 for r in verification_results if r['status'] == 'valid'),
                'invalid_shards': sum(1 for r in verification_results if r['status'] == 'invalid'),
                'error_shards': sum(1 for r in verification_results if r['status'] == 'error'),
                'details': verification_results
            }
            
        except Exception as e:
            return {
                'file_id': file_id,
                'overall_status': 'error',
                'error': str(e)
            }
    
    def repair_file(self, file_id: str) -> Dict:
        """
        修复文件（重新分发丢失或损坏的分片）
        
        Args:
            file_id: 文件ID
        
        Returns:
            repair_result: 修复结果
        """
        # 1. 验证文件完整性
        verification = self.verify_file_integrity(file_id)
        
        if verification['overall_status'] == 'valid':
            return {
                'file_id': file_id,
                'status': 'no_repair_needed',
                'message': '文件完整性良好，无需修复'
            }
        
        # 2. 加载元数据
        metadata, storage_locations = self._load_file_metadata(file_id)
        
        # 3. 识别需要修复的分片
        shards_to_repair = []
        for i, location in enumerate(storage_locations):
            # 检查分片状态
            shard_status = next(
                (r for r in verification['details'] if r['shard_index'] == location.shard_index),
                None
            )
            
            if shard_status and shard_status['status'] in ['invalid', 'error']:
                shards_to_repair.append({
                    'shard_index': location.shard_index,
                    'node_id': location.node_id,
                    'reason': shard_status.get('error', 'hash_or_proof_invalid')
                })
        
        if not shards_to_repair:
            return {
                'file_id': file_id,
                'status': 'no_repair_needed',
                'message': '没有需要修复的分片'
            }
        
        # 4. 修复分片
        repaired_count = 0
        repair_details = []
        
        for repair_info in shards_to_repair:
            try:
                # 获取其他分片来修复当前分片
                other_locations = [loc for loc in storage_locations 
                                 if loc.shard_index != repair_info['shard_index']]
                
                # 从其他节点获取分片
                other_shards = []
                other_indices = []
                
                for loc in other_locations[:self.erasure_coding.data_shards]:
                    try:
                        shard = self._retrieve_shard_from_node(loc)
                        other_shards.append(shard)
                        other_indices.append(loc.shard_index)
                    except Exception:
                        continue
                
                if len(other_shards) < self.erasure_coding.data_shards:
                    print(f"警告: 没有足够的分片来修复分片 {repair_info['shard_index']}")
                    continue
                
                # 修复分片
                repaired_shard = self.erasure_coding.repair_shard(other_shards, repair_info['shard_index'])
                
                # 选择新的存储节点
                node_requirements = self._get_node_requirements("balanced", 1)
                selected_nodes = self.node_selector.select_nodes(count=1, requirements=node_requirements)
                
                if not selected_nodes:
                    print(f"警告: 没有可用的节点来存储修复的分片 {repair_info['shard_index']}")
                    continue
                
                # 存储修复的分片
                new_node = selected_nodes[0]
                new_location = self._store_shard_on_node(
                    repaired_shard, 
                    repair_info['shard_index'], 
                    new_node, 
                    metadata.file_id
                )
                
                # 更新存储位置
                for j, loc in enumerate(storage_locations):
                    if loc.shard_index == repair_info['shard_index']:
                        storage_locations[j] = new_location
                        break
                
                # 删除旧分片（如果可能）
                try:
                    self._delete_shard_from_node_by_id(repair_info['node_id'], metadata.file_id, repair_info['shard_index'])
                except Exception as e:
                    print(f"警告: 无法删除旧分片: {str(e)}")
                
                repaired_count += 1
                repair_details.append({
                    'shard_index': repair_info['shard_index'],
                    'old_node': repair_info['node_id'],
                    'new_node': new_node.node_id,
                    'status': 'repaired'
                })
                
            except Exception as e:
                repair_details.append({
                    'shard_index': repair_info['shard_index'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 5. 保存更新的元数据
        if repaired_count > 0:
            self._save_file_metadata(metadata, storage_locations)
            
            # 更新缓存
            if file_id in self.file_cache:
                self.file_cache[file_id]['locations'] = storage_locations
                self.file_cache[file_id]['cached_at'] = time.time()
        
        return {
            'file_id': file_id,
            'filename': metadata.filename,
            'status': 'repaired' if repaired_count > 0 else 'failed',
            'shards_repaired': repaired_count,
            'total_shards_to_repair': len(shards_to_repair),
            'details': repair_details
        }
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        获取文件详细信息
        
        Args:
            file_id: 文件ID
        
        Returns:
            file_info: 文件信息，如果文件不存在则返回None
        """
        try:
            metadata, storage_locations = self._load_file_metadata(file_id)
            
            # 统计节点信息
            node_stats = {}
            for location in storage_locations:
                if location.node_id not in node_stats:
                    node_stats[location.node_id] = {
                        'address': location.node_address,
                        'port': location.node_port,
                        'shard_count': 0,
                        'last_verified': location.last_verified,
                        'verification_status': location.verification_status
                    }
                node_stats[location.node_id]['shard_count'] += 1
            
            return {
                'file_id': metadata.file_id,
                'filename': metadata.filename,
                'size': metadata.original_size,
                'uploaded_at': metadata.timestamp,
                'shard_count': metadata.shard_count,
                'redundancy': metadata.redundancy,
                'encryption_algorithm': metadata.encryption_algorithm,
                'hash_algorithm': metadata.hash_algorithm,
                'storage_locations': len(storage_locations),
                'nodes': node_stats,
                'metadata_path': str(self.metadata_dir / f"{file_id}.json")
            }
        except FileNotFoundError:
            return None
    
    def get_statistics(self) -> Dict:
        """
        获取客户端统计信息
        
        Returns:
            stats: 统计信息
        """
        # 获取文件列表
        files = self.list_files()
        
        # 计算总存储使用量
        total_size = sum(f['size'] for f in files)
        total_files = len(files)
        
        stats = self.stats.copy()
        stats.update({
            'total_files': total_files,
            'total_storage_bytes': total_size,
            'total_storage_mb': total_size / (1024 * 1024),
            'total_storage_gb': total_size / (1024 * 1024 * 1024),
            'cache_size': len(self.file_cache),
            'local_storage_dir': str(self.local_storage_dir),
            'uptime': time.time() - (self.stats.get('start_time', time.time()))
        })
        
        return stats
    
    def clear_cache(self) -> None:
        """
        清除客户端缓存
        """
        self.file_cache.clear()
        self.node_cache.clear()
        print("缓存已清除")
    
    def _get_node_requirements(self, optimize_for: str, shard_count: int) -> Dict:
        """
        获取节点选择需求
        
        Args:
            optimize_for: 优化目标
            shard_count: 分片数量
        
        Returns:
            requirements: 节点需求字典
        """
        requirements = {
            'ensure_geographic_distribution': True,
            'min_storage': 1024 * 1024 * 100,  # 100MB最小存储
        }
        
        if optimize_for == "speed":
            requirements.update({
                'prefer_low_latency': True,
                'min_bandwidth': 100,  # 100Mbps
                'max_latency': 100,    # 100ms
            })
        elif optimize_for == "security":
            requirements.update({
                'prefer_high_storage': True,
                'min_reputation': 0.8,
                'required_protocols': ['tls', 'encryption']
            })
        else:  # balanced
            requirements.update({
                'prefer_low_latency': True,
                'prefer_high_storage': True,
                'min_reputation': 0.6,
                'min_bandwidth': 50,   # 50Mbps
                'max_latency': 500,    # 500ms
            })
        
        return requirements
    
    def _store_shard_on_node(self, shard: bytes, shard_index: int, 
                           node: NodeInfo, file_id: str) -> StorageLocation:
        """
        将分片存储到节点
        
        Args:
            shard: 分片数据
            shard_index: 分片索引
            node: 节点信息
            file_id: 文件ID
        
        Returns:
            location: 存储位置信息
        """
        # 计算分片哈希
        shard_hash = hashlib.sha256(shard).hexdigest()
        
        # 这里应该实现实际的网络通信来存储分片
        # 这是一个简化版本，实际应该发送HTTP请求或使用P2P协议
        
        # 模拟存储操作
        storage_time = time.time()
        
        # 创建存储位置信息
        location = StorageLocation(
            node_id=node.node_id,
            shard_index=shard_index,
            shard_hash=shard_hash,
            node_address=node.address,
            node_port=node.port,
            stored_at=storage_time,
            last_verified=storage_time,
            verification_status="verified"
        )
        
        # 在实际实现中，这里应该：
        # 1. 连接到节点
        # 2. 发送存储请求
        # 3. 验证响应
        # 4. 处理错误
        
        print(f"分片 {shard_index} 已存储到节点 {node.node_id} ({node.address}:{node.port})")
        
        return location
    
    def _retrieve_shard_from_node(self, location: StorageLocation) -> bytes:
        """
        从节点检索分片
        
        Args:
            location: 存储位置信息
        
        Returns:
            shard: 分片数据
        
        Raises:
            ConnectionError: 如果无法连接到节点
            ValueError: 如果分片验证失败
        """
        # 这里应该实现实际的网络通信来检索分片
        # 这是一个简化版本
        
        # 模拟检索操作
        # 在实际实现中，这里应该：
        # 1. 连接到节点
        # 2. 发送检索请求
        # 3. 接收分片数据
        # 4. 验证哈希
        
        # 为了演示，我们返回一个模拟的分片
        # 实际实现应该从网络获取
        
        # 模拟分片数据（实际应该从存储中获取）
        shard_size = 1024  # 假设1KB分片
        shard_data = b'x' * shard_size
        
        # 验证哈希
        shard_hash = hashlib.sha256(shard_data).hexdigest()
        if shard_hash != location.shard_hash:
            raise ValueError(f"分片哈希不匹配: 期望 {location.shard_hash}, 实际 {shard_hash}")
        
        return shard_data
    
    def _delete_shard_from_node(self, location: StorageLocation) -> None:
        """
        从节点删除分片
        
        Args:
            location: 存储位置信息
        """
        # 这里应该实现实际的网络通信来删除分片
        # 这是一个简化版本
        
        print(f"从节点 {location.node_id} 删除分片 {location.shard_index}")
        
        # 在实际实现中，这里应该：
        # 1. 连接到节点
        # 2. 发送删除请求
        # 3. 验证响应
    
    def _delete_shard_from_node_by_id(self, node_id: str, file_id: str, shard_index: int) -> None:
        """
        通过节点ID删除分片
        
        Args:
            node_id: 节点ID
            file_id: 文件ID
            shard_index: 分片索引
        """
        # 简化实现
        print(f"从节点 {node_id} 删除文件 {file_id} 的分片 {shard_index}")
    
    def _save_file_metadata(self, metadata: FileMetadata, locations: List[StorageLocation]) -> None:
        """
        保存文件元数据
        
        Args:
            metadata: 文件元数据
            locations: 存储位置列表
        """
        metadata_file = self.metadata_dir / f"{metadata.file_id}.json"
        
        data = {
            'metadata': metadata.to_dict(),
            'locations': [asdict(loc) for loc in locations],
            'saved_at': time.time()
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_file_metadata(self, file_id: str) -> Tuple[FileMetadata, List[StorageLocation]]:
        """
        加载文件元数据
        
        Args:
            file_id: 文件ID
        
        Returns:
            metadata: 文件元数据
            locations: 存储位置列表
        
        Raises:
            FileNotFoundError: 如果元数据文件不存在
        """
        # 首先检查缓存
        if file_id in self.file_cache:
            cache_entry = self.file_cache[file_id]
            if time.time() - cache_entry['cached_at'] < 300:  # 5分钟缓存
                return cache_entry['metadata'], cache_entry['locations']
        
        # 从文件加载
        metadata_file = self.metadata_dir / f"{file_id}.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"文件元数据不存在: {file_id}")
        
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        # 解析元数据
        metadata = FileMetadata.from_dict(data['metadata'])
        
        # 解析存储位置
        locations = []
        for loc_data in data.get('locations', []):
            # 处理可选字段
            last_verified = loc_data.get('last_verified')
            verification_status = loc_data.get('verification_status', 'pending')
            
            location = StorageLocation(
                node_id=loc_data['node_id'],
                shard_index=loc_data['shard_index'],
                shard_hash=loc_data['shard_hash'],
                node_address=loc_data['node_address'],
                node_port=loc_data['node_port'],
                stored_at=loc_data['stored_at'],
                last_verified=last_verified,
                verification_status=verification_status
            )
            locations.append(location)
        
        # 更新缓存
        self.file_cache[file_id] = {
            'metadata': metadata,
            'locations': locations,
            'cached_at': time.time()
        }
        
        return metadata, locations
    
    def _reconstruct_shards_from_encoded(self, encoded_data: bytes, metadata: FileMetadata) -> List[bytes]:
        """
        从编码数据重建原始分片
        
        Args:
            encoded_data: 编码后的数据
            metadata: 文件元数据
        
        Returns:
            shards: 原始分片列表
        """
        # 这是一个简化版本
        # 实际实现需要根据编码方式正确分割数据
        
        # 计算每个原始分片的大小
        shard_size = len(encoded_data) // metadata.shard_count
        
        shards = []
        for i in range(metadata.shard_count):
            start = i * shard_size
            end = start + shard_size if i < metadata.shard_count - 1 else len(encoded_data)
            shard = encoded_data[start:end]
            shards.append(shard)
        
        return shards
    
    def add_test_nodes(self, count: int = 5) -> None:
        """
        添加测试节点（用于演示）
        
        Args:
            count: 节点数量
        """
        import random
        
        for i in range(count):
            node_id = f"test_node_{i}"
            node = NodeInfo(
                node_id=node_id,
                address=f"192.168.1.{100 + i}",
                port=8000 + i,
                storage_capacity=random.randint(100, 1000) * 1024 * 1024 * 1024,  # 100-1000GB
                used_storage=random.randint(0, 500) * 1024 * 1024 * 1024,  # 0-500GB
                bandwidth=random.randint(10, 1000),  # 10-1000Mbps
                latency=random.uniform(1, 100),  # 1-100ms
                uptime=random.uniform(0.8, 0.99),  # 80-99%
                reputation=random.uniform(0.6, 0.95),  # 60-95%
                last_seen=time.time() - random.uniform(0, 3600),  # 0-1小时前
                status=NodeStatus.ONLINE,
                geographic_location=(random.uniform(-90, 90), random.uniform(-180, 180))
            )
            
            self.node_selector.add_node(node)
            print(f"添加测试节点: {node_id} ({node.address}:{node.port})")
    
    def demo_upload_download(self, test_file_path: Optional[str] = None) -> None:
        """
        演示上传和下载功能
        
        Args:
            test_file_path: 测试文件路径（如果为None则创建测试文件）
        """
        import tempfile
        
        # 添加测试节点
        self.add_test_nodes(5)
        
        # 创建测试文件
        if test_file_path is None:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
                test_data = b"This is a test file for DAIC distributed storage system.\n" * 1000
                f.write(test_data)
                test_file_path = f.name
        
        print("=" * 60)
        print("DAIC存储系统演示")
        print("=" * 60)
        
        try:
            # 上传文件
            print("\n1. 上传文件...")
            file_id = self.upload_file(
                test_file_path,
                redundancy=3,
                optimize_for="balanced"
            )
            
            # 列出文件
            print("\n2. 列出文件...")
            files = self.list_files()
            for file_info in files:
                print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
            
            # 获取文件信息
            print("\n3. 获取文件信息...")
            file_info = self.get_file_info(file_id)
            if file_info:
                print(f"  文件ID: {file_info['file_id']}")
                print(f"  文件名: {file_info['filename']}")
                print(f"  文件大小: {file_info['size']} bytes")
                print(f"  分片数量: {file_info['shard_count']}")
                print(f"  存储节点: {len(file_info['nodes'])} 个")
            
            # 验证文件完整性
            print("\n4. 验证文件完整性...")
            verification = self.verify_file_integrity(file_id)
            print(f"  整体状态: {verification['overall_status']}")
            print(f"  有效分片: {verification['valid_shards']}/{verification['shards_checked']}")
            
            # 下载文件
            print("\n5. 下载文件...")
            output_file = tempfile.mktemp(suffix='_downloaded.txt')
            self.download_file(file_id, output_file)
            
            # 验证下载的文件
            with open(test_file_path, 'rb') as f1, open(output_file, 'rb') as f2:
                original_data = f1.read()
                downloaded_data = f2.read()
                
                if original_data == downloaded_data:
                    print("  验证: 下载的文件与原始文件一致 ✓")
                else:
                    print("  验证: 下载的文件与原始文件不一致 ✗")
            
            # 显示统计信息
            print("\n6. 统计信息...")
            stats = self.get_statistics()
            print(f"  上传文件数: {stats['files_uploaded']}")
            print(f"  下载文件数: {stats['files_downloaded']}")
            print(f"  总上传数据: {stats['total_bytes_uploaded'] / 1024 / 1024:.2f} MB")
            print(f"  总下载数据: {stats['total_bytes_downloaded'] / 1024 / 1024:.2f} MB")
            print(f"  失败操作数: {stats['failed_operations']}")
            
            # 清理临时文件
            if test_file_path and os.path.exists(test_file_path):
                os.unlink(test_file_path)
            if os.path.exists(output_file):
                os.unlink(output_file)
            
            print("\n演示完成！")
            
        except Exception as e:
            print(f"\n演示过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def run_interactive_demo(self) -> None:
        """
        运行交互式演示
        """
        print("=" * 60)
        print("DAIC分布式存储系统 - 交互式演示")
        print("=" * 60)
        
        # 添加测试节点
        self.add_test_nodes(5)
        
        while True:
            print("\n请选择操作:")
            print("1. 上传文件")
            print("2. 列出文件")
            print("3. 下载文件")
            print("4. 验证文件完整性")
            print("5. 修复文件")
            print("6. 删除文件")
            print("7. 显示统计信息")
            print("8. 运行完整演示")
            print("9. 退出")
            
            choice = input("\n请输入选项 (1-9): ").strip()
            
            if choice == "1":
                # 上传文件
                file_path = input("请输入文件路径: ").strip()
                if not os.path.exists(file_path):
                    print("错误: 文件不存在")
                    continue
                
                try:
                    redundancy = int(input("冗余因子 (默认3): ").strip() or "3")
                    optimize_for = input("优化目标 (speed/security/balanced, 默认balanced): ").strip() or "balanced"
                    
                    file_id = self.upload_file(file_path, redundancy=redundancy, optimize_for=optimize_for)
                    print(f"文件上传成功! 文件ID: {file_id}")
                    
                except Exception as e:
                    print(f"上传失败: {str(e)}")
            
            elif choice == "2":
                # 列出文件
                files = self.list_files()
                if not files:
                    print("没有文件")
                else:
                    print(f"\n找到 {len(files)} 个文件:")
                    for i, file_info in enumerate(files, 1):
                        print(f"{i}. {file_info['filename']} ({file_info['size']} bytes)")
                        print(f"   ID: {file_info['file_id']}")
                        print(f"   上传时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info['uploaded_at']))}")
                        print(f"   分片数: {file_info['shard_count']}, 冗余: {file_info['redundancy']}x")
            
            elif choice == "3":
                # 下载文件
                file_id = input("请输入文件ID: ").strip()
                output_path = input("请输入输出路径: ").strip()
                
                try:
                    self.download_file(file_id, output_path)
                    print(f"文件下载成功: {output_path}")
                except Exception as e:
                    print(f"下载失败: {str(e)}")
            
            elif choice == "4":
                # 验证文件完整性
                file_id = input("请输入文件ID: ").strip()
                
                try:
                    result = self.verify_file_integrity(file_id)
                    print(f"\n文件验证结果:")
                    print(f"  文件名: {result.get('filename', '未知')}")
                    print(f"  整体状态: {result['overall_status']}")
                    print(f"  检查分片: {result['shards_checked']}")
                    print(f"  有效分片: {result['valid_shards']}")
                    print(f"  无效分片: {result['invalid_shards']}")
                    print(f"  错误分片: {result['error_shards']}")
                    
                    if 'details' in result:
                        print("\n  分片详情:")
                        for detail in result['details']:
                            status_icon = "✓" if detail['status'] == 'valid' else "✗"
                            print(f"    分片 {detail['shard_index']}: {status_icon} {detail['status']}")
                            
                except Exception as e:
                    print(f"验证失败: {str(e)}")
            
            elif choice == "5":
                # 修复文件
                file_id = input("请输入文件ID: ").strip()
                
                try:
                    result = self.repair_file(file_id)
                    print(f"\n文件修复结果:")
                    print(f"  状态: {result['status']}")
                    print(f"  修复分片: {result['shards_repaired']}/{result['total_shards_to_repair']}")
                    
                    if 'details' in result:
                        for detail in result['details']:
                            print(f"    分片 {detail['shard_index']}: {detail['status']}")
                            
                except Exception as e:
                    print(f"修复失败: {str(e)}")
            
            elif choice == "6":
                # 删除文件
                file_id = input("请输入文件ID: ").strip()
                confirm = input(f"确认删除文件 {file_id}? (y/N): ").strip().lower()
                
                if confirm == 'y':
                    try:
                        self.delete_file(file_id)
                        print("文件删除成功")
                    except Exception as e:
                        print(f"删除失败: {str(e)}")
                else:
                    print("取消删除")
            
            elif choice == "7":
                # 显示统计信息
                stats = self.get_statistics()
                print(f"\n客户端统计信息:")
                print(f"  总文件数: {stats['total_files']}")
                print(f"  上传文件数: {stats['files_uploaded']}")
                print(f"  下载文件数: {stats['files_downloaded']}")
                print(f"  总上传数据: {stats['total_storage_mb']:.2f} MB")
                print(f"  总下载数据: {stats['total_bytes_downloaded'] / 1024 / 1024:.2f} MB")
                print(f"  失败操作数: {stats['failed_operations']}")
                print(f"  缓存大小: {stats['cache_size']}")
                print(f"  运行时间: {stats['uptime']:.1f} 秒")
            
            elif choice == "8":
                # 运行完整演示
                self.demo_upload_download()
            
            elif choice == "9":
                # 退出
                print("感谢使用DAIC存储系统!")
                break
            
            else:
                print("无效选项，请重新选择")
           
