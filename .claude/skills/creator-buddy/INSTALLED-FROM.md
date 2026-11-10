# Creator Buddy (vendored copy)

- Source: https://github.com/SpaceZephyr/creator-buddy (MIT)
- Pinned commit: edf46c567ff54b72ee2157d06f3a02dbd67aaa9c (2026-08-26)
- Copied as-is with `git archive`. Each sub-skill is exposed to Claude Code by a
  symlink in `.claude/skills/<skill-name>` that points into this folder.
- Paths like `gzh-Skills/...` inside the skills are relative to THIS folder
  (`.claude/skills/creator-buddy/`).
- To update: re-copy a newer commit over this folder and change the hash above.

Notes for this project: the skills are written in Chinese for WeChat, Xiaohongshu,
Bilibili and Douyin. Platform-data scripts need paid keys (REDFOX_API_KEY,
GUAIKEI_API_TOKEN, Volcengine/Labnana/LibTV keys) that this project does not have.
Kimi's own rules still apply: English captions by default, 4:5 carousels, WDT brand.
