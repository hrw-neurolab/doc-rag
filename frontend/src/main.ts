import "@/assets/styles/main.css";
import { createApp } from "vue";
import { createPinia } from "pinia";
import primeVueTheme from "@/prime-vue-theme";
import PrimeVue from "primevue/config";
import { ToastService, Tooltip } from "primevue";
import App from "@/App.vue";
import router from "@/router";
import { useSessionStore } from "@/stores/session-store";

const app = createApp(App);

app.use(PrimeVue, primeVueTheme);
app.use(ToastService);
app.directive("tooltip", Tooltip);

// 1. Create Pinia instance
const pinia = createPinia();
app.use(pinia);

// 2. Restore session from localStorage BEFORE the router or components load
const sessionStore = useSessionStore();
sessionStore.restoreSession();

// 3. Now install the router and mount
app.use(router);

app.mount("#app");