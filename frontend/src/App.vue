<script setup lang="ts">
import { computed, onBeforeMount, onMounted } from "vue";
import { useThemeStore } from "@/stores/theme-store";
import { storeToRefs } from "pinia";
import { RouterView } from "vue-router";
import { useFavicon } from "@vueuse/core";
import AppToast from "@/components/AppToast.vue";
import { useSessionStore } from "./stores/session-store";

const themeStore = useThemeStore();
const { isDark } = storeToRefs(themeStore);

const sessionStore = useSessionStore();

const favicon = computed(() => (isDark.value ? "/favicon-dark.ico" : "/favicon-light.ico"));
useFavicon(favicon);

onBeforeMount(sessionStore.restoreSession);
onMounted(themeStore.initializeTheme);
</script>

<template>
  <AppToast />
  <RouterView />
</template>
