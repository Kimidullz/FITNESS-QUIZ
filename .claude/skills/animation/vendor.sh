#!/usr/bin/env bash
# Copies pinned animation libraries from npm into <target>/libs/ so render pages
# can load them as local files. The sandbox blocks the CDNs (cdnjs, unpkg,
# jsdelivr) but npm works, so this is how libraries get into a cloud render.
# Usage: bash vendor.sh <target-dir>
set -euo pipefail
TARGET="${1:?usage: vendor.sh <target-dir>}"
CACHE="${HOME}/.cache/anim-libs"
mkdir -p "$CACHE" "$TARGET/libs"
if [ ! -d "$CACHE/node_modules/three" ]; then
  (cd "$CACHE" && [ -f package.json ] || npm init -y >/dev/null
   cd "$CACHE" && npm i --silent --no-audit --no-fund \
     gsap@3.13.0 animejs@3.2.2 lottie-web@5.12.2 three@0.170.0)
fi
NM="$CACHE/node_modules"
for f in gsap ScrollTrigger MotionPathPlugin SplitText DrawSVGPlugin MorphSVGPlugin TextPlugin CustomEase; do
  cp "$NM/gsap/dist/$f.min.js" "$TARGET/libs/"
done
cp "$NM/animejs/lib/anime.min.js" "$TARGET/libs/"
cp "$NM/lottie-web/build/player/lottie.min.js" "$TARGET/libs/"
cp "$NM/three/build/three.module.min.js" "$TARGET/libs/"
mkdir -p "$TARGET/libs/three-addons" && cp -r "$NM/three/examples/jsm/." "$TARGET/libs/three-addons/"
echo "Libraries copied to $TARGET/libs"
