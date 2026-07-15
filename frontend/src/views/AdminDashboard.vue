<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Admin Dashboard</h2>
      <p class="sub">Live counts, pinned up like it's results day.</p>
    </header>

    <div class="pin-row">
      <button
        type="button"
        class="pin-card"
        v-for="(item, i) in cards"
        :key="item.title"
        :style="{ '--tilt': tilts[i] + 'deg', '--accent': item.color }"
        @click="goToSection(item.section)"
      >
        <span class="pin-dot"></span>
        <div class="pin-icon" v-html="item.icon"></div>
        <p class="pin-label">{{ item.title }}</p>
        <p class="pin-value">
          <span v-if="loading">···</span>
          <span v-else>{{ item.value }}</span>
        </p>
      </button>
    </div>

    <section class="panel">
      <div v-if="activeSection === 'companies'">
        <div class="panel-head mt-2">
          <div class="section-title-row">
            <div>
              <h3>Company Registry</h3>
              <p>Track every company at a glance and review their approval status.</p>
            </div>
          </div>
        </div>

        <div v-if="loadingCompanies" class="muted">Loading companies…</div>
        <div v-else class="company-dashboard">
          <div class="summary-grid sticky-shell">
            <button
              class="summary-card pending"
              :class="{ active: activeCompanyTab === 'pending' }"
              @click="activeCompanyTab = 'pending'"
            >
              <p class="summary-label">Pending</p>
              <p class="summary-value">{{ pendingCompanies.length }}</p>
            </button>
            <button
              class="summary-card approved"
              :class="{ active: activeCompanyTab === 'approved' }"
              @click="activeCompanyTab = 'approved'"
            >
              <p class="summary-label">Approved</p>
              <p class="summary-value">{{ approvedCompanies.length }}</p>
            </button>
            <button
              class="summary-card rejected"
              :class="{ active: activeCompanyTab === 'rejected' }"
              @click="activeCompanyTab = 'rejected'"
            >
              <p class="summary-label">Rejected</p>
              <p class="summary-value">{{ rejectedCompanies.length }}</p>
            </button>
          </div>

          <div v-if="activeCompanyTab === 'pending'" class="status-group pending content-shell">
            <div class="group-head">
              <h4>Pending Companies</h4>
              <span class="group-badge">{{ pendingCompanies.length }}</span>
            </div>

            <div v-if="!pendingCompanies.length" class="empty-state">No pending companies right now.</div>
            <div v-else class="company-list">
              <div v-for="company in pendingCompanies" :key="company.id" class="company-card pending">
                <div>
                  <h4>{{ company.company_name }}</h4>
                  <p><strong>Contact:</strong> {{ company.hr_contact }}</p>
                  <p><strong>Email:</strong> {{ company.email }}</p>
                  <p><strong>Website:</strong> {{ company.website || '—' }}</p>
                  <p><strong>Description:</strong> {{ company.description || '—' }}</p>
                  <p><strong>Status:</strong> Pending</p>
                </div>
                <div class="actions">
                  <button class="btn approve" @click="handleAction(company.id, 'approve')">Approve</button>
                  <button class="btn reject" @click="handleAction(company.id, 'reject')">Reject</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activeCompanyTab === 'approved'" class="status-group approved content-shell">
            <div class="group-head">
              <h4>Approved Companies</h4>
              <span class="group-badge">{{ approvedCompanies.length }}</span>
            </div>

            <div v-if="!approvedCompanies.length" class="empty-state">No approved companies right now.</div>
            <div v-else class="company-list">
              <div v-for="company in approvedCompanies" :key="company.id" class="company-card approved">
                <div>
                  <h4>{{ company.company_name }}</h4>
                  <p><strong>Contact:</strong> {{ company.hr_contact }}</p>
                  <p><strong>Email:</strong> {{ company.email }}</p>
                  <p><strong>Website:</strong> {{ company.website || '—' }}</p>
                  <p><strong>Description:</strong> {{ company.description || '—' }}</p>
                  <p><strong>Status:</strong> Approved</p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="status-group rejected content-shell">
            <div class="group-head">
              <h4>Rejected Companies</h4>
              <span class="group-badge">{{ rejectedCompanies.length }}</span>
            </div>

            <div v-if="!rejectedCompanies.length" class="empty-state">No rejected companies right now.</div>
            <div v-else class="company-list">
              <div v-for="company in rejectedCompanies" :key="company.id" class="company-card rejected">
                <div>
                  <h4>{{ company.company_name }}</h4>
                  <p><strong>Contact:</strong> {{ company.hr_contact }}</p>
                  <p><strong>Email:</strong> {{ company.email }}</p>
                  <p><strong>Website:</strong> {{ company.website || '—' }}</p>
                  <p><strong>Description:</strong> {{ company.description || '—' }}</p>
                  <p><strong>Status:</strong> Rejected</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeSection === 'drives'">
        <div class="panel-head mt-2">
          <div class="section-title-row">
            <div>
              <h3>Drive Registry</h3>
              <p>Review every placement drive and switch between its approval states.</p>
            </div>
          </div>
        </div>

        <div v-if="loadingDrives" class="muted">Loading drives…</div>
        <div v-else class="company-dashboard">
          <div class="summary-grid sticky-shell">
            <button
              class="summary-card pending"
              :class="{ active: activeDriveTab === 'pending' }"
              @click="activeDriveTab = 'pending'"
            >
              <p class="summary-label">Pending</p>
              <p class="summary-value">{{ pendingDrives.length }}</p>
            </button>
            <button
              class="summary-card approved"
              :class="{ active: activeDriveTab === 'approved' }"
              @click="activeDriveTab = 'approved'"
            >
              <p class="summary-label">Approved</p>
              <p class="summary-value">{{ approvedDrives.length }}</p>
            </button>
            <button
              class="summary-card rejected"
              :class="{ active: activeDriveTab === 'rejected' }"
              @click="activeDriveTab = 'rejected'"
            >
              <p class="summary-label">Rejected</p>
              <p class="summary-value">{{ rejectedDrives.length }}</p>
            </button>
          </div>

          <div v-if="activeDriveTab === 'pending'" class="status-group pending content-shell">
            <div class="group-head">
              <h4>Pending Drives</h4>
              <span class="group-badge">{{ pendingDrives.length }}</span>
            </div>

            <div v-if="!pendingDrives.length" class="empty-state">No pending drives right now.</div>
            <div v-else class="company-list">
              <div v-for="drive in pendingDrives" :key="drive.id" class="company-card pending">
                <div>
                  <h4>{{ drive.title }}</h4>
                  <p><strong>Company:</strong> {{ drive.company_name }}</p>
                  <p><strong>Status:</strong> Pending</p>
                  <p><strong>Deadline:</strong> {{ drive.deadline }}</p>
                </div>
                <div class="actions">
                  <button class="btn approve" @click="handleDriveAction(drive.id, 'approve')">Approve</button>
                  <button class="btn reject" @click="handleDriveAction(drive.id, 'reject')">Reject</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activeDriveTab === 'approved'" class="status-group approved content-shell">
            <div class="group-head">
              <h4>Approved Drives</h4>
              <span class="group-badge">{{ approvedDrives.length }}</span>
            </div>

            <div v-if="!approvedDrives.length" class="empty-state">No approved drives right now.</div>
            <div v-else class="company-list">
              <div v-for="drive in approvedDrives" :key="drive.id" class="company-card approved">
                <div>
                  <h4>{{ drive.title }}</h4>
                  <p><strong>Company:</strong> {{ drive.company_name }}</p>
                  <p><strong>Status:</strong> Approved</p>
                  <p><strong>Deadline:</strong> {{ drive.deadline }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="status-group rejected content-shell">
            <div class="group-head">
              <h4>Rejected Drives</h4>
              <span class="group-badge">{{ rejectedDrives.length }}</span>
            </div>

            <div v-if="!rejectedDrives.length" class="empty-state">No rejected drives right now.</div>
            <div v-else class="company-list">
              <div v-for="drive in rejectedDrives" :key="drive.id" class="company-card rejected">
                <div>
                  <h4>{{ drive.title }}</h4>
                  <p><strong>Company:</strong> {{ drive.company_name }}</p>
                  <p><strong>Status:</strong> Rejected</p>
                  <p><strong>Deadline:</strong> {{ drive.deadline }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="panel-head mt-2">
          <div class="section-title-row center">
            <div class="text-center">
              <h3>Student List</h3>
              <p>Manage every student account and block or unblock access.</p>
            </div>
          </div>
        </div>

        <div v-if="loadingStudents" class="muted">Loading students…</div>
        <div v-else class="company-dashboard">
          <div class="summary-grid sticky-shell">
            <button
              class="summary-card pending"
              :class="{ active: activeStudentTab === 'all' }"
              @click="activeStudentTab = 'all'"
            >
              <p class="summary-label">All Students</p>
              <p class="summary-value">{{ students.length }}</p>
            </button>
            <button
              class="summary-card rejected"
              :class="{ active: activeStudentTab === 'blocked' }"
              @click="activeStudentTab = 'blocked'"
            >
              <p class="summary-label">Blocked</p>
              <p class="summary-value">{{ blockedStudents.length }}</p>
            </button>
          </div>

          <div v-if="activeStudentTab === 'all'" class="status-group pending content-shell">
            <div class="group-head">
              <h4>All Students</h4>
              <span class="group-badge">{{ students.length }}</span>
            </div>

            <div v-if="!students.length" class="empty-state">No students found.</div>
            <div v-else class="company-list">
              <div v-for="student in students" :key="student.id" class="company-card pending">
                <div>
                  <h4>{{ student.name }}</h4>
                  <p><strong>Email:</strong> {{ student.email }}</p>
                  <p><strong>Branch:</strong> {{ student.branch }}</p>
                  <p><strong>Year:</strong> {{ student.year }}</p>
                  <p><strong>CGPA:</strong> {{ student.cgpa }}</p>
                </div>
                <div class="actions">
                  <button class="btn reject" @click="toggleStudentBlacklist(student.id)">
                    {{ student.blacklisted ? 'Unblock' : 'Block' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="status-group rejected content-shell">
            <div class="group-head">
              <h4>Blocked Students</h4>
              <span class="group-badge">{{ blockedStudents.length }}</span>
            </div>

            <div v-if="!blockedStudents.length" class="empty-state">No blocked students right now.</div>
            <div v-else class="company-list">
              <div v-for="student in blockedStudents" :key="student.id" class="company-card rejected">
                <div>
                  <h4>{{ student.name }}</h4>
                  <p><strong>Email:</strong> {{ student.email }}</p>
                  <p><strong>Branch:</strong> {{ student.branch }}</p>
                  <p><strong>Year:</strong> {{ student.year }}</p>
                  <p><strong>CGPA:</strong> {{ student.cgpa }}</p>
                </div>
                <div class="actions">
                  <button class="btn reject" @click="toggleStudentBlacklist(student.id)">
                    Unblock
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      stats: {},
      companies: [],
      drives: [],
      students: [],
      loading: true,
      loadingCompanies: true,
      loadingDrives: true,
      loadingStudents: true,
      searchTerm: "",
      activeSection: "companies",
      activeCompanyTab: "pending",
      activeDriveTab: "pending",
      activeStudentTab: "all",
      tilts: [-3, 2, -1.5]
    };
  },
  computed: {
    pendingCompanies() {
      return this.companies.filter((company) => !company.approved && !company.rejected);
    },
    approvedCompanies() {
      return this.companies.filter((company) => company.approved);
    },
    rejectedCompanies() {
      return this.companies.filter((company) => company.rejected);
    },
    pendingDrives() {
      return this.drives.filter((drive) => (drive.status || "").toLowerCase() === "pending");
    },
    blockedStudents() {
      return this.students.filter((student) => student.blacklisted);
    },
    approvedDrives() {
      return this.drives.filter((drive) => (drive.status || "").toLowerCase() === "approved");
    },
    rejectedDrives() {
      return this.drives.filter((drive) => (drive.status || "").toLowerCase() === "rejected");
    },
    cards() {
      return [
        {
          title: "Total Students",
          section: "students",
          value: this.stats.total_students || 0,
          color: "#FF6B4A",
          icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 8l9-4 9 4-9 4-9-4z"/><path d="M7 10.5V16c0 1.2 2.2 3 5 3s5-1.8 5-3v-5.5"/><path d="M21 8v6"/></svg>`
        },
        {
          title: "Total Companies",
          section: "companies",
          value: this.stats.total_companies || 0,
          color: "#2EC4B6",
          icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="3" width="9" height="18"/><rect x="13" y="8" width="7" height="13"/><path d="M7 7h2M7 11h2M7 15h2"/></svg>`
        },
        {
          title: "Total Placement Drives",
          section: "drives",
          value: this.stats.total_drives || 0,
          color: "#FFC857",
          icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 3v18"/><path d="M6 4h12l-3 4 3 4H6"/></svg>`
        }
      ];
    },
    searchPlaceholder() {
      if (this.activeSection === "drives") return "Search placement drives";
      if (this.activeSection === "students") return "Search students";
      return "Search companies";
    }
  },
  async mounted() {
    await this.loadAdminData();
  },
  methods: {
    goToSection(section) {
      this.activeSection = section;
    },
    async loadAdminData() {
      try {
        const [statsRes, companiesRes, drivesRes, studentsRes] = await Promise.all([
          api.get("/admin/dashboard"),
          api.get("/admin/companies", { params: { search: this.searchTerm } }),
          api.get("/admin/drives", { params: { search: this.searchTerm } }),
          api.get("/admin/students", { params: { search: this.searchTerm } })
        ]);

        this.stats = statsRes.data;
        this.companies = companiesRes.data;
        this.drives = drivesRes.data;
        this.students = studentsRes.data;
      } catch (error) {
        console.error("Failed to load admin data", error);
      } finally {
        this.loading = false;
        this.loadingCompanies = false;
        this.loadingDrives = false;
        this.loadingStudents = false;
      }
    },
    async handleAction(companyId, action) {
      try {
        if (action === "approve") {
          await api.post(`/admin/companies/${companyId}/approve`);
        } else {
          await api.post(`/admin/companies/${companyId}/reject`);
        }
        this.companies = this.companies.filter((company) => company.id !== companyId);
      } catch (error) {
        console.error("Failed to update company status", error);
      }
    },
    async handleDriveAction(driveId, action) {
      try {
        if (action === "approve") {
          await api.post(`/admin/drives/${driveId}/approve`);
        } else {
          await api.post(`/admin/drives/${driveId}/reject`);
        }
        this.drives = this.drives.filter((drive) => drive.id !== driveId);
      } catch (error) {
        console.error("Failed to update drive status", error);
      }
    },
    async toggleStudentBlacklist(userId) {
      try {
        await api.post(`/admin/users/${userId}/toggle_blacklist`);
        this.students = this.students.map((student) =>
          student.id === userId ? { ...student, blacklisted: !student.blacklisted } : student
        );
      } catch (error) {
        console.error("Failed to update student blacklist", error);
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
  --coral: #ff6b4a;
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
  max-width: 640px;
  margin: 0 auto 2.75rem;
  text-align: left;
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
  border: none;
  border-radius: 10px;
  padding: 1.75rem 1.5rem 1.5rem;
  transform: rotate(var(--tilt));
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  cursor: pointer;
  text-align: left;
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
  background: var(--accent);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.35);
}

.pin-icon {
  width: 34px;
  height: 34px;
  color: var(--accent);
  margin-bottom: 0.9rem;
}

.pin-icon svg {
  width: 100%;
  height: 100%;
}

.pin-label {
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 0.35rem;
  color: rgba(20, 19, 43, 0.65);
}

.pin-value {
  font-family: "Space Grotesk", sans-serif;
  font-size: 2.4rem;
  font-weight: 700;
  margin: 0;
  line-height: 1;
}

@media (prefers-reduced-motion: reduce) {
  .pin-card {
    transition: none;
  }
}

/* Admin Controls panel */

.panel {
  max-width: 960px;
  margin: 2.25rem auto 0;
  background: var(--paper);
  color: var(--ink);
  border-radius: 14px;
  padding: 1.75rem 1.75rem 1.5rem;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
}

.panel-head {
  margin-bottom: 1rem;
}

.panel-head h3 {
  margin: 0 0 0.25rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
}

.panel-head p {
  margin: 0;
  color: rgba(20, 19, 43, 0.65);
  font-size: 0.9rem;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-title-row.center {
  justify-content: center;
  text-align: center;
}

.text-center {
  text-align: center;
}

.pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.4rem 0.85rem;
  background: var(--ink);
  color: var(--paper);
  font-size: 0.8rem;
  font-weight: 600;
  font-family: "Space Grotesk", sans-serif;
}

.tab-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1.25rem;
  border-bottom: 1.5px solid rgba(20, 19, 43, 0.1);
  padding-bottom: 1rem;
}

.tab-btn {
  border: 1.5px solid rgba(20, 19, 43, 0.15);
  background: #fff;
  color: var(--ink);
  border-radius: 999px;
  padding: 0.5rem 1.1rem;
  font-family: "Inter", sans-serif;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
}

.tab-btn:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.tab-btn.active {
  background: var(--ink);
  color: var(--paper);
  border-color: var(--ink);
}

.form-control {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border: 1.5px solid rgba(20, 19, 43, 0.15);
  border-radius: 8px;
  font-family: "Inter", sans-serif;
  font-size: 0.92rem;
  background: #fff;
  color: var(--ink);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--coral);
  box-shadow: 0 0 0 3px rgba(255, 107, 74, 0.15);
}

.muted {
  color: rgba(20, 19, 43, 0.6);
  font-size: 0.92rem;
}

.company-dashboard {
  display: grid;
  gap: 1.5rem;
}

.content-shell {
  min-height: 420px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 0.25rem;
  scrollbar-width: thin;
}

.sticky-shell {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--paper);
  padding-bottom: 0.4rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.9rem;
}

.summary-card {
  border-radius: 12px;
  padding: 1rem 1.1rem;
  border: 1.5px solid transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.summary-card.pending {
  background: rgba(255, 200, 87, 0.15);
  border-color: rgba(255, 200, 87, 0.4);
  color: #8a5a00;
}

.summary-card.approved {
  background: rgba(46, 196, 182, 0.12);
  border-color: rgba(46, 196, 182, 0.35);
  color: #17766d;
}

.summary-card.rejected {
  background: rgba(255, 107, 74, 0.12);
  border-color: rgba(255, 107, 74, 0.35);
  color: #b8391c;
}

.summary-card.active {
  box-shadow: 0 8px 18px rgba(20, 19, 43, 0.1);
  transform: translateY(-1px);
}

.summary-label {
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.7rem;
  font-weight: 700;
}

.status-group {
  border-radius: 12px;
  padding: 1.1rem;
  border: 1.5px solid rgba(20, 19, 43, 0.08);
  background: #fff;
}

.group-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.9rem;
}

.group-head h4 {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1rem;
}

.group-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.9rem;
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  background: rgba(20, 19, 43, 0.08);
  font-weight: 700;
  font-size: 0.82rem;
}

.empty-state {
  padding: 0.5rem 0 0.1rem;
  color: rgba(20, 19, 43, 0.55);
  font-size: 0.9rem;
}

.company-list {
  display: grid;
  gap: 0.9rem;
}

.company-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  border: 1.5px solid rgba(20, 19, 43, 0.1);
  border-radius: 10px;
  padding: 1rem 1.1rem;
  background: #fbfaff;
}

.company-card.approved {
  border-color: rgba(46, 196, 182, 0.35);
  background: rgba(46, 196, 182, 0.06);
}

.company-card.rejected {
  border-color: rgba(255, 107, 74, 0.35);
  background: rgba(255, 107, 74, 0.06);
}

.company-card.pending {
  border-color: rgba(255, 200, 87, 0.4);
  background: rgba(255, 200, 87, 0.08);
}

.company-card h4 {
  margin: 0 0 0.4rem;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1rem;
}

.company-card p {
  margin: 0.2rem 0;
  font-size: 0.88rem;
  color: rgba(20, 19, 43, 0.75);
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-shrink: 0;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 0.55rem 1.1rem;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn.approve {
  background: var(--teal);
  color: #fff;
}

.btn.approve:hover {
  box-shadow: 0 8px 16px rgba(46, 196, 182, 0.35);
}

.btn.reject {
  background: var(--coral);
  color: #fff;
}

.btn.reject:hover {
  box-shadow: 0 8px 16px rgba(255, 107, 74, 0.35);
}

@media (max-width: 680px) {
  .company-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .section-title-row {
    align-items: flex-start;
  }
}
</style>