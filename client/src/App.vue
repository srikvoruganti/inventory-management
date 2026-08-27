<template>
  <div class="app" :class="{ 'is-collapsed': isCollapsed }">
    <AppSidebar
      :is-open="isDrawerOpen"
      :collapsed="isCollapsed"
      @toggle-collapsed="toggleCollapsed"
      @show-profile-details="showProfileDetails = true"
      @show-tasks="showTasks = true"
    />

    <div
      v-if="isDrawerOpen"
      class="sidebar-backdrop"
      @click="closeDrawer"
    ></div>

    <div class="app-main">
      <header class="topbar">
        <button
          type="button"
          class="drawer-toggle"
          :aria-label="isDrawerOpen ? t('nav.closeMenu') : t('nav.openMenu')"
          :aria-expanded="isDrawerOpen"
          @click="toggleDrawer"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <FilterBar />
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import AppSidebar from './components/AppSidebar.vue'
import FilterBar from './components/FilterBar.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'

export default {
  name: 'App',
  components: {
    AppSidebar,
    FilterBar,
    ProfileDetailsModal,
    TasksModal
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])
    const isDrawerOpen = ref(false)

    // =====================================================================
    // Sidebar rail mode. App owns this because App owns the grid — the
    // shell's first column has to change width in lockstep with the rail.
    // =====================================================================
    const COLLAPSE_KEY = 'sidebar-collapsed'
    const RAIL_QUERY = '(max-width: 1280px)'
    const isCollapsed = ref(false)
    // Once the user toggles manually their choice is authoritative and the
    // viewport listener stops overriding it. Tracked outside the ref because
    // it is not rendered — only consulted by the listener.
    let hasStoredPreference = false
    let railMedia = null

    // Every localStorage touch is guarded: access throws outright in
    // private-browsing and blocked-cookie contexts, and an uncaught throw
    // during setup would take the whole app down with it.
    const readStoredCollapsed = () => {
      try {
        return localStorage.getItem(COLLAPSE_KEY)
      } catch (err) {
        return null
      }
    }

    const writeStoredCollapsed = (value) => {
      try {
        localStorage.setItem(COLLAPSE_KEY, value ? 'true' : 'false')
      } catch (err) {
        // Persistence is a nicety; the toggle still works for this session.
      }
    }

    const handleRailChange = (event) => {
      if (hasStoredPreference) return
      isCollapsed.value = event.matches
    }

    const toggleCollapsed = () => {
      isCollapsed.value = !isCollapsed.value
      hasStoredPreference = true
      writeStoredCollapsed(isCollapsed.value)
    }

    const toggleDrawer = () => {
      isDrawerOpen.value = !isDrawerOpen.value
    }

    const closeDrawer = () => {
      isDrawerOpen.value = false
    }

    // Close the drawer whenever navigation occurs — otherwise it stays open
    // covering the destination page and the tap looks like it did nothing.
    watch(() => route.path, closeDrawer)

    const handleKeydown = (event) => {
      if (event.key === 'Escape') {
        closeDrawer()
      }
    }

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(() => {
      loadTasks()
      window.addEventListener('keydown', handleKeydown)

      const stored = readStoredCollapsed()
      railMedia = window.matchMedia(RAIL_QUERY)

      if (stored === 'true' || stored === 'false') {
        hasStoredPreference = true
        isCollapsed.value = stored === 'true'
      } else {
        // No preference on record: rail by default on the narrower desktop
        // range, expanded above it.
        isCollapsed.value = railMedia.matches
      }

      railMedia.addEventListener('change', handleRailChange)
    })

    onUnmounted(() => {
      window.removeEventListener('keydown', handleKeydown)
      if (railMedia) {
        railMedia.removeEventListener('change', handleRailChange)
        railMedia = null
      }
    })

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask,
      isDrawerOpen,
      toggleDrawer,
      closeDrawer,
      isCollapsed,
      toggleCollapsed
    }
  }
}
</script>

<style>
/* =========================================================================
   Visual identity: instrument panel.
   Chassis (dark, amber-signalled) for chrome; paper-white work area for
   content. Every figure is set in the mono face — in an inventory system
   the numbers ARE the content, so they are typeset as data, not prose.

   Content-area colors deliberately stay on the slate/blue scale the views
   hardcode (~450 raw hexes in scoped styles). Amber lives ONLY in the
   sidebar and top bar; introducing it into content would strand the
   views' blues.
   ========================================================================= */
:root {
  /* ── Type ── */
  --font-ui:   'Archivo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-data: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;

  /* ── Chassis: the machine housing. Chrome only, never content. ── */
  --chassis:      #171B21;  /* sidebar ground */
  --chassis-2:    #1F252D;  /* sidebar hover / active bed */
  --chassis-rule: #2C333D;  /* sidebar dividers */
  --chassis-text: #9AA5B1;  /* sidebar idle label */
  --signal:       #E9962E;  /* amber — chrome only */
  --signal-dim:   #7A5216;

  /* ── Work area ── */
  --paper:    #F4F6F8;
  --panel:    #FFFFFF;
  --sunken:   #F1F5F9;
  --ink:      #0F172A;
  --body:     #334155;
  --graphite: #64748B;
  --rule:     #E2E8F0;
  --rule-2:   #CBD5E1;

  /* ── Semantic. Values match the hexes the views hardcode. ── */
  --ok:   #059669;  --ok-bg:   #ECFDF5;  --ok-line:   rgba(5, 150, 105, 0.35);
  --warn: #D97706;  --warn-bg: #FFFBEB;  --warn-line: rgba(217, 119, 6, 0.35);
  --bad:  #DC2626;  --bad-bg:  #FEF2F2;  --bad-line:  rgba(220, 38, 38, 0.35);
  --info: #2563EB;  --info-bg: #EFF6FF;  --info-line: rgba(37, 99, 235, 0.35);

  /* ── Geometry: squared off. Instruments do not have rounded bezels. ── */
  --r:      4px;
  --r-sm:   3px;
  --r-pill: 2px;

  /* Cards get borders, never shadows. This is for dropdowns and modals. */
  --shadow-pop: 0 8px 24px rgba(15, 23, 42, 0.12);

  /* ── Spacing: 4px scale ── */
  --s1:  4px;
  --s2:  8px;
  --s3:  12px;
  --s4:  16px;
  --s5:  20px;
  --s6:  24px;
  --s8:  32px;
  --s10: 40px;

  /* ── Layout ── */
  --sidebar-w:      260px;
  --sidebar-w-rail:  72px;
  --topbar-h:   60px;
  --content-max: 1440px;
  --transition: 150ms ease;

  /* =======================================================================
     Compatibility aliases. FilterBar, AppSidebar and the modals consume the
     older token names; they resolve to the new palette so nothing has to be
     touched twice. New code should use the tokens above.
     ======================================================================= */
  --space-1: var(--s1);
  --space-2: var(--s2);
  --space-3: var(--s3);
  --space-4: var(--s4);
  --space-5: var(--s5);
  --space-6: var(--s6);
  --space-8: var(--s8);
  --space-10: var(--s10);
  --space-12: 48px;

  --bg-app:     var(--paper);
  --bg-surface: var(--panel);
  --bg-sunken:  var(--sunken);
  --bg-hover:   var(--sunken);

  --text-strong:  var(--ink);
  --text-body:    var(--body);
  --text-muted:   var(--graphite);
  --text-subtle:  #94A3B8;
  --text-inverse: #FFFFFF;

  --border:        var(--rule);
  --border-strong: var(--rule-2);

  --accent:        var(--info);
  --accent-hover:  #1D4ED8;
  --accent-soft:   var(--info-bg);
  --accent-border: #BFDBFE;

  --success: var(--ok);   --success-soft: var(--ok-bg);
  --warning: var(--warn); --warning-soft: var(--warn-bg);
  --danger:  var(--bad);  --danger-soft:  var(--bad-bg);
  --info-soft: var(--info-bg);

  --radius-sm:   var(--r-sm);
  --radius-md:   var(--r);
  --radius-lg:   var(--r);
  --radius-full: var(--r-pill);

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: var(--shadow-pop);

  --text-xs:   0.75rem;
  --text-sm:   0.8125rem;
  --text-base: 0.875rem;
  --text-md:   1rem;
  --text-lg:   1.25rem;
  --text-xl:   1.5rem;
  --text-2xl:  1.75rem;

  --font-sans: var(--font-ui);
}

/* ── Base ── */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-ui);
  font-size: var(--text-base);
  background: var(--paper);
  color: var(--body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:focus-visible {
  outline: 2px solid var(--info);
  outline-offset: 2px;
  border-radius: var(--r-sm);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* =========================================================================
   Shell: [sidebar] [main]. Grid — not fixed positioning plus a margin —
   so content can never slide under the rail at odd viewport widths.
   ========================================================================= */
.app {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
  transition: grid-template-columns var(--transition);
}

/* Third layout state: icons-only rail. The sidebar's own scoped styles
   strip the labels; all this column has to do is narrow to match. */
.app.is-collapsed {
  grid-template-columns: var(--sidebar-w-rail) 1fr;
}

@media (prefers-reduced-motion: reduce) {
  .app {
    transition: none;
  }
}

.app-main {
  display: flex;
  flex-direction: column;
  /* Required: without it a wide table refuses to shrink and forces the
     whole page into horizontal scroll instead of scrolling internally. */
  min-width: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: var(--s4);
  min-height: var(--topbar-h);
  padding: var(--s2) var(--s6);
  background: var(--panel);
  border-bottom: 1px solid var(--rule);
}

.drawer-toggle {
  /* Shown only by the ≤1024px rule below, where the rail is a drawer. */
  display: none;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  padding: var(--s2);
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: var(--r);
  color: var(--ink);
  cursor: pointer;
  transition: background var(--transition), border-color var(--transition);
}

.drawer-toggle:hover {
  background: var(--sunken);
  border-color: var(--rule-2);
}

.drawer-toggle svg {
  width: 20px;
  height: 20px;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  padding: var(--s6);
}

/* ── Secondary/muted text, used in the brand block and inside views ── */
.subtitle {
  font-family: var(--font-ui);
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--graphite);
}

/* ── Page header ── */
.page-header {
  margin-bottom: var(--s6);
}

.page-header h2 {
  font-family: var(--font-ui);
  font-size: 28px;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
  margin-bottom: var(--s1);
}

.page-header p {
  font-family: var(--font-ui);
  color: var(--graphite);
  font-size: var(--text-base);
}

/* =========================================================================
   Stat tiles — instrument faces. Flat panel, hairline bezel, no shadow,
   and a tick-mark scale ruled along the lower edge.
   ========================================================================= */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--s4);
  margin-bottom: var(--s6);
}

.stat-card {
  position: relative;
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: var(--r);
  padding: var(--s5);
  /* Room beneath the figure for the tick rule drawn by ::after. */
  padding-bottom: calc(var(--s5) + 14px);
  transition: border-color var(--transition);
}

/* The scale. Kept in --rule-2 rather than amber — the boldness budget is
   spent on the chassis and the mono figures, not here. */
.stat-card::after {
  content: '';
  position: absolute;
  left: var(--s5);
  right: var(--s5);
  bottom: 12px;
  height: 6px;
  background: repeating-linear-gradient(90deg, var(--rule-2) 0 1px, transparent 1px 7px);
  border-bottom: 1px solid var(--rule);
}

.stat-card:hover {
  border-color: var(--rule-2);
}

.stat-label {
  display: block;
  font-family: var(--font-ui);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--graphite);
  margin-bottom: var(--s2);
}

.stat-value {
  font-family: var(--font-data);
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
  font-variant-numeric: tabular-nums;
}

.stat-card.success .stat-value { color: var(--ok); }
.stat-card.warning .stat-value { color: var(--warn); }
.stat-card.danger  .stat-value { color: var(--bad); }
.stat-card.info    .stat-value { color: var(--info); }

/* ── Cards ── */
.card {
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: var(--r);
  padding: var(--s6);
  margin-bottom: var(--s6);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s4);
  margin-bottom: var(--s5);
}

.card-title {
  font-family: var(--font-ui);
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
}

/* ── Tables. Wide tables scroll inside their container, never the page. ── */
.table-container {
  overflow-x: auto;
  border: 1px solid var(--rule);
  border-radius: var(--r);
  background: var(--panel);
}

/* Every view nests its table inside a card; the card already supplies the
   frame, so drop the container's own to avoid a doubled border. */
.card .table-container {
  border: none;
  border-radius: 0;
  background: transparent;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--sunken);
}

th {
  text-align: left;
  padding: var(--s3) var(--s4);
  font-family: var(--font-ui);
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--graphite);
  background: var(--sunken);
  border-bottom: 1px solid var(--rule);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

/* Figures are the content of this app, so every cell is set as data. */
td {
  padding: var(--s3) var(--s4);
  font-family: var(--font-data);
  font-size: 13px;
  color: var(--body);
  border-bottom: 1px solid var(--rule);
  font-variant-numeric: tabular-nums;
}

tbody tr:last-child td {
  border-bottom: none;
}

tbody tr {
  transition: background var(--transition);
}

tbody tr:hover {
  background: var(--sunken);
}

/* =========================================================================
   Badges — inspection tags. Squared, mono, uppercase, hairline outline in
   the semantic hue over its soft ground.
   ========================================================================= */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 7px;
  border: 1px solid transparent;
  border-radius: var(--r-pill);
  font-family: var(--font-data);
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  line-height: 1.5;
  font-variant-numeric: tabular-nums;
}

.badge.success,   .badge.increasing {
  background: var(--ok-bg);   color: var(--ok);   border-color: var(--ok-line);
}
.badge.warning,   .badge.medium     {
  background: var(--warn-bg); color: var(--warn); border-color: var(--warn-line);
}
.badge.danger,    .badge.high,
.badge.decreasing                   {
  background: var(--bad-bg);  color: var(--bad);  border-color: var(--bad-line);
}
.badge.info,      .badge.stable,
.badge.low                          {
  background: var(--info-bg); color: var(--info); border-color: var(--info-line);
}

/* ── States ── */
.loading, .error {
  padding: var(--s10);
  text-align: center;
  font-family: var(--font-ui);
  color: var(--graphite);
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: var(--r);
}

.error {
  color: var(--bad);
  border-color: var(--bad-line);
  background: var(--bad-bg);
}

/* =========================================================================
   Responsive: one breakpoint. Below it the rail becomes an off-canvas
   drawer, opened by the toggle that lives in the top bar.
   ========================================================================= */
@media (max-width: 1024px) {
  .app,
  /* Rail mode must not compound with the drawer. A stored collapse
     preference keeps .is-collapsed on the shell down here, and (0,2,0)
     would otherwise outrank the single-column rule below regardless of
     which media query it sits in. */
  .app.is-collapsed {
    grid-template-columns: 1fr;
  }

  /* The drawer rules for .sidebar itself live in AppSidebar.vue — a scoped
     rule there outranks anything this global sheet says about that class. */

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    z-index: 150;
    background: rgba(15, 23, 42, 0.5);
  }

  .drawer-toggle {
    display: inline-flex;
  }

  .main-content {
    padding: var(--s4);
  }
}

@media (min-width: 1025px) {
  .drawer-toggle {
    display: none;
  }

  .sidebar-backdrop {
    display: none;
  }
}
</style>
