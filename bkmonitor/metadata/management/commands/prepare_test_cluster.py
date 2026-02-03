# -*- coding: utf-8 -*-
"""
Django management command: 准备测试集群数据
用于创建 ClusterInfo 测试数据并刷新到 Redis
"""
from django.core.management.base import BaseCommand
from metadata.models.storage import ClusterInfo


class Command(BaseCommand):
    help = "准备测试集群数据并刷新到 Redis"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cluster-id",
            type=int,
            default=1,
            help="要创建的集群ID",
        )
        parser.add_argument(
            "--cluster-type",
            type=str,
            default="influxdb",
            choices=[
                "influxdb",
                "kafka",
                "redis",
                "elasticsearch",
                "victoria_metrics",
                "doris",
            ],
            help="集群类型",
        )
        parser.add_argument(
            "--domain",
            type=str,
            default="127.0.0.1",
            help="集群域名或IP",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=4090,
            help="集群端口",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="用户名",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="password123",
            help="密码",
        )

    def handle(self, *args, **options):
        cluster_id = options["cluster_id"]
        cluster_type = options["cluster_type"]
        domain = options["domain"]
        port = options["port"]
        username = options["username"]
        password = options["password"]

        self.stdout.write("=" * 60)
        self.stdout.write("准备 MySQL 测试数据")
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # 检查是否已存在
        try:
            cluster = ClusterInfo.objects.get(cluster_id=cluster_id)
            self.stdout.write(self.style.WARNING(f"⚠️  测试数据已存在: cluster_id={cluster.cluster_id}"))
            self.stdout.write(f"   集群名称: {cluster.cluster_name}")
            self.stdout.write(f"   集群类型: {cluster.cluster_type}")
            self.stdout.write(f"   地址: {cluster.domain_name}:{cluster.port}")
            self.stdout.write("")
            self.stdout.write("更新测试数据...")

            cluster.cluster_name = f"test_{cluster_type}_cluster"
            cluster.cluster_type = cluster_type
            cluster.domain_name = domain
            cluster.port = port
            cluster.schema = "http"
            cluster.username = username
            cluster.password = password
            cluster.description = "测试集群"
            cluster.is_default_cluster = False
            cluster.bk_tenant_id = "system"
            cluster.save()

            self.stdout.write(self.style.SUCCESS("✓ 测试数据已更新"))
        except ClusterInfo.DoesNotExist:
            self.stdout.write("创建测试数据...")

            cluster = ClusterInfo.objects.create(
                cluster_id=cluster_id,
                cluster_name=f"test_{cluster_type}_cluster",
                cluster_type=cluster_type,
                domain_name=domain,
                port=port,
                schema="http",
                username=username,
                password=password,
                description="测试集群",
                is_default_cluster=False,
                bk_tenant_id="system",
            )

            self.stdout.write(self.style.SUCCESS(f"✓ 创建成功: cluster_id={cluster.cluster_id}"))
            self.stdout.write(f"   集群名称: {cluster.cluster_name}")
            self.stdout.write(f"   集群类型: {cluster.cluster_type}")
            self.stdout.write(f"   地址: {cluster.domain_name}:{cluster.port}")

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("刷新数据到 Redis")
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # 刷新到 Redis
        try:
            ClusterInfo.refresh_redis_storage_config()
            self.stdout.write(self.style.SUCCESS("✓ 数据已刷新到 Redis"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ 刷新失败: {e}"))
            import traceback

            traceback.print_exc()
            return

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("验证 Redis 数据")
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # 验证
        try:
            config = ClusterInfo.get_redis_storage_config(cluster_id)
            if config:
                self.stdout.write(self.style.SUCCESS("✓ 验证成功"))
                self.stdout.write(f"   配置内容:")
                self.stdout.write(f"     address: {config.get('address')}")
                self.stdout.write(f"     username: {config.get('username')}")
                self.stdout.write(f"     password: {config.get('password')}")
                self.stdout.write(f"     type: {config.get('type')}")
            else:
                self.stdout.write(self.style.ERROR("✗ 验证失败: Redis 中没有数据"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ 验证失败: {e}"))
            import traceback

            traceback.print_exc()
            return

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ 所有操作完成！"))
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write("现在可以测试 API:")
        self.stdout.write(
            f'  curl "http://localhost:8000/api/v3/meta/config/get_redis_storage_config/?cluster_id={cluster_id}"'
        )

