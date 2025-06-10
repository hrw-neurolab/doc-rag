<script setup lang="ts">
import AppLogo from "@/components/AppLogo.vue";
import { useSessionStore } from "@/stores/session-store";
import { useThemeStore } from "@/stores/theme-store";
import { storeToRefs } from "pinia";
import { Divider } from "primevue";
import { computed } from "vue";

const sessionStore = useSessionStore();
const themeStore = useThemeStore();
const { isMobile } = storeToRefs(themeStore);

const logoSize = computed(() => (isMobile.value ? 150 : 200));
</script>

<template>
  <div class="welcome-screen">
    <AppLogo :width="logoSize" :height="logoSize" />
    <h1 style="text-align: center">Welcome back, {{ sessionStore.user?.first_name }}!</h1>
    <Divider />
    <p style="text-align: center">
      To get started, please select a resource from the sidebar or use the search bar to find what
      you need. At least one resource must be selected to start a chat.
    </p>
  </div>
</template>

<style scoped>
.welcome-screen {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  align-self: center;
  width: 100%;
  max-width: 30rem;
  flex-grow: 1;
}
</style>
