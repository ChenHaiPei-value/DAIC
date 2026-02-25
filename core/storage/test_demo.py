#!/usr/bin/env python3
"""
DAIC分布式存储系统演示脚本

这个脚本演示了如何使用DAIC分布式存储系统。
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from core.storage.client import DAICStorageClient


def main():
    """主函数"""
    print("=" * 70)
    print("DAIC分布式存储系统演示")
    print("=" * 70)
    
    # 创建客户端
    config = {
        'local_storage_dir': '/tmp/daic_demo',
        'chunk_size': 1024 * 64,  # 64KB分片
        'data_shards': 3,
        'parity_shards': 2,
        'min_reputation': 0.6,
        'max_latency': 500.0,
        'proof_validity_period': 1800
    }
    
    client = DAICStorageClient(config)
    
    print("\n1. 初始化客户端...")
    print(f"   本地存储目录: {config['local_storage_dir']}")
    print(f"   分片大小: {config['chunk_size']} 字节")
    print(f"   数据分片: {config['data_shards']}")
    print(f"   校验分片: {config['parity_shards']}")
    
    # 运行交互式演示
    client.run_interactive_demo()


def quick_demo():
    """快速演示"""
    print("=" * 70)
    print("DAIC分布式存储系统 - 快速演示")
    print("=" * 70)
    
    # 创建客户端
    client = DAICStorageClient({
        'local_storage_dir': '/tmp/daic_quick_demo'
    })
    
    # 运行完整演示
    client.demo_upload_download()


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 70)
    print("DAIC分布式存储系统 - 基本功能测试")
    print("=" * 70)
    
    import tempfile
    import hashlib
    
    # 创建客户端
    client = DAICStorageClient({
        'local_storage_dir': '/tmp/daic_test'
    })
    
    # 添加测试节点（需要至少5个节点，因为纠删码生成5个分片）
    client.add_test_nodes(5)
    
    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        test_content = b"Hello, DAIC Distributed Storage System!\n" * 100
        f.write(test_content)
        test_file = f.name
    
    try:
        print("\n1. 测试文件上传...")
        file_id = client.upload_file(
            test_file,
            redundancy=2,
            optimize_for="balanced"
        )
        print(f"   上传成功! 文件ID: {file_id}")
        
        print("\n2. 测试列出文件...")
        files = client.list_files()
        print(f"   找到 {len(files)} 个文件")
        for file_info in files:
            print(f"   - {file_info['filename']} ({file_info['size']} bytes)")
        
        print("\n3. 测试获取文件信息...")
        file_info = client.get_file_info(file_id)
        if file_info:
            print(f"   文件名: {file_info['filename']}")
            print(f"   文件大小: {file_info['size']} bytes")
            print(f"   分片数量: {file_info['shard_count']}")
            print(f"   冗余因子: {file_info['redundancy']}")
            print(f"   存储节点: {len(file_info['nodes'])} 个")
        
        print("\n4. 测试验证文件完整性...")
        verification = client.verify_file_integrity(file_id)
        print(f"   整体状态: {verification['overall_status']}")
        print(f"   有效分片: {verification['valid_shards']}/{verification['shards_checked']}")
        
        print("\n5. 测试文件下载...")
        output_file = tempfile.mktemp(suffix='_downloaded.txt')
        client.download_file(file_id, output_file)
        
        # 验证文件内容
        with open(test_file, 'rb') as f1, open(output_file, 'rb') as f2:
            original_hash = hashlib.sha256(f1.read()).hexdigest()
            downloaded_hash = hashlib.sha256(f2.read()).hexdigest()
            
            if original_hash == downloaded_hash:
                print("   验证: 文件内容一致 ✓")
            else:
                print("   验证: 文件内容不一致 ✗")
        
        print("\n6. 测试统计信息...")
        stats = client.get_statistics()
        print(f"   总文件数: {stats['total_files']}")
        print(f"   上传文件数: {stats['files_uploaded']}")
        print(f"   下载文件数: {stats['files_downloaded']}")
        print(f"   总上传数据: {stats['total_bytes_uploaded']} bytes")
        print(f"   总下载数据: {stats['total_bytes_downloaded']} bytes")
        
        print("\n7. 测试文件删除...")
        client.delete_file(file_id)
        print("   删除成功!")
        
        # 验证文件已删除
        files_after_delete = client.list_files()
        print(f"   删除后文件数: {len(files_after_delete)}")
        
        print("\n✅ 所有测试通过!")
        
    finally:
        # 清理临时文件
        if os.path.exists(test_file):
            os.unlink(test_file)
        if 'output_file' in locals() and os.path.exists(output_file):
            os.unlink(output_file)


def test_error_handling():
    """测试错误处理"""
    print("=" * 70)
    print("DAIC分布式存储系统 - 错误处理测试")
    print("=" * 70)
    
    client = DAICStorageClient({
        'local_storage_dir': '/tmp/daic_error_test'
    })
    
    print("\n1. 测试上传不存在的文件...")
    try:
        client.upload_file("/tmp/nonexistent_file.txt")
        print("   ❌ 应该抛出异常但没有")
    except FileNotFoundError as e:
        print(f"   ✅ 正确抛出异常: {str(e)}")
    except Exception as e:
        print(f"   ⚠️ 抛出其他异常: {type(e).__name__}: {str(e)}")
    
    print("\n2. 测试下载不存在的文件...")
    try:
        client.download_file("nonexistent_file_id", "/tmp/output.txt")
        print("   ❌ 应该抛出异常但没有")
    except FileNotFoundError as e:
        print(f"   ✅ 正确抛出异常: {str(e)}")
    except Exception as e:
        print(f"   ⚠️ 抛出其他异常: {type(e).__name__}: {str(e)}")
    
    print("\n3. 测试验证不存在的文件...")
    result = client.verify_file_integrity("nonexistent_file_id")
    if result['overall_status'] == 'error':
        print(f"   ✅ 正确返回错误状态: {result.get('error', '未知错误')}")
    else:
        print(f"   ❌ 应该返回错误状态但没有: {result}")
    
    print("\n✅ 错误处理测试完成!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DAIC分布式存储系统演示')
    parser.add_argument('--mode', choices=['interactive', 'quick', 'test', 'errors'], 
                       default='interactive', help='演示模式')
    
    args = parser.parse_args()
    
    if args.mode == 'interactive':
        main()
    elif args.mode == 'quick':
        quick_demo()
    elif args.mode == 'test':
        test_basic_functionality()
    elif args.mode == 'errors':
        test_error_handling()
    else:
        print(f"未知模式: {args.mode}")
        sys.exit(1)