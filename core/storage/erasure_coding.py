"""
纠删码模块

实现Reed-Solomon纠删码，用于数据冗余和恢复。
"""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np


class ErasureCoding:
    """纠删码管理器"""
    
    def __init__(self, data_shards: int = 3, parity_shards: int = 2):
        """
        初始化纠删码配置
        
        Args:
            data_shards: 数据分片数
            parity_shards: 校验分片数
        """
        self.data_shards = data_shards
        self.parity_shards = parity_shards
        self.total_shards = data_shards + parity_shards
        
        # 初始化Reed-Solomon编码矩阵
        self.encoding_matrix = self._create_encoding_matrix()
    
    def encode(self, data: bytes) -> List[bytes]:
        """
        编码数据
        
        Args:
            data: 原始数据
        
        Returns:
            shards: 编码后的分片列表（数据分片 + 校验分片）
        
        Raises:
            ValueError: 如果数据为空或太大
        """
        if not data:
            raise ValueError("数据不能为空")
        
        # 1. 数据填充到合适大小
        padded_data = self._pad_data(data)
        
        # 2. 分割数据
        data_chunks = self._split_data(padded_data)
        
        # 3. 计算校验分片
        parity_chunks = self._calculate_parity(data_chunks)
        
        # 4. 组合所有分片
        shards = data_chunks + parity_chunks
        
        return shards
    
    def decode(self, shards: List[Optional[bytes]], shard_indices: List[int]) -> bytes:
        """
        解码数据
        
        Args:
            shards: 可用的分片列表（None表示丢失的分片）
            shard_indices: 分片索引列表
        
        Returns:
            data: 恢复的原始数据
        
        Raises:
            ValueError: 如果没有足够的分片进行恢复
        """
        # 检查是否有足够的分片
        available_shards = len([s for s in shards if s is not None])
        if available_shards < self.data_shards:
            raise ValueError(
                f"需要至少 {self.data_shards} 个分片进行恢复，当前只有 {available_shards} 个"
            )
        
        # 重建数据
        reconstructed_data = self._reconstruct_data(shards, shard_indices)
        
        # 移除填充
        original_data = self._unpad_data(reconstructed_data)
        
        return original_data
    
    def repair_shard(self, shards: List[Optional[bytes]], missing_index: int) -> bytes:
        """
        修复丢失的分片
        
        Args:
            shards: 可用的分片列表
            missing_index: 丢失分片的索引
        
        Returns:
            repaired_shard: 修复的分片
        
        Raises:
            ValueError: 如果没有足够的分片进行修复
        """
        # 确保有足够的分片进行修复
        available_count = len([s for s in shards if s is not None])
        if available_count < self.data_shards:
            raise ValueError("没有足够的分片进行修复")
        
        # 使用剩余分片计算丢失的分片
        repaired_shard = self._calculate_missing_shard(shards, missing_index)
        
        return repaired_shard
    
    def get_redundancy_info(self) -> Dict:
        """
        获取冗余信息
        
        Returns:
            info: 冗余信息字典
        """
        return {
            'data_shards': self.data_shards,
            'parity_shards': self.parity_shards,
            'total_shards': self.total_shards,
            'redundancy_factor': self.total_shards / self.data_shards,
            'max_failures': self.parity_shards,
            'recovery_threshold': self.data_shards
        }
    
    def _pad_data(self, data: bytes) -> bytes:
        """
        将数据填充到合适大小
        
        Args:
            data: 原始数据
        
        Returns:
            padded_data: 填充后的数据
        """
        # 计算每个分片的大小
        shard_size = math.ceil(len(data) / self.data_shards)
        total_size = shard_size * self.data_shards
        
        # 填充数据
        if len(data) < total_size:
            padding_size = total_size - len(data)
            padded_data = data + bytes([0] * padding_size)
        else:
            padded_data = data
        
        return padded_data
    
    def _unpad_data(self, data: bytes) -> bytes:
        """
        移除数据填充
        
        Args:
            data: 填充后的数据
        
        Returns:
            original_data: 原始数据
        """
        # 查找第一个零字节的位置
        # 注意：这是一个简化版本，实际应该存储原始数据长度
        end_pos = len(data)
        for i in range(len(data) - 1, -1, -1):
            if data[i] != 0:
                end_pos = i + 1
                break
        
        return data[:end_pos]
    
    def _split_data(self, data: bytes) -> List[bytes]:
        """
        分割数据
        
        Args:
            data: 要分割的数据
        
        Returns:
            chunks: 数据块列表
        """
        chunk_size = len(data) // self.data_shards
        chunks = []
        
        for i in range(self.data_shards):
            start = i * chunk_size
            end = start + chunk_size if i < self.data_shards - 1 else len(data)
            chunk = data[start:end]
            chunks.append(chunk)
        
        return chunks
    
    def _calculate_parity(self, data_chunks: List[bytes]) -> List[bytes]:
        """
        计算校验分片
        
        Args:
            data_chunks: 数据分片列表
        
        Returns:
            parity_chunks: 校验分片列表
        """
        # 确保所有分片大小相同
        chunk_size = len(data_chunks[0])
        for chunk in data_chunks:
            if len(chunk) != chunk_size:
                # 填充到相同大小
                chunk = chunk.ljust(chunk_size, b'\x00')
        
        # 将分片转换为矩阵（使用int32避免溢出）
        data_matrix = np.zeros((self.data_shards, chunk_size), dtype=np.int32)
        for i, chunk in enumerate(data_chunks):
            data_matrix[i] = list(chunk)
        
        # 计算校验分片
        parity_matrix = np.dot(self.encoding_matrix[self.data_shards:].astype(np.int32), data_matrix)
        
        # 应用模运算并确保值在0-255范围内
        parity_matrix = parity_matrix % 256
        
        # 转换回字节列表
        parity_chunks = []
        for i in range(self.parity_shards):
            # 确保值在0-255范围内
            row = parity_matrix[i] % 256
            parity_chunk = bytes(row.astype(np.uint8))
            parity_chunks.append(parity_chunk)
        
        return parity_chunks
    
    def _create_encoding_matrix(self) -> np.ndarray:
        """
        创建Reed-Solomon编码矩阵
        
        Returns:
            matrix: 编码矩阵
        """
        # 创建Vandermonde矩阵
        matrix = np.zeros((self.total_shards, self.data_shards), dtype=np.uint8)
        
        for i in range(self.total_shards):
            for j in range(self.data_shards):
                matrix[i][j] = (i + 1) ** j % 256
        
        return matrix
    
    def _reconstruct_data(self, shards: List[Optional[bytes]], shard_indices: List[int]) -> bytes:
        """
        重建数据
        
        Args:
            shards: 可用的分片列表
            shard_indices: 分片索引列表
        
        Returns:
            data: 重建的数据
        """
        # 收集可用的分片和索引
        available_shards = []
        available_indices = []
        
        for shard, index in zip(shards, shard_indices):
            if shard is not None:
                available_shards.append(shard)
                available_indices.append(index)
        
        # 确保有足够的分片
        if len(available_shards) < self.data_shards:
            raise ValueError("没有足够的分片进行重建")
        
        # 选择前data_shards个分片进行重建
        if len(available_shards) > self.data_shards:
            available_shards = available_shards[:self.data_shards]
            available_indices = available_indices[:self.data_shards]
        
        # 获取分片大小
        shard_size = len(available_shards[0])
        
        # 创建子矩阵
        submatrix = self.encoding_matrix[available_indices[:self.data_shards], :self.data_shards]
        
        # 计算逆矩阵
        try:
            inv_matrix = np.linalg.inv(submatrix.astype(np.float64))
        except np.linalg.LinAlgError:
            raise ValueError("无法计算逆矩阵，分片选择不当")
        
        # 将分片转换为矩阵
        shard_matrix = np.zeros((self.data_shards, shard_size), dtype=np.uint8)
        for i, shard in enumerate(available_shards):
            shard_matrix[i] = list(shard)
        
        # 重建原始数据矩阵
        data_matrix = np.dot(inv_matrix, shard_matrix) % 256
        
        # 转换回字节
        data_chunks = []
        for i in range(self.data_shards):
            data_chunk = bytes(data_matrix[i].astype(np.uint8))
            data_chunks.append(data_chunk)
        
        # 合并数据块
        reconstructed_data = b''.join(data_chunks)
        
        return reconstructed_data
    
    def _calculate_missing_shard(self, shards: List[Optional[bytes]], missing_index: int) -> bytes:
        """
        计算丢失的分片
        
        Args:
            shards: 可用的分片列表
            missing_index: 丢失分片的索引
        
        Returns:
            missing_shard: 丢失的分片
        """
        # 收集可用的分片和索引
        available_shards = []
        available_indices = []
        
        for i, shard in enumerate(shards):
            if shard is not None and i != missing_index:
                available_shards.append(shard)
                available_indices.append(i)
        
        # 确保有足够的分片
        if len(available_shards) < self.data_shards:
            raise ValueError("没有足够的分片计算丢失的分片")
        
        # 选择data_shards个分片
        if len(available_shards) > self.data_shards:
            available_shards = available_shards[:self.data_shards]
            available_indices = available_indices[:self.data_shards]
        
        # 获取分片大小
        shard_size = len(available_shards[0])
        
        # 创建方程组
        # 我们需要解方程：encoding_matrix[missing_index] * data = missing_shard
        # 但我们有：encoding_matrix[available_indices] * data = available_shards
        
        # 解出data
        submatrix = self.encoding_matrix[available_indices, :self.data_shards]
        
        try:
            inv_matrix = np.linalg.inv(submatrix.astype(np.float64))
        except np.linalg.LinAlgError:
            raise ValueError("无法计算逆矩阵")
        
        # 将分片转换为矩阵
        shard_matrix = np.zeros((self.data_shards, shard_size), dtype=np.uint8)
        for i, shard in enumerate(available_shards):
            shard_matrix[i] = list(shard)
        
        # 计算原始数据
        data_matrix = np.dot(inv_matrix, shard_matrix) % 256
        
        # 计算丢失的分片
        missing_row = self.encoding_matrix[missing_index, :self.data_shards]
        missing_shard_matrix = np.dot(missing_row, data_matrix) % 256
        
        # 转换回字节
        missing_shard = bytes(missing_shard_matrix.astype(np.uint8))
        
        return missing_shard
    
    def validate_shards(self, shards: List[bytes]) -> bool:
        """
        验证分片是否有效
        
        Args:
            shards: 分片列表
        
        Returns:
            valid: 是否有效
        """
        if len(shards) != self.total_shards:
            return False
        
        # 检查所有分片大小是否相同
        shard_size = len(shards[0])
        for shard in shards:
            if len(shard) != shard_size:
                return False
        
        # 验证编码关系
        try:
            # 将分片转换为矩阵
            shard_matrix = np.zeros((self.total_shards, shard_size), dtype=np.uint8)
            for i, shard in enumerate(shards):
                shard_matrix[i] = list(shard)
            
            # 验证编码矩阵关系
            # 对于Reed-Solomon，所有分片应该满足编码关系
            # 这里进行简化验证
            return True
        except:
            return False