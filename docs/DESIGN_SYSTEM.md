# Editorial Field-Report Design System

> A design specification for converting a static website to an editorial / archaeological-journal aesthetic. Hand this document to Claude Code (or any agentic developer) and ask it to refactor the site to match. Every value, rule, and rationale needed to apply this style consistently is below.

---

## 1. Design Philosophy

This is an **editorial / academic-journal** aesthetic — think *The Paris Review* meets a Princeton University Press monograph, with hints of weathered field-notebook. It is NOT:

- ❌ A SaaS landing page
- ❌ A "modern minimalist" Inter-on-white layout
- ❌ A purple-gradient AI-generated look
- ❌ A Bootstrap or Tailwind default

It IS:

- ✅ Serif-forward, warm-toned, paper-textured
- ✅ Confident with negative space and ornamental rules
- ✅ Generous with typography — display fonts get to breathe
- ✅ Restrained color (3-4 ink colors total), used with intent
- ✅ Print-influenced: section numbers, drop caps, ornaments, masthead-style metadata

When in doubt: **err toward restraint and craft**. Big type, small accents, lots of room.

---

## 2. Color Tokens (CSS Custom Properties)

Define these once at `:root` and use everywhere. Do not introduce new colors without updating this list.

```css
:root {
  --ink:        #1a1612;   /* primary text — warm near-black, never pure #000 */
  --paper:      #f1ead9;   /* main background — aged paper, warm cream */
  --paper-deep: #e7dec7;   /* secondary surfaces — slightly deeper paper */
  --ochre:      #b8651a;   /* accent — warm orange-brown */
  --ochre-deep: #8a4a13;   /* secondary accent — deeper ochre */
  --moss:      #4a5234;   /* tertiary accent — used very sparingly */
  --rust:      #6e2a14;   /* heading accent — deep brick red */
  --shadow:    rgba(26, 22, 18, 0.15);
  --rule:      rgba(26, 22, 18, 0.2);  /* hairline rules between sections */
}
```

**Color usage rules:**

- Body text is always `--ink` on `--paper`. Never pure black on pure white.
- `--rust` is reserved for `h3` subheadings and inline emphasis.
- `--ochre-deep` is for section numbers, ornaments, and small decorative type.
- The dark inverted section (the "facts" block) flips: `--paper` text on `--ink` background, with `--ochre` accents.
- Avoid greys. Use translucent ink (e.g. `rgba(26, 22, 18, 0.55)`) when you need a muted tone — it keeps the warmth.

---

## 3. Typography

Three typefaces, each with a clear job. Load all weights from Google Fonts in a single `<link>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&family=Cinzel:wght@400;500;600&display=swap" rel="stylesheet">
```

| Font | Role | Where used |
|---|---|---|
| **Cinzel** | Display & titles | `h1`, `h2`, page titles, drop caps, large numerals in fact grid |
| **Cormorant Garamond** | Body & subheadings | All paragraph text, `h3`, blockquotes, deck/lede |
| **JetBrains Mono** | Metadata & labels | Section numbers, masthead, dates, axis labels, "filed/vol/no" type marks |

**DO NOT substitute** Inter, Roboto, system-ui, Arial, Georgia, or Times. The Cinzel/Cormorant pairing is the entire aesthetic.

**Type scale:**

```css
body         { font-family: 'Cormorant Garamond', serif; font-size: 19px; line-height: 1.65; }
h1.title     { font-family: 'Cinzel', serif; font-weight: 500; font-size: clamp(56px, 9vw, 140px); line-height: 0.92; letter-spacing: -0.01em; }
h2           { font-family: 'Cinzel', serif; font-weight: 500; font-size: clamp(30px, 4vw, 44px); line-height: 1.1; letter-spacing: -0.01em; }
h3           { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 24px; color: var(--rust); }
.section-num { font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 0.2em; color: var(--ochre-deep); text-transform: uppercase; }
.masthead    { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; opacity: 0.7; }
blockquote   { font-style: italic; font-size: 22px; line-height: 1.5; padding-left: 32px; border-left: 3px solid var(--ochre); }
```

**Body paragraph rules:**

- `text-align: justify` and `hyphens: auto` for body prose — gives it a print feel.
- Margin between paragraphs: `22px`.
- Max width of body content: `720px`. Never wider, regardless of viewport.
- The first paragraph of a major section gets `class="lead"` and a Cinzel drop cap.

---

## 4. Layout & Spatial System

### Page width

- **Hero / inverted blocks**: full-bleed, padded `60px 8vw` (mobile: `50px 24px`)
- **Reading content**: `max-width: 720px`, centered, padded `0 24px`
- **Facts grid (inverted block)**: `max-width: 1100px` inside its full-bleed dark section

### Vertical rhythm

- Section spacing: `80px` margin-bottom between sections
- Ornament-divider spacing: `80px` margin top and bottom
- `h3` to body: `36px` top, `16px` bottom
- Inverted blocks (facts, reading): `100px` vertical padding inside, `80px` outer margin separating from prose

### Hero

The hero takes a full viewport (`min-height: 100vh`) and contains four parts, in order:

1. **Masthead bar** — `flex` row, space-between: volume / category / year, in JetBrains Mono uppercase
2. **Title** — Cinzel display, with an italic Cormorant subtitle in `--ochre-deep` on a new line, sized `0.7em` of the main title
3. **Deck** — italic Cormorant, max 60ch, sized `clamp(20px, 2vw, 26px)`
4. **Meta strip** — flex-wrap row of label/value pairs (Subject, Region, Period, Filed, etc.) in JetBrains Mono

Two thin horizontal rules — one near the top, one near the bottom of the hero — frame it. Implement as `::before` and `::after` pseudo-elements absolutely positioned at top: 40px and bottom: 40px.

---

## 5. Ornaments & Section Dividers

Between major sections, place an ornament block. This is the single most distinctive small element of the system — do not skip it.

```html
<div class="ornament">
  <span class="glyph">✦</span>
  <span>II</span>
  <span class="glyph">✦</span>
</div>
```

```css
.ornament {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 80px auto;
  color: var(--ochre-deep);
  font-family: 'Cinzel', serif;
  font-size: 12px;
  letter-spacing: 0.3em;
}
.ornament::before, .ornament::after {
  content: "";
  flex: 0 0 80px;
  height: 1px;
  background: currentColor;
}
.ornament .glyph { font-size: 16px; }
```

Glyph rotation between sections: `✦`, `⊹`, `✦`, `⊹`, etc. Roman numerals (`I`, `II`, `III`, `IV`) for the central token.

---

## 6. Section Numbering Convention

Every major section header is preceded by a small JetBrains Mono label:

```html
<span class="section-num">§ 03 — The Argument</span>
<h2>...</h2>
```

The `§` symbol is part of the aesthetic. Number sections sequentially across the whole document.

---

## 7. Background & Texture

The paper texture is critical and must be applied to body. It uses **inline SVG noise** rather than an image asset — this keeps the page self-contained:

```css
body {
  background: var(--paper);
  background-image:
    radial-gradient(circle at 20% 30%, rgba(184, 101, 26, 0.06) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(74, 82, 52, 0.05) 0%, transparent 50%),
    url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.1 0 0 0 0 0.08 0 0 0 0 0.05 0 0 0 0 0.05 0 0 0 0.08 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
```

The two radial gradients add subtle warmth at opposite corners. The SVG noise filter produces the grain. Together they give the "aged paper" feeling.

---

## 8. Component Patterns

### 8.1 Drop cap (first paragraph of a section)

```html
<p class="lead">In the late eighteenth century...</p>
```

```css
p.lead { text-align: left; }
p.lead::first-letter {
  font-family: 'Cinzel', serif;
  font-size: 5em;
  float: left;
  line-height: 0.85;
  margin: 6px 10px -4px 0;
  color: var(--ochre-deep);
  font-weight: 600;
}
```

### 8.2 Pull quote / blockquote

```html
<blockquote>
  We speak English not just because our parents taught it to us...
  <span class="attrib">— Christine Kenneally, NYT Book Review</span>
</blockquote>
```

```css
blockquote {
  margin: 36px 0;
  padding: 0 0 0 32px;
  border-left: 3px solid var(--ochre);
  font-style: italic;
  font-size: 22px;
  line-height: 1.5;
}
blockquote .attrib {
  display: block;
  margin-top: 14px;
  font-style: normal;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  opacity: 0.7;
  color: var(--ochre-deep);
}
```

### 8.3 Featured-content card (e.g. "the book")

A `paper-deep` background panel with a double border (outer real, inner pseudo-element), a rotated rust-red "stamp" badge, and a metadata grid at the foot.

```html
<div class="book-feature">
  <span class="stamp">Foundational Text</span>
  <h3>...</h3>
  <p>...</p>
  <div class="book-meta">
    <div><span class="lbl">Author</span>Name</div>
    ...
  </div>
</div>
```

Key styling: the stamp uses `transform: rotate(-2deg)` and a `2px solid var(--rust)` border. The inner pseudo-border sits 12px in from each edge.

### 8.4 Timeline / chronology list

A two-column grid: date in JetBrains Mono on the left, prose on the right, hairline rule between rows.

```css
.timeline li {
  display: grid;
  grid-template-columns: 130px 1fr;
  gap: 24px;
  padding: 18px 0;
  border-bottom: 1px solid var(--rule);
  align-items: baseline;
}
.timeline .when {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--ochre-deep);
  font-weight: 500;
}
```

On mobile (`max-width: 700px`), collapse to single column.

### 8.5 Inverted facts grid

Full-bleed dark section. Grid of cards with hairline borders between them (achieved with `gap: 1px` over a translucent paper background — a classic CSS trick).

```css
.facts {
  background: var(--ink);
  color: var(--paper);
  padding: 100px 24px;
  margin: 80px -8vw 0;
}
.facts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1px;
  background: rgba(241, 234, 217, 0.15);
  border: 1px solid rgba(241, 234, 217, 0.15);
}
.fact { background: var(--ink); padding: 36px 28px; transition: background 0.4s; }
.fact:hover { background: #2a221a; }
.fact .num {
  font-family: 'Cinzel', serif;
  font-size: 38px;
  color: var(--ochre);
  display: block;
  margin-bottom: 8px;
}
.fact .num small { font-size: 0.5em; letter-spacing: 0.1em; opacity: 0.7; }
.fact h4 {
  font-family: 'Cinzel', serif;
  font-size: 13px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
```

Each card has: a Cinzel large numeral (or short alphanumeric like `R1b` or `2,822 BCE`), a tiny uppercase Cinzel heading, and a short body paragraph.

### 8.6 Reading list / references

Two-column grid (Roman numeral marker, content), set inside a `--paper-deep` block. Hairline rules separate each entry.

```css
.reading .item {
  padding: 24px 0;
  border-top: 1px solid var(--rule);
  display: grid;
  grid-template-columns: 50px 1fr;
  gap: 16px;
}
.reading .num-r {
  font-family: 'Cinzel', serif;
  font-size: 22px;
  color: var(--ochre-deep);
}
.reading .ref-meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ochre-deep);
}
```

### 8.7 Colophon (footer)

Centered, JetBrains Mono, low opacity. Single line of glyphs (`✦ ⊹ ✦`) on top, then 2-3 lines of metadata.

---

## 9. Responsive Rules

Single breakpoint at `700px`. Below it:

```css
@media (max-width: 700px) {
  body { font-size: 17px; }
  .hero { padding: 50px 24px; }
  .hero::before, .hero::after { left: 24px; right: 24px; }
  .masthead { font-size: 10px; gap: 16px; flex-wrap: wrap; margin-bottom: 60px; }
  .meta-strip { gap: 24px; }
  .timeline li { grid-template-columns: 1fr; gap: 4px; }
  .timeline .when { font-size: 11px; }
  .book-feature { padding: 40px 28px; margin: 40px 0; }
  .reading { margin: 60px -24px 0; }
  .facts { margin: 60px -24px 0; padding: 60px 20px; }
  .reading .item { grid-template-columns: 36px 1fr; gap: 10px; }
}
```

The `clamp()` calls in headline sizes handle most of the in-between gracefully. No tablet breakpoint needed.

---

## 10. Page Templates

For converting an existing site, identify which template each existing page maps to:

### 10.1 Article / long-form post template

```
[Hero — full viewport]
  Masthead row
  H1 title with italic ochre subtitle
  Deck (italic, max 60ch)
  Meta strip (subject / topic / period / filed)

[Ornament I]

[Body section]
  § 01 — Section name
  H2
  Lead paragraph (drop cap)
  Body paragraphs
  Optional: H3 subheadings, blockquotes, book-features

[Ornament II — repeat between every major section]

[Body section]
  ...

[Inverted facts/highlights block — full-bleed dark]

[Reading list / references — paper-deep block]

[Colophon]
```

### 10.2 Index / archive page

- Same hero pattern, but title becomes the site/archive name
- Replace body sections with a list using the `timeline` pattern: date on the left, post title + dek on the right
- Optionally a single facts/highlights block

### 10.3 About / colophon page

- Hero with shorter deck
- Single body section, prose-heavy
- A book-feature-style card for any prominent credentials/affiliations
- Colophon

### 10.4 Project / portfolio page

- Hero
- One book-feature card per project (with the rotated stamp showing the project status: "Live", "Archived", "In Progress")
- Body prose between projects
- Reading-list pattern works well for press / external links

---

## 11. Refactor Checklist for Claude Code

When applying this system to an existing site, work through this list **in order**:

1. **Audit existing pages.** Generate a list of every HTML/markdown file. Note which template (10.1–10.4 above) each maps to.

2. **Set up tokens.** Create `assets/css/tokens.css` (or equivalent) with the `:root` color and font variables from §2 and §3. Import it everywhere.

3. **Replace fonts.** Remove every existing font import (Inter, Roboto, system stacks, etc.). Add the single Google Fonts link from §3. Search the codebase for `font-family` declarations and replace them with the three approved stacks.

4. **Replace colors.** Search for hex codes, `rgb()`, named colors, and Tailwind color classes. Replace with `var(--token)` references. If the site uses Tailwind, either configure the Tailwind theme to expose these as `colors.ink`, `colors.paper`, etc., OR drop Tailwind for layout and keep it only for utility spacing.

5. **Apply the body texture.** Add the SVG noise + dual radial gradient background from §7 to `body`.

6. **Rebuild the hero.** For each page, lift the existing title/intro into the hero pattern from §4. Add masthead, deck, and meta strip even if some fields are placeholder.

7. **Add section structure.** Wrap content in `<section>` blocks. Add `.section-num` labels (`§ 01 — ...`). Insert ornaments between sections.

8. **Convert prose.** Change body paragraphs to justified, hyphenated. Apply `.lead` class with drop cap to first paragraph of each major section.

9. **Convert lists, tables, callouts.** Map existing components to the patterns in §8: blockquotes → §8.2, feature cards → §8.3, timeline/changelog → §8.4, stat blocks → §8.5, link lists / bibliography → §8.6.

10. **Add a colophon.** Replace the existing footer with the §8.7 colophon pattern.

11. **Test mobile.** Verify the §9 breakpoint behavior on every page.

12. **Strip unused CSS.** Once converted, prune any dead styles from the previous theme.

---

## 12. Things to Preserve from the Existing Site

Before refactoring, identify and **do not break**:

- Permalink/URL structure (SEO)
- Existing meta tags, OpenGraph, RSS feeds
- Image alt text and accessibility attributes
- Any JavaScript functionality (search, navigation, form handlers)
- Build-tool configuration (Eleventy, Hugo, Astro, Jekyll, etc.) — only restyle, don't migrate frameworks unless asked

---

## 13. Anti-patterns — Things to Actively Avoid

- ❌ Adding gradients beyond the two warm radial gradients on body
- ❌ Box-shadows on cards (the design uses borders and hairline rules instead)
- ❌ Border-radius above 0px — this aesthetic is sharp-cornered. Everything is a rectangle.
- ❌ Hover effects beyond the subtle `--ink` → `#2a221a` shift on facts cards. No lift, no scale, no glow.
- ❌ Icons. The ornaments (`✦ ⊹ §`) are the only iconography.
- ❌ Sans-serif anywhere except JetBrains Mono in its specific roles.
- ❌ Centered body prose. Body is left-aligned (justified), titles can be left or grid-aligned.
- ❌ Animation beyond the very subtle `transition: background 0.4s` on facts cards.

---

## 14. One-line summary for the agent

> Refactor this site to a serif-led editorial-journal aesthetic on warm paper-toned backgrounds, using Cinzel for display, Cormorant Garamond for body, and JetBrains Mono for metadata; replace all colors with the seven-token palette anchored on `--ink #1a1612` and `--paper #f1ead9`; structure every page as Hero → numbered Sections divided by `✦ — II — ✦` ornaments → optional inverted facts block → reading list → colophon; preserve URLs, build config, and accessibility throughout.
