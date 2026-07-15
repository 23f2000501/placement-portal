<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Student Dashboard</h2>
      <p class="sub">Manage your profile, review approved drives, and keep track of every application.</p>
    </header>

    <div v-if="loading" class="note">
      <p class="note-title">Pulling your placement board…</p>
    </div>

    <div v-else class="dashboard-grid">
      <section v-if="isProfileView" class="panel-card profile-panel">
        <div class="panel-head">
          <h3>Update Profile</h3>
          <p>Keep your details current before you apply.</p>
        </div>

        <div class="profile-summary">
          <div>
            <p class="summary-label">Name</p>
            <p class="summary-value">{{ profile?.name || '—' }}</p>
          </div>
          <div>
            <p class="summary-label">Branch</p>
            <p class="summary-value">{{ profile?.branch || '—' }}</p>
          </div>
          <div>
            <p class="summary-label">Year</p>
            <p class="summary-value">{{ profile?.year || '—' }}</p>
          </div>
          <div>
            <p class="summary-label">CGPA</p>
            <p class="summary-value">{{ profile?.cgpa || '—' }}</p>
          </div>
        </div>

        <form class="profile-form" @submit.prevent="saveProfile">
          <div class="field-row">
            <label class="field-group">
              <span class="field-label">Name</span>
              <input v-model="form.name" type="text" class="field" required />
            </label>
            <label class="field-group">
              <span class="field-label">Email</span>
              <input v-model="form.email" type="email" class="field" disabled />
            </label>
          </div>

          <div class="field-row">
            <label class="field-group">
              <span class="field-label">Branch</span>
              <input v-model="form.branch" type="text" class="field" required />
            </label>
            <label class="field-group">
              <span class="field-label">Year</span>
              <input v-model="form.year" type="text" class="field" required />
            </label>
          </div>

          <div class="field-row">
            <label class="field-group">
              <span class="field-label">CGPA</span>
              <input v-model="form.cgpa" type="number" step="0.01" class="field" required />
            </label>
            <label class="field-group">
              <span class="field-label">Resume URL</span>
              <input v-model="form.resume_url" type="url" class="field" />
            </label>
          </div>

          <p v-if="profileMessage" class="status-message" :class="profileMessageType">{{ profileMessage }}</p>
          <button class="btn-action" type="submit" :disabled="savingProfile">
            {{ savingProfile ? 'Saving…' : 'Save profile' }}
          </button>
        </form>
      </section>

      <template v-else>
        <section class="panel-card overview-card">
          <div class="panel-head">
            <h3>Overview</h3>
            <p>Stay updated on the latest opportunities and your recent activity.</p>
          </div>

          <div class="summary-row">
            <div class="summary-pill">
              <span class="summary-pill-label">Open Drives</span>
              <strong>{{ drives.length }}</strong>
            </div>
            <div class="summary-pill">
              <span class="summary-pill-label">Applications</span>
              <strong>{{ applications.length }}</strong>
            </div>
            <div class="summary-pill">
              <span class="summary-pill-label">Profile Status</span>
              <strong>{{ profile?.name ? 'Ready' : 'Pending' }}</strong>
            </div>
          </div>
        </section>

        <section class="panel-card">
          <div class="panel-head">
            <h3>Approved Drives</h3>
            <p>These are the placement drives currently open for applications.</p>
          </div>

          <div v-if="!drives.length" class="empty-state">No approved drives are available right now.</div>
          <div v-else class="list-stack">
            <div v-for="drive in drives" :key="drive.id" class="list-item">
              <div>
                <h4>{{ drive.title }}</h4>
                <p><strong>Company:</strong> {{ drive.company_name }}</p>
                <p><strong>Deadline:</strong> {{ drive.deadline }}</p>
              </div>
              <button
                class="btn-action"
                @click="apply(drive.id)"
                :disabled="applyingId === drive.id || appliedIds.includes(drive.id)"
              >
                {{ appliedIds.includes(drive.id) ? 'Applied' : applyingId === drive.id ? 'Applying…' : 'Apply' }}
              </button>
            </div>
          </div>
        </section>

        <section class="panel-card">
          <div class="panel-head">
            <h3>Applications & Placement History</h3>
            <p>Every submission you make is tracked here with its latest status.</p>
          </div>

          <div v-if="!applications.length" class="empty-state">You have not applied to any drive yet.</div>
          <div v-else class="list-stack">
            <div v-for="application in applications" :key="application.id" class="list-item">
              <div>
                <h4>{{ application.drive_title }}</h4>
                <p><strong>Company:</strong> {{ application.company_name }}</p>
                <p><strong>Status:</strong> {{ application.status }}</p>
                <p><strong>Applied on:</strong> {{ displayDateTime(application.application_date) }}</p>
                <div v-if="application.interview" class="interview-card">
                  <p><strong>Interview status:</strong> {{ application.interview.status || 'Pending' }}</p>
                  <p v-if="application.interview.proposed_slots?.length"><strong>Company slots:</strong> {{ application.interview.proposed_slots.join(' • ') }}</p>
                  <p v-if="application.interview.selected_slot"><strong>Selected slot:</strong> {{ displayDateTime(application.interview.selected_slot) }}</p>
                  <p v-if="application.interview.notes"><strong>Notes:</strong> {{ application.interview.notes }}</p>
                  <div class="interview-actions">
                    <template v-if="application.interview.proposed_slots?.length && application.interview.status !== 'Confirmed'">
                      <select v-model="studentSelectedSlot[application.id]" class="field field-sm">
                        <option value="">Choose a slot</option>
                        <option v-for="slot in application.interview.proposed_slots" :key="slot" :value="slot">{{ slot }}</option>
                      </select>
                      <button class="btn-action" type="button" @click="confirmInterview(application.id)">Confirm</button>
                      <button class="btn-action secondary" type="button" @click="requestReschedule(application.id)">Request reschedule</button>
                    </template>
                    <template v-else-if="application.interview.status === 'Confirmed'">
                      <template v-if="!studentRescheduleOpen[application.id]">
                        <button class="btn-action" type="button" @click="toggleReschedule(application.id)">Change slot</button>
                      </template>
                      <template v-else>
                        <button class="btn-action" type="button" @click="submitChangeSlot(application.id)">Submit change</button>
                        <button class="btn-action secondary" type="button" @click="toggleReschedule(application.id)">Cancel</button>
                      </template>
                    </template>
                  </div>

                  <div class="field-group" v-if="(application.interview.status !== 'Confirmed') || studentRescheduleOpen[application.id]">
                    <span class="field-label">If unavailable, propose alternate slot(s)</span>
                    <textarea v-model="studentProposedSlots[application.id]" class="field field-area" rows="3" placeholder="Enter preferred slots, one per line"></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      profile: null,
      drives: [],
      applications: [],
      loading: true,
      savingProfile: false,
      applyingId: null,
      appliedIds: [],
      profileMessage: "",
      profileMessageType: "success",
      form: {
        name: "",
        email: "",
        branch: "",
        year: "",
        cgpa: "",
        resume_url: ""
      },
      studentSelectedSlot: {},
      studentProposedSlots: {},
      studentRescheduleOpen: {}
    };
  },
  computed: {
    isProfileView() {
      return this.$route.path === "/student/profile";
    }
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const [profileRes, drivesRes, applicationsRes] = await Promise.all([
          api.get("/student/profile"),
          api.get("/student/dashboard"),
          api.get("/student/applications")
        ]);

        this.profile = profileRes.data;
        this.drives = drivesRes.data.drives || [];
        this.applications = applicationsRes.data || [];
        this.form = {
          name: this.profile.name || "",
          email: this.profile.email || "",
          branch: this.profile.branch || "",
          year: this.profile.year || "",
          cgpa: this.profile.cgpa || "",
          resume_url: this.profile.resume_url || ""
        };
        this.applications.forEach((application) => {
          this.studentSelectedSlot[application.id] = application.interview?.selected_slot || "";
          this.studentProposedSlots[application.id] = (application.interview?.student_proposed_slots || []).join("\n");
        });
      } catch (error) {
        console.error("Unable to load student dashboard", error);
      } finally {
        this.loading = false;
      }
    },
    toggleReschedule(applicationId) {
      this.studentRescheduleOpen[applicationId] = !this.studentRescheduleOpen[applicationId];
    },
    displayDateTime(value) {
      if (!value) return '';
      try {
        const d = new Date(value);
        if (isNaN(d.getTime())) return value;
        const year = d.getFullYear();
        // Avoid showing obviously wrong dates parsed from malformed input
        if (year < 1970 || year > 3000) return value;
        return d.toLocaleString();
      } catch (e) {
        return value;
      }
    },
    async saveProfile() {
      this.savingProfile = true;
      this.profileMessage = "";
      try {
        await api.put("/student/profile", {
          ...this.form,
          cgpa: Number(this.form.cgpa || 0)
        });
        this.profileMessage = "Profile updated successfully";
        this.profileMessageType = "success";
        this.profile = {
          ...this.profile,
          ...this.form,
          cgpa: Number(this.form.cgpa || 0)
        };
      } catch (error) {
        this.profileMessage = "Couldn't save profile right now.";
        this.profileMessageType = "error";
      } finally {
        this.savingProfile = false;
      }
    },
    async apply(driveId) {
      this.applyingId = driveId;
      try {
        await api.post("/student/apply", { drive_id: driveId });
        this.appliedIds.push(driveId);
        this.profileMessage = "Applied successfully";
        this.profileMessageType = "success";
        await this.loadData();
      } catch (error) {
        this.profileMessage = error.response?.data?.message || "Couldn't apply right now.";
        this.profileMessageType = "error";
      } finally {
        this.applyingId = null;
      }
    },
    async confirmInterview(applicationId) {
      try {
        await api.post(`/student/applications/${applicationId}/respond`, {
          selected_slot: this.studentSelectedSlot[applicationId]
        });
        this.profileMessage = "Interview slot confirmed";
        this.profileMessageType = "success";
        await this.loadData();
      } catch (error) {
        this.profileMessage = error.response?.data?.message || "Unable to confirm the slot.";
        this.profileMessageType = "error";
      }
    },
    async requestReschedule(applicationId) {
      const slots = (this.studentProposedSlots[applicationId] || "").split(/\n+/).map((slot) => slot.trim()).filter(Boolean);
      if (!slots.length) {
        this.profileMessage = "Please enter one or more alternate slots to request rescheduling.";
        this.profileMessageType = "error";
        return;
      }

      try {
        await api.post(`/student/applications/${applicationId}/respond`, {
          student_proposed_slots: slots
        });
        this.profileMessage = "Reschedule request sent";
        this.profileMessageType = "success";
        await this.loadData();
        this.studentRescheduleOpen[applicationId] = false;
      } catch (error) {
        this.profileMessage = error.response?.data?.message || "Unable to request a reschedule.";
        this.profileMessageType = "error";
      }
    },

    async submitChangeSlot(applicationId) {
      // reuse requestReschedule flow for submitting change
      await this.requestReschedule(applicationId);
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
  max-width: 920px;
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
  max-width: 420px;
  margin: 0 auto;
  background: var(--paper);
  color: var(--ink);
  border-radius: 10px;
  padding: 2.25rem 2rem;
  text-align: center;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
}

.note-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  margin: 0;
}

.dashboard-grid {
  max-width: 1160px;
  margin: 0 auto;
  display: grid;
  gap: 1.3rem;
}

.panel-card {
  background: rgba(239, 237, 247, 0.96);
  color: var(--ink);
  border-radius: 16px;
  padding: 1.35rem 1.4rem;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
}

.panel-head {
  margin-bottom: 1rem;
}

.panel-head h3 {
  margin: 0 0 0.3rem;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.1rem;
}

.panel-head p {
  margin: 0;
  color: rgba(20, 19, 43, 0.65);
  font-size: 0.92rem;
}

.overview-card {
  background: linear-gradient(135deg, rgba(255, 107, 74, 0.14), rgba(255, 200, 87, 0.16));
  border: 1px solid rgba(255, 107, 74, 0.22);
}

.profile-panel {
  background: linear-gradient(135deg, rgba(46, 196, 182, 0.16), rgba(255, 255, 255, 0.98));
  border: 1px solid rgba(46, 196, 182, 0.22);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.8rem;
}

.summary-pill {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 0.95rem 1rem;
  border-radius: 12px;
  background: rgba(20, 19, 43, 0.06);
}

.summary-pill-label {
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(20, 19, 43, 0.6);
}

.summary-pill strong {
  font-size: 1.1rem;
  color: var(--ink);
}

.profile-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.summary-label {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(20, 19, 43, 0.55);
}

.summary-value {
  margin: 0;
  font-weight: 700;
}

.profile-form {
  display: grid;
  gap: 0.8rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(20, 19, 43, 0.7);
}

.field {
  width: 100%;
  padding: 0.65rem 0.8rem;
  border: 1.5px solid rgba(20, 19, 43, 0.14);
  border-radius: 8px;
  font-family: "Inter", sans-serif;
  font-size: 0.92rem;
  background: #fff;
  color: var(--ink);
}

.field:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(255, 107, 74, 0.14);
}

.field:disabled {
  background: rgba(20, 19, 43, 0.06);
  color: rgba(20, 19, 43, 0.6);
}

.status-message {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.status-message.success {
  color: #17766d;
}

.status-message.error {
  color: #b8391c;
}

.btn-action {
  justify-self: start;
  border: none;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.btn-action:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(255, 107, 74, 0.24);
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.list-stack {
  display: grid;
  gap: 0.8rem;
}

.list-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.95rem 1rem;
  border-radius: 12px;
  background: rgba(20, 19, 43, 0.04);
}

.list-item h4 {
  margin: 0 0 0.3rem;
}

.list-item p {
  margin: 0.1rem 0;
  color: rgba(20, 19, 43, 0.7);
}

.empty-state {
  padding: 1rem;
  border-radius: 10px;
  background: rgba(20, 19, 43, 0.04);
  color: rgba(20, 19, 43, 0.7);
}

@media (max-width: 720px) {
  .list-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
