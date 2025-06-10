import { createRouter, createWebHistory } from "vue-router";
import AuthLayout from "@/layouts/AuthLayout.vue";
import AppLayout from "@/layouts/AppLayout.vue";
import appRoutes from "@/router/app-routes";
import authRoutes from "./auth-routes";
import { useSessionStore } from "@/stores/session-store";
import { storeToRefs } from "pinia";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/auth",
      name: "authentication",
      component: AuthLayout,
      redirect: "/auth/login",
      children: [...authRoutes],
    },
    {
      path: "/",
      name: "app",
      component: AppLayout,
      children: [...appRoutes],
    },
  ],
});

router.beforeEach(async (to) => {
  const authPages = authRoutes.map((route) => `/auth/${route.path}`);
  const isAppPage = !authPages.includes(to.path);

  const sessionStore = useSessionStore();
  const { user } = storeToRefs(sessionStore);

  if (isAppPage && !user.value) {
    return "/auth";
  }

  if (!isAppPage && user.value) {
    return "/";
  }
});

export default router;
