<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Student Dashboard</h2>
      <p class="sub">Manage your profile, review approved drives, and keep track of every application.</p>
    </header>

    <div v-if="loading" class="note" role="status" aria-live="polite">
      <span class="note-spinner" aria-hidden="true"></span>
      <p class="note-title">Pulling your placement board…</p>
    </div>

    <div v-else class="dashboard-grid">
      <section v-if="isProfileView" class="panel-card profile-panel">
        <div class="panel-head">
          <h3>Update Profile</h3>
          <p>Keep your details current before you apply.</p>
        </div>

        <div class="profile-summary">
          <div class="summary-fact">
            <p class="summary-label">Name</p>
            <p class="summary-value">{{ profile?.name || '—' }}</p>
          </div>
          <div class="summary-fact">
            <p class="summary-label">Branch</p>
            <p class="summary-value">{{ profile?.branch || '—' }}</p>
          </div>
          <div class="summary-fact">
            <p class="summary-label">Year</p>
            <p class="summary-value">{{ profile?.year || '—' }}</p>
          </div>
          <div class="summary-fact">
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
              <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="field" required />
            </label>
            <label class="field-group">
              <span class="field-label">Resume URL</span>
              <input v-model="form.resume_url" type="url" class="field" placeholder="https://…" />
            </label>
          </div>

          <div class="form-footer">
            <p v-if="profileMessage" class="status-message" :class="profileMessageType" role="alert">{{ profileMessage }}</p>
            <button class="btn-action" type="submit" :disabled="savingProfile">
              <span v-if="savingProfile" class="btn-spinner" aria-hidden="true"></span>
              {{ savingProfile ? 'Saving…' : 'Save profile' }}
            </button>
          </div>
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
            <div class="summary-pill" :class="{ 'summary-pill--ready': profile?.name }">
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

          <div v-if="!availableDrives.length" class="empty-state">
            <p class="empty-state-title">No available drives right now</p>
            <p class="empty-state-sub">Check back soon — new opportunities are posted regularly.</p>
          </div>
          <div v-else class="list-stack">
            <div v-for="drive in availableDrives" :key="drive.id" class="list-item">
              <div class="list-item-info">
                <h4>{{ drive.title }}</h4>
                <div class="meta-row">
                  <span><strong>Company:</strong> {{ drive.company_name }}</span>
                  <span><strong>Deadline:</strong> {{ drive.deadline }}</span>
                </div>
              </div>
              <button
                class="btn-action"
                @click="apply(drive.id)"
                :disabled="applyingId === drive.id"
              >
                <span v-if="applyingId === drive.id" class="btn-spinner" aria-hidden="true"></span>
                {{ applyingId === drive.id ? 'Applying…' : 'Apply' }}
              </button>
            </div>
          </div>
        </section>

        <section v-if="alreadyAppliedDrives.length" class="panel-card">
          <div class="panel-head">
            <h3>Already Applied</h3>
            <p>These drives have already been applied for and are tracked under your application history.</p>
          </div>
          <div class="list-stack">
            <div v-for="drive in alreadyAppliedDrives" :key="drive.id" class="list-item applied-item">
              <div class="list-item-info">
                <h4>{{ drive.title }}</h4>
                <div class="meta-row">
                  <span><strong>Company:</strong> {{ drive.company_name }}</span>
                  <span><strong>Deadline:</strong> {{ drive.deadline }}</span>
                </div>
              </div>
              <span class="pill pill-applied">Applied</span>
            </div>
          </div>
        </section>

        <section class="panel-card">
          <div class="panel-head panel-head-with-actions">
            <div>
              <h3>Applications & Placement History</h3>
              <p>Every submission you make is tracked here with its latest status.</p>
            </div>
            <div class="panel-head-actions">
              <button class="btn-secondary btn-small" type="button" @click="exportApplications" :disabled="exporting">
                {{ exporting ? 'Exporting…' : 'Export as CSV' }}
              </button>
              <button class="btn-secondary btn-small" type="button" @click="downloadApplications" :disabled="downloadLoading">
                {{ downloadLoading ? 'Downloading…' : 'Download latest CSV' }}
              </button>
            </div>
          </div>

          <div v-if="!applications.length" class="empty-state">
            <p class="empty-state-title">No applications yet</p>
            <p class="empty-state-sub">Apply to an approved drive above to get started.</p>
          </div>
          <div v-else class="list-stack">
            <div v-for="application in applications" :key="application.id" class="list-item application-item">
              <div class="list-item-info">
                <div class="application-item-head">
                  <h4>{{ application.drive_title }}</h4>
                  <span class="status-badge" :class="statusBadgeClass(application.status)">{{ application.status }}</span>
                </div>
                <div class="meta-row">
                  <span><strong>Company:</strong> {{ application.company_name }}</span>
                  <span><strong>Applied on:</strong> {{ displayDateTime(application.application_date) }}</span>
                </div>

                <div v-if="application.interview" class="interview-card">
                  <div class="interview-card-head">
                    <span class="interview-label">Interview</span>
                    <span class="status-badge" :class="statusBadgeClass(application.interview.status)">{{ application.interview.status || 'Pending' }}</span>
                  </div>
                  <p v-if="application.interview.proposed_slots?.length" class="interview-line">
                    <strong>Company slots:</strong> {{ application.interview.proposed_slots.join(' • ') }}
                  </p>
                  <p v-if="application.interview.selected_slot" class="interview-line">
                    <strong>Selected slot:</strong> {{ displayDateTime(application.interview.selected_slot) }}
                  </p>
                  <p v-if="application.interview.notes" class="interview-line">
                    <strong>Notes:</strong> {{ application.interview.notes }}
                  </p>

                  <div class="interview-actions">
                    <template v-if="application.interview.proposed_slots?.length && application.interview.status !== 'Confirmed'">
                      <select v-model="studentSelectedSlot[application.id]" class="field field-sm" aria-label="Choose an interview slot">
                        <option value="">Choose a slot</option>
                        <option v-for="slot in application.interview.proposed_slots" :key="slot" :value="slot">{{ slot }}</option>
                      </select>
                      <button class="btn-action btn-small" type="button" @click="confirmInterview(application.id)">Confirm</button>
                      <button class="btn-secondary btn-small" type="button" @click="requestReschedule(application.id)">Request reschedule</button>
                    </template>
                    <template v-else-if="application.interview.status === 'Confirmed'">
                      <template v-if="!studentRescheduleOpen[application.id]">
                        <button class="btn-secondary btn-small" type="button" @click="toggleReschedule(application.id)">Change slot</button>
                      </template>
                      <template v-else>
                        <button class="btn-action btn-small" type="button" @click="submitChangeSlot(application.id)">Submit change</button>
                        <button class="btn-secondary btn-small" type="button" @click="toggleReschedule(application.id)">Cancel</button>
                      </template>
                    </template>
                  </div>

                  <label class="field-group" v-if="(application.interview.status !== 'Confirmed') || studentRescheduleOpen[application.id]">
                    <span class="field-label">If unavailable, propose alternate slot(s)</span>
                    <textarea v-model="studentProposedSlots[application.id]" class="field field-area" rows="3" placeholder="Enter preferred slots, one per line"></textarea>
                  </label>
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
      appliedDrives: [],
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
      studentRescheduleOpen: {},
      exporting: false,
      downloadLoading: false
    };
  },
  computed: {
    isProfileView() {
      return this.$route.path === "/student/profile";
    },
    availableDrives() {
      return this.drives;
    },
    alreadyAppliedDrives() {
      return this.appliedDrives;
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
        this.drives = drivesRes.data.available_drives || [];
        this.appliedDrives = drivesRes.data.applied_drives || [];
        this.applications = applicationsRes.data || [];
        this.appliedIds = Array.from(
          new Set(
            this.applications
              .map((application) => application.drive_id)
              .filter((id) => id !== null && id !== undefined)
          )
        );
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
    statusBadgeClass(status) {
      const key = (status || "").toLowerCase();
      if (key.includes("pending")) return "status--pending";
      if (key.includes("shortlist")) return "status--shortlisted";
      if (key.includes("interview")) return "status--interview";
      if (key.includes("confirm")) return "status--confirmed";
      if (key.includes("select")) return "status--selected";
      if (key.includes("reject")) return "status--rejected";
      return "";
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
        const message = error.response?.data?.message;
        if (error.response?.status === 400 && message?.includes("Already applied")) {
          this.profileMessage = "Already applied to this drive.";
          this.profileMessageType = "success";
          await this.loadData();
        } else {
          this.profileMessage = message || "Couldn't apply right now.";
          this.profileMessageType = "error";
        }
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
    },
    async exportApplications() {
      this.exporting = true;
      this.profileMessage = "";
      try {
        const response = await api.post("/student/export-applications");
        this.profileMessage = response.data.message || "Export job queued.";
        this.profileMessageType = "success";
      } catch (error) {
        this.profileMessage = error.response?.data?.message || "Could not queue export.";
        this.profileMessageType = "error";
      } finally {
        this.exporting = false;
      }
    },
    async downloadApplications() {
      this.downloadLoading = true;
      this.profileMessage = "";
      try {
        const response = await api.get("/student/download-applications", {
          responseType: "blob"
        });
        const url = window.URL.createObjectURL(new Blob([response.data], { type: response.headers["content-type"] || "text/csv" }));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "application_history.csv");
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        this.profileMessage = "Download started.";
        this.profileMessageType = "success";
      } catch (error) {
        this.profileMessage = error.response?.data?.message || "Unable to download export file.";
        this.profileMessageType = "error";
      } finally {
        this.downloadLoading = false;
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
  max-width: 920px;
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
  margin: 0 0 0.5rem;
  letter-spacing: -0.01em;
  line-height: 1.15;
}

.sub {
  margin: 0;
  color: rgba(239, 237, 247, 0.62);
  font-size: 0.95rem;
  max-width: 56ch;
  line-height: 1.5;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
}

.note-spinner {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 3px solid rgba(20, 19, 43, 0.14);
  border-top-color: var(--accent);
  animation: spin 0.8s linear infinite;
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
  padding: 1.6rem 1.75rem;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
}

.panel-head {
  margin-bottom: 1.4rem;
}

.panel-head h3 {
  margin: 0 0 0.35rem;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.2rem;
  letter-spacing: -0.01em;
}

.panel-head p {
  margin: 0;
  color: rgba(20, 19, 43, 0.65);
  font-size: 0.92rem;
  line-height: 1.5;
  max-width: 60ch;
}

.panel-head-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.panel-head-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.overview-card {
  /* background: linear-gradient(135deg, rgba(232, 229, 229, 0.14), rgba(236, 241, 238, 0.16)); */
  border: 1px solid rgba(255, 107, 74, 0.22);
}

.profile-panel {
  background: linear-gradient(135deg, rgba(46, 196, 182, 0.16), rgba(255, 255, 255, 0.98));
  border: 1px solid rgba(46, 196, 182, 0.22);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.9rem;
}

.summary-pill {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1rem 1.1rem;
  border-radius: 12px;
  background: rgba(20, 19, 43, 0.06);
}

.summary-pill--ready strong {
  color: #17766d;
}

.summary-pill-label {
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(20, 19, 43, 0.6);
}

.summary-pill strong {
  font-size: 1.15rem;
  color: var(--ink);
}

.profile-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.8rem;
  margin-bottom: 1.4rem;
}

.summary-fact {
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: rgba(20, 19, 43, 0.05);
}

.summary-label {
  margin: 0 0 0.3rem;
  font-size: 0.74rem;
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
  gap: 1.1rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(20, 19, 43, 0.7);
}

.field {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1.5px solid rgba(20, 19, 43, 0.14);
  border-radius: 8px;
  font-family: "Inter", sans-serif;
  font-size: 0.92rem;
  background: #fff;
  color: var(--ink);
  box-sizing: border-box;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.field:hover:not(:disabled) {
  border-color: rgba(20, 19, 43, 0.24);
}

.field:focus,
.field:focus-visible {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(255, 107, 74, 0.16);
}

.field:disabled {
  background: rgba(20, 19, 43, 0.06);
  color: rgba(20, 19, 43, 0.6);
  cursor: not-allowed;
}

.field-area {
  resize: vertical;
  line-height: 1.5;
}

.field-sm {
  min-width: 190px;
  max-width: 260px;
}

.form-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
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
  padding: 0.7rem 1.1rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 0.9rem;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.btn-action:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(255, 107, 74, 0.28);
}

.btn-action:active:not(:disabled) {
  transform: translateY(0);
}

.btn-action:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  animation: spin 0.7s linear infinite;
}

.btn-secondary {
  border: 1.5px solid rgba(20, 19, 43, 0.16);
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 0.88rem;
  background: transparent;
  color: var(--ink);
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(20, 19, 43, 0.06);
  border-color: rgba(20, 19, 43, 0.28);
}

.btn-secondary:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-small {
  padding: 0.5rem 0.85rem;
  font-size: 0.82rem;
}

.list-stack {
  display: grid;
  gap: 0.85rem;
}

.list-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.05rem 1.15rem;
  border-radius: 12px;
  background: rgba(20, 19, 43, 0.04);
  transition: box-shadow 0.15s ease;
}

.list-item:hover {
  box-shadow: 0 6px 16px rgba(20, 19, 43, 0.08);
}

.list-item-info {
  flex: 1;
  min-width: 0;
}

.list-item h4 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  font-size: 0.88rem;
  color: rgba(20, 19, 43, 0.68);
}

.applied-item {
  background: rgba(20, 19, 43, 0.025);
}

.applied-item h4 {
  color: rgba(20, 19, 43, 0.75);
}

.pill {
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}

.pill-applied {
  background: rgba(46, 196, 182, 0.16);
  color: #17766d;
}

.application-item {
  align-items: stretch;
}

.application-item-head {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.application-item-head h4 {
  margin: 0;
}

.status-badge {
  padding: 0.32rem 0.65rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
  white-space: nowrap;
  background: rgba(46, 196, 182, 0.16);
  color: #17766d;
}

.status--pending {
  background: rgba(255, 200, 87, 0.22);
  color: #8a6600;
}

.status--shortlisted {
  background: rgba(46, 196, 182, 0.16);
  color: #17766d;
}

.status--interview {
  background: rgba(255, 107, 74, 0.14);
  color: #b8391c;
}

.status--confirmed {
  background: rgba(46, 196, 182, 0.22);
  color: #135e57;
}

.status--selected {
  background: rgba(23, 118, 109, 0.9);
  color: #fff;
}

.status--rejected {
  background: rgba(184, 57, 28, 0.12);
  color: #b8391c;
}

.interview-card {
  margin-top: 0.9rem;
  padding: 1rem 1.1rem;
  background: #fff;
  border: 1px solid rgba(20, 19, 43, 0.08);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.interview-card-head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.interview-label {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(20, 19, 43, 0.55);
}

.interview-line {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(20, 19, 43, 0.75);
}

.interview-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
  margin-top: 0.2rem;
}

.empty-state {
  padding: 1.6rem 1.2rem;
  border-radius: 10px;
  background: rgba(20, 19, 43, 0.03);
  border: 1px dashed rgba(20, 19, 43, 0.14);
  color: rgba(20, 19, 43, 0.7);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.empty-state-title {
  margin: 0;
  font-weight: 600;
  color: var(--ink);
}

.empty-state-sub {
  margin: 0;
  font-size: 0.88rem;
  color: rgba(20, 19, 43, 0.6);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 720px) {
  .board {
    padding: 2.25rem 1.1rem 3rem;
  }

  .panel-card {
    padding: 1.25rem 1.1rem;
  }

  .list-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .panel-head-with-actions {
    flex-direction: column;
  }

  .panel-head-actions {
    width: 100%;
  }

  .panel-head-actions .btn-secondary {
    flex: 1;
  }
}
</style>