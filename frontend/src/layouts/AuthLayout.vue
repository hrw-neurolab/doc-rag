<script setup lang="ts">
import AppLogo from "@/components/AppLogo.vue";
import { RouterView } from "vue-router";
import Divider from "primevue/divider";
import { useThemeStore } from "@/stores/theme-store";
import { computed } from "vue";

const { breakpoints } = useThemeStore();
const isMobile = breakpoints.smaller("tablet");
const logoDim = computed(() => (isMobile.value ? 60 : 80));
</script>

<template>
  <div class="auth-layout">
    <div class="auth-logo">
      <AppLogo :width="logoDim" :height="logoDim" />
      <Divider layout="vertical" />
      <h1 style="align-self: center">Doc Rag</h1>
    </div>
    <div class="auth-form">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
  width: 100%;
  max-width: 40rem;
  padding: 1rem 2rem;
  align-self: center;
  gap: 2rem;
}

.auth-logo {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  width: 100%;
}
</style>
