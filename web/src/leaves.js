import * as THREE from 'three';

// three.js coords (x, y=up, z); plan (x, y, z) → (x, z, -y)
const TREES = [   // pine canopies
  { x: -3.5, z: -0.3, r: 1.3 },
  { x: 7.35, z: 5.1, r: 1.1 },
  { x: -7.4, z: 5.3, r: 1.2 },
];
const BAMBOO = [
  { x: -4.35, z: 2.95, r: 0.8 },
  { x: 6.6, z: -4.6, r: 0.7 },
  { x: -1.6, z: 5.4, r: 0.6 },
];
// roofed footprints — leaves that drift into these respawn instead of clipping
const BUILDINGS = [
  { x0: -5.4, x1: 5.4, z0: -7.2, z1: -1.1 },   // main hall
  { x0: 4.7, x1: 8.9, z0: -3.5, z1: 3.5 },     // east wing
  { x0: -8.9, x1: -4.7, z0: -3.5, z1: 3.5 },   // west wing
  { x0: -1.1, x1: 4.1, z0: 3.2, z1: 6.6 },     // gatehouse
];

const COLORS = [0xd99a3a, 0xb5622f, 0x8a8f3c, 0xe0b64a, 0x96682e, 0xc47b32];
const N = 90;

function leafTexture() {
  const c = document.createElement('canvas');
  c.width = 64; c.height = 64;
  const g = c.getContext('2d');
  g.translate(32, 32);
  g.beginPath();
  g.moveTo(0, -26);
  g.bezierCurveTo(15, -14, 13, 12, 0, 26);
  g.bezierCurveTo(-13, 12, -15, -14, 0, -26);
  g.fillStyle = '#ffffff';
  g.fill();
  g.strokeStyle = 'rgba(40,25,10,0.4)';
  g.lineWidth = 2.5;
  g.beginPath(); g.moveTo(0, -22); g.lineTo(0, 22); g.stroke();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

const leaves = [];
const sway = [];
let mesh = null;
let dummy = null;
let mat = null;

function inBuilding(x, z) {
  for (const b of BUILDINGS) {
    if (x > b.x0 && x < b.x1 && z > b.z0 && z < b.z1) return true;
  }
  return false;
}

function spawn(i, first) {
  const L = leaves[i];
  const pool = Math.random();
  let x, z;
  if (pool < 0.55) {
    const t = TREES[(Math.random() * TREES.length) | 0];
    const a = Math.random() * Math.PI * 2, r = Math.random() * t.r;
    x = t.x + Math.cos(a) * r; z = t.z + Math.sin(a) * r * 0.8;
  } else if (pool < 0.75) {
    const b = BAMBOO[(Math.random() * BAMBOO.length) | 0];
    const a = Math.random() * Math.PI * 2, r = Math.random() * b.r;
    x = b.x + Math.cos(a) * r; z = b.z + Math.sin(a) * r * 0.8;
  } else {
    x = -8 + Math.random() * 16; z = -6 + Math.random() * 12;
  }
  if (inBuilding(x, z)) { spawn(i, first); return; }
  L.x = x; L.z = z;
  L.y = first ? 0.4 + Math.random() * 5 : 2.6 + Math.random() * 2.8;
  L.vy = 0.20 + Math.random() * 0.26;
  L.rx = Math.random() * Math.PI * 2; L.rz = Math.random() * Math.PI * 2;
  L.wx = (Math.random() - 0.5) * 2.4; L.wz = (Math.random() - 0.5) * 2.4;
  L.phase = Math.random() * Math.PI * 2;
  L.sway = 0.10 + Math.random() * 0.22;
  L.drift = 0.55 + Math.random() * 0.8;
  L.s = 0.7 + Math.random() * 0.6;
  L.state = 0; L.rest = 0;
}

export function initLeaves(scene) {
  const geo = new THREE.PlaneGeometry(0.10, 0.14);
  mat = new THREE.MeshLambertMaterial({
    map: leafTexture(), transparent: true, alphaTest: 0.35, side: THREE.DoubleSide,
  });
  mesh = new THREE.InstancedMesh(geo, mat, N);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  dummy = new THREE.Object3D();
  const col = new THREE.Color();
  for (let i = 0; i < N; i++) {
    leaves.push({});
    spawn(i, true);
    col.setHex(COLORS[i % COLORS.length]);
    col.offsetHSL((Math.random() - 0.5) * 0.02, 0, (Math.random() - 0.5) * 0.14);
    mesh.setColorAt(i, col);
  }
  scene.add(mesh);
  // canopy sway in the wind
  scene.traverse((o) => {
    if (/^PinePad|^BambooLeaf/.test(o.name)) {
      sway.push({ o, bx: o.rotation.x, bz: o.rotation.z, p: Math.random() * 9, w: 0.5 + Math.random() * 0.5 });
    }
  });
}

function windGust(t) {
  return 0.55 + 0.35 * Math.sin(t * 0.5) + 0.18 * Math.sin(t * 1.7 + 1.3);
}

export function updateLeaves(dt, t, phase) {
  if (!mesh) return;
  const gust = windGust(t);
  const wx = 0.82, wz = 0.55;   // steady breeze direction
  // warm the leaves a touch toward sunset/night
  const warm = Math.max(0, phase - 0.5) / 1.5;
  mat.color.setRGB(1, 1 - 0.18 * warm, 1 - 0.35 * warm);
  for (let i = 0; i < N; i++) {
    const L = leaves[i];
    if (L.state === 1) {        // resting on the ground
      L.rest -= dt;
      if (L.rest <= 0) spawn(i, false);
      dummy.position.set(L.x, 0.018, L.z);
      dummy.rotation.set(Math.PI / 2 + L.rx * 0.1, 0, L.rz);
    } else {
      L.x += wx * gust * L.drift * dt + Math.sin(t * 1.3 + L.phase) * L.sway * dt;
      L.z += wz * gust * L.drift * dt + Math.cos(t * 1.1 + L.phase) * L.sway * dt;
      L.y -= L.vy * dt;
      L.rx += L.wx * dt; L.rz += L.wz * dt;
      if (L.y <= 0.018) {
        L.state = 1;
        L.rest = 2.5 + Math.random() * 6;
      } else if (inBuilding(L.x, L.z)) {
        spawn(i, false);          // drifted under a roof — recycle
        continue;
      }
      dummy.position.set(L.x, L.y, L.z);
      dummy.rotation.set(L.rx, 0, L.rz);
    }
    dummy.scale.setScalar(L.s);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
  }
  mesh.instanceMatrix.needsUpdate = true;
  for (const s of sway) {
    s.o.rotation.x = s.bx + Math.sin(t * s.w + s.p) * 0.022;
    s.o.rotation.z = s.bz + Math.cos(t * s.w * 0.8 + s.p) * 0.028;
  }
}
