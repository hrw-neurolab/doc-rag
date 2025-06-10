<script setup lang="ts">
import { useThemeStore } from "@/stores/theme-store";
import { storeToRefs } from "pinia";
import { computed } from "vue";
import logoDark from "@/assets/images/logo-dark.svg";
import logoLight from "@/assets/images/logo-light.svg";

const { width, height } = defineProps<{ width: number; height: number }>();

const themeStore = useThemeStore();
const { isDark } = storeToRefs(themeStore);

const src = computed(() => (isDark.value ? logoDark : logoLight));
</script>

<template>
  <img :src="src" alt="Logo" :width="width" :height="height" />
</template>
