<template>
  <div class="bg-[#F5F7FA] w-[540px] rounded-[2px] px-[12px] py-[9px] flex mt-[16px] text-[#4D4F56]">
    <span>{{ $t('执行时间预览') }}：</span>
    <div>
      <div
        v-for="(item, index) in initExecutionTime()"
        :key="index"
        class="mb-[1px]">
        {{ item }}
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { timeFormatter } from '@/common/util';

const props = defineProps<{
  type: 0 | 1 | 2,
  interval: number
  executionTime: Array<string | number>
}>();
// 时间戳
const ONE_MINUTE = 1000 * 60;
const ONE_HOUR = ONE_MINUTE * 60;
const ONE_DAY = ONE_HOUR * 24;
/** 最多可展示的预览数量 */
const PREVIEW_COUNT = 3;
/** 单个执行的预览时间 */
const MAX_LOOP = PREVIEW_COUNT + 1;
const initExecutionTime = () => {
  let futureTimes = [];
  switch (props.type) {
    case 0:
      futureTimes = getMinutePreview();
      break;
    case 1:
      futureTimes = getHourPreview();
      break;
    case 2:
      futureTimes = getDayPreview();
      break;
  }

  const curTimeStamp = new Date().valueOf();
  return futureTimes
    .filter(timeStamp => timeStamp > curTimeStamp)
    .sort()
    .map(timeStamp => timeFormatter(timeStamp, 'YYYY-MM-DD HH:mm'))
    .slice(0, PREVIEW_COUNT);
};

/** 按分钟的执行时间预览 */
const getMinutePreview = () => {
  const arr = [];
  const minuteTimeStamp = props.interval ? ONE_MINUTE * props.interval : ONE_MINUTE;
  for (let i = 0; i < MAX_LOOP; i++) {
    const t = (new Date().valueOf()) + minuteTimeStamp * i;
    arr.push(t);
  }
  return arr;
};

/** 按小时的执行时间预览 */
const getHourPreview = () => {
  const arr = [];
  const currentHour = timeFormatter(new Date(), 'YYYY-MM-DD HH');
  const hourTimeStamp = props.interval ? ONE_HOUR * props.interval : ONE_HOUR;
  for (const minute of props.executionTime) {
    for (let i = 0; i < MAX_LOOP; i++) {
      const t = (new Date(`${currentHour}:${minute}`).valueOf()) + hourTimeStamp * i;
      arr.push(t);
    }
  }
  return arr;
};

/** 按天的执行时间预览 */
const getDayPreview = () => {
  const arr = [];
  const currentDay = timeFormatter(new Date(), 'YYYY-MM-DD');
  // 一天的时间戳
  const dayTimeStamp = props.interval ? ONE_DAY * props.interval : ONE_DAY;
  for (const hourAndMinute of props.executionTime) {
    for (let i = 0; i < MAX_LOOP; i++) {
      const t = (new Date(`${currentDay} ${hourAndMinute}`).valueOf()) + dayTimeStamp * i;
      arr.push(t);
    }
  }
  return arr;
};
</script>
