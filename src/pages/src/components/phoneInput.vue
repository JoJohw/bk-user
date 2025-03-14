<template>
  <div :class="['input-text', { 'input-disabled': disabled }, { 'input-style': inputStyle }]">
    <input
      type="text"
      ref="telRef"
      :class="['select-text', { 'input-error': telError }]"
      v-model="data.phone"
      :placeholder="$t('请输入')"
      :disabled="disabled"
      @blur="verifyInput"
      @focus="hiddenVerify"
      @input="handleInput"
      autofocus
    />
    <template v-if="tooltips">
      <bk-popover
        v-if="telError && data.phone"
        :content="$t(telErrorText)"
        placement="top"
      >
        <ExclamationCircleShape class="error-icon" />
      </bk-popover>
      <bk-popover
        v-if="telError && !data.phone && required"
        :content="$t('必填项')"
        placement="top"
      >
        <ExclamationCircleShape class="error-icon" />
      </bk-popover>
    </template>
    <template v-else>
      <p class="error-text" v-show="telError && data.phone">
        {{ $t(telErrorText) }}
      </p>
      <p class="error-text" v-show="telError && !data.phone && required">
        {{ $t('必填项') }}
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ExclamationCircleShape } from 'bkui-vue/lib/icon';
import intlTelInput from 'intl-tel-input/build/js/intlTelInput.min';
import telUtils from 'intl-tel-input/build/js/utils';
import { computed, defineProps, onBeforeUnmount, onMounted, ref } from 'vue';

import { COUNTRY_CODE } from '@/utils';

const props = defineProps({
  formData: {
    type: Object,
    default: () => {},
  },
  telError: {
    type: Boolean,
    default: false,
  },
  customTelErrorText: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  custom: {
    type: Boolean,
    default: false,
  },
  tooltips: {
    type: Boolean,
    default: false,
  },
  inputStyle: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(['changeCountryCode', 'changeTelError']);

const data = computed(() => {
  if (props.custom) {
    return {
      phone: props.formData.custom_phone,
      phone_country_code: props.formData.custom_phone_country_code,
    };
  }
  return props.formData;
});

const telErrorText = computed(() => {
  if (props.customTelErrorText !== '') {
    return props.customTelErrorText;
  }
  return '请填写正确的手机号';
});

const telRef = ref();
const area = ref('cn');
const iti = ref(null);

onMounted(async () => {
  if (data.value.phone_country_code) {
    COUNTRY_CODE.forEach((item) => {
      if (item.tel === data.value.phone_country_code.replace(/\+/g, '')) {
        area.value = item.short.toLowerCase();
        emit('changeCountryCode', item.tel);
      }
    });
  }
  initIntlTel();
});

onBeforeUnmount(() => {
  iti?.value.destroy();
});

const initIntlTel = () => {
  const input = telRef.value;
  try {
    iti.value = intlTelInput(input, {
      allowDropdown: true,
      separateDialCode: true, // 国旗右边显示区号
      formatOnDisplay: false, // 不自动加空格或横线
      placeholderNumberType: 'MOBILE', // 手机号码
      initialCountry: area.value, // 初始国家
      preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
      utilsScript: telUtils,
    });
  } catch (e) {
    console.warn('手机号国际化初始化失败，默认改为中国', e);
    handleInitError();
  }
  input.addEventListener('countrychange', () => {
    const countryData = iti.value.getSelectedCountryData(); // iso2(eg: cn) dialCode(eg: 86)
    area.value = countryData.iso2;
    emit('changeCountryCode', countryData.dialCode);
  });
};

const handleInitError = () => {
  const input = telRef.value;
  area.value = 'cn';
  iti.value = intlTelInput(input, {
    allowDropdown: true,
    separateDialCode: true, // 国旗右边显示区号
    formatOnDisplay: false, // 不自动加空格或横线
    placeholderNumberType: 'MOBILE', // 手机号码
    initialCountry: 'cn', // 初始国家
    preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
    utilsScript: telUtils,
  });
};

const verifyInput = () => {
  if (!props.required && data.value.phone === '') {
    return;
  }
  if (data.value.phone === '' && props.required) {
    return emit('changeTelError', true, data.value.phone);
  }
  const validation = area.value === 'cn'
    ? /^1[3-9]\d{9}$/.test(data.value.phone)
    : iti.value.isValidNumber();
  emit('changeTelError', !validation, data.value.phone);
};

const hiddenVerify = () => {
  window.changeInput = true;
};

const handleInput = () => {
  emit('changeTelError', false, data.value.phone);
};
</script>

<style lang="less">
@import url("@/css/intlTelInput.less");

.input-disabled .iti--separate-dial-code {
  .iti__selected-flag {
    cursor: no-drop;
  }

  &:hover .select-text {
    border-color: #979BA5;
  }
}
</style>

<style lang="less" scoped>
.input-text {
  position: relative;

  .error-icon {
    position: absolute;
    top: 12px;
    right: 8px;
    font-size: 16px;
    color: #ea3636;
  }

  input::placeholder {
    color: #c4c6cc;
  }

  .iti--separate-dial-code {
    &:hover .select-text {
      border-color: #979BA5;
    }

    .select-text {
      width: 100%;
      height: 32px;
      line-height: 32px;
      color: #63656e;
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      outline: none;
      resize: none;

      &:hover {
        border-color: #979BA5;
      }

      &:focus {
        border-color: #3a84ff;
      }
    }
  }
}

.input-style {
  .iti--separate-dial-code {
    &:hover .select-text {
      border-color: #979BA5;
    }

    .select-text {
      height: 40px;
      line-height: 40px;
      background: #F0F1F5;
      border: none;

      &:hover {
        border-color: #979BA5;
      }

      &:focus {
        border-color: #3a84ff;
      }
    }
  }
}

.error-text {
  position: absolute;
  margin: 2px 0 0;
  font-size: 12px;
  line-height: 18px;
  color: #ea3636;
}

.input-error {
  border: 1px solid #ea3636 !important;
}

.input-disabled {
  .select-text {
    cursor: no-drop;
  }
}
</style>
