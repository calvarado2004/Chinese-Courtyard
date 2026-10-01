import * as THREE from 'three';

function canvasTex(w, h, draw, repeat = true) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = repeat ? THREE.RepeatWrapping : THREE.ClampToEdgeWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

// Dark curved-tile roof: horizontal rows with staggered tile seams.
export function roofTexture() {
  return canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#262b33';
    g.fillRect(0, 0, w, h);
    const rows = 8;
    const rowH = h / rows;
    for (let r = 0; r < rows; r++) {
      const y = r * rowH;
      // subtle row shading
      g.fillStyle = `rgba(255,255,255,${0.035 + 0.02 * Math.sin(r * 1.7)})`;
      g.fillRect(0, y + 2, w, rowH - 4);
      // row seam (pan tile bottom edge)
      g.fillStyle = 'rgba(0,0,0,0.55)';
      g.fillRect(0, y + rowH - 2, w, 2);
      // vertical seams, staggered
      const cols = 8;
      const off = (r % 2) * (w / (cols * 2));
      for (let c = 0; c < cols; c++) {
        const x = ((c * w / cols + off) % w + w) % w;
        g.fillStyle = 'rgba(0,0,0,0.35)';
        g.fillRect(x, y, 2, rowH);
        g.fillStyle = 'rgba(255,255,255,0.06)';
        g.fillRect(x + 2, y, 2, rowH);
      }
    }
    // faint grain
    for (let i = 0; i < 900; i++) {
      g.fillStyle = `rgba(255,255,255,${Math.random() * 0.03})`;
      g.fillRect(Math.random() * w, Math.random() * h, 1, 1);
    }
  });
}

// Courtyard flagstone paving: 2x2 slabs per tile, bold joints, moss in the gaps.
export function pavingTexture() {
  return canvasTex(256, 256, (g, w, h) => {
    const rnd = mulberry(7);
    g.fillStyle = '#57534a';   // joint / grout colour
    g.fillRect(0, 0, w, h);
    const half = w / 2;
    for (let i = 0; i < 2; i++) {
      for (let j = 0; j < 2; j++) {
        const v = rnd() * 34;
        const x0 = i * half + 4, y0 = j * half + 4;
        const s = half - 8;
        g.fillStyle = `rgb(${146 + v},${140 + v},${124 + v})`;
        g.fillRect(x0, y0, s, s);
        // bevel: lit top edge, shaded bottom edge, chip texture
        g.fillStyle = 'rgba(255,255,255,0.13)';
        g.fillRect(x0, y0, s, 3);
        g.fillStyle = 'rgba(0,0,0,0.22)';
        g.fillRect(x0, y0 + s - 4, s, 4);
        g.fillRect(x0 + s - 4, y0, 4, s);
      }
    }
    // moss creeping into joints
    for (let i = 0; i < 70; i++) {
      const a = 0.2 + rnd() * 0.35;
      g.fillStyle = `rgba(${58 + rnd() * 26},${86 + rnd() * 30},${44 + rnd() * 18},${a})`;
      g.fillRect(rnd() * w, rnd() * h, 1 + rnd() * 3, 1 + rnd() * 2);
    }
    // grain + wear
    for (let i = 0; i < 1600; i++) {
      const a = Math.random() * 0.06;
      g.fillStyle = Math.random() > 0.5 ? `rgba(255,255,255,${a})` : `rgba(0,0,0,${a})`;
      g.fillRect(Math.random() * w, Math.random() * h, 2, 1);
    }
  });
}

// White limewash plaster: subtle mottling only (no blotches).
export function whitePlasterTexture() {
  return canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#f1ecdf';
    g.fillRect(0, 0, w, h);
    for (let i = 0; i < 700; i++) {
      const a = Math.random() * 0.05;
      g.fillStyle = Math.random() > 0.5 ? `rgba(255,255,255,${a})` : `rgba(120,112,94,${a})`;
      g.fillRect(Math.random() * w, Math.random() * h, 2, 2);
    }
    for (let i = 0; i < 350; i++) {
      g.fillStyle = `rgba(150,142,124,${Math.random() * 0.05})`;
      g.fillRect(Math.random() * w, Math.random() * h, 1, 1);
    }
  });
}

// Grey brick (青砖) courses in running bond — used for the wall base course.
// One 256px tile spans ~0.75 m (uv_box scale): courses ≈ 8 cm, bricks ≈ 19 cm.
export function brickTexture() {
  return canvasTex(256, 256, (g, w, h) => {
    const rows = 9, cols = 4;
    const bh = h / rows, bw = w / cols;
    const rngB = mulberry(5);
    const tones = [];
    for (let r = 0; r < rows; r++) {
      const row = [];
      for (let c = 0; c < cols; c++) row.push(rngB());
      tones.push(row);
    }
    g.fillStyle = '#98938a';   // mortar
    g.fillRect(0, 0, w, h);
    for (let r = 0; r < rows; r++) {
      const shift = (r % 2) * (bw / 2);
      for (let c = -1; c < cols + 1; c++) {
        const cm = ((c % cols) + cols) % cols;
        const t = tones[r][cm];
        const b = Math.round(96 + (t - 0.5) * 36);
        const x = c * bw + shift;
        g.fillStyle = `rgb(${b},${b + 4},${b + 2})`;
        g.fillRect(x + 1.6, r * bh + 1.6, bw - 3.2, bh - 3.2);
        // bevel: lit top edge, shaded bottom edge
        g.fillStyle = 'rgba(255,255,255,0.13)';
        g.fillRect(x + 1.6, r * bh + 1.6, bw - 3.2, 2);
        g.fillStyle = 'rgba(0,0,0,0.18)';
        g.fillRect(x + 1.6, (r + 1) * bh - 3.6, bw - 3.2, 2);
        // occasional darker over-fired brick
        if (t > 0.9) {
          g.fillStyle = 'rgba(44,50,50,0.4)';
          g.fillRect(x + 4, r * bh + 4, bw - 8, bh - 8);
        }
      }
    }
    // grime specks
    for (let i = 0; i < 900; i++) {
      const a = Math.random() * 0.08;
      g.fillStyle = Math.random() > 0.4 ? `rgba(28,32,32,${a})` : `rgba(255,255,255,${a})`;
      g.fillRect(Math.random() * w, Math.random() * h, 2, 1);
    }
  });
}

// Meadow/earth ground for the terrain outside the walls.
export function grassTexture() {
  return canvasTex(256, 256, (g, w, h) => {
    const rnd = mulberry(11);
    g.fillStyle = '#4f5a33';
    g.fillRect(0, 0, w, h);
    // patchy tone variation
    for (let i = 0; i < 26; i++) {
      const x = rnd() * w, y = rnd() * h, r = 12 + rnd() * 30;
      const grad = g.createRadialGradient(x, y, 0, x, y, r);
      grad.addColorStop(0, rnd() > 0.6 ? 'rgba(112,104,62,0.35)' : 'rgba(58,74,38,0.40)');
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      g.fillStyle = grad;
      g.fillRect(x - r, y - r, r * 2, r * 2);
    }
    // blades
    for (let i = 0; i < 2600; i++) {
      const x = rnd() * w, y = rnd() * h;
      const l = 2 + rnd() * 5;
      const tone = rnd();
      g.strokeStyle = tone > 0.72 ? `rgba(140,138,84,${0.25 + rnd() * 0.3})`
        : tone > 0.4 ? `rgba(88,102,52,${0.3 + rnd() * 0.3})`
        : `rgba(52,66,36,${0.3 + rnd() * 0.3})`;
      g.lineWidth = 1;
      g.beginPath();
      g.moveTo(x, y);
      g.lineTo(x + (rnd() - 0.5) * 2, y - l);
      g.stroke();
    }
  });
}

// Soft round sprite (stars, fireflies, moon glow).
export function glowTexture(inner = 'rgba(255,255,255,1)', outer = 'rgba(255,255,255,0)') {
  return canvasTex(64, 64, (g) => {
    const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, inner);
    grad.addColorStop(1, outer);
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
  }, false);
}

function mulberry(seed) {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}
