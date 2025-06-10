<script setup lang="ts">
import { Button } from "primevue";
import { ref } from "vue";
import AppLogo from "@/components/AppLogo.vue";
import MobileDrawer from "@/components/sidebar/MobileDrawer.vue";

const drawerOpened = ref(false);
</script>

<template>
  <div class="navbar">
    <div class="logo">
      <AppLogo :width="50" :height="50" />
      <h2>Doc Rag</h2>
    </div>
    <Button variant="text" icon="pi pi-bars" @click="drawerOpened = !drawerOpened" />
  </div>
  <MobileDrawer v-model:opened="drawerOpened" />
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
