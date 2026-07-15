<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Applications</h2>
      <p class="sub">Track every application you make and review the current status.</p>
    </header>

    <div v-if="loading" class="note">
      <p class="note-title">Fetching your applications…</p>
    </div>

    <div v-else-if="!applications.length" class="note">
      <p class="note-title">Nothing pinned up yet</p>
      <p class="note-text">Once applications start coming in, they'll show up here with their status.</p>
    </div>

    <div v-else class="application-grid">
      <div v-for="application in applications" :key="application.id" class="application-card">
        <div>
          <h3>{{ application.drive_title }}</h3>
          <p><strong>Company:</strong> {{ application.company_name }}</p>
          <p><strong>Status:</strong> {{ application.status }}</p>
          <p><strong>Applied on:</strong> {{ application.application_date }}</p>
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
      applications: [],
      loading: true
    };
  },
  async mounted() {
    this.loading = true;
    try {
      const response = await api.get("/student/applications");
      this.applications = response.data || [];
    } finally {
      this.loading = false;
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
  max-width: 760px;
  margin: 0 auto 2.25rem;
}

.eyebrow {
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #ffc857;
  margin: 0 0 0.5rem;
}

.headline {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 2.75rem);
  margin: 0 0 0.4rem;
  letter-spacing: -0.01em;
}

.sub {
  margin: 0;
  color: rgba(239, 237, 247, 0.6);
  font-size: 0.95rem;
}

.note {
  max-width: 460px;
  margin: 0 auto;
  background: var(--paper);
  color: var(--ink);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
}

.note-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  margin: 0 0 0.4rem;
}

.note-text {
  margin: 0;
  font-size: 0.92rem;
  color: rgba(20, 19, 43, 0.65);
}

.application-grid {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.application-card {
  padding: 1rem 1.1rem;
  border-radius: 14px;
  background: rgba(239, 237, 247, 0.95);
  color: var(--ink);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
}

.application-card h3 {
  margin: 0 0 0.35rem;
  font-family: "Space Grotesk", sans-serif;
}

.application-card p {
  margin: 0.2rem 0;
  color: rgba(20, 19, 43, 0.7);
}
</style>
