import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { glowTexture } from './textures.js';

// Blender plan coords (x, y, z) map to Three (x, z, -y)
const P = (x, y, z) => new THREE.Vector3(x, z, -y);

const POND = { x: 3.1, z: -0.5, rx: 1.3, rz: 0.82, y: 0.065 };

const life = {
  ready: false,
  koi: [], frogs: [], dragonflies: [], sparrows: [],
  cat: null, fireflies: [],
};

const rand = (a, b) => a + Math.random() * (b - a);

/* ------------------------------------------------------------------ koi */

function spawnKoi(scene, proto) {
  const colors = [0xe86f21, 0xe05a1e, 0xf0a030, 0xe9dcc4, 0xd94a2a];
  for (let i = 0; i < 5; i++) {
    const k = proto.clone();
    k.scale.setScalar(rand(0.85, 1.18));
    const a = rand(0, Math.PI * 2);
    const r = rand(0.1, 0.75);
    // y 0.04: back and tail fin break the water surface (plane y=0.055)
    k.position.set(POND.x + Math.cos(a) * r, 0.04, POND.z + Math.sin(a) * r * 0.6);
    scene.add(k);
    const parts = {};
    k.traverse((o) => {
      if (o.name === 'Koi_Tail') parts.tail = o;
      if (o.name === 'Koi_FinL') parts.finL = o;
      if (o.name === 'Koi_FinR') parts.finR = o;
      if (o.isMesh && o.material && o.material.name === 'KoiOrange') parts.body = o;
    });
    if (parts.body) {
      const m = parts.body.material.clone();
      m.color = new THREE.Color(colors[i % colors.length]);
      parts.body.material = m;
    }
    life.koi.push({
      root: k, parts,
      heading: rand(0, Math.PI * 2), speed: rand(0.14, 0.26),
      turn: rand(-0.3, 0.3), phase: rand(0, 9),
      turnTimer: rand(2, 6),
    });
  }
}

function updateKoi(dt, t) {
  for (const k of life.koi) {
    // slow wandering with gentle wall steering
    k.turnTimer -= dt;
    if (k.turnTimer <= 0) {
      k.turn = rand(-0.5, 0.5);
      k.turnTimer = rand(2.5, 6);
    }
    const dx = k.root.position.x - POND.x;
    const dz = k.root.position.z - POND.z;
    const e = (dx / POND.rx) ** 2 + (dz / POND.rz) ** 2;
    if (e > 0.72) {
      // steer back toward the pond centre
      const toC = Math.atan2(-dz, -dx);
      let d = toC - k.heading;
      d = Math.atan2(Math.sin(d), Math.cos(d));
      k.heading += d * Math.min(1, dt * 1.2);
    } else {
      k.heading += k.turn * dt;
      k.heading += Math.sin(t * 0.35 + k.phase) * 0.04 * dt;
    }
    k.root.position.x += Math.sin(k.heading) * k.speed * dt;
    k.root.position.z += Math.cos(k.heading) * k.speed * dt;
    const dir = new THREE.Vector3(Math.sin(k.heading), 0, Math.cos(k.heading));
    k.root.lookAt(k.root.position.clone().add(dir));
    k.root.rotateY(Math.sin(t * 1.8 + k.phase) * 0.08);      // gentle body sway
    if (k.parts.tail) k.parts.tail.rotation.y = Math.sin(t * 4.2 + k.phase) * 0.38;
    if (k.parts.finL) k.parts.finL.rotation.x = Math.sin(t * 2.1 + k.phase) * 0.15;
    if (k.parts.finR) k.parts.finR.rotation.x = Math.sin(t * 2.1 + k.phase + 1) * 0.15;
  }
}

/* ------------------------------------------------------------------ frogs */

function spawnFrogs(scene, proto) {
  // frog 0 on open paving by the pond, frog 1 perched on the rockery top (in-place hops)
  const spots = [P(1.1, -0.3, 0.02), P(4.4, 1.42, 0.8)];
  const rots = [2.4, 0.6];
  const maxHop = [0.35, 0.05];
  for (let i = 0; i < 2; i++) {
    const f = proto.clone();
    f.position.copy(spots[i]);
    f.rotation.y = rots[i];
    f.scale.setScalar(rand(0.9, 1.1));
    scene.add(f);
    const parts = {};
    f.traverse((o) => {
      if (o.name === 'Frog_Head') parts.head = o;
      if (o.name === 'Frog_Body') parts.body = o;
    });
    life.frogs.push({ root: f, parts, hopTimer: rand(6, 14), hopT: -1, from: new THREE.Vector3(), to: new THREE.Vector3(), maxHop: maxHop[i] });
  }
}

function updateFrogs(dt, t) {
  for (const f of life.frogs) {
    if (f.hopT >= 0) {
      f.hopT += dt;
      const k = Math.min(1, f.hopT / 0.5);
      f.root.position.lerpVectors(f.from, f.to, k);
      f.root.position.y = f.from.y + Math.sin(k * Math.PI) * 0.14;
      if (k >= 1) f.hopT = -1;
      continue;
    }
    // idle throat bob
    if (f.parts.head) f.parts.head.scale.y = 1 + 0.05 * Math.sin(t * 2.2 + f.hopTimer);
    f.hopTimer -= dt;
    if (f.hopTimer <= 0) {
      f.hopTimer = rand(9, 20);
      f.hopT = 0;
      f.from.copy(f.root.position);
      let a = f.root.rotation.y + rand(-1.1, 1.1);
      const dist = rand(f.maxHop * 0.3, f.maxHop);
      let to = f.from.clone().add(new THREE.Vector3(Math.sin(a) * dist, 0, Math.cos(a) * dist));
      // never hop into the pond
      const ex = (to.x - POND.x) / (POND.rx + 0.15);
      const ez = (to.z - POND.z) / (POND.rz + 0.15);
      if (ex * ex + ez * ez < 1) {
        a += Math.PI;
        to = f.from.clone().add(new THREE.Vector3(Math.sin(a) * dist, 0, Math.cos(a) * dist));
      }
      f.to.copy(to);
      f.root.rotation.y = a;
      if (f.parts.head) f.parts.head.scale.y = 1;
    }
  }
}

/* ------------------------------------------------------------------ dragonflies */

function spawnDragonflies(scene, proto) {
  const bases = [P(3.6, 0.9, 0.45), P(2.6, -0.1, 0.62)];
  for (let i = 0; i < 2; i++) {
    const d = proto.clone();
    d.scale.setScalar(0.9);
    d.position.copy(bases[i]);
    scene.add(d);
    const parts = [];
    d.traverse((o) => { if (o.name.startsWith('Dragonfly_Wing')) parts.push(o); });
    life.dragonflies.push({
      root: d, parts, base: bases[i], phase: rand(0, 9),
      a: rand(0.45, 0.65), b: rand(0.3, 0.5), fa: rand(0.5, 0.8), fb: rand(0.4, 0.7),
      dartT: rand(4, 9), dart: null,
    });
  }
}

function updateDragonflies(dt, t) {
  for (const d of life.dragonflies) {
    let p;
    if (d.dart) {
      d.dart.t += dt;
      const k = Math.min(1, d.dart.t / 0.38);
      p = d.dart.from.clone().lerp(d.dart.to, k);
      p.y = d.dart.from.y + Math.sin(k * Math.PI) * 0.1;
      if (k >= 1) d.dart = null;
    } else {
      p = new THREE.Vector3(
        d.base.x + Math.sin(t * d.fa + d.phase) * d.a,
        d.base.y + Math.sin(t * 0.7 + d.phase) * 0.12,
        d.base.z + Math.sin(t * d.fb + d.phase * 1.7) * d.b,
      );
      d.dartT -= dt;
      if (d.dartT <= 0) {
        d.dartT = rand(6, 13);
        const a = rand(0, Math.PI * 2);
        d.dart = {
          t: 0,
          from: d.root.position.clone(),
          to: p.clone().add(new THREE.Vector3(Math.sin(a) * rand(0.4, 0.7), 0, Math.cos(a) * rand(0.4, 0.7))),
        };
      }
    }
    const vel = p.clone().sub(d.root.position);
    if (vel.lengthSq() > 1e-7) d.root.lookAt(p.clone().add(vel));
    d.root.position.copy(p);
    const flap = Math.sin(t * 26 + d.phase) * 0.35;
    for (let i = 0; i < d.parts.length; i++) {
      const s = i < 2 ? -1 : 1;   // wings 0,1 = left (tip -X); 2,3 = right (tip +X)
      d.parts[i].rotation.z = s * (0.15 + flap);
    }
  }
}

/* ------------------------------------------------------------------ cat */

const CAT_SPOTS = [P(-2.8, -1.6, 0.02), P(1.8, -1.9, 0.02), P(-0.6, 0.9, 0.02), P(0.9, 1.6, 0.02), P(-2.3, 1.1, 0.02)];

function spawnCat(scene, proto) {
  const c = proto.clone();
  c.scale.setScalar(1.0);
  c.position.copy(CAT_SPOTS[0]);
  c.rotation.y = rand(0, Math.PI * 2);
  scene.add(c);
  const parts = {};
  c.traverse((o) => {
    if (o.name === 'Cat_HeadPivot') parts.head = o;
    if (o.name === 'Cat_Tail1') parts.t1 = o;
    if (o.name === 'Cat_Tail2') parts.t2 = o;
    if (o.name === 'Cat_Tail3') parts.t3 = o;
  });
  if (!parts.head) c.traverse((o) => { if (o.name === 'Cat_Head') parts.head = o; });
  life.cat = { root: c, parts, state: 'sit', timer: rand(6, 14), spot: 0, walkFrom: new THREE.Vector3(), walkTo: new THREE.Vector3() };
}

function updateCat(dt, t) {
  const c = life.cat;
  if (!c) return;
  // tail sway, always
  const s = Math.sin(t * 1.1);
  if (c.parts.t1) c.parts.t1.rotation.x = 0.9 + s * 0.12;
  if (c.parts.t2) c.parts.t2.rotation.x = 1.15 + Math.sin(t * 1.1 - 0.7) * 0.16;
  if (c.parts.t3) c.parts.t3.rotation.x = 1.45 + Math.sin(t * 1.1 - 1.4) * 0.2;

  if (c.state === 'sit') {
    c.timer -= dt;
    // occasional head glance
    if (c.parts.head) c.parts.head.rotation.y = Math.sin(t * 0.5 + c.spot) * 0.28;
    if (c.timer <= 0) {
      c.state = 'walk';
      c.spot = (c.spot + 1 + Math.floor(rand(0, 3))) % CAT_SPOTS.length;
      c.walkFrom.copy(c.root.position);
      c.walkTo.copy(CAT_SPOTS[c.spot]);
      c.timer = 0;
    }
  } else {
    c.timer += dt;
    const speed = 0.38;
    const total = c.walkFrom.distanceTo(c.walkTo);
    const need = total / speed;
    const k = Math.min(1, c.timer / need);
    c.root.position.lerpVectors(c.walkFrom, c.walkTo, k);
    c.root.position.y = c.walkFrom.y + Math.abs(Math.sin(c.timer * 7)) * 0.012;   // subtle gait bob
    const dir = c.walkTo.clone().sub(c.walkFrom);
    if (dir.lengthSq() > 1e-6) {
      const targetY = Math.atan2(dir.x, dir.z);
      let dY = targetY - c.root.rotation.y;
      dY = Math.atan2(Math.sin(dY), Math.cos(dY));
      c.root.rotation.y += dY * Math.min(1, dt * 4);
    }
    if (c.parts.head) c.parts.head.rotation.y = 0;
    if (k >= 1) {
      c.state = 'sit';
      c.timer = rand(9, 22);
    }
  }
}

/* ------------------------------------------------------------------ sparrows */

function spawnSparrows(scene, proto) {
  const spots = [P(-1.5, -2.2, 0.01), P(-0.9, -2.6, 0.01), P(4.6, -5.0, 0.01), P(-4.6, -0.5, 0.01)];
  for (const s of spots) {
    const b = proto.clone();
    b.scale.setScalar(rand(0.85, 1.05));
    b.position.copy(s);
    b.rotation.y = rand(0, Math.PI * 2);
    scene.add(b);
    const parts = {};
    b.traverse((o) => {
      if (o.name === 'Sparrow_HeadPivot') parts.head = o;
      if (o.name === 'Sparrow_Wing0') parts.w0 = o;
      if (o.name === 'Sparrow_Wing1') parts.w1 = o;
    });
    if (!parts.head) b.traverse((o) => { if (o.name === 'Sparrow_Head') parts.head = o; });
    life.sparrows.push({
      root: b, parts, hopTimer: rand(0.5, 3), hopT: -1,
      flyTimer: rand(10, 25), fly: null, home: s.clone(),
    });
  }
}

function updateSparrows(dt, t) {
  for (const sp of life.sparrows) {
    if (sp.fly) {
      sp.fly.t += dt;
      const k = Math.min(1, sp.fly.t / 0.9);
      sp.root.position.lerpVectors(sp.fly.from, sp.fly.to, k);
      sp.root.position.y = sp.fly.from.y + Math.sin(k * Math.PI) * 0.5;
      const flap = Math.sin(t * 22) * 0.55;
      if (sp.parts.w0) sp.parts.w0.rotation.z = -flap;
      if (sp.parts.w1) sp.parts.w1.rotation.z = flap;
      const dir = sp.fly.to.clone().sub(sp.fly.from);
      if (dir.lengthSq() > 1e-6) {
        const targetY = Math.atan2(dir.x, dir.z);
        let dY = targetY - sp.root.rotation.y;
        dY = Math.atan2(Math.sin(dY), Math.cos(dY));
        sp.root.rotation.y += dY * Math.min(1, dt * 6);
      }
      if (k >= 1) { sp.fly = null; if (sp.parts.w0) sp.parts.w0.rotation.z = 0; if (sp.parts.w1) sp.parts.w1.rotation.z = 0; }
      continue;
    }
    if (sp.hopT >= 0) {
      sp.hopT += dt;
      const k = Math.min(1, sp.hopT / 0.22);
      sp.root.position.lerpVectors(sp.hopFrom, sp.hopTo, k);
      sp.root.position.y = sp.hopFrom.y + Math.sin(k * Math.PI) * 0.07;
      if (k >= 1) sp.hopT = -1;
    } else {
      sp.hopTimer -= dt;
      if (sp.hopTimer <= 0) {
        sp.hopTimer = rand(1.2, 4);
        sp.hopT = 0;
        sp.hopFrom = sp.root.position.clone();
        const a = sp.root.rotation.y + rand(-1.4, 1.4);
        sp.hopTo = sp.hopFrom.clone().add(new THREE.Vector3(Math.sin(a) * 0.09, 0, Math.cos(a) * 0.09));
        sp.hopTo.y = sp.hopFrom.y;
        sp.root.rotation.y = a;
      }
      // occasional peck
      if (sp.parts.head) {
        sp.parts.head.rotation.x = Math.sin(t * 1.7 + sp.home.x) > 0.93 ? 0.5 : 0;
      }
      sp.flyTimer -= dt;
      if (sp.flyTimer <= 0) {
        sp.flyTimer = rand(12, 26);
        sp.fly = { t: 0, from: sp.root.position.clone() };
        const a = rand(0, Math.PI * 2);
        const dist = rand(0.8, 1.6);
        sp.fly.to = sp.fly.from.clone().add(new THREE.Vector3(Math.sin(a) * dist, 0, Math.cos(a) * dist));
        sp.fly.to.y = sp.home.y;
      }
    }
  }
}

/* ------------------------------------------------------------------ fireflies */

function spawnFireflies(scene) {
  const map = glowTexture('rgba(214,255,150,1)', 'rgba(214,255,150,0)');
  for (let i = 0; i < 34; i++) {
    // keep to the open courtyard; skip the gatehouse and moon-gate wall volumes
    let bx, by, tries = 0;
    do {
      bx = rand(-4.9, 4.9); by = rand(-5.9, 1.6); tries++;
    } while (tries < 10 && ((bx > -1.1 && bx < 4.1 && by < -3.2) || (bx > 3.55 && by > -3.9 && by < -3.3)));
    const m = new THREE.SpriteMaterial({
      map, color: Math.random() > 0.5 ? 0xd6ff96 : 0xffe98a,
      transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const s = new THREE.Sprite(m);
    const base = P(bx, by, rand(0.25, 1.6));
    s.position.copy(base);
    s.scale.setScalar(rand(0.05, 0.1));
    scene.add(s);
    life.fireflies.push({
      s, base, r: rand(0.3, 0.9), w: rand(0.15, 0.4), phase: rand(0, 9),
      blinkRate: rand(0.8, 2.2), h: base.y,
    });
  }
}

function updateFireflies(t, phase) {
  // fireflies fade in as full night approaches (phase: 0 day, 1 sunset, 2 night)
  const vis = Math.min(1, Math.max(0, (phase - 1.55) / 0.45));
  for (const f of life.fireflies) {
    f.s.position.set(
      f.base.x + Math.sin(t * f.w + f.phase) * f.r,
      f.h + Math.sin(t * 0.9 + f.phase * 2) * 0.18,
      f.base.z + Math.cos(t * f.w * 0.8 + f.phase) * f.r,
    );
    const pulse = Math.max(0, Math.sin(t * f.blinkRate + f.phase * 3));
    f.s.material.opacity = vis * (0.12 + 0.8 * pulse * pulse);
  }
}

/* ------------------------------------------------------------------ api */

export async function loadCritters(scene) {
  const loader = new GLTFLoader();
  const protos = {};
  for (const name of ['koi', 'frog', 'dragonfly', 'cat', 'sparrow']) {
    const g = await loader.loadAsync(`./models/critter_${name}.glb`);
    protos[name] = g.scene;
    protos[name].traverse((o) => { if (o.isMesh) o.castShadow = true; });
  }
  spawnKoi(scene, protos.koi);
  spawnFrogs(scene, protos.frog);
  spawnDragonflies(scene, protos.dragonfly);
  spawnCat(scene, protos.cat);
  spawnSparrows(scene, protos.sparrow);
  spawnFireflies(scene);
  life.ready = true;
}

export function updateLife(dt, t, nightT) {
  if (!life.ready) return;
  updateKoi(dt, t);
  updateFrogs(dt, t);
  updateDragonflies(dt, t);
  updateCat(dt, t);
  updateSparrows(dt, t);
  updateFireflies(t, nightT);
}
