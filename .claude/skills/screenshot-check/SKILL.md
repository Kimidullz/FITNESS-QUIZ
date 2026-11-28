---
name: screenshot-check
description: Give Claude eyes. Screenshot a page of the ARAMI site (or any HTML file, carousel or poster page) at phone and desktop widths with the pre-installed Playwright, flag JS errors and sideways scroll, then look at the shots and fix what is wrong. Use after every visual change, before saying a page is done.
---

# Screenshot check

This is our stand-in for `playwright-mcp`. The cloud box already has Chromium and
Playwright, so no MCP server or install is needed.

## Steps

1. Shoot the page (phone 390 and desktop 1440 by default):
   ```bash
   node .claude/skills/screenshot-check/shoot.js index.html "$SCRATCH/shots" 390,1440
   ```
   A URL works too: the live site is `https://kimidullz.github.io/FITNESS-QUIZ/`
   (uppercase path; the lowercase one is a 404), e.g. `.../FITNESS-QUIZ/?lang=en`.
2. Open each PNG with the Read tool and actually look: cut-off text, overlaps,
   tiny tap targets, low contrast, broken images, odd gaps, anything off-brand
   (WDT colours black/white, red #E30613, yellow #FFD200).
3. Read the PROBLEMS list the script prints (JS errors, sideways scroll).
4. Fix, then shoot again. Batch fixes: fix everything one look shows before
   shooting again. Stop after it looks right at both widths.
5. Check both languages when the page has them (BM default, `?lang=en`).

For a 1080x1350 carousel slide page, pass the width only: `... slides.html out 1080`.
Keep screenshots in the scratchpad, not in the repo (the repo is the live site).
