<template>
  <bk-form form-type="vertical" class="mt-[24px]">
    <bk-form-item
      label="执行时间"
      class="!mb-[12px]"
      required
      property="hours"
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
      class="cursor-pointer inline-block select-none"
      @click="handleHourPointAdd">
      <i class="user-icon icon-add-2 text-[18px] text-[#3A84FF] mr-[8px]"></i>
      <span class="text-[14px] text-[#3A84FF]">添加时间点</span>
    </div>
  </bk-form>
</template>

<script lang="ts" setup>
const data = defineModel<string[]>('value');
const handleHourPointAdd = () => {
  data.value.push('08:00');
};

const handleHourPointDelete = (index: number) => {
  if (data.value.length === 1) return;
  data.value.splice(index, 1);
};

</script>
