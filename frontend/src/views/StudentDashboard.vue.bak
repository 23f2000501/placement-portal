<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Student Dashboard</h2>
      <p class="sub">Open drives you're eligible for, ready to apply.</p>
    </header>

    <div v-if="loading" class="note">
      <p class="note-title">Pinning up the board…</p>
    </div>

    <div v-else-if="!drives.length" class="note">
      <span class="note-dot"></span>
      <div class="note-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="M6 3v18"/>
          <path d="M6 4h12l-3 4 3 4H6"/>
        </svg>
      </div>
      <p class="note-title">No open drives right now</p>
      <p class="note-text">Check back soon — new postings show up here as they open.</p>
    </div>

    <div class="pin-row" v-else>
      <div
        class="pin-card"
        v-for="(drive, i) in drives"
        :key="drive.id"
        :style="{ '--tilt': tilts[i % tilts.length] + 'deg' }"
      >
        <span class="pin-dot"></span>
        <h5 class="pin-title">{{ drive.title }}</h5>
        <p class="pin-company">{{ drive.company_name }}</p>
        <p class="pin-deadline">Deadline: {{ drive.deadline }}</p>
        <button
          class="btn-apply"
          @click="apply(drive.id)"
          :disabled="applyingId === drive.id || appliedIds.includes(drive.id)"
        >
          {{ appliedIds.includes(drive.id) ? 'Applied' : applyingId === drive.id ? 'Applying…' : 'Apply' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      drives: [],
      loading: true,
      applyingId: null,
      appliedIds: [],
      tilts: [-2.5, 1.5, -1, 2, -2, 1]
    };
  },
  async mounted() {
    try {
      const response = await api.get("/student/dashboard");
      this.drives = response.data.drives;
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async apply(driveId) {
      this.applyingId = driveId;
      try {
        await api.post("/student/apply", { drive_id: driveId });
        this.appliedIds.push(driveId);
        alert("Applied successfully");
      } finally {
        this.applyingId = null;
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
  margin: 0 auto 2.5rem;
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
  position: relative;
  max-width: 420px;
  margin: 0 auto;
  background: var(--paper);
  color: var(--ink);
  border-radius: 10px;
  padding: 2.25rem 2rem;
  text-align: center;
  transform: rotate(-1.5deg);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
}

.note-dot {
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

.note-icon {
  width: 38px;
  height: 38px;
  margin: 0 auto 1rem;
  color: var(--accent);
}

.note-icon svg {
  width: 100%;
  height: 100%;
}

.note-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  margin: 0 0 0.4rem;
}

.note-text {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(20, 19, 43, 0.65);
  line-height: 1.5;
}

.pin-row {
  max-width: 960px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2.5rem 2rem;
}

.pin-card {
  position: relative;
  background: var(--paper);
  color: var(--ink);
  border-radius: 10px;
  padding: 1.75rem 1.5rem 1.5rem;
  transform: rotate(var(--tilt));
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  display: flex;
  flex-direction: column;
}

.pin-card:hover {
  transform: rotate(0deg) translateY(-4px);
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.4);
}

.pin-dot {
  position: absolute;
  top: -9px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--teal);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.35);
}

.pin-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  margin: 0 0 0.35rem;
}

.pin-company {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: rgba(20, 19, 43, 0.7);
  font-weight: 600;
}

.pin-deadline {
  margin: 0 0 1.1rem;
  font-size: 0.85rem;
  color: rgba(20, 19, 43, 0.55);
}

.btn-apply {
  margin-top: auto;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 0.9rem;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease, background 0.15s ease;
}

.btn-apply:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(255, 107, 74, 0.35);
}

.btn-apply:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  background: rgba(20, 19, 43, 0.35);
}

@media (prefers-reduced-motion: reduce) {
  .pin-card,
  .btn-apply {
    transition: none;
  }
}
</style>