<template>
  <bk-form form-type="vertical" class="mt-[24px]">
    <bk-form-item
      label="每小时执行分钟"
      class="!mb-[12px]"
      required
      property="minute"
      description="在每小时的第 n 分钟执行同步"
    >
      <div
        v-for="(item, index) in data"
        :key="index"
        class="mb-[8px]">
        <bk-input
          v-model="data[index]"
          suffix="分"
          class="!w-[262px] mr-[16px]" />
        <i
          class="user-icon icon-minus-fill text-[#DCDEE5] cursor-pointer text-[18px]"
          @click="handleMinutePointDelete(index)">
        </i>
      </div>
    </bk-form-item>
    <div
      class="cursor-pointer inline-block select-none"
      @click="handleMinutePointAdd">
      <i class="user-icon icon-add-2 text-[18px] text-[#3A84FF] mr-[8px]"></i>
      <span class="text-[14px] text-[#3A84FF]">添加分钟点</span>
    </div>
  </bk-form>
</template>

<script lang="ts" setup>
const data = defineModel<number[]>('value');

const handleMinutePointAdd = () => {
  data.value.push(0);
};

const handleMinutePointDelete = (index: number) => {
  if (data.value.length === 1) return;
  data.value.splice(index, 1);
};
</script>
