<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Company Dashboard</h2>
      <p class="sub">Create drives, review applicants, and manage hiring activity from one place.</p>
    </header>

    <div v-if="loading" class="note">
      <p class="note-title">Pulling your company board…</p>
    </div>

    <div v-else class="dashboard-grid">
      <section v-if="activeSection === 'overview'" class="panel-card overview-card">
        <div class="panel-head">
          <h3>Company Overview</h3>
          <p>Keep your placement pipeline moving with approval status and active hiring activity.</p>
        </div>

        <div class="summary-row">
          <div class="summary-pill">
            <span class="summary-pill-label">Company</span>
            <strong>{{ profile?.company_name || '—' }}</strong>
          </div>
          <div class="summary-pill">
            <span class="summary-pill-label">Drives</span>
            <strong>{{ drives.length }}</strong>
          </div>
          <div class="summary-pill">
            <span class="summary-pill-label">Status</span>
            <strong>{{ profile?.approved ? 'Approved' : 'Pending' }}</strong>
          </div>
        </div>
      </section>

      <section v-else-if="activeSection === 'create'" class="panel-card">
        <div class="panel-head">
          <h3>Create New Drive</h3>
          <p>Post a new placement drive once your company is approved.</p>
        </div>

        <form class="profile-form" @submit.prevent="createDrive">
          <div class="field-row">
            <label class="field-group">
              <span class="field-label">Job Title</span>
              <input class="field" v-model="title" placeholder="Job Title" required />
            </label>
            <label class="field-group">
              <span class="field-label">Deadline</span>
              <input class="field" v-model="deadline" type="date" :min="today" required />
            </label>
          </div>

          <label class="field-group">
            <span class="field-label">Job Description</span>
            <textarea class="field field-area" v-model="description" placeholder="Job Description" required></textarea>
          </label>

          <div class="field-row field-row-3">
            <label class="field-group">
              <span class="field-label">Eligibility Branches</span>
              <input class="field" v-model="branch_eligibility" placeholder="Eligibility Branches" />
            </label>
            <label class="field-group">
              <span class="field-label">Eligibility Years</span>
              <input class="field" v-model="year_eligibility" placeholder="Eligibility Years" />
            </label>
            <label class="field-group">
              <span class="field-label">Minimum CGPA</span>
              <input class="field" v-model="min_cgpa" type="number" step="0.01" placeholder="Minimum CGPA" />
            </label>
          </div>

          <p v-if="message" class="status-message" :class="messageType">{{ message }}</p>
          <button class="btn-post" type="submit" :disabled="submitting">
            {{ submitting ? 'Posting…' : 'Create Drive' }}
          </button>
        </form>
      </section>

      <section v-else-if="activeSection === 'drives'" class="panel-card">
        <div class="panel-head">
          <h3>All Job Drives</h3>
          <p>Review every drive you have posted and the current applicant volume.</p>
        </div>

        <div v-if="!drives.length" class="empty-state">No drives have been posted yet.</div>
        <div v-else class="drive-list">
          <button
            v-for="drive in drives"
            :key="drive.id"
            class="drive-card"
            :class="{ active: selectedDriveId === drive.id }"
            type="button"
            @click="selectDrive(drive.id)"
          >
            <div>
              <h4>{{ drive.title }}</h4>
              <p>Status: {{ drive.status }}</p>
              <p>Applicants: {{ drive.applicants }}</p>
            </div>
            <span class="pill">{{ drive.status }}</span>
          </button>
        </div>
      </section>

      <section v-else class="panel-card">
        <div class="panel-head">
          <h3>Applicants</h3>
          <p>Shortlist, interview, select, or reject applicants from the selected drive.</p>
        </div>

        <div v-if="!selectedDrive" class="empty-state">Select a drive to see the applicants.</div>
        <div v-else>
          <div class="selected-drive-summary">
            <h4>{{ selectedDrive.title }}</h4>
            <p>{{ selectedDrive.status }} • {{ selectedDrive.applicants }} applicants</p>
          </div>

          <div v-if="!selectedDrive.applications.length" class="empty-state">No applications have been received for this drive yet.</div>

          <div v-else>
            <div class="filter-row">
              <label class="field-group field-sm">
                <span class="field-label">Status</span>
                <select class="field" v-model="filters.statusFilter">
                  <option>All</option>
                  <option>Pending</option>
                  <option>Shortlisted</option>
                  <option>Interview Scheduled</option>
                  <option>Confirmed</option>
                  <option>Selected</option>
                  <option>Rejected</option>
                </select>
              </label>
              <label class="field-group field-sm">
                <span class="field-label">Branch</span>
                <input class="field" v-model="filters.branchFilter" placeholder="e.g. CSE" />
              </label>
              <label class="field-group field-sm">
                <span class="field-label">Min CGPA</span>
                <input class="field" v-model="filters.minCgpaFilter" type="number" step="0.01" placeholder="0.00" />
              </label>
              <label class="field-group" style="flex:1">
                <span class="field-label">Search</span>
                <input class="field" v-model="filters.searchQuery" placeholder="Name or email" />
              </label>
              <div style="display:flex;gap:0.6rem;align-items:flex-end">
                <button class="btn-post" type="button" @click="clearFilters">Clear</button>
              </div>
            </div>

            <div class="applicant-list">
              <div v-for="applicant in filteredApplications" :key="applicant.id" class="applicant-card">
                <div class="applicant-main">
                  <h4>{{ applicant.student_name }}</h4>
                  <p>{{ applicant.student_email }}</p>
                  <div class="meta-row">
                    <span>Branch: {{ applicant.branch || '—' }}</span>
                    <span>CGPA: {{ applicant.cgpa || '—' }}</span>
                  </div>
                </div>

                <div class="applicant-actions">
                  <div class="status-line">
                    <span class="status-badge">{{ applicant.status }}</span>
                    <button class="btn-post btn-small" type="button" @click="toggleInterviewPanel(applicant.id)">
                      {{ interviewPanelOpen[applicant.id] ? 'Collapse' : (applicant.interview ? 'Update slots' : 'Schedule interview') }}
                    </button>
                  </div>
                  <div class="interview-summary" v-if="applicant.interview?.selected_slot && !interviewPanelOpen[applicant.id]">
                    <strong>Selected slot:</strong> {{ displayInterviewSlot(applicant.interview.selected_slot) }}
                  </div>
                  <div v-if="interviewPanelOpen[applicant.id]" class="interview-panel">
                    <div class="field-group">
                      <span class="field-label">Proposed slots</span>
                      <div v-for="(slot, idx) in (companySlotInputs[applicant.id] || [])" :key="idx" style="display:flex;gap:0.6rem;align-items:center;margin-bottom:0.5rem">
                        <input v-model="companySlotInputs[applicant.id][idx].date" class="field" type="date" :min="today" style="max-width:180px" />
                        <input v-model="companySlotInputs[applicant.id][idx].time" class="field" type="time" step="300" style="max-width:140px" />
                        <button class="btn-small" type="button" @click="removeCompanySlot(applicant.id, idx)">Remove</button>
                      </div>
                      <div style="display:flex;gap:0.6rem;margin-top:0.6rem">
                        <button class="btn-post" type="button" @click="addCompanySlot(applicant.id)">Add more slot</button>
                        <p class="hint" style="margin:0.25rem 0 0;font-size:0.85rem;color:rgba(20,19,43,0.6)">Use the date & time pickers to add slots; you can add multiple.</p>
                      </div>
                    </div>
                    <div class="field-group">
                      <span class="field-label">Notes</span>
                      <input v-model="companyInterviewNotes[applicant.id]" class="field" placeholder="Add any details" />
                    </div>
                    <button class="btn-post" type="button" @click="saveInterviewSchedule(applicant.id)">
                      {{ applicant.interview ? 'Update slots' : 'Schedule interview' }}
                    </button>
                    <p v-if="applicant.interview?.selected_slot" class="status-message success">Current slot: {{ applicant.interview.selected_slot }}</p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>
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
      title: "",
      description: "",
      deadline: "",
      branch_eligibility: "",
      year_eligibility: "",
      min_cgpa: 0,
      submitting: false,
      loading: true,
      message: "",
      messageType: "success",
      selectedDriveId: null,
      selectedStatuses: {},
      companySlotInputs: {},
      companySelectedSlot: {},
      companyInterviewNotes: {},
      interviewPanelOpen: {},
      filters: {
        statusFilter: 'All',
        branchFilter: '',
        searchQuery: '',
        minCgpaFilter: ''
      }
    };
  },
  computed: {
    activeSection() {
      return this.$route.query.section || "overview";
    },
    selectedDrive() {
      return this.drives.find((drive) => drive.id === this.selectedDriveId) || null;
    },
    today() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    },
    todayDateTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    ,
    // Filtered list derived from selected drive applications
    filteredApplications() {
      const apps = (this.selectedDrive && this.selectedDrive.applications) || [];
      return apps.filter((a) => {
        // status filter
        if (this.filters.statusFilter && this.filters.statusFilter !== 'All') {
          if ((a.status || '').toLowerCase() !== this.filters.statusFilter.toLowerCase()) return false;
        }

        // branch filter
        if (this.filters.branchFilter) {
          const branch = (a.branch || '').toLowerCase();
          if (!branch.includes(this.filters.branchFilter.toLowerCase())) return false;
        }

        // min cgpa filter
        if (this.filters.minCgpaFilter) {
          const min = parseFloat(this.filters.minCgpaFilter) || 0;
          const cgpa = parseFloat(a.cgpa) || 0;
          if (cgpa < min) return false;
        }

        // search query (name or email)
        if (this.filters.searchQuery) {
          const q = this.filters.searchQuery.toLowerCase();
          const name = (a.student_name || '').toLowerCase();
          const email = (a.student_email || '').toLowerCase();
          if (!name.includes(q) && !email.includes(q)) return false;
        }

        return true;
      });
    }
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const response = await api.get("/company/dashboard");
        this.profile = response.data;
        this.drives = (response.data.drives || []).map((drive) => ({ ...drive, applications: [] }));

        await Promise.all(
          this.drives.map(async (drive) => {
            try {
              const applicationsRes = await api.get(`/company/drives/${drive.id}/applications`);
              const applications = applicationsRes.data || [];
              const driveIndex = this.drives.findIndex((item) => item.id === drive.id);
              if (driveIndex >= 0) {
                this.drives[driveIndex].applications = applications;
                applications.forEach((application) => {
                  this.selectedStatuses[application.id] = application.status;
                  const proposed = application.interview?.proposed_slots || [];
                  this.companySlotInputs[application.id] = proposed.length
                    ? proposed.map((s) => {
                        const p = this.parseSelectedSlot(s);
                        return { date: p.date, time: p.time };
                      })
                    : [{ date: "", time: "" }];
                  const slot = this.parseSelectedSlot(application.interview?.selected_slot || "");
                  this.companySelectedSlot[application.id] = slot.raw;
                  this.companyInterviewNotes[application.id] = application.interview?.notes || "";
                  if (this.interviewPanelOpen[application.id] === undefined) {
                    this.interviewPanelOpen[application.id] = false;
                  }
                });
              }
            } catch (error) {
              console.error("Unable to load applications", error);
            }
          })
        );

        if (!this.selectedDriveId && this.drives.length) {
          this.selectedDriveId = this.drives[0].id;
        }

        this.drives = [...this.drives];
      } catch (error) {
        console.error("Unable to load company dashboard", error);
      } finally {
        this.loading = false;
      }
    },
    selectDrive(driveId) {
      this.selectedDriveId = driveId;
    },
    formatDateTimeLocal(value) {
      if (!value) {
        return "";
      }

      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)) {
        return value;
      }

      let normalized = value.trim();
      // Handle missing separator between date and time: e.g. "2026-07-145:30" -> "2026-07-14T5:30"
      const missingSepMatch = normalized.match(/^(\d{4}-\d{2}-\d{2})(\d{1,2}:\d{2})$/);
      if (missingSepMatch) {
        normalized = `${missingSepMatch[1]}T${missingSepMatch[2]}`;
      }
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(normalized)) {
        return normalized.replace(" ", "T");
      }

      const ampmMatch = normalized.match(/^(\d{4}-\d{2}-\d{2}) (\d{1,2}):(\d{2})\s*(AM|PM)$/i);
      if (ampmMatch) {
        let [, datePart, hourPart, minutePart, ampm] = ampmMatch;
        let hour = Number(hourPart);
        if (ampm.toUpperCase() === "PM" && hour < 12) hour += 12;
        if (ampm.toUpperCase() === "AM" && hour === 12) hour = 0;
        return `${datePart}T${String(hour).padStart(2, "0")}:${minutePart}`;
      }

      const parsed = new Date(normalized);
      if (!isNaN(parsed.getTime())) {
        const year = parsed.getFullYear();
        const month = String(parsed.getMonth() + 1).padStart(2, "0");
        const day = String(parsed.getDate()).padStart(2, "0");
        const hours = String(parsed.getHours()).padStart(2, "0");
        const minutes = String(parsed.getMinutes()).padStart(2, "0");
        return `${year}-${month}-${day}T${hours}:${minutes}`;
      }

      return "";
    },
    parseSelectedSlot(value) {
      if (!value) {
        return { raw: "", date: "", time: "" };
      }
      let normalized = value.trim();
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(normalized)) {
        return {
          raw: normalized,
          date: normalized.slice(0, 10),
          time: normalized.slice(11, 16)
        };
      }
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(normalized)) {
        normalized = normalized.replace(" ", "T");
        return {
          raw: normalized,
          date: normalized.slice(0, 10),
          time: normalized.slice(11, 16)
        };
      }
      const parsed = new Date(normalized);
      if (!isNaN(parsed.getTime())) {
        const year = parsed.getFullYear();
        const month = String(parsed.getMonth() + 1).padStart(2, "0");
        const day = String(parsed.getDate()).padStart(2, "0");
        const hours = String(parsed.getHours()).padStart(2, "0");
        const minutes = String(parsed.getMinutes()).padStart(2, "0");
        const formatted = `${year}-${month}-${day}T${hours}:${minutes}`;
        return {
          raw: formatted,
          date: `${year}-${month}-${day}`,
          time: `${hours}:${minutes}`
        };
      }
      return { raw: normalized, date: "", time: "" };
    },
    displayInterviewSlot(value) {
      if (!value) {
        return "";
      }
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)) {
        const parsed = new Date(value);
        return parsed.toLocaleString();
      }
      return value;
    },
    toggleInterviewPanel(applicationId) {
      this.interviewPanelOpen[applicationId] = !this.interviewPanelOpen[applicationId];
    },
    addCompanySlot(applicationId) {
      if (!this.companySlotInputs[applicationId]) this.companySlotInputs[applicationId] = [];
      this.companySlotInputs[applicationId].push({ date: "", time: "" });
    },
    removeCompanySlot(applicationId, index) {
      if (!this.companySlotInputs[applicationId]) return;
      this.companySlotInputs[applicationId].splice(index, 1);
      if (this.companySlotInputs[applicationId].length === 0) this.companySlotInputs[applicationId].push({ date: "", time: "" });
    },
    async createDrive() {
      this.submitting = true;
      this.message = "";
      try {
        await api.post("/company/drives", {
          title: this.title,
          description: this.description,
          application_deadline: this.deadline,
          branch_eligibility: this.branch_eligibility,
          year_eligibility: this.year_eligibility,
          min_cgpa: this.min_cgpa
        });
        this.message = "Placement drive created successfully";
        this.messageType = "success";
        this.title = "";
        this.description = "";
        this.deadline = "";
        this.branch_eligibility = "";
        this.year_eligibility = "";
        this.min_cgpa = 0;
        await this.loadData();
      } catch (error) {
        this.message = error.response?.data?.message || "Unable to create drive right now.";
        this.messageType = "error";
      } finally {
        this.submitting = false;
      }
    },
    clearFilters() {
      this.filters.statusFilter = 'All';
      this.filters.branchFilter = '';
      this.filters.searchQuery = '';
      this.filters.minCgpaFilter = '';
    },
    async updateApplicationStatus(applicationId) {
      try {
        await api.post(`/company/applications/${applicationId}/update`, {
          status: this.selectedStatuses[applicationId]
        });

        const drive = this.drives.find((item) => item.applications.some((app) => app.id === applicationId));
        if (drive) {
          const index = drive.applications.findIndex((app) => app.id === applicationId);
          if (index >= 0) {
            drive.applications[index].status = this.selectedStatuses[applicationId];
            this.drives = [...this.drives];
          }
        }
      } catch (error) {
        console.error("Unable to update application status", error);
      }
    },
    async saveInterviewSchedule(applicationId) {
      try {
        // Collect date+time pairs from slot inputs
        const inputs = this.companySlotInputs[applicationId] || [];
        const rawSlots = inputs
          .map((s) => (s.date && s.time) ? `${s.date}T${s.time}` : "")
          .filter(Boolean);

        const normalized = rawSlots.map((line) => this.formatDateTimeLocal(line)).filter(Boolean);

        if (normalized.length === 0 && rawSlots.length > 0) {
          this.message = "Some proposed slots could not be parsed — please ensure both date and time are set.";
          this.messageType = "error";
          return;
        }

        await api.post(`/company/applications/${applicationId}/schedule`, {
          proposed_slots: normalized,
          notes: this.companyInterviewNotes[applicationId],
          status: "Slots Proposed"
        });
        this.message = "Interview slots saved";
        this.messageType = "success";
        await this.loadData();
        this.interviewPanelOpen[applicationId] = false;
      } catch (error) {
        this.message = error.response?.data?.message || "Unable to save interview slots.";
        this.messageType = "error";
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
  max-width: 960px;
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

.profile-form {
  display: grid;
  gap: 0.8rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
}

.field-row-3 {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
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
  appearance: auto;
  -webkit-appearance: auto;
  -moz-appearance: auto;
  box-sizing: border-box;
}

input[type="date"],
input[type="time"],
input[type="datetime-local"] {
  appearance: auto;
  -webkit-appearance: auto;
  -moz-appearance: auto;
  cursor: pointer;
}

.field-area {
  min-height: 100px;
  resize: vertical;
}

.field-sm {
  min-width: 170px;
}

.filter-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  margin-bottom: 1rem;
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

.btn-post {
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

.btn-post:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(255, 107, 74, 0.24);
}

.btn-post:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.drive-list {
  display: grid;
  gap: 0.8rem;
}

.drive-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  width: 100%;
  border: 1px solid rgba(20, 19, 43, 0.08);
  border-radius: 12px;
  padding: 0.95rem 1rem;
  background: rgba(20, 19, 43, 0.04);
  cursor: pointer;
  text-align: left;
}

.drive-card.active {
  border-color: var(--accent);
  background: rgba(255, 107, 74, 0.1);
}

.drive-card h4 {
  margin: 0 0 0.25rem;
}

.drive-card p {
  margin: 0.2rem 0;
  color: rgba(20, 19, 43, 0.72);
}

.pill {
  padding: 0.4rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  background: rgba(255, 107, 74, 0.12);
  color: var(--accent);
}

.selected-drive-summary {
  margin-bottom: 1rem;
}

.selected-drive-summary h4 {
  margin: 0 0 0.2rem;
}

.selected-drive-summary p {
  margin: 0;
  color: rgba(20, 19, 43, 0.7);
}

.applicant-list {
  display: grid;
  gap: 0.8rem;
}

.applicant-card {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.95rem 1rem;
  border-radius: 12px;
  background: rgba(20, 19, 43, 0.04);
}

.applicant-main h4 {
  margin: 0 0 0.25rem;
}

.applicant-main p {
  margin: 0 0 0.3rem;
  color: rgba(20, 19, 43, 0.72);
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  font-size: 0.88rem;
  color: rgba(20, 19, 43, 0.7);
}

.applicant-actions {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.8rem;
}

.status-line {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  width: 100%;
}

.status-line .status-badge,
.status-line .btn-small {
  margin-right: 0;
}

.interview-summary {
  font-size: 0.92rem;
  color: rgba(20, 19, 43, 0.72);
}

.interview-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.btn-small {
  padding: 0.45rem 0.85rem;
  font-size: 0.8rem;
}

.status-badge {
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  background: rgba(46, 196, 182, 0.16);
  color: #17766d;
  font-size: 0.8rem;
  font-weight: 700;
}

.empty-state {
  padding: 1rem;
  border-radius: 10px;
  background: rgba(20, 19, 43, 0.04);
  color: rgba(20, 19, 43, 0.7);
}

@media (max-width: 760px) {
  .applicant-card,
  .drive-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .applicant-actions {
    align-items: flex-start;
  }
}
</style>
