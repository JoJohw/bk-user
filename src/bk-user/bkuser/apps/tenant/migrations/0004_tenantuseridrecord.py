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
# Generated by Django 3.2.25 on 2024-08-28 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_source', '0002_init_builtin_data_source_plugin'),
        ('tenant', '0003_init_default_tenant'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantUserIDRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=128, verbose_name='用户在数据源中的唯一标识')),
                ('tenant_user_id', models.CharField(max_length=128, verbose_name='租户用户 ID')),
                ('data_source', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='data_source.datasource')),
                ('tenant', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='tenant.tenant')),
            ],
            options={
                'unique_together': {('tenant', 'data_source', 'code')},
            },
        ),
    ]
