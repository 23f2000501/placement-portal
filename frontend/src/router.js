import { createRouter, createWebHistory } from "vue-router";
import Login from "./views/Login.vue";
import RegisterStudent from "./views/RegisterStudent.vue";
import RegisterCompany from "./views/RegisterCompany.vue";
import AdminDashboard from "./views/AdminDashboard.vue";
import CompanyDashboard from "./views/CompanyDashboard.vue";
import StudentDashboard from "./views/StudentDashboard.vue";
import DriveList from "./views/DriveList.vue";
import ApplicationList from "./views/ApplicationList.vue";
import { getAuth } from "./store/auth";

const routes = [
  { path: "/", component: Login, meta: { guestOnly: true } },
  { path: "/register-student", component: RegisterStudent, meta: { guestOnly: true } },
  { path: "/register-company", component: RegisterCompany, meta: { guestOnly: true } },
  { path: "/admin", component: AdminDashboard, meta: { requiresAuth: true, allowedRoles: ["admin"] } },
  { path: "/company", component: CompanyDashboard, meta: { requiresAuth: true, allowedRoles: ["company"] } },
  { path: "/student", component: StudentDashboard, meta: { requiresAuth: true, allowedRoles: ["student"] } },
  { path: "/student/profile", component: StudentDashboard, meta: { requiresAuth: true, allowedRoles: ["student"] } },
  { path: "/drives", component: DriveList, meta: { requiresAuth: true, allowedRoles: ["student", "company", "admin"] } },
  { path: "/applications", component: ApplicationList, meta: { requiresAuth: true, allowedRoles: ["student", "company", "admin"] } }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const { user, token } = getAuth();
  const role = user?.role;
  const isLoggedIn = Boolean(token && user);

  if (to.meta.guestOnly && isLoggedIn) {
    if (role === "admin") return next("/admin");
    if (role === "company") return next("/company");
    if (role === "student") return next("/student");
    return next("/");
  }

  if (to.meta.requiresAuth && !isLoggedIn) {
    return next("/");
  }

  if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(role)) {
    if (role === "admin") return next("/admin");
    if (role === "company") return next("/company");
    if (role === "student") return next("/student");
    return next("/");
  }

  next();
});

export default router;