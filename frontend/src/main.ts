import "@/assets/styles/main.css";
import { createApp } from "vue";
import { createPinia } from "pinia";
import primeVueTheme from "@/prime-vue-theme";
import PrimeVue from "primevue/config";
import { ToastService, Tooltip } from "primevue";
import App from "@/App.vue";
import router from "@/router";

const app = createApp(App);

app.use(PrimeVue, primeVueTheme);
app.use(ToastService);
app.directive("tooltip", Tooltip);

app.use(createPinia());
app.use(router);

app.mount("#app");
