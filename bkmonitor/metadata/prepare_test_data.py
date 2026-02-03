#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
准备测试数据脚本
用于创建 ClusterInfo 测试数据并刷新到 Redis
"""
import os
import sys
import django

# 设置 Django 环境
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
packages_dir = os.path.join(project_root, "packages")
if packages_dir not in sys.path:
    sys.path.insert(0, packages_dir)
sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from metadata.models.storage import ClusterInfo


def prepare_test_data():
    """准备测试数据"""
    print("=" * 60)
    print("准备 MySQL 测试数据")
    print("=" * 60)
    print()
    
    # 检查是否已存在
    try:
        cluster = ClusterInfo.objects.get(cluster_id=1)
        print(f"⚠️  测试数据已存在: cluster_id={cluster.cluster_id}")
        print(f"   集群名称: {cluster.cluster_name}")
        print(f"   集群类型: {cluster.cluster_type}")
        print(f"   地址: {cluster.domain_name}:{cluster.port}")
        print()
        print("更新测试数据...")
        cluster.cluster_name = "test_influxdb_cluster"
        cluster.cluster_type = ClusterInfo.TYPE_INFLUXDB
        cluster.domain_name = "127.0.0.1"
        cluster.port = 4090
        cluster.schema = "http"
        cluster.username = "admin"
        cluster.password = "password123"
        cluster.description = "测试集群"
        cluster.is_default_cluster = False
        cluster.bk_tenant_id = "system"
        cluster.save()
        print("✓ 测试数据已更新")
    except ClusterInfo.DoesNotExist:
        print("创建测试数据...")
        cluster = ClusterInfo.objects.create(
            cluster_id=1,
            cluster_name="test_influxdb_cluster",
            cluster_type=ClusterInfo.TYPE_INFLUXDB,
            domain_name="127.0.0.1",
            port=4090,
            schema="http",
            username="admin",
            password="password123",
            description="测试集群",
            is_default_cluster=False,
            bk_tenant_id="system",
        )
        print(f"✓ 创建成功: cluster_id={cluster.cluster_id}")
        print(f"   集群名称: {cluster.cluster_name}")
        print(f"   集群类型: {cluster.cluster_type}")
        print(f"   地址: {cluster.domain_name}:{cluster.port}")
    
    print()
    print("=" * 60)
    print("刷新数据到 Redis")
    print("=" * 60)
    print()
    
    # 刷新到 Redis
    try:
        ClusterInfo.refresh_redis_storage_config()
        print("✓ 数据已刷新到 Redis")
    except Exception as e:
        print(f"✗ 刷新失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("验证 Redis 数据")
    print("=" * 60)
    print()
    
    # 验证
    try:
        config = ClusterInfo.get_redis_storage_config(1)
        if config:
            print("✓ 验证成功")
            print(f"   配置内容:")
            print(f"     address: {config.get('address')}")
            print(f"     username: {config.get('username')}")
            print(f"     password: {config.get('password')}")
            print(f"     type: {config.get('type')}")
            return True
        else:
            print("✗ 验证失败: Redis 中没有数据")
            return False
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = prepare_test_data()
    print()
    print("=" * 60)
    if success:
        print("✓ 所有操作完成！")
        print()
        print("现在可以测试 API:")
        print("  curl \"http://localhost:8000/api/v3/meta/config/get_redis_storage_config/?cluster_id=1\"")
    else:
        print("✗ 操作失败，请检查错误信息")
    print("=" * 60)

