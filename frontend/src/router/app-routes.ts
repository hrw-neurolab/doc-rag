import type { RouteRecordRaw } from "vue-router";
import HomeView from "@/views/app/HomeView.vue";

const appRoutes: RouteRecordRaw[] = [
  {
    path: "",
    name: "home",
    component: HomeView,
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

export default appRoutes;
