import type { RouteRecordRaw } from "vue-router";
import LoginView from "@/views/auth/LoginView.vue";
import RegisterView from "@/views/auth/RegisterView.vue";

const authRoutes: RouteRecordRaw[] = [
  {
    path: "login",
    name: "login",
    component: LoginView,
  },
  {
    path: "register",
    name: "register",
    component: RegisterView,
  },
];

export default authRoutes;
