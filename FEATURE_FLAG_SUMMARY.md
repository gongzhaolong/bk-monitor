# Feature Flag 功能总结

## 概述

新增了特性开关（Feature Flag）功能，用于管理系统的特性开关配置。该功能参考了 `storage.py` 中 `ClusterInfo` 的实现方式，支持将配置存储到数据库、Consul 和 Redis，并提供了自动刷新机制。

## 功能对比

### Storage (ClusterInfo)
- **存储方式**: Redis + Consul
- **功能**: 管理存储集群配置信息（InfluxDB、Kafka、Redis、ES 等）
- **刷新机制**: 手动调用 `refresh_consul_storage_config()` 和 `refresh_redis_storage_config()`
- **数据格式**: 每个集群配置独立存储

## Storage Redis/Consul 刷新配置功能总结

### 概述

`ClusterInfo` 类提供了将存储集群配置同步到 Consul 和 Redis 的功能，用于查询模块（unify-query）快速读取配置信息。支持 InfluxDB、Kafka、Redis、Elasticsearch、Victoria Metrics、Doris 等多种存储类型。

### Consul 配置刷新

#### 1. `refresh_consul_storage_config()`

**功能**: 从数据库读取所有存储集群配置并刷新到 Consul

**实现逻辑**:
1. 从数据库获取所有存储集群信息（`ClusterInfo.objects.all()`）
2. 构建需要刷新的字典信息（按 `cluster_id` 去重）
3. 遍历所有集群信息并写入到 Consul
4. 更新版本时间戳到 Consul

**Consul 路径格式**:
- 配置路径: `{CONSUL_PREFIX_PATH}/{cluster_id}`
  - 例如: `bk_monitorv3_community_development/metadata/unify-query/data/storage/1`
- 版本路径: `{CONSUL_VERSION_PATH}`
  - 例如: `bk_monitorv3_community_development/metadata/unify-query/version/storage`

**存储格式**:
```json
{
  "address": "http://domain_name:port",  // 例如: "http://test.example.com:8086"
  "username": "username",
  "password": "password",
  "type": "influxdb|kafka|redis|elasticsearch|victoria_metrics|doris|..."
}
```

**Schema 处理逻辑**:
- 如果 `schema` 是 `"http"` 或 `"https"`，则使用该 schema
- 如果 `schema` 是其他值（如 `"tcp"`、`None`、空字符串），则默认使用 `"http"`

**使用示例**:
```python
from metadata.models.storage import ClusterInfo

# 刷新所有存储集群配置到 Consul
ClusterInfo.refresh_consul_storage_config()
```

#### 2. `get_all_consul_storage_config()`

**功能**: 从 Consul 读取所有存储集群配置

**返回值格式**:
```python
{
    "1": {
        "address": "http://127.0.0.1:4090",
        "username": "admin",
        "password": "password123",
        "type": "influxdb"
    },
    "2": {
        "address": "http://127.0.0.1:9200",
        "username": "elastic",
        "password": "password",
        "type": "elasticsearch"
    }
}
```

**使用示例**:
```python
from metadata.models.storage import ClusterInfo

# 从 Consul 读取所有集群配置
all_configs = ClusterInfo.get_all_consul_storage_config()
for cluster_id, config in all_configs.items():
    print(f"集群 {cluster_id}: {config['type']} - {config['address']}")
```

### Redis 配置刷新

#### 1. `refresh_redis_storage_config()`

**功能**: 从数据库读取所有存储集群配置并刷新到 Redis

**实现逻辑**:
1. 从数据库获取所有存储集群信息（`ClusterInfo.objects.all()`）
2. 将每个集群的配置信息序列化为 JSON 格式
3. 写入到 Redis，key 格式为: `bkmonitorv3:unify-query:data:storage:{cluster_id}`

**Redis Key 格式**:
- Key: `bkmonitorv3:unify-query:data:storage:{cluster_id}`
- Value: JSON 字符串，包含以下字段：
  ```json
  {
    "address": "http://domain_name:port",
    "username": "username",
    "password": "password",
    "type": "influxdb|kafka|redis|..."
  }
  ```

**使用示例**:
```python
from metadata.models.storage import ClusterInfo

# 刷新所有存储集群配置到 Redis
ClusterInfo.refresh_redis_storage_config()
```

#### 2. `get_redis_storage_config(cluster_id: int)`

**功能**: 从 Redis 读取指定集群的配置

**参数**:
- `cluster_id`: 集群ID

**返回值**: 配置字典，如果不存在或读取失败则返回 `None`

**返回值格式**:
```python
{
    "address": "http://127.0.0.1:4090",
    "username": "admin",
    "password": "password123",
    "type": "influxdb"
}
```

**使用示例**:
```python
from metadata.models.storage import ClusterInfo

# 从 Redis 读取集群配置
config = ClusterInfo.get_redis_storage_config(cluster_id=1)
if config:
    print(f"集群地址: {config['address']}")
    print(f"集群类型: {config['type']}")
```

#### 3. `get_all_redis_storage_config()`

**功能**: 从 Redis 读取所有存储集群配置

**返回值**: 包含所有集群配置的字典，key 为 `cluster_id`（字符串），value 为配置字典

**返回值格式**:
```python
{
    "1": {
        "address": "http://127.0.0.1:4090",
        "username": "admin",
        "password": "password123",
        "type": "influxdb"
    },
    "2": {
        "address": "http://127.0.0.1:9200",
        "username": "elastic",
        "password": "password",
        "type": "elasticsearch"
    }
}
```

**使用示例**:
```python
from metadata.models.storage import ClusterInfo

# 从 Redis 读取所有集群配置
all_configs = ClusterInfo.get_all_redis_storage_config()
for cluster_id, config in all_configs.items():
    print(f"集群 {cluster_id}: {config['type']} - {config['address']}")
```

### Consul vs Redis 对比

| 特性 | Consul | Redis |
|------|--------|-------|
| **存储路径** | `{CONSUL_PATH}/unify-query/data/storage/{cluster_id}` | `bkmonitorv3:unify-query:data:storage:{cluster_id}` |
| **数据格式** | JSON 对象 | JSON 字符串 |
| **读取性能** | 较慢（网络请求） | 较快（内存读取） |
| **版本管理** | 支持（`CONSUL_VERSION_PATH`） | 不支持 |
| **适用场景** | 配置变更通知、版本管理 | 高频读取、性能优化 |

### API 接口

#### 1. GetConsulStorageConfigResource

**功能**: 获取 Consul 中的存储集群配置（用于检查配置是否正确写入）

**API 端点**:
- `GET /api/v3/meta/config/get_consul_storage_config/?cluster_id=1` - 获取单个集群配置
- `GET /api/v3/meta/config/get_consul_storage_config/` - 获取所有集群配置

**请求参数**:
- `cluster_id` (int, optional): 集群ID
  - 如果提供 `cluster_id`：返回指定集群的配置
  - 如果不提供 `cluster_id`：返回所有集群的配置

**返回格式（单个集群）**:
```json
{
    "exists": true,
    "cluster_id": 1,
    "consul_path": "bk_monitorv3_community_development/metadata/unify-query/data/storage/1",
    "consul_index": 12345,
    "config": {
        "address": "http://domain_name:port",
        "username": "username",
        "password": "password",
        "type": "influxdb"
    }
}
```

**返回格式（所有集群）**:
```json
{
    "exists": true,
    "consul_path_prefix": "bk_monitorv3_community_development/metadata/unify-query/data/storage",
    "configs": {
        "1": {
            "address": "http://127.0.0.1:4090",
            "username": "admin",
            "password": "password123",
            "type": "influxdb"
        },
        "2": {
            "address": "http://127.0.0.1:9200",
            "username": "elastic",
            "password": "password",
            "type": "elasticsearch"
        }
    },
    "count": 2
}
```

**使用示例**:
```python
from metadata.resources.resources import GetConsulStorageConfigResource

# 获取单个集群配置
resource = GetConsulStorageConfigResource()
result = resource.request({"cluster_id": 1})

# 获取所有集群配置
result = resource.request({})  # 不提供 cluster_id
```

#### 2. GetRedisStorageConfigResource

**功能**: 获取 Redis 中的存储集群配置（用于检查配置是否正确写入）

**API 端点**:
- `GET /api/v3/meta/config/get_redis_storage_config/?cluster_id=1` - 获取单个集群配置
- `GET /api/v3/meta/config/get_redis_storage_config/` - 获取所有集群配置

**请求参数**:
- `cluster_id` (int, optional): 集群ID
  - 如果提供 `cluster_id`：返回指定集群的配置
  - 如果不提供 `cluster_id`：返回所有集群的配置

**返回格式（单个集群）**:
```json
{
    "exists": true,
    "cluster_id": 1,
    "redis_key": "bkmonitorv3:unify-query:data:storage:1",
    "config": {
        "address": "http://domain_name:port",
        "username": "username",
        "password": "password",
        "type": "influxdb"
    }
}
```

**返回格式（所有集群）**:
```json
{
    "exists": true,
    "redis_key_prefix": "bkmonitorv3:unify-query:data:storage",
    "configs": {
        "1": {
            "address": "http://127.0.0.1:4090",
            "username": "admin",
            "password": "password123",
            "type": "influxdb"
        },
        "2": {
            "address": "http://127.0.0.1:9200",
            "username": "elastic",
            "password": "password",
            "type": "elasticsearch"
        }
    },
    "count": 2
}
```

**使用示例**:
```python
from metadata.resources.resources import GetRedisStorageConfigResource

# 获取单个集群配置
resource = GetRedisStorageConfigResource()
result = resource.request({"cluster_id": 1})

# 获取所有集群配置
result = resource.request({})  # 不提供 cluster_id
```

### 配置刷新流程

```
数据库 (ClusterInfo)
    ↓
refresh_consul_storage_config() / refresh_redis_storage_config()
    ↓
Consul / Redis
    ↓
get_*_storage_config() / get_all_*_storage_config()
    ↓
查询模块使用配置
```

### 使用场景

1. **查询模块配置读取**: 查询模块需要频繁读取存储集群配置时，优先从 Redis 读取以提高性能
2. **配置缓存**: 将 Consul 中的配置缓存到 Redis，减少对 Consul 的访问压力
3. **回退机制**: 如果 Redis 中没有配置，可以回退到从数据库或 Consul 读取
4. **上线检查**: 使用 API 接口检查配置是否正确写入到 Consul 或 Redis

### 注意事项

1. **手动刷新**: Redis 和 Consul 配置需要手动调用刷新方法，不会自动同步
2. **数据一致性**: Redis/Consul 中的数据可能与数据库不一致，需要定期刷新
3. **错误处理**: 读取配置时如果失败，应回退到从数据库读取
4. **Key 命名**: Redis key 使用 `cluster_id` 作为后缀，确保每个集群配置独立存储
5. **版本管理**: Consul 支持版本管理，可以通过版本时间戳判断配置是否更新

### Feature Flag
- **存储方式**: Redis + Consul
- **功能**: 管理特性开关配置（variations、targeting、defaultRule）
- **刷新机制**: 自动刷新（save/delete 时自动触发）+ 手动刷新
- **数据格式**: 所有特性开关配置合并存储在一个 key 中

## 数据库模型

### FeatureFlag 模型

**表名**: `metadata_featureflag`

**字段定义**:
```python
class FeatureFlag(models.Model):
    flag_id = models.AutoField("特性开关ID", primary_key=True)
    flag_name = models.CharField("特性开关名称", max_length=128, unique=True, db_index=True)
    config = JsonField("配置信息", default=dict)  # 包含 variations、targeting、defaultRule 等
    is_enabled = models.BooleanField("是否启用", default=True, db_index=True)
    description = models.CharField("描述", max_length=512, default="", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
```

**配置格式示例**:
```json
{
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
}
```

**自动刷新机制**:
- `save()`: 保存时自动刷新所有启用的特性开关到 Consul 和 Redis
- `delete()`: 删除时自动刷新配置（自动排除已删除的配置）

## 配置管理类 (FeatureFlagConfig)

### Consul 配置

**路径**:
- 数据路径: `{CONSUL_PATH}/unify-query/data/feature_flag`
- 版本路径: `{CONSUL_PATH}/unify-query/version/feature_flag`

**存储格式**:
```json
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
```

**主要方法**:
- `refresh_consul_feature_flag_config_from_db()`: 从数据库读取并刷新到 Consul
- `refresh_consul_feature_flag_config(feature_flags: dict)`: 刷新指定配置到 Consul
- `get_all_consul_feature_flag_config()`: 从 Consul 读取所有配置
- `get_consul_feature_flag_config(flag_name: str)`: 从 Consul 读取指定配置
- `get_consul_feature_flag_version()`: 获取 Consul 版本时间戳

### Redis 配置

**Key**:
- 数据 Key: `bkmonitorv3:unify-query:data:feature_flag`
- 所有特性开关配置存储在一个 key 中

**存储格式**:
```json
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
```

**主要方法**:
- `refresh_redis_feature_flag_config_from_db()`: 从数据库读取并刷新到 Redis
- `refresh_redis_feature_flag_config(feature_flags: dict)`: 刷新指定配置到 Redis
- `get_all_redis_feature_flag_config()`: 从 Redis 读取所有配置
- `get_redis_feature_flag_config(flag_name: str)`: 从 Redis 读取指定配置

### 统一读取接口

**智能读取（支持回退）**:
- `get_feature_flag_config(flag_name: str, prefer_redis: bool = False)`: 优先从 Redis 或 Consul 读取，失败时回退
- `get_all_feature_flag_config(prefer_redis: bool = False)`: 读取所有配置，支持回退

**指定优先级读取**:
- `get_feature_flag_config_prefer_redis(flag_name: str)`: 优先从 Redis 读取
- `get_feature_flag_config_prefer_consul(flag_name: str)`: 优先从 Consul 读取
- `get_all_feature_flag_config_prefer_redis()`: 优先从 Redis 读取所有配置
- `get_all_feature_flag_config_prefer_consul()`: 优先从 Consul 读取所有配置

**特性开关值获取**:
- `get_feature_flag_value(flag_name: str, table_id: Optional[str] = None, prefer_redis: bool = True)`: 根据 table_id 和 targeting 规则计算特性开关值

**版本管理**:
- `get_consul_feature_flag_version()`: 获取 Consul 版本时间戳
- `is_feature_flag_config_updated(last_check_time: float)`: 检查配置是否已更新

**强制刷新**:
- `force_refresh_feature_flag_config()`: 强制从数据库刷新到 Consul 和 Redis

## 数据库迁移

**迁移文件**: `bkmonitor/metadata/migrations/0249_feature_flag.py`

**迁移内容**:
- 创建 `metadata_featureflag` 表
- 包含所有必需字段和索引

**运行迁移**:
```bash
python manage.py migrate metadata 0249_feature_flag
```

## 使用示例

### 1. 创建特性开关

```python
from metadata.models.feature_flag import FeatureFlag

# 创建特性开关
flag = FeatureFlag.objects.create(
    flag_name="must-vm-query",
    config={
        "variations": {
            "Default": False,
            "true": True,
            "false": False
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
    is_enabled=True,
    description="必须使用 VM 查询"
)
# 保存时会自动刷新到 Consul 和 Redis
```

### 2. 从数据库刷新到 Consul/Redis

```python
from metadata.models.feature_flag import FeatureFlagConfig

# 从数据库刷新到 Consul
FeatureFlagConfig.refresh_consul_feature_flag_config_from_db()

# 从数据库刷新到 Redis
FeatureFlagConfig.refresh_redis_feature_flag_config_from_db()

# 强制刷新（同时刷新 Consul 和 Redis）
FeatureFlagConfig.force_refresh_feature_flag_config()
```

### 3. 读取特性开关配置

```python
from metadata.models.feature_flag import FeatureFlagConfig

# 从 Redis 读取（优先）
config = FeatureFlagConfig.get_feature_flag_config_prefer_redis("must-vm-query")

# 从 Consul 读取（优先）
config = FeatureFlagConfig.get_feature_flag_config_prefer_consul("must-vm-query")

# 智能读取（自动回退）
config = FeatureFlagConfig.get_feature_flag_config("must-vm-query", prefer_redis=True)

# 读取所有配置
all_configs = FeatureFlagConfig.get_all_feature_flag_config(prefer_redis=True)
```

### 4. 获取特性开关值

```python
from metadata.models.feature_flag import FeatureFlagConfig

# 根据 table_id 获取特性开关值
value = FeatureFlagConfig.get_feature_flag_value(
    flag_name="must-vm-query",
    table_id="table_id_1",
    prefer_redis=True
)
```

### 5. 检查配置更新

```python
from metadata.models.feature_flag import FeatureFlagConfig
import time

# 记录上次检查时间
last_check_time = time.time()

# 执行其他操作...

# 检查配置是否已更新
if FeatureFlagConfig.is_feature_flag_config_updated(last_check_time):
    print("配置已更新，需要重新加载")
```

## 与 Storage 的相似之处

### 1. 刷新机制
- **Storage**: 手动调用 `refresh_consul_storage_config()` 和 `refresh_redis_storage_config()`
- **Feature Flag**: 自动刷新（save/delete）+ 手动刷新（`refresh_*_from_db()`）

### 2. 版本管理
- **Storage**: 使用 Consul 版本路径管理配置版本
- **Feature Flag**: 同样使用 Consul 版本路径，通过时间戳判断配置是否更新

### 3. 错误处理
- **Storage**: 捕获异常，避免配置刷新失败影响主流程
- **Feature Flag**: 同样捕获异常，save/delete 时的自动刷新失败不会影响数据库操作

### 4. 数据格式处理
- **Storage**: 将配置序列化为 JSON 存储
- **Feature Flag**: 同样使用 JSON 格式，支持复杂的配置结构（variations、targeting、defaultRule）

### 5. 读取接口
- **Storage**: 提供从 Consul/Redis 读取配置的方法
- **Feature Flag**: 提供多种读取方式（优先 Redis、优先 Consul、智能回退）

## 主要差异

### 1. 存储方式
- **Storage**: 仅支持 Redis（Consul 主要用于版本管理）
- **Feature Flag**: 同时支持 Redis 和 Consul，提供更灵活的读取策略

### 2. 数据组织
- **Storage**: 每个集群配置独立存储（`{prefix}:{cluster_id}`）
- **Feature Flag**: 所有特性开关配置合并存储在一个 key 中

### 3. 自动刷新
- **Storage**: 需要手动调用刷新方法
- **Feature Flag**: save/delete 时自动触发刷新，减少手动操作

### 4. 配置复杂度
- **Storage**: 相对简单的配置结构（address、username、password、type）
- **Feature Flag**: 支持复杂的特性开关配置（variations、targeting、defaultRule）

## 环境变量配置

### Redis 配置
```bash
export BK_MONITOR_TRANSFER_REDIS_MODE=standalone
export BK_MONITOR_TRANSFER_REDIS_HOST=127.0.0.1
export BK_MONITOR_TRANSFER_REDIS_PORT=6379
export BK_MONITOR_TRANSFER_REDIS_PASSWORD=""
export BK_MONITOR_TRANSFER_REDIS_DB=0
```

### Consul 配置
```bash
export CONSUL_HOST=127.0.0.1
export CONSUL_PORT=8500
```

## 测试

### 单元测试
- 文件: `bkmonitor/metadata/tests/test_feature_flag.py`
- 覆盖: 模型方法、配置管理类方法、自动刷新机制、读取接口等

### 功能测试
- 创建、更新、删除特性开关
- 验证自动刷新到 Consul 和 Redis
- 验证读取接口的正确性
- 验证版本管理和配置更新检查

## 总结

Feature Flag 功能提供了完整的特性开关管理能力，包括：
1. **数据库存储**: 持久化存储特性开关配置
2. **自动同步**: save/delete 时自动刷新到 Consul 和 Redis
3. **灵活读取**: 支持多种读取策略（优先 Redis、优先 Consul、智能回退）
4. **版本管理**: 通过 Consul 版本路径管理配置版本
5. **复杂配置**: 支持 variations、targeting、defaultRule 等复杂配置结构

该实现参考了 `storage.py` 中 `ClusterInfo` 的设计模式，保持了代码风格的一致性，同时针对特性开关的使用场景进行了优化（如自动刷新、合并存储等）。

