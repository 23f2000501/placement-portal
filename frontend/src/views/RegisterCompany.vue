<template>
  <div class="board">
    <div class="reg-card">
      <span class="card-dot"></span>
      <p class="eyebrow">Placement Cell // Company Signup</p>
      <h3 class="headline">Company Registration</h3>

      <form @submit.prevent="register">
        <div class="field-row">
          <div class="field-group">
            <label class="field-label">Company Name</label>
            <input v-model="company_name" type="text" class="field" required />
          </div>
          <div class="field-group">
            <label class="field-label">HR Contact</label>
            <input v-model="hr_contact" type="text" class="field" required />
          </div>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label class="field-label">Website</label>
            <input v-model="website" type="url" class="field" />
          </div>
          <div class="field-group">
            <label class="field-label">Contact Person</label>
            <input v-model="contact_person" type="text" class="field" required />
          </div>
        </div>

        <div class="field-group">
          <label class="field-label">Email</label>
          <input v-model="email" type="email" class="field" required />
        </div>

        <div class="field-group">
          <label class="field-label">Password</label>
          <div class="password-row">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="field"
              required
              minlength="6"
            />
            <button class="toggle-btn" type="button" @click="showPassword = !showPassword">
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
        </div>

        <div class="field-group">
          <label class="field-label">Description</label>
          <textarea v-model="description" class="field field-area"></textarea>
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button class="btn-submit" type="submit" :disabled="loading">
          {{ loading ? 'Submitting…' : 'Submit for Approval' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      company_name: "",
      hr_contact: "",
      website: "",
      contact_person: "",
      email: "",
      password: "",
      showPassword: false,
      description: "",
      loading: false,
      errorMsg: ""
    };
  },
  methods: {
    async register() {
      this.loading = true;
      this.errorMsg = "";
      try {
        await api.post("/auth/register_company", {
          company_name: this.company_name,
          hr_contact: this.hr_contact,
          website: this.website,
          contact_person: this.contact_person,
          email: this.email,
          password: this.password,
          description: this.description
        });
        this.$router.push("/");
      } catch (e) {
        this.errorMsg = "Couldn't submit your registration. Check your details and try again.";
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
  --accent: #2ec4b6;
  min-height: 100vh;
  background: var(--ink);
  background-image:
    radial-gradient(circle at 1px 1px, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 22px 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  font-family: "Inter", sans-serif;
}

.reg-card {
  position: relative;
  width: 100%;
  max-width: 560px;
  background: var(--paper);
  color: var(--ink);
  border-radius: 12px;
  padding: 2.25rem 2.25rem 2rem;
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
  color: #ff6b4a;
  margin: 0 0 0.4rem;
}

.headline {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.85rem;
  margin: 0 0 1.5rem;
  letter-spacing: -0.01em;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.field-group {
  margin-bottom: 1.1rem;
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
  font-size: 0.92rem;
  background: #fff;
  color: var(--ink);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.field:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(46, 196, 182, 0.18);
}

.field-area {
  min-height: 80px;
  resize: vertical;
}

.password-row {
  display: flex;
  gap: 0.5rem;
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
  margin: -0.4rem 0 1rem;
}

.btn-submit {
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

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(46, 196, 182, 0.35);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>