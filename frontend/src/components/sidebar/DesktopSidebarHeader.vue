<script setup lang="ts">
import AppLogo from "@/components/AppLogo.vue";
import { Button } from "primevue";
import { computed } from "vue";

const opened = defineModel<boolean>("opened", { required: true });
const width = computed(() => (opened.value ? "22rem" : "9rem"));

const handleClick = () => (opened.value = !opened.value);
</script>

<template>
  <div class="sidebar-header" :style="{ width: width }">
    <div class="logo-container">
      <AppLogo :width="50" :height="50" />
      <Transition name="fade">
        <h2 style="white-space: nowrap" v-if="opened">Doc Rag</h2>
      </Transition>
    </div>
    <Button variant="text" icon="pi pi-bars" @click="handleClick" />
  </div>
</template>

<style scoped>
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  transition: width 0.2s ease;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  overflow-x: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.1s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
