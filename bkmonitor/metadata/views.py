# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2025 Tencent. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from blueapps.account.decorators import login_exempt
from django.utils.decorators import method_decorator
from core.drf_resource.viewsets import ResourceRoute, ResourceViewSet
from metadata.resources.resources import (
    GetConsulFeatureFlagConfigResource,
    GetConsulStorageConfigResource,
    GetRedisFeatureFlagConfigResource,
    GetRedisStorageConfigResource,
)


@method_decorator(login_exempt, name='dispatch')
class ConfigCheckViewSet(ResourceViewSet):
    """
    配置检查 ViewSet
    用于检查 refresh_consul_storage_config、refresh_redis_storage_config、
    refresh_consul_feature_flag_config、refresh_redis_feature_flag_config 配置是否正确写入
    """

    resource_routes = [
        ResourceRoute("GET", GetConsulStorageConfigResource, endpoint="get_consul_storage_config"),
        ResourceRoute("GET", GetRedisStorageConfigResource, endpoint="get_redis_storage_config"),
        ResourceRoute("GET", GetConsulFeatureFlagConfigResource, endpoint="get_consul_feature_flag_config"),
        ResourceRoute("GET", GetRedisFeatureFlagConfigResource, endpoint="get_redis_feature_flag_config"),
    ]
