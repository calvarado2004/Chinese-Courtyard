import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { roofTexture, pavingTexture, glowTexture, grassTexture } from './textures.js';
import { loadCritters, updateLife } from './life.js';
import { initLeaves, updateLeaves } from './leaves.js';

/* ---------------------------------------------------------------- basics */

const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const SKY = [
  new THREE.Color(0xb9d2e2),   // day
  new THREE.Color(0xdfa06b),   // sunset
  new THREE.Color(0x0a0e1a),   // night
];
scene.background = SKY[0].clone();
scene.fog = new THREE.Fog(SKY[0].getHex(), 46, 170);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 220);
camera.position.set(16.5, 12, 14);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.0, -0.5);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 1.6;
controls.maxDistance = 70;

/* ---------------------------------------------------------------- lights */

const sun = new THREE.DirectionalLight(0xfff1dc, 3.2);
sun.position.set(20, 26, 13);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
sun.shadow.camera.far = 70;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.03;
scene.add(sun);

const hemi = new THREE.HemisphereLight(0xcfe0ee, 0x8a8375, 0.75);
scene.add(hemi);

const SUN = [
  { c: new THREE.Color(0xfff1dc), i: 3.2, p: new THREE.Vector3(20, 26, 13) },
  { c: new THREE.Color(0xff9e4f), i: 2.4, p: new THREE.Vector3(24, 6.5, -3) },
  { c: new THREE.Color(0x9db4ff), i: 0.28, p: new THREE.Vector3(-22, 20, -10) },
];
const HEMI = [
  { sky: new THREE.Color(0xcfe0ee), gnd: new THREE.Color(0x8a8375), i: 0.75 },
  { sky: new THREE.Color(0xe8b088), gnd: new THREE.Color(0x6e5a4a), i: 0.55 },
  { sky: new THREE.Color(0x1a2238), gnd: new THREE.Color(0x0c0e14), i: 0.32 },
];
const GLOW = {   // emissive / light fractions per mode (day, sunset, night)
  paper: [0, 0.35, 0.75],
  lantern: [0, 0.65, 1.6],
  warm: [0, 0.55, 1],
  stars: [0, 0, 1],
  moon: [0, 0.35, 0.9],
};

// warm interior/lantern lights, off during the day
const warmLights = [];
function addWarm(x, y, z, intensity) {
  const p = new THREE.PointLight(0xffb45a, 0, 7, 2);
  p.position.set(x, y, z);
  p.userData.maxIntensity = intensity;
  scene.add(p);
  warmLights.push(p);
}
addWarm(1.55, 0.95, 1.5, 2.6);   // stone lantern by the path
addWarm(0, 2.4, -4.3, 3.0);      // living room
addWarm(6.8, 1.6, 0.2, 2.4);     // tea room
addWarm(-6.9, 1.7, -0.5, 1.8);   // bedroom lamp

/* ---------------------------------------------------------------- sky extras */

const stars = (() => {
  const n = 900, pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2;
    const e = Math.acos(Math.random() * 0.95); // upper dome
    const r = 78;
    pos[i * 3] = r * Math.sin(e) * Math.cos(a);
    pos[i * 3 + 1] = r * Math.cos(e) + 2;
    pos[i * 3 + 2] = r * Math.sin(e) * Math.sin(a);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const m = new THREE.PointsMaterial({
    size: 0.32, map: glowTexture(), transparent: true, opacity: 0,
    depthWrite: false, blending: THREE.AdditiveBlending, color: 0xdfe8ff,
  });
  const p = new THREE.Points(g, m);
  p.renderOrder = -1;
  scene.add(p);
  return p;
})();

const moon = (() => {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture('rgba(226,234,255,1)', 'rgba(226,234,255,0)'),
    transparent: true, opacity: 0, depthWrite: false,
  }));
  s.position.set(-42, 34, -26);
  s.scale.setScalar(9);
  scene.add(s);
  return s;
})();

/* ---------------------------------------------------------------- loading */

const manager = new THREE.LoadingManager();
const barIn = document.getElementById('barIn');
manager.onProgress = (url, loaded, total) => { barIn.style.width = `${(loaded / total) * 100}%`; };

function showLoadError(msg) {
  const el = document.getElementById('loadErr');
  if (el) { el.textContent = msg; el.classList.add('show'); }
  barIn.parentElement.style.opacity = 0.25;
}
manager.onError = (url) => showLoadError(`Failed to load ${url}\nIs the static server running with web/ as its root?`);

const loader = new GLTFLoader(manager);
const emissive = { paper: [], lantern: [] };   // materials driven by day/night
let roofsHidden = false;
const roofMats = new Set();
const roofRoots = [];

function upgradeMaterials(root) {
  root.traverse((o) => {
    if (!o.isMesh) return;
    o.castShadow = !(o.name === 'Ground');
    o.receiveShadow = true;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of mats) {
      if (!m) continue;
      if (m.name === 'RoofTile' && !m.map) {
        m.map = roofTexture();
        m.color = new THREE.Color(0xffffff);
        m.roughness = 0.75;
      } else if (m.name === 'GroundPaving' && !m.map) {
        m.map = pavingTexture();
        m.map.repeat.set(0.5, 0.5);   // one texture span ≈ 2.25 m → flagstones ~1.1 m
        m.color = new THREE.Color(0xffffff);
        m.roughness = 0.95;
      } else if (m.name === 'TerrainEarth' && !m.map) {
        m.map = grassTexture();
        m.color = new THREE.Color(0xffffff);
        m.roughness = 1.0;
      } else if (m.name === 'PaperWarm') {
        m.emissive = new THREE.Color(0xffb45a);
        m.emissiveIntensity = 0;
        emissive.paper.push(m);
      } else if (m.name === 'LanternGlow') {
        m.emissive = new THREE.Color(0xffb45a);
        m.emissiveIntensity = 0;
        emissive.lantern.push(m);
      }
      if (m.name === 'RoofTile' || m.name === 'RidgeCap') roofMats.add(m);
    }
    if (/_Roof|_ridge|_fascia/.test(o.name)) roofRoots.push(o);
  });
}

async function loadModels() {
  const files = ['architecture.glb', 'garden.glb', 'interior.glb'];
  for (const f of files) {
    const gltf = await loader.loadAsync(`./models/${f}`);
    upgradeMaterials(gltf.scene);
    scene.add(gltf.scene);
  }
  makeWater();
}

/* ---------------------------------------------------------------- water */

let water = null;

function makeWater() {
  const pond = scene.getObjectByName('PondWater');
  if (!pond) return;
  const pos = new THREE.Vector3();
  const quat = new THREE.Quaternion();
  const scl = new THREE.Vector3();
  pond.getWorldPosition(pos);
  pond.getWorldQuaternion(quat);
  pond.getWorldScale(scl);
  pond.visible = false;

  const shader = {
    name: 'CourtyardWater',
    uniforms: {
      color: { value: null },
      tDiffuse: { value: null },
      textureMatrix: { value: null },
      uTime: { value: 0 },
      uSpout: { value: new THREE.Vector2(0.5, 0.5) },
      uAlpha: { value: 0.55 },
      uSunDir: { value: new THREE.Vector3(0, 1, 0) },
      uSunColor: { value: new THREE.Color(0xfff1dc) },
    },
    vertexShader: /* glsl */`
      uniform mat4 textureMatrix;
      varying vec4 vUv;
      varying vec2 vUvM;
      varying vec3 vWorld;
      #include <common>
      #include <logdepthbuf_pars_vertex>
      void main() {
        vUv = textureMatrix * vec4( position, 1.0 );
        vUvM = uv;
        vec4 wp = modelMatrix * vec4( position, 1.0 );
        vWorld = wp.xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
        #include <logdepthbuf_vertex>
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 color;
      uniform sampler2D tDiffuse;
      uniform float uTime;
      uniform vec2 uSpout;
      uniform float uAlpha;
      uniform vec3 uSunDir;
      uniform vec3 uSunColor;
      varying vec4 vUv;
      varying vec2 vUvM;
      varying vec3 vWorld;
      #include <logdepthbuf_pars_fragment>

      // calm water height field: two broad swells + fine ripple, slow
      float wh( vec2 p, float t ) {
        return 0.5 * sin( p.x * 21.0 + t * 0.9 ) * cos( p.y * 19.0 - t * 0.7 )
             + 0.25 * cos( p.x * 37.0 - t * 1.1 + sin( p.y * 31.0 + t * 0.5 ) )
             + 0.25 * sin( p.y * 27.0 + t * 0.8 );
      }

      void main() {
        #include <logdepthbuf_fragment>
        float t = uTime * 0.7;
        float e = 0.03;
        float hx = wh( vUvM + vec2( e, 0.0 ), t ) - wh( vUvM - vec2( e, 0.0 ), t );
        float hy = wh( vUvM + vec2( 0.0, e ), t ) - wh( vUvM - vec2( 0.0, e ), t );
        // spout wake ring, tight and fading fast
        float dS = distance( vUvM, uSpout );
        float ring = sin( dS * 40.0 - uTime * 3.0 ) * exp( - dS * 3.2 );
        vec2 dir = normalize( vUvM - uSpout + vec2( 1e-4 ) );
        vec2 off = vec2( hx, hy ) * 0.0045 + 0.010 * ring * dir;
        vec4 refl = texture2DProj( tDiffuse, vUv + vec4( off, 0.0, 0.0 ) );
        // pseudo-normal from the same field -> sun glitter path
        // (uv v runs along -world z, hence the sign flip on hy)
        vec3 viewDir = normalize( cameraPosition - vWorld );
        float fres = pow( 1.0 - clamp( viewDir.y, 0.0, 1.0 ), 2.0 );
        vec3 n = normalize( vec3( -hx * 0.55, 1.0, hy * 0.55 ) );
        vec3 R = reflect( -viewDir, n );
        float spec = pow( max( dot( R, uSunDir ), 0.0 ), 160.0 );
        vec3 tint = color * ( 0.92 + 0.08 * hx );
        vec3 col = mix( tint, refl.rgb, clamp( 0.20 + 0.75 * fres, 0.0, 1.0 ) );
        col += uSunColor * spec * 2.2;
        gl_FragColor = vec4( col, uAlpha + spec * 0.3 );
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  };

  const geo = pond.geometry.clone().rotateX(Math.PI / 2);
  geo.translate(0, 0, -0.055);   // lay the drawn surface exactly on the mirror plane
  water = new Reflector(geo, {
    textureWidth: 1024,
    textureHeight: 1024,
    color: 0x5e7d7a,
    shader,
  });
  water.material.transparent = true;
  water.position.copy(pos);
  // lift the mirror plane to the water surface height (Blender z=0.055)
  water.position.y += 0.055;
  // Reflector's mirror normal is the OBJECT's local +Z — point it up
  water.rotation.x = -Math.PI / 2;
  // spout ripple centre in the pond's uv space (uv scale 0.8 in Blender)
  water.material.uniforms.uSpout.value.set(4.7 / 0.8, 0.95 / 0.8);
  water.material.uniforms.color.value = new THREE.Color(0x5e7d7a);
  scene.add(water);
}

/* ---------------------------------------------------------------- day / sunset / night */

// time of day: 0 day · 1 sunset · 2 night; `phase` eases toward `timeMode`
let phase = 1;
let timeMode = 1;
const clock = new THREE.Clock();

const mix = (a, b, f) => a + (b - a) * f;

function applyDayNight() {
  const i = Math.min(1, Math.floor(phase));
  const f = phase - i;
  const j = i + 1;
  sun.color.copy(SUN[i].c).lerp(SUN[j].c, f);
  sun.intensity = mix(SUN[i].i, SUN[j].i, f);
  sun.position.lerpVectors(SUN[i].p, SUN[j].p, f);
  hemi.color.copy(HEMI[i].sky).lerp(HEMI[j].sky, f);
  hemi.groundColor.copy(HEMI[i].gnd).lerp(HEMI[j].gnd, f);
  hemi.intensity = mix(HEMI[i].i, HEMI[j].i, f);
  scene.background.copy(SKY[i]).lerp(SKY[j], f);
  scene.fog.color.copy(scene.background);
  stars.material.opacity = mix(GLOW.stars[i], GLOW.stars[j], f);
  moon.material.opacity = mix(GLOW.moon[i], GLOW.moon[j], f);
  for (const m of emissive.paper) m.emissiveIntensity = mix(GLOW.paper[i], GLOW.paper[j], f);
  for (const m of emissive.lantern) m.emissiveIntensity = mix(GLOW.lantern[i], GLOW.lantern[j], f);
  for (const l of warmLights) l.intensity = l.userData.maxIntensity * mix(GLOW.warm[i], GLOW.warm[j], f);
  if (water) {
    water.material.uniforms.uSunDir.value.copy(sun.position).normalize();
    water.material.uniforms.uSunColor.value.copy(sun.color);
  }
  document.getElementById('icoSun').style.display = timeMode === 0 ? '' : 'none';
  document.getElementById('icoRays').style.display = timeMode === 0 ? '' : 'none';
  document.getElementById('icoDusk').style.display = timeMode === 1 ? '' : 'none';
  document.getElementById('icoMoon').style.display = timeMode === 2 ? '' : 'none';
}

function cycleTime() {
  timeMode = (timeMode + 1) % 3;
}

/* ---------------------------------------------------------------- roof hide */

let roofOpacity = 1;
let roofTargetOp = 1;

function applyRoofs() {
  for (const m of roofMats) {
    m.transparent = roofOpacity < 0.999;
    m.opacity = roofOpacity;
    m.depthWrite = roofOpacity > 0.5;
  }
  document.getElementById('icoRoofLine').style.opacity = roofsHidden ? 0.25 : 1;
}

function toggleRoof() {
  roofsHidden = !roofsHidden;
  roofTargetOp = roofsHidden ? 0.05 : 1;
}

/* ---------------------------------------------------------------- WASD */

const keys = new Set();
addEventListener('keydown', (e) => {
  if (e.repeat) return;
  keys.add(e.code);
  if (e.code === 'KeyN') cycleTime();
  if (e.code === 'KeyR') toggleRoof();
});
addEventListener('keyup', (e) => keys.delete(e.code));

const fwd = new THREE.Vector3();
const right = new THREE.Vector3();
const move = new THREE.Vector3();

function updateWASD(dt) {
  let x = 0, z = 0;
  if (keys.has('KeyW') || keys.has('ArrowUp')) z -= 1;
  if (keys.has('KeyS') || keys.has('ArrowDown')) z += 1;
  if (keys.has('KeyA') || keys.has('ArrowLeft')) x -= 1;
  if (keys.has('KeyD') || keys.has('ArrowRight')) x += 1;
  if (!x && !z) return;
  const speed = (keys.has('ShiftLeft') || keys.has('ShiftRight')) ? 5.0 : 2.4;
  fwd.subVectors(controls.target, camera.position);
  fwd.y = 0;
  if (fwd.lengthSq() < 1e-6) return;
  fwd.normalize();
  right.crossVectors(fwd, new THREE.Vector3(0, 1, 0));
  move.set(0, 0, 0).addScaledVector(fwd, -z).addScaledVector(right, x);
  move.normalize().multiplyScalar(speed * dt);
  camera.position.add(move);
  controls.target.add(move);
  controls.target.x = THREE.MathUtils.clamp(controls.target.x, -8.6, 8.6);
  controls.target.z = THREE.MathUtils.clamp(controls.target.z, -6.2, 6.2);
  if (camera.position.y < 0.6) camera.position.y = 0.6;
}

/* ---------------------------------------------------------------- ui */

document.getElementById('btnDay').addEventListener('click', cycleTime);
document.getElementById('btnRoof').addEventListener('click', toggleRoof);

/* ---------------------------------------------------------------- boot + loop */

loadModels().then(() => {
  loadCritters(scene).catch((e) => console.error('critters failed', e));
  initLeaves(scene);
  setTimeout(() => document.getElementById('loading').classList.add('done'), 350);
  setTimeout(() => document.getElementById('hints').classList.add('dim'), 7000);
}).catch((e) => {
  console.error(e);
  showLoadError(`Could not load the scene: ${e && e.message ? e.message : e}`);
});

function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // day/night ease
  phase += (timeMode - phase) * Math.min(1, dt * 1.8);
  applyDayNight();

  // roof fade
  if (Math.abs(roofOpacity - roofTargetOp) > 0.002) {
    roofOpacity += (roofTargetOp - roofOpacity) * Math.min(1, dt * 5);
    applyRoofs();
  }

  if (water) water.material.uniforms.uTime.value = t;
  updateLife(dt, t, phase);
  updateLeaves(dt, t, phase);
  updateWASD(dt);
  controls.update();
  renderer.render(scene, camera);
}
tick();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
