<script setup lang="ts">
import { Drawer } from "primevue";
import ResourceList from "@/components/sidebar/ResourceList.vue";
import SidebarFooter from "@/components/sidebar/SidebarFooter.vue";

const opened = defineModel<boolean>("opened", { required: true });
</script>

<template>
  <Drawer position="right" v-model:visible="opened">
    <div class="sidebar-content">
      <ResourceList />
    </div>

    <template #footer>
      <SidebarFooter />
    </template>
  </Drawer>
</template>

<style scoped>
.drawer-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
