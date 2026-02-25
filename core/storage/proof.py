"""
存储证明模块

实现零知识存储证明系统，用于验证节点确实存储了数据。
"""

import hashlib
import os
import time
import uuid
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


class ZKStorageProof:
    """零知识存储证明系统"""
    
    def __init__(self, proof_validity_period: int = 3600):
        """
        初始化存储证明系统
        
        Args:
            proof_validity_period: 证明有效期（秒）
        """
        self.proof_validity_period = proof_validity_period
        self.backend = default_backend()
        
        # 初始化椭圆曲线（使用P-256曲线）
        self.curve = ec.SECP256R1()
    
    def generate_proof(self, data_chunk: bytes, node_id: str, 
                      private_key: Optional[bytes] = None) -> Dict:
        """
        生成零知识存储证明
        
        Args:
            data_chunk: 数据块
            node_id: 存储节点ID
            private_key: 可选的私钥（用于签名）
        
        Returns:
            proof: 存储证明字典
        """
        timestamp = time.time()
        
        # 1. 计算数据承诺
        data_commitment = self._compute_commitment(data_chunk)
        
        # 2. 生成随机挑战
        challenge = self._generate_challenge(data_commitment, node_id, timestamp)
        
        # 3. 生成响应（模拟零知识证明）
        response = self._generate_response(data_chunk, challenge)
        
        # 4. 生成证明ID
        proof_id = self._generate_proof_id(data_commitment, node_id, timestamp)
        
        # 5. 签名证明（如果提供了私钥）
        signature = None
        if private_key:
            signature = self._sign_proof({
                'proof_id': proof_id,
                'data_commitment': data_commitment,
                'challenge': challenge,
                'response': response,
                'timestamp': timestamp,
                'node_id': node_id
            }, private_key)
        
        proof = {
            'proof_id': proof_id,
            'data_commitment': data_commitment,
            'challenge': challenge,
            'response': response,
            'timestamp': timestamp,
            'node_id': node_id,
            'signature': signature,
            'validity_period': self.proof_validity_period
        }
        
        return proof
    
    def verify_proof(self, proof: Dict, public_key: Optional[bytes] = None, 
                    challenge: Optional[bytes] = None) -> bool:
        """
        验证存储证明
        
        Args:
            proof: 存储证明字典
            public_key: 可选的公钥（用于验证签名）
            challenge: 可选的挑战值（用于重新验证）
        
        Returns:
            valid: 证明是否有效
        """
        try:
            # 1. 验证基本字段
            required_fields = ['proof_id', 'data_commitment', 'challenge', 
                             'response', 'timestamp', 'node_id']
            for field in required_fields:
                if field not in proof:
                    return False
            
            # 2. 验证时间有效性
            current_time = time.time()
            if current_time - proof['timestamp'] > proof.get('validity_period', self.proof_validity_period):
                return False
            
            # 3. 验证证明ID
            expected_proof_id = self._generate_proof_id(
                proof['data_commitment'],
                proof['node_id'],
                proof['timestamp']
            )
            if proof['proof_id'] != expected_proof_id:
                return False
            
            # 4. 验证挑战一致性
            expected_challenge = self._generate_challenge(
                proof['data_commitment'],
                proof['node_id'],
                proof['timestamp']
            )
            if proof['challenge'] != expected_challenge:
                return False
            
            # 5. 验证响应（模拟零知识验证）
            if not self._verify_response(proof['response'], proof['challenge']):
                return False
            
            # 6. 验证签名（如果提供了公钥）
            if public_key and proof.get('signature'):
                if not self._verify_signature(proof, proof['signature'], public_key):
                    return False
            
            # 7. 可选：重新验证挑战
            if challenge:
                if not self._verify_challenge(proof, challenge):
                    return False
            
            return True
            
        except (KeyError, ValueError, TypeError):
            return False
    
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        生成密钥对
        
        Returns:
            private_key: 私钥（PEM格式）
            public_key: 公钥（PEM格式）
        """
        # 生成私钥
        private_key = ec.generate_private_key(self.curve, self.backend)
        
        # 获取公钥
        public_key = private_key.public_key()
        
        # 序列化密钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def _compute_commitment(self, data: bytes) -> str:
        """
        计算数据承诺（使用Merkle树根哈希）
        
        Args:
            data: 数据
        
        Returns:
            commitment: 数据承诺（十六进制字符串）
        """
        # 简单实现：使用SHA-256哈希
        # 实际实现应该使用Merkle树
        return hashlib.sha256(data).hexdigest()
    
    def _generate_challenge(self, commitment: str, node_id: str, timestamp: float) -> str:
        """
        生成挑战
        
        Args:
            commitment: 数据承诺
            node_id: 节点ID
            timestamp: 时间戳
        
        Returns:
            challenge: 挑战值（十六进制字符串）
        """
        # 使用随机数和上下文生成挑战
        random_seed = os.urandom(32)
        context = f"{commitment}:{node_id}:{timestamp}:{random_seed.hex()}"
        
        return hashlib.sha256(context.encode()).hexdigest()
    
    def _generate_response(self, data: bytes, challenge: str) -> Dict:
        """
        生成响应（模拟零知识证明）
        
        Args:
            data: 数据
            challenge: 挑战值
        
        Returns:
            response: 响应字典
        """
        # 这是一个简化版本
        # 实际零知识证明实现会更复杂
        
        # 计算数据的Merkle路径（简化）
        data_hash = hashlib.sha256(data).hexdigest()
        
        # 生成模拟的零知识证明
        proof_elements = []
        for i in range(4):  # 简化：4个证明元素
            element = hashlib.sha256(
                f"{data_hash}:{challenge}:{i}".encode()
            ).hexdigest()
            proof_elements.append(element)
        
        return {
            'data_hash': data_hash,
            'proof_elements': proof_elements,
            'verification_data': self._generate_verification_data(data, challenge)
        }
    
    def _verify_response(self, response: Dict, challenge: str) -> bool:
        """
        验证响应
        
        Args:
            response: 响应字典
            challenge: 挑战值
        
        Returns:
            valid: 响应是否有效
        """
        try:
            # 验证响应结构
            if 'data_hash' not in response or 'proof_elements' not in response:
                return False
            
            # 验证证明元素
            proof_elements = response['proof_elements']
            if not isinstance(proof_elements, list) or len(proof_elements) != 4:
                return False
            
            # 验证每个证明元素
            data_hash = response['data_hash']
            for i, element in enumerate(proof_elements):
                expected = hashlib.sha256(
                    f"{data_hash}:{challenge}:{i}".encode()
                ).hexdigest()
                if element != expected:
                    return False
            
            # 验证验证数据（如果存在）
            if 'verification_data' in response:
                if not self._verify_verification_data(response['verification_data']):
                    return False
            
            return True
            
        except (KeyError, ValueError, TypeError):
            return False
    
    def _generate_proof_id(self, commitment: str, node_id: str, timestamp: float) -> str:
        """
        生成证明ID
        
        Args:
            commitment: 数据承诺
            node_id: 节点ID
            timestamp: 时间戳
        
        Returns:
            proof_id: 证明ID
        """
        content = f"{commitment}:{node_id}:{timestamp}:{os.urandom(16).hex()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _sign_proof(self, proof_data: Dict, private_key: bytes) -> bytes:
        """
        签名证明
        
        Args:
            proof_data: 证明数据
            private_key: 私钥（PEM格式）
        
        Returns:
            signature: 签名
        """
        # 加载私钥
        private_key_obj = serialization.load_pem_private_key(
            private_key,
            password=None,
            backend=self.backend
        )
        
        # 准备签名数据
        data_to_sign = self._prepare_data_for_signing(proof_data)
        
        # 签名
        signature = private_key_obj.sign(
            data_to_sign,
            ec.ECDSA(hashes.SHA256())
        )
        
        return signature
    
    def _verify_signature(self, proof: Dict, signature: bytes, public_key: bytes) -> bool:
        """
        验证签名
        
        Args:
            proof: 证明字典
            signature: 签名
            public_key: 公钥（PEM格式）
        
        Returns:
            valid: 签名是否有效
        """
        try:
            # 加载公钥
            public_key_obj = serialization.load_pem_public_key(
                public_key,
                backend=self.backend
            )
            
            # 准备验证数据
            data_to_verify = self._prepare_data_for_signing({
                'proof_id': proof['proof_id'],
                'data_commitment': proof['data_commitment'],
                'challenge': proof['challenge'],
                'response': proof['response'],
                'timestamp': proof['timestamp'],
                'node_id': proof['node_id']
            })
            
            # 验证签名
            public_key_obj.verify(
                signature,
                data_to_verify,
                ec.ECDSA(hashes.SHA256())
            )
            
            return True
            
        except (InvalidSignature, ValueError, TypeError):
            return False
    
    def _prepare_data_for_signing(self, data: Dict) -> bytes:
        """
        准备签名数据
        
        Args:
            data: 要签名的数据
        
        Returns:
            data_bytes: 用于签名的字节数据
        """
        # 将字典转换为规范的字符串表示
        canonical_str = self._to_canonical_string(data)
        return canonical_str.encode('utf-8')
    
    def _to_canonical_string(self, data: Dict) -> str:
        """
        将字典转换为规范字符串
        
        Args:
            data: 字典数据
        
        Returns:
            canonical_str: 规范字符串
        """
        # 按键排序以确保一致性
        sorted_items = sorted(data.items())
        
        parts = []
        for key, value in sorted_items:
            if isinstance(value, dict):
                value_str = self._to_canonical_string(value)
            elif isinstance(value, list):
                value_str = ','.join(str(v) for v in value)
            else:
                value_str = str(value)
            parts.append(f"{key}:{value_str}")
        
        return '|'.join(parts)
    
    def _generate_verification_data(self, data: bytes, challenge: str) -> Dict:
        """
        生成验证数据
        
        Args:
            data: 数据
            challenge: 挑战值
        
        Returns:
            verification_data: 验证数据
        """
        # 计算数据的多个哈希以增加验证强度
        data_hash = hashlib.sha256(data).hexdigest()
        double_hash = hashlib.sha256(data_hash.encode()).hexdigest()
        
        # 生成随机验证点
        random_points = []
        for i in range(3):
            point_hash = hashlib.sha256(
                f"{data_hash}:{challenge}:point:{i}:{os.urandom(8).hex()}".encode()
            ).hexdigest()
            random_points.append(point_hash)
        
        return {
            'data_hash': data_hash,
            'double_hash': double_hash,
            'random_points': random_points,
            'timestamp': time.time()
        }
    
    def _verify_verification_data(self, verification_data: Dict) -> bool:
        """
        验证验证数据
        
        Args:
            verification_data: 验证数据
        
        Returns:
            valid: 验证数据是否有效
        """
        try:
            # 检查必需字段
            required_fields = ['data_hash', 'double_hash', 'random_points', 'timestamp']
            for field in required_fields:
                if field not in verification_data:
                    return False
            
            # 验证双重哈希
            data_hash = verification_data['data_hash']
            expected_double_hash = hashlib.sha256(data_hash.encode()).hexdigest()
            if verification_data['double_hash'] != expected_double_hash:
                return False
            
            # 验证随机点
            random_points = verification_data['random_points']
            if not isinstance(random_points, list) or len(random_points) != 3:
                return False
            
            # 验证时间戳（不要太旧）
            timestamp = verification_data['timestamp']
            if time.time() - timestamp > 3600:  # 1小时
                return False
            
            return True
            
        except (KeyError, ValueError, TypeError):
            return False
    
    def _verify_challenge(self, proof: Dict, challenge: bytes) -> bool:
        """
        验证挑战
        
        Args:
            proof: 证明字典
            challenge: 挑战值
        
        Returns:
            valid: 挑战是否有效
        """
        # 重新计算挑战
        expected_challenge = self._generate_challenge(
            proof['data_commitment'],
            proof['node_id'],
            proof['timestamp']
        )
        
        # 比较挑战
        return challenge.hex() == expected_challenge
    
    def generate_batch_proof(self, data_chunks: list, node_id: str, 
                           private_key: Optional[bytes] = None) -> Dict:
        """
        生成批量存储证明
        
        Args:
            data_chunks: 数据块列表
            node_id: 节点ID
            private_key: 可选的私钥
        
        Returns:
            batch_proof: 批量证明
        """
        timestamp = time.time()
        
        # 为每个数据块生成证明
        proofs = []
        for i, chunk in enumerate(data_chunks):
            proof = self.generate_proof(chunk, node_id, None)  # 先不签名
            proofs.append(proof)
        
        # 计算批量承诺
        batch_commitment = self._compute_batch_commitment(proofs)
        
        # 生成批量证明ID
        batch_proof_id = self._generate_batch_proof_id(batch_commitment, node_id, timestamp)
        
        # 签名批量证明
        signature = None
        if private_key:
            signature = self._sign_proof({
                'batch_proof_id': batch_proof_id,
                'batch_commitment': batch_commitment,
                'proof_count': len(proofs),
                'timestamp': timestamp,
                'node_id': node_id
            }, private_key)
        
        batch_proof = {
            'batch_proof_id': batch_proof_id,
            'batch_commitment': batch_commitment,
            'proofs': proofs,
            'proof_count': len(proofs),
            'timestamp': timestamp,
            'node_id': node_id,
            'signature': signature
        }
        
        return batch_proof
    
    def _compute_batch_commitment(self, proofs: list) -> str:
        """
        计算批量承诺
        
        Args:
            proofs: 证明列表
        
        Returns:
            commitment: 批量承诺
        """
        # 将所有证明的数据承诺连接起来
        all_commitments = ''.join(proof['data_commitment'] for proof in proofs)
        return hashlib.sha256(all_commitments.encode()).hexdigest()
    
    def _generate_batch_proof_id(self, commitment: str, node_id: str, timestamp: float) -> str:
        """
        生成批量证明ID
        
        Args:
            commitment: 批量承诺
            node_id: 节点ID
            timestamp: 时间戳
        
        Returns:
            proof_id: 批量证明ID
        """
        content = f"batch:{commitment}:{node_id}:{timestamp}:{os.urandom(16).hex()}"
        return hashlib.sha256(content.encode()).hexdigest()