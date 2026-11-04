# BMR for Dummies v4: render on a GPU PC

Needs Node 20+, ffmpeg and git.

```
git clone https://github.com/lemomo-ai/lemo-opuscar.git %USERPROFILE%\lemo-opuscar
cd %USERPROFILE%\lemo-opuscar
npm install
node node_modules/playwright-core/cli.js install chromium-headless-shell
node core/render/video.mjs <path-to>\reels\bmr-v4 --size 1080x1920 --fps 30 --workers 4 --q "ssaa=2" --out E:\Video\BMR-for-Dummies-v4-cinema.mp4
```
On Windows set `LEMO_ANGLE=d3d11` (or leave default) so Chromium uses the NVIDIA GPU.
`post.js` is a copy of lemo-opuscar `core/three/post.js` (MIT) with an anamorphic, top/bottom-falloff DoF.
