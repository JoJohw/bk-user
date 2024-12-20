# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from collections import defaultdict
from typing import Any, Dict, List

from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.data_models import AuditObject
from bkuser.apps.audit.recorder import add_audit_record, batch_add_audit_records
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.idp.models import Idp
from bkuser.apps.sync.data_models import DataSourceSyncOptions
from bkuser.apps.tenant.models import (
    Tenant,
    TenantDepartment,
    TenantManager,
    TenantUser,
    TenantUserValidityPeriodConfig,
)
from bkuser.utils.django import get_model_dict


class DataSourceAuditor:
    """用于记录数据源相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self, data_source: DataSource, waiting_delete_idps: List[Idp] | None = None):
        """记录变更前的相关数据记录"""
        self.data_befores["data_source"] = get_model_dict(data_source)
        self.data_befores["idps"] = [get_model_dict(idp) for idp in (waiting_delete_idps or [])]

    def record_create(self, data_source: DataSource):
        """记录数据源创建操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.CREATE_DATA_SOURCE,
            object_type=ObjectTypeEnum.DATA_SOURCE,
            object_id=data_source.id,
            data_after=get_model_dict(data_source),
        )

    def record_update(self, data_source: DataSource):
        """记录数据源更新操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_DATA_SOURCE,
            object_type=ObjectTypeEnum.DATA_SOURCE,
            object_id=data_source.id,
            data_before=self.data_befores["data_source"],
            data_after=get_model_dict(data_source),
        )

    def record_delete(self):
        """记录数据源删除操作"""
        data_source_audit_object = AuditObject(
            id=self.data_befores["data_source"]["id"],
            type=ObjectTypeEnum.DATA_SOURCE,
            operation=OperationEnum.DELETE_DATA_SOURCE,
            data_before=self.data_befores["data_source"],
        )
        # 记录 idp 删除前数据
        idp_audit_objects = [
            AuditObject(
                id=data_before_idp["id"],
                type=ObjectTypeEnum.IDP,
                operation=OperationEnum.DELETE_IDP,
                data_before=data_before_idp,
            )
            for data_before_idp in self.data_befores["idps"]
        ]

        batch_add_audit_records(
            operator=self.operator,
            tenant_id=self.tenant_id,
            objects=[data_source_audit_object] + idp_audit_objects,
        )

    def record_sync(self, data_source: DataSource, options: DataSourceSyncOptions):
        """记录数据源同步操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.SYNC_DATA_SOURCE,
            object_type=ObjectTypeEnum.DATA_SOURCE,
            object_id=data_source.id,
            extras={"overwrite": options.overwrite, "incremental": options.incremental, "trigger": options.trigger},
        )


class TenantUserUpdateAuditor:
    """用于记录租户用户修改操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self, tenant_user: TenantUser):
        """记录变更前的相关数据记录"""

        # 初始化对应 tenant_user 的审计数据
        self.data_befores = {
            "tenant_user": get_model_dict(tenant_user),
            "data_source_user": get_model_dict(tenant_user.data_source_user),
            # 记录修改前的用户部门
            "department_ids": list(
                DataSourceDepartmentUserRelation.objects.filter(
                    user=tenant_user.data_source_user,
                ).values_list("department_id", flat=True)
            ),
            # 记录修改前的用户上级
            "leader_ids": list(
                DataSourceUserLeaderRelation.objects.filter(user=tenant_user.data_source_user).values_list(
                    "leader_id", flat=True
                )
            ),
        }

    def record(self, tenant_user: TenantUser):
        """组装相关数据，并调用 apps.audit 模块里的方法进行记录"""

        ds_user_id = tenant_user.data_source_user.id
        ds_user_name = tenant_user.data_source_user.username
        ds_user_object = {"id": ds_user_id, "name": ds_user_name, "type": ObjectTypeEnum.DATA_SOURCE_USER}

        audit_objects: List[AuditObject] = []
        audit_objects.extend(
            [
                # 数据源用户本身信息
                AuditObject(
                    **ds_user_object,
                    operation=OperationEnum.MODIFY_DATA_SOURCE_USER,
                    data_before=self.data_befores["data_source_user"],
                    data_after=get_model_dict(tenant_user.data_source_user),
                ),
                # 数据源用户的部门
                AuditObject(
                    **ds_user_object,
                    operation=OperationEnum.MODIFY_USER_DEPARTMENT,
                    data_before={"department_ids": self.data_befores["department_ids"]},
                    data_after={
                        "department_ids": list(
                            DataSourceDepartmentUserRelation.objects.filter(
                                user=tenant_user.data_source_user,
                            ).values_list("department_id", flat=True)
                        )
                    },
                ),
                # 数据源用户的 Leader
                AuditObject(
                    **ds_user_object,
                    operation=OperationEnum.MODIFY_USER_LEADER,
                    data_before={"leader_ids": self.data_befores["leader_ids"]},
                    data_after={
                        "leader_ids": list(
                            DataSourceUserLeaderRelation.objects.filter(user=tenant_user.data_source_user).values_list(
                                "leader_id", flat=True
                            )
                        )
                    },
                ),
                # 租户用户
                AuditObject(
                    id=tenant_user.id,
                    type=ObjectTypeEnum.TENANT_USER,
                    operation=OperationEnum.MODIFY_TENANT_USER,
                    data_before=self.data_befores["tenant_user"],
                    data_after=get_model_dict(tenant_user),
                ),
            ]
        )

        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)


class TenantUserDestroyAuditor:
    """用于记录租户用户删除操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Dict] = {}

    def pre_record_data_before(self, tenant_user: TenantUser):
        """记录变更前的相关数据记录"""

        # 为每个用户的审计数据创建唯一的键
        tenant_user_id = tenant_user.id

        # 初始化对应 tenant_user 的审计数据
        # 若为本租户下的用户
        if tenant_user.tenant_id == self.tenant_id:
            self.data_befores[tenant_user_id] = {
                "tenant_user": get_model_dict(tenant_user),
                "data_source_user": get_model_dict(tenant_user.data_source_user),
                # 记录修改前的用户部门
                "department_ids": list(
                    DataSourceDepartmentUserRelation.objects.filter(
                        user=tenant_user.data_source_user,
                    ).values_list("department_id", flat=True)
                ),
                # 记录修改前的用户上级
                "leader_ids": list(
                    DataSourceUserLeaderRelation.objects.filter(user=tenant_user.data_source_user).values_list(
                        "leader_id", flat=True
                    )
                ),
                "tenant_id": tenant_user.tenant_id,
            }
        # 若为协同租户下的用户
        else:
            self.data_befores[tenant_user_id] = {
                "tenant_user": get_model_dict(tenant_user),
                "tenant_id": tenant_user.tenant_id,
            }

    def batch_pre_record_data_before(self, tenant_users: List[TenantUser]):
        """批量记录变更前的相关数据记录"""

        for tenant_user in tenant_users:
            self.pre_record_data_before(tenant_user)

    def record(self):
        """组装相关数据，并调用 apps.audit 模块里的方法进行记录"""
        audit_objects: List[AuditObject] = []

        for tenant_user_id, data_befores in self.data_befores.items():
            # 若为本租户下的用户
            if data_befores["tenant_id"] == self.tenant_id:
                ds_user_object = {
                    "id": data_befores["data_source_user"]["id"],
                    "name": data_befores["data_source_user"]["username"],
                    "type": ObjectTypeEnum.DATA_SOURCE_USER,
                }
                audit_objects.extend(self.generate_audit_objects(data_befores, tenant_user_id, ds_user_object))
            # 若为协同租户下的用户
            else:
                audit_objects.append(
                    # 协同租户用户
                    AuditObject(
                        id=tenant_user_id,
                        type=ObjectTypeEnum.TENANT_USER,
                        operation=OperationEnum.DELETE_COLLABORATION_TENANT_USER,
                        data_before=data_befores["tenant_user"],
                        extras={"collaboration_tenant_id": data_befores["tenant_id"]},
                    )
                )
        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)

    @staticmethod
    def generate_audit_objects(data_befores, tenant_user_id, ds_user_object):
        return [
            # 数据源用户本身信息
            AuditObject(
                **ds_user_object,
                operation=OperationEnum.DELETE_DATA_SOURCE_USER,
                data_before=data_befores["data_source_user"],
            ),
            # 数据源用户的部门
            AuditObject(
                **ds_user_object,
                operation=OperationEnum.DELETE_USER_DEPARTMENT,
                data_before={"department_ids": data_befores["department_ids"]},
                data_after={"department_ids": []},
            ),
            # 数据源用户的 Leader
            AuditObject(
                **ds_user_object,
                operation=OperationEnum.DELETE_USER_LEADER,
                data_before={"leader_ids": data_befores["leader_ids"]},
                data_after={"leader_ids": []},
            ),
            # 租户用户
            AuditObject(
                id=tenant_user_id,
                type=ObjectTypeEnum.TENANT_USER,
                operation=OperationEnum.DELETE_TENANT_USER,
                data_before=data_befores["tenant_user"],
            ),
        ]


class TenantUserCreateAuditor:
    """用于记录租户用户创建操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id

    def record(self, tenant_users: List[TenantUser]):
        """组装相关数据，并调用 apps.audit 模块里的方法进行记录"""
        audit_objects: List[AuditObject] = []
        for tenant_user in tenant_users:
            # 若为本租户下的用户
            if tenant_user.tenant_id == self.tenant_id:
                data_source_user = tenant_user.data_source_user
                ds_user_object = {
                    "id": data_source_user.id,
                    "name": data_source_user.username,
                    "type": ObjectTypeEnum.DATA_SOURCE_USER,
                }

                audit_objects.extend(
                    [
                        # 数据源用户本身信息
                        AuditObject(
                            **ds_user_object,
                            operation=OperationEnum.CREATE_DATA_SOURCE_USER,
                            data_after=get_model_dict(data_source_user),
                        ),
                        # 数据源用户的部门
                        AuditObject(
                            **ds_user_object,
                            operation=OperationEnum.CREATE_USER_DEPARTMENT,
                            data_after={
                                "department_ids": list(
                                    DataSourceDepartmentUserRelation.objects.filter(
                                        user=data_source_user,
                                    ).values_list("department_id", flat=True)
                                )
                            },
                        ),
                        # 租户用户信息
                        AuditObject(
                            id=tenant_user.id,
                            type=ObjectTypeEnum.TENANT_USER,
                            operation=OperationEnum.CREATE_TENANT_USER,
                            data_after=get_model_dict(tenant_user),
                        ),
                    ]
                )
            # 若为协同租户下的用户
            else:
                audit_objects.append(
                    # 协同租户用户信息
                    AuditObject(
                        id=tenant_user.id,
                        type=ObjectTypeEnum.TENANT_USER,
                        operation=OperationEnum.CREATE_COLLABORATION_TENANT_USER,
                        data_after=get_model_dict(tenant_user),
                        extras={"collaboration_tenant_id": tenant_user.tenant_id},
                    ),
                )

        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)


class TenantUserDepartmentRelationsAuditor:
    """用于记录用户-部门关系变更操作的审计"""

    def __init__(self, operator: str, tenant_id: str, data_source_user_ids: List[int]):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[int, Dict] = {}
        self.data_source_user_ids = data_source_user_ids

    def pre_record_data_before(self):
        """记录变更前的相关数据记录"""
        # 获取用户与部门之间的映射关系
        data_before_user_dept_map = self.get_user_department_map(self.data_source_user_ids)

        # 初始化 data_before, 记录变更前用户与部门之间的映射关系
        for data_source_user_id in self.data_source_user_ids:
            self.data_befores[data_source_user_id] = {"department_ids": data_before_user_dept_map[data_source_user_id]}

    def record(self, operation: OperationEnum, extras: Dict[str, List] | None = None):
        """批量记录"""
        data_source_users = DataSourceUser.objects.filter(
            id__in=self.data_source_user_ids,
        )
        # 记录变更后的用户与部门之间的映射关系
        data_after_user_dept_map = self.get_user_department_map(self.data_source_user_ids)

        audit_objects: List[AuditObject] = []

        for data_source_user in data_source_users:
            data_before = self.data_befores[data_source_user.id]
            data_after = {"department_ids": data_after_user_dept_map[data_source_user.id]}
            audit_objects.append(
                AuditObject(
                    id=data_source_user.id,
                    name=data_source_user.username,
                    type=ObjectTypeEnum.DATA_SOURCE_USER,
                    operation=operation,
                    data_before=data_before,
                    data_after=data_after,
                    extras=extras or {},
                )
            )
        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)

    @staticmethod
    def get_user_department_map(data_source_user_ids: List[int]) -> Dict:
        """记录用户与部门之间的映射关系"""
        user_department_relations = DataSourceDepartmentUserRelation.objects.filter(
            user_id__in=data_source_user_ids
        ).values("department_id", "user_id")
        user_department_map = defaultdict(list)

        # 将用户的所有部门存储在列表中
        for relation in user_department_relations:
            user_department_map[relation["user_id"]].append(relation["department_id"])

        return user_department_map


class TenantUserLeaderRelationsUpdateAuditor:
    """用于记录用户-上级关系变更操作的审计"""

    def __init__(self, operator: str, tenant_id: str, data_source_user_ids: List[int]):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[int, Dict] = {}
        self.data_source_user_ids = data_source_user_ids

    def pre_record_data_before(self):
        """记录变更前的相关数据记录"""
        # 获取用户与上级之间的映射关系
        data_before_user_leader_map = self.get_user_leader_map(self.data_source_user_ids)

        # 初始化 data_before, 记录变更前用户与上级之间的映射关系
        for data_source_user_id in self.data_source_user_ids:
            self.data_befores[data_source_user_id] = {"leader_ids": data_before_user_leader_map[data_source_user_id]}

    def record(self, extras: Dict[str, List] | None = None):
        """批量记录"""
        data_source_users = DataSourceUser.objects.filter(
            id__in=self.data_source_user_ids,
        )
        # 记录变更后的用户与上级之间的映射关系
        data_after_user_leader_map = self.get_user_leader_map(self.data_source_user_ids)

        audit_objects: List[AuditObject] = []

        for data_source_user in data_source_users:
            data_before = self.data_befores[data_source_user.id]
            data_after = {"leader_ids": data_after_user_leader_map[data_source_user.id]}
            audit_objects.append(
                AuditObject(
                    id=data_source_user.id,
                    name=data_source_user.username,
                    type=ObjectTypeEnum.DATA_SOURCE_USER,
                    operation=OperationEnum.MODIFY_USER_LEADER,
                    data_before=data_before,
                    data_after=data_after,
                    extras=extras or {},
                )
            )
        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)

    @staticmethod
    def get_user_leader_map(data_source_user_ids: List[int]) -> Dict:
        # 记录用户与上级之间的映射关系
        user_leader_relations = DataSourceUserLeaderRelation.objects.filter(user_id__in=data_source_user_ids).values(
            "leader_id", "user_id"
        )
        user_leader_map = defaultdict(list)

        # 将用户的所有上级存储在列表中
        for relation in user_leader_relations:
            user_leader_map[relation["user_id"]].append(relation["leader_id"])

        return user_leader_map


class TenantUserAccountExpiredAtUpdateAuditor:
    """用于记录租户用户账号有效期修改操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Dict] = {}

    def pre_record_data_before(self, tenant_user: TenantUser):
        self.data_befores[tenant_user.id] = {
            "account_expired_at": tenant_user.account_expired_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": tenant_user.status,
        }

    def batch_pre_record_data_before(self, tenant_users: List[TenantUser]):
        for tenant_user in tenant_users:
            self.pre_record_data_before(tenant_user)

    def record(self, tenant_user: TenantUser):
        # 重新获取 tenant_user 数据
        # Q: 为什么要重新获取？
        # A: tenant_user 的 account_expired_at 字段在存入数据库时会被转换为 UTC 时间，所以需要重新获取
        tenant_user.refresh_from_db()

        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_USER_ACCOUNT_EXPIRED_AT,
            object_type=ObjectTypeEnum.TENANT_USER,
            object_id=tenant_user.id,
            data_before=self.data_befores[tenant_user.id],
            data_after={
                "account_expired_at": tenant_user.account_expired_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": tenant_user.status,
            },
        )

    def batch_record(self, tenant_users: List[TenantUser]):
        audit_objects: List[AuditObject] = []

        audit_objects.extend(
            [
                AuditObject(
                    id=tenant_user.id,
                    type=ObjectTypeEnum.TENANT_USER,
                    operation=OperationEnum.MODIFY_USER_ACCOUNT_EXPIRED_AT,
                    data_before=self.data_befores[tenant_user.id],
                    data_after={
                        "account_expired_at": tenant_user.account_expired_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "status": tenant_user.status,
                    },
                )
                for tenant_user in tenant_users
            ]
        )
        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)


class TenantUserStatusUpdateAuditor:
    """用于记录租户用户账号状态修改操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Dict] = {}

    def pre_record_data_before(self, tenant_user: TenantUser):
        self.data_befores[tenant_user.id] = {"status": tenant_user.status}

    def batch_pre_record_data_before(self, tenant_users: List[TenantUser]):
        for tenant_user in tenant_users:
            self.pre_record_data_before(tenant_user)

    def record(self, tenant_user: TenantUser):
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_USER_STATUS,
            object_type=ObjectTypeEnum.TENANT_USER,
            object_id=tenant_user.id,
            data_before=self.data_befores[tenant_user.id],
            data_after={"status": tenant_user.status},
        )

    def batch_record(self, tenant_users: List[TenantUser]):
        audit_objects: List[AuditObject] = []

        audit_objects.extend(
            [
                AuditObject(
                    id=tenant_user.id,
                    type=ObjectTypeEnum.TENANT_USER,
                    operation=OperationEnum.MODIFY_USER_STATUS,
                    data_before=self.data_befores[tenant_user.id],
                    data_after={"status": tenant_user.status},
                )
                for tenant_user in tenant_users
            ]
        )
        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)


class TenantUserPasswordResetAuditor:
    """用于记录租户用户密码重置操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id

    def record(self, data_source_user: DataSourceUser, extras: Dict[str, int]):
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_USER_PASSWORD,
            object_type=ObjectTypeEnum.DATA_SOURCE_USER,
            object_name=data_source_user.username,
            object_id=data_source_user.id,
            extras=extras,
        )

    def batch_record(self, data_source_users: List[DataSourceUser], extras: Dict[str, int]):
        audit_objects: List[AuditObject] = []

        audit_objects.extend(
            [
                AuditObject(
                    id=data_source_user.id,
                    type=ObjectTypeEnum.DATA_SOURCE_USER,
                    name=data_source_user.username,
                    operation=OperationEnum.MODIFY_USER_PASSWORD,
                    extras=extras,
                )
                for data_source_user in data_source_users
            ]
        )
        batch_add_audit_records(self.operator, self.tenant_id, audit_objects)


class IdpAuditor:
    """用于记录认证源相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_before: Dict[str, Any] = {}

    def pre_record_data_before(self, idp: Idp):
        """记录变更前的相关数据记录"""
        self.data_before = get_model_dict(idp)

    def record_create(self, idp: Idp):
        """记录认证源创建操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.CREATE_IDP,
            object_type=ObjectTypeEnum.IDP,
            object_id=idp.id,
            data_after=get_model_dict(idp),
        )

    def record_update(self, idp: Idp):
        """记录认证源更新操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_IDP,
            object_type=ObjectTypeEnum.IDP,
            object_id=idp.id,
            data_before=self.data_before,
            data_after=get_model_dict(idp),
        )


class TenantDepartmentAuditor:
    """用于记录部门相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[int, Any] = {}

    def pre_record_data_before(self, tenant_department: TenantDepartment):
        """记录变更前的相关数据记录"""
        if tenant_department.tenant_id == self.tenant_id:
            data_source_department = tenant_department.data_source_department
            self.data_befores[tenant_department.id] = {
                "data_source_department": get_model_dict(data_source_department),
                "tenant_department": get_model_dict(tenant_department),
                "parent_department_id": DataSourceDepartmentRelation.objects.get(
                    department=data_source_department, data_source=data_source_department.data_source
                ).parent_id,
                "tenant_id": tenant_department.tenant_id,
            }
        else:
            self.data_befores[tenant_department.id] = {
                "collaboration_tenant_department": get_model_dict(tenant_department),
                "tenant_id": tenant_department.tenant_id,
            }

    def batch_pre_record_data_before(self, tenant_departments: List[TenantDepartment]):
        """批量记录变更前的相关数据记录"""
        for tenant_department in tenant_departments:
            self.pre_record_data_before(tenant_department)

    def record_create(self, tenant_departments: List[TenantDepartment]):
        """记录部门创建操作"""
        audit_records = []
        for tenant_department in tenant_departments:
            # 若为本租户下的部门
            if tenant_department.tenant_id == self.tenant_id:
                data_source_department = tenant_department.data_source_department
                ds_dept_object = {
                    "id": data_source_department.id,
                    "type": ObjectTypeEnum.DATA_SOURCE_DEPARTMENT,
                    "name": data_source_department.name,
                }

                # 父部门 ID
                parent_department_id = DataSourceDepartmentRelation.objects.get(
                    department=data_source_department, data_source=data_source_department.data_source
                ).parent_id

                audit_records.extend(
                    [
                        # 租户部门
                        AuditObject(
                            id=tenant_department.id,
                            type=ObjectTypeEnum.TENANT_DEPARTMENT,
                            operation=OperationEnum.CREATE_TENANT_DEPARTMENT,
                            data_after=get_model_dict(tenant_department),
                        ),
                        # 数据源部门
                        AuditObject(
                            **ds_dept_object,
                            operation=OperationEnum.CREATE_DATA_SOURCE_DEPARTMENT,
                            data_after=get_model_dict(data_source_department),
                        ),
                        # 租户部门父部门
                        AuditObject(
                            **ds_dept_object,
                            operation=OperationEnum.CREATE_PARENT_DEPARTMENT,
                            data_after={"parent_department": parent_department_id},
                        ),
                    ]
                )
            else:
                # 若为协同租户下的部门
                audit_records.append(
                    # 协同租户部门
                    AuditObject(
                        id=tenant_department.id,
                        type=ObjectTypeEnum.TENANT_DEPARTMENT,
                        operation=OperationEnum.CREATE_COLLABORATION_TENANT_DEPARTMENT,
                        data_after=get_model_dict(tenant_department),
                        extras={"collaboration_tenant_id": tenant_department.tenant_id},
                    )
                )
        batch_add_audit_records(self.operator, self.tenant_id, audit_records)

    def record_update(self, tenant_department: TenantDepartment):
        """记录部门更新操作"""
        data_source_department = tenant_department.data_source_department
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_DATA_SOURCE_DEPARTMENT,
            object_type=ObjectTypeEnum.DATA_SOURCE_DEPARTMENT,
            object_name=self.data_befores[tenant_department.id]["data_source_department"]["name"],
            object_id=data_source_department.id,
            data_before={"name": self.data_befores[tenant_department.id]["data_source_department"]["name"]},
            data_after={"name": data_source_department.name},
        )

    def record_update_parent_department(self, tenant_department: TenantDepartment):
        """记录租户部门父部门更新操作"""
        data_source_department = tenant_department.data_source_department
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_PARENT_DEPARTMENT,
            object_type=ObjectTypeEnum.DATA_SOURCE_DEPARTMENT,
            object_id=data_source_department.id,
            object_name=data_source_department.name,
            data_before={"parent_department_id": self.data_befores[tenant_department.id]["parent_department_id"]},
            data_after={
                "parent_department_id": DataSourceDepartmentRelation.objects.get(
                    department=data_source_department, data_source=data_source_department.data_source
                ).parent_id
            },
        )

    def record_delete(self):
        """记录部门删除操作"""
        audit_records = []
        for tenant_department_id, data_befores in self.data_befores.items():
            # 若为本租户下的部门
            if data_befores["tenant_id"] == self.tenant_id:
                ds_dept_object = {
                    "id": data_befores["data_source_department"]["id"],
                    "type": ObjectTypeEnum.DATA_SOURCE_DEPARTMENT,
                    "name": data_befores["data_source_department"]["name"],
                }
                audit_records.extend(
                    [
                        # 租户部门
                        AuditObject(
                            id=tenant_department_id,
                            type=ObjectTypeEnum.TENANT_DEPARTMENT,
                            operation=OperationEnum.DELETE_TENANT_DEPARTMENT,
                            data_before=data_befores["tenant_department"],
                        ),
                        # 数据源部门
                        AuditObject(
                            **ds_dept_object,
                            operation=OperationEnum.DELETE_DATA_SOURCE_DEPARTMENT,
                            data_before=data_befores["data_source_department"],
                        ),
                        # 租户部门父部门
                        AuditObject(
                            **ds_dept_object,
                            operation=OperationEnum.DELETE_PARENT_DEPARTMENT,
                            data_before={"parent_department_id": data_befores["parent_department_id"]},
                        ),
                    ]
                )
            else:
                # 若为协同租户下的部门
                audit_records.append(
                    # 协同租户部门
                    AuditObject(
                        id=tenant_department_id,
                        type=ObjectTypeEnum.TENANT_DEPARTMENT,
                        operation=OperationEnum.DELETE_COLLABORATION_TENANT_DEPARTMENT,
                        data_before=data_befores["collaboration_tenant_department"],
                        extras={"collaboration_tenant_id": data_befores["tenant_id"]},
                    )
                )

        batch_add_audit_records(self.operator, self.tenant_id, audit_records)


class VirtualUserAuditor:
    """用于记录虚拟用户相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self, tenant_user: TenantUser):
        """记录变更前的相关数据记录"""
        self.data_befores["tenant_user"] = get_model_dict(tenant_user)
        self.data_befores["data_source_user"] = get_model_dict(tenant_user.data_source_user)

    def record_create(self, tenant_user: TenantUser):
        """记录虚拟用户创建操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.CREATE_VIRTUAL_USER,
            object_type=ObjectTypeEnum.TENANT_USER,
            object_id=tenant_user.id,
            data_after=get_model_dict(tenant_user),
            extras={"object_type": ObjectTypeEnum.VIRTUAL_USER},
        )

        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.CREATE_VIRTUAL_USER,
            object_type=ObjectTypeEnum.DATA_SOURCE_USER,
            object_id=tenant_user.data_source_user.id,
            object_name=tenant_user.data_source_user.username,
            data_after=get_model_dict(tenant_user.data_source_user),
            extras={"object_type": ObjectTypeEnum.VIRTUAL_USER},
        )

    def record_update(self, tenant_user: TenantUser):
        """记录虚拟用户更新操作"""
        data_source_user = tenant_user.data_source_user
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_VIRTUAL_USER,
            object_type=ObjectTypeEnum.DATA_SOURCE_USER,
            object_id=data_source_user.id,
            object_name=data_source_user.username,
            data_before=self.data_befores["data_source_user"],
            data_after=get_model_dict(data_source_user),
            extras={"object_type": ObjectTypeEnum.VIRTUAL_USER},
        )

    def record_delete(self):
        """记录虚拟用户删除操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.DELETE_VIRTUAL_USER,
            object_type=ObjectTypeEnum.TENANT_USER,
            object_id=self.data_befores["tenant_user"]["id"],
            data_before=self.data_befores["tenant_user"],
            extras={"object_type": ObjectTypeEnum.VIRTUAL_USER},
        )

        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.DELETE_VIRTUAL_USER,
            object_type=ObjectTypeEnum.DATA_SOURCE_USER,
            object_id=self.data_befores["data_source_user"]["id"],
            object_name=self.data_befores["data_source_user"]["username"],
            data_before=self.data_befores["data_source_user"],
            extras={"object_type": ObjectTypeEnum.VIRTUAL_USER},
        )


class TenantUserPersonalInfoUpdateAuditor:
    """用于记录用户个人中心信息更新操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self, tenant_user: TenantUser):
        """记录变更前的相关数据记录"""
        self.data_befores["email"] = tenant_user.email
        self.data_befores["phone_info"] = tenant_user.phone_info

    def record_update_email(self, tenant_user: TenantUser):
        """记录用户邮箱更新操作"""
        # 重新获取 tenant_user 数据
        # Q: 为什么要重新获取？
        # A: 在更新邮箱的接口中，没有对 tenant_user 进行 save 操作，所以需要重新获取
        tenant_user.refresh_from_db()

        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_USER_EMAIL,
            object_type=ObjectTypeEnum.TENANT_USER,
            object_id=tenant_user.id,
            data_before={"email": self.data_befores["email"]},
            data_after={"email": tenant_user.email},
        )

    def record_update_phone(self, tenant_user: TenantUser):
        """记录用户手机号更新操作"""
        # 重新获取 tenant_user 数据
        # Q: 为什么要重新获取？
        # A: 在更新手机号的接口中，没有对 tenant_user 进行 save 操作，所以需要重新获取
        tenant_user.refresh_from_db()

        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_USER_PHONE,
            object_type=ObjectTypeEnum.TENANT_USER,
            object_id=tenant_user.id,
            data_before={"phone_info": self.data_befores["phone_info"]},
            data_after={"phone_info": tenant_user.phone_info},
        )


class TenantAuditor:
    """用于记录租户相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self, tenant: Tenant):
        """记录变更前的相关数据记录"""
        self.data_befores["tenant"] = get_model_dict(tenant)

    def record_create(self, tenant: Tenant):
        """记录租户创建操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.CREATE_TENANT,
            object_type=ObjectTypeEnum.TENANT,
            object_id=tenant.id,
            object_name=tenant.name,
            data_after=get_model_dict(tenant),
        )

    def record_update(self, tenant: Tenant):
        """记录租户更新操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_TENANT,
            object_type=ObjectTypeEnum.TENANT,
            object_id=tenant.id,
            object_name=self.data_befores["tenant"]["name"],
            data_before=self.data_befores["tenant"],
            data_after=get_model_dict(tenant),
        )

    def record_delete(self):
        """记录租户删除操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.DELETE_TENANT,
            object_type=ObjectTypeEnum.TENANT,
            object_id=self.data_befores["tenant"]["id"],
            object_name=self.data_befores["tenant"]["name"],
            data_before=self.data_befores["tenant"],
        )

    def record_update_status(self, tenant: Tenant):
        """记录租户状态更新操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_TENANT_STATUS,
            object_type=ObjectTypeEnum.TENANT,
            object_id=tenant.id,
            object_name=tenant.name,
            data_before={"status": self.data_befores["tenant"]["status"]},
            data_after={"status": tenant.status},
        )


class TenantRealManagerAuditor:
    """用于记录租户实名管理员相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self):
        """记录变更前的相关数据记录"""
        self.data_befores["real_manager_ids"] = list(
            TenantManager.objects.filter(
                tenant_id=self.tenant_id, tenant_user__data_source__type=DataSourceTypeEnum.REAL
            ).values_list("tenant_user_id", flat=True)
        )
        self.data_befores["tenant_name"] = Tenant.objects.get(id=self.tenant_id).name

    def record_create(self):
        """记录租户实名管理员创建操作"""
        self.create_audit_record(OperationEnum.CREATE_TENANT_REAL_MANAGER)

    def record_delete(self):
        """记录租户实名管理员删除操作"""
        self.create_audit_record(OperationEnum.DELETE_TENANT_REAL_MANAGER)

    def create_audit_record(self, operation: OperationEnum):
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=operation,
            object_type=ObjectTypeEnum.TENANT,
            object_id=self.tenant_id,
            object_name=self.data_befores["tenant_name"],
            data_before={"real_manager_ids": self.data_befores["real_manager_ids"]},
            data_after={
                "real_manager_ids": list(
                    TenantManager.objects.filter(
                        tenant_id=self.tenant_id, tenant_user__data_source__type=DataSourceTypeEnum.REAL
                    ).values_list("tenant_user_id", flat=True)
                )
            },
        )


class TenantUserValidityPeriodConfigUpdateAuditor:
    """用于记录租户账户有效期配置相关操作的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.data_befores: Dict[str, Any] = {}

    def pre_record_data_before(self, config: TenantUserValidityPeriodConfig):
        """记录变更前的相关数据记录"""
        self.data_befores["config"] = get_model_dict(config)

    def record(self, config: TenantUserValidityPeriodConfig):
        """记录租户账户有效期配置更新操作"""
        add_audit_record(
            operator=self.operator,
            tenant_id=self.tenant_id,
            operation=OperationEnum.MODIFY_TENANT_ACCOUNT_VALIDITY_PERIOD_CONFIG,
            object_type=ObjectTypeEnum.TENANT,
            object_id=self.tenant_id,
            object_name=config.tenant.name,
            data_before=self.data_befores["config"],
            data_after=get_model_dict(config),
        )
