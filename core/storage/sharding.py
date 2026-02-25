"""
数据分片和加密模块

负责将数据分片、加密、计算哈希，并生成元数据。
"""

import hashlib
import os
import time
import uuid
from typing import Dict, List, Tuple, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class DataSharding:
    """数据分片管理器"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 默认1MB分片
        """
        初始化数据分片管理器
        
        Args:
            chunk_size: 分片大小（字节）
        """
        self.chunk_size = chunk_size
        self.backend = default_backend()
    
    def shard_data(self, data: bytes, redundancy: int = 3, 
                   encryption_key: Optional[bytes] = None) -> Tuple[List[bytes], Dict]:
        """
        将数据分片并添加冗余
        
        Args:
            data: 原始数据
            redundancy: 冗余因子（默认3）
            encryption_key: 可选的加密密钥
        
        Returns:
            shards: 数据分片列表
            metadata: 分片元数据
        """
        # 1. 数据加密
        if encryption_key:
            encrypted_data = self._encrypt_data(data, encryption_key)
        else:
            # 生成随机密钥
            encryption_key = os.urandom(32)
            encrypted_data = self._encrypt_data(data, encryption_key)
        
        # 2. 数据分片
        shards = self._split_into_chunks(encrypted_data)
        
        # 3. 计算分片哈希
        shard_hashes = [self._calculate_hash(shard) for shard in shards]
        
        # 4. 生成元数据
        metadata = {
            'file_id': str(uuid.uuid4()),
            'original_size': len(data),
            'encrypted_size': len(encrypted_data),
            'shard_count': len(shards),
            'redundancy': redundancy,
            'shard_hashes': shard_hashes,
            'encryption_info': self._generate_key_info(encryption_key),
            'timestamp': time.time(),
            'chunk_size': self.chunk_size,
            'hash_algorithm': 'sha256',
            'encryption_algorithm': 'aes-256-gcm'
        }
        
        return shards, metadata
    
    def reconstruct_data(self, shards: List[bytes], metadata: Dict, 
                        decryption_key: Optional[bytes] = None) -> bytes:
        """
        从分片重建数据
        
        Args:
            shards: 数据分片列表
            metadata: 分片元数据
            decryption_key: 解密密钥
        
        Returns:
            data: 重建的原始数据
        """
        # 1. 验证分片完整性
        self._verify_shards(shards, metadata)
        
        # 2. 合并分片
        encrypted_data = self._merge_chunks(shards)
        
        # 3. 解密数据
        if decryption_key is None:
            decryption_key = self._extract_key_from_info(metadata['encryption_info'])
        
        data = self._decrypt_data(encrypted_data, decryption_key)
        
        # 4. 验证数据大小
        if len(data) != metadata['original_size']:
            raise ValueError(f"数据大小不匹配: 期望 {metadata['original_size']}, 实际 {len(data)}")
        
        return data
    
    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """
        使用AES-256-GCM加密数据
        
        Args:
            data: 原始数据
            key: 加密密钥（32字节）
        
        Returns:
            encrypted_data: 加密后的数据
        """
        # 生成随机IV（12字节用于GCM）
        iv = os.urandom(12)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # 加密数据
        encrypted = encryptor.update(data) + encryptor.finalize()
        
        # 返回IV + 加密数据 + 认证标签
        return iv + encryptor.tag + encrypted
    
    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        解密AES-256-GCM加密的数据
        
        Args:
            encrypted_data: 加密数据（IV + tag + 数据）
            key: 解密密钥
        
        Returns:
            data: 解密后的原始数据
        """
        # 提取IV（前12字节）、tag（后16字节）和加密数据
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # 解密数据
        data = decryptor.update(ciphertext) + decryptor.finalize()
        
        return data
    
    def _split_into_chunks(self, data: bytes) -> List[bytes]:
        """
        将数据分割成固定大小的块
        
        Args:
            data: 要分割的数据
        
        Returns:
            chunks: 数据块列表
        """
        chunks = []
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def _merge_chunks(self, chunks: List[bytes]) -> bytes:
        """
        合并数据块
        
        Args:
            chunks: 数据块列表
        
        Returns:
            data: 合并后的数据
        """
        return b''.join(chunks)
    
    def _calculate_hash(self, data: bytes) -> str:
        """
        计算数据的SHA-256哈希
        
        Args:
            data: 要计算哈希的数据
        
        Returns:
            hash: 十六进制哈希字符串
        """
        return hashlib.sha256(data).hexdigest()
    
    def _verify_shards(self, shards: List[bytes], metadata: Dict) -> None:
        """
        验证分片完整性
        
        Args:
            shards: 数据分片列表
            metadata: 分片元数据
        
        Raises:
            ValueError: 如果分片验证失败
        """
        # 检查分片数量
        if len(shards) != metadata['shard_count']:
            raise ValueError(f"分片数量不匹配: 期望 {metadata['shard_count']}, 实际 {len(shards)}")
        
        # 检查每个分片的哈希
        for i, (shard, expected_hash) in enumerate(zip(shards, metadata['shard_hashes'])):
            actual_hash = self._calculate_hash(shard)
            if actual_hash != expected_hash:
                raise ValueError(f"分片 {i} 哈希不匹配: 期望 {expected_hash}, 实际 {actual_hash}")
    
    def _generate_key_info(self, key: bytes) -> Dict:
        """
        生成密钥信息（不包含实际密钥）
        
        Args:
            key: 加密密钥
        
        Returns:
            key_info: 密钥信息字典
        """
        # 生成密钥指纹
        key_fingerprint = hashlib.sha256(key).hexdigest()
        
        return {
            'key_fingerprint': key_fingerprint,
            'key_length': len(key),
            'key_algorithm': 'aes-256-gcm',
            'key_id': str(uuid.uuid4())
        }
    
    def _extract_key_from_info(self, key_info: Dict) -> bytes:
        """
        从密钥信息中提取密钥（简化版本，实际应使用密钥管理系统）
        
        Args:
            key_info: 密钥信息
        
        Returns:
            key: 加密密钥
        """
        # 注意：这是一个简化版本
        # 实际实现应该从安全的密钥管理系统获取密钥
        # 这里返回一个随机密钥作为示例
        return os.urandom(32)
    
    def generate_key(self, password: Optional[str] = None, salt: Optional[bytes] = None) -> bytes:
        """
        生成加密密钥
        
        Args:
            password: 可选的密码
            salt: 可选的盐值
        
        Returns:
            key: 32字节的加密密钥
        """
        if password:
            # 使用密码派生密钥
            if salt is None:
                salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
            key = kdf.derive(password.encode())
        else:
            # 生成随机密钥
            key = os.urandom(32)
        
        return key
    
    def calculate_optimal_chunk_size(self, file_size: int) -> int:
        """
        计算最优分片大小
        
        Args:
            file_size: 文件大小（字节）
        
        Returns:
            optimal_size: 最优分片大小
        """
        # 基于文件大小动态调整分片大小
        if file_size < 1024 * 1024:  # < 1MB
            return 64 * 1024  # 64KB
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            return 1024 * 1024  # 1MB
        elif file_size < 1024 * 1024 * 1024:  # < 1GB
            return 4 * 1024 * 1024  # 4MB
        else:  # >= 1GB
            return 16 * 1024 * 1024  # 16MB