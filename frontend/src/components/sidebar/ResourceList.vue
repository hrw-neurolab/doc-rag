<script setup lang="ts">
import { computed, ref } from "vue";
import { Checkbox, InputText } from "primevue";
import ResourceListItem from "@/components/sidebar/ResourceListItem.vue";
import { watchThrottled } from "@vueuse/core";
import { useResourceStore } from "@/stores/resource-store";
import { storeToRefs } from "pinia";
import AddResourceButton from "@/components/sidebar/AddResourceButton.vue";

const resourceStore = useResourceStore();
const { resources, selectedResourceIds } = storeToRefs(resourceStore);
const query = ref("");

const allSelected = computed({
  get: () =>
    selectedResourceIds.value.size > 0 && selectedResourceIds.value.size === resources.value.length,
  set: (value: boolean) => {
    if (value) {
      resources.value.forEach((r) => selectedResourceIds.value.add(r._id));
      return;
    }
    selectedResourceIds.value.clear();
  },
});

watchThrottled(query, () => resourceStore.fetchResources(query.value), { throttle: 300 });
</script>

<template>
  <h2>Resources</h2>
  <AddResourceButton />
  <div class="resource-filter">
    <Checkbox
      size="large"
      :indeterminate="selectedResourceIds.size > 0 && selectedResourceIds.size < resources.length"
      binary
      v-model="allSelected"
    />
    <InputText :style="{ flexGrow: 1 }" v-model="query" placeholder="Search..." />
  </div>
  <div class="resource-list">
    <ResourceListItem v-for="resource in resources" :key="resource._id" :resource="resource" />
  </div>
</template>

<style scoped>
.resource-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.resource-list {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow-y: auto;
  gap: 0.5rem;
}
</style>
