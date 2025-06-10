<script setup lang="ts">
import routes from "@/api/routes";
import { useApi } from "@/api/use-api";
import { useResourceStore } from "@/stores/resource-store";
import type { Resource } from "@/types/api";
import { storeToRefs } from "pinia";
import { Button, Checkbox, Menu } from "primevue";
import { computed, ref, useTemplateRef } from "vue";

const { resource } = defineProps<{ resource: Resource }>();

const resourceStore = useResourceStore();
const { resources, selectedResourceIds } = storeToRefs(resourceStore);

const icon = computed(() => (resource.type === "pdf" ? "pi pi-file-pdf" : "pi pi-globe"));
const selected = computed({
  get: () => selectedResourceIds.value.has(resource._id),
  set: (value: boolean) => {
    if (!value) {
      selectedResourceIds.value.delete(resource._id);
      return;
    }
    selectedResourceIds.value.add(resource._id);
  },
});

const pt = {
  root: {
    style: {
      justifyContent: "flex-start",
      flexGrow: 1,
    },
  },
  label: {
    style: {
      flexGrow: 1,
      textAlign: "left",
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap",
    },
  },
};

const menu = useTemplateRef("menu");
const toggleMenu = (e: MouseEvent) => menu.value?.toggle(e);
const { del } = useApi(routes.resources.delete.deleteResource);

const handleDelete = async () => {
  await del({ routeParams: [resource._id], successMessage: "Resource deleted." });
  resources.value = resources.value.filter((r) => r._id !== resource._id);
  selectedResourceIds.value.delete(resource._id);
};

const menuContent = ref([
  {
    label: "Actions",
    items: [
      {
        label: "Delete",
        icon: "pi pi-trash",
        command: handleDelete,
      },
    ],
  },
]);
</script>

<template>
  <div class="resource-list-item">
    <Checkbox v-model="selected" binary />
    <Button
      :severity="selected ? 'secondary' : undefined"
      :variant="selected ? undefined : 'text'"
      :icon="icon"
      :label="resource.title"
      v-tooltip="resource.title"
      :pt="pt"
      @click="selected = !selected"
    />
    <Button variant="text" icon="pi pi-ellipsis-v" @click="toggleMenu" />
    <Menu ref="menu" :model="menuContent" popup />
  </div>
</template>

<style scoped>
.resource-list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}
</style>
