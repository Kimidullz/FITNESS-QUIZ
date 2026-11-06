---
name: animation
description: Use when animating anything for Kimi (reels, title cards, kinetic text, carousel motion, quiz-site effects, 3D scenes) with GSAP, anime.js, Lottie or three.js. Covers pinned CDN links for published pages, local copies for cloud renders, and the frame-by-frame Puppeteer/Playwright render pattern.
---

# Animation libraries

Four libraries, pinned. Pick the smallest one that does the job.

| Library | Version | Use it for |
|---|---|---|
| GSAP (+ plugins) | 3.13.0 | Default. Timelines, kinetic text (SplitText), SVG drawing/morphing, motion paths. All plugins are free since 3.13. |
| anime.js | 3.2.2 | Light one-off tweens and staggers when GSAP is overkill. Global `anime`. |
| Lottie (lottie-web) | 5.12.2 | Playing a ready-made After Effects / LottieFiles `.json` animation (icons, stickers, confetti). |
| three.js | 0.170.0 | Real 3D (rotating product, glass, particles). Heavy, see "3D" below. |

## Two ways to load them

**1. Published pages (Artifacts, the GitHub Pages quiz site, anything a viewer opens in a browser): CDN tags.**

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/SplitText.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/MotionPathPlugin.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/DrawSVGPlugin.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.2/anime.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
<script type="importmap">{ "imports": {
  "three": "https://unpkg.com/three@0.170.0/build/three.module.min.js",
  "three/addons/": "https://unpkg.com/three@0.170.0/examples/jsm/" } }</script>
```

Only include the tags the page actually uses. Register GSAP plugins with `gsap.registerPlugin(ScrollTrigger, SplitText)`.

**2. Cloud renders (making an MP4 in this sandbox): local copies.** The sandbox blocks cdnjs, unpkg and jsdelivr, but npm works. Copy the libraries next to the render page:

```bash
bash .claude/skills/animation/vendor.sh <render-folder>   # creates <render-folder>/libs/
```

Then load `libs/gsap.min.js`, `libs/SplitText.min.js`, `libs/anime.min.js`, `libs/lottie.min.js`, `libs/three.module.min.js` (and `libs/three-addons/...`) by relative path.

## Rendering a video (the pattern every reel uses)

Never let animations play in real time during a render, or frames come out uneven. Build everything paused and move it to an exact time per frame. A working starter is in `template/` (WDT colours, GSAP SplitText + anime.js stagger, 4 s at 30 fps, 1080x1920):

```bash
cp -r .claude/skills/animation/template <work>/my-reel
bash .claude/skills/animation/vendor.sh <work>/my-reel
cd <work>/my-reel && NODE_PATH=$(npm root -g) node render.js frames 4
ffmpeg -framerate 30 -i frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
```

The page contract (same as the earlier BMR reel renders): it sets `window.TOTAL_FRAMES`, `window.ready` (a promise that resolves once fonts/assets load) and `window.renderFrame(f)`. `index.html#f=45` shows frame 45 for a quick look.

How to drive each library from `renderFrame(f)`, with `t = f / FPS`:

- **GSAP:** one `gsap.timeline({ paused: true })`, then `tl.seek(t, false)`. Call `gsap.ticker.lagSmoothing(0)`. For ScrollTrigger-style effects in a video, animate on the timeline instead of scroll.
- **anime.js:** create with `autoplay: false`, then `anim.seek(t * 1000)` (milliseconds).
- **Lottie:** `lottie.loadAnimation({ container, path: 'anim.json', renderer: 'svg', autoplay: false, loop: false })`, wait for its `DOMLoaded` event inside `window.ready`, then `anim.goToAndStop(t * 1000, false)` (or by frame: `goToAndStop(frame, true)`).
- **three.js:** no clock. Set positions/rotations from `t` yourself, then `renderer.render(scene, camera)`. Create the renderer with `preserveDrawingBuffer: true` so the screenshot sees the canvas.

## 3D and heavy scenes

The cloud machine has no GPU (WebGL runs on the slow SwiftShader software renderer). A simple three.js scene is fine here; anything heavy (lots of particles, glass/refraction, post-processing, long 3D reels) goes on Kimi's own PC through a Remote Control session, using the CDN version of the page or the same `libs/` folder copied over.

## House rules that still apply

- WDT colours: black, white, red `#E30613`, yellow `#FFD200`. English copy unless Kimi asks for Malay.
- Carousels are 4:5 (1080x1350) for both IG and TikTok. Reels/videos are 9:16 (1080x1920).
- Keep motion readable: Kimi's audience includes older viewers, so give text time on screen and avoid frantic cuts.
- Never put copyrighted song lyrics on screen; Kimi adds music in TikTok/CapCut.
- For bigger video projects, the `hyperframes` skill is the other option; it also needs GSAP copied locally (vendor.sh does that).
