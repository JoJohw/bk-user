<template>
  <bk-loading :loading="isLoading" class="data-source-content user-scroll-y">
    <bk-form
      v-if="props.curStep === 1 && ldapConfigData.plugin_id"
      form-type="vertical"
      ref="formRef1"
      :model="ldapConfigData"
      :rules="rulesLdapConfig">
      <Row :title="$t('服务配置')">
        <bk-form-item class="w-[560px]" :label="$t('LDAP 服务地址')" required property="server_config.server_url">
          <bk-input
            placeholder="ldap://127.0.0.1:3390"
            v-model="ldapConfigData.server_config.server_url"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <bk-form-item class="w-[560px]" :label="$t('Bind DN')" required property="server_config.bind_dn">
          <bk-input
            placeholder="cn=admin,ou=system_users,dc=bk,dc=example,dc=com"
            v-model="ldapConfigData.server_config.bind_dn"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <bk-form-item class="w-[560px]" :label="$t('Bind DN 密码')" required property="server_config.bind_password">
          <bk-input
            type="password"
            autocomplete="new-password"
            placeholder="*********"
            v-model="ldapConfigData.server_config.bind_password"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <bk-form-item class="w-[560px]" :label="$t('根目录 (Base DN)')" required property="server_config.base_dn">
          <bk-input
            placeholder="dc=bk,dc=example,dc=com"
            v-model="ldapConfigData.server_config.base_dn"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <div class="flex w-[560px]">
          <bk-form-item class="flex-1" :label="$t('分页请求每页数量')">
            <bk-input
              class="mb8"
              v-model="ldapConfigData.server_config.page_size"
              :max="100"
              :min="1"
              size="small"
              type="number"
              clearable
            />
          </bk-form-item>
          <bk-form-item
            class="ml-[24px] flex-1"
            :label="$t('请求超时时间')">
            <bk-input
              class="mb8"
              v-model="ldapConfigData.server_config.request_timeout"
              :max="100"
              :min="1"
              size="small"
              type="number"
              clearable
            />
          </bk-form-item>
        </div>
      </Row>
      <Row :title="$t('数据配置')">
        <bk-form-item class="w-[560px]" :label="$t('用户对象类')" required property="data_config.user_object_class">
          <bk-input
            placeholder="inetOrgPerson"
            v-model="ldapConfigData.data_config.user_object_class"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <bk-form-item
          class="w-[560px]"
          :label="$t('用户 Base DN')"
          :description="$t('支持同步多个 LDAP 树（森林），需为每棵树指定相应的 Base DN')">
          <div
            v-for="(item, index) in ldapConfigData.data_config.user_search_base_dns"
            :key="index"
            class="my-[15px]"
          >
            <bk-input
              placeholder="ou=company,dc=bk,dc=example,dc=com"
              v-model="ldapConfigData.data_config.user_search_base_dns[index]"
              @focus="handleFocus"
              @input="handleChange" />
            <i v-if="index !== 0" class="user-icon icon-minus-fill" @click="() => handleDelBaseDn('user', index)" />
          </div>
          <bk-button class="my-[12px] text-[14px]" text theme="primary" @click="() => handleAddBaseDn('user')">
            <i class="user-icon icon-add-2 mr8" />
            {{ $t('新增') }}
          </bk-button>
        </bk-form-item>
        <bk-form-item class="w-[560px]" :label="$t('部门对象类')" required property="data_config.dept_object_class">
          <bk-input
            placeholder="organizationalUnit"
            v-model="ldapConfigData.data_config.dept_object_class"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <bk-form-item
          class="w-[560px]"
          :label="$t('部门 Base DN')"
          :description="$t('支持同步多个 LDAP 树（森林），需为每棵树指定相应的 Base DN')">
          <div
            v-for="(item, index) in ldapConfigData.data_config.dept_search_base_dns"
            :key="index"
            class="my-[15px]"
          >
            <bk-input
              placeholder="ou=company,dc=bk,dc=example,dc=com"
              v-model="ldapConfigData.data_config.dept_search_base_dns[index]"
              @focus="handleFocus"
              @input="handleChange" />
            <i v-if="index !== 0" class="user-icon icon-minus-fill" @click="() => handleDelBaseDn('dept', index)" />
          </div>
          <bk-button class="my-[12px] text-[14px]" text theme="primary" @click="() => handleAddBaseDn('dept')">
            <i class="user-icon icon-add-2 mr8" />
            {{ $t('新增') }}
          </bk-button>
        </bk-form-item>
        <div class="btn">
          <div>
            <bk-button
              class="mr-[8px]"
              theme="primary"
              :outline="!nextDisabled"
              :loading="connectionLoading"
              @click="handleTestConnection">{{ $t('连通性测试') }}</bk-button>
            <bk-button theme="primary" class="mr8" :disabled="nextDisabled" @click="handleNext">
              {{ $t('下一步') }}
            </bk-button>
            <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
          </div>
          <div class="connection-alert" v-if="connectionStatus !== null">
            <bk-alert
              :theme="connectionStatus ? 'success' : 'error'"
              :show-icon="false">
              <template #title>
                <span>
                  <i v-if="connectionStatus" class="user-icon icon-duihao-2" />
                  <i v-else class="bk-sq-icon icon-close-fill" />
                  {{ connectionText }}
                </span>
              </template>
            </bk-alert>
          </div>
        </div>
      </Row>
    </bk-form>
    <bk-form
      v-else
      form-type="vertical"
      ref="formRef2"
      :model="fieldSettingData"
      :rules="rulesFieldSetting">
      <Row :title="$t('字段映射')">
        <FieldMapping
          :field-setting-data="fieldSettingData"
          :api-fields="apiFields"
          :rules="rulesFieldSetting"
          :source-field="$t('用户管理字段')"
          :target-field="$t('API返回字段')"
          @change-api-fields="changeApiFields"
          @handle-add-field="handleAddField"
          @handle-delete-field="handleDeleteField"
          @change-custom-field="changeCustomField" />
      </Row>
      <Row :title="$t('用户组信息')">
        <bk-checkbox class="mb-[10px]" v-model="fieldSettingData.user_group_config.enabled">
          {{ $t('支持用户组') }}
        </bk-checkbox>
        <template v-if="fieldSettingData.user_group_config.enabled">
          <bk-form-item
            class="w-[560px]" :label="$t('用户组对象类')" required
            property="user_group_config.object_class">
            <bk-select
              @change="handleChange"
              placeholder="groupOfNames"
              v-model="fieldSettingData.user_group_config.object_class">
              <bk-option
                v-for="item in userGroupClassOptions"
                :key="item.value"
                :value="item.value"
                :label="item.label"
              />
            </bk-select>
          </bk-form-item>
          <bk-form-item
            class="w-[560px]" :label="$t('用户组 Base DN')" required
            property="user_group_config.search_base_dns"
            :description="$t('支持同步多个 LDAP 树（森林），需为每棵树指定相应的 Base DN')">
            <div
              v-for="(item, index) in fieldSettingData.user_group_config.search_base_dns"
              :key="index"
              class="my-[15px]"
            >
              <bk-input
                placeholder="ou=company,dc=bk,dc=example,dc=com"
                v-model="fieldSettingData.user_group_config.search_base_dns[index]"
                @focus="handleFocus"
                @change="handleChange" />
              <i v-if="index !== 0" class="user-icon icon-minus-fill" @click="() => handleDelBaseDn('group', index)" />
            </div>
            <bk-button class="my-[12px] text-[14px]" text theme="primary" @click="() => handleAddBaseDn('group')">
              <i class="user-icon icon-add-2 mr8" />
              {{ $t('新增') }}
            </bk-button>
          </bk-form-item>
          <bk-form-item
            class="w-[560px]" :label="$t('用户组成员字段')" required
            property="user_group_config.group_member_field">
            <bk-input
              :disabled="true"
              placeholder="member / uniqueMember"
              v-model="fieldSettingData.user_group_config.group_member_field"
              @focus="handleFocus"
              @change="handleChange" />
          </bk-form-item>
        </template>
      </Row>
      <Row :title="$t('Leader 信息')">
        <bk-checkbox class="mb-[10px]" v-model="fieldSettingData.leader_config.enabled" @change="handleChange">
          {{ $t('支持用户 Leader') }}
        </bk-checkbox>
        <template v-if="fieldSettingData.leader_config.enabled">
          <bk-form-item
            class="w-[560px]" :label="$t('Leader 字段名')" required
            property="leader_config.leader_field">
            <bk-select
              class="w-[560px]"
              placeholder="manager"
              v-model="fieldSettingData.leader_config.leader_field"
              :clearable="false"
              @change="(val: string, oldVal: string) => changeApiFields(val, oldVal)">
              <bk-option
                v-for="item in apiFields"
                :key="item.key"
                :value="item.key"
                :label="item.key"
                :disabled="item.disabled"
              />
            </bk-select>
          </bk-form-item>
        </template>
      </Row>
      <Row :title="$t('同步配置')">
        <bk-form-item :label="$t('同步周期')">
          <bk-select
            class="w-[560px]"
            v-model="fieldSettingData.sync_config.sync_period"
            :clearable="false"
            @change="handleChange">
            <bk-option
              v-for="item in SYNC_CONFIG_LIST"
              :key="item.value"
              :value="item.value"
              :label="item.label"
            />
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t('同步超时时间')">
          <bk-select
            class="w-[560px]"
            :clearable="false"
            v-model="fieldSettingData.sync_config.sync_timeout"
            @change="handleChange">
            <bk-option
              v-for="item in SYNC_TIMEOUT_LIST"
              :key="item.value"
              :value="item.value"
              :label="item.label"
            />
          </bk-select>
        </bk-form-item>
        <div class="btn">
          <bk-button class="mr8" @click="handleLastStep">{{ $t('上一步') }}</bk-button>
          <bk-button theme="primary" class="mr8" :loading="submitLoading" @click="handleSubmit">
            {{ true ? $t('保存') : $t('提交') }}
          </bk-button>
          <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
      </Row>
    </bk-form>
  </bk-loading>
</template>

<script lang="ts" setup>
import { defineEmits, defineProps, inject, onMounted, ref, watch } from 'vue';

import FieldMapping from '@/components/field-mapping/FieldMapping.vue';
import Row from '@/components/layouts/ItemRow.vue';
import { useValidate } from '@/hooks';
import { getDataSourceDetails, getFields, newDataSource, postTestConnection, putDataSourceDetails } from '@/http';
import { t } from '@/language';
import router from '@/router';
import { SYNC_CONFIG_LIST, SYNC_TIMEOUT_LIST } from '@/utils';
const props = defineProps({
  curStep: {
    type: Number,
  },
  dataSourceId: {
    type: String,
  },
  isReset: {
    type: Boolean,
    default: false,
  },
});
const isLoading = ref(false);
const formRef1 = ref(null);
const formRef2 = ref(null);

interface LdapConfigData {
  plugin_id: string,
  server_config: {
    server_url: string,
    bind_dn: string,
    bind_password: string,
    base_dn: string,
    page_size: number,
    request_timeout: number
  },
  data_config: {
    user_object_class: string,
    user_search_base_dns: string[],
    dept_object_class: string,
    dept_search_base_dns: string[]
  }
}

const ldapConfigData = ref<LdapConfigData>({
  plugin_id: '',
  server_config: {
    server_url: '',
    bind_dn: '',
    bind_password: '',
    base_dn: '',
    page_size: 0,
    request_timeout: 0,
  },
  data_config: {
    user_object_class: '',
    user_search_base_dns: [],
    dept_object_class: '',
    dept_search_base_dns: [],
  },
});

const validate = useValidate();
const rulesLdapConfig = {
  'server_config.server_url': [validate.required],
  'server_config.bind_dn': [validate.required],
  'server_config.bind_password': [validate.required],
  'server_config.base_dn': [validate.required],
  'data_config.user_object_class': [validate.required],
  'data_config.dept_object_class': [validate.required],
};

const defaultLdapConfig = () => ({
  plugin_id: 'ldap',
  server_config: {
    server_url: '',
    bind_dn: '',
    bind_password: '',
    base_dn: '',
    page_size: 100,
    request_timeout: 30,
  },
  data_config: {
    user_object_class: '',
    user_search_base_dns: [''] as string[],
    dept_object_class: '',
    dept_search_base_dns: [''] as string[],
  },
});

// 重置数据
watch(() => props.isReset, () => {
  if (props.curStep === 1) {
    nextDisabled.value = true;
    connectionStatus.value = null;
    ldapConfigData.value = defaultLdapConfig();
  } else {
    const { field_mapping: fieldMapping, addFieldList, sync_config: syncConfig } = fieldSettingData.value;
    fieldMapping.builtin_fields.forEach(item => item.source_field = '');
    addFieldList.forEach(item => item.source_field = '');
    apiFields.value.forEach(item => item.disabled = false);
    syncConfig.sync_period = 24 * 60;
  }
});

const userGroupClassOptions = [
  {
    value: 'groupOfNames',
    label: 'groupOfNames',
  },
  {
    value: 'groupOfUniqueNames',
    label: 'groupOfUniqueNames',
  },
];

const fieldSettingData = ref({
  field_mapping: {
    // 内置字段
    builtin_fields: [],
    // 自定义字段
    custom_fields: [],
  },
  user_group_config: {
    enabled: true,
    object_class: '',
    search_base_dns: [''],
    group_member_field: '',
  },
  leader_config: {
    enabled: true,
    leader_field: '',
  },
  // 同步配置
  sync_config: {
    sync_period: 24 * 60,
    sync_timeout: 60 * 60,
  },
  addFieldList: [],
});
const apiFields = ref([]);
const fieldMappingList = ref([]);
const rulesFieldSetting = {
  target_field: [validate.required],
  source_field: [validate.required],
  'user_group_config.object_class': [validate.required],
  'user_group_config.group_member_field': [validate.required],
  'user_group_config.search_base_dns': [validate.required],
  'leader_config.leader_field': [validate.required],
};

const editLeaveBefore = inject('editLeaveBefore');
const handleLastStep = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }

  nextDisabled.value = true;
  connectionStatus.value = null;
  emit('updateCurStep', 1);

  fieldSettingData.value.field_mapping.builtin_fields = [];
  fieldSettingData.value.field_mapping.custom_fields = [];
  apiFields.value = [];
  fieldSettingData.value.addFieldList = [];
  if (props?.dataSourceId) {
    const res = await getDataSourceDetails(props.dataSourceId);
    fieldSettingData.value.sync_config = res.data?.sync_config;
  } else {
    fieldSettingData.value.sync_config.sync_period = 24 * 60;
  }
};

const nextDisabled = ref(true);
const connectionLoading = ref(false);
const connectionStatus = ref(null);
const connectionText = ref('');
const userProperties = ref([]);

const handleTestConnection = async () => {
  try {
    await formRef1.value.validate();
    connectionLoading.value = true;
    connectionStatus.value = null;
    // LDAP连通性测试必需要带上user_group_config、leader_config
    const params = {
      plugin_id: ldapConfigData.value.plugin_id,
      plugin_config: {
        server_config: ldapConfigData.value.server_config,
        data_config: ldapConfigData.value.data_config,
        user_group_config: {
          enabled: false,
          object_class: '',
          search_filter: '',
          group_member_field: '',
        },
        leader_config: {
          enabled: false,
          leader_field: '',
        },
      },
    };
    if (props?.dataSourceId) {
      params.data_source_id = props.dataSourceId;
    }
    const res = await postTestConnection(params);
    if (res.data.error_message === '') {
      connectionStatus.value = true;
      connectionText.value = t('测试成功');
      nextDisabled.value = false;
      userProperties.value = Object.keys(res.data?.user?.properties);
    } else {
      connectionStatus.value = false;
      connectionText.value = res.data.error_message;
      nextDisabled.value = true;
    }
  } catch (e) {
    console.warn(e);
  } finally {
    connectionLoading.value = false;
  }
};

const emit = defineEmits(['updateCurStep', 'updateSuccess']);

interface Field {
  id?: number;
  name: any;
  display_name?: string;
  data_type?: string;
  required: any;
  unique?: boolean;
  default?: string;
  options?: any[];
}

interface Item {
  target_field: any;
  source_field: any;
  mapping_operation: any;
}

const handleNext = async () => {
  try {
    emit('updateCurStep', 2);
    isLoading.value = true;
    const res = await getFields();
    if (props?.dataSourceId) {
      const list = [];
      const customList: any[] = [];
      const mapFields = (fields: Field, item: Item, isDisabled: boolean, fieldMappingType: string) => {
        if (fields.name !== item.target_field) return;

        list.push(item.source_field);
        customList.push(fields.name);
        Object.assign(fields, {
          mapping_operation: item.mapping_operation,
          source_field: item.source_field,
          disabled: isDisabled,
        });
        apiFields.value.push({ key: item.source_field, disabled: isDisabled });

        if (fieldMappingType === 'builtin_fields' && fields.required) {
          fieldSettingData.value.field_mapping.builtin_fields.push(fields);
        } else {
          fieldSettingData.value.addFieldList.push(item);
          fieldSettingData.value.field_mapping.custom_fields.push(fields);
        }
      };

      fieldMappingList.value.forEach((item) => {
        res.data?.builtin_fields?.forEach(fields => mapFields(fields, item, true, 'builtin_fields'));
        res.data?.custom_fields?.forEach(fields => mapFields(fields, item, true, 'custom_fields'));
      });

      const filterKeys = new Set(apiFields.value.map(item => item.key));

      const addApiField = (fields: { name: string }, isDisabled: boolean) => {
        if (!filterKeys.has(fields.name)) {
          apiFields.value.push({ key: fields.name, disabled: isDisabled });
          filterKeys.add(fields.name);
        }
      };

      res.data?.custom_fields?.concat(res.data?.builtin_fields || []).forEach((fields) => {
        if (!customList.includes(fields.name)) {
          fieldSettingData.value.field_mapping.custom_fields.push(fields);
        }
      });

      userProperties.value.forEach(item => addApiField({ name: item }, false));
    } else {
      const { builtin_fields: builtinFields, custom_fields: customFields } = res.data || {};

      const updateFields = (fields: any[], isBuiltin: boolean) => {
        fields.forEach((field) => {
          Object.assign(field, {
            mapping_operation: 'direct',
            source_field: '',
            disabled: isBuiltin && !field.required,
          });

          const target = isBuiltin && field.required ? 'builtin_fields' : 'custom_fields';
          fieldSettingData.value.field_mapping[target].push(field);

          if (isBuiltin && !field.required) {
            fieldSettingData.value.addFieldList.push({
              mapping_operation: 'direct',
              source_field: '',
              target_field: field.name,
            });
          }
        });
      };

      updateFields(builtinFields, true);
      updateFields(customFields, false);

      apiFields.value = userProperties.value.map(item => ({ key: item, disabled: false }));
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
  nextDisabled.value = true;
  connectionStatus.value = null;
};

watch(() => fieldSettingData.value.user_group_config.object_class, (value) => {
  if (value === 'groupOfNames') {
    fieldSettingData.value.user_group_config.group_member_field = 'member';
  }
  if (value === 'groupOfUniqueNames') {
    fieldSettingData.value.user_group_config.group_member_field = 'uniqueMember';
  }
});

const handleFocus = () => {
  window.changeInput = true;
};

const changeApiFields = (newValue: string, oldValue: string) => {
  apiFields.value.forEach((item) => {
    if (item.key === newValue) {
      item.disabled = true;
    } else if (item.key === oldValue) {
      item.disabled = false;
    }
  });
  handleChange();
};

// 新增自定义字段
const handleAddField = () => {
  fieldSettingData.value.addFieldList.push({ target_field: '', mapping_operation: 'direct', source_field: '' });
  handleChange();
};

// 删除自定义字段
const handleDeleteField = (item: { target_field: any; source_field: any; }, index: number) => {
  fieldSettingData.value.addFieldList.splice(index, 1);

  const enableField = (fields: any[], fieldKey: string, fieldName: any) => {
    const field = fields.find(element => element[fieldKey] === fieldName);
    if (field) field.disabled = false;
  };

  enableField(fieldSettingData.value.field_mapping.custom_fields, 'name', item.target_field);
  enableField(apiFields.value, 'key', item.source_field);
  handleChange();
};

// 更改自定义字段
const changeCustomField = (newValue: string, oldValue: string) => {
  fieldSettingData.value.field_mapping.custom_fields.forEach((element) => {
    if (element.name === newValue) {
      element.disabled = true;
    } else if (element.name === oldValue) {
      element.disabled = false;
    }
  });
  handleChange();
};

onMounted(async () => {
  try {
    isLoading.value = true;
    if (props?.dataSourceId) {
      const res = await getDataSourceDetails(props.dataSourceId);
      ldapConfigData.value.plugin_id = res.data?.plugin?.id;
      if (JSON.stringify(res.data?.plugin_config) !== '{}') {
        ldapConfigData.value.data_config = res.data?.plugin_config?.data_config;
        ldapConfigData.value.server_config = res.data?.plugin_config?.server_config;
        fieldSettingData.value.leader_config = res.data?.plugin_config?.leader_config;
        fieldSettingData.value.user_group_config = res.data?.plugin_config?.user_group_config;
      }
      fieldSettingData.value.sync_config = res.data?.sync_config;
      fieldMappingList.value = res.data?.field_mapping;
    } else {
      ldapConfigData.value = defaultLdapConfig();
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

const submitLoading = ref(false);

const handleSubmit = async () => {
  try {
    await formRef2.value.validate();
    submitLoading.value = true;

    const list = fieldSettingData.value.field_mapping.builtin_fields.map(item => ({
      target_field: item.name,
      mapping_operation: item.mapping_operation,
      source_field: item.source_field,
    }));

    const params = {
      plugin_config: {
        server_config: ldapConfigData.value.server_config,
        data_config: ldapConfigData.value.data_config,
        user_group_config: fieldSettingData.value.user_group_config,
        leader_config: fieldSettingData.value.leader_config,
      },
      field_mapping: [
        ...list,
        ...fieldSettingData.value.addFieldList,
      ],
      sync_config: fieldSettingData.value.sync_config,
    };

    if (props?.dataSourceId) {
      params.id = props.dataSourceId;
      await putDataSourceDetails(params);
      emit('updateSuccess', t('更新'));
    } else {
      params.plugin_id = ldapConfigData.value.plugin_id;
      await newDataSource(params);
      emit('updateSuccess', t('新建成功'));
    }
    window.changeInput = false;
  } catch (e) {
    console.warn(e);
  } finally {
    submitLoading.value = false;
  }
};

const handleCancel = () => {
  router.push({ name: 'dataSource' });
};

const handleAddBaseDn = (type: string) => {
  if (type === 'user') {
    ldapConfigData.value.data_config.user_search_base_dns.push('');
    return;
  }

  if (type === 'dept') {
    ldapConfigData.value.data_config.dept_search_base_dns.push('');
    return;
  }

  if (type === 'group') {
    fieldSettingData.value.user_group_config.search_base_dns.push('');
    return;
  }
};

const handleDelBaseDn = (type: string, index: number) => {
  if (type === 'user') {
    ldapConfigData.value.data_config.user_search_base_dns.splice(index, 1);
    return;
  }

  if (type === 'dept') {
    ldapConfigData.value.data_config.dept_search_base_dns.splice(index, 1);
    return;
  }

  if (type === 'group') {
    fieldSettingData.value.user_group_config.search_base_dns.splice(index, 1);
    return;
  }
};

</script>

<style lang="less" scoped>
.api-url-style {
  display: flex;
  align-items: center;

  .bk-button {
    margin-left: 24px;

    .bk-button-text {
      font-size: 12px;
    }

    .icon-canshu {
      margin-right: 5px;
      font-size: 14px;
    }
  }
}

.row-wrapper {
  padding: 0 24px;
  margin-bottom: 0;
  border-bottom: 1px solid #EAEBF0;

  &:last-child {
    border-bottom: none;
  }
}

.btn {
  position: relative;
  padding: 8px 0 32px;

  button {
    min-width: 88px;
  }

  .connection-alert {
    width: 100%;
    margin-top: 8px;
  }

  .icon-close-fill {
    font-size: 14px;
    color: #EA3636;
  }

  .icon-duihao-2 {
    font-size: 14px;
    color: #2DCB56;
  }
}

.icon-minus-fill {
  margin-left: 10px;
  margin-top: 8px;
  font-size: 16px;
  color: #dcdee5;
  cursor: pointer;
  position: absolute;

  &:hover {
    color: #c4c6cc;
  }
}
</style>
