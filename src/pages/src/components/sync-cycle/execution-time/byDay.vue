<template>
  <bk-form-item
    :label="$t('执行时间')"
    class="!mb-[12px] mt-[24px]"
    required
    property="hour"
    :rules="rules"
  >
    <div
      v-for="(item, index) in data"
      :key="index"
      class="mb-[8px]">
      <bk-time-picker
        v-model="data[index]"
        append-to-body
        clearable
        format="HH:mm"
        type="time"
        class="!w-[262px] mr-[16px]"
      />
      <i
        class="user-icon icon-minus-fill text-[#DCDEE5] cursor-pointer text-[18px]"
        @click="handleHourPointDelete(index)">
      </i>
    </div>
  </bk-form-item>
  <div
    class="cursor-pointer inline-block select-none mt-[12px]"
    @click="handleHourPointAdd">
    <i class="user-icon icon-add-2 text-[18px] text-[#3A84FF] mr-[8px]"></i>
    <span class="text-[14px] text-[#3A84FF]">{{ $t('添加时间点') }}</span>
  </div>
</template>

<script lang="ts" setup>
import { t } from '@/language/index';

const data = defineModel<string[]>('value');
const handleHourPointAdd = () => {
  data.value.push(null);
};

const handleHourPointDelete = (index: number) => {
  if (data.value.length === 1) return;
  data.value.splice(index, 1);
};

const rules = [
  {
    message: t('必填项'),
    required: true,
    trigger: 'blur',
    validator: () => data.value.every(item => item !== null),
  },
];

</script>
