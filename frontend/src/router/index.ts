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
    {
      path: "/results",
      component: () => import("../views/Results.vue"),
      meta: { auth: true },
    },
    {
      path: "/learn/:courseId/:lessonId",
      component: () => import("../views/Learn.vue"),
      meta: { auth: true },
    },
    {
      path: "/courses/:courseId/quiz",
      component: () => import("../views/Quiz.vue"),
      meta: { auth: true },
    },
    { path: "/forbidden", component: () => import("../views/Forbidden.vue") },
    {
      path: "/admin",
      component: () => import("../views/admin/AdminLayout.vue"),
      meta: { auth: true, admin: true },
      children: [
        { path: "", component: () => import("../views/admin/Dashboard.vue") },
        {
          path: "categories",
          component: () => import("../views/admin/Categories.vue"),
        },
        {
          path: "courses",
          component: () => import("../views/admin/Courses.vue"),
        },
        {
          path: "courses/:courseId/edit",
          component: () => import("../views/admin/CourseEdit.vue"),
        },
        { path: "users", component: () => import("../views/admin/Users.vue") },
      ],
    },
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
  if (to.meta.admin && auth.user?.role !== "admin") return "/forbidden";
});
