# Impeccable Style Setup — Mosaic Hostels

**Integration Date:** 2026-06-26  
**Service:** https://impeccable.style/  
**Purpose:** 1-click frontend design validation + anti-pattern detection  

---

## Setup Instructions

### 1. Install Impeccable Skill
```bash
# Via Claude Code (auto-discovered)
/impeccable
```

### 2. Available Commands (23 total)
See https://impeccable.style/ for full list. Key commands:

- `validate` — Check component against design system
- `audit` — Full page design audit (colors, spacing, typography)
- `contrast` — Verify WCAG AA contrast ratios
- `responsive` — Check breakpoint compliance
- `accessibility` — Scan for a11y issues
- `performance` — Check CSS/JS performance
- `anti-patterns` — Detect common design mistakes

### 3. Project Integration

#### 3.1 Before Design Review
Run validation on all components:
```bash
/impeccable validate --file design-tokens.css
/impeccable audit --file index.html
/impeccable accessibility --file index.html
```

#### 3.2 Before Launch
Run full audit:
```bash
/impeccable audit --project .
/impeccable contrast --file styles/design-tokens.css
/impeccable responsive --breakpoints 375,768,1024,1440
```

#### 3.3 Continuous Monitoring
Add to CI/CD pipeline:
```yaml
# .github/workflows/design-audit.yml
name: Design Audit
on: [pull_request]
jobs:
  impeccable:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: /impeccable audit --project .
      - run: /impeccable contrast --file styles/
```

---

## Design System Alignment

### Mosaic Hostels Design Tokens → Impeccable Validation

| Token | Value | Impeccable Check |
|-------|-------|------------------|
| Primary Color | #E11D48 | Contrast vs all backgrounds |
| Text Primary | #1F2937 | WCAG AA minimum 4.5:1 |
| Touch Target | 44×44px | Responsive grid validation |
| Spacing | 8dp grid | Consistency audit |
| Animation | 150-300ms | Performance check |

### Anti-Patterns to Flag
❌ Hardcoded hex values (use CSS variables)  
❌ Non-semantic HTML (use heading hierarchy)  
❌ Icon-only buttons (add aria-labels)  
❌ Fixed containers (use responsive units)  
❌ No focus states (require :focus rings)  
❌ Text < 12px (accessibility violation)  
❌ Color-only differentiation (add icons/text)  
❌ Animation > 500ms (performance issue)  

---

## Workflow Integration

### Pre-Code-Review Checklist
- [ ] Run `/impeccable audit` on new files
- [ ] Fix flagged anti-patterns
- [ ] Verify contrast ratios (WCAG AA)
- [ ] Check responsive breakpoints
- [ ] Test accessibility (keyboard, screen reader)

### Pre-Merge Checklist
- [ ] `/impeccable audit --project .` passes
- [ ] No accessibility warnings
- [ ] Performance score ≥90
- [ ] All breakpoints tested (375, 768, 1024, 1440)
- [ ] Dark mode verified

### Pre-Launch Checklist
- [ ] Full Impeccable audit clean
- [ ] Lighthouse score ≥90 (all metrics)
- [ ] Manual testing on real devices
- [ ] Analytics tracking ready
- [ ] Deployment plan documented

---

## Command Reference

### Validation
```bash
/impeccable validate <file>          # Single component
/impeccable audit <file>             # Full page audit
/impeccable audit --project .        # Entire project
```

### Accessibility
```bash
/impeccable accessibility <file>     # A11y scan
/impeccable contrast <file>          # Contrast check (WCAG AA)
/impeccable focus <file>             # Focus state validation
```

### Responsive & Performance
```bash
/impeccable responsive <file>        # Breakpoint check
/impeccable responsive --breakpoints 375,768,1024,1440
/impeccable performance <file>       # CSS/JS perf
```

### Anti-Patterns
```bash
/impeccable anti-patterns <file>     # Detect common mistakes
/impeccable suggestions <file>       # Design improvement ideas
```

---

## Integration with Design System

### Color Validation
```bash
/impeccable contrast --file .claude/DESIGN_SYSTEM.md
# Verifies: Primary/Secondary/Accent colors meet 4.5:1 ratio
```

### Typography Validation
```bash
/impeccable audit --typography
# Verifies: Font sizes, weights, line heights per design system
```

### Component Validation
```bash
/impeccable validate .claude/DESIGN_HOMEPAGE_MOCKUP.html
# Verifies: Buttons, cards, forms match design specs
```

---

## Task Defaults with Impeccable

### New Design Task Template
```markdown
- [ ] Design component [NAME]
  - [ ] Create mockup (HTML/CSS)
  - [ ] Run `/impeccable validate` ← Must pass
  - [ ] Check contrast (WCAG AA)
  - [ ] Test on 375px, 1024px
  - [ ] Run accessibility audit
  - [ ] Code review + merge
```

### New Feature Task Template
```markdown
- [ ] Build [FEATURE]
  - [ ] Follow design system
  - [ ] Run `/impeccable audit`
  - [ ] Fix anti-patterns
  - [ ] Lighthouse ≥90
  - [ ] Test accessibility
```

### Pre-Launch Task Template
```markdown
- [ ] Pre-launch design audit
  - [ ] `/impeccable audit --project .`
  - [ ] Fix all flagged issues
  - [ ] Verify contrast ratios
  - [ ] Test dark mode
  - [ ] Check responsive (375-1440px)
  - [ ] Performance optimization
  - [ ] Analytics tracking ready
```

---

## Configuration File

Create `.impeccable.config.json` in project root:

```json
{
  "breakpoints": [375, 768, 1024, 1440],
  "wcagLevel": "AA",
  "colorContrast": 4.5,
  "minTouchTarget": 44,
  "maxAnimationDuration": 500,
  "designSystemFile": ".claude/DESIGN_SYSTEM.md",
  "excludePatterns": ["node_modules", ".git", "vendor"],
  "autoFix": false,
  "reportFormat": "json"
}
```

---

## Resources

- **Impeccable Docs:** https://impeccable.style/
- **WCAG 2.1 AA:** https://www.w3.org/WAI/WCAG21/quickref/
- **Design System:** `.claude/DESIGN_SYSTEM.md` (14 sections)
- **Mockup:** `.claude/DESIGN_HOMEPAGE_MOCKUP.html` (test here)

---

## Next Steps

1. ✅ Install `/impeccable` skill
2. ✅ Run baseline audit on mockup
3. ✅ Configure `.impeccable.config.json`
4. ✅ Add pre-launch task to todos
5. ✅ Integrate into CI/CD pipeline (future)

---

**Status:** Setup Complete — Ready for Design Validation
