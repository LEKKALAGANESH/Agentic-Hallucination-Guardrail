# Sprint 4 -- UI/UX Standards & Specifications

## Agentic Hallucination Guardrail (LLMOps Platform)

| Field              | Value                                      |
| ------------------ | ------------------------------------------ |
| **Document**       | Sprint 4 UI/UX Standards                   |
| **Version**        | 1.0.0                                      |
| **Status**         | Approved -- Ready for Implementation       |
| **Last Updated**   | 2026-03-21                                 |
| **Classification** | Internal -- Engineering Reference          |
| **Audience**       | Frontend Engineers, QA, Design, Product     |

---

## Table of Contents

1. [4.1 -- Loading Experience](#41--loading-experience)
2. [4.2 -- Responsiveness (Flawless Up to 4K)](#42--responsiveness-flawless-up-to-4k)
3. [4.3 -- Micro-Interactions & Polish](#43--micro-interactions--polish)
4. [4.4 -- Accessibility](#44--accessibility)
5. [4.5 -- Design System Foundations](#45--design-system-foundations)

---

## Guiding Principle

> **"Never show a blank screen."**
>
> Every millisecond of the user's experience is designed. From the instant a query leaves the client to the moment the final agent result renders, the interface communicates progress, maintains spatial stability, and respects every user -- regardless of device, ability, or connection speed.

---

## 4.1 -- Loading Experience

### 4.1.1 Design Philosophy

The loading experience is not a waiting room. It is the first phase of the result display. Skeleton cards are not placeholders -- they are the layout itself, rendered before data arrives. The user should perceive a single continuous flow from query submission to full result, with no jarring transitions, no layout shifts, and no blank states.

### 4.1.2 Loading Sequence Timeline

The following timeline governs every query submission. All times are measured from the moment the user triggers the query (click, Enter key, or API call).

| Time (ms)   | Event                                      | Visual State                                                                 |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------- |
| 0           | Query submitted                            | Submit button enters disabled + spinner state. Input field locks.            |
| 0           | Skeleton layout rendered                   | Full skeleton card grid appears instantly. No intermediate blank frame.      |
| 0           | Shimmer animation starts                   | Left-to-right gradient sweep begins on all skeleton cards (1.5s loop).      |
| 0           | Live Trace panel opens                     | Panel slides in from the right (200ms ease-out) or expands if already open. |
| 0           | Progress bar appears                       | Thin bar at top of dashboard, 0% width, color: `--color-primary-500`.       |
| 50-100      | WebSocket connection confirmed             | Live Trace shows "Connected" status indicator (green dot).                   |
| 100-200     | First agent acknowledged                   | Live Trace updates: first agent name appears with "Initializing" status.     |
| 200-800     | Agents begin processing                    | Live Trace cycles through agent statuses. Progress bar advances.             |
| 500-2000    | First agent completes                      | Its skeleton card crossfades (300ms) to real content. Shimmer stops on it.   |
| 1000-4000   | Subsequent agents complete                 | Each card crossfades individually as its agent finishes. Order varies.       |
| 2000-6000   | Final agent completes                      | Last skeleton card replaced. Progress bar hits 100%.                         |
| 6000+300    | Progress bar fades out                     | Bar fades (200ms ease-out) after holding at 100% for 300ms.                  |
| 6000+500    | Live Trace auto-collapses (if applicable)  | Panel compresses to summary strip unless user has pinned it open.            |

### 4.1.3 Skeleton Card Specifications

Every dashboard section has a purpose-built skeleton that mirrors the exact dimensions and layout of its loaded counterpart. Skeletons are not generic grey boxes -- they encode the structure of the content they will become.

#### Dashboard Overview Skeleton

```
+--------------------------------------------------+
|  [====  title bar  ====]          [==] [==] [==]  |  <- header row: title block + 3 action icon blocks
|                                                    |
|  [=========]  [=========]  [=========]             |  <- 3 metric cards (equal width)
|  [==      ]  [==      ]  [==      ]               |  <- subtitle lines within each
|  [========]  [========]  [========]                |  <- value blocks (taller, bolder weight)
|                                                    |
|  [==========================================]      |  <- chart area (aspect ratio 16:9)
|  [==========================================]      |
|  [==========================================]      |
|  [==========================================]      |
|                                                    |
|  [====  table header  ====]                        |  <- table header bar
|  [--- row ---]  [--- row ---]  [--- row ---]      |  <- 5 table row skeletons
|  [--- row ---]  [--- row ---]  [--- row ---]      |
|  [--- row ---]  [--- row ---]  [--- row ---]      |
|  [--- row ---]  [--- row ---]  [--- row ---]      |
|  [--- row ---]  [--- row ---]  [--- row ---]      |
+--------------------------------------------------+
```

| Skeleton Region        | Dimensions / Shape          | Corner Radius   | Background            |
| ---------------------- | --------------------------- | --------------- | --------------------- |
| Title bar              | 220px x 24px                | 4px             | `--skeleton-base`     |
| Action icons           | 32px x 32px each            | 50% (circle)    | `--skeleton-base`     |
| Metric card            | 1fr x 96px                  | 8px             | `--skeleton-base`     |
| Metric subtitle        | 60% of card width x 14px    | 4px             | `--skeleton-highlight`|
| Metric value           | 40% of card width x 28px    | 4px             | `--skeleton-highlight`|
| Chart area             | 100% x aspect-ratio 16/9    | 8px             | `--skeleton-base`     |
| Table header           | 100% x 40px                 | 4px 4px 0 0     | `--skeleton-base`     |
| Table row              | 100% x 48px                 | 0               | `--skeleton-base`     |

#### Confidence Gauge Skeleton

```
+----------------------------+
|                            |
|       [  arc shape  ]      |  <- semi-circle arc, stroke only
|       [             ]      |
|                            |
|     [=== value ===]        |  <- center value block
|     [== label ==]          |  <- label block below
|                            |
+----------------------------+
```

| Skeleton Region  | Dimensions / Shape              | Corner Radius | Background            |
| ---------------- | ------------------------------- | ------------- | --------------------- |
| Arc stroke       | 180deg arc, 120px radius, 12px  | N/A (stroke)  | `--skeleton-base`     |
| Value block      | 80px x 32px                     | 4px           | `--skeleton-highlight`|
| Label block      | 100px x 16px                    | 4px           | `--skeleton-base`     |

#### Live Trace Panel Skeleton

```
+-------------------------------+
| [== Agent Pipeline ==]        |  <- panel title
|                               |
| [*] Agent 1 ........... [==]  |  <- agent row: icon + name + status badge
| [*] Agent 2 ........... [==]  |
| [*] Agent 3 ........... [==]  |
| [*] Agent 4 ........... [==]  |
| [*] Agent 5 ........... [==]  |
|                               |
| [====== timing bar ======]    |  <- aggregate timing bar
+-------------------------------+
```

| Skeleton Region  | Dimensions / Shape        | Corner Radius | Background            |
| ---------------- | ------------------------- | ------------- | --------------------- |
| Panel title      | 160px x 20px              | 4px           | `--skeleton-base`     |
| Agent icon       | 24px x 24px               | 50%           | `--skeleton-base`     |
| Agent name       | 120px x 16px              | 4px           | `--skeleton-highlight`|
| Status badge     | 64px x 24px               | 12px          | `--skeleton-base`     |
| Timing bar       | 100% x 8px                | 4px           | `--skeleton-base`     |

### 4.1.4 Shimmer Animation Specification

The shimmer animation creates the perception of activity. It is a translucent gradient that sweeps across skeleton elements in a continuous loop.

| Property              | Value                                                                 |
| --------------------- | --------------------------------------------------------------------- |
| Gradient type         | Linear, 90deg (left to right)                                        |
| Color stops           | `--skeleton-base` 0%, `--skeleton-shimmer` 50%, `--skeleton-base` 100% |
| `--skeleton-base`     | Light: `hsl(220, 15%, 92%)` / Dark: `hsl(220, 15%, 18%)`            |
| `--skeleton-shimmer`  | Light: `hsl(220, 15%, 96%)` / Dark: `hsl(220, 15%, 24%)`            |
| Background size       | 200% 100%                                                            |
| Animation duration    | 1.5s                                                                 |
| Animation timing      | ease-in-out                                                          |
| Animation iteration   | infinite                                                             |
| Animation direction   | normal (always left-to-right)                                        |
| Reduced motion        | Replace shimmer with static `--skeleton-base` + subtle pulse opacity (0.6 to 1.0, 2s) |

### 4.1.5 Progressive Replacement (Optimistic Rendering)

When an agent completes and returns data, its corresponding skeleton card is replaced with real content. This happens per-card, not all-at-once.

**Technical Mechanism:**

1. Each dashboard section is wrapped in a container that holds two layers: the skeleton layer (rear) and the content layer (front).
2. On mount, the skeleton layer is visible (`opacity: 1`) and the content layer is invisible (`opacity: 0; pointer-events: none`).
3. When the associated agent's data arrives (via WebSocket message or React Query cache update), the component sets a `loaded` flag.
4. The `loaded` flag triggers a CSS transition:
   - Content layer: `opacity: 0 -> 1` over 300ms ease-out.
   - Skeleton layer: `opacity: 1 -> 0` over 300ms ease-out (simultaneous).
   - After transition completes (detected via `onTransitionEnd`), the skeleton DOM node is unmounted to free memory.
5. The content layer is pre-rendered in the background (hidden) so that the crossfade reveals a fully painted frame -- no flash of unstyled content.

**Layout Stability Rules:**

- Skeleton cards and content cards MUST occupy identical bounding boxes. No Cumulative Layout Shift (CLS) is permitted during replacement.
- If content is taller than the skeleton (e.g., a table with more rows than expected), the container must expand smoothly (`max-height` transition, 300ms ease-out) after the crossfade completes.
- If content is shorter, the container must shrink smoothly using the same transition.

**Replacement Order:**

Cards replace in the order their agents complete. There is no enforced visual ordering. The user sees whichever results arrive first. This communicates speed and real-time processing.

### 4.1.6 Live Trace Panel

The Live Trace panel is the user's real-time window into the agent pipeline. It shows which agents are running, which have completed, and what the current bottleneck is.

**Panel States:**

| State        | Visual Treatment                                                        |
| ------------ | ----------------------------------------------------------------------- |
| Collapsed    | 48px strip at bottom-right showing agent count and overall status icon  |
| Expanded     | 320px-wide side panel (right-docked) showing full agent list            |
| Pinned       | Same as expanded, but does not auto-collapse after completion           |
| Disconnected | Red border, "Reconnecting..." message, retry countdown                 |

**Agent Row States:**

| Agent Status   | Icon              | Color                    | Animation                        |
| -------------- | ----------------- | ------------------------ | -------------------------------- |
| Queued         | Clock             | `--color-neutral-400`    | None                             |
| Initializing   | Spinner (12px)    | `--color-primary-400`    | Spin, 1s linear infinite         |
| Running        | Pulse dot (8px)   | `--color-primary-500`    | Pulse scale 1.0-1.4, 1s ease    |
| Completed      | Checkmark         | `--color-success-500`    | Pop-in scale 0->1, 200ms ease   |
| Failed         | X-circle          | `--color-error-500`      | Shake, 300ms                     |
| Timed Out      | Clock-alert       | `--color-warning-500`    | None (static)                    |

**Update Mechanism:**

- The Live Trace panel subscribes to a dedicated WebSocket channel (`ws://api/trace/stream`).
- Each message contains: `{ agentId, status, startedAt, completedAt, metadata }`.
- On each message, the corresponding agent row updates its icon, color, and timing display.
- A horizontal timeline bar at the bottom of the panel shows all agents as colored segments, building in real time as agents complete. This gives an at-a-glance view of parallelism and bottlenecks.

### 4.1.7 Progress Bar Estimation

The progress bar at the top of the dashboard provides a linear estimate of overall completion.

**Estimation Algorithm:**

1. On query submission, fetch historical average durations per agent from the metrics cache (stored client-side from previous sessions, updated via API).
2. Sum all agent expected durations to get `totalExpectedMs`.
3. As each agent completes, add its `actualDurationMs` to `completedMs`.
4. For still-running agents, interpolate based on elapsed time vs. their individual expected duration: `estimatedProgress = min(elapsedMs / expectedMs, 0.95)` (capped at 95% to avoid premature completion appearance).
5. Overall progress = `(completedMs + sum(runningAgentEstimates)) / totalExpectedMs`.
6. Clamp the bar to never decrease (monotonic progress). If re-estimation produces a lower value, hold the current position.
7. When all agents complete, snap to 100% (with a 150ms ease-out fill animation).

**Visual Specification:**

| Property          | Value                                          |
| ----------------- | ---------------------------------------------- |
| Height            | 3px (resting), 4px (hover)                     |
| Position          | Fixed, top of dashboard content area           |
| Background track  | `--color-neutral-200` (light) / `--color-neutral-700` (dark) |
| Fill color        | `--color-primary-500`                          |
| Fill transition   | `width` 300ms ease-out                         |
| Completion color  | `--color-success-500` (transitions on 100%)    |
| Border radius     | 0 (flush with container edges)                 |

### 4.1.8 Fallback Behavior -- Exceeded Expectations

When loading exceeds the estimated duration, the system must degrade gracefully rather than leave the user in a silent waiting state.

| Threshold             | Behavior                                                                              |
| --------------------- | ------------------------------------------------------------------------------------- |
| > 1.5x expected time  | Progress bar transitions to indeterminate mode (animated stripe pattern, no %).        |
| > 2x expected time    | Toast notification: "This is taking longer than usual. Agents are still working."      |
| > 3x expected time    | Toast notification with action: "Still working... [Cancel Query] [View Partial Results]" |
| > 30 seconds absolute | "View Partial Results" button appears in the dashboard header, replacing any completed skeleton cards with whatever data is available. Incomplete cards show a "Pending" badge. |
| > 60 seconds absolute | Auto-surface partial results. Incomplete cards show "Timed Out" badge with retry button per agent. |
| WebSocket disconnect  | Live Trace shows "Reconnected" state. Polling fallback activates (2s interval). Toast: "Live updates interrupted. Retrying..." |
| Complete failure      | Full error state card replaces the dashboard: icon, message, [Retry] button, [View Logs] link. No skeleton remains visible. |

**Partial Results Rendering:**

- Completed agent cards render normally.
- In-progress agent cards show their skeleton with an overlaid semi-transparent badge: "Still processing..." with a spinner.
- Failed agent cards show an error state within the card boundary: red-tinted background, error icon, brief message, [Retry] button.
- The dashboard layout remains stable throughout -- no cards appear or disappear, only their internal content changes.

---

## 4.2 -- Responsiveness (Flawless Up to 4K)

### 4.2.1 Breakpoint System

Seven breakpoints define the responsive behavior of every component. These are not suggestions -- they are mandatory testing gates.

| Token Name     | Width (px) | Classification     | Primary Devices                          |
| -------------- | ---------- | ------------------ | ---------------------------------------- |
| `xs`           | 320        | Small phone        | iPhone SE, Galaxy S series (compact)     |
| `sm`           | 480        | Large phone        | iPhone Pro Max, Pixel 7                  |
| `md`           | 768        | Tablet portrait    | iPad Mini, iPad Air (portrait)           |
| `lg`           | 1024       | Tablet landscape   | iPad Pro (landscape), small laptops      |
| `xl`           | 1440       | Desktop            | Standard monitors, laptops               |
| `2xl`          | 2560       | QHD / Ultrawide    | 27" QHD monitors, ultrawides             |
| `4k`           | 3840       | 4K UHD             | 32" 4K monitors, large displays          |

**Breakpoint Implementation:**

All breakpoints use `min-width` (mobile-first) media queries:

```
--bp-xs:  320px
--bp-sm:  480px
--bp-md:  768px
--bp-lg:  1024px
--bp-xl:  1440px
--bp-2xl: 2560px
--bp-4k:  3840px
```

**Updated Wireframes Cross-Reference:**

For complete wireframe diagrams at breakpoints not fully specified here, see `skeleton-diagrams.md`:
- **768px (Tablet Portrait):** Section 4, wireframe 3 — 2-column grid with collapsible sidebar, trace panel as bottom sheet
- **2560px (QHD):** Section 4, wireframe 6 — 3-column grid, expanded sidebar (400px), increased padding (64px), enlarged font scale
- **3840px (4K UHD):** Section 4, wireframe 7 — 4-column grid, max-width 3400px centered, 96px container padding, all spacing tokens scaled to `--space-12`

> These wireframes define the pixel-exact layout at each breakpoint. The Sprint 4 breakpoint tokens above define the responsive behavior rules.

### 4.2.2 Layout Behavior Per Breakpoint

#### `xs` (320px) -- Small Phone

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 1                                                                     |
| Navigation             | Bottom tab bar (fixed, 56px height). Hamburger menu for overflow.     |
| Dashboard metrics      | Stacked vertically, full width. Horizontal scroll carousel optional.  |
| Chart                  | Full width. Simplified axis labels. Touch-drag to pan.                |
| Table                  | Card-list view (each row becomes a stacked card).                     |
| Live Trace             | Full-screen overlay (bottom sheet, swipe to dismiss).                 |
| Confidence Gauge       | 100% width, centered. Arc radius scales to 80px.                     |
| Side panels            | Hidden. Accessible via bottom sheet or full-screen overlay.           |
| Padding                | 16px horizontal.                                                      |
| Gap                    | 12px between cards.                                                   |

#### `sm` (480px) -- Large Phone

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 1 (2 for metric cards only)                                          |
| Navigation             | Bottom tab bar (same as xs).                                          |
| Dashboard metrics      | 2-column grid for metric cards. Chart remains full-width.             |
| Table                  | Card-list view (same as xs, but cards are slightly wider).            |
| Live Trace             | Bottom sheet (60% height, draggable).                                 |
| Confidence Gauge       | 100% width. Arc radius scales to 100px.                              |
| Padding                | 16px horizontal.                                                      |
| Gap                    | 12px between cards.                                                   |

#### `md` (768px) -- Tablet Portrait

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 2                                                                     |
| Navigation             | Top horizontal bar. No hamburger -- all primary items visible.        |
| Dashboard metrics      | 3-column grid for metric cards.                                       |
| Chart                  | Full width, spans both columns. Full axis labels restored.            |
| Table                  | Standard table layout returns. Horizontal scroll if > 5 columns.     |
| Live Trace             | Right-docked panel, 280px wide. Pushes content left.                  |
| Confidence Gauge       | Inline within grid. Arc radius 100px.                                 |
| Padding                | 24px horizontal.                                                      |
| Gap                    | 16px between cards.                                                   |

#### `lg` (1024px) -- Tablet Landscape / Small Laptop

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 3                                                                     |
| Navigation             | Left sidebar (240px, collapsible to 64px icon rail).                  |
| Dashboard metrics      | 3-column grid. Cards gain internal sparkline charts.                  |
| Chart                  | Spans 2 of 3 columns. Tooltip on hover enabled.                      |
| Table                  | Full table. Sortable column headers active. Up to 8 visible columns. |
| Live Trace             | Right-docked panel, 300px. Overlay mode available.                    |
| Confidence Gauge       | Inline. Arc radius 120px.                                             |
| Padding                | 32px horizontal (excluding sidebar).                                  |
| Gap                    | 20px between cards.                                                   |

#### `xl` (1440px) -- Standard Desktop

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 4                                                                     |
| Navigation             | Left sidebar expanded (240px) by default.                             |
| Dashboard metrics      | 4-column grid. Full metric detail visible.                            |
| Chart                  | Spans 3 of 4 columns. Full interactivity (zoom, pan, brush select).  |
| Table                  | Full table. All columns visible. Inline editing enabled.              |
| Live Trace             | Right-docked panel, 320px. Persistent by default.                     |
| Confidence Gauge       | Inline. Arc radius 120px. Peer comparison ring visible.               |
| Padding                | 32px horizontal.                                                      |
| Gap                    | 24px between cards.                                                   |

#### `2xl` (2560px) -- QHD / Ultrawide

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 6                                                                     |
| Navigation             | Left sidebar expanded (280px). Secondary nav section visible.         |
| Dashboard metrics      | 6-column grid. Metric cards show trend arrows and mini charts.        |
| Chart                  | Spans 4 of 6 columns. Higher data density, more tick marks.          |
| Table                  | Full table. Comfortable cell padding. Row-hover detail panel.         |
| Live Trace             | Right-docked panel, 360px. Timeline visualization gains detail.       |
| Confidence Gauge       | Inline. Arc radius 140px.                                             |
| Max content width      | 2200px centered with auto margins if viewport exceeds this.          |
| Padding                | 40px horizontal.                                                      |
| Gap                    | 24px between cards.                                                   |

#### `4k` (3840px) -- 4K UHD

| Aspect                 | Behavior                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| Grid columns           | 8                                                                     |
| Navigation             | Left sidebar (320px). All nav items expanded with descriptions.       |
| Dashboard metrics      | 8-column grid (or 4-column double-height for richer cards).          |
| Chart                  | Spans 6 of 8 columns. Maximum data resolution. Sub-pixel rendering.  |
| Table                  | Full table. Every column visible. Generous whitespace.                |
| Live Trace             | Right-docked panel, 400px. Full agent dependency graph visible.       |
| Confidence Gauge       | Inline. Arc radius 160px. Full annotation ring.                       |
| Max content width      | 3200px centered.                                                      |
| Padding                | 48px horizontal.                                                      |
| Gap                    | 32px between cards.                                                   |

### 4.2.3 Fluid Typography Scale

All typography uses CSS `clamp()` functions to scale smoothly between breakpoints. No text should ever overflow, truncate unexpectedly, or become unreadable at any viewport width.

| Token               | Min (320px)  | Preferred         | Max (3840px) | Weight  | Line Height | Usage                              |
| -------------------- | ------------ | ----------------- | ------------ | ------- | ----------- | ---------------------------------- |
| `--font-display-1`   | 28px         | 2.5vw + 0.5rem   | 56px         | 700     | 1.1         | Page titles, hero metrics          |
| `--font-display-2`   | 24px         | 2vw + 0.5rem     | 44px         | 700     | 1.15        | Section titles                     |
| `--font-heading-1`   | 20px         | 1.5vw + 0.5rem   | 36px         | 600     | 1.2         | Card titles, panel headers         |
| `--font-heading-2`   | 18px         | 1.25vw + 0.5rem  | 28px         | 600     | 1.25        | Subsection headers                 |
| `--font-heading-3`   | 16px         | 1vw + 0.5rem     | 24px         | 600     | 1.3         | Widget titles, table headers       |
| `--font-body-lg`     | 16px         | 0.9vw + 0.5rem   | 20px         | 400     | 1.5         | Primary body text                  |
| `--font-body`        | 14px         | 0.8vw + 0.5rem   | 18px         | 400     | 1.5         | Default body text                  |
| `--font-body-sm`     | 13px         | 0.7vw + 0.4rem   | 16px         | 400     | 1.45        | Secondary text, descriptions       |
| `--font-caption`     | 12px         | 0.6vw + 0.4rem   | 14px         | 400     | 1.4         | Labels, timestamps, metadata       |
| `--font-overline`    | 10px         | 0.5vw + 0.3rem   | 13px         | 600     | 1.4         | Overline labels, badges            |
| `--font-code`        | 13px         | 0.7vw + 0.4rem   | 16px         | 400     | 1.6         | Code blocks, monospace content     |

**Implementation Pattern:**

```
font-size: clamp(<min>, <preferred>, <max>);
```

**Overflow Prevention Rules:**

1. All text containers must have `overflow-wrap: break-word`.
2. Long strings without spaces (URLs, hashes, agent IDs) must have `word-break: break-all` on their container.
3. Single-line labels that might overflow must use `text-overflow: ellipsis` with a `title` attribute for the full value.
4. No text element may ever cause horizontal scrolling on the viewport.

### 4.2.4 Grid System

The layout uses CSS Grid as the primary system, with Container Queries enabling component-level responsiveness independent of viewport width.

**Dashboard Grid:**

| Breakpoint | Columns              | Column Width   | Gap     | Margin (horizontal) |
| ---------- | -------------------- | -------------- | ------- | ------------------- |
| `xs`       | 1                    | 1fr            | 12px    | 16px                |
| `sm`       | 2                    | 1fr            | 12px    | 16px                |
| `md`       | 2                    | 1fr            | 16px    | 24px                |
| `lg`       | 3                    | 1fr            | 20px    | 32px                |
| `xl`       | 4                    | 1fr            | 24px    | 32px                |
| `2xl`      | 6                    | 1fr            | 24px    | 40px                |
| `4k`       | 8                    | 1fr            | 32px    | 48px                |

**Subgrid Usage:**

Components that contain their own internal grids (e.g., metric cards with icon + value + trend) must use `subgrid` to align with the parent grid tracks when the browser supports it, falling back to independent grid definitions.

### 4.2.5 Container Query Strategy

Container Queries decouple component responsiveness from the viewport. A component placed in the main content area, a sidebar, or a modal should adapt to its container's width, not the window.

**Container Definition:**

Every major layout region is declared as a containment context:

| Container Name          | Element                              | Containment Type     |
| ----------------------- | ------------------------------------ | -------------------- |
| `dashboard-main`        | Main content area                    | `inline-size`        |
| `sidebar-nav`           | Left navigation sidebar              | `inline-size`        |
| `live-trace`            | Live Trace panel                     | `inline-size`        |
| `metric-card`           | Individual metric card wrapper       | `inline-size`        |
| `chart-container`       | Chart wrapper                        | `inline-size`        |
| `table-container`       | Data table wrapper                   | `inline-size`        |
| `modal-body`            | Modal content area                   | `inline-size`        |

**Container Query Breakpoints:**

Components respond to their container width using these thresholds:

| Token        | Container Width | Typical Trigger                        |
| ------------ | --------------- | -------------------------------------- |
| `cq-compact` | < 200px         | Sidebar-docked widget, collapsed panel |
| `cq-narrow`  | 200px - 399px   | Sidebar, narrow modal                  |
| `cq-medium`  | 400px - 639px   | Half-width panel, standard modal       |
| `cq-wide`    | 640px - 899px   | Main content (mobile/tablet)           |
| `cq-full`    | >= 900px        | Main content (desktop+)               |

**Component Adaptation Rules:**

| Component          | `cq-compact`          | `cq-narrow`             | `cq-medium`            | `cq-wide`              | `cq-full`               |
| ------------------ | --------------------- | ----------------------- | ---------------------- | ----------------------- | ----------------------- |
| MetricCard         | Icon only, no text    | Icon + value, no trend  | Icon + value + trend   | Full card with sparkline| Full + comparison       |
| ConfidenceGauge    | Numeric only (no arc) | Mini arc (60px radius)  | Standard arc (100px)   | Standard + label        | Full arc + annotations  |
| DataTable          | Hidden / "View" link  | 2-col card list         | 3-col table            | Full table, scroll      | Full table, all cols    |
| Chart              | Sparkline only        | Mini chart, no axes     | Chart with Y-axis      | Full chart              | Full + brush select     |
| LiveTrace agent row| Dot + status color    | Icon + name (truncated) | Icon + name + status   | Full row + timing       | Full + dependency info  |

### 4.2.6 Touch Targets

All interactive elements must meet minimum touch target sizes for accessibility and usability on touch devices.

| Element Type           | Minimum Size | Recommended Size | Notes                                      |
| ---------------------- | ------------ | ---------------- | ------------------------------------------ |
| Buttons                | 44x44px      | 48x48px          | Includes padding around visible button.    |
| Icon buttons           | 44x44px      | 44x44px          | Tap area may extend beyond visible icon.   |
| Links (inline)         | 44px height  | N/A              | Achieved via padding. Text width is fluid. |
| Table rows (clickable) | 48px height  | 56px height      | Entire row is the tap target.              |
| Checkboxes / Radios    | 44x44px      | 44x44px          | Includes label as part of tap target.      |
| Tab items              | 44px height  | 48px height      | Minimum 44px width or text width + 24px.   |
| Dropdown items         | 44px height  | 48px height      | Full width of dropdown.                    |
| Close buttons (X)      | 44x44px      | 44x44px          | Common miss-tap target. Never smaller.     |

**Spacing Between Targets:**

Adjacent touch targets must have a minimum 8px gap between their tap areas (not their visible boundaries -- the tap area itself).

**Stylus Input Testing:**

Stylus (pen) input introduces additional precision and hover considerations beyond finger touch:
- Stylus tip precision is ~1px (vs. ~10px for fingertip), so minimum touch targets of 44x44px are still required for consistency, but stylus users may benefit from smaller secondary targets (32x32px minimum).
- `pointer: fine` media query may be used to detect stylus/mouse input and offer refined hit targets where appropriate.
- Hover states must be tested with stylus hover (many stylus devices support hover at ~10mm distance). Ensure hover previews (tooltips, popovers) activate correctly on stylus hover and dismiss on stylus lift.
- Test devices: Apple Pencil (iPad), Samsung S Pen, Wacom stylus on Windows tablets.
- All touch event handlers must use `pointerdown`/`pointerup` (unified pointer events) rather than `touchstart`/`touchend` to correctly handle stylus, touch, and mouse input from a single handler.

### 4.2.7 Responsive Testing Checklist

Every component and page must pass this checklist at all 7 breakpoints before it can be merged.

| #  | Check                                               | Pass Criteria                                                      |
| -- | --------------------------------------------------- | ------------------------------------------------------------------ |
| 1  | No horizontal overflow                              | `document.body.scrollWidth <= window.innerWidth` at every bp       |
| 2  | No text truncation (unless intentional with tooltip) | Visual inspection at each bp. `title` attr present if truncated.   |
| 3  | No overlapping elements                             | No z-index collisions. No absolute-positioned elements escaping.   |
| 4  | Touch targets meet minimums                         | Audit all interactive elements with dev tools at `xs` and `sm`.    |
| 5  | Images/charts scale without distortion              | `object-fit` and `aspect-ratio` verified.                          |
| 6  | Grid layout is correct                              | Column count matches spec at each bp. No orphaned single items.    |
| 7  | Navigation mode is correct                          | Bottom bar on mobile, sidebar on desktop. Verified at each bp.     |
| 8  | Live Trace panel mode is correct                    | Bottom sheet on mobile, side panel on desktop. Transition smooth.  |
| 9  | Typography scale is correct                         | Headings, body, captions all match fluid scale. No fixed px leaks. |
| 10 | Skeleton cards match loaded layout exactly           | No CLS. Dimensions identical between skeleton and loaded states.   |
| 11 | Container queries fire correctly                    | Components in sidebar, modal, and main area all adapt properly.    |
| 12 | Spacing/gaps match spec                             | Padding and gap values verified at each bp.                        |
| 13 | 4K renders without excessive whitespace             | Content max-width applied. Grid expands to fill. No "postage stamp" layouts. |
| 14 | 320px renders without broken layout                 | Single-column stack. All content accessible. No clipping.          |

---

## 4.3 -- Micro-Interactions & Polish

### 4.3.1 Transition Specification Table

Every animated property in the application is governed by the following specifications. No transitions should be added ad-hoc -- they must reference this table or extend it through a design review.

| Element                     | Property            | Duration | Easing       | Delay  | Notes                                       |
| --------------------------- | ------------------- | -------- | ------------ | ------ | ------------------------------------------- |
| Button (primary)            | background-color    | 200ms    | ease-out     | 0ms    | Hover and active states.                    |
| Button (primary)            | transform (scale)   | 150ms    | ease-out     | 0ms    | Active: scale(0.97). Subtle press effect.   |
| Button (primary)            | box-shadow          | 200ms    | ease-out     | 0ms    | Hover: elevate shadow. Active: reduce.      |
| Button (icon)               | background-color    | 150ms    | ease-out     | 0ms    | Subtle bg fill on hover.                    |
| Button (icon)               | transform (scale)   | 150ms    | ease-out     | 0ms    | Hover: scale(1.05). Active: scale(0.95).    |
| Card                        | box-shadow          | 200ms    | ease-out     | 0ms    | Hover: elevate from shadow-1 to shadow-2.   |
| Card                        | transform (translateY)| 200ms  | ease-out     | 0ms    | Hover: translateY(-2px).                    |
| Skeleton -> Content         | opacity             | 300ms    | ease-out     | 0ms    | Crossfade during progressive replacement.   |
| Live Trace panel open       | transform (translateX)| 200ms  | ease-out     | 0ms    | Slide in from right.                        |
| Live Trace panel close      | transform (translateX)| 150ms  | ease-in      | 0ms    | Slide out to right. Slightly faster.        |
| Live Trace agent status     | opacity, transform  | 250ms    | ease-out     | 0ms    | Status icon crossfade + scale pop.          |
| Progress bar fill           | width               | 300ms    | ease-out     | 0ms    | Smooth width transitions.                   |
| Progress bar completion     | background-color    | 200ms    | ease-out     | 0ms    | Primary -> success color.                   |
| Progress bar fade-out       | opacity             | 200ms    | ease-out     | 300ms  | 300ms delay after reaching 100%.            |
| Tooltip appear              | opacity, transform  | 150ms    | ease-out     | 300ms  | 300ms hover delay before showing.           |
| Tooltip disappear           | opacity             | 100ms    | ease-in      | 0ms    | Instant on mouse-leave.                     |
| Dropdown open               | opacity, transform  | 200ms    | ease-out     | 0ms    | Scale from 0.95 + fade. Transform-origin: top. |
| Dropdown close              | opacity             | 150ms    | ease-in      | 0ms    | Fade only. No scale on close.               |
| Modal open                  | opacity (backdrop)  | 200ms    | ease-out     | 0ms    | Backdrop fade.                              |
| Modal open                  | opacity, transform  | 250ms    | ease-out     | 50ms   | Content: scale(0.95)->1 + fade. 50ms after backdrop. |
| Modal close                 | opacity, transform  | 200ms    | ease-in      | 0ms    | Reverse of open. Content first, then backdrop. |
| Toast enter                 | transform (translateX)| 300ms  | ease-out     | 0ms    | Slide in from right edge.                   |
| Toast exit                  | opacity, transform  | 200ms    | ease-in      | 0ms    | Fade + slide right.                         |
| Tab indicator               | transform (translateX), width | 250ms | ease-out | 0ms | Slides between tab positions.               |
| Sidebar expand              | width               | 250ms    | ease-out     | 0ms    | 64px -> 240px.                              |
| Sidebar collapse            | width               | 200ms    | ease-in      | 0ms    | 240px -> 64px.                              |
| Confidence Gauge arc        | stroke-dashoffset   | 800ms    | ease-out     | 200ms  | Animated on load. Delayed 200ms for drama.  |
| Confidence Gauge value      | (counter animation) | 600ms    | ease-out     | 400ms  | Number counts up from 0 to final value.     |
| Chart data points           | opacity             | 300ms    | ease-out     | 0ms    | Staggered: 50ms per point.                  |
| Focus ring                  | box-shadow          | 100ms    | ease-out     | 0ms    | Instant-feel but not literally instant.      |

### 4.3.2 Hover State Specifications

| Component              | Property Change on Hover                                               | Visual Description                                    |
| ---------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------- |
| Primary Button         | `background-color: --color-primary-600`, `box-shadow: shadow-2`        | Darkens slightly, lifts.                              |
| Secondary Button       | `background-color: --color-primary-50`, `border-color: --color-primary-400` | Subtle fill appears inside border.               |
| Ghost Button           | `background-color: --color-neutral-100`                                | Faint background reveals.                             |
| Icon Button            | `background-color: --color-neutral-100`, `transform: scale(1.05)`     | Circle fill appears, slight grow.                     |
| Card                   | `box-shadow: shadow-2`, `transform: translateY(-2px)`                  | Lifts off the page.                                   |
| Table Row              | `background-color: --color-neutral-50`                                 | Row highlights.                                       |
| Link (text)            | `color: --color-primary-600`, `text-decoration-color: currentColor`    | Underline becomes fully opaque.                       |
| Nav Item               | `background-color: --color-neutral-100`, `color: --color-primary-600`  | Background fill + text color shift.                   |
| Sidebar Item           | `background-color: --color-neutral-100`, left border accent 3px       | Indent marker appears.                                |
| Tab                    | `color: --color-primary-600`                                           | Text color shifts. Indicator does not move on hover.  |
| Badge                  | `transform: scale(1.05)`                                               | Slight grow.                                          |
| Confidence Gauge arc   | `filter: brightness(1.1)`                                              | Arc brightens slightly.                               |
| Live Trace agent row   | `background-color: --color-neutral-50`                                 | Row highlights for click affordance.                  |
| Toggle switch          | `box-shadow: 0 0 0 2px --color-primary-200`                           | Glow ring around track.                               |

### 4.3.3 Focus Ring Specifications

Focus rings are mandatory on every interactive element. They must be visible, consistent, and not obscured by surrounding elements.

| Property                | Value                                               |
| ----------------------- | --------------------------------------------------- |
| Style                   | `box-shadow` (not `outline` -- to respect border-radius) |
| Color (light mode)      | `--color-primary-500` at 50% opacity                |
| Color (dark mode)       | `--color-primary-400` at 60% opacity                |
| Width                   | 3px                                                 |
| Offset                  | 2px (gap between element edge and ring)             |
| Border radius           | Matches element's border-radius + offset            |
| High contrast override  | Solid `--color-primary-500` at 100% opacity, 3px    |
| Transition              | 100ms ease-out                                      |

**Focus Ring Rules:**

1. Focus rings appear ONLY on keyboard focus (`:focus-visible`), never on mouse click.
2. Elements with custom focus states (e.g., input fields with border-color change) must ALSO show the focus ring. The ring is additive, not a replacement.
3. Focus rings must never be clipped by `overflow: hidden` on parent containers. If a parent clips, the ring must be implemented with `outline` + `outline-offset` as a fallback.
4. The ring must be visible against both light and dark backgrounds. The dual-opacity specification above ensures this.

### 4.3.4 Toast Notification System

Toast notifications communicate background events (agent completions, errors, system messages) without interrupting the user's current task.

**Position and Layout:**

| Property              | Value                                                       |
| --------------------- | ----------------------------------------------------------- |
| Position              | Fixed, bottom-right corner                                  |
| Bottom offset         | 24px from viewport bottom                                   |
| Right offset          | 24px from viewport right                                    |
| Mobile position       | Fixed, bottom-center, full width minus 32px margin          |
| Width                 | 360px (desktop), `calc(100vw - 32px)` (mobile)             |
| Max width             | 480px                                                       |
| Z-index               | `--z-toast` (900)                                           |

**Toast Anatomy:**

```
+---------------------------------------------+
| [icon]  Title text              [X close]    |
|         Description text (optional)          |
|         [Action Button] (optional)           |
+---------------------------------------------+
```

| Region      | Typography         | Color                                 |
| ----------- | ------------------ | ------------------------------------- |
| Icon        | 20px               | Matches severity color                |
| Title       | `--font-body`, 600 | `--color-neutral-900`                 |
| Description | `--font-body-sm`   | `--color-neutral-600`                 |
| Action      | `--font-body-sm`, 600 | `--color-primary-600`              |
| Close       | 16px icon          | `--color-neutral-400`                 |

**Severity Variants:**

| Variant   | Icon        | Left Border Color          | Background                     |
| --------- | ----------- | -------------------------- | ------------------------------ |
| Info      | Info circle | `--color-info-500`         | `--color-info-50`              |
| Success   | Checkmark   | `--color-success-500`      | `--color-success-50`           |
| Warning   | Alert tri   | `--color-warning-500`      | `--color-warning-50`           |
| Error     | X circle    | `--color-error-500`        | `--color-error-50`             |
| Neutral   | Bell        | `--color-neutral-300`      | `--color-neutral-50`           |

**Timing and Stacking:**

| Behavior              | Specification                                                       |
| --------------------- | ------------------------------------------------------------------- |
| Auto-dismiss (info)   | 5000ms                                                              |
| Auto-dismiss (success)| 4000ms                                                              |
| Auto-dismiss (warning)| 8000ms                                                              |
| Auto-dismiss (error)  | No auto-dismiss. Manual close required.                             |
| Stacking direction    | Upward (newest at bottom, older toasts shift up).                   |
| Max visible           | 3 toasts. 4th toast collapses into "+N more" counter.               |
| Stack gap             | 8px between toasts.                                                 |
| Pause on hover        | Auto-dismiss timer pauses while any toast is hovered.               |
| Dismiss gesture       | Swipe right (mobile) or click X.                                    |
| Dismiss animation     | Slide right + fade, 200ms ease-in. Stack re-flows with 200ms transition. |
| Duplicate suppression | If an identical toast (same title + description) exists, increment a counter badge instead of creating a new toast. |

### 4.3.5 Reduced Motion Support

Users who set `prefers-reduced-motion: reduce` in their OS settings receive a fully functional but calmer experience.

| Standard Animation                 | Reduced Motion Alternative                              |
| ---------------------------------- | ------------------------------------------------------- |
| Shimmer sweep on skeletons         | Static skeleton with subtle opacity pulse (0.6-1.0, 2s) |
| Card hover translateY + shadow     | Background-color change only (no movement)              |
| Skeleton-to-content crossfade      | Instant swap (opacity: 0 -> 1 in 0ms)                   |
| Live Trace panel slide             | Instant show/hide (display toggle)                       |
| Toast slide-in                     | Instant appear (opacity: 0 -> 1 in 0ms)                 |
| Toast slide-out                    | Instant disappear                                        |
| Confidence Gauge arc animation     | Arc renders at final position instantly                   |
| Confidence Gauge value counter     | Value renders as final number instantly                   |
| Progress bar width transition      | Width updates instantly (still accurate, just no lerp)   |
| Modal scale + fade                 | Opacity only, 100ms                                      |
| Dropdown scale + fade              | Opacity only, 100ms                                      |
| Chart data point stagger           | All points appear simultaneously                          |
| Button press scale                 | No scale. Color change only.                             |
| Spinner icon rotation              | Replace with static "..." text or three-dot icon          |
| Pulse dot (agent running)          | Static solid dot                                          |

**Implementation Rule:**

All animation code must be wrapped in a motion-preference check. The pattern is:

1. Define animations in a `motion-safe` context.
2. Define reduced alternatives in a `motion-reduced` context.
3. Never rely on animation for conveying information -- always have a static fallback that communicates the same state.

### 4.3.6 Framer Motion Specifications -- Live Trace Panel

The Live Trace panel is the most animation-intensive component. The following Framer Motion (React) animation variants govern its behavior.

**Panel Open/Close:**

| Variant   | Properties                                                                | Transition                        |
| --------- | ------------------------------------------------------------------------- | --------------------------------- |
| `hidden`  | `x: "100%"`, `opacity: 0`                                                | --                                |
| `visible` | `x: 0`, `opacity: 1`                                                     | `duration: 0.2, ease: "easeOut"` |
| `exit`    | `x: "100%"`, `opacity: 0`                                                | `duration: 0.15, ease: "easeIn"` |

**Agent Row List (staggered entry):**

| Variant     | Properties                                        | Transition                                              |
| ----------- | ------------------------------------------------- | ------------------------------------------------------- |
| `hidden`    | `opacity: 0`, `x: 20`                             | --                                                      |
| `visible`   | `opacity: 1`, `x: 0`                              | `duration: 0.25, ease: "easeOut"`                       |
| `stagger`   | (parent) `staggerChildren: 0.05, delayChildren: 0.1` | 50ms between each row, 100ms initial delay           |

**Agent Status Icon Swap:**

| Variant        | Properties                                    | Transition                                         |
| -------------- | --------------------------------------------- | -------------------------------------------------- |
| `initial`      | `scale: 0.5`, `opacity: 0`                    | --                                                 |
| `animate`      | `scale: 1`, `opacity: 1`                      | `type: "spring", stiffness: 500, damping: 25`     |
| `exit`         | `scale: 0.5`, `opacity: 0`                    | `duration: 0.1`                                    |

**Timeline Bar Segment Growth:**

| Variant     | Properties                                     | Transition                                           |
| ----------- | ---------------------------------------------- | ---------------------------------------------------- |
| `initial`   | `scaleX: 0`, `transformOrigin: "left"`          | --                                                   |
| `animate`   | `scaleX: 1`                                     | `duration: 0.4, ease: "easeOut"`                     |

**Agent Completion Celebration (checkmark pop):**

| Variant     | Properties                                     | Transition                                           |
| ----------- | ---------------------------------------------- | ---------------------------------------------------- |
| `initial`   | `scale: 0`, `rotate: -45`                      | --                                                   |
| `animate`   | `scale: 1`, `rotate: 0`                        | `type: "spring", stiffness: 400, damping: 15`       |

**Reduced Motion Overrides for Framer Motion:**

When `prefers-reduced-motion: reduce` is detected, all Framer Motion transitions are overridden:

| Standard Transition               | Reduced Motion Override               |
| --------------------------------- | ------------------------------------- |
| All spring animations             | `duration: 0, type: "tween"`         |
| All tween animations              | `duration: 0`                         |
| Stagger children                  | `staggerChildren: 0`                 |
| Layout animations                 | `layout: false`                       |

---

## 4.4 -- Accessibility

### 4.4.1 Compliance Target

**WCAG 2.1 Level AA** is the minimum compliance standard. Where feasible, Level AAA criteria are adopted (noted in this document where applicable).

### 4.4.2 ARIA Role Assignments

Every component must use correct ARIA roles, states, and properties. The following table defines the authoritative role for each component in the system.

| Component               | HTML Element     | ARIA Role             | ARIA Properties                                                                              |
| ------------------------ | ---------------- | --------------------- | -------------------------------------------------------------------------------------------- |
| Dashboard page           | `<main>`         | `main`                | `aria-label="Hallucination guardrail dashboard"`                                             |
| Navigation sidebar       | `<nav>`          | `navigation`          | `aria-label="Primary navigation"`                                                            |
| Metric card              | `<article>`      | (implicit)            | `aria-label="[Metric name] metric"`                                                          |
| Confidence Gauge         | `<figure>`       | `img`                 | `aria-label="Confidence score: [value]%"`, `aria-roledescription="gauge"`                    |
| Data table               | `<table>`        | `table` (implicit)    | `aria-label="[Table description]"`, column headers use `<th scope="col">`                    |
| Sortable column header   | `<th>`           | `columnheader`        | `aria-sort="ascending|descending|none"`                                                      |
| Live Trace panel         | `<aside>`        | `complementary`       | `aria-label="Live agent trace"`, `aria-live="polite"`                                        |
| Live Trace agent row     | `<div>`          | `status`              | `aria-label="[Agent name]: [status]"`, `aria-live="polite"`                                  |
| Progress bar             | `<div>`          | `progressbar`         | `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`, `aria-label="Query progress"`   |
| Toast container          | `<div>`          | `region`              | `aria-label="Notifications"`, `aria-live="polite"`                                           |
| Individual toast         | `<div>`          | `alert` (error) / `status` (others) | `aria-live="assertive"` (error) / `aria-live="polite"` (others)             |
| Modal dialog             | `<div>`          | `dialog`              | `aria-modal="true"`, `aria-labelledby="[title-id]"`, `aria-describedby="[desc-id]"`         |
| Dropdown menu            | `<ul>`           | `menu`                | `aria-label="[Menu purpose]"`                                                                |
| Dropdown item            | `<li>`           | `menuitem`            | `aria-disabled` when inactive                                                                |
| Tab list                 | `<div>`          | `tablist`             | `aria-label="[Tab group purpose]"`                                                           |
| Individual tab           | `<button>`       | `tab`                 | `aria-selected="true|false"`, `aria-controls="[panel-id]"`                                   |
| Tab panel                | `<div>`          | `tabpanel`            | `aria-labelledby="[tab-id]"`                                                                 |
| Toggle switch            | `<button>`       | `switch`              | `aria-checked="true|false"`, `aria-label="[Toggle purpose]"`                                 |
| Search input             | `<input>`        | `searchbox`           | `aria-label="Search"`, `aria-autocomplete="list"` if applicable                              |
| Sidebar collapse button  | `<button>`       | `button`              | `aria-expanded="true|false"`, `aria-label="Collapse sidebar"`                                |
| Skeleton card            | `<div>`          | `presentation`        | `aria-hidden="true"` (skeletons are invisible to screen readers)                              |
| Loading spinner          | `<div>`          | `status`              | `aria-label="Loading"`, `aria-live="polite"`                                                 |
| Error state card         | `<div>`          | `alert`               | `aria-live="assertive"`                                                                      |
| Chart (interactive)      | `<div>`          | `img`                 | `aria-label="[Chart description with summary data]"`                                         |
| Chart data table (hidden)| `<table>`        | `table`               | Visually hidden table behind every chart for screen reader access to data.                    |

### 4.4.3 Screen Reader Announcement Triggers

Dynamic state changes must be announced to screen readers. The following table enumerates every announcement trigger and its corresponding text.

| Trigger Event                        | Announcement Text                                              | `aria-live` | Priority     |
| ------------------------------------ | -------------------------------------------------------------- | ----------- | ------------ |
| Query submitted                      | "Query submitted. Loading results."                            | `polite`    | Low          |
| First agent starts processing        | "Agent [name] is now processing."                              | `polite`    | Low          |
| Agent completes successfully         | "[Agent name] completed. Result available."                    | `polite`    | Low          |
| Agent fails                          | "[Agent name] failed. Error: [brief message]."                 | `assertive` | High         |
| All agents complete                  | "All agents complete. [N] results available."                  | `polite`    | Medium       |
| Progress exceeds 2x expected time    | "Processing is taking longer than expected."                   | `polite`    | Low          |
| Partial results available            | "Partial results are now available. [N] of [M] agents complete." | `polite`  | Medium       |
| Toast notification appears (info)    | "[Toast title]. [Toast description]."                          | `polite`    | Low          |
| Toast notification appears (error)   | "Error: [Toast title]. [Toast description]."                   | `assertive` | High         |
| Modal opens                          | (Focus moves to modal. Title announced via `aria-labelledby`.) | N/A         | N/A          |
| Modal closes                         | (Focus returns to trigger element.)                            | N/A         | N/A          |
| Table sort changes                   | "Table sorted by [column], [direction]."                       | `polite`    | Low          |
| Sidebar collapses                    | "Sidebar collapsed."                                           | `polite`    | Low          |
| Sidebar expands                      | "Sidebar expanded."                                            | `polite`    | Low          |
| Live Trace panel opens               | "Agent trace panel opened."                                    | `polite`    | Low          |
| Live Trace panel closes              | "Agent trace panel closed."                                    | `polite`    | Low          |
| Confidence score updates             | "Confidence score updated to [value] percent."                 | `polite`    | Low          |
| WebSocket disconnects                | "Live connection lost. Attempting to reconnect."               | `assertive` | High         |
| WebSocket reconnects                 | "Live connection restored."                                    | `polite`    | Medium       |

### 4.4.4 Keyboard Navigation Flow

The tab order follows a logical reading order: left-to-right, top-to-bottom, with grouped components forming tab stops.

**Global Tab Order:**

| Order | Element                          | Key Behavior                                                                           |
| ----- | -------------------------------- | -------------------------------------------------------------------------------------- |
| 1     | Skip-to-content link             | Hidden until focused. Enter jumps focus to `<main>`.                                   |
| 2     | Sidebar navigation               | Arrow up/down moves between nav items. Enter activates. Home/End jump to first/last.   |
| 3     | Sidebar collapse toggle          | Enter/Space toggles collapse.                                                          |
| 4     | Dashboard header (page title)    | Not focusable (heading, not interactive).                                              |
| 5     | Dashboard action buttons         | Tab between buttons. Enter/Space activates.                                            |
| 6     | Metric cards (if interactive)    | Tab between cards. Enter opens detail view.                                            |
| 7     | Chart area                       | Tab focuses chart. Arrow keys navigate data points. Enter shows tooltip.               |
| 8     | Table headers (sortable)         | Tab between sortable headers. Enter/Space toggles sort. Arrow keys also work.          |
| 9     | Table rows                       | Arrow up/down moves between rows. Enter opens detail. Tab moves to next interactive cell.|
| 10    | Live Trace panel toggle          | Enter/Space opens/closes panel.                                                        |
| 11    | Live Trace agent rows            | Arrow up/down within panel. Enter expands agent detail.                                |
| 12    | Toast notifications              | Tab focus moves to newest toast. Enter activates action. Esc dismisses.                |

**Browser Shortcut Collision Analysis:**

The following table documents keyboard shortcuts that conflict with browser or OS defaults. Our shortcuts must avoid these or provide an override mechanism.

| Our Shortcut | Intended Action | Collision | Browser/OS Default | Resolution |
|---|---|---|---|---|
| `Ctrl+K` | Open command palette | **Chrome, Edge, Firefox** | Focus address bar | Use `Ctrl+K` only when focus is inside the dashboard (not the address bar). Add a visual hint: "Press Ctrl+K when focused in the app." Alternative: `Ctrl+/` as fallback. |
| `Ctrl+S` | Save current configuration | **All browsers** | Save page as HTML | `preventDefault()` on the keydown event within the app container. Show toast: "Configuration saved." |
| `Ctrl+D` | Toggle dark mode | **Chrome, Edge** | Bookmark current page | Remap to `Ctrl+Shift+D` to avoid collision. |
| `Ctrl+F` | Search within dashboard | **All browsers** | Browser find-in-page | Do NOT override. Allow browser find-in-page. Our search uses `Ctrl+Shift+F` or the command palette. |
| `Ctrl+L` | Open live trace panel | **Chrome, Edge** | Focus address bar | Remap to `Ctrl+Shift+L` to avoid collision. |
| `Esc` | Close modal/panel | None | — | Safe. No collision. |
| `?` | Open keyboard shortcut help | None | — | Safe. Only active when no input is focused. |

**Rule:** Never override `Ctrl+C`, `Ctrl+V`, `Ctrl+X`, `Ctrl+Z`, `Ctrl+A`, `Ctrl+F`, `Ctrl+T`, `Ctrl+W`, or `Ctrl+N`. These are sacred browser shortcuts that users expect to work universally.

**Focus Trapping:**

- Modals trap focus. Tab cycles within modal content. Esc closes.
- Dropdown menus trap focus. Arrow up/down navigates. Esc closes and returns focus to trigger.
- The Live Trace panel does NOT trap focus (it is supplementary content, not modal).

**Focus Return:**

After any overlay (modal, dropdown, bottom sheet) closes, focus must return to the element that triggered it. If that element no longer exists (e.g., a deleted item), focus moves to the nearest logical sibling.

### 4.4.5 Color Contrast Ratios

All color pairings must meet WCAG 2.1 AA minimum contrast ratios. The following table documents required ratios per element type.

| Element Type                  | Foreground Token          | Background Token          | Required Ratio | Target Ratio |
| ----------------------------- | ------------------------- | ------------------------- | -------------- | ------------ |
| Body text                     | `--color-neutral-900`     | `--color-neutral-0`       | 4.5:1          | 7:1+         |
| Secondary text                | `--color-neutral-600`     | `--color-neutral-0`       | 4.5:1          | 5:1+         |
| Caption / metadata            | `--color-neutral-500`     | `--color-neutral-0`       | 4.5:1          | 4.5:1        |
| Heading text                  | `--color-neutral-900`     | `--color-neutral-0`       | 4.5:1          | 7:1+         |
| Link text                     | `--color-primary-600`     | `--color-neutral-0`       | 4.5:1          | 5:1+         |
| Button text (primary)         | `--color-neutral-0`       | `--color-primary-600`     | 4.5:1          | 7:1+         |
| Button text (secondary)       | `--color-primary-700`     | `--color-neutral-0`       | 4.5:1          | 5:1+         |
| Error text                    | `--color-error-700`       | `--color-neutral-0`       | 4.5:1          | 5:1+         |
| Success text                  | `--color-success-700`     | `--color-neutral-0`       | 4.5:1          | 5:1+         |
| Warning text                  | `--color-warning-800`     | `--color-warning-50`      | 4.5:1          | 5:1+         |
| Placeholder text              | `--color-neutral-400`     | `--color-neutral-0`       | 4.5:1          | 4.5:1        |
| Icon (informational)          | `--color-neutral-500`     | `--color-neutral-0`       | 3:1            | 4.5:1        |
| Icon (interactive)            | `--color-neutral-700`     | `--color-neutral-0`       | 3:1            | 4.5:1        |
| Focus ring                    | `--color-primary-500`     | any background            | 3:1            | 3:1          |
| Border (input)                | `--color-neutral-300`     | `--color-neutral-0`       | 3:1            | 3:1          |
| Chart data series             | each series               | `--color-neutral-0`       | 3:1            | 3:1          |
| Gauge arc (filled)            | `--color-primary-500`     | `--color-neutral-100`     | 3:1            | 3:1          |

**Dark Mode Contrast:**

All dark mode tokens are independently validated for contrast. The same ratios apply. Dark mode uses lighter foreground colors on dark backgrounds -- it is not simply an inversion.

**Dark Mode Contrast Verification Table:**

| Element Type | Light Foreground Token | Dark Background Token | Computed Ratio | Pass (AA)? | Skeleton Diagrams Section 9 Token |
|---|---|---|---|---|---|
| Body text | `--color-neutral-100` | `--color-neutral-900` | 15.3:1 | Yes | `--text-primary-dark` |
| Secondary text | `--color-neutral-300` | `--color-neutral-900` | 9.7:1 | Yes | `--text-secondary-dark` |
| Caption / metadata | `--color-neutral-400` | `--color-neutral-900` | 6.4:1 | Yes | `--text-tertiary-dark` |
| Heading text | `--color-neutral-50` | `--color-neutral-900` | 17.1:1 | Yes | `--text-primary-dark` |
| Link text | `--color-primary-300` | `--color-neutral-900` | 7.2:1 | Yes | `--link-dark` |
| Button text (primary) | `--color-neutral-900` | `--color-primary-400` | 8.1:1 | Yes | `--btn-primary-text-dark` |
| Error text | `--color-error-300` | `--color-neutral-900` | 6.8:1 | Yes | `--text-error-dark` |
| Success text | `--color-success-300` | `--color-neutral-900` | 7.5:1 | Yes | `--text-success-dark` |
| Placeholder text | `--color-neutral-500` | `--color-neutral-800` | 4.6:1 | Yes | `--text-placeholder-dark` |
| Focus ring | `--color-primary-400` | any dark background | 5.1:1 | Yes | `--focus-ring-dark` |
| Skeleton shimmer base | `--skeleton-base-dark` | `--color-neutral-900` | 1.8:1 | N/A (decorative) | Section 9, shimmer tokens |
| Gauge arc (filled) | `--color-primary-400` | `--color-neutral-800` | 5.3:1 | Yes | `--gauge-fill-dark` |

> **Cross-reference:** Token names in the rightmost column correspond to the dark mode color tokens defined in `skeleton-diagrams.md` Section 9 (Color Tokens). Where Sprint 4 tokens and skeleton diagram tokens differ, skeleton diagram values are canonical per the reconciliation note in skeleton-diagrams.md Section 2.

### 4.4.6 High Contrast Mode

When the user enables high contrast mode (via OS setting or an in-app toggle), the following adjustments apply.

| Element                  | Standard Mode                           | High Contrast Mode                                       |
| ------------------------ | --------------------------------------- | -------------------------------------------------------- |
| Body text                | `--color-neutral-900`                   | `#000000` (pure black)                                   |
| Background               | `--color-neutral-0` (#FFFFFF)           | `#FFFFFF` (pure white)                                   |
| Borders                  | `--color-neutral-200` (subtle)          | `#000000` 2px solid (all borders visible)                |
| Focus ring               | `--color-primary-500` at 50% opacity    | `#000000` 3px solid (no opacity)                         |
| Links                    | `--color-primary-600`                   | Underlined + `#0000EE` (standard link blue)              |
| Buttons (primary)        | `--color-primary-600` bg                | `#000000` bg, `#FFFFFF` text, 2px border                 |
| Buttons (secondary)      | `--color-neutral-0` bg, border          | `#FFFFFF` bg, `#000000` text, 2px `#000000` border       |
| Icons                    | Various colors                          | `#000000` fill (all icons monochrome)                    |
| Chart data series        | Color-differentiated                    | Pattern-differentiated (stripes, dots, dashes) + labels  |
| Gauge arc                | Gradient fill                           | Solid `#000000` fill, `#FFFFFF` track, 2px border        |
| Skeleton shimmer         | Gradient animation                      | Static `#E0E0E0` fill, 2px dashed `#000000` border      |
| Shadows                  | Box-shadow (various)                    | Removed. Replaced with 1px solid `#000000` border.       |
| Status colors (red/green)| Semantic colors                         | Semantic colors retained + text labels always visible     |

**Detection:**

High contrast mode is detected via `@media (forced-colors: active)` and the `prefers-contrast: more` media query. Both must be supported.

### 4.4.7 Focus Management Strategy

Focus management ensures that the user's keyboard position is always logical and never lost.

| Scenario                               | Focus Behavior                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------ |
| Page load                              | Focus on skip-to-content link (visible on first Tab press).                    |
| Route change (SPA navigation)          | Focus moves to the new page's `<h1>`. Document title updates.                 |
| Modal opens                            | Focus moves to the first focusable element inside the modal (usually close button or first input). |
| Modal closes                           | Focus returns to the trigger element that opened the modal.                    |
| Dropdown opens                         | Focus moves to the first menu item.                                            |
| Dropdown closes (Esc)                  | Focus returns to the trigger button.                                           |
| Dropdown closes (selection)            | Focus returns to the trigger button. Selection is applied.                     |
| Item deleted from list                 | Focus moves to the next item. If last item was deleted, focus moves to the previous item. If list is empty, focus moves to the nearest heading or action. |
| Toast appears                          | Focus does NOT move to the toast (toasts are passive). Screen reader announces it via `aria-live`. |
| Error state appears                    | Focus moves to the error message or the first actionable element within the error state (e.g., Retry button). |
| Live Trace panel opens (user-triggered)| Focus moves to the panel's first focusable element (close/pin button).         |
| Live Trace panel opens (auto)          | Focus does NOT move (auto-open is passive).                                    |
| Skeleton replaced with content         | Focus does NOT move (replacement is passive). If the user was focused on a skeleton area, focus moves to the equivalent content element. |
| Tab key on last element in page        | Focus wraps to skip-to-content link (natural browser behavior).                |

### 4.4.8 Semantic HTML Element Choices

Every component must use the most semantically appropriate HTML element. This table is the definitive guide -- no `<div>` where a semantic element exists.

| Component / Region       | Element          | Rationale                                                           |
| ------------------------ | ---------------- | ------------------------------------------------------------------- |
| Page wrapper             | `<body>`         | Root.                                                               |
| App shell                | `<div id="app">` | React root. No semantic role.                                      |
| Skip link                | `<a>`            | Anchor link to `#main-content`.                                     |
| Header bar               | `<header>`       | Top-level page header containing logo and global actions.           |
| Primary navigation       | `<nav>`          | Sidebar or top navigation. Uses `<ul>/<li>` for items.             |
| Nav link                 | `<a>` or `<Link>` | Anchor for route navigation. Not a `<div>` with onClick.          |
| Main content area        | `<main>`         | One per page. `id="main-content"` for skip link target.            |
| Page title               | `<h1>`           | One per page. Describes the current view.                           |
| Section title            | `<h2>`           | Dashboard sections (Metrics, Chart, Table, etc.).                   |
| Subsection title         | `<h3>`           | Card titles, widget headers within sections.                        |
| Metric card              | `<article>`      | Self-contained metric. Could be understood independently.           |
| Metric value             | `<data>`         | Machine-readable value in `value` attribute. Display value as text. |
| Data table               | `<table>`        | Tabular data. Never a grid of `<div>` elements.                    |
| Table header cell        | `<th>`           | With `scope="col"` or `scope="row"`.                               |
| Table body               | `<tbody>`        | Groups body rows.                                                   |
| Table row                | `<tr>`           | Each data row.                                                      |
| Table cell               | `<td>`           | Data cells within rows.                                             |
| Chart wrapper            | `<figure>`       | Wraps chart + caption.                                              |
| Chart caption            | `<figcaption>`   | Describes the chart's purpose.                                      |
| Chart accessible data    | `<table>`        | Visually hidden. Screen reader alternative to visual chart.         |
| Confidence Gauge         | `<figure>`       | Wraps gauge + caption.                                              |
| Gauge caption            | `<figcaption>`   | "Confidence: [value]%"                                              |
| Live Trace panel         | `<aside>`        | Supplementary content related to main dashboard.                    |
| Agent list in Live Trace | `<ol>`           | Ordered list (agents have pipeline order).                          |
| Agent item               | `<li>`           | List item within `<ol>`.                                            |
| Buttons (action)         | `<button>`       | Always `<button>`, never `<div>` or `<a>` for actions.             |
| Links (navigation)       | `<a>`            | Always `<a>` for navigation.                                       |
| Form fields              | `<input>`, `<select>`, `<textarea>` | Native form elements. `<label>` always associated. |
| Form group               | `<fieldset>`     | Groups related inputs. `<legend>` describes the group.              |
| Time display             | `<time>`         | `datetime` attribute for machine-readable value.                    |
| Code snippet             | `<pre><code>`    | Preformatted code blocks.                                           |
| Inline code              | `<code>`         | Agent names, IDs, technical terms within prose.                     |
| Emphasis                 | `<em>` / `<strong>` | Semantic emphasis, not `<span>` with bold styling.               |
| Lists (unordered)        | `<ul>`           | Feature lists, bullet points, non-sequential items.                 |
| Lists (ordered)          | `<ol>`           | Sequential steps, ranked items.                                     |
| Description pairs        | `<dl>/<dt>/<dd>` | Key-value pairs (e.g., agent metadata).                             |
| Divider                  | `<hr>`           | Thematic break. Not a `<div>` with a border.                       |
| Toast container          | `<section>`      | Named region with `aria-label`.                                     |
| Footer                   | `<footer>`       | Page-level footer with version, links.                              |

---

## 4.5 -- Design System Foundations

### 4.5.1 Color Palette

#### Primary Colors

| Token                  | Light Mode | Dark Mode  | Usage                                          |
| ---------------------- | ---------- | ---------- | ---------------------------------------------- |
| `--color-primary-50`   | `#EFF6FF`  | `#1E293B`  | Hover fills, selected backgrounds              |
| `--color-primary-100`  | `#DBEAFE`  | `#1E3A5F`  | Active/pressed backgrounds                     |
| `--color-primary-200`  | `#BFDBFE`  | `#1E4D8C`  | Focus rings, decorative borders                |
| `--color-primary-300`  | `#93C5FD`  | `#2563EB`  | Decorative elements, progress track accents    |
| `--color-primary-400`  | `#60A5FA`  | `#3B82F6`  | Icons (secondary), hover accents               |
| `--color-primary-500`  | `#3B82F6`  | `#60A5FA`  | Primary brand color, links, active states      |
| `--color-primary-600`  | `#2563EB`  | `#93C5FD`  | Button backgrounds, strong accents             |
| `--color-primary-700`  | `#1D4ED8`  | `#BFDBFE`  | Button hover, strong text emphasis             |
| `--color-primary-800`  | `#1E40AF`  | `#DBEAFE`  | Darkest interactive accent                     |
| `--color-primary-900`  | `#1E3A8A`  | `#EFF6FF`  | Rarely used. Extreme emphasis only.            |

#### Neutral Colors

| Token                  | Light Mode | Dark Mode  | Usage                                          |
| ---------------------- | ---------- | ---------- | ---------------------------------------------- |
| `--color-neutral-0`    | `#FFFFFF`  | `#0F172A`  | Page background, card backgrounds              |
| `--color-neutral-50`   | `#F8FAFC`  | `#1E293B`  | Subtle background (table row hover, sidebar)   |
| `--color-neutral-100`  | `#F1F5F9`  | `#334155`  | Card background (secondary), input background  |
| `--color-neutral-200`  | `#E2E8F0`  | `#475569`  | Borders, dividers, skeleton base               |
| `--color-neutral-300`  | `#CBD5E1`  | `#64748B`  | Disabled borders, decorative borders           |
| `--color-neutral-400`  | `#94A3B8`  | `#94A3B8`  | Placeholder text, disabled text, muted icons   |
| `--color-neutral-500`  | `#64748B`  | `#CBD5E1`  | Secondary text, captions, metadata             |
| `--color-neutral-600`  | `#475569`  | `#E2E8F0`  | Body text (secondary)                          |
| `--color-neutral-700`  | `#334155`  | `#F1F5F9`  | Body text (primary alternative)                |
| `--color-neutral-800`  | `#1E293B`  | `#F8FAFC`  | Headings                                       |
| `--color-neutral-900`  | `#0F172A`  | `#FFFFFF`  | Highest contrast text                          |

#### Semantic Colors

**Success:**

| Token                   | Light Mode | Dark Mode  |
| ----------------------- | ---------- | ---------- |
| `--color-success-50`    | `#F0FDF4`  | `#14532D`  |
| `--color-success-100`   | `#DCFCE7`  | `#166534`  |
| `--color-success-200`   | `#BBF7D0`  | `#15803D`  |
| `--color-success-500`   | `#22C55E`  | `#4ADE80`  |
| `--color-success-600`   | `#16A34A`  | `#86EFAC`  |
| `--color-success-700`   | `#15803D`  | `#BBF7D0`  |

**Warning:**

| Token                   | Light Mode | Dark Mode  |
| ----------------------- | ---------- | ---------- |
| `--color-warning-50`    | `#FFFBEB`  | `#78350F`  |
| `--color-warning-100`   | `#FEF3C7`  | `#92400E`  |
| `--color-warning-200`   | `#FDE68A`  | `#B45309`  |
| `--color-warning-500`   | `#F59E0B`  | `#FBBF24`  |
| `--color-warning-600`   | `#D97706`  | `#FDE68A`  |
| `--color-warning-700`   | `#B45309`  | `#FEF3C7`  |
| `--color-warning-800`   | `#92400E`  | `#FFFBEB`  |

**Error:**

| Token                   | Light Mode | Dark Mode  |
| ----------------------- | ---------- | ---------- |
| `--color-error-50`      | `#FEF2F2`  | `#7F1D1D`  |
| `--color-error-100`     | `#FEE2E2`  | `#991B1B`  |
| `--color-error-200`     | `#FECACA`  | `#B91C1C`  |
| `--color-error-500`     | `#EF4444`  | `#F87171`  |
| `--color-error-600`     | `#DC2626`  | `#FCA5A5`  |
| `--color-error-700`     | `#B91C1C`  | `#FECACA`  |

**Info:**

| Token                   | Light Mode | Dark Mode  |
| ----------------------- | ---------- | ---------- |
| `--color-info-50`       | `#EFF6FF`  | `#1E3A5F`  |
| `--color-info-100`      | `#DBEAFE`  | `#1E4D8C`  |
| `--color-info-200`      | `#BFDBFE`  | `#2563EB`  |
| `--color-info-500`      | `#3B82F6`  | `#60A5FA`  |
| `--color-info-600`      | `#2563EB`  | `#93C5FD`  |
| `--color-info-700`      | `#1D4ED8`  | `#BFDBFE`  |

### 4.5.2 Spacing Scale

A consistent spacing scale based on a 4px base unit. Every margin, padding, and gap in the system must use one of these tokens.

| Token              | Value   | Common Usage                                                    |
| ------------------ | ------- | --------------------------------------------------------------- |
| `--space-0`        | 0px     | Reset spacing.                                                  |
| `--space-0.5`      | 2px     | Hairline gaps (icon-to-text within tight badges).               |
| `--space-1`        | 4px     | Tightest intentional gap. Inner padding of small badges.        |
| `--space-1.5`      | 6px     | Compact inner padding.                                          |
| `--space-2`        | 8px     | Default inner padding (buttons, inputs, table cells).           |
| `--space-3`        | 12px    | Small card padding. Gap between stacked elements (mobile).      |
| `--space-4`        | 16px    | Default card padding. Standard gap between sections (mobile).   |
| `--space-5`        | 20px    | Medium gap. Desktop grid gap (lg breakpoint).                   |
| `--space-6`        | 24px    | Large card padding. Standard gap (desktop).                     |
| `--space-8`        | 32px    | Section padding (desktop). Page margin (desktop).               |
| `--space-10`       | 40px    | Large section padding (2xl breakpoint).                         |
| `--space-12`       | 48px    | Page margin (4k breakpoint). Major section spacing.             |
| `--space-16`       | 64px    | Sidebar collapsed width. Large whitespace.                      |
| `--space-20`       | 80px    | Maximum section spacing.                                        |
| `--space-24`       | 96px    | Metric card height (skeleton/loaded).                           |

**Rules:**

1. Never use raw pixel values for spacing. Always use tokens.
2. Vertical rhythm: body text line-height creates a natural 24px baseline grid (`16px * 1.5 = 24px`). All spacing values should feel harmonious with this grid.
3. Padding within interactive elements must account for touch target minimums (44px).

### 4.5.3 Border Radius Scale

| Token              | Value   | Usage                                                           |
| ------------------ | ------- | --------------------------------------------------------------- |
| `--radius-none`    | 0px     | Sharp corners (table cells, full-width elements).               |
| `--radius-sm`      | 2px     | Subtle rounding (badges, code inline).                          |
| `--radius-md`      | 4px     | Default rounding (buttons, inputs, small cards).                |
| `--radius-lg`      | 8px     | Card rounding. Panel rounding.                                  |
| `--radius-xl`      | 12px    | Large cards, modal corners.                                     |
| `--radius-2xl`     | 16px    | Bottom sheets (mobile), prominent cards.                        |
| `--radius-full`    | 9999px  | Pill shapes (badges, toggle tracks, avatar circles).            |

**Rules:**

1. Nested elements must use a smaller radius than their parent so the inner curve tracks the outer curve visually.
2. Elements that span the full width of their container (tables, full-bleed banners) should have `border-radius: 0` on the edges that touch the container.

### 4.5.4 Shadow System

Shadows provide depth hierarchy. Each level represents an increasing degree of elevation.

| Token              | Light Mode Value                                               | Dark Mode Value                                                | Usage                                     |
| ------------------ | -------------------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------- |
| `--shadow-0`       | `none`                                                         | `none`                                                         | Flat (no elevation).                      |
| `--shadow-1`       | `0 1px 2px 0 rgba(0,0,0,0.05)`                                | `0 1px 2px 0 rgba(0,0,0,0.3)`                                 | Cards at rest. Subtle lift.               |
| `--shadow-2`       | `0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)` | `0 1px 3px 0 rgba(0,0,0,0.4), 0 1px 2px -1px rgba(0,0,0,0.3)` | Cards on hover. Elevated elements.       |
| `--shadow-3`       | `0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)` | `0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -2px rgba(0,0,0,0.3)` | Dropdowns, tooltips.                |
| `--shadow-4`       | `0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)` | `0 10px 15px -3px rgba(0,0,0,0.4), 0 4px 6px -4px rgba(0,0,0,0.3)` | Modals, floating panels.          |
| `--shadow-5`       | `0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)` | `0 20px 25px -5px rgba(0,0,0,0.4), 0 8px 10px -6px rgba(0,0,0,0.3)` | Top-level overlays (toast stack). |
| `--shadow-inner`   | `inset 0 2px 4px 0 rgba(0,0,0,0.05)`                         | `inset 0 2px 4px 0 rgba(0,0,0,0.3)`                          | Input fields (focused), recessed areas.   |
| `--shadow-focus`   | `0 0 0 3px rgba(59,130,246,0.5)`                              | `0 0 0 3px rgba(96,165,250,0.6)`                              | Focus ring (used with box-shadow).        |

**Rules:**

1. Dark mode shadows are heavier (higher opacity) because the base surfaces are already dark -- subtle shadows would be invisible.
2. Shadows must never be the only way to distinguish overlapping elements. Always pair with borders or background-color differences.

### 4.5.5 Z-Index System

A managed z-index scale prevents stacking conflicts. No z-index value should be used outside of these tokens.

| Token              | Value  | Usage                                                          |
| ------------------ | ------ | -------------------------------------------------------------- |
| `--z-base`         | 0      | Default stacking. Most content.                                |
| `--z-dropdown`     | 100    | Dropdown menus, autocomplete panels.                           |
| `--z-sticky`       | 200    | Sticky table headers, sticky nav bars.                         |
| `--z-sidebar`      | 300    | Sidebar navigation (desktop).                                  |
| `--z-live-trace`   | 400    | Live Trace panel (side-docked).                                |
| `--z-overlay`      | 500    | Bottom sheets (mobile), non-modal overlays.                    |
| `--z-modal-backdrop` | 600  | Modal backdrop (semi-transparent overlay).                     |
| `--z-modal`        | 700    | Modal dialog content.                                          |
| `--z-toast`        | 900    | Toast notifications. Above everything except dev tools.        |
| `--z-tooltip`      | 1000   | Tooltips. Topmost UI layer.                                    |
| `--z-dev`          | 9999   | Development-only debug overlays. Stripped in production.       |

**Rules:**

1. Never use a raw integer for z-index. Always use a token.
2. Within a stacking context, use relative ordering (e.g., `calc(var(--z-modal) + 1)`) rather than inventing new tokens for minor adjustments.
3. Create new stacking contexts (`isolation: isolate`) on major layout regions to prevent z-index leaks between unrelated component trees.

### 4.5.6 Dark/Light Mode Color Mappings

The application supports both light and dark modes. Mode switching is based on (in priority order):

1. User's explicit selection (persisted in `localStorage`).
2. System preference (`prefers-color-scheme` media query).
3. Default: light mode.

**Semantic Mapping Table:**

| Semantic Token                  | Light Mode Source         | Dark Mode Source          |
| ------------------------------- | ------------------------- | ------------------------- |
| `--bg-page`                     | `--color-neutral-0`       | `--color-neutral-0`       |
| `--bg-surface`                  | `--color-neutral-0`       | `--color-neutral-50`      |
| `--bg-surface-raised`           | `--color-neutral-0`       | `--color-neutral-100`     |
| `--bg-surface-sunken`           | `--color-neutral-50`      | `--color-neutral-0`       |
| `--bg-interactive`              | `--color-primary-600`     | `--color-primary-500`     |
| `--bg-interactive-hover`        | `--color-primary-700`     | `--color-primary-400`     |
| `--bg-interactive-active`       | `--color-primary-800`     | `--color-primary-300`     |
| `--bg-interactive-disabled`     | `--color-neutral-200`     | `--color-neutral-200`     |
| `--text-primary`                | `--color-neutral-900`     | `--color-neutral-900`     |
| `--text-secondary`              | `--color-neutral-600`     | `--color-neutral-500`     |
| `--text-tertiary`               | `--color-neutral-500`     | `--color-neutral-400`     |
| `--text-on-primary`             | `--color-neutral-0`       | `--color-neutral-0`       |
| `--text-link`                   | `--color-primary-600`     | `--color-primary-500`     |
| `--text-success`                | `--color-success-700`     | `--color-success-500`     |
| `--text-warning`                | `--color-warning-700`     | `--color-warning-500`     |
| `--text-error`                  | `--color-error-700`       | `--color-error-500`       |
| `--border-default`              | `--color-neutral-200`     | `--color-neutral-200`     |
| `--border-strong`               | `--color-neutral-300`     | `--color-neutral-300`     |
| `--border-interactive`          | `--color-primary-500`     | `--color-primary-400`     |
| `--border-error`                | `--color-error-500`       | `--color-error-500`       |
| `--skeleton-base`               | `hsl(220,15%,92%)`        | `hsl(220,15%,18%)`        |
| `--skeleton-shimmer`            | `hsl(220,15%,96%)`        | `hsl(220,15%,24%)`        |

**Mode Transition:**

When the user toggles between modes, the transition must be smooth:

| Property              | Specification                                  |
| --------------------- | ---------------------------------------------- |
| Transition property   | `background-color, color, border-color, fill, stroke` |
| Duration              | 200ms                                          |
| Easing                | ease-out                                       |
| Applied to            | `*, *::before, *::after` (via global rule)     |
| Exception             | Images, videos, and canvas elements do not transition. |

**Implementation:**

- CSS custom properties are defined on `:root` (light) and `:root[data-theme="dark"]` (dark).
- JavaScript toggles the `data-theme` attribute on `<html>`.
- The `prefers-color-scheme` media query sets the default if no `data-theme` attribute is present.
- All component styles reference semantic tokens (e.g., `--bg-surface`), never raw color tokens (e.g., `--color-neutral-0`) directly. This ensures that mode switching requires zero per-component overrides.

---

## Appendix A -- Quick Reference Card

**Loading:** Skeleton at 0ms. Shimmer loops at 1.5s. Cards crossfade at 300ms as agents finish. Progress bar at top. Live Trace on right. Fallback at 1.5x expected time.

**Breakpoints:** 320 / 480 / 768 / 1024 / 1440 / 2560 / 3840. Mobile-first. Container queries for component-level adaptation.

**Transitions:** 200-300ms ease-out. Never instant. Never sluggish. Reduced motion honored everywhere.

**Accessibility:** WCAG 2.1 AA. ARIA roles on every component. Screen reader announcements for all state changes. 44x44px minimum touch targets. Semantic HTML. No div soup.

**Design Tokens:** Primary blue palette. 4px spacing base. Managed z-index scale. Full dark/light mode. All colors in semantic token layer.

---

## Appendix B -- Document Governance

| Action            | Owner              | Frequency         |
| ----------------- | ------------------ | ----------------- |
| Author            | Frontend Lead      | Sprint 4 start    |
| Review            | Design, QA, A11y   | Before sprint dev |
| Update            | Any engineer (PR)  | As needed         |
| Audit compliance  | QA + A11y Lead     | End of each sprint|

---

*End of Sprint 4 UI/UX Standards -- Agentic Hallucination Guardrail*
