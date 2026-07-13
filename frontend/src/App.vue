<template>
  <div class="app-shell">
    <nav class="navbar">
      <a class="brand" href="#">
        <span class="brand-dot"></span>
        Placement Portal
      </a>
      <div class="nav-links">
        <router-link v-for="link in visibleLinks" :key="link.to" class="nav-link" :to="link.to">
          {{ link.label }}
        </router-link>
        <button v-if="isLoggedIn" class="nav-link logout-btn" type="button" @click="handleLogout">
          Logout
        </button>
      </div>
    </nav>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { getAuth, logout } from "./store/auth";

export default {
  data() {
    return {
      user: null,
      role: null,
      isLoggedIn: false
    };
  },
  computed: {
    visibleLinks() {
      if (!this.isLoggedIn) {
        return [{ to: "/", label: "Login" }];
      }

      if (this.role === "student") {
        return [{ to: "/student", label: "Student Dashboard" }];
      }

      if (this.role === "company") {
        return [{ to: "/company", label: "Company Dashboard" }];
      }

      if (this.role === "admin") {
        return [{ to: "/admin", label: "Admin Dashboard" }];
      }

      return [{ to: "/", label: "Login" }];
    }
  },
  created() {
    this.syncAuth();
  },
  watch: {
    $route: {
      handler() {
        this.syncAuth();
      },
      immediate: true
    }
  },
  methods: {
    syncAuth() {
      const { user, token } = getAuth();
      this.user = user;
      this.isLoggedIn = Boolean(user && token);
      this.role = user?.role || null;
    },
    handleLogout() {
      logout();
      this.syncAuth();
      this.$router.push("/");
    }
  }
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap");

.app-shell {
  min-height: 100vh;
  background: #14132b;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 1.75rem;
  background: #14132b;
  border-bottom: 1px solid rgba(239, 237, 247, 0.1);
  font-family: "Inter", sans-serif;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  color: #efedf7;
  text-decoration: none;
  letter-spacing: -0.01em;
}

.brand-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff6b4a;
  box-shadow: 0 0 0 3px rgba(255, 107, 74, 0.2);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-link {
  font-family: "Inter", sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: rgba(239, 237, 247, 0.65);
  text-decoration: none;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  transition: color 0.15s ease, background 0.15s ease;
}

.nav-link:hover {
  color: #efedf7;
  background: rgba(239, 237, 247, 0.08);
}

.nav-link.router-link-exact-active {
  color: #14132b;
  background: #ffc857;
}

.logout-btn {
  border: none;
  cursor: pointer;
  background: transparent;
}

.app-main {
  min-height: calc(100vh - 64px);
}

@media (max-width: 560px) {
  .navbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-links {
    flex-wrap: wrap;
  }
}
</style>