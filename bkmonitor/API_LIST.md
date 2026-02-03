# BK-Monitor API 列表

## API 概览

项目共有 **145+ 个 API 接口**，主要分为以下几个模块：

## 主要 API 路径

### 1. REST API v1 (monitor_api)
**路径**: `/rest/v1/`
- 基础监控 API
- 数据模型 CRUD 操作
- 用户配置管理

### 2. REST API v2 (monitor_web)
**路径**: `/rest/v2/`
主要模块包括：

#### 2.1 告警策略 (strategies)
- 创建/编辑/删除告警策略
- 策略列表查询
- 策略应用到服务

#### 2.2 数据探索 (data_explorer)
- 数据查询
- 查询历史
- 指标查询

#### 2.3 采集配置 (collecting)
- 采集配置管理
- 采集插件管理
- 采集状态查询

#### 2.4 可用性监控 (uptime_check)
- 创建/编辑/删除拨测任务
- 拨测节点管理
- 拨测组管理
- 任务状态变更

#### 2.5 告警事件 (alert_events)
- 告警事件查询
- 事件处理

#### 2.6 屏蔽配置 (shield)
- 创建/编辑/删除屏蔽
- 屏蔽列表查询

#### 2.7 通知组 (notice_group)
- 通知组管理
- 用户组管理

#### 2.8 自定义指标 (custom_time_series)
- 创建/编辑/删除自定义时序
- 自定义事件组管理

#### 2.9 场景视图 (scene_view)
- 场景视图管理
- 仪表盘管理

#### 2.10 报告 (report / new_report)
- 订阅报告管理
- 报告发送
- 报告记录查询

#### 2.11 日历 (calendars)
- 日历管理
- 日历事项管理

#### 2.12 配置管理 (config)
- 系统配置
- 业务配置

#### 2.13 其他模块
- **插件管理** (plugin)
- **性能监控** (performance)
- **概览** (overview)
- **Grafana** (grafana)
- **K8s** (k8s)
- **AIOps** (aiops)
- **数据链路** (datalink)
- **查询模板** (query_template)
- **导出导入** (export_import)
- **分享** (share)
- **IAM** (iam)
- **搜索** (search)
- **代码即配置** (as_code)
- **事件** (incident)

### 3. APM API (apm_web)
**路径**: `/apm/`
- **应用管理** (meta)
  - 创建/删除应用
  - 应用列表
  - 应用详情
- **链路追踪** (trace_api)
  - 链路查询
  - Span 查询
- **性能分析** (profile_api)
  - Profile 数据查询
- **指标** (metric)
  - 指标查询
  - 指标事件
- **拓扑** (topo)
  - 服务拓扑
- **服务** (service)
  - 服务列表
  - 服务详情
- **日志** (service_log)
  - 服务日志查询
- **数据库** (service_db)
  - 数据库查询
- **容器** (container)
  - 容器监控
- **事件** (event)
  - APM 事件
- **策略** (strategy)
  - APM 告警策略

### 4. FTA API (fta_web)
**路径**: `/fta/`
- 告警处理
- 事件插件
- 告警分配
- 动作配置

### 5. 查询 API (query-api)
**路径**: `/query-api/rest/v2/`
- 统一查询接口
- 数据查询

### 6. 其他 API

#### 6.1 监控适配器 (monitor_adapter)
**路径**: `/`
- Grafana 适配
- 通用适配接口

#### 6.2 链路追踪 (apm_trace)
**路径**: `/trace/`
- 链路追踪相关 API

#### 6.3 内核 API (kernel_api)
- 核心功能 API

#### 6.4 健康检查
**路径**: `/metrics/`
- Prometheus 指标

#### 6.5 Swagger 文档 (开发环境)
**路径**: `/swagger/` 或 `/redoc/`
- API 文档界面

## API 访问方式

### 基础 URL
```
http://localhost:8000
```

### 主要 API 端点示例

1. **监控 API v2**: `http://localhost:8000/rest/v2/`
2. **监控 API v1**: `http://localhost:8000/rest/v1/`
3. **APM API**: `http://localhost:8000/apm/`
4. **FTA API**: `http://localhost:8000/fta/`
5. **查询 API**: `http://localhost:8000/query-api/rest/v2/`

## API 文档

详细的 API 文档位于：
- `docs/api/apidocs/zh_hans/` - 中文 API 文档（145+ 个接口）
- `docs/api/monitor_v3.yaml` - OpenAPI 规范文件

## 查看 API 文档

在开发环境中，可以访问：
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## 主要 API 分类

### 监控相关
- 告警策略管理
- 数据采集配置
- 告警事件处理
- 屏蔽规则管理
- 通知组管理

### 数据查询相关
- 指标查询
- 日志查询
- 事件查询
- 自定义查询

### APM 相关
- 应用管理
- 链路追踪
- 性能分析
- 服务监控

### 配置管理
- 采集配置
- 告警配置
- 系统配置
- 业务配置

### 其他功能
- 日历管理
- 报告订阅
- 场景视图
- 数据导出导入

