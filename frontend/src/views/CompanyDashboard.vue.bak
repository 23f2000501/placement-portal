<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Company Dashboard</h2>
    </header>

    <div v-if="profile" class="board-body">
      <div class="status-strip">
        <span class="company-name">{{ profile.company_name }}</span>
        <span class="status-pill" :class="profile.approved ? 'is-approved' : 'is-waiting'">
          <span class="status-dot"></span>
          {{ profile.approved ? 'Approved' : 'Waiting approval' }}
        </span>
      </div>

      <div class="panel">
        <span class="panel-dot"></span>
        <h3 class="panel-title">Create New Drive</h3>
        <form @submit.prevent="createDrive">
          <div class="field-row">
            <input class="field" v-model="title" placeholder="Job Title" required />
            <input class="field" v-model="deadline" type="date" required />
          </div>
          <textarea class="field field-area" v-model="description" placeholder="Job Description" required></textarea>
          <div class="field-row field-row-3">
            <input class="field" v-model="branch_eligibility" placeholder="Eligibility Branches" />
            <input class="field" v-model="year_eligibility" placeholder="Eligibility Years" />
            <input class="field" v-model="min_cgpa" type="number" step="0.01" placeholder="Minimum CGPA" />
          </div>
          <button class="btn-post" type="submit" :disabled="submitting">
            {{ submitting ? 'Posting…' : 'Create Drive' }}
          </button>
        </form>
      </div>

      <div class="pin-row" v-if="profile.drives && profile.drives.length">
        <div
          class="pin-card"
          v-for="(drive, i) in profile.drives"
          :key="drive.id"
          :style="{ '--tilt': tilts[i % tilts.length] + 'deg' }"
        >
          <span class="pin-dot"></span>
          <h5 class="pin-title">{{ drive.title }}</h5>
          <p class="pin-line">Status: <strong>{{ drive.status }}</strong></p>
          <p class="pin-line">Applicants: <strong>{{ drive.applicants }}</strong></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      profile: null,
      title: "",
      description: "",
      deadline: "",
      branch_eligibility: "",
      year_eligibility: "",
      min_cgpa: 0,
      submitting: false,
      tilts: [-2.5, 1.5, -1, 2]
    };
  },
  async mounted() {
    const response = await api.get("/company/dashboard");
    this.profile = response.data;
  },
  methods: {
    async createDrive() {
      this.submitting = true;
      try {
        await api.post("/company/drives", {
          title: this.title,
          description: this.description,
          application_deadline: this.deadline,
          branch_eligibility: this.branch_eligibility,
          year_eligibility: this.year_eligibility,
          min_cgpa: this.min_cgpa
        });
        window.location.reload();
      } catch (e) {
        this.submitting = false;
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
  --teal: #2ec4b6;
  --amber: #ffc857;
  min-height: 100%;
  background: var(--ink);
  background-image:
    radial-gradient(circle at 1px 1px, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 22px 22px;
  padding: 3rem 2rem 4rem;
  font-family: "Inter", sans-serif;
  color: var(--paper);
}

.board-head {
  max-width: 720px;
  margin: 0 auto 2rem;
}

.eyebrow {
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--amber);
  margin: 0 0 0.5rem;
}

.headline {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 2.75rem);
  margin: 0;
  letter-spacing: -0.01em;
}

.board-body {
  max-width: 720px;
  margin: 0 auto;
}

.status-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.company-name {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.2rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(239, 237, 247, 0.08);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.is-approved { color: var(--teal); }
.is-approved .status-dot { background: var(--teal); }
.is-waiting { color: var(--amber); }
.is-waiting .status-dot { background: var(--amber); }

.panel {
  position: relative;
  background: var(--paper);
  color: var(--ink);
  border-radius: 12px;
  padding: 2rem 1.75rem 1.75rem;
  margin-bottom: 2.5rem;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
}

.panel-dot {
  position: absolute;
  top: -9px;
  left: 28px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.35);
}

.panel-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  margin: 0 0 1.25rem;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
  margin-bottom: 0.9rem;
}

.field-row-3 {
  grid-template-columns: 1fr 1fr 1fr;
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
  box-shadow: 0 0 0 3px rgba(255, 107, 74, 0.15);
}

.field-area {
  min-height: 90px;
  resize: vertical;
  margin-bottom: 0.9rem;
}

.btn-post {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 0.95rem;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.btn-post:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(255, 107, 74, 0.35);
}

.btn-post:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pin-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2.25rem 1.5rem;
}

.pin-card {
  position: relative;
  background: var(--paper);
  color: var(--ink);
  border-radius: 10px;
  padding: 1.5rem 1.25rem 1.25rem;
  transform: rotate(var(--tilt));
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.3);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.pin-card:hover {
  transform: rotate(0deg) translateY(-3px);
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.35);
}

.pin-dot {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--teal);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
}

.pin-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.05rem;
  margin: 0 0 0.6rem;
}

.pin-line {
  margin: 0 0 0.25rem;
  font-size: 0.88rem;
  color: rgba(20, 19, 43, 0.75);
}

@media (max-width: 640px) {
  .field-row,
  .field-row-3 {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .pin-card,
  .btn-post {
    transition: none;
  }
}
</style>