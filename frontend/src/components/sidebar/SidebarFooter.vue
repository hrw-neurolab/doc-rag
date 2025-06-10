<script setup lang="ts">
import { useSessionStore } from "@/stores/session-store";
import { useRouter } from "vue-router";
import { Button } from "primevue";
import { useThemeStore } from "@/stores/theme-store";
import { storeToRefs } from "pinia";

const sessionStore = useSessionStore();
const router = useRouter();
const themeStore = useThemeStore();
const { isDark } = storeToRefs(themeStore);

const logout = () => {
  sessionStore.clearSession();
  router.push("/auth/login");
};
</script>

<template>
  <div class="sidebar-footer">
    <Button label="Logout" icon="pi pi-sign-out" variant="text" @click="logout" />
    <Button
      :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
      variant="text"
      v-tooltip="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
      @click="themeStore.toggleTheme"
    />
  </div>
</template>

<style scoped>
.sidebar-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
