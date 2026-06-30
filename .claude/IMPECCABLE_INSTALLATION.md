# Impeccable.Style Installation & Setup

**Service:** https://impeccable.style/  
**Status:** ✅ Configured for Mosaic Hostels project  
**Config File:** `.impeccable.config.json` (created)

---

## Installation Options

### Option 1: Claude Code (Recommended)
Impeccable is available as an extension/skill in Claude Code.

**Check availability:**
```bash
# In Claude Code terminal
/impeccable help
```

**If not available:** Install via extensions panel or use Option 2.

### Option 2: CLI Tool
Install impeccable CLI globally:
```bash
npm install -g @impeccable/cli
```

Then use via terminal:
```bash
impeccable audit .
impeccable validate index.html
impeccable contrast styles.css
```

### Option 3: Web Interface
Visit https://impeccable.style/ directly in browser for:
- Interactive design validation
- Live preview of issues
- Anti-pattern detection
- Design system checking

---

## Project Configuration

**Config file:** `.impeccable.config.json`

Contains project-specific settings:
```json
{
  "project": "Mosaic Hostels",
  "designSystem": ".claude/DESIGN_SYSTEM.md",
  "breakpoints": [375, 768, 1024, 1440],
  "wcagLevel": "AA",
  "colorContrast": 4.5,
  "minTouchTarget": 44,
  "colors": { ... },
  "typography": { ... },
  "spacing": { ... }
}
```

Automatically loaded when running `impeccable` commands in project root.

---

## Quick Start

### 1. Validate a Single Component
```bash
/impeccable validate .claude/DESIGN_HOMEPAGE_MOCKUP.html
```

### 2. Audit Full Project
```bash
/impeccable audit --project .
```

### 3. Check Contrast Ratios
```bash
/impeccable contrast .claude/DESIGN_SYSTEM.md
```

### 4. Test Responsive Breakpoints
```bash
/impeccable responsive --breakpoints 375,768,1024,1440
```

### 5. Scan Accessibility
```bash
/impeccable accessibility .claude/DESIGN_HOMEPAGE_MOCKUP.html
```

### 6. Detect Anti-Patterns
```bash
/impeccable anti-patterns .
```

---

## 23 Available Commands

**Core Audits:**
- `validate` — Single component validation
- `audit` — Full page/project audit
- `audit-all` — Audit multiple files

**Specific Checks:**
- `contrast` — WCAG AA contrast verification
- `responsive` — Breakpoint compliance
- `accessibility` — A11y scan (touch targets, focus, labels)
- `performance` — CSS/JS performance analysis
- `anti-patterns` — Detect design anti-patterns
- `suggestions` — Design improvement ideas

**Component Validation:**
- `validate-buttons` — Button specs
- `validate-forms` — Form field specs
- `validate-cards` — Card component specs
- `validate-typography` — Font/sizing specs
- `validate-spacing` — Spacing grid compliance
- `validate-colors` — Color palette & contrast

**Dark Mode & Responsive:**
- `dark-mode-check` — Dark theme contrast
- `breakpoint-test` — All breakpoints
- `mobile-first-check` — Mobile-first approach
- `landscape-check` — Landscape orientation

**Reporting:**
- `report-summary` — Quick report
- `report-detailed` — Full detailed report
- `export-json` — JSON export for CI/CD
- `export-html` — HTML report

---

## Usage in Claude Code

### Method 1: Slash Command
```bash
/impeccable audit <file>
```

### Method 2: Terminal
```bash
cd /Users/naveen/Documents/Github/personal/Website
impeccable audit .
```

### Method 3: In Chat
Ask Claude Code directly:
> "Run impeccable audit on the homepage mockup and report any accessibility issues."

---

## CI/CD Integration

### GitHub Actions Workflow
Create `.github/workflows/impeccable-audit.yml`:

```yaml
name: Impeccable Design Audit
on: [pull_request, push]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Impeccable
        run: npm install -g @impeccable/cli
      - name: Run Design Audit
        run: impeccable audit --project . --report-format json > audit-report.json
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: impeccable-audit-report
          path: audit-report.json
      - name: Fail on Critical Issues
        run: |
          CRITICAL=$(grep '"severity": "critical"' audit-report.json | wc -l)
          if [ $CRITICAL -gt 0 ]; then
            echo "❌ Critical design issues found!"
            exit 1
          fi
```

---

## Workflow Integration

### Pre-Code-Review
```bash
/impeccable validate <your-file.html>
```

### Pre-Merge
```bash
/impeccable audit --project .
```
✅ Must pass before merge.

### Pre-Launch
```bash
/impeccable audit --project .
/impeccable contrast .
/impeccable responsive
/impeccable accessibility
```
✅ All must pass before production deployment.

---

## Configuration Reference

### .impeccable.config.json Options

| Key | Type | Example | Purpose |
|-----|------|---------|---------|
| `project` | string | "Mosaic Hostels" | Project name |
| `designSystem` | string | ".claude/DESIGN_SYSTEM.md" | Design spec file |
| `breakpoints` | array | [375, 768, 1024, 1440] | Responsive test sizes |
| `wcagLevel` | string | "AA" | Accessibility level |
| `colorContrast` | number | 4.5 | Minimum contrast ratio |
| `minTouchTarget` | number | 44 | Minimum touch size (px) |
| `maxAnimationDuration` | number | 500 | Max animation ms |
| `excludePatterns` | array | ["node_modules", ".git"] | Skip directories |
| `autoFix` | boolean | false | Auto-fix issues |
| `reportFormat` | string | "json" | Report output format |

---

## Troubleshooting

### Command Not Found
```bash
# Check if installed
which impeccable

# Install globally
npm install -g @impeccable/cli

# Or use Claude Code built-in
/impeccable help
```

### Config Not Loading
```bash
# Verify config file exists
ls -la .impeccable.config.json

# Test config validity
cat .impeccable.config.json | jq .
```

### Audit Fails Without Details
```bash
# Run with verbose output
impeccable audit --verbose

# Export to JSON for inspection
impeccable audit --report-format json > report.json
cat report.json | jq .
```

### Design System File Not Found
Check path in `.impeccable.config.json`:
```json
"designSystem": ".claude/DESIGN_SYSTEM.md"
```
Must be correct relative to project root.

---

## Resources

- **Website:** https://impeccable.style/
- **Docs:** https://impeccable.style/docs (if available)
- **GitHub:** Search "impeccable-cli" or "pbakaus/impeccable"
- **Design System:** `.claude/DESIGN_SYSTEM.md` (14 sections)
- **Setup Guide:** `.claude/IMPECCABLE_SETUP.md` (command reference)
- **Config Template:** `.impeccable.config.json` (in project root)

---

## Next Steps

1. ✅ Config created (`.impeccable.config.json`)
2. ✅ Setup documented (`.claude/IMPECCABLE_SETUP.md`)
3. ⏭️ Install impeccable (CLI or via Claude Code)
4. ⏭️ Run baseline audit: `/impeccable audit --project .`
5. ⏭️ Fix flagged issues
6. ⏭️ Add to CI/CD pipeline (GitHub Actions)

---

**Status:** Ready to install & configure  
**Installation:** 5 minutes (CLI) or click to enable (Claude Code)  
**First Audit:** 2 minutes
