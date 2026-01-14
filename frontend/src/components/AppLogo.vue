<script setup lang="ts">
import { useThemeStore } from "@/stores/theme-store";
import { storeToRefs } from "pinia";
import { computed } from "vue";
import logoDark from "@/assets/images/logo-dark.svg";
import logoLight from "@/assets/images/logo-light.svg";

import hrwDark from "@/assets/images/hrw-dark.svg";
import transferhubDark from "@/assets/images/transferhub-dark.svg";
import hrwLight from "@/assets/images/hrw-light.svg";
import transferhubLight from "@/assets/images/transferhub-light.svg";


// const { width, height } = defineProps<{ width: number; height: number }>();
const { height } = defineProps<{ height: number }>();

const themeStore = useThemeStore();
const { isDark } = storeToRefs(themeStore);

// const src = computed(() => (isDark.value ? logoDark : logoLight));
const logos = computed(() => {
  return isDark.value
    ? [hrwDark, transferhubDark]
    : [hrwLight, transferhubLight];
});

</script>

<template>
  <!-- <img :src="src" alt="Logo" :width="width" :height="height" /> -->
  <div class="app-logo">
    <img
      v-for="(logo, index) in logos"
      :key="index"
      :src="logo"
      alt="Logo"
      :height="32"
    />
  </div>
</template>
