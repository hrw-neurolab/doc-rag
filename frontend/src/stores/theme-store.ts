import { DARK_MODE_CLASS } from "@/prime-vue-theme";
import { useBreakpoints, usePreferredDark } from "@vueuse/core";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useThemeStore = defineStore("theme", () => {
  const prefersDark = usePreferredDark();
  const isDark = ref(false);

  const initializeTheme = () => {
    const storedTheme = localStorage.getItem("theme") as "dark" | "light" | null;
    const theme = storedTheme || (prefersDark.value ? "dark" : "light");

    if (theme === "dark" && !document.documentElement.classList.contains(DARK_MODE_CLASS)) {
      document.documentElement.classList.add(DARK_MODE_CLASS);
    }

    if (storedTheme === null) {
      localStorage.setItem("theme", theme);
    }

    isDark.value = theme === "dark";
  };

  const toggleTheme = () => {
    document.documentElement.classList.toggle(DARK_MODE_CLASS);
    localStorage.setItem("theme", isDark.value ? "light" : "dark");
    isDark.value = !isDark.value;
  };

  const breakpoints = useBreakpoints({
    mobile: 0,
    tablet: 640,
    desktop: 900,
  });
  const isMobile = breakpoints.smaller("tablet");

  return { isDark, initializeTheme, toggleTheme, isMobile, breakpoints };
});
