# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Dict, List

from pydantic import BaseModel


class RawDataSourceUser(BaseModel):
    """原始数据源用户信息"""

    # 用户唯一标识
    id: str
    # 用户名，邮箱，手机号等个人信息
    properties: Dict[str, str]
    # 直接上级信息
    leaders: List[str]
    # 所属部门信息
    departments: List[str]


class RawDataSourceDepartment(BaseModel):
    """原始数据源部门信息"""

    # 部门唯一标识（如：IEG）
    id: str
    # 部门名称
    name: str
    # 上级部门
    parent: str


class TestConnectionResult(BaseModel):
    """连通性测试结果，包含示例数据"""

    error_message: str
    user: RawDataSourceUser
    department: RawDataSourceDepartment