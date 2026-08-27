<template>
  <aside class="sidebar" :class="{ open: isOpen, 'is-collapsed': collapsed }">
    <div class="sidebar-brand">
      <div class="brand-text">
        <h1 class="brand-name">{{ t('nav.companyName') }}</h1>
        <span class="subtitle brand-sub">{{ t('nav.subtitle') }}</span>
      </div>

      <button
        type="button"
        class="rail-toggle"
        :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        :aria-expanded="!collapsed"
        @click="$emit('toggle-collapsed')"
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
          <path :d="collapsed ? 'M9 18l6-6-6-6' : 'M15 18l-6-6 6-6'" />
        </svg>
      </button>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.primary')">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
        :aria-current="$route.path === item.path ? 'page' : undefined"
        :title="collapsed ? t(item.labelKey) : null"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path :d="item.icon" />
        </svg>
        <span class="nav-label">{{ t(item.labelKey) }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

// 24x24 stroke paths. Kept as data (not markup) so every nav row renders an
// identical <svg> shell and inherits hover/active color via currentColor.
const ICONS = {
  dashboard: 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
  inventory: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
  orders: 'M9 2h6a2 2 0 012 2v16a2 2 0 01-2 2H9a2 2 0 01-2-2V4a2 2 0 012-2zM10 7h4M10 11h4M10 15h2',
  demand: 'M3 17l6-6 4 4 8-8M21 7v5M21 7h-5',
  restocking: 'M21 2v6h-6M3 22v-6h6M21 8a9 9 0 00-15-3L3 8M3 16a9 9 0 0015 3l3-3',
  finance: 'M12 2v20M17 6H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6',
  reports: 'M3 21h18M7 21V11M12 21V5M17 21v-7'
}

export default {
  name: 'AppSidebar',
  components: {
    LanguageSwitcher,
    ProfileMenu
  },
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    collapsed: {
      type: Boolean,
      default: false
    }
  },
  emits: ['show-profile-details', 'show-tasks', 'toggle-collapsed'],
  setup() {
    const { t } = useI18n()

    const navItems = [
      { path: '/', labelKey: 'nav.overview', icon: ICONS.dashboard },
      { path: '/inventory', labelKey: 'nav.inventory', icon: ICONS.inventory },
      { path: '/orders', labelKey: 'nav.orders', icon: ICONS.orders },
      { path: '/demand', labelKey: 'nav.demandForecast', icon: ICONS.demand },
      { path: '/restocking', labelKey: 'nav.restocking', icon: ICONS.restocking },
      { path: '/spending', labelKey: 'nav.finance', icon: ICONS.finance },
      { path: '/reports', labelKey: 'nav.reports', icon: ICONS.reports }
    ]

    return {
      t,
      navItems
    }
  }
}
</script>

<style scoped>
/* The rail is the machine chassis: dark ground, hairline rules, and amber
   reserved for exactly one job — marking the active route. Everything to
   the right of this border is paper-white work area. */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--chassis);
  border-right: 1px solid var(--chassis-rule);
  /* Was overflow-y: auto. Per spec, overflow-y:auto with overflow-x:visible
     computes overflow-x to auto too — making the whole rail a clipping box
     on BOTH axes. At 72px that shears off the footer dropdowns, so the
     scroll moves down into .sidebar-nav and the footer stays unclipped. */
  overflow: visible;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--s3);
  /* Pinned so the nav below does not jump when the brand text is pulled
     out of flow on collapse. Matches the expanded content height exactly. */
  min-height: 72px;
  padding: var(--s5) var(--s5) var(--s4);
  border-bottom: 1px solid var(--chassis-rule);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: var(--s1);
  min-width: 0;
}

/* Right-aligned beside the brand text when expanded; centered in the rail
   when collapsed (the brand text is out of flow by then). */
.rail-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  margin-left: auto;
  padding: 0;
  background: transparent;
  border: 1px solid var(--chassis-rule);
  border-radius: var(--r-sm);
  color: var(--chassis-text);
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}

.rail-toggle:hover {
  background: var(--chassis-2);
  color: #FFFFFF;
}

.rail-toggle:focus-visible {
  outline: 2px solid var(--signal);
  outline-offset: 2px;
}

.rail-toggle svg {
  width: 16px;
  height: 16px;
}

.brand-name {
  font-family: var(--font-ui);
  font-size: var(--text-md);
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.01em;
}

/* Set as a machine label, not prose — mono, spaced, uppercase. */
.brand-sub {
  font-family: var(--font-data);
  font-size: 10.5px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--chassis-text);
}

/* The rail's only scroll container. min-height:0 is required — a flex item
   defaults to min-height:auto and would refuse to shrink below its content,
   pushing the footer off-screen instead of scrolling. */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--s4) var(--s3);
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--s3);
  min-height: 44px;
  padding: var(--s2) var(--s3);
  border-radius: var(--r-sm);
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: 500;
  color: var(--chassis-text);
  text-decoration: none;
  transition: background var(--transition), color var(--transition);
}

.nav-item:hover {
  background: var(--chassis-2);
  color: #FFFFFF;
}

/* The one place amber appears: current position on the machine. */
.nav-item.active {
  background: var(--chassis-2);
  color: var(--signal);
  font-weight: 600;
}

/* Flush to the left edge of the item, not inset — it reads as a lit
   indicator on the rail rather than a decorative accent. */
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--signal);
  border-radius: 0;
}

.nav-item:focus-visible {
  outline: 2px solid var(--signal);
  outline-offset: -2px;
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--s2);
  padding: var(--s4) var(--s3);
  border-top: 1px solid var(--chassis-rule);
}

/* The footer sits at the bottom of a scrolling rail, so the language and
   profile dropdowns have to open upward and stay inside the 260px rail —
   their default downward/280px-wide placement would be clipped away. */
.sidebar-footer :deep(.dropdown-menu) {
  top: auto;
  bottom: calc(100% + var(--s2));
  left: 0;
  right: 0;
  min-width: 0;
  border-radius: var(--r);
  box-shadow: var(--shadow-pop);
}

.sidebar-footer :deep(.language-button),
.sidebar-footer :deep(.profile-button) {
  width: 100%;
}

.sidebar-footer :deep(.language-label),
.sidebar-footer :deep(.profile-name) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-footer :deep(.chevron) {
  margin-left: auto;
}

/* =========================================================================
   LanguageSwitcher and ProfileMenu ship light-surface triggers (white
   ground, slate text) that are invisible against the chassis. Recolored
   from here rather than by editing those components, since they are also
   usable on light backgrounds elsewhere.

   Selectors are deliberately one class deeper than the components' own
   scoped rules (which are (0,2,0) after the data attribute) so these win
   on specificity and not on source order.
   ========================================================================= */
.sidebar-footer :deep(.language-switcher .language-button),
.sidebar-footer :deep(.profile-menu .profile-button) {
  background: var(--chassis-2);
  border-color: var(--chassis-rule);
  border-radius: var(--r-sm);
  font-family: var(--font-ui);
  color: #FFFFFF;
}

.sidebar-footer :deep(.language-switcher .language-button:hover),
.sidebar-footer :deep(.profile-menu .profile-button:hover) {
  background: #262D37;
  border-color: #3A424E;
}

.sidebar-footer :deep(.language-switcher .language-button:focus-visible),
.sidebar-footer :deep(.profile-menu .profile-button:focus-visible) {
  outline: 2px solid var(--signal);
  outline-offset: 2px;
}

.sidebar-footer :deep(.profile-menu .profile-name) {
  color: #FFFFFF;
}

.sidebar-footer :deep(.language-switcher .globe-icon),
.sidebar-footer :deep(.language-switcher .chevron),
.sidebar-footer :deep(.profile-menu .chevron) {
  color: var(--chassis-text);
}

/* Dropdowns stay light panels — they float over the work area's palette
   and their own scoped styles already read correctly there. */

/* =========================================================================
   Rail mode: icons only, 72px. Fenced inside min-width:1025px so it can
   never compound with the drawer below — down there the panel is a 260px
   overlay that always shows full labels, regardless of the stored
   collapse preference.
   ========================================================================= */
@media (min-width: 1025px) {
  .sidebar.is-collapsed .sidebar-brand {
    justify-content: center;
    padding-left: var(--s3);
    padding-right: var(--s3);
  }

  .sidebar.is-collapsed .rail-toggle {
    margin: 0 auto;
  }

  /* Visually hidden, NOT display:none or visibility:hidden — the labels
     have to stay in the accessibility tree so the links keep announcing
     their destination. Sighted users get the native title tooltip instead;
     a CSS ::after tooltip would be clipped by .sidebar-nav's scroll box. */
  .sidebar.is-collapsed .brand-text,
  .sidebar.is-collapsed .nav-label,
  .sidebar.is-collapsed .sidebar-footer :deep(.language-label),
  .sidebar.is-collapsed .sidebar-footer :deep(.profile-name),
  .sidebar.is-collapsed .sidebar-footer :deep(.chevron) {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
    border: 0;
  }

  .sidebar.is-collapsed .nav-item {
    justify-content: center;
    gap: 0;
    padding: var(--s2);
  }

  /* Held one step larger so the icon carries the 72px column on its own. */
  .sidebar.is-collapsed .nav-icon {
    width: 20px;
    height: 20px;
  }

  .sidebar.is-collapsed .sidebar-footer {
    padding-left: var(--s2);
    padding-right: var(--s2);
  }

  .sidebar.is-collapsed .sidebar-footer :deep(.language-button),
  .sidebar.is-collapsed .sidebar-footer :deep(.profile-button) {
    justify-content: center;
    gap: 0;
    padding-left: 0;
    padding-right: 0;
  }

  /* Released from the rail's width: still anchored to the footer's left
     edge and still opening upward, but now free to run rightward over the
     work area instead of rendering as a 72px sliver. */
  .sidebar.is-collapsed .sidebar-footer :deep(.dropdown-menu) {
    right: auto;
    min-width: 200px;
  }
}

/* Off-canvas drawer below 1024px. Kept here rather than in App.vue's global
   sheet because a scoped rule on .sidebar outranks an unscoped one. */
@media (max-width: 1024px) {
  /* The hamburger in the top bar owns this range. */
  .rail-toggle {
    display: none;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-w);
    z-index: 200;
    transform: translateX(-100%);
    transition: transform var(--transition);
    box-shadow: var(--shadow-pop);
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
</style>
