<template>
  <div class="text-[#4D4F56] text-[14px]">
    <div class="flex">
      <bk-radio-group v-model="syncCycle" @change="handleSyncCycleChange">
        <bk-radio-button
          v-for="radio in radioOptions"
          :key="radio.id"
          :label="radio.id">
          {{ radio.label }}
        </bk-radio-button>
      </bk-radio-group>

      <div class="ml-[24px] flex items-center">
        <span>{{ $t('每隔') }}</span>
        <bk-input
          :max="60"
          :min="1"
          v-model="curInterValTime"
          @change="handleIntervalTimeChange"
          type="number"
          placeholder="0"
          class="!w-[64px] !h-[32px] mx-[8px]" />
        <span>{{ cycleIntervalSuffixTextMap[syncCycle] }}</span>
      </div>
    </div>

    <ByHour
      v-if="syncCycle === 1"
      v-model:value="form.hour.executionTime" />

    <ByDay
      v-if="syncCycle === 2"
      v-model:value="form.day.executionTime" />

    <ExecutionTimePreview
      :type="syncCycle"
      :interval="curInterValTime"
      :execution-time="curExecutionTime" />
  </div>
</template>

<script lang="ts" setup>
import { computed, reactive, ref } from 'vue';

import ByDay from './execution-time/byDay.vue';
import ByHour from './execution-time/byHour.vue';
import ExecutionTimePreview from './execution-time/executionTimePreview.vue';

import { t } from '@/language/index';
/** 同步周期类型 */
type SyncCycleType = keyof typeof cycleIntervalSuffixTextMap;

const DEFAULT_MINUTE_BY_HOUR = 0;
const DEFAULT_HOUR_BT_DAY = '08:00:00';

/** 同步周期选项 */
const radioOptions = ref([
  {
    id: 0,
    label: t('按分钟'),
  },
  {
    id: 1,
    label: t('按小时'),
  },
  {
    id: 2,
    label: t('按天'),
  },
]);
const cycleIntervalSuffixTextMap = {
  0: t('分钟执行同步'),
  1: t('小时执行同步'),
  2: t('天执行同步'),
};
/** 当前选择的同步周期 */
const syncCycle = ref<SyncCycleType>(0);

const curInterValTime = ref(1);
/** 已添加的执行时间(小时/天) */
const form = reactive({
  minute: {
    interval: 1,
  },
  hour: {
    interval: 1,
    executionTime: [DEFAULT_MINUTE_BY_HOUR],
  },
  day: {
    interval: 1,
    executionTime: [DEFAULT_HOUR_BT_DAY],
  },
});

const curExecutionTime = computed(() => {
  if (syncCycle.value === 1) {
    return form.hour.executionTime;
  }
  if (syncCycle.value === 2) {
    return form.day.executionTime;
  }
  return [];
});

const handleSyncCycleChange = (value: SyncCycleType) => {
  switch (value) {
    case 0:
      curInterValTime.value = form.minute.interval;
      break;
    case 1:
      curInterValTime.value = form.hour.interval;
      break;
    case 2:
      curInterValTime.value = form.day.interval;
      break;
  }
};

const handleIntervalTimeChange = (value: number) => {
  switch (syncCycle.value) {
    case 0:
      form.minute.interval = value;
      break;
    case 1:
      form.hour.interval = value;
      break;
    case 2:
      form.day.interval = value;
      break;
  }
};

</script>
