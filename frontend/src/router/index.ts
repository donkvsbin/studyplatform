import { createRouter, createWebHistory } from "vue-router";
import { useAuth } from "../stores/auth";
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: () => import("../views/Home.vue") },
    { path: "/courses", component: () => import("../views/Courses.vue") },
    {
      path: "/courses/:courseId",
      component: () => import("../views/CourseDetail.vue"),
    },
    {
      path: "/my-learning",
      component: () => import("../views/MyLearning.vue"),
      meta: { auth: true },
    },
    { path: "/assistant", component: () => import("../views/Assistant.vue") },
    { path: "/login", component: () => import("../views/Auth.vue") },
    { path: "/register", component: () => import("../views/Auth.vue") },
    {
      path: "/settings",
      component: () => import("../views/Settings.vue"),
      meta: { auth: true },
    },
    {
      path: "/:pathMatch(.*)*",
      component: () => import("../views/NotFound.vue"),
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
});
router.beforeEach(async (to) => {
  const auth = useAuth();
  try {
    await auth.init();
  } catch {
    /* Page requests expose backend connection failures. */
  }
  if (to.meta.auth && !auth.user)
    return { path: "/login", query: { redirect: to.fullPath } };
});
