# Design System Tokens

Full CSS custom property spec for the warm espresso + ivory + rust palette.

## Colors

```css
:root {
  /* Backgrounds */
  --bg:           #1a1612;                    /* espresso ink */
  --bg-soft:      #221c16;                    /* slightly lifted */
  --panel:        rgba(32, 26, 21, 0.78);     /* glassmorphism base */
  --panel-strong: rgba(20, 16, 13, 0.9);      /* opaque overlay */
  --ink:          #0e0b08;                     /* deepest black */

  /* Text */
  --text:         #f3ecd8;                    /* warm ivory/bone */
  --muted:        #9a8f7a;                    /* brownish-gray */
  --muted-strong: #d4c9ae;                    /* brighter muted */

  /* Accent */
  --accent:       #d0542c;                    /* rust-red, primary */
  --accent-strong:#e37148;                    /* hover rust */
  --accent-dark:  #a33d1a;                    /* depth/pressed */
  --aoi:          #e5a853;                    /* ochre, regions */
  --positive:     #c74633;                    /* deep coral, exemplars */
  --negative:     #3b82f6;                    /* blue, contrast */
  --amber:        #f59e0b;                    /* toggles, warnings */

  /* Elevation */
  --shadow-lg: 0 28px 80px rgba(0,0,0,0.55), 0 2px 0 rgba(255,255,255,0.04) inset;
  --shadow-md: 0 18px 42px rgba(0,0,0,0.45);

  /* Radii */
  --radius:    14px;   /* cards, panels */
  --radius-sm: 8px;    /* buttons, inputs */
}
```

## Typography

### Font loading (index.html)
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
```

### Font assignments
```css
body {
  font-family: "Inter Tight", sans-serif;
  font-feature-settings: "ss01", "cv11";
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

h1, h2, h3, .brand-text h1 {
  font-family: "Fraunces", serif;
}

h1 {
  font-size: 1.6rem;
  font-weight: 500;
  font-variation-settings: "opsz" 144;
  letter-spacing: -0.04em;
}

h2 {
  font-size: 1.3rem;
  font-weight: 500;
  font-variation-settings: "opsz" 36;
}

.mono, .score, .coord, .chip-label {
  font-family: "JetBrains Mono", monospace;
  font-variant-numeric: tabular-nums;
}
```

### Letterspacing scale
- Display (h1, brand): `-0.04em`
- Body: `-0.005em`
- Labels/kickers: `0.22em` (uppercase, open)

## Glassmorphism

```css
.glass-panel {
  background: var(--panel);
  backdrop-filter: blur(18px) saturate(140%);
  -webkit-backdrop-filter: blur(18px) saturate(140%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
}
```

## Buttons

```css
.btn-primary {
  background: linear-gradient(180deg, var(--accent) 0%, var(--accent-dark) 100%);
  color: var(--ink);
  border: none;
  border-radius: var(--radius-sm);
  font-family: "JetBrains Mono", monospace;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 7px 18px;
  cursor: pointer;
  transition: transform 140ms, box-shadow 140ms;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(208, 84, 44, 0.3);
}
```

## Segmented control (view mode tabs)

```css
.view-tabs {
  display: grid;
  grid-template-columns: repeat(N, 1fr);
  gap: 2px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: var(--radius-sm);
  padding: 2px;
}

.view-tab {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 5px 0;
  border-radius: 6px;
  color: var(--muted);
  transition: all 140ms;
}

.view-tab.is-active {
  background: linear-gradient(180deg, var(--accent) 0%, var(--accent-dark) 100%);
  color: var(--ink);
  box-shadow: 0 4px 14px rgba(208, 84, 44, 0.28),
              0 0 0 1px rgba(208, 84, 44, 0.32) inset;
}
```

## Animations

```css
/* Staggered list reveal */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: none; }
}
.list-item {
  animation: fadeSlideUp 320ms ease-out both;
  animation-delay: calc(var(--i, 0) * 28ms);
}

/* Status LED pulse */
@keyframes pulse-idle { 0%,100% { opacity: 0.5; } 50% { opacity: 1; } }
@keyframes pulse-busy { 0%,100% { opacity: 0.6; transform: scale(1); } 50% { opacity: 1; transform: scale(1.15); } }
.status-dot { animation: pulse-idle 2.8s ease-in-out infinite; }
.status-dot.busy { animation: pulse-busy 1.2s ease-in-out infinite; }

/* Brand orbital rings */
@keyframes spin { to { transform: rotate(360deg); } }
.brand-ring   { animation: spin 14s linear infinite; }
.brand-ring-2 { animation: spin 22s linear infinite reverse; }

/* Tutorial ripple */
@keyframes tut-ripple {
  0%   { box-shadow: 0 0 0 0 rgba(208,84,44,0.5); }
  50%  { box-shadow: 0 0 0 14px rgba(208,84,44,0.2); }
  100% { box-shadow: 0 0 0 28px rgba(208,84,44,0); }
}

/* Panel/element entrance */
@keyframes fadeSlide {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: none; }
}
```

## Scroll fade mask

```css
.scrollable-list {
  overflow-y: auto;
  -webkit-mask-image: linear-gradient(to bottom, #000 80%, transparent 100%);
  mask-image: linear-gradient(to bottom, #000 80%, transparent 100%);
}
```

## Custom range slider

```css
input[type="range"] {
  -webkit-appearance: none;
  height: 5px;
  border-radius: 3px;
  background: linear-gradient(90deg,
    var(--accent) 0%,
    var(--accent) var(--v, 20%),
    rgba(255,255,255,0.12) var(--v, 20%),
    rgba(255,255,255,0.12) 100%
  );
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--bg);
  border: 2px solid var(--accent);
  box-shadow: 0 0 0 4px rgba(208, 84, 44, 0.18);
  cursor: pointer;
}
```

## Starfield + Vignette

```css
.viewport::before {
  content: "";
  position: absolute; inset: 0;
  background-image:
    radial-gradient(1px 1px at 17% 32%, rgba(255,255,255,0.85), transparent 60%),
    radial-gradient(1px 1px at 72% 18%, rgba(255,255,255,0.7), transparent 60%),
    radial-gradient(1px 1px at 41% 71%, rgba(255,255,255,0.6), transparent 60%),
    radial-gradient(1px 1px at 89% 55%, rgba(255,255,255,0.75), transparent 60%),
    radial-gradient(1px 1px at 28% 88%, rgba(255,255,255,0.5), transparent 60%),
    radial-gradient(1px 1px at 63% 42%, rgba(255,255,255,0.65), transparent 60%),
    radial-gradient(1px 1px at 5% 12%, rgba(255,255,255,0.55), transparent 60%),
    radial-gradient(1px 1px at 95% 82%, rgba(255,255,255,0.45), transparent 60%);
  opacity: 0.55;
  z-index: 0;
  pointer-events: none;
}

.viewport::after {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at center, transparent 40%, rgba(14, 11, 8, 0.6) 100%);
  z-index: 1;
  pointer-events: none;
}
```

## Plasma Colormap (5-stop)

```typescript
function interpolatePlasma(t: number): string {
  // 0.0 yellow -> 0.25 orange -> 0.5 magenta -> 0.75 violet -> 1.0 indigo
  const stops = [
    [0.0,  [240, 249, 33]],   // #f0f921
    [0.25, [248, 149, 64]],   // #f89540
    [0.5,  [204, 71, 120]],   // #cc4778
    [0.75, [126, 3, 167]],    // #7e03a7
    [1.0,  [13, 8, 135]],     // #0d0887
  ];
  // Linear interpolation between adjacent stops
}
```

## Number formatting

```typescript
function compact(n: number): string {
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}
```
