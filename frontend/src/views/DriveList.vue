<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Placement Drives</h2>
      <p class="sub">Browse approved drives and apply when a role matches your profile.</p>
    </header>

    <div v-if="loading" class="note">
      <p class="note-title">Loading approved drives…</p>
    </div>

    <div v-else-if="!drives.length" class="note">
      <p class="note-title">No drives pinned up yet</p>
      <p class="note-text">Approved drives will land here as soon as companies post them.</p>
    </div>

    <div v-else class="drive-grid">
      <div v-for="drive in drives" :key="drive.id" class="drive-card">
        <div>
          <h3>{{ drive.title }}</h3>
          <p><strong>Company:</strong> {{ drive.company_name }}</p>
          <p><strong>Deadline:</strong> {{ drive.deadline }}</p>
        </div>
        <button class="btn-action" @click="apply(drive.id)" :disabled="applyingId === drive.id || appliedIds.includes(drive.id)">
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
      appliedIds: []
    };
  },
  async mounted() {
    await this.loadDrives();
  },
  methods: {
    async loadDrives() {
      this.loading = true;
      try {
        const response = await api.get("/student/dashboard");
        this.drives = response.data.drives || [];
      } finally {
        this.loading = false;
      }
    },
    async apply(driveId) {
      this.applyingId = driveId;
      try {
        await api.post("/student/apply", { drive_id: driveId });
        this.appliedIds.push(driveId);
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

.drive-grid {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.drive-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border-radius: 14px;
  background: rgba(239, 237, 247, 0.95);
  color: var(--ink);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
}

.drive-card h3 {
  margin: 0 0 0.35rem;
  font-family: "Space Grotesk", sans-serif;
}

.drive-card p {
  margin: 0.2rem 0;
  color: rgba(20, 19, 43, 0.7);
}

.btn-action {
  border: none;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 700px) {
  .drive-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
