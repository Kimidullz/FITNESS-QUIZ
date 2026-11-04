// v4 cinema: full-frame 9:16 three.js scene. Particle-fusion hook (instanced, angular-momentum vortex) that
// condenses into the obsidian heart, frosted-glass torso, overhead key + cyan rim + orange sweep, shadows,
// GTAO ambient occlusion, anamorphic DoF with top/bottom falloff, and 3D-tracked data for the 2D HUD.
// Exposes window.R3D = { canvas, draw(f) } — deterministic per frame.
import * as THREE from 'three';
import { ParametricGeometry } from 'three/addons/geometries/ParametricGeometry.js';
import { makePost } from './post.js';

export const VW = 1080, VH = 1920;   // hard 9:16 portrait
const FPS = 30, BEAT = 25;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (f, a, b) => clamp((f - a) / (b - a));
const eio = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
// spring impulse (mass .35, stiffness 180, damping 12) — same physics as the 2D layer
const SA = 12 / 0.7, SW = Math.sqrt(180 / 0.35 - SA * SA);
const IMP_N = (() => { const t = Math.atan(SW / SA) / SW; return Math.exp(-SA * t) * Math.sin(SW * t); })();
const spring = fr => { if (fr <= 0) return 0; const t = fr / FPS; return 1 - Math.exp(-SA * t) * (Math.cos(SW * t) + (SA / SW) * Math.sin(SW * t)); };
const kick = fr => { if (fr <= 0) return 0; const t = fr / FPS; return Math.exp(-SA * t) * Math.sin(SW * t) / IMP_N; };
const pulse = f => { const ph = ((f % BEAT) + BEAT) % BEAT; return { s: 1 + 0.09 * kick(ph) + 0.045 * kick(ph - 7), e: Math.max(0, kick(ph)) + 0.5 * Math.max(0, kick(ph - 7)) }; };

const canvas = document.createElement('canvas'); canvas.width = VW; canvas.height = VH;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance', stencil: false });
if (!renderer.capabilities.isWebGL2) console.warn('WebGL2 not available');
renderer.setPixelRatio(1); renderer.setSize(VW, VH, false);
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0b0d);

// ---------- strip-light studio, baked once into PMREM (no HDRI clutter on the glass) ----------
const env = new THREE.Scene(); env.background = new THREE.Color(0x000000);
const strip = (w, h, color, k, pos, look = [0, 0, 0]) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(k), side: THREE.DoubleSide }));
  m.position.set(...pos); m.lookAt(...look); env.add(m); return m; };
strip(0.8, 9, 0xffffff, 1.6, [-5, 0.5, -4]);            // tall side strips behind → glass silhouette
strip(0.8, 9, 0xffffff, 1.2, [5, 0.5, -4]);
strip(1.2, 9, 0x00d2ff, 4.0, [-4, 1.5, -3.5]);           // cyan rim, rear-left
strip(10, 3, 0xffffff, 0.35, [0, 6, 0]);                 // soft top box (volume for frosted glass)
strip(6, 0.6, 0xffffff, 0.6, [0, -1.5, -7]);              // far horizon rim
strip(2.5, 4, 0xcf752b, 0.25, [2.5, 1, 6]);                // warm front card
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(env, 0, 0.1, 100).texture;
scene.environmentIntensity = 0.8;

// ---------- background structural grid (melts into bokeh) ----------
const gridTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 1024; const x = c.getContext('2d');
  x.fillStyle = '#0b0b0d'; x.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i <= 32; i++) { x.strokeStyle = i % 4 === 0 ? 'rgba(247,244,235,0.26)' : 'rgba(247,244,235,0.10)'; x.lineWidth = i % 4 === 0 ? 3 : 2;
    x.beginPath(); x.moveTo(i * 32, 0); x.lineTo(i * 32, 1024); x.moveTo(0, i * 32); x.lineTo(1024, i * 32); x.stroke(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; })();
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d');
  const gr = x.createRadialGradient(256, 256, 0, 256, 256, 256); gr.addColorStop(0, 'rgba(245,248,255,1)'); gr.addColorStop(0.4, 'rgba(235,240,250,0.3)'); gr.addColorStop(1, 'rgba(230,235,245,0)');
  x.fillStyle = gr; x.fillRect(0, 0, 512, 512); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const back = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.MeshBasicMaterial({ map: gridTex, color: new THREE.Color(0.55, 0.55, 0.55) }));
// soft warm-white light pool behind the bust: gives the frosted glass something bright to scatter
const pool = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 4.2), new THREE.MeshBasicMaterial({ map: glowTex, transparent: false, color: new THREE.Color(0.62, 0.62, 0.6), blending: THREE.AdditiveBlending, depthWrite: false }));
pool.position.set(0.3, 0.4, -3.1); scene.add(pool);
back.position.set(0, 0.6, -3.6); back.scale.set(1.2, 1.8, 1); back.receiveShadow = true; scene.add(back);

const floor = new THREE.Mesh(new THREE.CircleGeometry(4, 64), new THREE.MeshStandardMaterial({ color: 0x141416, roughness: 0.35, metalness: 0.2 }));
floor.rotation.x = -Math.PI / 2; floor.position.y = -1.42; floor.receiveShadow = true; scene.add(floor);

// ---------- torso: one continuous parametric sculpture ----------
// keys: [v, y, halfWidth, halfDepth] from the rounded base to the neck cap
const K = [[0, -1.36, 0, 0], [0.03, -1.33, 0.55, 0.34], [0.10, -1.20, 0.80, 0.50], [0.28, -0.70, 0.84, 0.53], [0.46, -0.15, 0.97, 0.60],
  [0.60, 0.28, 1.10, 0.58], [0.70, 0.50, 1.27, 0.52], [0.77, 0.68, 1.18, 0.45], [0.84, 0.83, 0.64, 0.37], [0.89, 0.92, 0.37, 0.32],
  [0.96, 1.20, 0.32, 0.30], [0.985, 1.28, 0.22, 0.21], [1, 1.31, 0, 0]];
function keyAt(v) {
  let i = 0; while (i < K.length - 2 && v > K[i + 1][0]) i++;
  const p0 = K[Math.max(0, i - 1)], p1 = K[i], p2 = K[i + 1], p3 = K[Math.min(K.length - 1, i + 2)];
  const t = (v - p1[0]) / (p2[0] - p1[0]);
  const cr = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
  return [1, 2, 3].map(j => cr(p0[j], p1[j], p2[j], p3[j]));
}
const sp = (c, n) => Math.sign(c) * Math.pow(Math.abs(c), 2 / n);
const G = (x, w) => Math.exp(-(x * x) / (w * w));
const torsoGeo = new ParametricGeometry((u, v, out) => {
  const [y, a0, b0] = keyAt(v); const a = Math.max(0, a0), b = Math.max(0, b0);
  const th = u * Math.PI * 2; let x = a * sp(Math.cos(th), 2.5), z = b * sp(Math.sin(th), 2.5);
  if (z > 0) { // front: pectorals, sternum groove, a hint of abdominals
    z += 0.075 * G(y - 0.16, 0.22) * G(Math.abs(x) - 0.42, 0.28) * (z / Math.max(b, 1e-3));
    z -= 0.035 * G(x, 0.07) * G(y + 0.05, 0.55) * (z / Math.max(b, 1e-3));
    z += 0.02 * G(Math.abs(x) - 0.14, 0.1) * G(((y + 0.75) % 0.25) - 0.12, 0.06) * G(y + 0.75, 0.4);
    z += 0.03 * G(y - 0.62, 0.06) * G(Math.abs(x) - 0.4, 0.3);                   // clavicles
  } else { z += 0.035 * G(x, 0.09) * Math.min(1, -z / Math.max(b, 1e-3)); }     // spine groove
  out.set(x, y, z);
}, 160, 140);
torsoGeo.computeVertexNormals();
const glass = new THREE.MeshPhysicalMaterial({
  transparent: true, opacity: 0, color: 0xffffff, roughness: 0.15, transmission: 0.9, thickness: 1.2, ior: 1.45, metalness: 0,
  attenuationColor: new THREE.Color(0xf3f1ec), attenuationDistance: 6, specularIntensity: 1, clearcoat: 0.4, clearcoatRoughness: 0.12,
  dispersion: 0.25, side: THREE.FrontSide });
const torso = new THREE.Mesh(torsoGeo, glass); torso.castShadow = true; torso.receiveShadow = true; scene.add(torso);

// ---------- heart: high-gloss obsidian / metallic core (opaque, so it reaches the transmission buffer) ----------
const heartGeo = new ParametricGeometry((s, t, out) => {
  const T = t * Math.PI * 2, S = s * Math.PI;
  const hx = 16 * Math.pow(Math.sin(T), 3) / 17, hy = (13 * Math.cos(T) - 5 * Math.cos(2 * T) - 2 * Math.cos(3 * T) - Math.cos(4 * T)) / 17;
  const k = Math.sin(S); out.set(hx * k, (hy + 0.15) * k, 0.62 * Math.cos(S) * (0.55 + 0.45 * k));
}, 64, 96);
heartGeo.computeVertexNormals();
const obsidian = new THREE.MeshPhysicalMaterial({ color: 0x0a0a0c, metalness: 0.85, roughness: 0.1, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.6, side: THREE.DoubleSide });
const heart = new THREE.Mesh(heartGeo, obsidian); heart.castShadow = true;
const heartPivot = new THREE.Group(); heartPivot.position.set(0.2, 0.12, 0.12); heartPivot.rotation.set(0.15, -0.35, -0.38);
heartPivot.add(heart); scene.add(heartPivot);
const HEART_R = 0.46;
// warm aura behind the core: the light the glass refracts on every contraction
const aura = new THREE.Mesh(new THREE.SphereGeometry(0.30, 32, 24), new THREE.MeshBasicMaterial({ color: 0xcf752b }));
aura.position.set(0.2, 0.12, -0.22); scene.add(aura);

// ---------- particle fusion hook: one InstancedMesh, GPU-instanced draw ----------
// Each particle conserves angular momentum (omega = L / r^2) while drag pulls its radius in, so the swirl spins up
// as it funnels down the centre of the frame; a curl-like flow field adds turbulence; particles grow as they merge.
const N = 2400, HEART_POS = new THREE.Vector3(0.2, 0.12, 0.12);
const rnd = (() => { let a = 1234567; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; })();
const P = Array.from({ length: N }, () => ({ r0: 0.4 + 2.4 * Math.sqrt(rnd()), th0: rnd() * Math.PI * 2, y0: 0.8 + 3.6 * rnd(), z0: (rnd() - 0.5) * 1.2,
  L: (0.35 + 0.5 * rnd()) * (rnd() < 0.85 ? 1 : -1), d: 2 + rnd() * 26, dur: 46 + rnd() * 22, s: 0.012 + 0.022 * rnd(), ph: rnd() * 6.283 }));
const pMat = new THREE.MeshPhysicalMaterial({ color: 0xf2c9a0, roughness: 0.32, transmission: 0.55, thickness: 0.6, ior: 1.38,
  attenuationColor: new THREE.Color(0xcf752b), attenuationDistance: 0.25, sheen: 0.6, sheenColor: new THREE.Color(0xffd2a8), sheenRoughness: 0.5,
  emissive: new THREE.Color(0xcf752b), emissiveIntensity: 0.25 });   // transmission + attenuation + sheen = subsurface-style light diffusion
const pMesh = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 14, 10), pMat, N); pMesh.castShadow = true;
pMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(pMesh);
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), V = new THREE.Vector3(), Sc = new THREE.Vector3();
const flow = (x, y, z, t) => [Math.sin(1.7 * y + 2.1 * t) * Math.cos(1.3 * z), Math.sin(1.9 * z + 1.7 * t) * Math.cos(1.1 * x) * 0.5, Math.sin(1.5 * x + 1.3 * t) * Math.cos(1.6 * y)];
function particleState(p, f, out) {
  const u = clamp((f - p.d) / p.dur); if (u >= 1) return 0;
  const k = 1 - Math.pow(1 - u, 2.2);                                   // drag: fast start, settles into the core
  const r = Math.max(0.02, p.r0 * (1 - k));
  // integrate omega = L / r^2 over u (angular momentum conserved while the radius shrinks)
  let th = p.th0; const n = 18; for (let i = 0; i < n; i++) { const ui = (i + 0.5) / n * u; const ri = Math.max(0.12, p.r0 * (1 - (1 - Math.pow(1 - ui, 2.2))));
    th += p.L / (ri * ri) * (u / n) * 1.6; }
  const yc = lerp(p.y0, HEART_POS.y, 1 - Math.pow(1 - u, 1.6));
  const amp = 0.35 * (1 - k), fl = flow(p.r0 * Math.cos(th), yc, p.z0, f / 30 + p.ph);
  out.set(HEART_POS.x + r * Math.cos(th) + amp * fl[0], yc + amp * fl[1], HEART_POS.z + p.z0 * (1 - k) + r * 0.6 * Math.sin(th) + amp * fl[2]);
  return p.s * (1 + 1.2 * k) * (u > 0.88 ? (1 - u) / 0.12 : 1) * clamp((f + 2) / 6);   // fuse: grow as they merge, then absorb
}

// ---------- lights: dark-field, cyan rim rear-left, orange key sweeping the front ----------
scene.add(new THREE.HemisphereLight(0xffffff, 0x101010, 0.05));
const top = new THREE.SpotLight(0xfff1e2, 0, 0, 0.42, 0.5, 1.5); top.position.set(0.1, 6.5, 1.2); top.target.position.set(0, 0, 0);   // overhead key
top.castShadow = true; top.shadow.mapSize.set(2048, 2048); top.shadow.bias = -0.0003; top.shadow.radius = 5; scene.add(top, top.target);
const labelLight = new THREE.PointLight(0x00d2ff, 0, 2.2, 2); scene.add(labelLight);   // glow from the HUD label onto nearby glass
const rim = new THREE.SpotLight(0x00d2ff, 0, 0, 0.42, 0.35, 1.6); rim.position.set(-3.4, 3.0, -3.4); rim.target.position.set(0, 0.3, 0);
scene.add(rim, rim.target);
const key = new THREE.SpotLight(0xcf752b, 0, 0, 0.5, 0.55, 1.4); key.position.set(-3, 1.6, 4.2); key.target.position.set(0, 0.1, 0);
key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -0.0004; key.shadow.radius = 4;
scene.add(key, key.target);
const core = new THREE.PointLight(0xff8a3a, 0, 1.6, 2); core.position.set(0.2, 0.12, 0.42); scene.add(core);

// ---------- camera + post (physical DoF locked on the heart) ----------
const camera = new THREE.PerspectiveCamera(30, VW / VH, 0.1, 80);
const SSAA = +(new URLSearchParams(location.search).get('ssaa') || 1);
const post = makePost(renderer, scene, camera, VW, VH, { ssaa: SSAA, ao: true, aoRadius: 0.3, aoAmt: 0.8 });
post.dof.aper = 900; post.dof.maxCoc = 26;
post.bloom.strength = 0.32; post.bloom.threshold = 0.9; post.bloom.radius = 0.55;
const vu = post.vig.uniforms; if (vu.amt) vu.amt.value = 0.45; if (vu.fade) vu.fade.value = 1; if (vu.warm) vu.warm.value = 0; if (vu.contrast) vu.contrast.value = 0.12; if (vu.sat) vu.sat.value = 1.05;
const heartWorld = new THREE.Vector3();

function draw(f) {
  // slow cinematic orbit + push
  const o = eio(seg(f, 0, 300)), ang = lerp(-0.30, 0.16, o), R = lerp(10.6, 9.4, o);
  camera.position.set(Math.sin(ang) * R, 0.55 + 0.15 * o, Math.cos(ang) * R);
  camera.lookAt(0.06, 0.25, 0);
  camera.setViewOffset(VW, VH, 70, 130, VW, VH);   // subject sits left of the right-hand UI rail and above the caption band
  camera.updateMatrixWorld();
  // light reveal: rim first (contour before content), then the warm key, then the heart ignites
  const rimA = eio(seg(f, 0, 16)), keyA = eio(seg(f, 8, 34)), coreA = eio(seg(f, 60, 84));
  rim.intensity = 520 * rimA; top.intensity = 160 * eio(seg(f, 4, 30));
  const sw = eio(seg(f, 0, 240));                                    // key sweeps slowly across the front facade
  key.position.set(lerp(-3.6, 3.6, sw), 1.5 + 0.3 * Math.sin(sw * Math.PI), 4.2);
  key.intensity = 45 * keyA;
  const p = pulse(f);
  const form = clamp(spring(f - 70));                                // the heart condenses from the fused particles
  heart.scale.setScalar(HEART_R * p.s * Math.max(0.001, form));
  glass.opacity = eio(seg(f, 40, 104)); torso.visible = glass.opacity > 0.001;
  let merged = 0; const box = [1e9, 1e9, -1e9, -1e9];
  for (let i = 0; i < N; i++) { const sc = f < 120 ? particleState(P[i], f, V) : 0;
    if (sc <= 0) { if (f >= P[i].d + P[i].dur) merged++; M4.makeScale(0, 0, 0); pMesh.setMatrixAt(i, M4); continue; }
    M4.compose(V, Q, Sc.setScalar(sc)); pMesh.setMatrixAt(i, M4);
    if (i % 12 === 0) { const s2 = V.clone().project(camera); const sx = (s2.x * 0.5 + 0.5) * VW, sy = (-s2.y * 0.5 + 0.5) * VH;
      box[0] = Math.min(box[0], sx); box[1] = Math.min(box[1], sy); box[2] = Math.max(box[2], sx); box[3] = Math.max(box[3], sy); } }
  pMesh.instanceMatrix.needsUpdate = true; pMesh.visible = f < 120;
  track.merged = merged; track.total = N; track.cloud = box[2] > box[0] ? box : null;
  core.intensity = coreA * (2 + 10 * p.e);
  aura.material.color.setRGB(0.81, 0.46, 0.17).multiplyScalar(coreA * (0.06 + 0.5 * p.e));
  aura.scale.setScalar(0.85 + 0.25 * p.e); aura.visible = coreA > 0.02;
  heart.getWorldPosition(heartWorld);
  post.dof.focus = camera.position.distanceTo(heartWorld);
  const hs = heartWorld.clone().project(camera);
  track.heart = { x: (hs.x * 0.5 + 0.5) * VW, y: (-hs.y * 0.5 + 0.5) * VH, r: 150 * p.s * form };
  // HUD label glow lights the glass beside it (true 3D position of the label anchor)
  labelLight.position.set(heartWorld.x + 0.9, heartWorld.y + 0.45, heartWorld.z + 0.6); labelLight.intensity = 2.5 * eio(seg(f, 96, 112)) * (1 - seg(f, 200, 214));
  post.composer.render();
  return canvas;
}

const track = {};
window.R3D = { canvas, draw, VW, VH, track };
window.r3dReady = true;
