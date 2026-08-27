# Sidebar Layout

Markup, CSS, and icon set for the left navigation rail. Assumes the tokens in [design-tokens.md](design-tokens.md) are already declared.

## Shell structure

Use CSS Grid for the shell. Do **not** use `position: fixed` on the sidebar plus a manual `margin-left` on the content — that pairing is the most common source of content sliding under the sidebar at odd viewport widths.

```
.app                     grid: [sidebar 260px] [main 1fr]
├── AppSidebar           sticky, 100vh, scrolls independently
└── .app-main            flex column, min-width: 0
    ├── .topbar          slim strip: page controls, drawer toggle
    └── .main-content    router-view
```

`min-width: 0` on `.app-main` is required. Without it, a wide table inside a grid child refuses to shrink and pushes the whole page into horizontal scroll.

```css
.app {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
}

.app-main {
  display: flex;
  flex-direction: column;
  min-width: 0;            /* lets wide content scroll internally */
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-height: var(--topbar-h);
  padding: 0 var(--space-6);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  padding: var(--space-6);
}
```

## Sidebar component

```vue
<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <div class="sidebar-brand">
      <span class="brand-name">{{ t('nav.companyName') }}</span>
      <span class="brand-sub">{{ t('nav.subtitle') }}</span>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.primary')">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
        :aria-current="$route.path === item.path ? 'page' : undefined"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="1.5"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path :d="item.icon" />
        </svg>
        <span class="nav-label">{{ t(item.labelKey) }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <!-- language switcher, profile menu -->
    </div>
  </aside>
</template>
```

Key points:

- `v-for` is keyed on `item.path`, never the array index.
- The active expression must match whatever the original top nav used. If it was `$route.path === '/x'`, keep that — switching to `router-link-active` changes behavior on nested routes.
- Labels go through the i18n helper. Every key added here must exist in **all** locale files.

## Sidebar CSS

```css
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-5) var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--border);
}
.brand-name {
  font-size: var(--text-md);
  font-weight: 650;
  color: var(--text-strong);
  letter-spacing: -0.01em;
}
.brand-sub { font-size: var(--text-xs); color: var(--text-muted); }

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 44px;                 /* touch target floor */
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  text-decoration: none;
  font-size: var(--text-base);
  font-weight: 500;
  transition: background var(--transition), color var(--transition);
}
.nav-item:hover { background: var(--bg-hover); color: var(--text-strong); }
.nav-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }

.nav-icon { width: 18px; height: 18px; flex-shrink: 0; }
.nav-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-3);
  border-top: 1px solid var(--border);
}
```

## Icons

Inline SVG only — **never emoji**. Each entry is the `d` attribute for a 24×24 `stroke="currentColor"` path, so icons inherit hover and active colors for free.

```js
const ICONS = {
  // Overview / dashboard — four panels
  dashboard: 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
  // Inventory — stacked boxes
  inventory: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
  // Orders — document with lines
  orders: 'M9 2h6a2 2 0 012 2v16a2 2 0 01-2 2H9a2 2 0 01-2-2V4a2 2 0 012-2zM10 7h4M10 11h4M10 15h2',
  // Demand — trend line
  demand: 'M3 17l6-6 4 4 8-8M21 7v5M21 7h-5',
  // Restocking — refresh arrows
  restocking: 'M21 2v6h-6M3 22v-6h6M21 8a9 9 0 00-15-3L3 8M3 16a9 9 0 0015 3l3-3',
  // Finance / spending — currency
  finance: 'M12 2v20M17 6H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6',
  // Reports — bar chart
  reports: 'M3 21h18M7 21V11M12 21V5M17 21v-7'
}
```

Pick the icon whose shape matches the route's meaning. If a route has no obvious match, use a neutral shape rather than forcing a metaphor.

## Responsive

One breakpoint at 1024px. Below it the sidebar becomes an off-canvas drawer.

The toggle button **must** live in the top bar and be visible whenever the drawer is closed. A drawer with no reachable open control makes the app unnavigable.

### Where each rule goes — this matters

Split the responsive CSS by which stylesheet owns the selector:

| Rules | Stylesheet | Why |
|---|---|---|
| `.sidebar`, `.sidebar.open` | **Scoped**, inside `AppSidebar.vue` | See below |
| `.app`, `.sidebar-backdrop`, `.drawer-toggle` | Global | Owned by the shell, not the sidebar |

`.sidebar` is defined in a scoped component, so Vue compiles it to `.sidebar[data-v-xxxxxx]` — specificity (0,2,0). An unscoped global `.sidebar` is (0,1,0) and **loses**. Put the drawer's `position: fixed` / `transform` rules in the global sheet and the scoped `position: sticky` wins instead: the drawer silently never opens, with a green build and no console error.

Give `.drawer-toggle` a `display: none` default in the global sheet rather than relying on the media queries alone — at exactly 1025px neither `max-width: 1024px` nor a `min-width: 1025px` block may apply as expected across browsers, and an unstyled toggle appears beside a docked sidebar.

```css
/* ── scoped, in AppSidebar.vue ── */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-w);
    z-index: 200;
    transform: translateX(-100%);
    transition: transform var(--transition);
    box-shadow: var(--shadow-md);
  }
  .sidebar.open { transform: translateX(0); }
}

/* ── global, in App.vue ── */
@media (max-width: 1024px) {
  .app { grid-template-columns: 1fr; }

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    z-index: 150;
    background: rgba(15, 23, 42, 0.4);
  }

  .drawer-toggle { display: inline-flex; }
  .main-content { padding: var(--space-4); }
}

@media (min-width: 1025px) {
  .drawer-toggle { display: none; }
  .sidebar-backdrop { display: none; }
}
```

Drawer behavior:

- Close on route change, or the drawer stays open covering the page the user just navigated to.
- Close on backdrop click and on `Escape`.
- The toggle needs an `aria-label` and `:aria-expanded`.

## Icons-only rail (optional third state)

A collapsed rail sits between the expanded sidebar and the drawer: expanded above ~1280px, a ~72px icon rail from 1025–1280px, drawer at ≤1024px. Drive the width from the shell's grid, `.app.is-collapsed { grid-template-columns: var(--sidebar-w-rail) 1fr; }`, and hold the state in the root component since it owns the grid.

Four things break if you don't handle them:

**The sidebar clips on both axes.** `overflow-y: auto` with `overflow-x: visible` computes `overflow-x` to `auto` per spec, so the whole rail is a clipping box. Anything reaching rightward out of a 72px rail — a tooltip, a footer dropdown — is severed. Move the scroll inward:

```css
.sidebar     { overflow: visible; }
.sidebar-nav { flex: 1; min-height: 0; overflow-y: auto; }
```

`min-height: 0` is load-bearing. A flex item defaults to `min-height: auto` and with `flex: 1` refuses to shrink below its content, so the footer gets pushed off-screen instead of the nav scrolling. This also moves the footer outside the scroll box, which is what lets its dropdowns escape the rail.

**Hidden labels must stay in the accessibility tree.** `display: none` or `visibility: hidden` on the label leaves screen reader users with a column of unlabeled icons. Visually hide it instead, and give sighted users a native `title` only while collapsed:

```css
.is-collapsed .nav-label {
  position: absolute; width: 1px; height: 1px;
  margin: -1px; overflow: hidden; clip-path: inset(50%);
  white-space: nowrap; border: 0;
}
```

Use the native `title` rather than a CSS `::after` tooltip — a CSS tooltip is clipped by the nav's scroll container, and escaping that needs JS positioning that isn't worth the fragility.

**The collapsed class outranks the drawer rule.** `.app.is-collapsed` is (0,2,0) and beats a bare `.app` (0,1,0) *regardless of which media query each sits in*. A stored collapse preference would otherwise keep the rail column width inside the drawer breakpoint. List both selectors in the drawer query:

```css
@media (max-width: 1024px) {
  .app,
  .app.is-collapsed { grid-template-columns: 1fr; }
}
```

Fence the rail-mode styles inside `@media (min-width: 1025px)` for the same reason — a stored preference must never strip labels from the drawer.

**Persisted state can throw.** `localStorage` throws outright in private-browsing and blocked-cookie contexts, and an uncaught throw during setup blanks the app. Wrap every read and write in `try/catch`, returning a sensible default. Follow the media query only until the user toggles manually; after that their choice wins.

```js
// Close the drawer whenever navigation occurs — otherwise it covers the
// destination page on mobile and looks like the tap did nothing.
watch(() => route.path, () => { isOpen.value = false })
```
