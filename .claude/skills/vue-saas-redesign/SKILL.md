---
name: vue-saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS interface with a left vertical navigation sidebar replacing the top nav bar, a 4px spacing system, and consistent surface/typography tokens. Use when asked to modernize, restyle, or redesign a Vue app's look and feel, convert a top nav to a sidebar, add a vertical navigation rail, or make an app look like a professional SaaS product.
---

# Vue 3 SaaS Redesign

Converts a Vue 3 app from a horizontal top-nav layout to a modern SaaS shell: a persistent left sidebar, a slim top bar for page context, and a token-driven design system applied consistently across every view.

The design tokens and component CSS are fixed and defined in [references/design-tokens.md](references/design-tokens.md). The sidebar markup, icon set, and responsive behavior are in [references/sidebar-layout.md](references/sidebar-layout.md). Read both before editing anything.

## The rule that matters most

**Find the app's global stylesheet first, and preserve its class contract.**

Most Vue apps of this shape put an *unscoped* `<style>` block in `App.vue` that acts as the global design system. Views then use classes like `.card` and `.badge` without defining them. If you rewrite that stylesheet and drop a class, every view that used it silently loses its styling — and because the views still compile, the build stays green and nothing tells you.

Before changing any CSS:

```bash
# 1. Is App.vue's style block unscoped? (no "scoped" attribute = global)
grep -n "<style" client/src/App.vue

# 2. Inventory every global class the stylesheet defines.
#    Match class tokens anywhere on the line, NOT just at line start — a
#    grouped selector like ".badge.success, .badge.increasing { }" hides its
#    second half behind the comma, and an anchored pattern reports it missing.
sed -n '/<style/,/<\/style>/p' client/src/App.vue \
  | grep -oE '\.[a-zA-Z][a-zA-Z0-9_-]*' | sort -u

# 3. Confirm which of those the views actually consume
grep -rohE 'class="[^"]*"' client/src/views/ client/src/components/ \
  | tr ' ' '\n' | grep -oE '[a-z][a-z0-9-]+' | sort | uniq -c | sort -rn | head -40
```

Every class in step 2 that appears in step 3 **must still exist** after your rewrite, with the same semantic role. Restyle them; never delete or rename them. That single constraint is what lets you replace an entire visual system without touching the view files.

## Procedure

### 1. Survey

- Locate the root layout component (usually `App.vue`) and the router config (`main.js` or `router/index.js`).
- Extract the route list — path, label, and how the active state is computed. Labels may come from an i18n helper such as `t('nav.x')`; if so, every new label you add must be registered in **all** locale files, not just English.
- Note any components living inside the current nav bar (language switcher, profile menu, filter bar). Each needs a deliberate new home; see step 3.
- Run the class-contract commands above and write the list down.

### 2. Build the sidebar component

Create `client/src/components/AppSidebar.vue` using the markup in [references/sidebar-layout.md](references/sidebar-layout.md).

- One `<router-link>` per route, vertical, with an inline SVG icon and a text label.
- **Never use emoji as navigation icons.** Use the inline SVG set in the reference — 24×24, `stroke="currentColor"`, `stroke-width="1.5"`, `fill="none"` — so icons inherit the active/hover color automatically.
- Preserve the app's existing active-state logic. If it used `$route.path === '/x'`, keep exactly that; switching to `router-link-active` changes which item highlights on nested routes.
- Give the `<nav>` an `aria-label`, and mark the current item with `aria-current="page"`.

### 3. Restructure the shell

Replace the `<header class="top-nav">` block in `App.vue` with the grid shell from the reference. Relocate what lived in the old nav:

| Was in the top nav | Goes to |
|---|---|
| Logo / product name | Sidebar header |
| Nav links | Sidebar body |
| Language switcher, profile menu | Sidebar footer |
| Filter bar or page controls | Top bar, above the router view |

The top bar stays — a slim strip for page context and controls. It is not a second navigation.

**Check every relocated component for stale offsets.** A component that sat below the old nav often hardcodes its height — `position: sticky; top: 70px`, or its own background and bottom border. Once it moves inside the new sticky top bar those rules double-frame it and pin it at the wrong offset. Strip them from the component's own style block; don't compensate elsewhere.

**Check child components that open dropdowns.** A menu inside the sidebar footer defaults to opening downward (`top: 100%`) and may be wider than the rail. At the bottom of a scrolling sidebar it gets clipped out of view entirely. Flip such menus upward and constrain their width from the parent using `:deep()`, rather than editing the child component.

### 4. Apply the tokens

Replace the global stylesheet with the token block and component CSS from [references/design-tokens.md](references/design-tokens.md), keeping every class from your step-1 inventory.

- Declare all tokens on `:root`. Never hardcode a hex value, spacing value, or radius in a component after this point.
- Every spacing value must land on the 4px grid via a `--space-*` token. No `0.813rem`-style magic numbers.
- One elevation level. Cards get a border, not a drop shadow; reserve `--shadow-md` for genuinely floating things like dropdowns and modals.

### 5. Verify — all four, in order

```bash
cd client && npm run build          # 1. compiles clean
```

2. **Class contract intact** — re-run the step-1 inventory against the new stylesheet and diff. Any class present before and missing now is a regression, even though the build passed. Before reporting a class missing, grep the stylesheet for it directly — a grouped selector will read as absent to a sloppier pattern.
3. **Every route renders.** Visit each one and confirm the sidebar highlights the right item. A build-clean app with a blank view is the most common failure here.
4. **Responsive.** At ≤1024px the sidebar must become a toggleable drawer, and the toggle must be reachable — a drawer with no visible open control makes the whole app unnavigable on a laptop.

## Non-negotiables

- **No emoji anywhere in the UI.** Inline SVG only.
- **Keyboard access.** Every nav item needs a visible `:focus-visible` ring. Do not remove focus outlines to tidy the design.
- **Respect reduced motion.** Wrap transitions in `@media (prefers-reduced-motion: reduce)` overrides.
- **Touch targets ≥ 44px** on nav items.
- **Don't restructure view internals.** This skill changes the shell and the design system. Rewriting a view's markup is a separate task — the whole point of preserving the class contract is that views need no edits.

## Common failures

**Views lose all styling after the rewrite.** The global stylesheet was replaced without preserving the class contract. Re-run the step-1 inventory and restore the missing classes.

**Content sits under the sidebar.** The sidebar is `position: fixed` but the content area has no matching offset. Use the CSS grid shell from the reference rather than fixed positioning plus a manual margin.

**Nav labels render as raw keys** (`nav.restocking`). A label was added to the sidebar but not to every locale file. Check all of them, not just English.

**Active state stops working.** The route-matching expression was changed during the port. It must match the original logic exactly.

**Sidebar scrolls away on long pages.** The sidebar needs `position: sticky; top: 0; height: 100vh` with its own `overflow-y: auto`, independent of page scroll.
