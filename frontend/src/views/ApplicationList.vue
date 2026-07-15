<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Applications</h2>
      <p class="sub">Track every application you make and review the current status.</p>
    </header>

    <div v-if="loading" class="note">
      <span class="spinner" aria-hidden="true"></span>
      <p class="note-title">Fetching your applications…</p>
    </div>

    <div v-else-if="!applications.length" class="note">
      <p class="note-title">Nothing pinned up yet</p>
      <p class="note-text">Once applications start coming in, they'll show up here with their status.</p>
    </div>

    <div v-else class="application-grid">
      <div
        v-for="application in applications"
        :key="application.id"
        class="application-card"
        :class="statusClass(application.status)"
      >
        <div class="card-head">
          <h3>{{ application.drive_title }}</h3>
          <span class="status-badge" :class="statusClass(application.status)">
            {{ application.status }}
          </span>
        </div>
        <p class="company-name">{{ application.company_name }}</p>
        <p class="applied-on">Applied on {{ formatDateTime(application.application_date) }}</p>
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
  methods: {
    formatDateTime(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit"
      });
    },
    statusClass(status) {
      const normalized = (status || "").toLowerCase();
      if (normalized === "selected" || normalized === "confirmed") return "status-positive";
      if (normalized === "rejected") return "status-negative";
      if (normalized === "interview scheduled") return "status-info";
      return "status-pending";
    }
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
  --teal: #2ec4b6;
  --amber: #ffc857;
  --violet: #9d4edd;
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
  color: var(--amber);
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

.spinner {
  display: inline-block;
  width: 22px;
  height: 22px;
  margin-bottom: 0.9rem;
  border: 3px solid rgba(20, 19, 43, 0.15);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1rem;
  align-items: start;
}

.application-card {
  padding: 1.1rem 1.25rem;
  border-radius: 14px;
  background: rgba(239, 237, 247, 0.95);
  color: var(--ink);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
  border-left: 4px solid transparent;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.application-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.3);
}

.application-card.status-pending {
  border-left-color: var(--amber);
}

.application-card.status-info {
  border-left-color: var(--violet);
}

.application-card.status-positive {
  border-left-color: var(--teal);
}

.application-card.status-negative {
  border-left-color: var(--accent);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.application-card h3 {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.05rem;
  line-height: 1.3;
}

.status-badge {
  flex-shrink: 0;
  white-space: nowrap;
  padding: 0.28rem 0.7rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-badge.status-pending {
  background: rgba(255, 200, 87, 0.2);
  color: #8a5a00;
}

.status-badge.status-info {
  background: rgba(157, 78, 221, 0.16);
  color: #6b3fa0;
}

.status-badge.status-positive {
  background: rgba(46, 196, 182, 0.16);
  color: #17766d;
}

.status-badge.status-negative {
  background: rgba(255, 107, 74, 0.16);
  color: #b8391c;
}

.company-name {
  margin: 0 0 0.3rem;
  font-weight: 600;
  color: rgba(20, 19, 43, 0.85);
}

.applied-on {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(20, 19, 43, 0.55);
}

@media (prefers-reduced-motion: reduce) {
  .application-card {
    transition: none;
  }
  .spinner {
    animation-duration: 1.6s;
  }
}
</style>