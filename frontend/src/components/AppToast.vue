<script setup lang="ts">
import { useThemeStore } from "@/stores/theme-store";
import { storeToRefs } from "pinia";
import Toast from "primevue/toast";

const themeStore = useThemeStore();
const { isMobile } = storeToRefs(themeStore);

const pt = {
  root: {
    style: {
      width: "100%",
      maxWidth: isMobile ? "20rem" : "25rem",
    },
  },
};
</script>

<template>
  <Toast :pt="pt" error-icon="pi pi-bolt" position="bottom-center" />
</template>
