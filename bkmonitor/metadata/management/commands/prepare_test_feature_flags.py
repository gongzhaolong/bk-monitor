# -*- coding: utf-8 -*-
"""
Django management command: 准备测试特性开关数据
用于创建 FeatureFlag 测试数据并刷新到 Consul 和 Redis
"""
from django.core.management.base import BaseCommand
from metadata.models.feature_flag import FeatureFlagConfig


class Command(BaseCommand):
    help = "准备测试特性开关数据并刷新到 Consul 和 Redis"

    def add_arguments(self, parser):
        parser.add_argument(
            "--refresh-consul",
            action="store_true",
            help="刷新到 Consul",
        )
        parser.add_argument(
            "--refresh-redis",
            action="store_true",
            help="刷新到 Redis",
        )
        parser.add_argument(
            "--refresh-all",
            action="store_true",
            help="刷新到 Consul 和 Redis（默认）",
        )

    def handle(self, *args, **options):
        # 准备测试数据
        feature_flags = {
            "must-vm-query": {
                "variations": {
                    "Default": False,
                    "true": True,
                    "false": False,
                },
                "targeting": [
                    {
                        "query": 'tableID in ["table_id_1", "table_id_2"]',
                        "percentage": {
                            "true": 100,
                            "false": 0,
                        },
                    }
                ],
                "defaultRule": {
                    "variation": "Default",
                },
            },
            "range-vm-query": {
                "variations": {
                    "Default": 0,
                    "true": 30000,
                },
                "targeting": [
                    {
                        "query": 'tableID in ["table_id_1", "table_id_3"]',
                        "percentage": {
                            "true": 100,
                        },
                    }
                ],
                "defaultRule": {
                    "variation": "Default",
                },
            },
        }

        refresh_consul = options.get("refresh_consul", False)
        refresh_redis = options.get("refresh_redis", False)
        refresh_all = options.get("refresh_all", False)

        # 如果没有指定，默认刷新到两者
        if not refresh_consul and not refresh_redis:
            refresh_all = True

        if refresh_all:
            refresh_consul = True
            refresh_redis = True

        self.stdout.write("=" * 60)
        self.stdout.write("准备测试特性开关数据")
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write(f"特性开关数量: {len(feature_flags)}")
        for flag_name in feature_flags.keys():
            self.stdout.write(f"  - {flag_name}")
        self.stdout.write("")

        # 刷新到 Consul
        if refresh_consul:
            self.stdout.write("=" * 60)
            self.stdout.write("刷新数据到 Consul")
            self.stdout.write("=" * 60)
            self.stdout.write("")

            try:
                FeatureFlagConfig.refresh_consul_feature_flag_config(feature_flags)
                self.stdout.write(self.style.SUCCESS("✓ 数据已刷新到 Consul"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ 刷新到 Consul 失败: {e}"))
                import traceback

                traceback.print_exc()

        # 刷新到 Redis
        if refresh_redis:
            self.stdout.write("")
            self.stdout.write("=" * 60)
            self.stdout.write("刷新数据到 Redis")
            self.stdout.write("=" * 60)
            self.stdout.write("")

            try:
                FeatureFlagConfig.refresh_redis_feature_flag_config(feature_flags)
                self.stdout.write(self.style.SUCCESS("✓ 数据已刷新到 Redis"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ 刷新到 Redis 失败: {e}"))
                import traceback

                traceback.print_exc()

        # 验证数据
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("验证数据")
        self.stdout.write("=" * 60)
        self.stdout.write("")

        if refresh_consul:
            try:
                all_configs = FeatureFlagConfig.get_all_consul_feature_flag_config()
                if all_configs:
                    self.stdout.write(self.style.SUCCESS("✓ Consul 验证成功"))
                    self.stdout.write(f"   配置数量: {len(all_configs)}")
                else:
                    self.stdout.write(self.style.WARNING("⚠️  Consul 中没有数据"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Consul 验证失败: {e}"))

        if refresh_redis:
            try:
                all_configs = FeatureFlagConfig.get_all_redis_feature_flag_config()
                if all_configs:
                    self.stdout.write(self.style.SUCCESS("✓ Redis 验证成功"))
                    self.stdout.write(f"   配置数量: {len(all_configs)}")
                else:
                    self.stdout.write(self.style.WARNING("⚠️  Redis 中没有数据"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Redis 验证失败: {e}"))

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ 所有操作完成！"))
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write("现在可以测试 API:")
        self.stdout.write(
            '  curl "http://localhost:8000/api/v3/meta/config/get_consul_feature_flag_config/"'
        )
        self.stdout.write(
            '  curl "http://localhost:8000/api/v3/meta/config/get_redis_feature_flag_config/"'
        )
        self.stdout.write(
            '  curl "http://localhost:8000/api/v3/meta/config/get_consul_feature_flag_config/?flag_name=must-vm-query"'
        )

