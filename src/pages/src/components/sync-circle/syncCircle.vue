<template>
  <div class="text-[#4D4F56] text-[14px]">
    <div class="flex">
      <bk-radio-group v-model="circleValue">
        <bk-radio-button
          v-for="radio in circleList"
          :key="radio.id"
          :label="radio.id">
          {{ radio.label }}
        </bk-radio-button>
      </bk-radio-group>

      <div class="ml-[24px] flex items-center">
        <span>每隔</span>
        <bk-input :max="60" :min="0" type="number" placeholder="0" class="!w-[64px] !h-[32px] mx-[8px]" clearable />
        <span>{{ circleIntervalSuffixTextMap[circleValue] }}</span>
      </div>
    </div>

    <bk-form form-type="vertical" class="mt-[24px]" v-if="circleValue === 1">
      <bk-form-item
        label="每小时执行分钟"
        class="!mb-[12px]"
        required
        property="minute"
        description="在每小时的第 n 分钟执行同步"
      >
        <bk-input suffix="分" class="!w-[262px] mr-[16px]" />
        <i class="user-icon icon-minus-fill text-[#DCDEE5] cursor-pointer text-[18px]"></i>
      </bk-form-item>
      <div class="cursor-pointer">
        <i class="user-icon icon-add-2 text-[18px] text-[#3A84FF] mr-[8px]"></i>
        <span class="text-[14px] text-[#3A84FF]">添加分钟点</span>
      </div>
    </bk-form>

    <bk-form form-type="vertical" class="mt-[24px]" v-if="circleValue === 2">
      <bk-form-item
        label="执行时间"
        class="!mb-[12px]"
        required
        property="hours"
      >
        <bk-date-picker
          append-to-body
          clearable
          type="time"
          class="!w-[262px] mr-[16px]"
        />
        <i class="user-icon icon-minus-fill text-[#DCDEE5] cursor-pointer text-[18px]"></i>
      </bk-form-item>
      <div class="cursor-pointer">
        <i class="user-icon icon-add-2 text-[18px] text-[#3A84FF] mr-[8px]"></i>
        <span class="text-[14px] text-[#3A84FF]">添加时间点</span>
      </div>
    </bk-form>

    <div class="bg-[#fff] w-[540px] rounded-[2px] px-[12px] py-[9px] flex mt-[16px]">
      <span>执行时间预览：</span>
      <div>-</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const circleList = ref([
  {
    id: 0,
    label: '按分钟',
  },
  {
    id: 1,
    label: '按小时',
  },
  {
    id: 2,
    label: '按天',
  },
]);

const circleValue = ref(0);
const circleIntervalSuffixTextMap = {
  0: '分钟执行同步',
  1: '小时执行同步',
  2: '天执行同步',
};

</script>
