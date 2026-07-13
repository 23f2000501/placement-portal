<template>
  <div class="board">
    <div class="login-card">
      <span class="card-dot"></span>
      <p class="eyebrow">Placement Cell // Sign In</p>
      <h3 class="headline">Login</h3>

      <form @submit.prevent="login">
        <label class="field-label">Email</label>
        <input v-model="email" type="email" class="field" required />

        <label class="field-label">Password</label>
        <div class="password-row">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="field"
            required
          />
          <button class="toggle-btn" type="button" @click="showPassword = !showPassword">
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button class="btn-login" type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Login' }}
        </button>
      </form>

      <div class="signup-links">
        <router-link to="/register-student">Student signup</router-link>
        <span class="dot-sep">•</span>
        <router-link to="/register-company">Company signup</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";
import { saveAuth } from "../store/auth";

export default {
  data() {
    return {
      email: "",
      password: "",
      showPassword: false,
      loading: false,
      errorMsg: ""
    };
  },
  methods: {
    async login() {
      this.loading = true;
      this.errorMsg = "";
      try {
        const response = await api.post("/auth/login", {
          email: this.email,
          password: this.password
        });
        saveAuth(response.data.user, response.data.access_token);
        const role = response.data.user.role;
        if (role === "admin") this.$router.push("/admin");
        else if (role === "company") this.$router.push("/company");
        else this.$router.push("/student");
      } catch (e) {
        this.errorMsg = "Couldn't log in. Check your email and password.";
        this.loading = false;
        throw e;
      }
    }
  }
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap");

.board {
  --ink: #14132b;
  --paper: #efedf7;
  --accent: #ff6b4a;
  min-height: 100vh;
  background: var(--ink);
  background-image:
    radial-gradient(circle at 1px 1px, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 22px 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  font-family: "Inter", sans-serif;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  background: var(--paper);
  color: var(--ink);
  border-radius: 12px;
  padding: 2.25rem 2rem 2rem;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.4);
}

.card-dot {
  position: absolute;
  top: -9px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.35);
}

.eyebrow {
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.75rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #2ec4b6;
  margin: 0 0 0.4rem;
}

.headline {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.9rem;
  margin: 0 0 1.5rem;
  letter-spacing: -0.01em;
}

.field-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
  color: rgba(20, 19, 43, 0.7);
}

.field {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1.5px solid rgba(20, 19, 43, 0.15);
  border-radius: 8px;
  font-family: "Inter", sans-serif;
  font-size: 0.95rem;
  background: #fff;
  color: var(--ink);
  margin-bottom: 1.1rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.field:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(255, 107, 74, 0.15);
}

.password-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.1rem;
}

.password-row .field {
  margin-bottom: 0;
}

.toggle-btn {
  flex-shrink: 0;
  font-family: "Inter", sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0 0.9rem;
  border-radius: 8px;
  border: 1.5px solid rgba(20, 19, 43, 0.15);
  background: #fff;
  color: var(--ink);
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.toggle-btn:hover {
  border-color: var(--accent);
}

.error-msg {
  color: #d64545;
  font-size: 0.85rem;
  margin: -0.5rem 0 1rem;
}

.btn-login {
  width: 100%;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 0.98rem;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(255, 107, 74, 0.35);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.signup-links {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.88rem;
}

.signup-links a {
  color: var(--ink);
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1.5px solid var(--accent);
}

.signup-links a:hover {
  color: var(--accent);
}

.dot-sep {
  margin: 0 0.6rem;
  color: rgba(20, 19, 43, 0.35);
}
</style>