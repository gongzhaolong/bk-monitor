"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2025 Tencent. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import logging
import re
import time
from typing import Optional, Any

from django.conf import settings
from metadata import config
from metadata.utils import consul_tools
from metadata.utils.redis_tools import RedisTools

logger = logging.getLogger("metadata")


class FeatureFlagConfig:
    """
    特性开关配置管理类
    用于管理特性开关配置的读取和写入，支持 Redis 和 Consul 两种存储方式
    参考 storage.py 中 ClusterInfo 的实现方式
    """

    # Consul 配置路径
    CONSUL_PREFIX_PATH = f"{config.CONSUL_PATH}/unify-query/data/feature_flag"
    # CONSUL_VERSION_PATH = f"{config.CONSUL_PATH}/unify-query/version/feature_flag"
    
    # Redis 配置路径，参考 Consul 路径结构
    REDIS_PREFIX_KEY = "bkmonitorv3:unify-query:data:feature_flag"
    # REDIS_VERSION_KEY = "bkmonitorv3:unify-query:version:feature_flag"

    @classmethod
    def refresh_consul_feature_flag_config(cls, feature_flags: dict):
        """
        刷新特性开关配置到 Consul，参考 refresh_consul_storage_config 方法实现
        
        功能说明：
        1. 将所有特性开关配置合并为一个 JSON 对象
        2. 写入到 Consul，路径格式为: {CONSUL_PATH}/unify-query/data/feature_flag
        3. 支持复杂的特性开关格式，包含 variations、targeting、defaultRule
        
        Consul 存储格式：
        - Key: {CONSUL_PATH}/unify-query/data/feature_flag
        - Value: JSON 字典，包含所有特性开关配置，格式如下：
          {
            "must-vm-query": {
              "variations": {
                "Default": false,
                "true": true,
                "false": false
              },
              "targeting": [{
                "query": "tableID in [\"table_id_1\", \"table_id_2\"]",
                "percentage": {
                  "true": 100,
                  "false": 0
                }
              }],
              "defaultRule": {
                "variation": "Default"
              }
            },
            "range-vm-query": {
              ...
            }
          }
        
        :param feature_flags: 特性开关配置字典，格式为 {flag_name: flag_config}
                            flag_config 包含 variations、targeting、defaultRule 等字段
        :return: None
        """
        # 从 settings 读取 Consul 配置，如果没有则使用默认值
        consul_host = getattr(settings, "CONSUL_CLIENT_HOST", "127.0.0.1")
        consul_port = getattr(settings, "CONSUL_CLIENT_PORT", 8500)
        hash_consul = consul_tools.HashConsul(host=consul_host, port=consul_port)
        
        # 1. 将所有特性开关配置合并为一个 JSON 对象
        # 直接使用传入的 feature_flags 字典，它已经包含了所有 flag 的配置
        config_value = feature_flags
        
        # 2. 构建 Consul 路径，格式: {CONSUL_PATH}/unify-query/data/feature_flag
        consul_path = cls.CONSUL_PREFIX_PATH
        
        # 3. 写入 Consul（所有 flags 存储在一个 key 中）
        hash_consul.put(key=consul_path, value=config_value)
        logger.debug(f"consul path->[{consul_path}] is refresh with {len(feature_flags)} feature flags success.")
        
        logger.info(f"all feature flag config is refresh to consul success count->[{len(feature_flags)}].")

    @classmethod
    def refresh_redis_feature_flag_config(cls, feature_flags: dict):
        """
        刷新特性开关配置到 Redis，参考 refresh_redis_storage_config 方法实现
        
        功能说明：
        1. 将所有特性开关配置合并为一个 JSON 对象
        2. 写入到 Redis，key 格式为: bkmonitorv3:unify-query:data:feature_flag
        3. 支持复杂的特性开关格式，包含 variations、targeting、defaultRule
        
        Redis 存储格式：
        - Key: bkmonitorv3:unify-query:data:feature_flag
        - Value: JSON 字符串，包含所有特性开关配置，格式如下：
          {
            "must-vm-query": {
              "variations": {
                "Default": false,
                "true": true,
                "false": false
              },
              "targeting": [{
                "query": "tableID in [\"table_id_1\", \"table_id_2\"]",
                "percentage": {
                  "true": 100,
                  "false": 0
                }
              }],
              "defaultRule": {
                "variation": "Default"
              }
            },
            "range-vm-query": {
              ...
            }
          }
        
        :param feature_flags: 特性开关配置字典，格式为 {flag_name: flag_config}
                            flag_config 包含 variations、targeting、defaultRule 等字段
        :return: None
        """
        # 1. 将所有特性开关配置合并为一个 JSON 对象
        # 直接使用传入的 feature_flags 字典，它已经包含了所有 flag 的配置
        config_value = feature_flags
        
        # 2. 构建 Redis key，格式: bkmonitorv3:unify-query:data:feature_flag
        redis_key = cls.REDIS_PREFIX_KEY
        
        # 3. 将配置信息序列化为 JSON 字符串并写入 Redis（所有 flags 存储在一个 key 中）
        RedisTools().client.set(redis_key, json.dumps(config_value))
        logger.debug(f"redis key->[{redis_key}] is refresh with {len(feature_flags)} feature flags success.")
        
        logger.info(f"all feature flag config is refresh to redis success count->[{len(feature_flags)}].")

    @classmethod
    def get_all_consul_feature_flag_config(cls) -> Optional[dict]:
        """
        从 Consul 读取所有特性开关配置
        
        功能说明：
        1. 从 Consul 读取所有特性开关配置（单个 key）
        2. 返回包含所有 flags 的配置字典
        
        Consul 路径格式：
        - Key: {CONSUL_PATH}/unify-query/data/feature_flag
        
        返回值格式：
        {
            "must-vm-query": {
                "variations": {...},
                "targeting": [...],
                "defaultRule": {...}
            },
            "range-vm-query": {
                ...
            }
        }
        
        :return: 包含所有 flags 的配置字典，如果不存在或读取失败则返回 None
        """
        # 从 settings 读取 Consul 配置，如果没有则使用默认值
        consul_host = getattr(settings, "CONSUL_CLIENT_HOST", "127.0.0.1")
        consul_port = getattr(settings, "CONSUL_CLIENT_PORT", 8500)
        hash_consul = consul_tools.HashConsul(host=consul_host, port=consul_port)
        
        # 构建 Consul 路径（所有 flags 存储在一个 key 中）
        consul_path = cls.CONSUL_PREFIX_PATH
        
        try:
            # 从 Consul 读取配置数据
            index, consul_data = hash_consul.get(consul_path)
            
            if consul_data and consul_data.get("Value"):
                # 获取 Value 字段（可能是 bytes 或字符串）
                value_str = consul_data["Value"]
                
                # 如果 Value 是 bytes，需要先解码为字符串
                if isinstance(value_str, bytes):
                    value_str = value_str.decode("utf-8")
                
                # 如果 Value 是字符串，需要解析 JSON
                if isinstance(value_str, str):
                    return json.loads(value_str)
                # 如果已经是字典，直接返回
                elif isinstance(value_str, dict):
                    return value_str
            
            # 如果 Consul 中没有该 key，返回 None
            return None
            
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"get all consul feature flag config error, error->[{e}]")
            return None

    @classmethod
    def get_consul_feature_flag_config(cls, flag_name: str) -> Optional[dict]:
        """
        从 Consul 读取特性开关配置，参考 Consul 的 get 方法实现
        
        功能说明：
        1. 从 Consul 读取所有特性开关配置（单个 key）
        2. 从配置中提取指定 flag_name 的配置
        3. 解析并返回配置字典
        4. 如果配置不存在或读取失败，返回 None
        
        Consul 路径格式：
        - Key: {CONSUL_PATH}/unify-query/data/feature_flag
        
        返回值格式：
        {
            "variations": {
              "Default": <default_value>,
              "true": <true_value>,
              "false": <false_value>
            },
            "targeting": [{
              "query": "tableID in [\"table_id_1\", \"table_id_2\"]",
              "percentage": {
                "true": 100,
                "false": 0
              }
            }],
            "defaultRule": {
              "variation": "Default"
            }
          }
        
        使用场景：
        - 查询模块需要获取特性开关配置时，从 Consul 读取
        - 如果 Consul 中没有配置，可以回退到从数据库或 Redis 读取
        
        :param flag_name: 特性开关名称
        :return: 配置字典，如果不存在或读取失败则返回 None
        """
        # 从 settings 读取 Consul 配置，如果没有则使用默认值
        consul_host = getattr(settings, "CONSUL_CLIENT_HOST", "127.0.0.1")
        consul_port = getattr(settings, "CONSUL_CLIENT_PORT", 8500)
        hash_consul = consul_tools.HashConsul(host=consul_host, port=consul_port)
        
        # 构建 Consul 路径（所有 flags 存储在一个 key 中）
        consul_path = cls.CONSUL_PREFIX_PATH
        
        try:
            # 从 Consul 读取配置数据
            # Consul 返回格式: (index, value_dict)，其中 value_dict["Value"] 是 JSON 字符串
            index, consul_data = hash_consul.get(consul_path)
            
            if consul_data and consul_data.get("Value"):
                # 获取 Value 字段（可能是 bytes 或字符串）
                value_str = consul_data["Value"]
                
                # 如果 Value 是 bytes，需要先解码为字符串
                if isinstance(value_str, bytes):
                    value_str = value_str.decode("utf-8")
                
                # 如果 Value 是字符串，需要解析 JSON
                if isinstance(value_str, str):
                    all_flags = json.loads(value_str)
                # 如果已经是字典，直接使用
                elif isinstance(value_str, dict):
                    all_flags = value_str
                else:
                    return None
                
                # 从所有 flags 中提取指定 flag_name 的配置
                if isinstance(all_flags, dict) and flag_name in all_flags:
                    return all_flags[flag_name]
            
            # 如果 Consul 中没有该 key 或 flag_name 不存在，返回 None
            return None
            
        except Exception as e:  # pylint: disable=broad-except
            # 捕获所有异常，避免因为 Consul 连接问题或数据格式问题导致程序崩溃
            logger.error(f"get consul feature flag config error, flag_name->[{flag_name}], error->[{e}]")
            return None

    @classmethod
    def get_all_redis_feature_flag_config(cls) -> Optional[dict]:
        """
        从 Redis 读取所有特性开关配置
        
        功能说明：
        1. 从 Redis 读取所有特性开关配置（单个 key）
        2. 返回包含所有 flags 的配置字典
        
        Redis key 格式：
        - Key: bkmonitorv3:unify-query:data:feature_flag
        
        返回值格式：
        {
            "must-vm-query": {
                "variations": {...},
                "targeting": [...],
                "defaultRule": {...}
            },
            "range-vm-query": {
                ...
            }
        }
        
        :return: 包含所有 flags 的配置字典，如果不存在或读取失败则返回 None
        """
        # 构建 Redis key（所有 flags 存储在一个 key 中）
        redis_key = cls.REDIS_PREFIX_KEY
        
        try:
            # 从 Redis 读取配置数据
            data = RedisTools().client.get(redis_key)
            
            if data:
                # 如果数据是 bytes 类型，需要先解码为字符串
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                
                # 将 JSON 字符串解析为 Python 字典（包含所有 flags）
                return json.loads(data)
            
            # 如果 Redis 中没有该 key，返回 None
            return None
            
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"get all redis feature flag config error, error->[{e}]")
            return None

    @classmethod
    def get_redis_feature_flag_config(cls, flag_name: str) -> Optional[dict]:
        """
        从 Redis 读取特性开关配置，参考 get_redis_storage_config 方法实现
        
        功能说明：
        1. 从 Redis 读取所有特性开关配置（单个 key）
        2. 从配置中提取指定 flag_name 的配置
        3. 解析 JSON 字符串并返回配置字典
        4. 如果配置不存在或读取失败，返回 None
        
        Redis key 格式：
        - Key: bkmonitorv3:unify-query:data:feature_flag
        - Value: JSON 字符串，包含所有特性开关配置
        
        返回值格式：
        {
            "variations": {
              "Default": <default_value>,
              "true": <true_value>,
              "false": <false_value>
            },
            "targeting": [{
              "query": "tableID in [\"table_id_1\", \"table_id_2\"]",
              "percentage": {
                "true": 100,
                "false": 0
              }
            }],
            "defaultRule": {
              "variation": "Default"
            }
        }
        
        使用场景：
        - 查询模块需要获取特性开关配置时，优先从 Redis 读取（性能更好）
        - 如果 Redis 中没有配置，可以回退到从数据库或 Consul 读取
        
        :param flag_name: 特性开关名称
        :return: 配置字典，如果不存在或读取失败则返回 None
        """
        # 构建 Redis key（所有 flags 存储在一个 key 中）
        redis_key = cls.REDIS_PREFIX_KEY
        
        try:
            # 从 Redis 读取配置数据
            # Redis 返回的数据可能是 bytes 类型，需要转换为字符串
            data = RedisTools().client.get(redis_key)
            
            if data:
                # 如果数据是 bytes 类型，需要先解码为字符串
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                
                # 将 JSON 字符串解析为 Python 字典（包含所有 flags）
                all_flags = json.loads(data)
                
                # 从所有 flags 中提取指定 flag_name 的配置
                if isinstance(all_flags, dict) and flag_name in all_flags:
                    return all_flags[flag_name]
            
            # 如果 Redis 中没有该 key 或 flag_name 不存在，返回 None
            return None
            
        except Exception as e:  # pylint: disable=broad-except
            # 捕获所有异常，避免因为 Redis 连接问题或数据格式问题导致程序崩溃
            logger.error(f"get redis feature flag config error, flag_name->[{flag_name}], error->[{e}]")
            return None

    @classmethod
    def get_feature_flag_config(cls, flag_name: str, prefer_redis: bool = True) -> Optional[dict]:
        """
        获取特性开关配置，优先从 Redis 读取，如果不存在则从 Consul 读取
        
        功能说明：
        1. 根据 prefer_redis 参数决定优先读取顺序
        2. 如果 prefer_redis=True，先尝试从 Redis 读取，失败则从 Consul 读取
        3. 如果 prefer_redis=False，先尝试从 Consul 读取，失败则从 Redis 读取
        4. 如果两者都失败，返回 None
        
        :param flag_name: 特性开关名称
        :param prefer_redis: 是否优先从 Redis 读取，默认 True
        :return: 配置字典，如果不存在或读取失败则返回 None
        """
        if prefer_redis:
            # 优先从 Redis 读取
            config = cls.get_redis_feature_flag_config(flag_name)
            if config:
                return config
            
            # Redis 中没有，尝试从 Consul 读取
            return cls.get_consul_feature_flag_config(flag_name)
        else:
            # 优先从 Consul 读取
            config = cls.get_consul_feature_flag_config(flag_name)
            if config:
                return config
            
            # Consul 中没有，尝试从 Redis 读取
            return cls.get_redis_feature_flag_config(flag_name)


    @classmethod
    def get_feature_flag_value(cls, flag_name: str, table_id: Optional[str] = None, prefer_redis: bool = True) -> Optional[Any]:
        """
        获取特性开关的值，根据 tableID 匹配 targeting 规则
        
        功能说明：
        1. 获取特性开关配置
        2. 根据 table_id 匹配 targeting 规则中的 query
        3. 如果匹配到规则，根据 percentage 返回对应的 variation 值
        4. 如果没有匹配到规则，返回 defaultRule 指定的 variation 值
        
        判断逻辑：
        1. 遍历 targeting 规则，检查 table_id 是否匹配 query 条件
        2. 如果匹配，根据 percentage 分配返回对应的 variation 值
        3. 如果不匹配任何规则，返回 defaultRule.variation 对应的值
        
        :param flag_name: 特性开关名称
        :param table_id: 结果表 ID（可选），用于匹配 targeting 规则
        :param prefer_redis: 是否优先从 Redis 读取，默认 True
        :return: 特性开关的值，如果配置不存在则返回 None
        """
        config = cls.get_feature_flag_config(flag_name, prefer_redis=prefer_redis)
        
        # 如果配置不存在，返回 None
        if not config:
            return None
        
        variations = config.get("variations", {})
        targeting = config.get("targeting", [])
        default_rule = config.get("defaultRule", {})
        
        # 如果有 table_id，尝试匹配 targeting 规则
        if table_id and targeting:
            for rule in targeting:
                query = rule.get("query", "")
                percentage = rule.get("percentage", {})
                
                # 简单的 query 解析：支持 "tableID in [\"table_id_1\", \"table_id_2\"]" 格式
                if "tableID in" in query and table_id:
                    # 匹配 tableID in ["table_id_1", "table_id_2"] 格式
                    match = re.search(r'tableID in \[(.*?)\]', query)
                    if match:
                        table_list_str = match.group(1)
                        # 提取引号中的值
                        table_list = [t.strip().strip('"').strip("'") for t in table_list_str.split(",")]
                        
                        # 如果 table_id 在列表中，根据 percentage 返回对应的值
                        if table_id in table_list:
                            # 根据 percentage 分配（简化实现，实际可能需要更复杂的逻辑）
                            # 这里假设 percentage["true"] 为 100 时返回 "true" 对应的值
                            if percentage.get("true", 0) == 100:
                                return variations.get("true")
                            elif percentage.get("false", 0) == 100:
                                return variations.get("false")
                            # 如果有其他百分比分配逻辑，可以在这里扩展
                            # 如果 percentage 中没有明确的 true/false，返回第一个非 Default 的 variation
                            for variation_name, variation_value in variations.items():
                                if variation_name != "Default" and percentage.get(variation_name, 0) == 100:
                                    return variation_value
        
        # 如果没有匹配到规则，返回默认值
        default_variation = default_rule.get("variation", "Default")
        return variations.get(default_variation)

