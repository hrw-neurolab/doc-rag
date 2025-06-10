<script setup lang="ts">
import { RouterView } from "vue-router";
import DesktopSidebar from "@/components/sidebar/DesktopSidebar.vue";
import { useThemeStore } from "@/stores/theme-store";
import MobileNavbar from "@/components/MobileNavbar.vue";
import { useResourceStore } from "@/stores/resource-store";
import { onMounted } from "vue";

const { breakpoints } = useThemeStore();
const isDesktop = breakpoints.greaterOrEqual("desktop");

const { fetchResources } = useResourceStore();
onMounted(fetchResources);
</script>

<template>
  <div :class="isDesktop ? 'desktop-layout' : 'mobile-layout'">
    <DesktopSidebar v-if="isDesktop" />
    <MobileNavbar v-else />
    <main
      class="page-container"
      :class="isDesktop ? 'desktop-page-container' : 'mobile-page-container'"
    >
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.desktop-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.mobile-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.page-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.desktop-page-container {
  align-items: center;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.mobile-page-container {
  min-height: 0;
}
</style>
