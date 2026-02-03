# 配置检查 API 接口文档

## 概述

本文档介绍用于检查 `refresh_consul_storage_config`、`refresh_redis_storage_config`、`refresh_consul_feature_flag_config` 和 `refresh_redis_feature_flag_config` 配置是否正确写入的 API 接口。

这些接口主要用于项目上线时验证配置是否正确写入到 Consul 或 Redis。

## HTTP API 端点

所有接口都通过 HTTP API 暴露，可以通过 HTTP 请求访问：

- **基础路径：** `/api/v3/meta/config/`
- **请求方法：** GET
- **认证：** 需要登录认证（除非接口配置了 `login_exempt`）

### API 端点列表

1. `GET /api/v3/meta/config/get_consul_storage_config/?cluster_id=1` - 获取单个集群配置
2. `GET /api/v3/meta/config/get_consul_storage_config/` - 获取所有集群配置
3. `GET /api/v3/meta/config/get_redis_storage_config/?cluster_id=1` - 获取单个集群配置
4. `GET /api/v3/meta/config/get_redis_storage_config/` - 获取所有集群配置
5. `GET /api/v3/meta/config/get_consul_feature_flag_config/?flag_name=enable_new_query` - 获取单个 flag
6. `GET /api/v3/meta/config/get_consul_feature_flag_config/` - 获取所有 flags
7. `GET /api/v3/meta/config/get_redis_feature_flag_config/?flag_name=enable_new_query` - 获取单个 flag
8. `GET /api/v3/meta/config/get_redis_feature_flag_config/` - 获取所有 flags

## API 接口列表

### 1. GetConsulStorageConfigResource

**功能：** 获取 Consul 中的存储集群配置

**请求参数：**
- `cluster_id` (int, optional): 集群ID
  - 如果提供 `cluster_id`：返回指定集群的配置
  - 如果不提供 `cluster_id`：返回所有集群的配置

**返回格式（获取单个集群配置）：**
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

**返回格式（获取所有集群配置，不提供 cluster_id 参数）：**
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

**配置不存在时返回：**
```json
{
    "exists": false,
    "cluster_id": 1,
    "consul_path": "bk_monitorv3_community_development/metadata/unify-query/data/storage/1",
    "message": "配置不存在于 Consul: ..."
}
```

**使用示例：**

**Python 代码调用：**

**获取单个集群配置：**
```python
from metadata.resources.resources import GetConsulStorageConfigResource

resource = GetConsulStorageConfigResource()
result = resource.request({"cluster_id": 1})
print(result)
```

**获取所有集群配置：**
```python
from metadata.resources.resources import GetConsulStorageConfigResource

resource = GetConsulStorageConfigResource()
result = resource.request({})  # 不提供 cluster_id
print(result)
```

**HTTP 请求：**

**获取单个集群配置：**
```bash
# 使用 curl
curl -X GET "http://your-domain/api/v3/meta/config/get_consul_storage_config/?cluster_id=1" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_consul_storage_config/",
    params={"cluster_id": 1},
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

**获取所有集群配置：**
```bash
# 使用 curl（不提供 cluster_id 参数）
curl -X GET "http://your-domain/api/v3/meta/config/get_consul_storage_config/" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_consul_storage_config/",
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

### 2. GetRedisStorageConfigResource

**功能：** 获取 Redis 中的存储集群配置

**请求参数：**
- `cluster_id` (int, optional): 集群ID
  - 如果提供 `cluster_id`：返回指定集群的配置
  - 如果不提供 `cluster_id`：返回所有集群的配置

**返回格式（获取单个集群配置）：**
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

**返回格式（获取所有集群配置，不提供 cluster_id 参数）：**
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

**配置不存在时返回：**
```json
{
    "exists": false,
    "cluster_id": 1,
    "redis_key": "bkmonitorv3:unify-query:data:storage:1",
    "message": "配置不存在于 Redis: ..."
}
```

**使用示例：**

**Python 代码调用：**

**获取单个集群配置：**
```python
from metadata.resources.resources import GetRedisStorageConfigResource

resource = GetRedisStorageConfigResource()
result = resource.request({"cluster_id": 1})
print(result)
```

**获取所有集群配置：**
```python
from metadata.resources.resources import GetRedisStorageConfigResource

resource = GetRedisStorageConfigResource()
result = resource.request({})  # 不提供 cluster_id
print(result)
```

**HTTP 请求：**

**获取单个集群配置：**
```bash
# 使用 curl
curl -X GET "http://your-domain/api/v3/meta/config/get_redis_storage_config/?cluster_id=1" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_redis_storage_config/",
    params={"cluster_id": 1},
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

**获取所有集群配置：**
```bash
# 使用 curl（不提供 cluster_id 参数）
curl -X GET "http://your-domain/api/v3/meta/config/get_redis_storage_config/" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_redis_storage_config/",
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

### 3. GetConsulFeatureFlagConfigResource

**功能：** 获取 Consul 中的特性开关配置

**请求参数：**
- `flag_name` (str, optional): 特性开关名称
  - 如果提供 `flag_name`：返回指定 flag 的配置
  - 如果不提供 `flag_name`：返回所有 flags 的配置

**返回格式（获取单个 flag）：**
```json
{
    "exists": true,
    "flag_name": "enable_new_query",
    "consul_path": "bk_monitorv3_community_development/metadata/unify-query/data/feature_flag",
    "config": {
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
}
```

**返回格式（获取所有 flags，不提供 flag_name 参数）：**
```json
{
    "exists": true,
    "consul_path": "bk_monitorv3_community_development/metadata/unify-query/data/feature_flag",
    "configs": {
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
            "variations": {
                "Default": 0,
                "true": 30000
            },
            "targeting": [{
                "query": "tableID in [\"table_id_1\", \"table_id_3\"]",
                "percentage": {
                    "true": 100
                }
            }],
            "defaultRule": {
                "variation": "Default"
            }
        }
    },
    "count": 2
}
```

**配置不存在时返回：**
```json
{
    "exists": false,
    "flag_name": "enable_new_query",
    "consul_path": "bk_monitorv3_community_development/metadata/unify-query/data/feature_flag",
    "message": "配置不存在于 Consul: bk_monitorv3_community_development/metadata/unify-query/data/feature_flag (flag_name: enable_new_query)"
}
```

**使用示例：**

**Python 代码调用：**
```python
from metadata.resources.resources import GetConsulFeatureFlagConfigResource

resource = GetConsulFeatureFlagConfigResource()
result = resource.request({"flag_name": "enable_new_query"})
print(result)
```

**HTTP 请求：**

**获取单个 flag：**
```bash
# 使用 curl
curl -X GET "http://your-domain/api/v3/meta/config/get_consul_feature_flag_config/?flag_name=enable_new_query" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_consul_feature_flag_config/",
    params={"flag_name": "enable_new_query"},
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

**获取所有 flags：**
```bash
# 使用 curl（不提供 flag_name 参数）
curl -X GET "http://your-domain/api/v3/meta/config/get_consul_feature_flag_config/" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_consul_feature_flag_config/",
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

### 4. GetRedisFeatureFlagConfigResource

**功能：** 获取 Redis 中的特性开关配置

**请求参数：**
- `flag_name` (str, optional): 特性开关名称
  - 如果提供 `flag_name`：返回指定 flag 的配置
  - 如果不提供 `flag_name`：返回所有 flags 的配置

**返回格式（获取单个 flag）：**
```json
{
    "exists": true,
    "flag_name": "enable_new_query",
    "redis_key": "bkmonitorv3:unify-query:data:feature_flag",
    "config": {
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
}
```

**返回格式（获取所有 flags，不提供 flag_name 参数）：**
```json
{
    "exists": true,
    "redis_key": "bkmonitorv3:unify-query:data:feature_flag",
    "configs": {
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
            "variations": {
                "Default": 0,
                "true": 30000
            },
            "targeting": [{
                "query": "tableID in [\"table_id_1\", \"table_id_3\"]",
                "percentage": {
                    "true": 100
                }
            }],
            "defaultRule": {
                "variation": "Default"
            }
        }
    },
    "count": 2
}
```

**配置不存在时返回：**
```json
{
    "exists": false,
    "flag_name": "enable_new_query",
    "redis_key": "bkmonitorv3:unify-query:data:feature_flag",
    "message": "配置不存在于 Redis: bkmonitorv3:unify-query:data:feature_flag (flag_name: enable_new_query)"
}
```

**使用示例：**

**Python 代码调用：**
```python
from metadata.resources.resources import GetRedisFeatureFlagConfigResource

resource = GetRedisFeatureFlagConfigResource()
result = resource.request({"flag_name": "enable_new_query"})
print(result)
```

**HTTP 请求：**

**获取单个 flag：**
```bash
# 使用 curl
curl -X GET "http://your-domain/api/v3/meta/config/get_redis_feature_flag_config/?flag_name=enable_new_query" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_redis_feature_flag_config/",
    params={"flag_name": "enable_new_query"},
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

**获取所有 flags：**
```bash
# 使用 curl（不提供 flag_name 参数）
curl -X GET "http://your-domain/api/v3/meta/config/get_redis_feature_flag_config/" \
  -H "Cookie: your-session-cookie"

# 使用 Python requests
import requests

response = requests.get(
    "http://your-domain/api/v3/meta/config/get_redis_feature_flag_config/",
    cookies={"sessionid": "your-session-id"}
)
result = response.json()
print(result)
```

## 上线检查脚本示例

### 检查所有存储集群配置

**方式一：使用获取所有配置的接口（推荐）**

```python
from metadata.resources.resources import (
    GetConsulStorageConfigResource,
    GetRedisStorageConfigResource
)

def check_all_storage_configs():
    """检查所有存储集群的配置是否正确写入（使用获取所有配置的接口）"""
    consul_resource = GetConsulStorageConfigResource()
    redis_resource = GetRedisStorageConfigResource()
    
    results = {
        "consul": {"exists": False, "count": 0, "configs": {}},
        "redis": {"exists": False, "count": 0, "configs": {}}
    }
    
    # 检查 Consul（获取所有配置）
    consul_result = consul_resource.request({})  # 不提供 cluster_id
    if consul_result.get("exists"):
        results["consul"] = {
            "exists": True,
            "count": consul_result.get("count", 0),
            "configs": consul_result.get("configs", {})
        }
    else:
        results["consul"]["error"] = consul_result.get("message")
    
    # 检查 Redis（获取所有配置）
    redis_result = redis_resource.request({})  # 不提供 cluster_id
    if redis_result.get("exists"):
        results["redis"] = {
            "exists": True,
            "count": redis_result.get("count", 0),
            "configs": redis_result.get("configs", {})
        }
    else:
        results["redis"]["error"] = redis_result.get("message")
    
    return results
```

**方式二：逐个检查每个集群配置**

```python
from metadata.models.storage import ClusterInfo
from metadata.resources.resources import (
    GetConsulStorageConfigResource,
    GetRedisStorageConfigResource
)

def check_all_storage_configs_individual():
    """检查所有存储集群的配置是否正确写入（逐个检查）"""
    clusters = ClusterInfo.objects.all()
    
    consul_resource = GetConsulStorageConfigResource()
    redis_resource = GetRedisStorageConfigResource()
    
    results = {
        "consul": {"success": [], "failed": []},
        "redis": {"success": [], "failed": []}
    }
    
    for cluster in clusters:
        cluster_id = cluster.cluster_id
        
        # 检查 Consul
        consul_result = consul_resource.request({"cluster_id": cluster_id})
        if consul_result.get("exists"):
            results["consul"]["success"].append(cluster_id)
        else:
            results["consul"]["failed"].append({
                "cluster_id": cluster_id,
                "error": consul_result.get("message")
            })
        
        # 检查 Redis
        redis_result = redis_resource.request({"cluster_id": cluster_id})
        if redis_result.get("exists"):
            results["redis"]["success"].append(cluster_id)
        else:
            results["redis"]["failed"].append({
                "cluster_id": cluster_id,
                "error": redis_result.get("message")
            })
    
    return results
```

### 检查特性开关配置

```python
from metadata.resources.resources import (
    GetConsulFeatureFlagConfigResource,
    GetRedisFeatureFlagConfigResource
)

def check_feature_flags(flag_names):
    """检查特性开关配置是否正确写入"""
    consul_resource = GetConsulFeatureFlagConfigResource()
    redis_resource = GetRedisFeatureFlagConfigResource()
    
    results = {
        "consul": {"success": [], "failed": []},
        "redis": {"success": [], "failed": []}
    }
    
    for flag_name in flag_names:
        # 检查 Consul
        consul_result = consul_resource.request({"flag_name": flag_name})
        if consul_result.get("exists"):
            results["consul"]["success"].append(flag_name)
        else:
            results["consul"]["failed"].append({
                "flag_name": flag_name,
                "error": consul_result.get("message")
            })
        
        # 检查 Redis
        redis_result = redis_resource.request({"flag_name": flag_name})
        if redis_result.get("exists"):
            results["redis"]["success"].append(flag_name)
        else:
            results["redis"]["failed"].append({
                "flag_name": flag_name,
                "error": redis_result.get("message")
            })
    
    return results
```

## 配置路径说明

### Storage 配置路径

**Consul 路径格式：**
```
{CONSUL_PATH}/unify-query/data/storage/{cluster_id}
```
例如：`bk_monitorv3_community_development/metadata/unify-query/data/storage/1`

**Redis Key 格式：**
```
bkmonitorv3:unify-query:data:storage:{cluster_id}
```
例如：`bkmonitorv3:unify-query:data:storage:1`

### Feature Flag 配置路径

**Consul 路径格式：**
```
{CONSUL_PATH}/unify-query/data/feature_flag
```
例如：`bk_monitorv3_community_development/metadata/unify-query/data/feature_flag`

**说明：** 所有特性开关配置存储在一个 Consul key 中，value 是一个包含所有 flags 的 JSON 对象，格式如下：
```json
{
  "must-vm-query": {
    "variations": {...},
    "targeting": [...],
    "defaultRule": {...}
  },
  "range-vm-query": {
    "variations": {...},
    "targeting": [...],
    "defaultRule": {...}
  }
}
```

**Redis Key 格式：**
```
bkmonitorv3:unify-query:data:feature_flag
```
例如：`bkmonitorv3:unify-query:data:feature_flag`

**说明：** 所有特性开关配置存储在一个 Redis key 中，value 是一个包含所有 flags 的 JSON 字符串，格式与 Consul 相同。

## 注意事项

1. **错误处理：** 所有接口都包含异常处理，如果读取失败会返回错误信息
2. **配置不存在：** 如果配置不存在，`exists` 字段为 `false`，并包含 `message` 说明原因
3. **配置格式：** 返回的配置格式与写入时保持一致
4. **性能考虑：** Redis 读取性能优于 Consul，建议优先检查 Redis

## HTTP API 批量检查示例

### 使用 HTTP 请求批量检查存储集群配置

**方式一：使用获取所有配置的接口（推荐）**

```python
import requests

def check_all_storage_configs_http(base_url, session_cookie):
    """使用 HTTP API 检查所有存储集群的配置（获取所有配置）"""
    results = {
        "consul": {"exists": False, "count": 0, "configs": {}},
        "redis": {"exists": False, "count": 0, "configs": {}}
    }
    
    # 检查 Consul（获取所有配置）
    consul_response = requests.get(
        f"{base_url}/api/v3/meta/config/get_consul_storage_config/",
        cookies={"sessionid": session_cookie}
    )
    consul_result = consul_response.json().get("data", {})
    if consul_result.get("exists"):
        results["consul"] = {
            "exists": True,
            "count": consul_result.get("count", 0),
            "configs": consul_result.get("configs", {})
        }
    else:
        results["consul"]["error"] = consul_result.get("message")
    
    # 检查 Redis（获取所有配置）
    redis_response = requests.get(
        f"{base_url}/api/v3/meta/config/get_redis_storage_config/",
        cookies={"sessionid": session_cookie}
    )
    redis_result = redis_response.json().get("data", {})
    if redis_result.get("exists"):
        results["redis"] = {
            "exists": True,
            "count": redis_result.get("count", 0),
            "configs": redis_result.get("configs", {})
        }
    else:
        results["redis"]["error"] = redis_result.get("message")
    
    return results
```

**方式二：逐个检查每个集群配置**

```python
import requests

def check_all_storage_configs_http_individual(base_url, session_cookie):
    """使用 HTTP API 检查所有存储集群的配置（逐个检查）"""
    # 首先获取所有集群列表（需要根据实际情况调整）
    clusters = [1, 2, 3]  # 示例集群ID列表
    
    results = {
        "consul": {"success": [], "failed": []},
        "redis": {"success": [], "failed": []}
    }
    
    for cluster_id in clusters:
        # 检查 Consul
        consul_response = requests.get(
            f"{base_url}/api/v3/meta/config/get_consul_storage_config/",
            params={"cluster_id": cluster_id},
            cookies={"sessionid": session_cookie}
        )
        consul_result = consul_response.json().get("data", {})
        if consul_result.get("exists"):
            results["consul"]["success"].append(cluster_id)
        else:
            results["consul"]["failed"].append({
                "cluster_id": cluster_id,
                "error": consul_result.get("message")
            })
        
        # 检查 Redis
        redis_response = requests.get(
            f"{base_url}/api/v3/meta/config/get_redis_storage_config/",
            params={"cluster_id": cluster_id},
            cookies={"sessionid": session_cookie}
        )
        redis_result = redis_response.json().get("data", {})
        if redis_result.get("exists"):
            results["redis"]["success"].append(cluster_id)
        else:
            results["redis"]["failed"].append({
                "cluster_id": cluster_id,
                "error": redis_result.get("message")
            })
    
    return results
```

### 使用 HTTP 请求批量检查特性开关配置

```python
import requests

def check_feature_flags_http(base_url, session_cookie, flag_names):
    """使用 HTTP API 检查特性开关配置"""
    results = {
        "consul": {"success": [], "failed": []},
        "redis": {"success": [], "failed": []}
    }
    
    for flag_name in flag_names:
        # 检查 Consul
        consul_response = requests.get(
            f"{base_url}/api/v3/meta/config/get_consul_feature_flag_config/",
            params={"flag_name": flag_name},
            cookies={"sessionid": session_cookie}
        )
        consul_result = consul_response.json()
        if consul_result.get("exists"):
            results["consul"]["success"].append(flag_name)
        else:
            results["consul"]["failed"].append({
                "flag_name": flag_name,
                "error": consul_result.get("message")
            })
        
        # 检查 Redis
        redis_response = requests.get(
            f"{base_url}/api/v3/meta/config/get_redis_feature_flag_config/",
            params={"flag_name": flag_name},
            cookies={"sessionid": session_cookie}
        )
        redis_result = redis_response.json()
        if redis_result.get("exists"):
            results["redis"]["success"].append(flag_name)
        else:
            results["redis"]["failed"].append({
                "flag_name": flag_name,
                "error": redis_result.get("message")
            })
    
    return results
```

## 相关文件

- 接口实现：`bkmonitor/metadata/resources/resources.py`
- ViewSet 定义：`bkmonitor/metadata/views.py`
- URL 路由配置：`bkmonitor/metadata/urls.py`
- Storage 模型：`bkmonitor/metadata/models/storage.py`
- Feature Flag 模型：`bkmonitor/metadata/models/feature_flag.py`
- Consul 工具：`bkmonitor/metadata/utils/consul_tools.py`
- Redis 工具：`bkmonitor/metadata/utils/redis_tools.py`

