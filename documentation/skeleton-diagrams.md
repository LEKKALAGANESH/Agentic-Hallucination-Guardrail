# Skeleton Diagrams & Responsive Layout Specification

## Agentic Hallucination Guardrail (LLMOps)

> **Purpose:** Figma-level layout specification for every component at every breakpoint. A developer should build the entire UI from this document alone.

---

## Table of Contents

1. [Global Layout Grid](#1-global-layout-grid)
2. [Typography Scale](#2-typography-scale)
3. [Spacing System](#3-spacing-system)
4. [Full Page Wireframes (All 7 Breakpoints)](#4-full-page-wireframes)
5. [Component Specifications](#5-component-specifications)
6. [Skeleton Loading States](#6-skeleton-loading-states)
7. [Touch & Interaction Targets](#7-touch--interaction-targets)
8. [Shadow & Elevation System](#8-shadow--elevation-system)
9. [Color Tokens](#9-color-tokens)
10. [Missing Feature Skeleton Specifications (From User Critique)](#10-missing-feature-skeleton-specifications-from-user-critique)
    - 10.1 Query Input Component | 10.2 Markdown Rendering | 10.3 Copy Button | 10.4 Response Action Bar
    - 10.5 Response Rating | 10.6 Share / Deep Link | 10.7 Command Palette | 10.8 Keyboard Shortcuts
    - 10.9 Session History Sidebar | 10.10 Notification Center | 10.11 Historical Trend Charts
    - 10.12 Batch Query Processing | 10.13 Onboarding Tutorial | 10.14 Dark Mode Toggle | 10.15 Updated Wireframes
11. [Additional Missing Feature Specifications](#11-additional-missing-feature-specifications)
    - 11.1 Progress Bar | 11.2 Stop/Cancel Status Bar | 11.3 Settings Panel | 11.4 Compare View
    - 11.5 Glossary Tooltips | 11.6 Empty State | 11.7 Expand/Collapse | 11.8 Bookmarks | 11.9 Inline Diff
    - 11.10 Checkpoint Manager | 11.11 Warning Banners | 11.12 Score Unavailable | 11.13 Mobile Drawer
    - 11.14 Toast Component | 11.15 Correction Log Skeleton | 11.16 Additional Skeletons
    - 11.17 Query Input Reconciliation | 11.18 Breakpoint & Cross-Document Reconciliation
    - 11.19 Error States | 11.20 Z-Index Stacking Order | 11.21 Collapsed Sidebar State
    - 11.22 Confirmation Dialog | 11.23 Dropdown Menu Component | 11.24 Modal System

---

## 1. Global Layout Grid

### Container Specifications

| Property            | 320px          | 480px          | 768px          | 1024px      | 1440px     | 2560px     | 3840px     |
| ------------------- | -------------- | -------------- | -------------- | ----------- | ---------- | ---------- | ---------- |
| Container max-width | 100%           | 100%           | 100%           | 960px       | 1280px     | 2200px     | 3400px     |
| Container padding-x | 16px           | 16px           | 24px           | 32px        | 40px       | 64px       | 96px       |
| Container padding-y | 16px           | 16px           | 24px           | 24px        | 32px       | 48px       | 64px       |
| Grid columns        | 1              | 1              | 2              | 2           | 3          | 3          | 4          |
| Grid gap            | 12px           | 16px           | 16px           | 20px        | 24px       | 32px       | 40px       |
| Sidebar width       | 0 (hidden)     | 0 (hidden)     | 0 (hidden)     | 280px       | 320px      | 400px      | 480px      |
| Sidebar mode        | Drawer overlay | Drawer overlay | Drawer overlay | Collapsible | Persistent | Persistent | Persistent |

### Header Bar

| Property           | 320px                     | 480px     | 768px     | 1024px    | 1440px    | 2560px    | 3840px    |
| ------------------ | ------------------------- | --------- | --------- | --------- | --------- | --------- | --------- |
| Height             | 56px                      | 56px      | 60px      | 64px      | 64px      | 72px      | 80px      |
| Padding-x          | 16px                      | 16px      | 24px      | 32px      | 40px      | 64px      | 96px      |
| Logo height        | 24px                      | 24px      | 28px      | 32px      | 32px      | 40px      | 48px      |
| Nav item gap       | —                         | —         | —         | 8px       | 12px      | 16px      | 20px      |
| Action button size | 36x36px                   | 36x36px   | 36x36px   | 36x36px   | 40x40px   | 48x48px   | 56x56px   |
| Dark mode toggle   | 36x36px                   | 36x36px   | 36x36px   | 36x36px   | 40x40px   | 48x48px   | 56x56px   |
| Hamburger menu     | 36x36px                   | 36x36px   | 36x36px   | Hidden    | Hidden    | Hidden    | Hidden    |
| Position           | Fixed top                 | Fixed top | Fixed top | Fixed top | Fixed top | Fixed top | Fixed top |
| Border-bottom      | 1px solid --border-subtle | same      | same      | same      | same      | same      | same      |
| z-index            | 100                       | 100       | 100       | 100       | 100       | 100       | 100       |

---

## 2. Typography Scale

| Element              | 320px          | 480px          | 768px          | 1024px         | 1440px         | 2560px         | 3840px        | Weight | Line-height |
| -------------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | ------------- | ------ | ----------- |
| H1 (Page title)      | 22px/1.375rem  | 24px/1.5rem    | 28px/1.75rem   | 32px/2rem      | 36px/2.25rem   | 44px/2.75rem   | 56px/3.5rem   | 700    | 1.2         |
| H2 (Section title)   | 18px/1.125rem  | 20px/1.25rem   | 22px/1.375rem  | 24px/1.5rem    | 28px/1.75rem   | 34px/2.125rem  | 42px/2.625rem | 600    | 1.3         |
| H3 (Card title)      | 16px/1rem      | 16px/1rem      | 18px/1.125rem  | 20px/1.25rem   | 22px/1.375rem  | 26px/1.625rem  | 32px/2rem     | 600    | 1.3         |
| Body                 | 14px/0.875rem  | 14px/0.875rem  | 15px/0.9375rem | 16px/1rem      | 16px/1rem      | 18px/1.125rem  | 22px/1.375rem | 400    | 1.6         |
| Body small           | 13px/0.8125rem | 13px/0.8125rem | 14px/0.875rem  | 14px/0.875rem  | 14px/0.875rem  | 16px/1rem      | 20px/1.25rem  | 400    | 1.5         |
| Caption              | 11px/0.6875rem | 12px/0.75rem   | 12px/0.75rem   | 13px/0.8125rem | 13px/0.8125rem | 15px/0.9375rem | 18px/1.125rem | 400    | 1.4         |
| Metric value (large) | 28px/1.75rem   | 32px/2rem      | 36px/2.25rem   | 40px/2.5rem    | 48px/3rem      | 60px/3.75rem   | 72px/4.5rem   | 800    | 1.1         |
| Metric label         | 12px/0.75rem   | 12px/0.75rem   | 13px/0.8125rem | 14px/0.875rem  | 14px/0.875rem  | 16px/1rem      | 20px/1.25rem  | 500    | 1.3         |
| Button text          | 14px/0.875rem  | 14px/0.875rem  | 14px/0.875rem  | 14px/0.875rem  | 15px/0.9375rem | 17px/1.0625rem | 20px/1.25rem  | 500    | 1.0         |
| Input text           | 14px/0.875rem  | 14px/0.875rem  | 15px/0.9375rem | 16px/1rem      | 16px/1rem      | 18px/1.125rem  | 22px/1.375rem | 400    | 1.5         |
| Code/mono            | 13px/0.8125rem | 13px/0.8125rem | 14px/0.875rem  | 14px/0.875rem  | 14px/0.875rem  | 16px/1rem      | 20px/1.25rem  | 400    | 1.5         |
| Toast text           | 13px/0.8125rem | 13px/0.8125rem | 14px/0.875rem  | 14px/0.875rem  | 14px/0.875rem  | 16px/1rem      | 18px/1.125rem | 500    | 1.4         |

**Font family:** `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
**Mono font:** `"JetBrains Mono", "Fira Code", "Cascadia Code", monospace`

**Fluid typography formula:** `font-size: clamp(MIN, PREFERRED, MAX)`

- H1: `clamp(1.375rem, 1rem + 1.5vw, 3.5rem)`
- Body: `clamp(0.875rem, 0.8rem + 0.3vw, 1.375rem)`
- Metric value: `clamp(1.75rem, 1.2rem + 2.5vw, 4.5rem)`
- H2: `clamp(1.125rem, 0.9rem + 1.2vw, 2.625rem)`
- H3: `clamp(1rem, 0.85rem + 0.9vw, 2rem)`
- Body small: `clamp(0.8125rem, 0.75rem + 0.25vw, 1.25rem)`
- Caption: `clamp(0.6875rem, 0.6rem + 0.3vw, 1.125rem)`
- Metric label: `clamp(0.75rem, 0.65rem + 0.35vw, 1.25rem)`
- Button text: `clamp(0.875rem, 0.82rem + 0.2vw, 1.25rem)`
- Input text: `clamp(0.875rem, 0.8rem + 0.3vw, 1.375rem)`
- Code/mono: `clamp(0.8125rem, 0.75rem + 0.25vw, 1.25rem)`

### Sprint 4 Token Mapping

Sprint 4 (4.2.3) defines typography using CSS token names. This table maps skeleton pixel values to Sprint 4 tokens. **Skeleton pixel values are the rendered output; Sprint 4 tokens are the implementation mechanism.**

| Skeleton Element     | Sprint 4 Token       | Notes                                         |
| -------------------- | -------------------- | --------------------------------------------- |
| H1 (Page title)      | `--font-display-2`   | Skeleton 22-56px maps to Sprint 4 24-44px range; use skeleton values as override |
| H2 (Section title)   | `--font-heading-1`   | Close match                                   |
| H3 (Card title)      | `--font-heading-2`   | Close match                                   |
| Body                 | `--font-body`        | Exact match (14-18px)                         |
| Body small           | `--font-body-sm`     | Exact match (13-16px)                         |
| Caption              | `--font-caption`     | Exact match (11-14px)                         |
| Metric value (large) | `--font-display-1`   | Skeleton 28-72px exceeds Sprint 4 28-56px; use skeleton values |
| Metric label         | `--font-overline`    | Sprint 4 10-13px, skeleton 12-20px; use skeleton values |
| Button text          | `--font-body`        | Weight 500 vs Sprint 4 weight 400; use skeleton weight |
| Input text           | `--font-body`        | Exact match                                   |
| Code/mono            | `--font-code`        | Exact match (13-16px)                         |
| Toast text           | `--font-body-sm`     | Weight 500; use skeleton weight                |

**Where Sprint 4 token ranges and skeleton pixel values conflict, skeleton values are canonical** because they match the wireframes and breakpoint tables throughout this document.

---

## 3. Spacing System

| Token        | Value | Usage                                                   |
| ------------ | ----- | ------------------------------------------------------- |
| `--space-1`  | 4px   | Inline icon-text gap, tight element spacing             |
| `--space-2`  | 8px   | Compact element padding, badge internal padding         |
| `--space-3`  | 12px  | Card padding (mobile), small gaps between related items |
| `--space-4`  | 16px  | Default card padding (mobile), input internal padding   |
| `--space-5`  | 20px  | Section gaps (mobile), medium padding                   |
| `--space-6`  | 24px  | Card padding (tablet+), gap between cards               |
| `--space-7`  | 32px  | Section gaps (desktop), large card padding              |
| `--space-8`  | 40px  | Page section dividers, hero spacing                     |
| `--space-9`  | 48px  | Page-level padding (desktop), major section breaks      |
| `--space-10` | 64px  | 2K+ enlarged container padding                          |
| `--space-11` | 80px  | Large spacing at 2K+                                    |
| `--space-12` | 96px  | 4K container padding, hero section spacing              |

### Border Radius Scale

| Token           | Value  | Usage                                   |
| --------------- | ------ | --------------------------------------- |
| `--radius-xs`   | 2px    | Tiny elements, tags                     |
| `--radius-sm`   | 4px    | Badges, small chips, inline code        |
| `--radius-md`   | 8px    | Cards (mobile), buttons, inputs         |
| `--radius-lg`   | 12px   | Cards (desktop), modals                 |
| `--radius-xl`   | 16px   | Large cards (2K+), hero sections        |
| `--radius-2xl`  | 24px   | 4K card radius                          |
| `--radius-full` | 9999px | Circular elements, pill badges, avatars |

### Fluid Spacing Formula

Spacing tokens scale linearly between mobile and 4K using the same `clamp()` approach as typography:

```
--space-fluid: clamp(MOBILE_VALUE, calc(MOBILE_VALUE + (4K_VALUE - MOBILE_VALUE) * ((100vw - 320px) / (3840px - 320px))), 4K_VALUE);
```

**Example:** Card padding scales from 12px (mobile) to 32px (4K):
```
--card-padding: clamp(12px, calc(12px + 20 * ((100vw - 320px) / 3520)), 32px);
```

---

## 4. Full Page Wireframes

### 320px — Small Mobile (Single Column, Drawer Nav)

```
+-------------------------------+ 0px
|  [☰]  Guardrail AI   [🌙][⚙] | 56px header (fixed)
+-------------------------------+ 56px
| ⬇ 16px padding-top            |
| +---------------------------+ |
| | 🔍 Enter your query...    | | Query Input: h=48px
| |  [Submit ➤]               | | Button: 44x44px
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | ⚠ CIRCUIT BREAKER BANNER  | | h=48px (if active)
| | System paused. [Retry]    | |
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | RESPONSE CARD              | |
| | Confidence: [██████ 78%]  | | Gauge inline, h=32px
| | padding: 12px              | |
| | Response text here...      | | Body: 14px
| | ...multi-line content...   | |
| |                            | |
| | [📋 Copy] [🔄 Retry]      | | Action bar: 36px btns
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | SOURCE ATTRIBUTION         | |
| | [▶ Source 1: arxiv...]     | | Collapsed: h=48px each
| | [▶ Source 2: github...]    | |
| | [▶ Source 3: docs...]      | |
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | CORRECTION LOG             | |
| | Round 1: 42% → Round 2:   | |
| | 78% (Final)               | |
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | LIVE TRACE (collapsed)     | |
| | [▶ Expand Trace Panel]     | | h=48px, tap to expand
| +---------------------------+ |
|                               |
+-------------------------------+
```

**320px Layout Rules:**

- All components: width=100%, single column stack
- Padding-x: 16px on container
- Gap between components: 12px
- LiveTrace: collapsed by default, expands as overlay drawer from bottom (h=70vh)
- ConfidenceGauge: inline within Response Card (not standalone)
- CircuitBreaker banner: only visible when active

---

### 480px — Large Mobile (Single Column, Slightly Wider)

```
+-------------------------------------+ 0px
|  [☰]   Guardrail AI      [🌙] [⚙]  | 56px header
+-------------------------------------+ 56px
| ⬇ 16px padding                       |
| +----------------------------------+ |
| | 🔍 Enter your query...   [Submit]| | h=48px, btn inline
| +----------------------------------+ |
| ⬇ 16px gap                          |
| +----------------------------------+ |
| | RESPONSE CARD                     | |
| | +-----+ Confidence: 78%          | | Gauge: 56x56 circle
| | | ██  | Body text here...        | |
| | +-----+                          | |
| |        Response continues...      | |
| | [📋 Copy] [🔄 Retry] [📤 Share] | | 3 action btns
| +----------------------------------+ |
| ⬇ 16px gap                          |
| +----------------------------------+ |
| | SOURCE ATTRIBUTION                | |
| | [▶ Source 1] [rel: 0.92]         | |
| | [▶ Source 2] [rel: 0.87]         | |
| +----------------------------------+ |
| ⬇ 16px gap                          |
| +----------------------------------+ |
| | CORRECTION LOG                    | |
| +----------------------------------+ |
| ⬇ 16px gap                          |
| +----------------------------------+ |
| | LIVE TRACE [▶ Expand]            | | Still collapsed
| +----------------------------------+ |
+-------------------------------------+
```

---

### 768px — Tablet (2-Column Grid)

```
+---------------------------------------------------+ 0px
|  [☰]   Guardrail AI            [🌙] [⚙] [?]      | 60px header
+---------------------------------------------------+ 60px
| ⬇ 24px padding                                     |
| +-----------------------------------------------+ |
| | 🔍 Enter your query...              [Submit ➤]| | h=52px
| +-----------------------------------------------+ |
| ⬇ 16px gap                                        |
| +-----------------------------------------------+ |
| | ⚠ CIRCUIT BREAKER (if active, full width)     | | h=52px
| +-----------------------------------------------+ |
| ⬇ 16px gap                                        |
| +---------------------+ +---------------------+   |
| | RESPONSE CARD       | | CONFIDENCE GAUGE    |   |
| | padding: 16px       | | +---------+         |   |
| | Body: 15px          | | |  78%    |  Radial |   |
| | Response text...    | | +---------+         |   |
| | ...content...       | | Breakdown:          |   |
| | ...multi-line...    | | Faith: 0.82         |   |
| |                     | | Relev: 0.91         |   |
| | [📋] [🔄] [📤]     | | Halluc: 0.15        |   |
| | w: ~60%             | | w: ~40%             |   |
| +---------------------+ +---------------------+   |
| ⬇ 16px gap                                        |
| +---------------------+ +---------------------+   |
| | SOURCE ATTRIBUTION  | | CORRECTION LOG      |   |
| | [▶ Source 1]        | | Round 1: 42%        |   |
| | [▶ Source 2]        | | Round 2: 78% ✓      |   |
| | [▶ Source 3]        | |                     |   |
| | w: ~50%             | | w: ~50%             |   |
| +---------------------+ +---------------------+   |
| ⬇ 16px gap                                        |
| +-----------------------------------------------+ |
| | LIVE TRACE (inline, full width)                | |
| | [Agent1]→[Agent2]→[Agent3]→[Agent4]           | |
| | Status: ✓ Complete  |  Collapsed: h=120px     | |
| +-----------------------------------------------+ |
+---------------------------------------------------+
```

---

### 1024px — Small Desktop (2-Column + Collapsible Sidebar)

```
+------------------------------------------------------------------+ 0px
| [Logo] Guardrail AI    [Search] [Docs] [Settings] [🌙]          | 64px
+------------------------------------------------------------------+
| +--------+ +---------------------------------------------------+ |
| | SIDEBAR| | MAIN CONTENT AREA                                 | |
| | w:280px| | padding: 32px                                     | |
| |        | |                                                   | |
| | History| | +-----------------------------------------------+ | |
| | [Q1]   | | | 🔍 Query Input               [Submit ➤]      | | | h=52px
| | [Q2]   | | +-----------------------------------------------+ | |
| | [Q3]   | | ⬇ 20px                                           | |
| | [Q4]   | | +-----------------------------------------------+ | |
| | [Q5]   | | | ⚠ CIRCUIT BREAKER (if active)                 | | |
| |        | | +-----------------------------------------------+ | |
| | ------| | ⬇ 20px                                           | |
| | Config | | +------------------------+ +-------------------+ | |
| | [Rules]| | | RESPONSE CARD          | | CONFIDENCE GAUGE  | | |
| | [Thrsh]| | | padding: 20px          | | Radial: 140x140px | | |
| |        | | | Body: 16px             | | Score: 40px font  | | |
| |        | | |                        | | Breakdown table   | | |
| |        | | | Response text here...  | |                   | | |
| |        | | | ...full markdown...    | |                   | | |
| |        | | |                        | |                   | | |
| |        | | | [📋] [🔄] [📤] [⬇]   | |                   | | |
| |        | | | w: ~62%                | | w: ~38%           | | |
| |        | | +------------------------+ +-------------------+ | |
| |        | | ⬇ 20px                                           | |
| |        | | +------------------------+ +-------------------+ | |
| |        | | | SOURCE ATTRIBUTION     | | CORRECTION LOG    | | |
| |        | | | Expanded cards         | | Timeline view     | | |
| |        | | | w: ~55%                | | w: ~45%           | | |
| |        | | +------------------------+ +-------------------+ | |
| |        | | ⬇ 20px                                           | |
| |        | | +-----------------------------------------------+ | |
| |        | | | LIVE TRACE (full width, expandable)            | | |
| |        | | | [●]→[●]→[●]→[●]→[●]→[●]                      | | |
| |        | | | h: 180px (collapsed) / 400px (expanded)       | | |
| |        | | +-----------------------------------------------+ | |
| +--------+ +---------------------------------------------------+ |
+------------------------------------------------------------------+
```

---

### 1440px — Desktop (3-Column + Persistent Sidebar)

```
+--------------------------------------------------------------------------------+ 0px
| [Logo] Guardrail AI      [Search...]    [Docs]  [API]  [Settings]  [🌙] [👤]  | 64px
+--------------------------------------------------------------------------------+
| +----------+ +----------------------------------------------------------------+ |
| | SIDEBAR  | | MAIN CONTENT: max-width 1280px, padding: 40px                  | |
| | w: 320px | |                                                                | |
| |          | | +------------------------------------------------------------+ | |
| | HISTORY  | | | 🔍 Enter your query...                        [Submit ➤]  | | | h=56px
| | [Q1] ✓  | | +------------------------------------------------------------+ | |
| | [Q2] ✓  | | ⬇ 24px                                                        | |
| | [Q3] ◌  | | +------------------+ +------------------+ +----------------+ | |
| | [Q4] ✗  | | | RESPONSE CARD    | | CONFIDENCE       | | LIVE TRACE     | | |
| | [Q5] ✓  | | | padding: 24px    | | GAUGE            | | (sidebar mode) | | |
| |          | | | Body: 16px       | | Radial: 160px    | | w: ~25%        | | |
| | -------- | | | w: ~45%          | | Score: 48px      | | Scrollable     | | |
| | CONFIG   | | |                  | | w: ~30%          | | h: full        | | |
| | [Rules]  | | | Full markdown    | | Metric breakdown | | Node graph     | | |
| | [Thresh] | | | response with    | | - Faithfulness   | | [●] Agent1 ✓  | | |
| | [Models] | | | code blocks,     | | - Relevancy      | | [●] Agent2 ✓  | | |
| | [Budget] | | | citations, and   | | - Hallucination  | | [●] Agent3 ◌  | | |
| |          | | | inline refs      | | - Toxicity       | | [●] Agent4 —  | | |
| | -------- | | |                  | | - Bias           | |               | | |
| | STATS    | | | [📋] [🔄] [📤]  | |                  | | Total: 4.2s   | | |
| | Queries  | | | [⬇ Export]       | |                  | | Tokens: 847   | | |
| | today: 12| | +------------------+ +------------------+ +----------------+ | |
| | Total: 89| | ⬇ 24px                                                        | |
| |          | | +------------------------------+ +--------------------------+ | |
| |          | | | SOURCE ATTRIBUTION           | | CORRECTION LOG           | | |
| |          | | | [▼ arxiv:2401.1234 — 0.94]   | | Attempt 1: Score 0.42    | | |
| |          | | | [▶ github.com/... — 0.87]    | |   → Temp reduced 0.7→0.5 | | |
| |          | | | [▶ docs.lang... — 0.81]      | | Attempt 2: Score 0.78 ✓  | | |
| |          | | | w: ~55%                      | | w: ~45%                  | | |
| |          | | +------------------------------+ +--------------------------+ | |
| +----------+ +----------------------------------------------------------------+ |
+--------------------------------------------------------------------------------+
```

---

### 2560px — QHD/2K (3-Column, Enlarged Spacing)

```
+---------------------------------------------------------------------------------------------+ 0px
| [Logo] Guardrail AI          [Search...]       [Docs] [API] [Settings] [🌙] [👤]           | 72px
+---------------------------------------------------------------------------------------------+
| +-------------+ +------------------------------------------------------------------------+ |
| | SIDEBAR     | | MAIN CONTENT: max-width 2200px, padding: 64px                         | |
| | w: 400px    | |                                                                        | |
| | padding:32px| | +--------------------------------------------------------------------+ | |
| |             | | | 🔍 Enter your query...                             [Submit ➤]     | | | h=60px
| | HISTORY     | | +--------------------------------------------------------------------+ | |
| | h-item:52px | | ⬇ 32px                                                                | |
| |             | | +--------------------+ +--------------------+ +--------------------+ | |
| | CONFIG      | | | RESPONSE CARD      | | CONFIDENCE GAUGE   | | LIVE TRACE         | | |
| | All expanded| | | padding: 32px      | | Radial: 200px dia  | | Node graph: full   | | |
| |             | | | Body: 18px         | | Score: 60px font   | | Node: 40px circles | | |
| | STATS       | | | w: ~45%            | | w: ~28%            | | Line: 3px thick    | | |
| | All visible | | | min-h: 400px       | | min-h: 400px       | | w: ~27%            | | |
| |             | | +--------------------+ +--------------------+ +--------------------+ | |
| |             | | ⬇ 32px                                                                | |
| |             | | +--------------------+ +--------------------+ +--------------------+ | |
| |             | | | SOURCE ATTRIBUTION | | CORRECTION LOG     | | METRICS SUMMARY    | | |
| |             | | | Expanded by default| | Full timeline      | | Aggregate scores   | | |
| |             | | | w: ~35%            | | w: ~35%            | | w: ~30%            | | |
| |             | | +--------------------+ +--------------------+ +--------------------+ | |
| +-------------+ +------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------------------+
```

---

### 3840px — 4K UHD (4-Column, Maximum Content Density)

```
+-----------------------------------------------------------------------------------------------------------+ 0px
| [Logo] Guardrail AI              [Search...]           [Docs] [API] [Settings] [🌙] [👤] [Notifications] | 80px
+-----------------------------------------------------------------------------------------------------------+
| +---------------+ +-----------------------------------------------------------------------------+          |
| | SIDEBAR       | | MAIN CONTENT: max-width 3400px, padding: 96px                              |          |
| | w: 480px      | |                                                                             |          |
| | padding: 40px | | +-------------------------------------------------------------------------+ |          |
| |               | | | 🔍 Enter your query (multi-line supported)                [Submit ➤]  | | h=64px   |
| | HISTORY       | | +-------------------------------------------------------------------------+ |          |
| | h-item: 60px  | | ⬇ 40px                                                                   |          |
| | font: 20px    | | +------------------+ +------------------+ +---------------+ +-----------+ |          |
| |               | | | RESPONSE CARD    | | CONFIDENCE       | | LIVE TRACE    | | CORRECTION| |          |
| | CONFIG        | | | padding: 40px    | | GAUGE            | |               | | LOG       | |          |
| | All expanded  | | | Body: 22px       | | Radial: 240px    | | Full graph    | | Timeline  | |          |
| | font: 20px    | | | Code: 20px       | | Score: 72px font | | Node: 48px    | | font: 22px| |          |
| |               | | | w: ~35%          | | w: ~20%          | | w: ~25%       | | w: ~20%   | |          |
| | STATS         | | | min-h: 500px     | | min-h: 500px     | | min-h: 500px  | | min-h:500 | |          |
| |               | | +------------------+ +------------------+ +---------------+ +-----------+ |          |
| |               | | ⬇ 40px                                                                   |          |
| |               | | +------------------+ +------------------+ +------------------+ +--------+ |          |
| |               | | | SOURCE 1         | | SOURCE 2         | | SOURCE 3         | | SRC 4  | |          |
| |               | | | Expanded card    | | Expanded card    | | Expanded card    | | Card   | |          |
| |               | | | w: ~25%          | | w: ~25%          | | w: ~25%          | | w:~25% | |          |
| |               | | +------------------+ +------------------+ +------------------+ +--------+ |          |
| +---------------+ +-----------------------------------------------------------------------------+          |
+-----------------------------------------------------------------------------------------------------------+
```

---

## 5. Component Specifications

### 5.1 — Query Input Area

| Property          | 320px                               | 480px       | 768px | 1024px | 1440px | 2560px | 3840px |
| ----------------- | ----------------------------------- | ----------- | ----- | ------ | ------ | ------ | ------ |
| Width             | 100%                                | 100%        | 100%  | 100%   | 100%   | 100%   | 100%   |
| Height            | 48px                                | 48px        | 52px  | 52px   | 56px   | 60px   | 64px   |
| Padding-x         | 12px                                | 16px        | 16px  | 16px   | 20px   | 24px   | 32px   |
| Padding-y         | 12px                                | 12px        | 14px  | 14px   | 16px   | 18px   | 20px   |
| Font-size         | 14px                                | 14px        | 15px  | 16px   | 16px   | 18px   | 22px   |
| Border-radius     | 8px                                 | 8px         | 8px   | 8px    | 10px   | 12px   | 16px   |
| Border            | 1px solid --border-default          | same        | same  | same   | same   | 1.5px  | 2px    |
| Submit btn width  | 100% below                          | 80px inline | 100px | 100px  | 110px  | 130px  | 160px  |
| Submit btn height | 44px                                | 44px        | 44px  | 44px   | 44px   | 52px   | 56px   |
| Submit btn radius | 8px                                 | 8px         | 8px   | 8px    | 10px   | 12px   | 16px   |
| Focus ring        | 2px offset, 2px solid --focus-color | same        | same  | same   | same   | 3px    | 3px    |
| Placeholder color | --text-tertiary                     | same        | same  | same   | same   | same   | same   |

**Mobile (320px):** Submit button stacks below input, full width.
**480px+:** Submit button sits inline at right edge of input.

---

### 5.2 — Response Card

| Property           | 320px                     | 480px       | 768px       | 1024px      | 1440px      | 2560px      | 3840px      |
| ------------------ | ------------------------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| Width              | 100%                      | 100%        | ~60%        | ~62%        | ~45%        | ~45%        | ~35%        |
| Min-height         | 200px                     | 200px       | 250px       | 300px       | 300px       | 400px       | 500px       |
| Padding            | 12px                      | 16px        | 16px        | 20px        | 24px        | 32px        | 40px        |
| Margin-bottom      | 12px                      | 16px        | 16px        | 20px        | 24px        | 32px        | 40px        |
| Border-radius      | 8px                       | 8px         | 10px        | 12px        | 12px        | 16px        | 20px        |
| Border             | 1px solid --border-subtle | same        | same        | same        | same        | 1.5px       | 2px         |
| Shadow             | elevation-1               | elevation-1 | elevation-2 | elevation-2 | elevation-2 | elevation-2 | elevation-3 |
| Body font-size     | 14px                      | 14px        | 15px        | 16px        | 16px        | 18px        | 22px        |
| Code block font    | 13px                      | 13px        | 14px        | 14px        | 14px        | 16px        | 20px        |
| Code block padding | 8px                       | 12px        | 12px        | 16px        | 16px        | 20px        | 24px        |
| Code block radius  | 4px                       | 6px         | 6px         | 8px         | 8px         | 10px        | 12px        |
| Action bar height  | 36px                      | 40px        | 40px        | 40px        | 44px        | 48px        | 56px        |
| Action button size | 32x32px                   | 36x36px     | 36x36px     | 36x36px     | 40x40px     | 44x44px     | 52x52px     |
| Action btn gap     | 4px                       | 8px         | 8px         | 8px         | 12px        | 16px        | 20px        |

**Action Buttons:** Copy, Retry, Share, Export — icon-only on mobile, icon+label on 1024px+

---

### 5.3 — Confidence Gauge

| Property          | 320px                   | 480px                | 768px           | 1024px          | 1440px          | 2560px          | 3840px          |
| ----------------- | ----------------------- | -------------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| Display mode      | Inline in Response Card | Inline w/ mini gauge | Standalone card | Standalone card | Standalone card | Standalone card | Standalone card |
| Gauge diameter    | 32px (inline bar)       | 56px                 | 120px           | 140px           | 160px           | 200px           | 240px           |
| Arc stroke width  | N/A (bar)               | 6px                  | 8px             | 10px            | 12px            | 14px            | 18px            |
| Score font-size   | 16px                    | 20px                 | 28px            | 40px            | 48px            | 60px            | 72px            |
| Score font-weight | 700                     | 700                  | 800             | 800             | 800             | 800             | 800             |
| Label font-size   | 12px                    | 12px                 | 13px            | 14px            | 14px            | 16px            | 20px            |
| Card width        | N/A                     | N/A                  | ~40%            | ~38%            | ~30%            | ~28%            | ~20%            |
| Card padding      | N/A                     | N/A                  | 16px            | 20px            | 24px            | 32px            | 40px            |
| Card min-height   | N/A                     | N/A                  | 200px           | 280px           | 300px           | 400px           | 500px           |
| Breakdown rows    | Hidden                  | Hidden               | Visible         | Visible         | Visible         | Visible         | Visible         |
| Breakdown font    | N/A                     | N/A                  | 13px            | 14px            | 14px            | 16px            | 20px            |
| Breakdown row-h   | N/A                     | N/A                  | 28px            | 32px            | 32px            | 40px            | 48px            |
| Tooltip width     | 200px                   | 240px                | 280px           | 300px           | 320px           | 400px           | 480px           |

**Color zones on arc:**

- Red (0-49%): `#EF4444` / dark: `#F87171`
- Yellow (50-79%): `#F59E0B` / dark: `#FBBF24`
- Green (80-100%): `#10B981` / dark: `#34D399`

**Mobile (320px):** Displays as a colored progress bar (h=8px) with score text next to it inside the Response Card.
**480px:** Mini radial gauge (56px) floats top-right in Response Card.
**768px+:** Becomes its own standalone card in the grid.

---

### 5.4 — Live Trace Panel

| Property              | 320px         | 480px         | 768px           | 1024px          | 1440px               | 2560px         | 3840px         |
| --------------------- | ------------- | ------------- | --------------- | --------------- | -------------------- | -------------- | -------------- |
| Display mode          | Bottom drawer | Bottom drawer | Inline (full-w) | Inline (full-w) | Column in grid       | Column in grid | Column in grid |
| Width                 | 100%          | 100%          | 100%            | 100%            | ~25%                 | ~27%           | ~25%           |
| Collapsed height      | 48px          | 48px          | 120px           | 180px           | Full height          | Full height    | Full height    |
| Expanded height       | 70vh          | 70vh          | 300px           | 400px           | Full height          | Full height    | Full height    |
| Padding               | 12px          | 16px          | 16px            | 20px            | 24px                 | 32px           | 40px           |
| Node circle diameter  | 24px          | 28px          | 32px            | 36px            | 36px                 | 40px           | 48px           |
| Connection line width | 2px           | 2px           | 2px             | 2px             | 2px                  | 3px            | 3px            |
| Agent name font-size  | 12px          | 12px          | 13px            | 14px            | 14px                 | 16px           | 20px           |
| Status indicator      | 8px dot       | 8px dot       | 10px dot        | 12px dot        | 12px dot             | 14px dot       | 16px dot       |
| Timestamp font-size   | 10px          | 11px          | 12px            | 12px            | 13px                 | 15px           | 18px           |
| Scroll area max-h     | 60vh          | 60vh          | 240px           | 340px           | calc(100vh - 200px)  | same           | same           |
| Expand/collapse btn   | 44x44px       | 44x44px       | 36x36px         | 36x36px         | Hidden (always open) | Hidden         | Hidden         |

**Animation specs:**

- Drawer slide: 250ms ease-out
- Node appear: 200ms ease-out, staggered 50ms per node
- Connection line draw: 300ms ease-out (SVG stroke-dashoffset animation)
- Status dot pulse: 1.5s infinite for "running" state

**Virtualization Threshold:** When the trace log exceeds 100 entries, the trace panel switches from native DOM rendering to `react-window` (FixedSizeList). Row height: 48px. Overscan: 5 rows above and below viewport. Below 100 entries, standard `.map()` rendering is used for simpler DOM and faster initial render. The threshold is configurable via `TRACE_VIRTUALIZATION_THRESHOLD` environment variable.

---

### 5.5 — Source Attribution Cards

| Property                    | 320px            | 480px     | 768px     | 1024px    | 1440px    | 2560px    | 3840px    |
| --------------------------- | ---------------- | --------- | --------- | --------- | --------- | --------- | --------- |
| Card width                  | 100%             | 100%      | ~50%      | ~55%      | ~55%      | ~35%      | ~25%      |
| Collapsed height            | 48px             | 48px      | 52px      | 56px      | 56px      | 64px      | 72px      |
| Expanded height             | auto (200-400px) | auto      | auto      | auto      | auto      | auto      | auto      |
| Card padding                | 10px 12px        | 12px 16px | 14px 16px | 16px 20px | 16px 24px | 20px 32px | 24px 40px |
| Margin-bottom               | 8px              | 8px       | 10px      | 12px      | 12px      | 16px      | 20px      |
| Border-radius               | 6px              | 8px       | 8px       | 10px      | 10px      | 12px      | 16px      |
| Title font-size             | 13px             | 14px      | 14px      | 15px      | 15px      | 17px      | 20px      |
| Relevance badge             | 28x20px          | 32x22px   | 32x22px   | 36x24px   | 36x24px   | 44x28px   | 52x32px   |
| Badge font-size             | 10px             | 11px      | 11px      | 12px      | 12px      | 14px      | 16px      |
| Excerpt font-size           | 13px             | 13px      | 14px      | 14px      | 14px      | 16px      | 20px      |
| Max visible (before scroll) | 3                | 3         | 4         | 5         | 5         | 6         | 8         |
| Expand icon size            | 20px             | 20px      | 20px      | 24px      | 24px      | 28px      | 32px      |

---

### 5.6 — Circuit Breaker Banner

| Property          | 320px                       | 480px           | 768px        | 1024px       | 1440px       | 2560px       | 3840px       |
| ----------------- | --------------------------- | --------------- | ------------ | ------------ | ------------ | ------------ | ------------ |
| Width             | 100%                        | 100%            | 100%         | 100%         | 100%         | 100%         | 100%         |
| Height            | auto (min 48px)             | auto (min 48px) | 52px         | 52px         | 56px         | 64px         | 72px         |
| Padding-x         | 12px                        | 16px            | 24px         | 32px         | 40px         | 64px         | 96px         |
| Padding-y         | 10px                        | 10px            | 12px         | 14px         | 14px         | 16px         | 20px         |
| Icon size         | 20px                        | 20px            | 24px         | 24px         | 24px         | 28px         | 32px         |
| Message font-size | 13px                        | 14px            | 14px         | 15px         | 15px         | 17px         | 20px         |
| Retry button      | 36x32px                     | 36x32px         | 80x36px      | 80x36px      | 90x40px      | 110x48px     | 130x56px     |
| Retry btn label   | Icon only                   | Icon only       | "Retry" text | "Retry" text | "Retry" text | "Retry" text | "Retry" text |
| Position          | Sticky below header         | same            | same         | same         | same         | same         | same         |
| Background        | --color-error-50            | same            | same         | same         | same         | same         | same         |
| Border-bottom     | 2px solid --color-error-500 | same            | same         | same         | same         | 3px          | 3px          |
| z-index           | 90                          | 90              | 90           | 90           | 90           | 90           | 90           |

**States:**

- Level 1-2 (Agent/Node): Yellow background, amber border — "Correction in progress..."
- Level 3 (Swarm): Orange background — "Loop detected. Showing partial results."
- Level 4 (Global): Red background — "System paused for safety. Here's what we know so far."

---

### 5.7 — Correction Log

| Property            | 320px | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| ------------------- | ----- | ----- | ----- | ------ | ------ | ------ | ------ |
| Width               | 100%  | 100%  | ~50%  | ~45%   | ~45%   | ~35%   | ~20%   |
| Min-height          | 100px | 100px | 150px | 200px  | 200px  | 280px  | 350px  |
| Padding             | 12px  | 16px  | 16px  | 20px   | 24px   | 32px   | 40px   |
| Border-radius       | 8px   | 8px   | 10px  | 12px   | 12px   | 16px   | 20px   |
| Timeline dot size   | 10px  | 10px  | 12px  | 12px   | 14px   | 16px   | 20px   |
| Timeline line width | 2px   | 2px   | 2px   | 2px    | 2px    | 3px    | 3px    |
| Round label font    | 13px  | 13px  | 14px  | 14px   | 14px   | 16px   | 20px   |
| Score font          | 16px  | 18px  | 20px  | 24px   | 28px   | 34px   | 40px   |
| Diff indicator      | 12px  | 12px  | 14px  | 16px   | 16px   | 20px   | 24px   |

---

## 6. Skeleton Loading States

### Skeleton Color Tokens

| Token                  | Light Mode                                                | Dark Mode                 |
| ---------------------- | --------------------------------------------------------- | ------------------------- |
| `--skeleton-base`      | `#E2E8F0`                                                 | `#2D3748`                 |
| `--skeleton-highlight` | `#F7FAFC`                                                 | `#4A5568`                 |
| `--skeleton-shimmer`   | linear-gradient(90deg, base 0%, highlight 50%, base 100%) | same pattern, dark values |

### Shimmer Animation

```css
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
/* Duration: 1.5s, timing: ease-in-out, iteration: infinite */
/* Background-size: 200% 100% */
```

**GPU Acceleration Hints:** All animated elements receive `will-change: transform, opacity` during active animation and `will-change: auto` after completion (to release GPU memory). Skeleton shimmer cards use `transform: translateZ(0)` to promote to compositor layer, preventing main-thread repaints during the gradient sweep. The Live Trace panel's scrolling container uses `contain: layout style paint` for isolation. These hints are conditional: only applied when `navigator.hardwareConcurrency >= 4` to avoid GPU overhead on low-end devices.

### Skeleton Wireframes Per Component

#### Response Card Skeleton

```
+----------------------------------+
| [====== title ======]   [●]     |   title: 60% width x 20px, circle: 32px
|                                  |
| [=====================]          |   text line 1: 90% width x 14px
| [=================]              |   text line 2: 75% width x 14px
| [====================]           |   text line 3: 85% width x 14px
| [==============]                 |   text line 4: 65% width x 14px
| [==================]             |   text line 5: 80% width x 14px
|                                  |
| [====]  [====]  [====]          |   3 action buttons: 48x32px each
+----------------------------------+
Corner radius: matches real card (8-20px by breakpoint)
```

#### Confidence Gauge Skeleton (768px+)

```
+--------------------+
|     +-------+      |    Circular outline: gauge diameter
|    /         \     |    Stroke: dashed, --skeleton-base
|   |    [==]   |    |    Center rectangle: 60% x 28px (score placeholder)
|    \         /     |
|     +-------+      |
|                    |
| [=====] [===]      |    2 rows of metric bars
| [=====] [===]      |    label: 40% width, value: 25% width
| [=====] [===]      |
| [=====] [===]      |
+--------------------+
```

#### Live Trace Skeleton

```
+----------------------------------------+
| [====== TRACE ======]                  |   header: 50% x 18px
|                                        |
| [●]----[●]----[●]----[○]----[○]       |   circles: node diameter, filled=done
|  |      |      |      |      |        |   lines: 2px dashed
| [==]   [==]   [==]   [==]   [==]      |   labels: 40px x 12px
+----------------------------------------+
```

#### Source Attribution Skeleton

```
+----------------------------------+
| [▶] [===============]  [====]    |   chevron: 16px, title: 60%, badge: 40x20px
+----------------------------------+
+----------------------------------+
| [▶] [=============]    [====]    |   stacked, 3-5 rows
+----------------------------------+
+----------------------------------+
| [▶] [================]  [====]   |
+----------------------------------+
Row height matches collapsed height per breakpoint
```

---

## 7. Touch & Interaction Targets

| Element Type                   | 320-480px          | 768px   | 1024-1440px | 2560px  | 3840px  |
| ------------------------------ | ------------------ | ------- | ----------- | ------- | ------- |
| Primary button (Submit)        | 44x44px min        | 44x44px | 40x40px     | 48x48px | 56x56px |
| Secondary button (Copy, Share) | 44x44px min        | 44x44px | 36x36px     | 44x44px | 52x52px |
| Icon button (Dark mode, Menu)  | 44x44px min        | 44x44px | 36x36px     | 48x48px | 56x56px |
| Source card expand toggle      | 44x44px            | 44x44px | 32x32px     | 40x40px | 48x48px |
| Sidebar history item           | 44px height        | 44px    | 40px height | 52px    | 60px    |
| Trace node (interactive)       | 44x44px touch area | 44x44px | 36x36px     | 40x40px | 48x48px |
| Toast dismiss                  | 44x44px            | 44x44px | 32x32px     | 40x40px | 48x48px |
| Input field                    | 48px height        | 52px    | 52px height | 60px    | 64px    |

**Touch area padding:** When the visual element is smaller than the touch target, add invisible padding to meet minimums. For example, a 24px icon on mobile gets `padding: 10px` to create a 44x44px touch area.

---

## 8. Shadow & Elevation System

| Level | Light Mode                                                | Dark Mode                     | Usage                         |
| ----- | --------------------------------------------------------- | ----------------------------- | ----------------------------- |
| 0     | none                                                      | none                          | Flat inline elements          |
| 1     | `0 1px 2px rgba(0,0,0,0.05)`                              | `0 1px 2px rgba(0,0,0,0.3)`   | Subtle cards, resting state   |
| 2     | `0 2px 4px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)`  | `0 2px 4px rgba(0,0,0,0.4)`   | Default cards, sections       |
| 3     | `0 4px 8px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.06)`  | `0 4px 8px rgba(0,0,0,0.5)`   | Hover state, elevated cards   |
| 4     | `0 8px 16px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.08)` | `0 8px 16px rgba(0,0,0,0.6)`  | Dropdowns, tooltips, popovers |
| 5     | `0 16px 32px rgba(0,0,0,0.2), 0 8px 16px rgba(0,0,0,0.1)` | `0 16px 32px rgba(0,0,0,0.7)` | Modals, drawers               |
| 6     | `0 24px 48px rgba(0,0,0,0.25)`                            | `0 24px 48px rgba(0,0,0,0.8)` | Full-screen overlays          |

---

## 9. Color Tokens

### Light Mode

| Token                    | Hex       | Usage                               |
| ------------------------ | --------- | ----------------------------------- |
| `--color-bg-primary`     | `#FFFFFF` | Page background                     |
| `--color-bg-secondary`   | `#F8FAFC` | Card backgrounds, sidebar           |
| `--color-bg-tertiary`    | `#F1F5F9` | Hover states, alternate rows        |
| `--color-text-primary`   | `#0F172A` | Headings, primary text              |
| `--color-text-secondary` | `#475569` | Body text, descriptions             |
| `--color-text-tertiary`  | `#94A3B8` | Placeholders, captions              |
| `--color-border-default` | `#E2E8F0` | Card borders, dividers              |
| `--color-border-subtle`  | `#F1F5F9` | Subtle separators                   |
| `--color-primary-500`    | `#6366F1` | Primary actions, links, focus rings |
| `--color-primary-600`    | `#4F46E5` | Primary hover                       |
| `--color-success-500`    | `#10B981` | High confidence, pass states        |
| `--color-warning-500`    | `#F59E0B` | Medium confidence, caution          |
| `--color-error-500`      | `#EF4444` | Low confidence, circuit breaker     |
| `--color-error-50`       | `#FEF2F2` | Error banner background             |
| `--color-error-700`      | `#B91C1C` | Diff removed text, error emphasis   |
| `--color-info-500`       | `#3B82F6` | Informational, live trace           |
| `--color-info-50`        | `#EFF6FF` | Info banner background              |
| `--color-success-50`     | `#ECFDF5` | Diff added background               |
| `--color-success-700`    | `#047857` | Diff added text                     |
| `--color-warning-50`     | `#FFFBEB` | Warning banner bg, bookmark filter  |
| `--color-warning-800`    | `#92400E` | Warning text on warning backgrounds |
| `--color-primary-300`    | `#A5B4FC` | Bar chart fill, subtle accents      |
| `--color-neutral-200`    | `#E2E8F0` | Progress bar track (light)          |
| `--color-neutral-400`    | `#94A3B8` | Neutral/cancelled states            |
| `--color-neutral-700`    | `#334155` | Progress bar track (dark)           |

### Dark Mode

| Token                    | Hex       |
| ------------------------ | --------- |
| `--color-bg-primary`     | `#0F172A` |
| `--color-bg-secondary`   | `#1E293B` |
| `--color-bg-tertiary`    | `#334155` |
| `--color-text-primary`   | `#F8FAFC` |
| `--color-text-secondary` | `#CBD5E1` |
| `--color-text-tertiary`  | `#64748B` |
| `--color-border-default` | `#334155` |
| `--color-border-subtle`  | `#1E293B` |
| `--color-primary-500`    | `#818CF8` |
| `--color-primary-600`    | `#6366F1` |
| `--color-primary-300`    | `#6366F1` |
| `--color-neutral-200`    | `#4A5568` |
| `--color-neutral-400`    | `#718096` |
| `--color-neutral-700`    | `#CBD5E1` |
| `--color-success-50`     | `#064E3B` |
| `--color-success-700`    | `#6EE7B7` |
| `--color-warning-50`     | `#78350F` |
| `--color-warning-800`    | `#FDE68A` |
| `--color-error-50`       | `#7F1D1D` |
| `--color-error-700`      | `#FCA5A5` |
| `--color-info-50`        | `#1E3A5F` |

---

## 10. Missing Feature Skeleton Specifications (From User Critique)

> The user critique identified 35 missing behavioral patterns (78% gap rate). This section adds Figma-level specs for every missing feature that requires a UI component. Each feature includes a responsive box model table, ASCII wireframes, and interaction notes.

---

### 10.1 — Query Input Component (P0 Critical)

**The entire query input was unspecified.** This is the primary interaction point for every user.

| Property                 | 320px                      | 480px | 768px           | 1024px | 1440px | 2560px | 3840px |
| ------------------------ | -------------------------- | ----- | --------------- | ------ | ------ | ------ | ------ |
| Width                    | 100%                       | 100%  | 100%            | 100%   | 100%   | 100%   | 100%   |
| Min-height               | 48px                       | 48px  | 52px            | 56px   | 56px   | 64px   | 72px   |
| Max-height (auto-expand) | 160px (5 lines)            | 160px | 200px (6 lines) | 240px  | 240px  | 300px  | 360px  |
| Padding-x                | 12px                       | 16px  | 16px            | 20px   | 20px   | 28px   | 36px   |
| Padding-y                | 12px                       | 12px  | 14px            | 16px   | 16px   | 20px   | 24px   |
| Font-size                | 14px                       | 14px  | 15px            | 16px   | 16px   | 18px   | 22px   |
| Line-height              | 1.5                        | 1.5   | 1.5             | 1.5    | 1.5    | 1.5    | 1.5    |
| Border                   | 1px solid --border-default | same  | same            | same   | same   | 1.5px  | 2px    |
| Border-radius            | 8px                        | 8px   | 10px            | 10px   | 12px   | 14px   | 16px   |
| Focus border             | 2px solid --primary-500    | same  | same            | same   | same   | 2.5px  | 3px    |
| Placeholder font         | 14px, --text-tertiary      | same  | 15px            | 16px   | 16px   | 18px   | 22px   |

**Token Counter (bottom-right of input):**

| Property             | 320px                   | 480px | 768px | 1024px     | 1440px | 2560px | 3840px |
| -------------------- | ----------------------- | ----- | ----- | ---------- | ------ | ------ | ------ |
| Font-size            | 11px                    | 11px  | 12px  | 12px       | 13px   | 15px   | 18px   |
| Color                | --text-tertiary         | same  | same  | same       | same   | same   | same   |
| Warning color (>80%) | --warning-500           | same  | same  | same       | same   | same   | same   |
| Error color (>95%)   | --error-500             | same  | same  | same       | same   | same   | same   |
| Position             | bottom-right, 8px inset | same  | same  | 12px inset | 12px   | 16px   | 20px   |

**Submit Button:**

| Property           | 320px              | 480px         | 768px    | 1024px   | 1440px                | 2560px   | 3840px   |
| ------------------ | ------------------ | ------------- | -------- | -------- | --------------------- | -------- | -------- |
| Width              | 100% (below input) | 80px (inline) | 100px    | 100px    | 110px                 | 130px    | 160px    |
| Height             | 44px               | 44px          | 44px     | 44px     | 44px                  | 52px     | 56px     |
| Font-size          | 14px               | 14px          | 14px     | 14px     | 15px                  | 17px     | 20px     |
| Border-radius      | 8px                | 8px           | 8px      | 8px      | 10px                  | 12px     | 16px     |
| Icon (send arrow)  | 18px               | 18px          | 18px     | 18px     | 20px                  | 24px     | 28px     |
| Label              | Icon only          | Icon only     | "Submit" | "Submit" | "Submit"              | "Submit" | "Submit" |
| Shortcut hint      | Hidden             | Hidden        | Hidden   | Hidden   | "Ctrl+Enter" visible  | same     | same     |
| Shortcut hint font | —                  | —             | —        | —        | 12px, --text-tertiary | 14px     | 16px     |

**Stop Button (replaces Submit during processing):**

| Property           | 320px       | 480px  | 768px             | 1024px | 1440px | 2560px | 3840px |
| ------------------ | ----------- | ------ | ----------------- | ------ | ------ | ------ | ------ |
| Width              | 100%        | 100%   | 120px             | 120px  | 140px  | 160px  | 200px  |
| Height             | 44px        | 44px   | 44px              | 44px   | 44px   | 52px   | 56px   |
| Background         | --error-500 | same   | same              | same   | same   | same   | same   |
| Text color         | white       | same   | same              | same   | same   | same   | same   |
| Icon (stop square) | 16px        | 16px   | 16px              | 16px   | 18px   | 20px   | 24px   |
| Label              | "Stop"      | "Stop" | "Stop Generating" | same   | same   | same   | same   |
| Border-radius      | 8px         | 8px    | 8px               | 8px    | 10px   | 12px   | 16px   |

**File Upload Button (optional, below input on desktop):**

| Property         | 320px  | 480px  | 768px  | 1024px  | 1440px  | 2560px  | 3840px  |
| ---------------- | ------ | ------ | ------ | ------- | ------- | ------- | ------- |
| Display          | Hidden | Hidden | Hidden | Visible | Visible | Visible | Visible |
| Height           | —      | —      | —      | 36px    | 36px    | 44px    | 52px    |
| Font-size        | —      | —      | —      | 13px    | 14px    | 16px    | 18px    |
| Icon (paperclip) | —      | —      | —      | 16px    | 16px    | 20px    | 24px    |

**Wireframes:**

```
320px Mobile:                             1440px Desktop:
+-----------------------------+           +--------------------------------------------------------------+
| Ask a question...           |           | Ask a question or paste text to verify for hallucinations... |
|                             |           |                                                              |
|                  23/4096 tok|           |                                                              |
+-----------------------------+           |                                                   89/4096 tok|
| [     ■ Stop Generating    ]|           | [📎 Upload]           [Ctrl+Enter]   [■ Stop Generating]    |
+-----------------------------+           +--------------------------------------------------------------+
```

---

### 10.2 — Markdown / Response Rendering (P0 Critical)

Response cards must render LLM markdown output. These specs define content styling WITHIN the Response Card.

**Heading Scale (within response):**

| Element               | 320px    | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| --------------------- | -------- | ----- | ----- | ------ | ------ | ------ | ------ |
| Response H2           | 17px/600 | 18px  | 19px  | 20px   | 22px   | 26px   | 30px   |
| Response H3           | 15px/600 | 16px  | 17px  | 18px   | 19px   | 22px   | 26px   |
| Response H4           | 14px/600 | 15px  | 16px  | 17px   | 17px   | 20px   | 24px   |
| Response body         | 14px/400 | 14px  | 15px  | 16px   | 16px   | 18px   | 22px   |
| Heading margin-top    | 16px     | 16px  | 20px  | 24px   | 24px   | 28px   | 32px   |
| Heading margin-bottom | 8px      | 8px   | 10px  | 12px   | 12px   | 14px   | 16px   |

**Code Blocks:**

| Property             | 320px                | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| -------------------- | -------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Font-size            | 12px                 | 13px   | 13px   | 14px   | 14px   | 16px   | 20px   |
| Font-family          | JetBrains Mono       | same   | same   | same   | same   | same   | same   |
| Padding              | 10px 12px            | 12px   | 14px   | 16px   | 16px   | 20px   | 24px   |
| Border-radius        | 6px                  | 6px    | 8px    | 8px    | 8px    | 10px   | 12px   |
| Background           | --bg-tertiary        | same   | same   | same   | same   | same   | same   |
| Max-height           | 300px (scroll)       | 300px  | 400px  | 500px  | 500px  | 600px  | 800px  |
| Overflow-x           | scroll               | scroll | scroll | scroll | scroll | scroll | scroll |
| Line-height          | 1.5                  | 1.5    | 1.5    | 1.5    | 1.5    | 1.5    | 1.5    |
| Language label font  | 10px                 | 10px   | 11px   | 12px   | 12px   | 14px   | 16px   |
| Copy button size     | 28x28px              | 28x28  | 32x32  | 32x32  | 32x32  | 40x40  | 48x48  |
| Copy button position | top-right, 6px inset | same   | 8px    | 8px    | 8px    | 10px   | 12px   |

**Inline Code:**

| Property      | All breakpoints          |
| ------------- | ------------------------ |
| Font-family   | JetBrains Mono           |
| Font-size     | 0.9em (relative to body) |
| Padding       | 2px 6px                  |
| Border-radius | 4px                      |
| Background    | --bg-tertiary            |

**Tables in Response:**

| Property            | 320px                      | 480px    | 768px    | 1024px    | 1440px    | 2560px    | 3840px    |
| ------------------- | -------------------------- | -------- | -------- | --------- | --------- | --------- | --------- |
| Cell padding        | 6px 8px                    | 8px 10px | 8px 12px | 10px 14px | 10px 14px | 12px 16px | 14px 20px |
| Header bg           | --bg-tertiary              | same     | same     | same      | same      | same      | same      |
| Header font-weight  | 600                        | same     | same     | same      | same      | same      | same      |
| Border              | 1px solid --border-default | same     | same     | same      | same      | same      | same      |
| Overflow-x (mobile) | scroll                     | scroll   | auto     | auto      | auto      | auto      | auto      |
| Sticky first column | Yes                        | Yes      | No       | No        | No        | No        | No        |
| Min cell width      | 80px                       | 80px     | auto     | auto      | auto      | auto      | auto      |

**Blockquotes:**

| Property     | All breakpoints         |
| ------------ | ----------------------- |
| Border-left  | 3px solid --primary-500 |
| Padding-left | 16px                    |
| Margin       | 12px 0                  |
| Color        | --text-secondary        |
| Font-style   | italic                  |

**Lists:**

| Property               | All breakpoints   |
| ---------------------- | ----------------- |
| Indent per level       | 20px              |
| Bullet/number size     | matches body font |
| Item margin-bottom     | 4px               |
| Nested list margin-top | 4px               |

**Math / LaTeX Rendering (KaTeX):**

| Property               | 320px             | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ---------------------- | ----------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Inline math font-size  | 1em (matches body)| same   | same   | same   | same   | same   | same   |
| Inline math baseline   | Aligned to text baseline | same | same | same | same | same | same |
| Block math font-size   | 1.1em             | same   | same   | same   | same   | same   | same   |
| Block math padding-y   | 12px              | 12px   | 16px   | 16px   | 20px   | 24px   | 32px   |
| Block math margin-y    | 12px              | 12px   | 16px   | 16px   | 20px   | 24px   | 32px   |
| Block math max-width   | 100%              | 100%   | 100%   | 100%   | 100%   | 100%   | 100%   |
| Block math overflow-x  | scroll            | scroll | auto   | auto   | auto   | auto   | auto   |
| Block math text-align  | center            | center | center | center | center | center | center |
| Block math bg          | transparent       | same   | same   | same   | same   | same   | same   |

- Renderer: KaTeX (preferred) or MathJax. KaTeX is lighter and faster for local-first apps.
- Inline: `$E = mc^2$` renders inline with surrounding text, no line-break disruption.
- Block: `$$\sum_{i=1}^{n} x_i$$` renders centered, full-width, with vertical padding.
- Accessibility: each math element gets `aria-label` with text representation (e.g., `aria-label="E equals m c squared"`).
- Long equations on mobile: horizontal scroll within the block container, not line-wrapped.

**Max content width:** `clamp(100%, 100%, 80ch)` — text lines capped at ~80 characters for readability on wide screens. Code blocks, tables, and block math may exceed this.

---

### 10.3 — Copy Button (P0 Critical)

Present on: (a) every response card header, (b) every code block.

**Response Card Copy Button:**

| Property                 | 320px               | 480px  | 768px                  | 1024px | 1440px          | 2560px | 3840px |
| ------------------------ | ------------------- | ------ | ---------------------- | ------ | --------------- | ------ | ------ |
| Size                     | 36x36px             | 36x36  | 36x36                  | 36x36  | 40x40           | 44x44  | 52x52  |
| Icon size                | 16px                | 16px   | 16px                   | 16px   | 18px            | 20px   | 24px   |
| Position                 | Top-right of card   | same   | same                   | same   | same            | same   | same   |
| Offset from edge         | 8px                 | 8px    | 12px                   | 12px   | 16px            | 20px   | 24px   |
| Label                    | Hidden              | Hidden | "Copy"                 | "Copy" | "Copy Response" | same   | same   |
| Label font               | —                   | —      | 12px                   | 12px   | 13px            | 15px   | 18px   |
| Success icon (checkmark) | Same size           | same   | same                   | same   | same            | same   | same   |
| Success color            | --success-500       | same   | same                   | same   | same            | same   | same   |
| Success duration         | 2 seconds           | same   | same                   | same   | same            | same   | same   |
| Tooltip                  | "Copy to clipboard" | same   | Hidden (label visible) | same   | same            | same   | same   |

**Code Block Copy Button:**

| Property          | All breakpoints                         |
| ----------------- | --------------------------------------- |
| Size              | Same as code block spec in 10.2         |
| Position          | Top-right of code block, inside padding |
| Opacity (default) | 0.6                                     |
| Opacity (hover)   | 1.0                                     |
| Transition        | opacity 150ms ease-out                  |

---

### 10.4 — Response Action Bar (P1 Important)

Unified action bar at the bottom of every response card. Contains: Copy, Regenerate, Edit & Retry, Share, Export, Feedback.

| Property             | 320px                     | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| -------------------- | ------------------------- | ----- | ----- | ------ | ------ | ------ | ------ |
| Bar height           | 44px                      | 44px  | 44px  | 44px   | 48px   | 52px   | 60px   |
| Bar padding-x        | 8px                       | 12px  | 12px  | 16px   | 16px   | 24px   | 32px   |
| Bar border-top       | 1px solid --border-subtle | same  | same  | same   | same   | same   | same   |
| Button size          | 36x36 (icon)              | 36x36 | 36x36 | 36x36  | 40x40  | 44x44  | 52x52  |
| Button gap           | 4px                       | 4px   | 8px   | 8px    | 8px    | 12px   | 16px   |
| Button border-radius | 6px                       | 6px   | 6px   | 6px    | 8px    | 8px    | 10px   |

**Button Visibility per Breakpoint:**

| Button          | 320px    | 480px    | 768px      | 1024px     | 1440px     | 2560px     | 3840px     |
| --------------- | -------- | -------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Copy            | Icon     | Icon     | Icon+Label | Icon+Label | Icon+Label | Icon+Label | Icon+Label |
| Regenerate      | Icon     | Icon     | Icon+Label | Icon+Label | Icon+Label | Icon+Label | Icon+Label |
| Edit & Retry    | Overflow | Icon     | Icon+Label | Icon+Label | Icon+Label | Icon+Label | Icon+Label |
| Share           | Overflow | Overflow | Icon       | Icon+Label | Icon+Label | Icon+Label | Icon+Label |
| Export          | Overflow | Overflow | Overflow   | Icon       | Icon+Label | Icon+Label | Icon+Label |
| Feedback (👍👎) | Overflow | Icon     | Icon       | Icon+Label | Icon+Label | Icon+Label | Icon+Label |
| Overflow (⋯)    | Visible  | Visible  | Visible    | Hidden     | Hidden     | Hidden     | Hidden     |

```
320px:  [📋] [🔄] [👍👎] [⋯]
480px:  [📋] [🔄] [✏️] [👍👎] [⋯]
768px:  [📋 Copy] [🔄 Retry] [✏️ Edit] [📤] [👍👎] [⋯]
1024px: [📋 Copy] [🔄 Retry] [✏️ Edit & Retry] [📤 Share] [⬇ Export] [👍 👎]
1440px+: Same as 1024px with more spacing
```

**PDF Export Engine:** `html2pdf.js` (client-side, zero server dependency). Renders the current response card (including confidence gauge SVG, source citations, and correction log) to PDF via HTML-to-canvas-to-PDF pipeline. Maximum export size: 10MB. Fallback: browser native `window.print()` with `@media print` stylesheet.

---

### 10.5 — Response Rating / Feedback (P1 Important)

| Property                 | 320px  | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ------------------------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Thumb button size        | 36x36  | 36x36  | 36x36  | 36x36  | 40x40  | 44x44  | 52x52  |
| Thumb icon size          | 16px   | 16px   | 16px   | 16px   | 18px   | 20px   | 24px   |
| Gap between thumbs       | 4px    | 4px    | 8px    | 8px    | 8px    | 12px   | 16px   |
| "Was this helpful?" text | Hidden | Hidden | Hidden | 13px   | 14px   | 16px   | 18px   |
| Flag button              | Hidden | 36x36  | 36x36  | 36x36  | 40x40  | 44x44  | 52x52  |
| Flag dropdown width      | 100%   | 200px  | 240px  | 260px  | 280px  | 320px  | 380px  |
| Feedback textarea height | 80px   | 80px   | 100px  | 100px  | 120px  | 140px  | 160px  |
| Feedback textarea font   | 13px   | 13px   | 14px   | 14px   | 14px   | 16px   | 20px   |

**States:** Default (neutral gray) → Thumbs up (green fill) → Thumbs down (red fill) → Flagged (amber fill)

**Flag Dropdown Options:**

- Hallucination not caught
- False positive correction
- Source attribution wrong
- Response quality poor
- Other (opens textarea)

---

### 10.6 — Share / Deep Link System (P1 Important)

| Property             | 320px               | 480px       | 768px      | 1024px          | 1440px          | 2560px | 3840px |
| -------------------- | ------------------- | ----------- | ---------- | --------------- | --------------- | ------ | ------ |
| Share button         | In overflow         | In overflow | 36x36 icon | 36x36 + "Share" | 40x40 + "Share" | 44x44  | 52x52  |
| Dropdown width       | 100% (bottom sheet) | 200px       | 240px      | 260px           | 280px           | 320px  | 380px  |
| Dropdown item height | 44px                | 44px        | 40px       | 40px            | 40px            | 48px   | 56px   |
| Dropdown item font   | 14px                | 14px        | 14px       | 14px            | 14px            | 16px   | 20px   |
| Dropdown item icon   | 18px                | 18px        | 18px       | 18px            | 18px            | 20px   | 24px   |

**Dropdown Items:**

- Copy Link (📋)
- Export as JSON (⬇)
- Export as PDF (📄)
- Export as CSV (📊)

**URL Routing:**

| Property | Value |
| --- | --- |
| Routing mode | Hash-based (`/#/`) — no server required for local-first SPA |
| Dashboard route | `/#/` |
| Query result route | `/#/query/[id]` |
| Batch route | `/#/batch` |
| Settings route | `/#/settings` |
| Query ID format | UUID v4, generated client-side on submission |
| Browser back/forward | Navigates between viewed query results |
| Invalid deep link | Show "Query not found. It may have been deleted." with [Go to Dashboard] button |
| localStorage key prefix | `guardrail-` |

```
320px (bottom sheet):           1440px (dropdown):
+---------------------------+   +----+--------------------------+
| Share Result               |   | Card  [📋] [🔄] [📤 Share▾]|
|                           |   |       +--------------------+ |
| [📋] Copy Link            |   |       | 📋 Copy Link       | |
| [⬇] Export as JSON        |   |       | ⬇ Export JSON      | |
| [📄] Export as PDF         |   |       | 📄 Export PDF       | |
| [📊] Export as CSV         |   |       | 📊 Export CSV       | |
|                           |   |       +--------------------+ |
| [Cancel]                  |   +------------------------------+
+---------------------------+
```

---

### 10.7 — Command Palette (P1 Important)

Desktop/tablet-with-keyboard only. Triggered by Ctrl+K.

| Property               | 768px               | 1024px | 1440px | 2560px  | 3840px   |
| ---------------------- | ------------------- | ------ | ------ | ------- | -------- |
| Modal width            | min(480px, 90vw)    | 520px  | 560px  | 600px   | 720px    |
| Modal max-height       | 60vh                | 60vh   | 50vh   | 50vh    | 50vh     |
| Modal border-radius    | 12px                | 12px   | 12px   | 16px    | 20px     |
| Search input height    | 48px                | 48px   | 52px   | 56px    | 64px     |
| Search input font      | 16px                | 16px   | 16px   | 18px    | 22px     |
| Result item height     | 40px                | 40px   | 44px   | 48px    | 56px     |
| Result item font       | 14px                | 14px   | 14px   | 16px    | 20px     |
| Shortcut badge font    | 11px                | 11px   | 12px   | 14px    | 16px     |
| Shortcut badge padding | 2px 6px             | same   | same   | 4px 8px | 4px 10px |
| Shortcut badge bg      | --bg-tertiary       | same   | same   | same    | same     |
| Shortcut badge radius  | 4px                 | 4px    | 4px    | 4px     | 6px      |
| Category header font   | 11px/500, uppercase | same   | same   | 13px    | 16px     |
| Category header color  | --text-tertiary     | same   | same   | same    | same     |
| Backdrop               | rgba(0,0,0,0.4)     | same   | same   | same    | same     |
| Shadow                 | elevation-5         | same   | same   | same    | same     |

```
1440px Desktop:
+----------------------------------------------------------------------+
|          ╔══════════════════════════════════════════╗                  |
|          ║ > Search actions...               [Esc] ║                  |
|          ╠══════════════════════════════════════════╣                  |
|          ║ RECENT                                   ║                  |
|          ║   Dashboard                   G then D  ║                  |
|          ║   Last query result           G then L  ║                  |
|          ║ ACTIONS                                  ║                  |
|          ║   Submit New Query            Ctrl+Enter║                  |
|          ║   Export Results              Ctrl+E    ║                  |
|          ║   Toggle Dark Mode            Ctrl+T    ║                  |
|          ╚══════════════════════════════════════════╝                  |
+----------------------------------------------------------------------+
```

**Fuzzy Search Engine:** Fuse.js with `threshold: 0.3`, `keys: ["label", "description", "shortcut"]`, `includeScore: true`. Results sorted by score ascending (best match first). Maximum 10 results displayed. Debounce: 150ms after last keystroke before searching.

---

### 10.8 — Keyboard Shortcuts Overlay (P1 Important)

Triggered by `?` or `Ctrl+/`. Not available on mobile (no physical keyboard).

| Property            | 768px                              | 1024px | 1440px | 2560px | 3840px |
| ------------------- | ---------------------------------- | ------ | ------ | ------ | ------ |
| Modal width         | min(560px, 90vw)                   | 640px  | 720px  | 800px  | 960px  |
| Modal max-height    | 70vh                               | 70vh   | 60vh   | 60vh   | 60vh   |
| Columns             | 1                                  | 2      | 2      | 3      | 4      |
| Column gap          | —                                  | 32px   | 40px   | 48px   | 56px   |
| Section header font | 13px/600, uppercase                | 13px   | 14px   | 16px   | 18px   |
| Key combo font      | 12px mono                          | 12px   | 13px   | 15px   | 18px   |
| Key badge           | 20x20px, radius 4px, --bg-tertiary | same   | 22x22  | 26x26  | 30x30  |
| Description font    | 13px                               | 13px   | 14px   | 16px   | 18px   |
| Row height          | 32px                               | 32px   | 36px   | 40px   | 48px   |

**Shortcut Categories:**

| Shortcut        | Action                 |
| --------------- | ---------------------- |
| `Ctrl+Enter`    | Submit query           |
| `Ctrl+K`        | Command palette        |
| `Ctrl+/` or `?` | Show shortcuts         |
| `Esc`           | Close panel / Cancel   |
| `C`             | Copy current response  |
| `R`             | Regenerate response    |
| `E`             | Edit & resubmit        |
| `J` / `K`       | Next / Previous result |
| `B`             | Bookmark result        |
| `D`             | Toggle inline diff     |
| `T`             | Toggle trace panel     |
| `/`             | Focus search input     |
| `G then D`      | Go to Dashboard        |
| `G then S`      | Go to Settings         |
| `G then H`      | Go to History          |
| `G then B`      | Go to Batch            |

---

### 10.9 — Session History Sidebar (P1 Important)

On 1024px+, the sidebar includes query history. These specs detail the history content inside the sidebar.

| Property                | 1024px                                                     | 1440px              | 2560px | 3840px |
| ----------------------- | ---------------------------------------------------------- | ------------------- | ------ | ------ |
| Sidebar width           | 280px                                                      | 320px               | 400px  | 480px  |
| Search input height     | 36px                                                       | 40px                | 44px   | 52px   |
| Search input font       | 13px                                                       | 14px                | 16px   | 18px   |
| Search input margin     | 12px                                                       | 16px                | 20px   | 24px   |
| New Query button height | 40px                                                       | 40px                | 48px   | 56px   |
| New Query button font   | 14px                                                       | 14px                | 16px   | 18px   |
| History item height     | 52px                                                       | 56px                | 64px   | 72px   |
| History item padding-x  | 12px                                                       | 16px                | 20px   | 24px   |
| Query preview font      | 13px, truncate 1 line                                      | 14px                | 16px   | 18px   |
| Timestamp font          | 11px, --text-tertiary                                      | 12px                | 14px   | 16px   |
| Confidence badge        | 28x18px, 10px font                                         | 32x20               | 36x24  | 44x28  |
| Pin/Bookmark icon       | 14px                                                       | 16px                | 18px   | 20px   |
| Divider (date groups)   | "Today", "Yesterday", "Mar 20" — 11px/500, --text-tertiary | 12px                | 14px   | 16px   |
| Scroll area             | calc(100vh - 280px)                                        | calc(100vh - 300px) | same   | same   |

**Mobile/Tablet (320-768px):** History accessed via hamburger menu → drawer overlay. Drawer width: 85vw (max 360px).

```
1440px Desktop sidebar:
+------------------+
| [+ New Query    ]|  40px
| [🔍 Search...]   |  40px
|                  |
| Today            |  date divider
| +-- [Q] What... |
| |    87% · 2m   |  history item
| +-- [Q] Explain |
| |    94% · 15m  |
| +-- [Q] List the|
| |    76% ★ · 1h |  ★ = bookmarked
|                  |
| Yesterday        |
| +-- [Q] Why do..|
| |    91% · 22h  |
|                  |
| ── Config ──     |
| [Rules]          |
| [Thresholds]     |
| [Models]         |
+------------------+
```

**localStorage Budget:** Maximum 500 session entries, 5MB total budget. When budget is exceeded, oldest entries are evicted (FIFO). Entry size is estimated at `JSON.stringify(entry).length` bytes. A `storage` event listener warns the user at 80% capacity: "History is nearing storage limits. Oldest entries will be removed automatically."

---

### 10.10 — Notification Center (P2 Nice-to-have)

| Property                  | 320px                 | 480px        | 768px    | 1024px   | 1440px   | 2560px   | 3840px   |
| ------------------------- | --------------------- | ------------ | -------- | -------- | -------- | -------- | -------- |
| Bell icon size            | 20px                  | 20px         | 20px     | 20px     | 22px     | 26px     | 30px     |
| Badge (count) size        | 16px circle           | same         | same     | same     | 18px     | 20px     | 24px     |
| Badge font                | 10px/700, white       | same         | same     | same     | 11px     | 13px     | 15px     |
| Panel mode                | Bottom sheet (100%)   | Bottom sheet | Dropdown | Dropdown | Dropdown | Dropdown | Dropdown |
| Panel width               | 100%                  | 100%         | 360px    | 360px    | 400px    | 440px    | 520px    |
| Panel max-height          | 70vh                  | 70vh         | 400px    | 400px    | 480px    | 540px    | 640px    |
| Notification row-h        | 64px                  | 64px         | 60px     | 60px     | 64px     | 72px     | 80px     |
| Notification icon         | 20px                  | 20px         | 20px     | 20px     | 22px     | 26px     | 30px     |
| Notification title font   | 14px/500              | same         | same     | same     | 14px     | 16px     | 20px     |
| Notification detail font  | 12px                  | same         | same     | same     | 13px     | 15px     | 18px     |
| Timestamp font            | 11px, --text-tertiary | same         | same     | same     | 12px     | 14px     | 16px     |
| "Mark all read" font      | 13px, --primary-500   | same         | same     | same     | 14px     | 16px     | 18px     |
| Max visible before scroll | 5                     | 5            | 5        | 5        | 6        | 7        | 8        |

**Notification Types & Icons:**

- Error (circuit breaker, crash): `⚠️` red
- Warning (loop detected, low confidence): `⚡` amber
- Info (query completed): `ℹ️` blue
- Success (high confidence): `✓` green

**Notification Click Behavior:** Clicking a notification navigates to the relevant context (e.g., clicking a "Query completed" notification scrolls to that query's response card and highlights it with a 2s pulse animation). The notification panel closes automatically after navigation. Notifications without a navigation target (e.g., system alerts) display an inline detail expansion instead.

---

### 10.11 — Historical Trend Charts (P1 Important)

| Property              | 320px           | 480px   | 768px    | 1024px   | 1440px   | 2560px   | 3840px   |
| --------------------- | --------------- | ------- | -------- | -------- | -------- | -------- | -------- |
| Section layout        | 1 chart stacked | 1 chart | 2x1 grid | 2x2 grid | 2x2 grid | 2x2 grid | 4x1 grid |
| Chart height          | 180px           | 200px   | 200px    | 220px    | 260px    | 320px    | 380px    |
| Chart width           | 100%            | 100%    | ~50%     | ~50%     | ~50%     | ~50%     | ~25%     |
| Chart padding         | 12px            | 16px    | 16px     | 20px     | 24px     | 32px     | 40px     |
| Axis label font       | 10px            | 10px    | 11px     | 11px     | 12px     | 14px     | 16px     |
| Data point radius     | 3px             | 3px     | 3px      | 4px      | 4px      | 5px      | 6px      |
| Line width            | 2px             | 2px     | 2px      | 2px      | 2.5px    | 3px      | 3px      |
| Time range selector-h | 32px            | 32px    | 36px     | 36px     | 36px     | 44px     | 52px     |
| Time range button-w   | 40px            | 40px    | 48px     | 48px     | 56px     | 64px     | 80px     |
| Time range font       | 12px            | 12px    | 13px     | 13px     | 14px     | 16px     | 18px     |
| Tooltip width         | 140px           | 160px   | 180px    | 200px    | 220px    | 260px    | 300px    |

**4 Charts:**

1. Average Confidence Over Time (line chart, --primary-500)
2. Correction Rate Over Time (line chart, --warning-500)
3. Average Latency P50 (line chart, --info-500)
4. Queries Per Day (bar chart, --primary-300)

**Time Range Options:** `[7d] [30d] [90d] [Custom]`

**Mobile Interaction (320-480px):**

- Touch: Tap a data point to show tooltip; tooltip persists until user taps elsewhere or scrolls
- Time range selector: horizontally scrollable button row (same pattern as settings tabs)
- Chart navigation: vertical stack with scroll; charts are single-column and stacked
- Pinch-to-zoom: not supported (complexity vs value trade-off for local-only app)
- Swipe: not applicable (charts are stacked vertically, standard page scroll applies)

**Desktop Interaction (768px+):**

- Hover: tooltip appears on data point hover with 300ms delay (per Sprint 4 transition spec)
- Click-drag: brush-select a time range and zoom in (1440px+ only)
- Double-click: reset zoom to default range
- Keyboard: Tab to chart, arrow keys to navigate data points, Enter to show tooltip

---

### 10.12 — Batch Query Processing (P1 Important)

Full-page view accessible from navigation ("Batch" tab).

| Property            | 320px      | 480px      | 768px    | 1024px | 1440px | 2560px | 3840px |
| ------------------- | ---------- | ---------- | -------- | ------ | ------ | ------ | ------ |
| Textarea height     | 120px      | 120px      | 160px    | 160px  | 200px  | 240px  | 280px  |
| Textarea font       | 13px mono  | same       | 14px     | 14px   | 14px   | 16px   | 20px   |
| Upload btn height   | 44px       | 44px       | 40px     | 40px   | 40px   | 48px   | 56px   |
| Results layout      | Card stack | Card stack | Table    | Table  | Table  | Table  | Table  |
| Table row height    | —          | —          | 44px     | 44px   | 48px   | 56px   | 64px   |
| Table header font   | —          | —          | 13px/600 | 13px   | 14px   | 16px   | 18px   |
| Table body font     | —          | —          | 13px     | 14px   | 14px   | 16px   | 20px   |
| Status badge        | 56x22px    | same       | same     | same   | 64x24  | 72x28  | 84x32  |
| Progress bar height | 4px        | 4px        | 4px      | 4px    | 4px    | 6px    | 8px    |
| Batch actions bar-h | 48px       | 48px       | 48px     | 48px   | 52px   | 56px   | 64px   |

**Table Columns by Breakpoint:**

| Column      | 320px       | 480px       | 768px  | 1024px | 1440px | 2560px | 3840px |
| ----------- | ----------- | ----------- | ------ | ------ | ------ | ------ | ------ |
| #           | Card        | Card        | 40px   | 40px   | 48px   | 56px   | 64px   |
| Query       | Card title  | Card title  | flex   | flex   | flex   | flex   | flex   |
| Status      | Badge       | Badge       | 80px   | 80px   | 100px  | 120px  | 140px  |
| Score       | In badge    | In badge    | 60px   | 60px   | 72px   | 80px   | 100px  |
| Corrections | Hidden      | Hidden      | Hidden | 80px   | 80px   | 100px  | 120px  |
| Latency     | Hidden      | Hidden      | Hidden | Hidden | 80px   | 100px  | 120px  |
| Actions     | Card footer | Card footer | 48px   | 48px   | 60px   | 72px   | 80px   |

---

### 10.13 — Onboarding / First-Run Tutorial (P2 Nice-to-have)

| Property             | 320px                                          | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| -------------------- | ---------------------------------------------- | ----- | ----- | ------ | ------ | ------ | ------ |
| Overlay card width   | 90vw                                           | 90vw  | 480px | 520px  | 560px  | 640px  | 760px  |
| Overlay card padding | 20px                                           | 24px  | 32px  | 32px   | 40px   | 48px   | 56px   |
| Overlay card radius  | 12px                                           | 12px  | 16px  | 16px   | 16px   | 20px   | 24px   |
| Title font           | 18px/600                                       | 20px  | 22px  | 24px   | 24px   | 28px   | 34px   |
| Body font            | 14px                                           | 14px  | 15px  | 16px   | 16px   | 18px   | 22px   |
| Step indicator       | 6px dots                                       | 6px   | 8px   | 8px    | 8px    | 10px   | 12px   |
| Step indicator gap   | 8px                                            | 8px   | 8px   | 10px   | 10px   | 12px   | 14px   |
| Skip button          | 13px, --text-tertiary                          | same  | same  | same   | 14px   | 16px   | 18px   |
| Next button height   | 44px                                           | 44px  | 44px  | 44px   | 44px   | 52px   | 56px   |
| Next button width    | 100%                                           | 100%  | 120px | 120px  | 130px  | 150px  | 180px  |
| Highlight overlay    | 4px border, --primary-500, 8px offset, pulsing | same  | same  | same   | same   | same   | same   |

**Onboarding Steps (4 total):**

1. "Welcome! This is your AI Hallucination Guardrail" → highlights the query input
2. "Ask any question — we'll check for hallucinations" → highlights submit button
3. "Every answer gets a confidence score" → highlights confidence gauge area
4. "Watch agents work in real-time" → highlights live trace panel

**Onboarding Illustration:** A custom SVG composition featuring three overlapping elements: (1) a magnifying glass (representing inspection/validation), (2) a checkmark inside a shield (representing trust/guardrail), and (3) a circular arrow (representing the correction loop). Colors use `--color-primary-500` and `--color-success-500` tokens. The illustration animates on first load: magnifying glass slides in from left (300ms), shield fades in at center (300ms, 150ms delay), arrow draws clockwise (500ms, 300ms delay). Total animation: 800ms. `prefers-reduced-motion`: static composition, no animation.

---

### 10.14 — Dark Mode Toggle (P1 Important)

Located in the header bar. Already sized in header spec (Section 1), but needs internal detail.

| Property              | 320px          | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| --------------------- | -------------- | ----- | ----- | ------ | ------ | ------ | ------ |
| Toggle container      | 36x36          | 36x36 | 36x36 | 36x36  | 40x40  | 48x48  | 56x56  |
| Icon (sun/moon)       | 18px           | 18px  | 18px  | 18px   | 20px   | 24px   | 28px   |
| Or: pill toggle width | —              | —     | —     | 52px   | 52px   | 64px   | 76px   |
| Pill toggle height    | —              | —     | —     | 28px   | 28px   | 32px   | 38px   |
| Pill thumb diameter   | —              | —     | —     | 22px   | 22px   | 26px   | 32px   |
| Transition            | 200ms ease-out | same  | same  | same   | same   | same   | same   |

**Mobile (320-768):** Simple icon button. Tap toggles between ☀️ (light) and 🌙 (dark).
**Desktop (1024+):** Can use a pill toggle with sun on left, moon on right, sliding thumb.

**Dark Mode Transition:** All theme-dependent CSS custom properties transition with `200ms ease-out`. Applied via `*, *::before, *::after { transition: background-color 200ms ease-out, color 200ms ease-out, border-color 200ms ease-out, box-shadow 200ms ease-out; }` on the `[data-theme]` attribute change. Exception: SVG fill/stroke transitions use `150ms ease-out` for snappier icon updates. Images and media are excluded from transition to prevent flash.

---

### 10.15 — Updated Full-Page Wireframes (With All Missing Features)

Now that the missing features are specified, here are the updated full-page layouts showing where everything fits.

#### 320px Mobile — Updated

````
+-------------------------------+ 0px
|  [☰]  Guardrail AI   [🔔][🌙]| 56px header (fixed)
+-------------------------------+ 56px
| (ONBOARDING OVERLAY on 1st visit)
|                               |
| +---------------------------+ |
| | Ask a question...         | | Query Input: auto-expand
| |                 12/4096   | | Token counter
| | [■ Stop]  [Submit ➤]     | | 44px buttons
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | ⚠ CIRCUIT BREAKER BANNER  | | (if active)
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | RESPONSE CARD              | |
| | ## Heading renders         | | Markdown rendered
| | Body text with **bold**    | |
| | ```code```          [copy] | | Code + copy btn
| | > blockquote               | |
| |                            | |
| | [87%] [📋][🔄][👍👎][⋯]  | | Action bar
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | SOURCE ATTRIBUTION         | |
| | [▶ Source 1: arxiv...]     | |
| | [▶ Source 2: github...]    | |
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | CORRECTION LOG             | |
| | Round 1: 42% → 78% ✓     | |
| +---------------------------+ |
| ⬇ 12px gap                    |
| +---------------------------+ |
| | LIVE TRACE [▶ Expand]     | | Collapsed: 48px
| +---------------------------+ |
+-------------------------------+
````

#### 1440px Desktop — Updated

````
+--------------------------------------------------------------------------------+ 0px
| [Logo]  Guardrail AI   [Search] [Batch] [Docs] [Settings] [🔔(3)] [🌙] [👤]  | 64px
+--------------------------------------------------------------------------------+
| +----------+ +----------------------------------------------------------------+ |
| | SIDEBAR  | | MAIN CONTENT                                                  | |
| | w: 320px | |                                                                | |
| |          | | +------------------------------------------------------------+ | |
| | [+ New Q]| | | Ask a question or paste text to verify...                   | | |
| | [🔍 Srch]| | |                                                89/4096 tok | | |
| |          | | | [📎 Upload]    [Ctrl+Enter]   [■ Stop]  [Submit ➤]         | | |
| | Today    | | +------------------------------------------------------------+ | |
| | [Q1] 87% | | ⬇ 24px                                                        | |
| | [Q2] 94% | | +------------------+ +------------------+ +----------------+ | |
| | [Q3] 76%★| | | RESPONSE CARD    | | CONFIDENCE       | | LIVE TRACE     | | |
| |          | | | ## Markdown       | | GAUGE            | | (sidebar mode) | | |
| | Yesterday| | | Body + **bold**  | | Radial: 160px    | | Node graph     | | |
| | [Q4] 91% | | | ```code``` [copy]| | Score: 48px      | |                | | |
| |          | | | > blockquote     | | Breakdown table  | | [●] Agent1 ✓  | | |
| | ── Conf ─| | |                  | |                  | | [●] Agent2 ✓  | | |
| | [Rules]  | | | Action Bar:      | |                  | | [●] Agent3 ◌  | | |
| | [Thresh] | | | [📋 Copy] [🔄]  | |                  | |               | | |
| | [Models] | | | [✏️ Edit&Retry]  | | Was this helpful?| | Total: 4.2s   | | |
| |          | | | [📤 Share▾]      | | [👍 Yes] [👎 No] | |               | | |
| | ── Stats | | | [⬇ Export▾]      | | [🚩 Flag]        | |               | | |
| | Today: 12| | +------------------+ +------------------+ +----------------+ | |
| |          | | ⬇ 24px                                                        | |
| |          | | +------------------------------+ +--------------------------+ | |
| |          | | | SOURCE ATTRIBUTION           | | CORRECTION LOG           | | |
| |          | | | [▼ arxiv:2401.1234 — 0.94]   | | Attempt 1: 42%           | | |
| |          | | | [▶ github.com/... — 0.87]    | | Attempt 2: 78% ✓        | | |
| |          | | +------------------------------+ +--------------------------+ | |
| |          | | ⬇ 24px                                                        | |
| |          | | TREND CHARTS (if enabled)                                     | |
| |          | | +-------------------+ +-------------------+                  | |
| |          | | | Avg Confidence    | | Correction Rate   |                  | |
| |          | | | [chart 260px]     | | [chart 260px]     |                  | |
| |          | | +-------------------+ +-------------------+                  | |
| +----------+ +----------------------------------------------------------------+ |
+--------------------------------------------------------------------------------+
````

---

## 11. Additional Missing Feature Specifications

> The following sections close every remaining gap identified in the user critique, Sprint 4, and Sprint 5 acceptance criteria that Section 10 did not cover. Each feature includes a responsive box-model table, ASCII wireframes at key breakpoints, interaction notes, and accessibility requirements.

---

### 11.1 — Progress Bar Component (P0 Critical)

Sprint 4 (4.1.7) defines the estimation algorithm and visual properties but no responsive box-model table or wireframes exist in the skeleton spec.

| Property              | 320px                      | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| --------------------- | -------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Height (resting)      | 3px                        | 3px    | 3px    | 3px    | 3px    | 4px    | 5px    |
| Height (hover)        | 4px                        | 4px    | 4px    | 4px    | 4px    | 5px    | 6px    |
| Position              | Fixed, top of content area | same   | same   | same   | same   | same   | same   |
| Width                 | 100%                       | 100%   | 100%   | 100%   | 100%   | 100%   | 100%   |
| z-index               | 95                         | 95     | 95     | 95     | 95     | 95     | 95     |
| Track color (light)   | --color-neutral-200        | same   | same   | same   | same   | same   | same   |
| Track color (dark)    | --color-neutral-700        | same   | same   | same   | same   | same   | same   |
| Fill color            | --color-primary-500        | same   | same   | same   | same   | same   | same   |
| Completion fill color | --color-success-500        | same   | same   | same   | same   | same   | same   |
| Fill transition       | width 300ms ease-out       | same   | same   | same   | same   | same   | same   |
| Border-radius         | 0                          | 0      | 0      | 0      | 0      | 0      | 0      |

**ETA Tooltip (appears on hover):**

| Property       | 320px             | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| -------------- | ----------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Display        | Hidden (no hover) | Hidden | Visible | Visible | Visible | Visible | Visible |
| Width          | —                 | —      | 120px  | 140px  | 140px  | 160px  | 200px  |
| Height         | —                 | —      | 28px   | 30px   | 30px   | 36px   | 44px   |
| Font-size      | —                 | —      | 12px   | 12px   | 13px   | 15px   | 18px   |
| Background     | —                 | —      | --color-bg-secondary | same | same | same | same |
| Border-radius  | —                 | —      | 4px    | 4px    | 4px    | 6px    | 8px    |
| Padding        | —                 | —      | 4px 8px | 4px 8px | 6px 10px | 8px 12px | 8px 16px |
| Shadow         | —                 | —      | elevation-4 | same | same | same | same |
| Position       | —                 | —      | Centered below bar, follows cursor x | same | same | same | same |
| Text template  | —                 | —      | "~Ns remaining" | same | same | same | same |

**Wireframes:**

```
768px Tablet (hover state):
+---------------------------------------------------+
| [████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 42%  | 3px bar, full width
|                    ↓                               |
|              [~4s remaining]                       | tooltip, 120px
+---------------------------------------------------+

1440px Desktop (hover state):
+--------------------------------------------------------------------------------+
| [█████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 65%   | 3px bar
|                                        ↓                                        |
|                                  [~2s remaining]                                | tooltip, 140px
+--------------------------------------------------------------------------------+
```

**States:**

- **Determinate (0-99%):** Solid fill, --primary-500, advances monotonically
- **Indeterminate (>1.5x expected time):** Animated stripe pattern, no percentage
- **Complete (100%):** Fill transitions to --success-500, holds 300ms, then fades out 200ms
- **Error:** Fill transitions to --error-500, stays visible until dismissed

**Accessibility:**

- `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`
- `aria-label="Query processing progress"`
- Indeterminate state: remove `aria-valuenow`, add `aria-label="Processing, please wait"`

**`prefers-reduced-motion` Override:** When reduced motion is enabled, the indeterminate progress bar replaces the sliding animation with a static dashed pattern: `background: repeating-linear-gradient(90deg, var(--color-primary-500) 0px, var(--color-primary-500) 8px, transparent 8px, transparent 16px)`. The determinate progress bar still updates its width but without the `transition` property. The completion state (100%) uses a static green fill with no fade-out animation.

---

### 11.2 — Processing Status Bar (P0 Critical)

During query processing, a status bar appears below the progress bar showing the current agent and count. The **primary stop button is in the Query Input area (10.1)**, which transforms from Submit to Stop during processing. This section specifies the **status text and secondary cancel link** that supplements it.

**Design Decision:** Only ONE prominent stop button exists (in the query input area, per 10.1). The status bar here shows a subtle "Cancel" text link, not a second red button, to avoid duplicate-action confusion.

| Property            | 320px                       | 480px        | 768px             | 1024px    | 1440px    | 2560px    | 3840px    |
| ------------------- | --------------------------- | ------------ | ----------------- | --------- | --------- | --------- | --------- |
| Container width     | 100%                        | 100%         | 100%              | 100%      | 100%      | 100%      | 100%      |
| Container height    | 56px                        | 56px         | 52px              | 52px      | 56px      | 64px      | 72px      |
| Container padding-x | 16px                        | 16px         | 24px              | 32px      | 40px      | 64px      | 96px      |
| Container position  | Below progress bar, sticky  | same         | same              | same      | same      | same      | same      |
| Container bg        | --color-bg-primary          | same         | same              | same      | same      | same      | same      |
| Status text font    | 13px                        | 13px         | 14px              | 14px      | 15px      | 17px      | 20px      |
| Status text color   | --text-secondary            | same         | same              | same      | same      | same      | same      |
| Cancel link font    | 13px/500                    | 13px         | 14px              | 14px      | 14px      | 16px      | 18px      |
| Cancel link color   | --color-error-500           | same         | same              | same      | same      | same      | same      |
| Cancel link hover   | --color-error-700, underline | same        | same              | same      | same      | same      | same      |
| Cancel link label   | "Cancel"                    | "Cancel"     | "Cancel"          | "Cancel"  | "Cancel"  | "Cancel"  | "Cancel"  |
| Layout              | Status stacked, cancel below | same        | Status left, cancel right (inline) | same | same | same | same |

**Wireframes:**

```
320px Mobile:
+-------------------------------+
| [████████████░░░░░░░░] 42%    | progress bar
+-------------------------------+
| Processing query...           |
| Agent 2 of 5 running          | status text
| Cancel                        | text link, --error-500
+-------------------------------+

768px Tablet:
+---------------------------------------------------+
| [████████████████░░░░░░░░░░░░░░] 42%              | progress bar
+---------------------------------------------------+
| Processing query... (2 of 5 agents)       Cancel  | inline text link
+---------------------------------------------------+

1440px Desktop:
+--------------------------------------------------------------------------------+
| [█████████████████████████████░░░░░░░░░░░░░░░░░] 65%                           |
+--------------------------------------------------------------------------------+
| Processing "What causes inflation..." (3 of 5 agents)              Cancel     |
+--------------------------------------------------------------------------------+

Note: The primary Stop button is in the Query Input area (10.1).
The "Cancel" link here is a secondary affordance for users whose attention
is on the progress area rather than the input area.
```

**Interaction Flow:**

1. After query submission, the status container appears below the progress bar
2. Status text shows current agent name and count (e.g., "Agent 2 of 5 running")
3. Clicking Stop sends a WebSocket cancellation signal
4. Pipeline halts; completed agent results render normally, in-progress agents show "Cancelled" badge
5. Progress bar stops and transitions to neutral (--color-neutral-400)
6. Toast: "Generation stopped. Partial results shown."
7. Status container collapses with 200ms ease-out animation

**Accessibility:**

- Stop button: `aria-label="Stop generating response"`
- Status text: `role="status"`, `aria-live="polite"`
- Keyboard: Esc triggers stop when no modal/dropdown is open
- Screen reader: announces "Generation stopped" via `aria-live="assertive"` after cancellation

---

### 11.3 — Settings Panel (P1 Important)

Full settings page accessible from sidebar navigation or avatar menu. User-critique section 4.14 defines the wireframes; this section adds the responsive box-model table.

**Page Layout:**

| Property               | 320px              | 480px       | 768px        | 1024px            | 1440px            | 2560px            | 3840px            |
| ---------------------- | ------------------ | ----------- | ------------ | ----------------- | ----------------- | ----------------- | ----------------- |
| Layout mode            | Single column      | Single col  | Single col   | Sidebar + content | Sidebar + content | Sidebar + content | Sidebar + content |
| Settings sidebar width | 0 (hidden)         | 0           | 0            | 200px             | 220px             | 260px             | 320px             |
| Settings sidebar bg    | —                  | —           | —            | --color-bg-secondary | same           | same              | same              |
| Content area width     | 100%               | 100%        | 100%         | calc(100% - 200px) | calc(100% - 220px) | calc(100% - 260px) | calc(100% - 320px) |
| Content max-width      | 100%               | 100%        | 100%         | 640px             | 720px             | 800px             | 960px             |
| Content padding        | 16px               | 16px        | 24px         | 32px              | 40px              | 48px              | 64px              |
| Section gap            | 24px               | 24px        | 32px         | 32px              | 40px              | 48px              | 56px              |

**Settings Sidebar (1024px+):**

| Property             | 1024px                     | 1440px | 2560px | 3840px |
| -------------------- | -------------------------- | ------ | ------ | ------ |
| Nav item height      | 40px                       | 40px   | 48px   | 56px   |
| Nav item padding-x   | 16px                       | 16px   | 20px   | 24px   |
| Nav item font        | 14px                       | 14px   | 16px   | 18px   |
| Nav item radius      | 6px                        | 6px    | 8px    | 10px   |
| Active item bg       | --color-bg-tertiary        | same   | same   | same   |
| Active item font-wt  | 600                        | 600    | 600    | 600    |
| Section divider      | 1px solid --border-subtle  | same   | same   | same   |
| Divider margin-y     | 8px                        | 8px    | 12px   | 16px   |

**Mobile (320-768px) — Tab Navigation:**

| Property        | 320px                    | 480px  | 768px  |
| --------------- | ------------------------ | ------ | ------ |
| Tab bar height  | 44px                     | 44px   | 48px   |
| Tab bar padding | 0 8px                    | 0 12px | 0 16px |
| Tab font-size   | 13px                     | 13px   | 14px   |
| Tab min-width   | 64px                     | 72px   | 80px   |
| Tab gap         | 0 (scrollable row)       | 0      | 4px    |
| Active tab      | Bottom border 2px, --primary-500 | same | same |
| Tab overflow     | Horizontal scroll        | same   | same   |

**Setting Row (individual setting item):**

| Property               | 320px                     | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ---------------------- | ------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Row min-height         | 52px                      | 52px   | 48px   | 48px   | 52px   | 56px   | 64px   |
| Row padding-y          | 12px                      | 12px   | 10px   | 10px   | 12px   | 14px   | 16px   |
| Label font             | 14px/500                  | 14px   | 14px   | 14px   | 15px   | 17px   | 20px   |
| Description font       | 12px, --text-tertiary     | 12px   | 13px   | 13px   | 13px   | 15px   | 18px   |
| Toggle switch width    | 44px                      | 44px   | 44px   | 44px   | 48px   | 52px   | 60px   |
| Toggle switch height   | 24px                      | 24px   | 24px   | 24px   | 26px   | 28px   | 32px   |
| Toggle thumb diameter  | 20px                      | 20px   | 20px   | 20px   | 22px   | 24px   | 28px   |
| Dropdown min-width     | 120px                     | 140px  | 160px  | 160px  | 180px  | 200px  | 240px  |
| Dropdown height        | 36px                      | 36px   | 36px   | 36px   | 40px   | 44px   | 52px   |
| Number input width     | 80px                      | 80px   | 80px   | 80px   | 90px   | 100px  | 120px  |
| Segment button height  | 36px                      | 36px   | 36px   | 36px   | 40px   | 44px   | 52px   |
| Segment button font    | 13px                      | 13px   | 13px   | 13px   | 14px   | 16px   | 18px   |
| Layout                 | Label above, control below | same  | Label left, control right | same | same | same | same |
| Row border-bottom      | 1px solid --border-subtle | same   | same   | same   | same   | same   | same   |

**Text Size Slider:**

| Property        | 320px                     | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| --------------- | ------------------------- | ----- | ----- | ------ | ------ | ------ | ------ |
| Slider width    | 100%                      | 100%  | 200px | 200px  | 240px  | 280px  | 340px  |
| Slider height   | 4px (track)               | 4px   | 4px   | 4px    | 5px    | 6px    | 8px    |
| Thumb diameter  | 20px                      | 20px  | 20px  | 20px   | 22px   | 24px   | 28px   |
| A- button       | 28px, 13px font           | same  | same  | same   | 32px, 14px | 36px, 16px | 44px, 18px |
| A+ button       | 28px, 17px font           | same  | same  | same   | 32px, 18px | 36px, 20px | 44px, 24px |
| Track radius    | 2px                       | 2px   | 2px   | 2px    | 3px    | 3px    | 4px    |
| Fill color      | --primary-500             | same  | same  | same   | same   | same   | same   |

**Wireframes:**

```
320px Mobile:
+-------------------------------+
| < Back     Settings           |
+-------------------------------+
| [Appearance|Notifs|Query|Data]| ← scrollable tabs, 44px
+-------------------------------+
|                               |
| Theme                         |
| [Light] [Dark] [System]     | ← segment buttons
|                               |
| Density                       |
| [Compact] [Comfortable]     |
|                               |
| Text Size                     |
| A- [═══════|═══] A+         | ← slider
|                               |
| Animations                    |
| Enable animations    [toggle]|
|                               |
| High Contrast                 |
| Enable high contrast [toggle]|
+-------------------------------+

1440px Desktop:
+--------------------------------------------------------------------------------+
| Settings                                                                        |
|                                                                                 |
| +----------+ +----------------------------------------------------------------+|
| | SIDEBAR  | | Appearance                                                     ||
| |          | |                                                                 ||
| |[Appear.] | | Theme         [Light] [Dark] [System]                          ||
| | Notifs   | | Density       [Compact] [Comfortable] [Spacious]               ||
| | Query    | | Text Size     A- [═══════════|════] A+                         ||
| | Data     | | Animations    Enable animations             [toggle]           ||
| | Shortcuts| | High Contrast Enable high contrast mode     [toggle]           ||
| | About    | |                                                                 ||
| |          | | ─────────────────────────────────────────────────               ||
| |          | | [Reset to Defaults]                                             ||
| +----------+ +----------------------------------------------------------------+|
+--------------------------------------------------------------------------------+
```

**Settings Categories:**

| Category    | Settings Included |
| ----------- | ----------------- |
| Appearance  | Theme (Light/Dark/System — **default: System**, fallback: Light if `prefers-color-scheme` unsupported), Density (Compact/Comfortable/Spacious — default: Comfortable), Text Size (slider), Animations (toggle, default: on), High Contrast (toggle, default: off) |
| Notifications | Error alerts (toggle, default: on), Query completions (toggle, default: off), Circuit breaker (toggle, default: on), Loop detection (toggle, default: on) |
| Query Defaults | Max tokens (number input, default 4096), Max correction rounds (number input, default 3), Auto-retry on timeout (toggle, default: off), Confidence thresholds — Low: (number input, default 50%), High: (number input, default 80%) |
| Data        | Export all data (button), Clear query history (button with confirmation dialog per 11.22), Data retention period (dropdown: 7d/30d/90d/Forever — default: Forever) |
| Shortcuts   | Link to keyboard shortcuts overlay (Section 10.8) |
| About       | Version number, build info, "Show Tutorial" link |

**Interaction Flow:**

1. Changes apply immediately — no "Save" button needed
2. All settings persisted in localStorage under key `guardrail-settings` (JSON object)
3. "Reset to Defaults" per section with confirmation dialog (per 11.22)
4. Settings page uses same header/sidebar as main dashboard
5. Theme "System" monitors `prefers-color-scheme` media query in real time (no reload needed)

**Accessibility:**

- All toggles: `role="switch"`, `aria-checked`
- All dropdowns: `role="listbox"`, `aria-expanded`
- Segment buttons: `role="radiogroup"` with `role="radio"` items
- Slider: `role="slider"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, `aria-label="Text size"`
- Section navigation (mobile tabs): `role="tablist"` with `role="tab"` items
- Section navigation (desktop sidebar): `role="navigation"`, `aria-current="page"` on active item

---

### 11.4 — Regenerate & Compare View (P1 Important)

User-critique section 4.12 defines the action buttons. This section specifies the **"Compare with Previous Run"** side-by-side layout that has no skeleton spec.

**Compare View Layout:**

| Property              | 320px              | 480px              | 768px          | 1024px         | 1440px         | 2560px         | 3840px         |
| --------------------- | ------------------ | ------------------ | -------------- | -------------- | -------------- | -------------- | -------------- |
| Layout mode           | Stacked (tab swap) | Stacked (tab swap) | Side-by-side   | Side-by-side   | Side-by-side   | Side-by-side   | Side-by-side   |
| Panel width (each)    | 100%               | 100%               | ~50%           | ~50%           | ~50%           | ~50%           | ~50%           |
| Panel divider         | Tab bar            | Tab bar            | 1px vertical   | 1px vertical   | 1px vertical   | 1.5px vertical | 2px vertical   |
| Divider color         | —                  | —                  | --border-default | same         | same           | same           | same           |
| Panel padding         | 12px               | 16px               | 16px           | 20px           | 24px           | 32px           | 40px           |
| Panel label height    | 0 (in tab)         | 0                  | 32px           | 36px           | 36px           | 44px           | 52px           |
| Panel label font      | —                  | —                  | 13px/600       | 14px/600       | 14px/600       | 16px/600       | 18px/600       |
| Panel label bg        | —                  | —                  | --bg-secondary | same           | same           | same           | same           |
| Tab bar height        | 40px               | 40px               | Hidden         | Hidden         | Hidden         | Hidden         | Hidden         |
| Tab font              | 14px               | 14px               | —              | —              | —              | —              | —              |
| Diff highlight bg     | --color-error-50 (removed) / --color-success-50 (added) | same | same | same | same | same | same |
| Max height            | 60vh               | 60vh               | 60vh           | 70vh           | 70vh           | 70vh           | 70vh           |
| Close button size     | 36x36              | 36x36              | 36x36          | 36x36          | 40x40          | 44x44          | 52x52          |
| Container mode        | Full-screen modal  | Full-screen modal  | Inline panel   | Inline panel   | Inline panel   | Inline panel   | Inline panel   |
| Container radius      | 0                  | 0                  | 12px           | 12px           | 12px           | 16px           | 20px           |
| Container shadow      | none               | none               | elevation-3    | elevation-3    | elevation-3    | elevation-3    | elevation-3    |

**Wireframes:**

```
320px Mobile (tab-swapped):
+-------------------------------+
| Compare Runs           [X]   |
| [◉ Original] [○ Regenerated]| ← tab bar, 40px
+-------------------------------+
|                               |
| Original Response             |
|                               |
| Text with differences         |
| highlighted in red for        |
| removed content...            |
|                               |
| Confidence: 42%               |
| Corrections: 3                |
+-------------------------------+

768px Tablet (side-by-side):
+---------------------------------------------------+
| Compare Runs                               [X]    |
+---------------------------------------------------+
| Original            ┃ Regenerated                  |
| ────────────────────╂─────────────────────────     |
| Text with red       ┃ Text with green              |
| highlights for      ┃ highlights for               |
| removed content     ┃ added content                |
|                     ┃                              |
| Confidence: 42%     ┃ Confidence: 78%              |
| Corrections: 3      ┃ Corrections: 1               |
+---------------------------------------------------+

1440px Desktop (side-by-side):
+--------------------------------------------------------------------------------+
| Compare Runs                                                        [X Close]  |
+--------------------------------------------------------------------------------+
| Original Response                    ┃ Regenerated Response                     |
| ─────────────────────────────────────╂──────────────────────────────────────    |
|                                      ┃                                          |
| Response text with inline diff       ┃ Response text with inline diff           |
| markers. Removed words in red bg.    ┃ markers. Added words in green bg.        |
|                                      ┃                                          |
| Confidence: 42%                      ┃ Confidence: 78%                          |
| Corrections: 3                       ┃ Corrections: 1                           |
| Latency: 3.2s                        ┃ Latency: 2.8s                            |
+--------------------------------------------------------------------------------+
```

**Accessibility:**

- Compare container: `role="region"`, `aria-label="Compare response runs"`
- Each panel: `aria-label="Original response"` / `"Regenerated response"`
- Mobile tabs: `role="tablist"` with `role="tabpanel"` for content
- Diff highlights: not color-only — strikethrough for removed, underline for added
- Close button: `aria-label="Close comparison view"`

---

### 11.5 — Glossary / Contextual Help Tooltips (P1 Important)

User-critique Stage 2 identifies that technical terms like "Confidence Score," "Circuit Breaker," "Agent Pipeline" need in-context explanation for first-time users.

**Help Icon (placed next to technical terms):**

| Property         | 320px                    | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ---------------- | ------------------------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Icon size        | 14px                     | 14px   | 14px   | 16px   | 16px   | 18px   | 22px   |
| Icon color       | --text-tertiary          | same   | same   | same   | same   | same   | same   |
| Icon hover color | --primary-500            | same   | same   | same   | same   | same   | same   |
| Touch target     | 32x32px                  | 32x32  | 28x28  | 24x24  | 24x24  | 28x28  | 32x32  |
| Cursor           | help                     | same   | same   | same   | same   | same   | same   |
| Gap from label   | 4px                      | 4px    | 4px    | 4px    | 6px    | 6px    | 8px    |
| Icon shape       | Circle with "?" (outlined) | same | same   | same   | same   | same   | same   |

**Help Popover (opens on click mobile, hover desktop):**

| Property          | 320px                       | 480px       | 768px  | 1024px | 1440px | 2560px | 3840px |
| ----------------- | --------------------------- | ----------- | ------ | ------ | ------ | ------ | ------ |
| Trigger           | Tap (toggle)                | Tap         | Hover  | Hover  | Hover  | Hover  | Hover  |
| Width             | calc(100vw - 32px)          | 280px       | 300px  | 320px  | 340px  | 400px  | 480px  |
| Max-height        | 200px (scroll)              | 200px       | 240px  | 240px  | 260px  | 300px  | 360px  |
| Padding           | 12px                        | 12px        | 14px   | 16px   | 16px   | 20px   | 24px   |
| Border-radius     | 8px                         | 8px         | 8px    | 8px    | 10px   | 12px   | 16px   |
| Shadow            | elevation-4                 | elevation-4 | same   | same   | same   | same   | same   |
| Background        | --color-bg-primary          | same        | same   | same   | same   | same   | same   |
| Border            | 1px solid --border-default  | same        | same   | same   | same   | same   | same   |
| Title font        | 14px/600                    | 14px        | 14px   | 15px   | 15px   | 17px   | 20px   |
| Body font         | 13px/400                    | 13px        | 13px   | 14px   | 14px   | 16px   | 20px   |
| Body color        | --text-secondary            | same        | same   | same   | same   | same   | same   |
| "Learn more" font | 13px/500, --primary-500     | same        | same   | 14px   | 14px   | 16px   | 18px   |
| Arrow size        | 8px                         | 8px         | 8px    | 8px    | 8px    | 10px   | 12px   |
| Dismiss           | Tap outside                 | Tap outside | Mouse out (300ms delay) | same | same | same | same |
| Position          | Bottom-center, above if clipped | same   | Auto (prefer bottom) | same | same | same | same |

**Wireframes:**

```
1440px Desktop:
+----------------------------------------------------------------------+
| Confidence Score: 87%  [?]                                           |
|                         |                                            |
|                         v                                            |
|  +-------------------------------------------------------+          |
|  | What is a Confidence Score?                            |          |
|  |                                                       |          |
|  | A number from 0-100% showing how certain the system   |          |
|  | is that its answer is factually correct. Higher is     |          |
|  | better. Scores below 50% should be manually verified.  |          |
|  |                                                       |          |
|  | [Learn more...]                                       |          |
|  +-------------------------------------------------------+          |
+----------------------------------------------------------------------+
```

**Glossary Terms:**

| Term | Plain Language Alias | Definition |
| --- | --- | --- |
| Confidence Score | Trust Level | A 0-100% rating of how certain the system is that its answer is factually correct |
| Circuit Breaker | Safety Check | An automatic system that blocks any requests to external paid APIs, enforcing $0.00 cost |
| Agent Pipeline | Processing Steps | The sequence of AI agents that process your query: generate, evaluate, correct |
| Hallucination | Made-Up Information | When an AI generates information that sounds plausible but is factually incorrect |
| Critic Agent | Fact Checker | The AI agent that evaluates each claim in a response for accuracy |
| NF4 Quantization | Compressed Model | A technique that makes the AI model smaller and faster while keeping quality high |
| Live Trace | Activity Monitor | A real-time view of what each processing step is doing as your query is handled |
| Source Attribution | Citation | A link to the original source document that supports a specific claim |

**Accessibility:**

- Icon: `aria-label="Help: [term name]"`, `aria-haspopup="true"`, `aria-expanded="false/true"`
- Popover: `role="tooltip"`, `aria-describedby` linking icon to popover
- Keyboard: Enter/Space to open, Esc to close
- Focus trapped in popover on mobile (tap-triggered); not trapped on desktop (hover)

---

### 11.6 — Empty State with Sample Queries (P1 Important)

Sprint 5 DC-05 specifies "No queries yet" text. User-critique Stage 1 recommends clickable sample queries. This section adds the complete responsive spec.

| Property                 | 320px               | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ------------------------ | -------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Container max-width      | 100%                | 100%   | 480px  | 520px  | 560px  | 640px  | 760px  |
| Container align          | Center               | Center | Center | Center | Center | Center | Center |
| Container padding        | 32px 16px            | 32px   | 48px   | 56px   | 64px   | 80px   | 96px   |
| Illustration size        | 120x120px            | 140x140 | 160x160 | 180x180 | 200x200 | 240x240 | 280x280 |
| Title font               | 18px/600             | 20px   | 22px   | 24px   | 28px   | 34px   | 40px   |
| Title color              | --text-primary       | same   | same   | same   | same   | same   | same   |
| Title margin-top         | 20px                 | 24px   | 28px   | 32px   | 32px   | 40px   | 48px   |
| Description font         | 14px                 | 14px   | 15px   | 16px   | 16px   | 18px   | 22px   |
| Description color        | --text-secondary     | same   | same   | same   | same   | same   | same   |
| Description margin-top   | 8px                  | 8px    | 12px   | 12px   | 12px   | 16px   | 20px   |
| Sample queries margin-top| 24px                 | 24px   | 32px   | 32px   | 32px   | 40px   | 48px   |
| Sample query item height | 48px                 | 48px   | 44px   | 44px   | 48px   | 52px   | 60px   |
| Sample query item gap    | 8px                  | 8px    | 8px    | 8px    | 12px   | 12px   | 16px   |
| Sample query font        | 14px                 | 14px   | 14px   | 14px   | 15px   | 17px   | 20px   |
| Sample query padding-x   | 16px                 | 16px   | 16px   | 16px   | 20px   | 24px   | 32px   |
| Sample query border      | 1px solid --border-default | same | same | same | same | 1.5px | 2px |
| Sample query radius      | 8px                  | 8px    | 8px    | 8px    | 10px   | 12px   | 16px   |
| Sample query hover bg    | --color-bg-tertiary  | same   | same   | same   | same   | same   | same   |
| Sample query icon        | 16px, --text-tertiary "▶" | same | same | same | 18px | 20px | 24px |
| Sample query cursor      | pointer              | same   | same   | same   | same   | same   | same   |

**Wireframes:**

```
320px Mobile:
+-------------------------------+
|                               |
|        [illustration]         |  120x120
|                               |
|   No queries yet              |  18px/600
|                               |
|   Submit your first query to  |  14px
|   check for hallucinations.   |
|                               |
|   Try one of these:           |  14px/600
|                               |
| [▶ "What causes inflation?"]| ← clickable, 48px
| [▶ "Explain quantum physics"]|
| [▶ "List Nobel Prize winners"]|
|                               |
+-------------------------------+

1440px Desktop:
+--------------------------------------------------------------------------------+
|                                                                                 |
|                           [illustration]                                        |  200x200
|                                                                                 |
|                       No queries yet                                            |  28px/600
|                                                                                 |
|         Submit your first query and the system will verify                      |  16px
|         each claim, score confidence, and correct errors.                       |
|                                                                                 |
|                       Try one of these:                                         |
|                                                                                 |
|            [▶ "What causes inflation in emerging markets?"]                    |
|            [▶ "Explain quantum entanglement in simple terms"]                  |
|            [▶ "List the capital cities of all EU member states"]               |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

**Interaction Flow:**

1. Shown when query history is empty (no queries submitted yet)
2. Clicking a sample query populates the query input with that text and auto-submits
3. After first query is submitted, empty state never appears again (replaced by query results)
4. Illustration uses a simple SVG graphic (search/magnifying glass with checkmark)

**Accessibility:**

- Container: `role="region"`, `aria-label="Getting started"`
- Sample queries: `role="button"`, `aria-label="Try sample query: [text]"`
- Keyboard: Tab to each sample, Enter to submit

---

### 11.7 — Expand/Collapse Long Responses (P1 Important)

User-critique #21 identifies this as missing. Response cards need a truncation system for long outputs.

| Property                | 320px                    | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ----------------------- | ------------------------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Collapsed max-height    | 200px                    | 200px  | 280px  | 320px  | 360px  | 480px  | 600px  |
| Gradient overlay height | 60px                     | 60px   | 80px   | 80px   | 80px   | 100px  | 120px  |
| Gradient from color     | transparent              | same   | same   | same   | same   | same   | same   |
| Gradient to color       | --color-bg-primary       | same   | same   | same   | same   | same   | same   |
| Toggle button width     | 100%                     | 100%   | 100%   | 100%   | 100%   | 100%   | 100%   |
| Toggle button height    | 36px                     | 36px   | 36px   | 36px   | 40px   | 44px   | 52px   |
| Toggle button font      | 13px/500                 | 13px   | 13px   | 14px   | 14px   | 16px   | 18px   |
| Toggle button color     | --primary-500            | same   | same   | same   | same   | same   | same   |
| Toggle button bg        | transparent              | same   | same   | same   | same   | same   | same   |
| Toggle button radius    | 0 0 8px 8px              | same   | same   | same   | same   | 0 0 12px 12px | 0 0 16px 16px |
| Toggle icon size        | 14px                     | 14px   | 14px   | 14px   | 16px   | 18px   | 20px   |
| Expand animation        | max-height 300ms ease-out | same  | same   | same   | same   | same   | same   |
| Collapse animation      | max-height 200ms ease-in | same   | same   | same   | same   | same   | same   |
| Trigger threshold       | Content > collapsed max-height | same | same | same | same | same | same |

**Wireframes:**

```
Collapsed State (320px):
+-------------------------------+
| RESPONSE CARD                 |
|                               |
| Response text begins here     |
| and continues for several     |
| lines with markdown content   |
| including code blocks and     |
| ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ | ← gradient fade
| ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ |
| [▼ Show More (847 words)]    | ← toggle button
+-------------------------------+

Expanded State (320px):
+-------------------------------+
| RESPONSE CARD                 |
|                               |
| Response text begins here     |
| and continues for several     |
| lines with markdown content   |
| including code blocks and     |
| citations. The full response  |
| is now visible without any    |
| truncation or gradient...     |
| ...rest of content...         |
|                               |
| [▲ Show Less]                | ← toggle button
+-------------------------------+
```

**Behavior Rules:**

- Only applies if rendered content exceeds the `collapsed max-height`
- Short responses render fully with no toggle button
- Toggle label: "Show More (N words)" when collapsed, "Show Less" when expanded
- Scrolls to top of card on collapse if card top is above viewport
- State is not persisted — defaults to collapsed on page load

**Accessibility:**

- Toggle button: `aria-expanded="false/true"`, `aria-controls="response-content-[id]"`
- Content area: `id="response-content-[id]"`
- Screen reader: announces "Expanded" / "Collapsed" on toggle

---

### 11.8 — Bookmark / Star Results (P1 Important)

User-critique #7 identifies this as missing. The sidebar wireframe (10.9) shows a star icon but no dedicated spec exists.

**Bookmark Toggle Button (on Response Card):**

| Property                | 320px                     | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ----------------------- | ------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Button size             | 36x36                     | 36x36  | 36x36  | 36x36  | 40x40  | 44x44  | 52x52  |
| Icon size               | 16px                      | 16px   | 16px   | 16px   | 18px   | 20px   | 24px   |
| Position                | Action bar (overflow on 320) | Action bar | Action bar | Action bar | Action bar | Action bar | Action bar |
| Default icon            | Star outline (☆)          | same   | same   | same   | same   | same   | same   |
| Active icon             | Star filled (★)           | same   | same   | same   | same   | same   | same   |
| Default color           | --text-tertiary           | same   | same   | same   | same   | same   | same   |
| Active color            | --color-warning-500       | same   | same   | same   | same   | same   | same   |
| Transition              | color 150ms, scale 150ms  | same   | same   | same   | same   | same   | same   |
| Scale on activate       | 1.0 → 1.2 → 1.0 (bounce) | same   | same   | same   | same   | same   | same   |

**Bookmark Indicator (in Session History Sidebar):**

| Property             | 1024px                    | 1440px | 2560px | 3840px |
| -------------------- | ------------------------- | ------ | ------ | ------ |
| Star icon size       | 12px                      | 14px   | 16px   | 18px   |
| Star icon color      | --color-warning-500       | same   | same   | same   |
| Position in row      | Right of timestamp        | same   | same   | same   |
| Gap from timestamp   | 4px                       | 4px    | 6px    | 8px    |

**Bookmarks Filter (in Sidebar):**

| Property             | 1024px                     | 1440px | 2560px | 3840px |
| -------------------- | -------------------------- | ------ | ------ | ------ |
| Filter toggle height | 32px                       | 36px   | 40px   | 48px   |
| Filter toggle font   | 12px/500                   | 13px   | 15px   | 17px   |
| Filter toggle icon   | ★ 12px                    | 14px   | 16px   | 18px   |
| Active bg            | --color-warning-50         | same   | same   | same   |
| Active border        | 1px solid --color-warning-500 | same | same  | same   |
| Position             | Below search input, above history list | same | same | same |

**Wireframes:**

```
Sidebar filter (1440px):
+------------------+
| [+ New Query    ]|
| [🔍 Search...]   |
| [★ Bookmarks (3)]| ← filter toggle
|                  |
| Today            |
| [Q1] 87% · 2m   |
| [Q2] 94% ★ · 15m| ← ★ = bookmarked
| [Q3] 76% · 1h   |
+------------------+

Sidebar filter active (1440px):
+------------------+
| [+ New Query    ]|
| [🔍 Search...]   |
| [★ Bookmarks (3)]| ← active state, warning-50 bg
|                  |
| [Q2] 94% ★ · 15m| ← only bookmarked shown
| [Q7] 91% ★ · 3d |
| [Q11] 88% ★ · 5d|
+------------------+
```

**Interaction Flow:**

1. Click star icon on response card to toggle bookmark
2. Bookmarks stored in localStorage as array of query IDs
3. Sidebar shows ★ icon next to bookmarked items
4. "Bookmarks" filter in sidebar toggles between all/bookmarked-only view
5. Bookmarks survive page reload (localStorage)
6. Keyboard shortcut `B` toggles bookmark on focused result (per Section 10.8)

**Accessibility:**

- Toggle: `aria-label="Bookmark this result"` / `"Remove bookmark"`, `aria-pressed="false/true"`
- Filter: `aria-label="Show bookmarked results only"`, `aria-pressed="false/true"`
- Screen reader: announces "Bookmarked" / "Bookmark removed" via `aria-live="polite"`

---

### 11.9 — Inline Diff Toggle on Response Card (P1 Important)

User-critique Part 2 notes that corrections are only viewable in a separate log panel. This section specifies an inline diff view directly within the response body.

| Property                 | 320px                     | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ------------------------ | ------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Toggle button size       | 36x36                     | 36x36  | 36x36  | 36x36  | 40x40  | 44x44  | 52x52  |
| Toggle position          | In corrections badge area | same   | same   | same   | same   | same   | same   |
| Toggle label             | Hidden                    | Hidden | "Show Diff" | same | same | same | same |
| Toggle label font        | —                         | —      | 12px   | 12px   | 13px   | 15px   | 18px   |
| Toggle icon              | Diff icon (split lines)   | same   | same   | same   | same   | same   | same   |
| Toggle icon size         | 16px                      | 16px   | 16px   | 16px   | 18px   | 20px   | 24px   |
| Removed text bg          | --color-error-50          | same   | same   | same   | same   | same   | same   |
| Removed text decoration  | line-through              | same   | same   | same   | same   | same   | same   |
| Removed text color       | --color-error-700         | same   | same   | same   | same   | same   | same   |
| Added text bg            | --color-success-50        | same   | same   | same   | same   | same   | same   |
| Added text decoration    | underline                 | same   | same   | same   | same   | same   | same   |
| Added text color         | --color-success-700       | same   | same   | same   | same   | same   | same   |
| Diff legend height       | 24px                      | 24px   | 28px   | 28px   | 28px   | 32px   | 36px   |
| Diff legend font         | 11px                      | 11px   | 12px   | 12px   | 13px   | 15px   | 17px   |
| Diff legend margin-bottom| 8px                       | 8px    | 8px    | 8px    | 12px   | 12px   | 16px   |

**Wireframes:**

```
Diff OFF (default):
+----------------------------------------------------------------------+
| RESPONSE CARD                                        [2 corrections] |
|                                                                      |
| The capital of Australia is Canberra. It was chosen as a             |
| compromise between Sydney and Melbourne in 1908.                      |
+----------------------------------------------------------------------+

Diff ON (toggle active):
+----------------------------------------------------------------------+
| RESPONSE CARD                                   [2 corrections] [≡✓] |
|                                                                      |
| ░ Removed  ▓ Added                                                   | ← legend
|                                                                      |
| The capital of Australia is ░Sydney░ ▓Canberra▓. It was chosen as a |
| compromise between Sydney and Melbourne in ░1901░ ▓1908▓.            |
+----------------------------------------------------------------------+
```

**Interaction Flow:**

1. Diff toggle appears only when the response has corrections (corrections badge > 0)
2. Clicking the toggle inserts inline diff markers into the response body
3. Removed text shown with strikethrough + red background
4. Added text shown with underline + green background
5. A small legend appears above the response body
6. Toggle is independent per response card — toggling one does not affect others
7. Keyboard shortcut `D` toggles diff on focused card

**Accessibility:**

- Toggle: `aria-label="Show inline corrections"`, `aria-pressed="false/true"`
- Removed text: `<del>` element with `aria-label="Removed: [text]"`
- Added text: `<ins>` element with `aria-label="Added: [text]"`
- Legend: `role="note"`, `aria-label="Diff legend: red strikethrough for removed, green underline for added"`
- Color is never the only indicator (strikethrough and underline provide non-color differentiation)

---

### 11.10 — Checkpoint Manager UI (P2 Nice-to-have)

Sprint 5 (5.2.4) defines resume/start-fresh behavior but the dialog and checkpoint browser have no skeleton spec.

**Resume Dialog (appears on restart after crash):**

| Property              | 320px                      | 480px  | 768px     | 1024px    | 1440px    | 2560px    | 3840px    |
| --------------------- | -------------------------- | ------ | --------- | --------- | --------- | --------- | --------- |
| Dialog width          | calc(100vw - 32px)         | 90vw   | 420px     | 460px     | 500px     | 560px     | 680px     |
| Dialog padding        | 20px                       | 24px   | 28px      | 32px      | 32px      | 40px      | 48px      |
| Dialog radius         | 12px                       | 12px   | 12px      | 12px      | 12px      | 16px      | 20px      |
| Dialog shadow         | elevation-5                | same   | same      | same      | same      | same      | same      |
| Title font            | 18px/600                   | 18px   | 20px      | 22px      | 22px      | 26px      | 30px      |
| Body font             | 14px                       | 14px   | 14px      | 15px      | 15px      | 17px      | 20px      |
| Checkpoint info bg    | --color-bg-tertiary        | same   | same      | same      | same      | same      | same      |
| Checkpoint info padding | 12px                     | 12px   | 14px      | 16px      | 16px      | 20px      | 24px      |
| Checkpoint info radius | 8px                       | 8px    | 8px       | 8px       | 8px       | 10px      | 12px      |
| Checkpoint info font  | 13px mono                  | 13px   | 13px      | 14px      | 14px      | 16px      | 20px      |
| Button height         | 44px                       | 44px   | 44px      | 44px      | 44px      | 52px      | 56px      |
| Resume btn width      | calc(50% - 4px)            | same   | 140px     | 140px     | 160px     | 180px     | 220px     |
| Fresh btn width       | calc(50% - 4px)            | same   | 140px     | 140px     | 160px     | 180px     | 220px     |
| Button gap            | 8px                        | 8px    | 12px      | 12px      | 12px      | 16px      | 20px      |
| Resume btn style      | Primary (filled)           | same   | same      | same      | same      | same      | same      |
| Fresh btn style       | Secondary (outlined)       | same   | same      | same      | same      | same      | same      |
| Backdrop              | rgba(0,0,0,0.5)            | same   | same      | same      | same      | same      | same      |

**Wireframes:**

```
320px Mobile:
+-------------------------------+
|                               |
| +---------------------------+|
| | Previous Session Found    ||
| |                           ||
| | +-------------------------+|
| | | Checkpoint: Query 37/50 ||
| | | Agent: Critic (step 3)  ||
| | | Saved: 14:32, Mar 21    ||
| | | Version: 1.2.0          ||
| | +-------------------------+|
| |                           ||
| | Resume from where you     ||
| | left off, or start fresh. ||
| |                           ||
| | [Resume]    [Start Fresh] ||
| +---------------------------+|
|                               |
+-------------------------------+

1440px Desktop:
+--------------------------------------------------------------------------------+
|  (backdrop)                                                                     |
|                                                                                 |
|       +----------------------------------------------------+                   |
|       | Previous Session Found                              |                   |
|       |                                                    |                   |
|       | +------------------------------------------------+ |                   |
|       | | Checkpoint Details                              | |                   |
|       | | Position:  Query 37 of 50                       | |                   |
|       | | Last Agent: Critic Agent (Step 3 of 5)          | |                   |
|       | | Saved At:  14:32:07, March 21, 2026             | |                   |
|       | | Version:   1.2.0                                | |                   |
|       | | Integrity: ✓ Valid                              | |                   |
|       | +------------------------------------------------+ |                   |
|       |                                                    |                   |
|       | Resume from the last checkpoint, or discard it     |                   |
|       | and start fresh. Previous data will be archived.   |                   |
|       |                                                    |                   |
|       |       [Resume from Checkpoint]  [Start Fresh]      |                   |
|       +----------------------------------------------------+                   |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

**Version Mismatch Variant:**

When checkpoint version differs from current system version, add a warning:

```
| +------------------------------------------------+ |
| | ⚠ Version Mismatch                             | |
| | Checkpoint: v1.1.0  |  Current: v1.2.0        | |
| | Resume may be unreliable.                      | |
| +------------------------------------------------+ |
|                                                    |
|   [Resume Anyway]  [Start Fresh (Recommended)]    |
```

**Accessibility:**

- Dialog: `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby="checkpoint-title"`
- Focus trapped within dialog
- Autofocus on "Resume" button (the safer action)
- Checkpoint details: `role="region"`, `aria-label="Checkpoint details"`

---

### 11.11 — Performance Warning Banners (P2 Nice-to-have)

Sprint 5 (IS-06, CB-03) define CPU-fallback and token-budget-exceeded notifications but no skeleton spec exists.

**Warning Banner (shared layout for all performance warnings):**

| Property          | 320px                          | 480px   | 768px    | 1024px   | 1440px   | 2560px   | 3840px   |
| ----------------- | ------------------------------ | ------- | -------- | -------- | -------- | -------- | -------- |
| Width             | 100%                           | 100%    | 100%     | 100%     | 100%     | 100%     | 100%     |
| Min-height        | 44px                           | 44px    | 40px     | 40px     | 44px     | 48px     | 56px     |
| Padding-x         | 12px                           | 16px    | 24px     | 32px     | 40px     | 64px     | 96px     |
| Padding-y         | 8px                            | 8px     | 8px      | 10px     | 10px     | 12px     | 14px     |
| Icon size         | 16px                           | 16px    | 18px     | 18px     | 18px     | 22px     | 26px     |
| Message font      | 13px                           | 13px    | 13px     | 14px     | 14px     | 16px     | 18px     |
| Dismiss btn size  | 28x28px                        | 28x28   | 28x28    | 32x32    | 32x32    | 36x36    | 44x44    |
| Position          | Below circuit breaker banner   | same    | same     | same     | same     | same     | same     |
| z-index           | 85                             | 85      | 85       | 85       | 85       | 85       | 85       |
| Border-bottom     | 1px solid                      | same    | same     | same     | same     | 1.5px    | 2px      |

**Warning Types:**

| Type | Background | Border Color | Icon | Message |
| --- | --- | --- | --- | --- |
| CPU Fallback | --color-warning-50 | --color-warning-500 | ⚡ | "Running on CPU — performance is reduced. GPU recommended." |
| Token Budget Exceeded | --color-warning-50 | --color-warning-500 | ⚠ | "Token budget exceeded. Partial results returned." |
| Slow Query | --color-info-50 | --color-info-500 | ⏱ | "This is taking longer than usual. Agents are still working." |
| Model Not Found | --color-error-50 | --color-error-500 | ✕ | "Local model not found. Please reinstall the model." |
| Disk Full | --color-error-50 | --color-error-500 | ✕ | "Disk full — checkpoints disabled. Pipeline continues without persistence." |

**Wireframe:**

```
+--------------------------------------------------------------------------------+
| ⚡ Running on CPU — performance is reduced. GPU recommended.            [✕]    |
+--------------------------------------------------------------------------------+
```

**Accessibility:**

- `role="alert"`, `aria-live="polite"` (warning) or `aria-live="assertive"` (error)
- Dismiss: `aria-label="Dismiss warning"`
- Keyboard: Tab to dismiss button, Enter to dismiss

---

### 11.12 — Score Unavailable State for Confidence Gauge (P2 Nice-to-have)

Sprint 5 CS edge cases define "Score unavailable" and "Calculating..." states but the skeleton-diagrams have no visual spec for these.

**Calculating State (during processing):**

| Property             | 320px                    | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| -------------------- | ------------------------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Display              | Inline text              | Mini spinner | Spinner in gauge | same | same | same | same |
| Spinner diameter     | —                        | 24px   | 48px   | 56px   | 64px   | 80px   | 96px   |
| Spinner stroke       | —                        | 3px    | 4px    | 4px    | 5px    | 6px    | 8px    |
| Spinner color        | --primary-500            | same   | same   | same   | same   | same   | same   |
| Text                 | "Calculating..."         | same   | same   | same   | same   | same   | same   |
| Text font            | 12px, --text-tertiary    | 12px   | 14px   | 14px   | 14px   | 16px   | 20px   |
| Animation            | Pulse opacity 1s infinite | Spinner rotation 1s linear infinite | same | same | same | same | same |

**Score Unavailable State (critic timeout/error):**

| Property              | 320px                      | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| --------------------- | -------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Display               | Inline text                | Inline text | In gauge area | same | same | same | same |
| Icon                  | ⚠ 14px                   | ⚠ 14px | ⚠ 24px | ⚠ 28px | ⚠ 32px | ⚠ 40px | ⚠ 48px |
| Icon color            | --color-warning-500        | same   | same   | same   | same   | same   | same   |
| Text                  | "Score unavailable"        | same   | same   | same   | same   | same   | same   |
| Text font             | 12px, --text-tertiary      | 12px   | 14px   | 14px   | 14px   | 16px   | 20px   |
| Retry button          | "Retry" 28x28 icon-only    | same   | 80x32 text btn | same | same | 90x36 | 100x40 |
| Retry button font     | —                          | —      | 12px   | 12px   | 13px   | 15px   | 17px   |
| Gauge arc             | Hidden                     | Dashed, --skeleton-base | same | same | same | same | same |
| Gauge arc stroke      | —                          | 2px dashed | 3px dashed | same | same | 4px | 5px |

**Wireframes:**

```
Calculating (768px):
+--------------------+
|     +-------+      |
|    / ◠ spin  \     |    Spinner inside gauge outline
|   |          |     |
|    \        /      |
|     +-------+      |
|   Calculating...   |
+--------------------+

Score Unavailable (768px):
+--------------------+
|     +- - - -+      |
|    /         \     |    Dashed arc outline
|   |    ⚠     |    |    Warning icon centered
|    \         /     |
|     +- - - -+      |
| Score unavailable  |
|     [Retry]        |
+--------------------+
```

**Accessibility:**

- Calculating: `aria-label="Confidence score is being calculated"`, `role="status"`
- Unavailable: `aria-label="Confidence score unavailable"`, `role="status"`
- Retry: `aria-label="Retry confidence score calculation"`
- Score must NEVER show 0% when the actual state is "unavailable" (they are semantically different)

---

### 11.13 — Mobile Drawer Navigation (P1 Important)

The global layout grid (Section 1) specifies "Drawer overlay" for sidebar mode on 320-768px, but the drawer's internal content has no spec.

| Property                | 320px                      | 480px   | 768px   |
| ----------------------- | -------------------------- | ------- | ------- |
| Drawer width            | 85vw (max 320px)           | 85vw (max 360px) | 85vw (max 400px) |
| Drawer position         | Left edge, full height     | same    | same    |
| Drawer z-index          | 300 (per 11.20)            | 300     | 300     |
| Backdrop z-index        | 400 (per 11.20)            | 400     | 400     |
| Drawer bg               | --color-bg-primary         | same    | same    |
| Drawer shadow           | elevation-6                | same    | same    |
| Backdrop                | rgba(0,0,0,0.5)            | same    | same    |
| Slide animation         | 250ms ease-out             | same    | same    |
| Close button size       | 44x44px                    | same    | same    |
| Close button position   | Top-right, 8px inset       | 12px    | 16px    |
| Header height           | 56px                       | 56px    | 60px    |
| Header padding-x        | 16px                       | 16px    | 24px    |
| Logo height (in drawer) | 24px                       | 24px    | 28px    |
| Nav section title font  | 11px/600, uppercase, --text-tertiary | same | 12px |
| Nav section title margin | 16px 0 8px 16px           | same    | 16px 0 8px 24px |
| Nav item height         | 48px                       | 48px    | 44px    |
| Nav item padding-x      | 16px                       | 16px    | 24px    |
| Nav item font           | 15px                       | 15px    | 15px    |
| Nav item icon size      | 20px                       | 20px    | 20px    |
| Nav item icon gap       | 12px                       | 12px    | 12px    |
| Nav item active bg      | --color-bg-tertiary        | same    | same    |
| Nav item active font-wt | 600                        | 600     | 600     |
| Nav item active border  | 3px left, --primary-500    | same    | same    |
| Divider margin          | 8px 16px                   | 8px 16px | 8px 24px |
| Search input height     | 40px                       | 40px    | 44px    |
| Search input margin     | 8px 16px                   | 8px 16px | 8px 24px |
| Search input font       | 14px                       | 14px    | 14px    |
| History list scroll     | calc(100vh - 280px)        | same    | same    |
| History item height     | 52px                       | 52px    | 48px    |
| History query font      | 14px, truncate 1 line      | same    | same    |
| History timestamp font  | 11px, --text-tertiary      | 11px    | 12px    |
| History confidence badge| 28x18px, 10px font          | same    | 32x20   |

**Wireframes:**

```
320px Mobile (drawer open):
+-------------------------------+------+
|  Guardrail AI          [X]  |░░░░░░|  backdrop
+-------------------------------+░░░░░░|
| [🔍 Search queries...]       |░░░░░░|
+-------------------------------+░░░░░░|
| NAVIGATION                    |░░░░░░|
| [📊] Dashboard           ◀  |░░░░░░|  ◀ = active
| [📦] Batch Processing        |░░░░░░|
| [⚙] Settings                |░░░░░░|
+-------------------------------+░░░░░░|
| HISTORY                       |░░░░░░|
| Today                         |░░░░░░|
| [Q] What causes inf... 87%  |░░░░░░|
| [Q] Explain quantum... 94%  |░░░░░░|
| [Q] List the capital... 76%★|░░░░░░|
| Yesterday                     |░░░░░░|
| [Q] Why do markets... 91%   |░░░░░░|
+-------------------------------+░░░░░░|
| CONFIG                        |░░░░░░|
| [Rules] [Thresholds]         |░░░░░░|
+-------------------------------+------+
```

**Interaction Flow:**

1. Hamburger menu (☰) in header opens drawer
2. Drawer slides in from left with backdrop overlay
3. Tapping backdrop or [X] button closes drawer
4. Selecting a nav item closes drawer and navigates
5. Swipe-right-to-left on drawer edge closes it (gesture)
6. History items are tappable — opens that query result and closes drawer

**Accessibility:**

- Drawer: `role="dialog"`, `aria-modal="true"`, `aria-label="Navigation menu"`
- Focus trapped within drawer while open
- Close: `aria-label="Close navigation menu"`
- Nav items: `role="navigation"` container, `aria-current="page"` on active item
- Backdrop: inert (not focusable)
- Esc key closes drawer

---

### 11.14 — Toast Notification Component (P1 Important)

Sprint 4 (4.3.4) defines toast behavior comprehensively, but skeleton-diagrams.md has no per-breakpoint box-model table for the toast component.

| Property              | 320px                         | 480px        | 768px    | 1024px   | 1440px   | 2560px   | 3840px   |
| --------------------- | ----------------------------- | ------------ | -------- | -------- | -------- | -------- | -------- |
| Position              | Fixed, bottom-center          | same         | Fixed, bottom-right | same | same | same | same |
| Bottom offset         | 16px                          | 16px         | 24px     | 24px     | 24px     | 32px     | 40px     |
| Right offset          | —                             | —            | 24px     | 24px     | 24px     | 32px     | 40px     |
| Width                 | calc(100vw - 32px)            | calc(100vw - 32px) | 360px | 360px | 400px | 440px | 520px |
| Max-width             | 480px                         | 480px        | 480px    | 480px    | 480px    | 520px    | 600px    |
| Min-height            | 48px                          | 48px         | 48px     | 48px     | 48px     | 56px     | 64px     |
| Padding               | 12px 16px                     | 12px 16px    | 12px 16px | 14px 16px | 14px 16px | 16px 20px | 20px 24px |
| Border-radius         | 8px                           | 8px          | 8px      | 8px      | 10px     | 12px     | 16px     |
| Border-left           | 4px solid [severity color]    | same         | same     | same     | same     | 5px      | 6px      |
| Shadow                | elevation-4                   | same         | same     | same     | same     | same     | elevation-5 |
| Icon size             | 18px                          | 18px         | 20px     | 20px     | 20px     | 24px     | 28px     |
| Icon margin-right     | 8px                           | 8px          | 10px     | 10px     | 10px     | 12px     | 16px     |
| Title font            | 14px/600                      | 14px         | 14px     | 14px     | 14px     | 16px     | 18px     |
| Description font      | 12px                          | 12px         | 13px     | 13px     | 13px     | 15px     | 17px     |
| Close btn size        | 28x28px                       | 28x28        | 28x28    | 28x28    | 32x32    | 36x36    | 44x44    |
| Close btn icon        | 12px                          | 12px         | 14px     | 14px     | 14px     | 16px     | 20px     |
| Action btn height     | 28px                          | 28px         | 28px     | 28px     | 32px     | 36px     | 44px     |
| Action btn font       | 12px/500                      | 12px         | 13px     | 13px     | 13px     | 15px     | 17px     |
| Stack gap             | 8px                           | 8px          | 8px      | 8px      | 8px      | 10px     | 12px     |
| Max visible stacked   | 3                             | 3            | 3        | 3        | 3        | 4        | 5        |
| z-index               | 1000 (per 11.20)              | 1000         | 1000     | 1000     | 1000     | 1000     | 1000     |

**Wireframes:**

```
320px Mobile (bottom-center):
+-------------------------------+
|                               |
|                               |  ← page content
|                               |
| +---------------------------+|
| | [✓] Copied to clipboard  ||  toast, full-width - 32px
| +---------------------------+|
+-------------------------------+

1440px Desktop (bottom-right):
+--------------------------------------------------------------------------------+
|                                                                                 |
|                                                                                 |
|                                            +------------------------------+     |
|                                            | [⚠] Circuit breaker tripped |     |
|                                            |     Request blocked.         |     |
|                                            |     [View Details]      [X]  |     |
|                                            +------------------------------+     |
|                                            | [✓] Copied to clipboard [X]  |     |
|                                            +------------------------------+     |
+--------------------------------------------------------------------------------+
```

**Animations:**

- Enter: slide-up + fade-in, 200ms ease-out
- Exit: slide-right + fade-out, 200ms ease-in
- Stack reflow: 200ms ease-out transition on all sibling positions
- Dismiss gesture (mobile): swipe-right, 150ms ease-in

**Accessibility:**

- Per Sprint 4 spec: `aria-live="assertive"` (error), `aria-live="polite"` (all others)
- Close: `aria-label="Dismiss notification"`
- Action: standard button semantics
- Focus does NOT move to toast (passive notification)

---

### 11.15 — Correction Log Skeleton Loading State

Section 6 defines skeletons for Response Card, Confidence Gauge, Live Trace, and Source Attribution but omits the Correction Log.

```
Correction Log Skeleton:
+----------------------------------+
| [====== CORRECTIONS ======]     |   header: 50% x 18px
|                                  |
| [●]── [==========]              |   timeline dot + text line
|   |   [========]                 |   score placeholder
|   |                              |
| [●]── [============]            |
|   |   [=======]                 |
|   |                              |
| [○]── [===========]             |   unfilled dot = pending
|       [=========]               |
+----------------------------------+
Timeline dot: matches timeline dot size per breakpoint (10-20px)
Timeline line: 2-3px, dashed --skeleton-base
Text lines: 60-80% width x 14px, --skeleton-base
Score blocks: 40% width x 20px, --skeleton-highlight
Corner radius: matches real card
```

**Skeleton Dimensions by Breakpoint:**

| Element            | 320px    | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| ------------------ | -------- | ----- | ----- | ------ | ------ | ------ | ------ |
| Card width         | 100%     | 100%  | ~50%  | ~45%   | ~45%   | ~35%   | ~20%   |
| Card min-height    | 80px     | 80px  | 120px | 160px  | 160px  | 220px  | 280px  |
| Timeline dot       | 10px     | 10px  | 12px  | 12px   | 14px   | 16px   | 20px   |
| Timeline line      | 2px dashed | same | same  | same   | same   | 3px    | 3px    |
| Text line height   | 12px     | 12px  | 14px  | 14px   | 14px   | 16px   | 20px   |
| Score block height | 16px     | 18px  | 20px  | 24px   | 28px   | 34px   | 40px   |
| Rows shown         | 2        | 2     | 3     | 3      | 3      | 4      | 5      |

---

### 11.16 — Additional Skeleton Loading States (Section 10 Features)

Section 6 skeletons cover the original components. These skeletons cover features added in Section 10.

#### Batch Processing Table Skeleton

```
+-----------------------------------------------+
| [====== BATCH ======]    [====] [====]        |   header + 2 action btns
|                                                |
| [=== textarea ===========================]    |   textarea: 100% x 120-200px
| [=========================================]   |
| [=========================================]   |
|                                                |
| [=] [==============] [====] [====]            |   row 1: #, query, status, score
| [=] [=============]  [====] [====]            |   row 2
| [=] [==============] [====] [====]            |   row 3
| [=] [============]   [====] [====]            |   row 4
| [=] [=============]  [====] [====]            |   row 5
+-----------------------------------------------+
Row height: matches table row height per breakpoint (44-64px)
# column: 40-64px
Query column: flex
Status/Score: 60-140px each
```

#### Historical Trend Chart Skeleton

```
+----------------------------+
| [====== CHART TITLE ======]|   title: 60% x 16px
|                            |
| [========================] |   chart area: 100% x chart height
| [========================] |   (180-380px by breakpoint)
| [========================] |   filled with --skeleton-base
| [========================] |
|                            |
| [==] [==] [==] [==]       |   time range buttons: 4 x 40-80px
+----------------------------+
```

#### Notification Center Skeleton

```
+-----------------------------+
| [======= NOTIFS =======]   |   header: 60% x 16px
|                             |
| [●] [=================]    |   notification row
|     [============]          |   detail line
|                             |
| [●] [================]     |
|     [===========]           |
|                             |
| [●] [=================]    |
|     [=============]         |
+-----------------------------+
Row height: matches notification row-h per breakpoint (60-80px)
Icon: 20-30px circles
Text: 60-80% width
```

#### Session History Sidebar Skeleton (1024px+)

```
+------------------+
| [==== BTN ====] |   new query button: 100% x 40-56px
| [🔍 =========] |   search input: 100% x 36-52px
|                  |
| [===]            |   date divider: 40% x 12px
| [●] [========]  |   history item: dot + text
|     [=====]      |   timestamp
| [●] [=========] |
|     [====]       |
| [●] [=======]   |
|     [======]     |
|                  |
| [===]            |   date divider
| [●] [========]  |
|     [=====]      |
+------------------+
Item height: matches history item height per breakpoint (52-72px)
```

#### Command Palette Skeleton (loading state while searching)

```
+------------------------------------------+
| > [===========]                    [Esc] |   search input shimmer
+------------------------------------------+
| [===========]                            |   category: 40% x 12px
|   [=============]            [====]      |   item + shortcut
|   [============]             [====]      |
|   [==============]           [====]      |
| [==========]                             |   category
|   [=============]            [====]      |
|   [===========]              [====]      |
+------------------------------------------+
```

---

### 11.17 — Query Input Specification Reconciliation

Section 5.1 and Section 10.1 both define Query Input specs. This table reconciles discrepancies. **Section 10.1 values take precedence** as it is the more complete specification.

| Property        | Section 5.1 Value | Section 10.1 Value | Canonical Value (use this) |
| --------------- | ----------------- | ------------------ | -------------------------- |
| Min-height 320  | 48px              | 48px               | 48px                       |
| Min-height 2560 | —                 | 64px               | 64px                       |
| Min-height 3840 | —                 | 72px               | 72px                       |
| Max-height      | Not specified     | 160-360px           | 160-360px (per 10.1)       |
| Border-radius 768 | 8px            | 10px               | **10px** (10.1)            |
| Border-radius 1024 | 8px           | 10px               | **10px** (10.1)            |
| Border-radius 1440 | 10px          | 12px               | **12px** (10.1)            |
| Border-radius 2560 | 12px          | 14px               | **14px** (10.1)            |
| Focus ring 2560 | 3px              | 2.5px (from focus border) | **3px** (5.1 — more accessible) |
| Focus ring 3840 | 3px              | 3px                | 3px                        |
| Token counter   | Not specified     | Full spec           | Per 10.1                   |
| Stop button     | Not specified     | Full spec           | Per 10.1                   |
| File upload     | Not specified     | Full spec           | Per 10.1                   |

**Resolution:** Section 5.1 should be treated as a simplified overview. Section 10.1 is the authoritative specification for the Query Input component. Where values conflict, Section 10.1 values are canonical.

---

### 11.18 — Breakpoint & Cross-Document Reconciliation

Sprint 4, Sprint 5, and this skeleton document each define layout properties. This section is the **single source of truth** for all conflicts. Where any other document disagrees with the values below, this section is canonical.

**Canonical Breakpoints (7 layout-changing breakpoints):**

| # | Width | Name | Source | Layout Change |
| --- | --- | --- | --- | --- |
| 1 | 320px | Mobile Small | Sprint 4 + Sprint 5 | Single column, drawer nav, collapsed components |
| 2 | 480px | Mobile Large | Sprint 4 + Sprint 5 | Single column, slightly wider cards |
| 3 | 768px | Tablet | Sprint 4 + Sprint 5 | 2-column grid, inline live trace |
| 4 | 1024px | Small Desktop | Sprint 4 + Sprint 5 | Collapsible sidebar, 2-column main |
| 5 | 1440px | Desktop | Sprint 4 | 3-column grid, persistent sidebar |
| 6 | 2560px | QHD/2K | Sprint 4 | Enlarged spacing, 3-column with bigger nodes |
| 7 | 3840px | 4K UHD | Sprint 4 + Sprint 5 | 4-column grid, maximum content density |

**Tested Checkpoints (not layout-changing, but verified visually):**

| Width | Name | Notes |
| --- | --- | --- |
| 1280px | Laptop | Between 1024 and 1440. Uses 1024px layout with extra margin. No grid change. |
| 1920px | Full HD | Between 1440 and 2560. Uses 1440px layout. Primary design target per Sprint 5. |

**Resolution:** All skeleton diagrams in this document use the 7 Sprint 4 breakpoints (320, 480, 768, 1024, 1440, 2560, 3840). The Sprint 5 breakpoints of 1280px and 1920px are verified checkpoints — the layout at those widths is interpolated from the nearest lower layout-changing breakpoint. No additional layout specs are needed for 1280 and 1920, but visual regression tests must include them.

#### Grid Column Count Reconciliation

Sprint 4 (4.2.2/4.2.4) and this skeleton document define different column counts. **Skeleton values are canonical** because the wireframes in Sections 4 and 10.15 are drawn with these column counts and they work with the actual component inventory.

| Breakpoint | Sprint 4 Columns | Skeleton Columns (Canonical) | Explanation |
| --- | :---: | :---: | --- |
| 320px | 1 | **1** | Agreement |
| 480px | 2 | **1** | Sprint 4's 2-col at 480px is only for metric card sub-grids, not the page grid |
| 768px | 2 | **2** | Agreement |
| 1024px | 3 | **2** | Sidebar takes one "column" worth of space; main content has 2-col grid |
| 1440px | 4 | **3** | Main content has 3 grid columns; sidebar is separate |
| 2560px | 6 | **3** | Sprint 4's 6-col applies to metric card sub-grids within dashboard summary |
| 3840px | 8 | **4** | Sprint 4's 8-col applies to metric card sub-grids; page grid is 4-col |

Sprint 4's higher column counts (4/6/8) define the **metric card sub-grid** within the dashboard summary section. The skeleton's column counts define the **page-level grid** that positions the major components (Response Card, Confidence Gauge, Live Trace, Source Attribution, Correction Log).

#### Sidebar Width Reconciliation

| Breakpoint | Sprint 4 Sidebar | Skeleton Sidebar (Canonical) | Reason |
| --- | --- | --- | --- |
| 1024px | 240px (collapsible to 64px) | **280px** (collapsible to 64px per 11.21) | Extra 40px needed for history list + search input |
| 1440px | 240px | **320px** | Session history, config, and stats sections require more width |
| 2560px | 280px | **400px** | Proportional scaling for 2K; prevents cramped history items |
| 3840px | 320px | **480px** | 4K screens have more space; wider sidebar improves readability at 20px font |

#### Navigation Pattern Reconciliation

| Breakpoint | Sprint 4 Pattern | Skeleton Pattern (Canonical) | Reason |
| --- | --- | --- | --- |
| 320px | Bottom tab bar (56px) | **Hamburger menu + left drawer** | Drawer accommodates history, config, and dynamic content; bottom tab bar suits fixed 3-4 views only |
| 480px | Bottom tab bar | **Hamburger menu + left drawer** | Same reasoning |
| 768px | Top horizontal bar, no hamburger | **Hamburger menu + left drawer** | At 768px sidebar is still hidden (0 width per Section 1); drawer needed for history access |
| 1024px+ | Left sidebar | **Left sidebar** | Agreement |

**Trade-off note:** Bottom tab bars offer better thumb reachability on large phones. The hamburger + drawer pattern was chosen because the app's navigation includes variable-length query history, config, and stats — content that cannot fit in a fixed 4-5 item bottom bar.

#### Live Trace Positioning Reconciliation

| Breakpoint | Sprint 4 Position | Skeleton Position (Canonical) | Reason |
| --- | --- | --- | --- |
| 768px | Right-docked panel, 280px, pushes content | **Inline, full-width in grid** | Right-docked at 768px + potential left sidebar leaves <200px for content — unusable |
| 1024px | Right-docked panel, 300px | **Inline, full-width in grid** | Same reasoning; sidebar is 280px, trace would need 300px, leaving <440px for content |
| 1440px | Right-docked panel, 320px, persistent | **Column in 3-col grid (~25%)** | Integrated into grid = ~320px; functionally equivalent but simpler layout logic |
| 2560px | Right-docked panel, 360px | **Column in 3-col grid (~27%)** | ~594px; more space than Sprint 4's 360px |
| 3840px | Right-docked panel, 400px | **Column in 4-col grid (~25%)** | ~850px; significantly more space than Sprint 4's 400px |

#### Typography Token Reconciliation

See Section 2 "Sprint 4 Token Mapping" table for the complete mapping between Sprint 4 CSS tokens and skeleton pixel values.

---

### 11.19 — Error and Edge-Case States for Section 10 Features

Section 10 defines happy-path layouts. This section specifies error and empty states for each new feature.

#### Batch Processing Error States

**Upload Error:**

```
+-----------------------------------------------+
| ⚠ Upload Failed                              |
|                                                |
| The file could not be parsed. Supported        |
| formats: CSV (one query per row), JSON         |
| (array of strings).                            |
|                                                |
| [Try Again]                                   |
+-----------------------------------------------+
```

**All Queries Failed:**

```
+-----------------------------------------------+
| Batch Results: 0/50 succeeded                 |
|                                                |
| # | Query                  | Status   | Score |
| 1 | What causes inflat...  | Failed   | —     |
| 2 | Explain quantum en...  | Failed   | —     |
| ...                                            |
|                                                |
| [Retry All Failed] [Export Error Log]          |
+-----------------------------------------------+
```

| State Element       | Styling |
| ------------------- | ------- |
| Error row bg        | --color-error-50 |
| Error status badge  | --color-error-500, white text |
| Error icon          | ✕ 14px, --color-error-500 |
| Retry button        | Secondary style (outlined) |

#### Search No Results (Session History Sidebar)

```
+------------------+
| [🔍 quantum...]  |
|                  |
| No results found |   14px, --text-tertiary
|                  |
| Try a different  |   13px, --text-tertiary
| search term.     |
+------------------+
```

| Property        | Value |
| --------------- | ----- |
| Icon            | 🔍 32px, --text-tertiary, 0.5 opacity |
| Title font      | 14px/500, --text-secondary |
| Description font | 13px, --text-tertiary |
| Padding         | 32px 16px |
| Text-align      | center |

#### Trend Charts Insufficient Data

```
+----------------------------+
| Avg Confidence Over Time   |
|                            |
|     [chart icon, 48px]     |   --text-tertiary, 0.3 opacity
|                            |
|   Not enough data yet.     |   14px, --text-secondary
|   Submit at least 5        |   13px, --text-tertiary
|   queries to see trends.   |
+----------------------------+
```

| Property        | Value |
| --------------- | ----- |
| Icon            | Line chart outline, 48px, --text-tertiary |
| Title font      | Same as chart title |
| Message font    | 14px/500, --text-secondary |
| Detail font     | 13px, --text-tertiary |
| Min queries     | 5 (before charts render) |

#### Notification Center Empty

```
+------------------------------+
| Notifications                |
|                              |
|     [bell icon, 40px]        |   --text-tertiary, 0.3 opacity
|                              |
|   No notifications yet.     |   14px, --text-secondary
|   Events will appear here   |   13px, --text-tertiary
|   as you use the system.    |
+------------------------------+
```

#### Command Palette No Results

```
+------------------------------------------+
| > quantum entanglement fuzzy     [Esc]   |
+------------------------------------------+
|                                          |
|   No matching actions or queries.        |   14px, --text-secondary
|                                          |
|   Try a shorter search term, or press    |   13px, --text-tertiary
|   Esc to close.                          |
+------------------------------------------+
```

---

### 11.20 — Z-Index Stacking Order

All z-index values used across this document, unified into a single authoritative scale. Components must use these layers — no ad-hoc z-index values.

| z-index | Layer     | Elements |
| :-----: | --------- | -------- |
| 1000    | Toast     | Toast notifications (11.14). Always on top. |
| 500     | Modal     | All modals: Command Palette (10.7), Keyboard Shortcuts (10.8), Onboarding (10.13), Checkpoint Dialog (11.10), Compare View (11.4), Confirmation Dialog (11.22). |
| 400     | Overlay   | Mobile drawer backdrop (11.13), modal backdrops. |
| 300     | Drawer    | Mobile drawer panel (11.13). |
| 200     | Popover   | Tooltips, popovers, dropdowns (11.23), glossary help (11.5), share dropdown (10.6), flag dropdown (10.5). |
| 100     | Header    | Fixed header bar (Section 1). |
| 95      | Progress  | Progress bar (11.1). |
| 90      | Banner    | Circuit breaker banner (5.6). |
| 85      | Warning   | Performance warning banners (11.11). |
| 1       | Content   | All page content, cards, sidebar. |
| 0       | Background| Page background. |

**Rules:**

- No component may use a z-index outside this table without updating this table.
- Toasts (1000) always render above modals (500) so error notifications remain visible during dialogs.
- Popovers (200) render above the header (100) so tooltips near the top edge are not clipped.
- The progress bar (95) renders below the header (100) and above the circuit breaker banner (90).

---

### 11.21 — Collapsed Sidebar State (1024px+)

Sprint 4 (4.2.2) defines collapsible sidebar at `lg`. This section specifies the collapsed visual state.

| Property                | 1024px                     | 1440px | 2560px | 3840px |
| ----------------------- | -------------------------- | ------ | ------ | ------ |
| Collapsed width         | 64px                       | 64px   | 72px   | 80px   |
| Expanded width          | 280px                      | 320px  | 400px  | 480px  |
| Collapse animation      | width 200ms ease-in        | same   | same   | same   |
| Expand animation        | width 250ms ease-out       | same   | same   | same   |
| Logo (collapsed)        | Icon only, 24px            | 24px   | 28px   | 32px   |
| Nav item (collapsed)    | Icon only, centered, 36x36 | 36x36  | 40x40  | 48x48  |
| Nav item tooltip        | Right-side tooltip, 120px  | same   | same   | same   |
| Nav item gap            | 4px                        | 4px    | 6px    | 8px    |
| Toggle button position  | Bottom of sidebar, centered | same  | same   | same   |
| Toggle button size      | 32x32                      | 32x32  | 36x36  | 44x44  |
| Toggle button icon      | Chevron left (collapse) / right (expand), 14px | same | 16px | 18px |
| History section         | Hidden                     | Hidden | Hidden | Hidden |
| Config section          | Hidden                     | Hidden | Hidden | Hidden |
| Stats section           | Hidden                     | Hidden | Hidden | Hidden |
| Search input            | Hidden                     | Hidden | Hidden | Hidden |
| "New Query" button      | "+" icon only, 36x36       | same   | 40x40  | 48x48  |

**Wireframe (1024px collapsed):**

```
+------+
| [Logo]| 64px
|      |
| [📊] | Dashboard
| [📦] | Batch
| [⚙]  | Settings
|      |
|      |
|      |
| [+]  | New Query
|      |
| [◀] | Collapse toggle
+------+
```

**Interaction Flow:**

1. Click toggle chevron to collapse/expand
2. Hover a nav item while collapsed shows a right-side tooltip with the item name
3. Keyboard: Sidebar collapse toggle is focusable; Enter/Space toggles
4. Main content area expands to fill the space freed by sidebar collapse
5. Collapsed state persisted in localStorage (`guardrail-sidebar-collapsed: true`)
6. On 1440px+, sidebar defaults to expanded; on 1024px, defaults to collapsed to maximize content area

**Accessibility:**

- Toggle: `aria-label="Collapse sidebar"` / `"Expand sidebar"`, `aria-expanded="true/false"`
- Collapsed nav items: `aria-label="[item name]"` (since text label is hidden)
- Screen reader: announces "Sidebar collapsed" / "Sidebar expanded" via `aria-live="polite"`

---

### 11.22 — Confirmation Dialog Component

Reusable confirmation dialog for destructive or irreversible actions. Used by: Settings "Clear query history" (11.3), Settings "Reset to Defaults" (11.3), Esc to clear long input (10.1).

| Property               | 320px                     | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ---------------------- | ------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Dialog width           | calc(100vw - 32px)        | 90vw   | 400px  | 420px  | 440px  | 520px  | 640px  |
| Dialog max-width       | 480px                     | 480px  | 480px  | 480px  | 480px  | 560px  | 680px  |
| Dialog padding         | 20px                      | 24px   | 28px   | 32px   | 32px   | 40px   | 48px   |
| Dialog radius          | 12px                      | 12px   | 12px   | 12px   | 12px   | 16px   | 20px   |
| Dialog shadow          | elevation-5               | same   | same   | same   | same   | same   | same   |
| Dialog bg              | --color-bg-primary        | same   | same   | same   | same   | same   | same   |
| Title font             | 18px/600                  | 18px   | 20px   | 20px   | 22px   | 26px   | 30px   |
| Title color            | --text-primary            | same   | same   | same   | same   | same   | same   |
| Body font              | 14px                      | 14px   | 14px   | 15px   | 15px   | 17px   | 20px   |
| Body color             | --text-secondary          | same   | same   | same   | same   | same   | same   |
| Button row margin-top  | 20px                      | 20px   | 24px   | 24px   | 28px   | 32px   | 40px   |
| Button height          | 44px                      | 44px   | 44px   | 44px   | 44px   | 52px   | 56px   |
| Button gap             | 8px                       | 8px    | 12px   | 12px   | 12px   | 16px   | 20px   |
| Button font            | 14px/500                  | 14px   | 14px   | 14px   | 15px   | 17px   | 20px   |
| Button radius          | 8px                       | 8px    | 8px    | 8px    | 10px   | 12px   | 16px   |
| Primary btn (confirm)  | Full-width                | Full-width | auto (min 120px) | same | same | same | same |
| Secondary btn (cancel) | Full-width                | Full-width | auto (min 120px) | same | same | same | same |
| Button layout          | Stacked (primary on top)  | Stacked | Inline, right-aligned | same | same | same | same |
| Backdrop               | Per 11.24 Modal System    | same   | same   | same   | same   | same   | same   |
| z-index                | 500 (per 11.20)           | same   | same   | same   | same   | same   | same   |

**Variants:**

| Variant | Primary Button Style | Primary Button Label | Use Case |
| --- | --- | --- | --- |
| Destructive | --error-500 bg, white text | "Delete" / "Clear" | Clear history, delete data |
| Caution | --warning-500 bg, white text | "Reset" / "Confirm" | Reset to defaults |
| Neutral | --primary-500 bg, white text | "Confirm" | Non-destructive confirmations |

**Wireframes:**

```
320px Mobile:
+-------------------------------+
| Clear Query History?          |  title
|                               |
| This will permanently delete  |  body
| all query history and cannot  |
| be undone.                    |
|                               |
| [    Clear All History      ] |  destructive primary
| [         Cancel            ] |  secondary
+-------------------------------+

1440px Desktop:
+---------------------------------------------+
| Clear Query History?                        |
|                                             |
| This will permanently delete all query      |
| history and cannot be undone.               |
|                                             |
|              [Cancel]  [Clear All History]  |
+---------------------------------------------+
```

**Accessibility:**

- Dialog: `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby`, `aria-describedby`
- Focus: autofocus on secondary (Cancel) button for destructive dialogs (safer default)
- Focus trapped within dialog
- Esc closes dialog (same as clicking Cancel)
- Screen reader: dialog title announced on open

---

### 11.23 — Dropdown Menu Component

Shared dropdown menu spec referenced by: Share dropdown (10.6), Flag dropdown (10.5), Settings dropdowns (11.3), Export dropdown, any future dropdown.

| Property                | 320px                      | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ----------------------- | -------------------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| Mode                    | Bottom sheet (full-width)  | Bottom sheet | Dropdown | Dropdown | Dropdown | Dropdown | Dropdown |
| Min-width               | 100%                       | 100%   | 180px  | 200px  | 200px  | 240px  | 280px  |
| Max-width               | 100%                       | 100%   | 320px  | 320px  | 360px  | 400px  | 480px  |
| Max-height              | 50vh                       | 50vh   | 320px  | 320px  | 360px  | 400px  | 480px  |
| Padding-y               | 8px                        | 8px    | 4px    | 4px    | 4px    | 6px    | 8px    |
| Border-radius           | 12px 12px 0 0              | same   | 8px    | 8px    | 10px   | 12px   | 16px   |
| Border                  | none                       | none   | 1px solid --border-default | same | same | 1.5px | 2px |
| Shadow                  | elevation-5                | same   | elevation-4 | same | same | same | same |
| Background              | --color-bg-primary         | same   | same   | same   | same   | same   | same   |
| z-index                 | 200 (per 11.20)            | same   | same   | same   | same   | same   | same   |
| Item height             | 48px                       | 48px   | 40px   | 40px   | 40px   | 48px   | 56px   |
| Item padding-x          | 16px                       | 16px   | 12px   | 12px   | 14px   | 16px   | 20px   |
| Item font               | 15px                       | 15px   | 14px   | 14px   | 14px   | 16px   | 20px   |
| Item icon size          | 20px                       | 20px   | 18px   | 18px   | 18px   | 20px   | 24px   |
| Item icon gap           | 12px                       | 12px   | 8px    | 8px    | 10px   | 12px   | 16px   |
| Item hover bg           | --color-bg-tertiary        | same   | same   | same   | same   | same   | same   |
| Item active bg          | --color-primary-50         | same   | same   | same   | same   | same   | same   |
| Divider height          | 1px                        | 1px    | 1px    | 1px    | 1px    | 1px    | 1px    |
| Divider margin-y        | 4px                        | 4px    | 4px    | 4px    | 4px    | 6px    | 8px    |
| Divider color           | --border-subtle            | same   | same   | same   | same   | same   | same   |
| Group header font       | 11px/600, uppercase, --text-tertiary | same | same | same | 12px | 14px | 16px |
| Group header padding    | 8px 16px 4px               | same   | 6px 12px 2px | same | same | 8px 16px 4px | 8px 20px 4px |

**Position Logic (768px+ dropdown mode):**

1. Default: below trigger element, left-aligned
2. If dropdown would overflow bottom of viewport: flip to above trigger
3. If dropdown would overflow right edge: right-align instead of left-align
4. Minimum 8px gap from viewport edges

**Mobile Bottom Sheet (320-480px):**

1. Slides up from bottom edge
2. Background backdrop: rgba(0,0,0,0.3)
3. Slide animation: 200ms ease-out
4. Swipe-down to dismiss
5. "Cancel" button at bottom (48px height)
6. Handle bar at top: 36px wide x 4px, --neutral-400, centered, radius 2px

**Wireframe:**

```
768px Dropdown:                     320px Bottom Sheet:
+--trigger button--+                +-------------------------------+
| ▼                |                |                               |
+------------------+                |                               |
| [📋] Copy Link   |                |          [===]                | handle bar
| [⬇] Export JSON  |                | +---------------------------+|
| [📄] Export PDF   |                | | [📋] Copy Link            ||
| [📊] Export CSV   |                | | [⬇] Export JSON           ||
+------------------+                | | [📄] Export PDF            ||
                                    | | [📊] Export CSV            ||
                                    | |                           ||
                                    | | [Cancel]                  ||
                                    | +---------------------------+|
                                    +-------------------------------+
```

**Accessibility:**

- Container: `role="menu"`, `aria-label="[dropdown purpose]"`
- Items: `role="menuitem"`
- Keyboard: Arrow up/down navigates, Enter selects, Esc closes
- Focus: first item receives focus on open; focus returns to trigger on close
- Disabled items: `aria-disabled="true"`, visually muted (--text-tertiary, no hover)
- Group headers: `role="presentation"` (not focusable)

---

### 11.24 — Modal System

Shared modal foundation inherited by all modal components. Individual modals (Command Palette, Keyboard Shortcuts, Onboarding, Checkpoint, Compare View, Confirmation) specify their own content layout on top of this base.

**Backdrop:**

| Property        | 320px              | 480px | 768px | 1024px | 1440px | 2560px | 3840px |
| --------------- | ------------------ | ----- | ----- | ------ | ------ | ------ | ------ |
| Background      | rgba(0,0,0,0.5)   | same  | same  | same   | same   | same   | same   |
| z-index         | 400 (per 11.20)    | same  | same  | same   | same   | same   | same   |
| Click to dismiss| Yes (unless aria-modal prevents) | same | same | same | same | same | same |
| Enter animation | opacity 0→1, 200ms ease-out | same | same | same | same | same | same |
| Exit animation  | opacity 1→0, 150ms ease-in | same | same | same | same | same | same |

**Modal Container:**

| Property            | 320px              | 480px  | 768px  | 1024px | 1440px | 2560px | 3840px |
| ------------------- | ------------------ | ------ | ------ | ------ | ------ | ------ | ------ |
| z-index             | 500 (per 11.20)    | same   | same   | same   | same   | same   | same   |
| Position            | Fixed, centered    | same   | same   | same   | same   | same   | same   |
| Enter animation     | opacity 0→1, scale 0.95→1, 250ms ease-out, 50ms delay after backdrop | same | same | same | same | same | same |
| Exit animation      | opacity 1→0, scale 1→0.95, 200ms ease-in | same | same | same | same | same | same |
| Background          | --color-bg-primary | same   | same   | same   | same   | same   | same   |
| Border              | none               | none   | 1px solid --border-default | same | same | 1.5px | 2px |
| Shadow              | elevation-5        | same   | same   | same   | same   | elevation-6 | same |
| Default border-radius | 12px             | 12px   | 12px   | 12px   | 12px   | 16px   | 20px   |
| Close button position | Top-right, 12px inset | same | 16px | 16px | 16px | 20px | 24px |
| Close button size   | 36x36              | 36x36  | 36x36  | 36x36  | 40x40  | 44x44  | 52x52  |
| Close button icon   | 16px "X"           | same   | same   | same   | 18px   | 20px   | 24px   |

**Body Scroll Lock:**

When any modal is open, `overflow: hidden` is applied to `<body>` to prevent background scrolling. On iOS, `-webkit-overflow-scrolling: touch` is also disabled on body.

**Focus Management:**

1. On open: focus moves to the first focusable element inside the modal (or autofocus element if specified)
2. Tab cycles within modal content (focus trap)
3. Shift+Tab cycles in reverse
4. Esc closes modal
5. On close: focus returns to the element that triggered the modal
6. If trigger element no longer exists (e.g., deleted item), focus moves to nearest logical sibling
7. Background content set to `inert` (not focusable, not announced by screen readers)

**Accessibility:**

- Container: `role="dialog"` (or `role="alertdialog"` for confirmations), `aria-modal="true"`
- Title: linked via `aria-labelledby`
- Description (if any): linked via `aria-describedby`
- Close button: `aria-label="Close"`

**Reduced Motion:**

When `prefers-reduced-motion: reduce` is active:
- Backdrop: instant show/hide (`opacity` transition 0ms)
- Modal: instant show/hide (`opacity` transition 0ms, no `scale` transform)
- All spring/ease animations disabled

**Nested Modal Policy:** Nested modals are **not supported**. If an action inside a modal requires a confirmation dialog, the parent modal must close first, then the confirmation dialog opens as a top-level modal. This prevents z-index stacking issues, focus trap conflicts, and accessibility complications. Implementation: the `openModal()` function checks `modalStack.length`; if > 0, it closes the current modal (with `onClose` callback) before opening the new one. A `queueModal()` function is available for sequential modal flows.

---

> **End of Skeleton Diagram Specification.** This document provides complete implementation specifications for every visual element in the Agentic Hallucination Guardrail dashboard, including all features from Sprint 4 UX Standards, Sprint 5 Acceptance Criteria, and the User-Centric Critique. All cross-document conflicts have been reconciled in Section 11.18, and this document is the canonical source for layout, sizing, and visual properties. A developer should build the entire UI from this document alone.
