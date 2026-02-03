# Consul Storage 配置管理

## 概述

`bkmonitor/metadata/models/storage.py` 中的 `ClusterInfo` 类提供了将存储集群配置同步到 Consul 的功能。这个功能主要用于将数据库中的存储集群配置信息（如 InfluxDB、Kafka、Redis、Elasticsearch 等）同步到 Consul，供查询模块（unify-query）使用。

## 核心方法

### `refresh_consul_storage_config()`

**功能说明：**
刷新查询模块的存储配置到 Consul。

**实现逻辑：**
1. 从数据库获取所有存储集群信息（`ClusterInfo.objects.all()`）
2. 构建需要刷新的字典信息（按 `cluster_id` 去重）
3. 遍历所有集群信息并写入到 Consul
4. 写入版本信息到 Consul

**Consul 路径格式：**
- 配置路径：`{CONSUL_PREFIX_PATH}/{cluster_id}`
  - 例如：`bk_monitorv3_community_development/metadata/unify-query/data/storage/1`
- 版本路径：`{CONSUL_VERSION_PATH}`
  - 例如：`bk_monitorv3_community_development/metadata/unify-query/version/storage`

**配置内容：**
```python
{
    "address": "{schema}://{domain_name}:{port}",  # 例如: "http://test.example.com:8086"
    "username": "{username}",
    "password": "{password}",
    "type": "{cluster_type}"  # 例如: "influxdb", "kafka", "redis", "elasticsearch"
}
```

**Schema 处理逻辑：**
- 如果 `schema` 是 `"http"` 或 `"https"`，则使用该 schema
- 如果 `schema` 是其他值（如 `"tcp"`、`None`、空字符串），则默认使用 `"http"`

**代码位置：**
```211:250:bkmonitor/metadata/models/storage.py
    @classmethod
    def refresh_consul_storage_config(cls):
        """
        刷新查询模块的table consul配置
        :return: None
        """

        hash_consul = consul_tools.HashConsul()

        # 1. 获取需要刷新的信息列表
        info_list = cls.objects.all()

        total_count = info_list.count()
        logger.debug(f"total find->[{total_count}] es storage info to refresh")

        # 2. 构建需要刷新的字典信息
        refresh_dict = {}
        for storage_info in info_list:
            refresh_dict[storage_info.cluster_id] = storage_info

        # 3. 遍历所有的字典信息并写入至consul
        for cluster_id, storage_info in list(refresh_dict.items()):
            consul_path = "/".join([cls.CONSUL_PREFIX_PATH, str(cluster_id)])

            # 根据 schema 生成地址，如果 schema 不是 http 或 https，则默认使用 http
            schema = storage_info.schema if storage_info.schema in ["http", "https"] else "http"

            hash_consul.put(
                key=consul_path,
                value={
                    "address": f"{schema}://{storage_info.domain_name}:{storage_info.port}",
                    "username": storage_info.username,
                    "password": storage_info.password,
                    "type": storage_info.cluster_type,
                },
            )
            logger.debug(f"consul path->[{consul_path}] is refresh with value->[{refresh_dict}] success.")

        hash_consul.put(key=cls.CONSUL_VERSION_PATH, value={"time": time.time()})

        logger.info(f"all es table info is refresh to consul success count->[{total_count}].")
```

## 配置路径常量

```python
CONSUL_PREFIX_PATH = f"{config.CONSUL_PATH}/unify-query/data/storage"
CONSUL_VERSION_PATH = f"{config.CONSUL_PATH}/unify-query/version/storage"
```

其中 `config.CONSUL_PATH` 的格式为：
```python
CONSUL_PATH = "{APP_CODE}_{PLATFORM}_{ENVIRONMENT}/metadata"
```

例如：`bk_monitorv3_community_development/metadata`

## 支持的存储类型

- `TYPE_INFLUXDB = "influxdb"`
- `TYPE_KAFKA = "kafka"`
- `TYPE_REDIS = "redis"`
- `TYPE_BKDATA = "bkdata"`
- `TYPE_ES = "elasticsearch"`
- `TYPE_ARGUS = "argus"`
- `TYPE_VM = "victoria_metrics"`
- `TYPE_DORIS = "doris"`

## 使用示例

### 刷新所有存储配置到 Consul

```python
from metadata.models.storage import ClusterInfo

# 刷新所有存储集群配置到 Consul
ClusterInfo.refresh_consul_storage_config()
```

### 从 Consul 读取配置

```python
from metadata.utils import consul_tools

hash_consul = consul_tools.HashConsul()
consul_path = f"{ClusterInfo.CONSUL_PREFIX_PATH}/1"  # cluster_id = 1
index, consul_data = hash_consul.get(consul_path)

if consul_data:
    config = json.loads(consul_data["Value"])
    print(config)
    # 输出: {
    #   "address": "http://test.example.com:8086",
    #   "username": "test_user",
    #   "password": "test_password",
    #   "type": "influxdb"
    # }
```

## 相关工具类

### `consul_tools.HashConsul`

用于与 Consul 交互的工具类，主要方法：
- `put(key, value)`: 写入配置到 Consul
- `get(key)`: 从 Consul 读取配置，返回 `(index, value_dict)` 元组
- `delete(key)`: 从 Consul 删除配置

## 测试

已创建单元测试文件：`metadata/tests/storage/test_refresh_consul_storage.py`

测试覆盖：
- 单个集群配置刷新
- 多个集群配置刷新
- Schema 处理逻辑（http/https/其他）
- Consul 路径格式验证
- 版本信息写入
- 空集群列表处理
- 重复 cluster_id 去重

## 与 Redis Storage 的对比

| 特性 | Consul Storage | Redis Storage |
|------|---------------|---------------|
| 配置路径 | `{CONSUL_PATH}/unify-query/data/storage/{cluster_id}` | `bkmonitorv3:unify-query:data:storage:{cluster_id}` |
| 版本路径 | `{CONSUL_PATH}/unify-query/version/storage` | `bkmonitorv3:unify-query:version:storage` |
| 存储格式 | JSON（通过 HashConsul 自动序列化） | JSON 字符串 |
| 读取方式 | `hash_consul.get(key)` 返回 `(index, value_dict)` | `redis_client.get(key)` 返回 bytes/str |
| 使用场景 | 配置中心，服务发现 | 缓存，快速读取 |

## 注意事项

1. **Schema 处理**：非 http/https 的 schema 会默认使用 http
2. **去重逻辑**：相同 `cluster_id` 的配置会被覆盖（后一个覆盖前一个）
3. **版本信息**：每次刷新都会更新版本时间戳，用于判断配置是否更新
4. **路径格式**：Consul 路径使用 `/` 分隔，Redis key 使用 `:` 分隔

## 相关文件

- `bkmonitor/metadata/models/storage.py` - 主要实现
- `bkmonitor/metadata/utils/consul_tools.py` - Consul 工具类
- `bkmonitor/metadata/config.py` - 配置路径定义
- `bkmonitor/metadata/tests/storage/test_refresh_consul_storage.py` - 单元测试

