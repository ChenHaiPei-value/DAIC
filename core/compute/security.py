"""
安全模块

负责节点认证、数据签名、证书管理等安全功能。
"""

import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import base64

logger = logging.getLogger(__name__)


class SecurityManager:
    """安全管理器"""
    
    def __init__(self, private_key: Optional[str] = None):
        """
        初始化安全管理器
        
        Args:
            private_key: 私钥（如果为None则生成新密钥）
        """
        self.private_key = private_key or self._generate_private_key()
        self.public_key = self._derive_public_key(self.private_key)
        self.certificates: Dict[str, Dict] = {}
        
        logger.info("安全管理器初始化完成")
    
    def _generate_private_key(self) -> str:
        """生成私钥"""
        # 在实际应用中应该使用真正的加密库
        # 这里使用UUID作为示例
        return str(uuid.uuid4())
    
    def _derive_public_key(self, private_key: str) -> str:
        """从私钥派生公钥"""
        # 在实际应用中应该使用真正的加密算法
        # 这里使用SHA256作为示例
        return hashlib.sha256(private_key.encode()).hexdigest()
    
    def generate_node_certificate(self, node_id: str, public_key: Optional[str] = None) -> str:
        """
        生成节点证书
        
        Args:
            node_id: 节点ID
            public_key: 节点公钥
            
        Returns:
            证书字符串
        """
        if public_key is None:
            public_key = self.public_key
        
        certificate = {
            "version": "1.0",
            "node_id": node_id,
            "public_key": public_key,
            "issuer": "daic-network",
            "issue_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "certificate_id": str(uuid.uuid4()),
        }
        
        # 签名证书
        signature = self.sign_data(json.dumps(certificate, sort_keys=True))
        certificate["signature"] = signature
        
        # 存储证书
        self.certificates[node_id] = certificate
        
        # 转换为字符串
        cert_str = json.dumps(certificate)
        
        logger.info(f"为节点 {node_id} 生成证书")
        return cert_str
    
    def generate_enhanced_certificate(
        self,
        node_id: str,
        node_type: str,
        public_key: str,
        gpu_info: Dict,
    ) -> str:
        """
        生成增强版节点证书
        
        Args:
            node_id: 节点ID
            node_type: 节点类型
            public_key: 节点公钥
            gpu_info: GPU硬件信息
            
        Returns:
            证书字符串
        """
        certificate = {
            "version": "2.0",
            "node_id": node_id,
            "node_type": node_type,
            "public_key": public_key,
            "gpu_info": gpu_info,
            "issuer": "daic-enhanced-network",
            "issue_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "certificate_id": str(uuid.uuid4()),
            "security_level": "enhanced",
            "capabilities": ["ai_training", "ai_inference", "federated_learning"],
        }
        
        # 签名证书
        signature = self.sign_data(json.dumps(certificate, sort_keys=True))
        certificate["signature"] = signature
        
        # 存储证书
        self.certificates[node_id] = certificate
        
        # 转换为字符串
        cert_str = json.dumps(certificate)
        
        logger.info(f"为增强版节点 {node_id} ({node_type}) 生成证书")
        return cert_str
    
    def sign_data(self, data: str) -> str:
        """
        签名数据
        
        Args:
            data: 要签名的数据
            
        Returns:
            签名
        """
        # 在实际应用中应该使用真正的数字签名算法
        # 这里使用HMAC-SHA256作为示例
        import hmac
        
        # 使用私钥作为密钥
        key = self.private_key.encode()
        message = data.encode()
        
        # 生成HMAC签名
        signature = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        return signature
    
    def verify_signature(self, data: str, signature: str, public_key: str) -> bool:
        """
        验证签名
        
        Args:
            data: 原始数据
            signature: 签名
            public_key: 公钥
            
        Returns:
            签名是否有效
        """
        # 在实际应用中应该使用真正的数字签名验证
        # 这里简化验证逻辑
        try:
            # 模拟验证过程
            expected_signature = self._simulate_signature(data, public_key)
            return signature == expected_signature
        except Exception as e:
            logger.error(f"签名验证失败: {e}")
            return False
    
    def _simulate_signature(self, data: str, public_key: str) -> str:
        """模拟签名生成（用于验证）"""
        # 在实际应用中应该使用真正的验证逻辑
        return hashlib.sha256((data + public_key).encode()).hexdigest()
    
    def verify_certificate(self, certificate_str: str) -> bool:
        """
        验证证书
        
        Args:
            certificate_str: 证书字符串
            
        Returns:
            证书是否有效
        """
        try:
            certificate = json.loads(certificate_str)
            
            # 检查证书格式
            required_fields = ["node_id", "public_key", "issuer", "issue_date", "expiry_date", "signature"]
            for field in required_fields:
                if field not in certificate:
                    logger.warning(f"证书缺少必要字段: {field}")
                    return False
            
            # 检查证书是否过期
            expiry_date = datetime.fromisoformat(certificate["expiry_date"])
            if datetime.now() > expiry_date:
                logger.warning(f"证书已过期: {certificate['node_id']}")
                return False
            
            # 验证签名
            cert_copy = certificate.copy()
            signature = cert_copy.pop("signature")
            
            # 重新生成数据字符串
            data = json.dumps(cert_copy, sort_keys=True)
            
            # 验证签名
            if not self.verify_signature(data, signature, certificate["public_key"]):
                logger.warning(f"证书签名无效: {certificate['node_id']}")
                return False
            
            logger.info(f"证书验证通过: {certificate['node_id']}")
            return True
            
        except Exception as e:
            logger.error(f"证书验证异常: {e}")
            return False
    
    def encrypt_data(self, data: str, public_key: str) -> str:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            public_key: 接收方公钥
            
        Returns:
            加密后的数据
        """
        # 在实际应用中应该使用真正的非对称加密
        # 这里使用简单的base64编码作为示例
        encoded = base64.b64encode(data.encode()).decode()
        return f"encrypted:{public_key[:8]}:{encoded}"
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的数据
            
        Returns:
            解密后的数据
        """
        # 在实际应用中应该使用真正的非对称解密
        # 这里使用简单的base64解码作为示例
        try:
            if encrypted_data.startswith("encrypted:"):
                parts = encrypted_data.split(":", 2)
                if len(parts) == 3:
                    encoded_data = parts[2]
                    decoded = base64.b64decode(encoded_data).decode()
                    return decoded
            return encrypted_data
        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            return encrypted_data
    
    def generate_session_key(self, node_id: str) -> str:
        """
        生成会话密钥
        
        Args:
            node_id: 节点ID
            
        Returns:
            会话密钥
        """
        # 生成随机会话密钥
        session_key = str(uuid.uuid4())
        
        # 记录会话
        logger.info(f"为节点 {node_id} 生成会话密钥")
        
        return session_key
    
    def validate_session(self, node_id: str, session_key: str) -> bool:
        """
        验证会话
        
        Args:
            node_id: 节点ID
            session_key: 会话密钥
            
        Returns:
            会话是否有效
        """
        # 在实际应用中应该检查会话过期时间等
        # 这里简化验证逻辑
        return len(session_key) == 36  # UUID长度
    
    def get_public_key(self) -> str:
        """获取公钥"""
        return self.public_key
    
    def get_certificate(self, node_id: str) -> Optional[Dict]:
        """获取证书"""
        return self.certificates.get(node_id)


# 演示函数
def demo_security_manager():
    """演示安全管理器"""
    print("="*50)
    print("安全管理器演示")
    print("="*50)
    
    # 创建安全管理器
    security = SecurityManager()
    
    # 生成证书
    certificate = security.generate_node_certificate("node_001")
    print(f"生成的证书: {certificate[:100]}...")
    
    # 验证证书
    is_valid = security.verify_certificate(certificate)
    print(f"证书验证: {'通过' if is_valid else '失败'}")
    
    # 数据签名和验证
    data = "Hello, DAIC Network!"
    signature = security.sign_data(data)
    print(f"数据签名: {signature[:32]}...")
    
    # 加密解密
    encrypted = security.encrypt_data(data, security.get_public_key())
    print(f"加密数据: {encrypted[:50]}...")
    
    decrypted = security.decrypt_data(encrypted)
    print(f"解密数据: {decrypted}")
    
    # 生成会话密钥
    session_key = security.generate_session_key("node_001")
    print(f"会话密钥: {session_key}")
    
    # 验证会话
    is_session_valid = security.validate_session("node_001", session_key)
    print(f"会话验证: {'有效' if is_session_valid else '无效'}")
    
    print("\n" + "="*50)
    print("演示完成!")
    print("="*50)


if __name__ == "__main__":
    demo_security_manager()