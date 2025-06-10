<script setup lang="ts">
import { computed, ref } from "vue";
import { Divider } from "primevue";
import DesktopSidebarHeader from "@/components/sidebar/DesktopSidebarHeader.vue";
import ResourceList from "@/components/sidebar/ResourceList.vue";
import SidebarFooter from "@/components/sidebar/SidebarFooter.vue";

const opened = ref(true);
const width = computed(() => (opened.value ? "22rem" : "0"));
</script>

<template>
  <div class="sidebar-wrapper">
    <DesktopSidebarHeader v-model:opened="opened" />
    <div class="sidebar" :style="{ width }">
      <div class="sidebar-content">
        <ResourceList />
        <Divider :style="{ marginBottom: 0 }" />
        <SidebarFooter />
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar-wrapper {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.sidebar {
  height: 100%;
  overflow-x: hidden;
  transition: width 0.2s ease;
}
.sidebar-content {
  display: flex;
  flex-direction: column;
  width: 22rem;
  height: 100%;
  padding: 1rem;
  gap: 1rem;
}
</style>
