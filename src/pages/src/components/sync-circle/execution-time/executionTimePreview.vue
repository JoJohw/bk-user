<template>
  <div class="bg-[#fff] w-[540px] rounded-[2px] px-[12px] py-[9px] flex mt-[16px]">
    <span>执行时间预览：</span>
    <div v-if="type === 0">-</div>
    <template v-else>
      <div
        v-for="(item, index) in previewExecutionTime"
        :key="index">
        {{ item }}
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

import { getTimeStamp, timeFormatter } from '@/common/util';

const props = defineProps<{
  type: 0 | 1 | 2,
  executionTime: Array<string | number>
}>();

const previewExecutionTime = computed(() => {
  const format = 'YYYY-MM-DD HH:mm';
  const curTime = timeFormatter(new Date(), format);
  for (const o of props.executionTime) {
    console.log(getTimeStamp(o))
  }
  return curTime;
});

const initExecutionTime = () => {
  // 根据当前时间、每小时执行分钟[多个]、（间隔时间），获取将来执行时间

  if (props.type === 1) {

  }
}
</script>
