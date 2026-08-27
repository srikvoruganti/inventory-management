# Design Tokens

The fixed token system for the SaaS redesign. Declare all of it on `:root` in the app's global stylesheet. After this block exists, no component may hardcode a color, spacing value, radius, or shadow.

## Token block

```css
:root {
  /* ── Spacing: 4px grid. Every margin, padding, and gap uses one of these. ── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* ── Surfaces ── */
  --bg-app: #f8fafc;        /* page canvas behind content */
  --bg-surface: #ffffff;    /* cards, sidebar, top bar */
  --bg-sunken: #f1f5f9;     /* table headers, inset areas */
  --bg-hover: #f1f5f9;

  /* ── Text ── */
  --text-strong: #0f172a;   /* headings */
  --text-body: #334155;     /* body copy, table cells */
  --text-muted: #64748b;    /* labels, secondary */
  --text-subtle: #94a3b8;   /* placeholders, disabled */
  --text-inverse: #ffffff;

  /* ── Borders ── */
  --border: #e2e8f0;
  --border-strong: #cbd5e1;

  /* ── Accent ── */
  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --accent-soft: #eff6ff;   /* active nav background */
  --accent-border: #bfdbfe;

  /* ── Semantic. Separate from accent; never used for branding. ── */
  --success: #059669;  --success-soft: #ecfdf5;
  --warning: #d97706;  --warning-soft: #fffbeb;
  --danger:  #dc2626;  --danger-soft:  #fef2f2;
  --info:    #2563eb;  --info-soft:    #eff6ff;

  /* ── Radii ── */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* ── Elevation: one level. Cards use borders, not shadows. ── */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);

  /* ── Type scale ── */
  --text-xs: 0.75rem;    /* 12px - uppercase labels */
  --text-sm: 0.8125rem;  /* 13px - dense table text */
  --text-base: 0.875rem; /* 14px - body default */
  --text-md: 1rem;       /* 16px - card titles */
  --text-lg: 1.25rem;    /* 20px - section headings */
  --text-xl: 1.5rem;     /* 24px - stat values */
  --text-2xl: 1.75rem;   /* 28px - page titles */

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* ── Layout ── */
  --sidebar-w: 260px;
  --topbar-h: 60px;
  --content-max: 1440px;

  --transition: 150ms ease;
}
```

## Base

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  background: var(--bg-app);
  color: var(--text-body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Component classes

These are the shared classes views consume. Restyle them; do not rename or remove them. Names here follow the common convention — match whatever your step-1 inventory actually found.

```css
/* ── Page header ── */
.page-header { margin-bottom: var(--space-6); }
.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 650;
  color: var(--text-strong);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-1);
}
.page-header p { color: var(--text-muted); font-size: var(--text-base); }

/* ── Stat tiles ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}
.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: border-color var(--transition);
}
.stat-card:hover { border-color: var(--border-strong); }
.stat-label {
  display: block;
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}
.stat-value {
  font-size: var(--text-xl);
  font-weight: 650;
  color: var(--text-strong);
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}
.stat-card.success .stat-value { color: var(--success); }
.stat-card.warning .stat-value { color: var(--warning); }
.stat-card.danger  .stat-value { color: var(--danger); }
.stat-card.info    .stat-value { color: var(--info); }

/* ── Cards ── */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.card-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--text-strong);
}

/* ── Tables. Wide tables must scroll inside their container, never the page. ── */
.table-container {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
}
table { width: 100%; border-collapse: collapse; }
thead { background: var(--bg-sunken); }
th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border);
  color: var(--text-body);
  font-size: var(--text-base);
}
tbody tr:last-child td { border-bottom: none; }
tbody tr { transition: background var(--transition); }
tbody tr:hover { background: var(--bg-sunken); }

/* A table container nested in a card would otherwise draw a second frame
   inside one that already has a border, radius, and background. Check whether
   the app nests these before shipping the standalone styling above. */
.card .table-container {
  border: none;
  border-radius: 0;
  background: transparent;
}

/* ── Badges ── */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  line-height: 1.5;
}
.badge.success,   .badge.increasing { background: var(--success-soft); color: var(--success); }
.badge.warning,   .badge.medium     { background: var(--warning-soft); color: var(--warning); }
.badge.danger,    .badge.high,
.badge.decreasing                    { background: var(--danger-soft);  color: var(--danger); }
.badge.info,      .badge.stable,
.badge.low                           { background: var(--info-soft);    color: var(--info); }

/* ── States ── */
.loading, .error {
  padding: var(--space-10);
  text-align: center;
  color: var(--text-muted);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.error { color: var(--danger); border-color: var(--danger); background: var(--danger-soft); }
```

## Rules

1. **No hardcoded values.** Every color, space, radius, and shadow comes from a token.
2. **Spacing lands on the grid.** If a value isn't a `--space-*` token, it's wrong.
3. **Borders over shadows.** Cards and tiles get `1px solid var(--border)`. `--shadow-md` is reserved for floating elements — dropdowns, modals, the mobile drawer.
4. **Semantic color is not accent color.** Green/amber/red carry meaning. Never use them for branding or decoration.
5. **Tabular numerals** on any figure that stacks in a column: `font-variant-numeric: tabular-nums`.
