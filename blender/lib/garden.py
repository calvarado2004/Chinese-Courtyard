"""Garden: pond, rockery, pines, bamboo, stone lanterns, paths, plantings."""
import math
import random
from . import common as C


def blob_outline(cx, cy, rx, ry, n=26, jitter=0.14, seed=3):
    rng = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        w = 1.0 + rng.uniform(-jitter, jitter)
        pts.append((cx + rx * w * math.cos(a), cy + ry * w * math.sin(a)))
    return pts


def mesh_from_outline(name, pts, z_top, z_bot, col, material, cap_top=True, cap_bottom=True):
    """Closed prism from a 2D outline (pond basin, ground beds)."""
    n = len(pts)
    verts, faces = [], []
    for (x, y) in pts:
        verts.append((x, y, z_top))
    for (x, y) in pts:
        verts.append((x, y, z_bot))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    if cap_top:
        faces.append(tuple(range(n - 1, -1, -1)))
    if cap_bottom:
        faces.append(tuple(range(n, 2 * n)))
    return C.new_obj(name, verts, faces, material, col)


def make_pond(col, cx, cy, rx, ry, seed=7):
    pts = blob_outline(cx, cy, rx, ry, seed=seed)
    basin = mesh_from_outline("PondBasin", pts, 0.02, -0.55, col, "PondDepth")
    C.uv_planar_top(basin, scale=0.8)
    water_pts = [(cx + (x - cx) * 0.96, cy + (y - cy) * 0.96) for (x, y) in pts]
    water = mesh_from_outline("PondWater", water_pts, 0.055, 0.03, col, "PondWater")
    C.uv_planar_top(water, scale=0.8)
    # stone rim
    rng = random.Random(seed + 1)
    for i in range(0, len(pts), 2):
        x, y = pts[i]
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1.0
        r = rng.uniform(0.10, 0.17)
        s = C.sphere(f"PondRim{i}", r, (x + dx / d * 0.06, y + dy / d * 0.06, -0.03),
                     rng.choice(["RockGray", "PathStone"]), col, seg=7, ring=5,
                     scale=(rng.uniform(0.8, 1.5), rng.uniform(0.8, 1.5), rng.uniform(0.5, 0.8)))
        s.rotation_euler = (0, 0, rng.uniform(0, math.pi))
    return water


def make_rockery(col, cx, cy, seed=11, scale=1.0, z0=0.0):
    rng = random.Random(seed)
    stones = [
        (0.00, 0.00, 0.55, 0.42),
        (0.42, 0.18, 0.40, 0.34),
        (-0.36, 0.22, 0.34, 0.30),
        (0.12, -0.30, 0.30, 0.26),
        (-0.20, -0.24, 0.24, 0.20),
        (0.55, -0.12, 0.22, 0.18),
    ]
    for i, (dx, dy, h, r) in enumerate(stones):
        x, y = cx + dx * scale, cy + dy * scale
        s = C.sphere(f"Rockery{i}", r * scale, (x, y, z0 + h * scale * 0.42), "RockGray", col,
                     seg=8, ring=6,
                     scale=(rng.uniform(0.75, 1.2), rng.uniform(0.75, 1.2), rng.uniform(0.9, 1.5)))
        s.rotation_euler = (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(0, math.pi))
    # small moss patches at the foot
    for i in range(3):
        C.cyl(f"RockeryMoss{i}", rng.uniform(0.10, 0.16), 0.02,
              (cx + rng.uniform(-0.7, 0.7) * scale, cy + rng.uniform(-0.45, 0.45) * scale, z0),
              "MossGreen", col, seg=8)


def make_pine(col, cx, cy, h=3.2, seed=5, z0=0.0):
    """Pine: wandering tapered trunk, root flare, radial branches with
    clustered foliage clumps — an irregular crown instead of blob pads."""
    rng = random.Random(seed)
    tag = f"{cx:.1f}_{cy:.1f}"
    r0 = 0.11 * (0.75 + h / 6.0)
    # trunk: three tapered segments with a slight wander
    x, y, z = cx, cy, z0
    r = r0
    total = h * 0.72
    for s in range(3):
        seg_h = total / 3 * rng.uniform(0.85, 1.15)
        tilt, lean = rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06)
        C.cyl(f"PineTrunk{s}_{tag}", r, seg_h, (x, y, z), "WoodDark", col,
              seg=8, r_top=r * 0.72, rot=(tilt, lean, 0))
        x += math.tan(lean) * seg_h
        y += math.tan(tilt) * seg_h
        z += seg_h
        r *= 0.72
    C.cyl(f"PineRoot{tag}", r0 * 1.9, 0.12, (cx, cy, z0), "WoodDark", col, seg=8, r_top=r0)
    # branches radiating from the crown, foliage clumps at their tips
    crown = z
    zones = []
    for b in range(rng.randint(4, 6)):
        a = 2 * math.pi * b / 5 + rng.uniform(-0.35, 0.35)
        bl = rng.uniform(0.55, 1.05) * (0.75 + h / 8.0)
        bx, by = x + math.cos(a) * bl, y + math.sin(a) * bl
        bz = crown - rng.uniform(0.05, 0.22)
        C.cyl(f"PineBranch{b}_{tag}", 0.05, math.hypot(bx - x, by - y),
              ((x + bx) / 2, (y + by) / 2, (crown + bz) / 2), "WoodDark", col,
              seg=6, r_top=0.018, rot=(math.pi / 2, 0, a + math.pi / 2))
        zones.append((bx, by, bz, 0.40))
        zones.append(((x + bx) / 2, (y + by) / 2, (crown + bz) / 2 + 0.06, 0.30))
    zones.append((x, y, crown + 0.22, 0.48))
    zones.append((x + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3), crown + 0.02, 0.36))
    for i, (px, py, pz, pr) in enumerate(zones):
        for k in range(rng.randint(2, 3)):
            s = C.sphere(f"PinePad{i}_{k}_{tag}", pr * rng.uniform(0.72, 1.0),
                         (px + rng.uniform(-0.16, 0.16), py + rng.uniform(-0.16, 0.16),
                          pz + rng.uniform(-0.08, 0.08)),
                         "LeafPine", col, seg=9, ring=6,
                         scale=(1.0, rng.uniform(0.85, 1.05), 0.55), smooth=True)
            s.rotation_euler = (0, 0, rng.uniform(0, math.pi))


def make_bush(col, cx, cy, s=1.0, seed=5, z0=0.0):
    """Shrub: cluster of smooth leaf blobs over a couple of twigs."""
    rng = random.Random(seed)
    tag = f"{cx:.1f}_{cy:.1f}"
    for i in range(rng.randint(3, 5)):
        r = rng.uniform(0.22, 0.40) * s
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.22 * s)
        m = "LeafGreen" if rng.random() < 0.7 else "MossGreen"
        sph = C.sphere(f"Bush{i}_{tag}", r,
                       (cx + math.cos(a) * d, cy + math.sin(a) * d, z0 + r * 0.7), m, col,
                       seg=9, ring=6,
                       scale=(rng.uniform(0.9, 1.25), rng.uniform(0.9, 1.25), rng.uniform(0.65, 0.9)),
                       smooth=True)
        sph.rotation_euler = (0, 0, rng.uniform(0, math.pi))
    for i in range(2):
        a = rng.uniform(0, 2 * math.pi)
        C.cyl(f"BushTwig{i}_{tag}", 0.015, rng.uniform(0.2, 0.35) * s,
              (cx + math.cos(a) * 0.1, cy + math.sin(a) * 0.1, z0), "WoodDark", col,
              seg=5, rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0))


def _merged_sphere(verts, faces, cx, cy, cz, r, squash=0.6, seg=8, ring=5, rng=None):
    """Append an irregular smooth sphere to a verts/faces pair (merged foliage)."""
    i0 = len(verts)
    js = rng.uniform(0.85, 1.15) if rng else 1.0
    ks = rng.uniform(0.85, 1.15) if rng else 1.0
    for j in range(ring + 1):
        phi = math.pi * j / ring
        for i in range(seg):
            th = 2 * math.pi * i / seg
            verts.append((cx + r * js * math.sin(phi) * math.cos(th),
                          cy + r * ks * math.sin(phi) * math.sin(th),
                          cz + r * squash * math.cos(phi)))
    for j in range(ring):
        for i in range(seg):
            a = i0 + j * seg + i
            b = i0 + j * seg + (i + 1) % seg
            c = i0 + (j + 1) * seg + (i + 1) % seg
            d = i0 + (j + 1) * seg + i
            if j == 0:
                faces.append((a, c, d))
            elif j == ring - 1:
                faces.append((a, b, d))
            else:
                faces.append((a, b, c, d))


def make_pine_far(col, cx, cy, h, seed, z0=0.0):
    """Distant pine: single tapered trunk + one merged irregular crown mesh."""
    rng = random.Random(seed)
    tag = f"{cx:.0f}_{cy:.0f}"
    r0 = 0.09 * (0.8 + h / 6.0)
    lean, tilt = rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08)
    C.cyl(f"PineTrunkF{tag}", r0, h * 0.68, (cx, cy, z0), "WoodDark", col,
          seg=6, r_top=r0 * 0.5, rot=(tilt, lean, 0))
    tx, ty = cx + math.tan(lean) * h * 0.68, cy + math.tan(tilt) * h * 0.68
    verts, faces = [], []
    n = rng.randint(5, 7)
    for k in range(n):
        r = rng.uniform(0.45, 0.85) * (0.8 + h / 8.0)
        a = 2 * math.pi * k / n + rng.uniform(-0.5, 0.5)
        d = rng.uniform(0.15, 0.75)
        _merged_sphere(verts, faces,
                       tx + math.cos(a) * d, ty + math.sin(a) * d,
                       z0 + h * 0.62 + (k / n) * h * 0.34 + rng.uniform(-0.1, 0.1),
                       r * rng.uniform(0.8, 1.0), rng=rng)
    ob = C.new_obj(f"PineCrownF{tag}", verts, faces, "LeafPine", col, smooth=True)
    return ob


def make_bush_far(col, cx, cy, s, seed, z0=0.0):
    """Distant shrub: one merged blob cluster (single object)."""
    rng = random.Random(seed)
    verts, faces = [], []
    m = "LeafGreen" if rng.random() < 0.7 else "MossGreen"
    for i in range(rng.randint(3, 5)):
        r = rng.uniform(0.22, 0.40) * s
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.22 * s)
        _merged_sphere(verts, faces, cx + math.cos(a) * d, cy + math.sin(a) * d,
                       z0 + r * 0.7, r, squash=rng.uniform(0.65, 0.9), rng=rng)
    if verts:
        C.new_obj(f"BushF{cx:.0f}_{cy:.0f}", verts, faces, m, col, smooth=True)


def make_stump(col, cx, cy, seed, z0=0.0):
    rng = random.Random(seed)
    r = rng.uniform(0.10, 0.16)
    C.cyl(f"Stump{cx:.0f}_{cy:.0f}", r, rng.uniform(0.18, 0.32), (cx, cy, z0),
          "WoodDark", col, seg=8, r_top=r * 0.92)
    C.cyl(f"StumpTop{cx:.0f}_{cy:.0f}", r * 0.9, 0.02, (cx, cy, z0 + 0.30),
          "WoodWarm", col, seg=8)


def make_bamboo_clump(col, cx, cy, n=7, seed=9):
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.35)
        h = rng.uniform(2.1, 3.3)
        tilt = rng.uniform(-0.09, 0.09)
        lean = rng.uniform(-0.09, 0.09)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        C.cyl(f"Bamboo{i}_{cx:.1f}_{cy:.1f}", 0.022, h, (x, y, 0), "LeafBamboo", col,
              seg=6, r_top=0.016, rot=(tilt, lean, 0))
        tx, ty = x + math.tan(lean) * h, y + math.tan(tilt) * h
        for k in range(3):
            s = C.sphere(f"BambooLeaf{i}_{k}_{cx:.1f}", 0.22,
                         (tx + rng.uniform(-0.25, 0.25), ty + rng.uniform(-0.25, 0.25),
                          h - k * 0.38 - 0.15), "LeafBamboo", col, seg=7, ring=5,
                         scale=(1.4, 0.55, 0.35))
            s.rotation_euler = (rng.uniform(-0.4, 0.4), 0, rng.uniform(0, math.pi))


def make_lantern(col, cx, cy, h=1.05):
    tag = f"{cx:.1f}_{cy:.1f}"
    C.box(f"LanternBase{tag}", (0.42, 0.42, 0.10), (cx, cy, 0.05), "StoneGray", col)
    C.cyl(f"LanternPost{tag}", 0.055, h * 0.55, (cx, cy, 0.10), "StoneGray", col, seg=8)
    z0 = 0.10 + h * 0.55
    # light chamber: glowing box with corner posts so the glow shows on all faces
    C.box(f"LanternLight{tag}", (0.20, 0.20, 0.20), (cx, cy, z0 + 0.10), "LanternGlow", col)
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.box(f"LanternCorner{tag}_{sx}{sy}", (0.045, 0.045, 0.24),
                  (cx + sx * 0.10, cy + sy * 0.10, z0 + 0.10), "StoneGray", col)
    C.box(f"LanternCap{tag}", (0.36, 0.36, 0.05), (cx, cy, z0 + 0.245), "StoneGray", col)
    C.cyl(f"LanternKnob{tag}", 0.045, 0.09, (cx, cy, z0 + 0.295), "StoneGray", col, seg=6)


_PATH_SEQ = [0]


def make_path(col, pts, width=0.5, seed=13, thick=0.045, z0=0.0, zfn=None):
    """Stepping stones along a polyline; zfn(x, y) lets stones follow terrain."""
    rng = random.Random(seed)
    pid = _PATH_SEQ[0]
    _PATH_SEQ[0] += 1
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist / 0.62))
        for k in range(n + 1):
            t = k / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if i > 0 and k == 0:
                continue
            zb = (zfn(x, y) - 0.02) if zfn else z0
            C.box(f"Path{pid}_{i}_{k}", (width * rng.uniform(0.85, 1.15), width * rng.uniform(0.85, 1.15), thick),
                  (x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.05, 0.05), zb + thick / 2),
                  "PathStone", col, rot=(0, 0, rng.uniform(-0.2, 0.2)))


def make_planting_strip(col, x0, y0, x1, y1, seed=17):
    """Dark soil strip with moss blobs along a wall."""
    rng = random.Random(seed)
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(length / 0.8))
    ang = math.atan2(y1 - y0, x1 - x0)
    for i in range(n):
        t = (i + 0.5) / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        w = rng.uniform(0.5, 0.7)
        bed = C.box(f"Bed{i}_{x:.1f}_{y:.1f}", (0.8, w, 0.05), (x, y, 0.025), "SoilDark", col, rot=(0, 0, ang))
        C.uv_planar_top(bed, scale=1.0)
        for k in range(rng.randint(2, 4)):
            r = rng.uniform(0.08, 0.16)
            s = C.sphere(f"Shrub{i}_{k}_{x:.1f}", r,
                         (x + rng.uniform(-0.3, 0.3), y + rng.uniform(-w / 3, w / 3), r * 0.55),
                         "LeafGreen", col, seg=8, ring=5, scale=(1.1, 1.0, 0.7))
            s.rotation_euler = (0, 0, rng.uniform(0, math.pi))


def terrain_z(x, y):
    """Height of the landscape plane at (x, y) — shared by terrain + props."""
    relief = (-0.05 + 0.02 * math.sin(x * 0.32) * math.sin(y * 0.27)
              + 0.012 * math.sin(x * 0.9 + y * 0.6))
    m = max(abs(x) - 9.6, abs(y) - 7.35, 0.0)
    k = min(1.0, m / 1.5)
    return relief * k + (-0.07) * (1 - k)


def make_terrain(col, size=(88.0, 66.0), seg=(44, 33)):
    """Landscape plane around the compound with gentle rolling relief.

    Dips to a flat apron just under the compound slab so nothing pokes
    through the courtyard paving."""
    rx, ry = size[0] / 2, size[1] / 2
    nx, ny = seg
    verts, faces = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -rx + size[0] * i / nx
            y = -ry + size[1] * j / ny
            verts.append((x, y, terrain_z(x, y)))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            b = a + 1
            c = a + nx + 2
            d = a + nx + 1
            faces.append((a, b, c, d))
    ob = C.new_obj("Terrain1", verts, faces, "TerrainEarth", col)
    C.uv_planar_top(ob, scale=2.0)
    return ob


def make_grass(col, cx, cy, r, tufts, seed, material="LeafGreen", hmax=0.20, z0=0.0):
    """Patch of grass tufts merged into one mesh (two tri-blades per blade)."""
    rng = random.Random(seed)
    verts, faces = [], []
    for _ in range(tufts):
        tx = cx + rng.uniform(-r, r)
        ty = cy + rng.uniform(-r, r)
        for _ in range(rng.randint(5, 8)):
            a = rng.uniform(0, 2 * math.pi)
            d = rng.uniform(0, 0.10)
            bx, by = tx + math.cos(a) * d, ty + math.sin(a) * d
            h = rng.uniform(0.09, hmax)
            lean = rng.uniform(0.05, 0.30) * h
            la = rng.uniform(0, 2 * math.pi)
            w = rng.uniform(0.012, 0.020)
            i0 = len(verts)
            verts.append((bx - math.sin(la) * w, by + math.cos(la) * w, z0))
            verts.append((bx + math.sin(la) * w, by - math.cos(la) * w, z0))
            verts.append((bx + math.cos(la) * lean * 0.6, by + math.sin(la) * lean * 0.6, z0 + h))
            faces.append((i0, i0 + 1, i0 + 2))
            faces.append((i0 + 2, i0 + 1, i0))
    if verts:
        C.new_obj(f"Grass{cx:.1f}_{cy:.1f}", verts, faces, material, col)


def make_leaf_litter(col, cx, cy, r, n, seed, material="LeafFall"):
    """Flat fallen-leaf scatter on the ground (one merged mesh)."""
    rng = random.Random(seed)
    verts, faces = [], []
    for _ in range(n):
        x = cx + rng.uniform(-r, r)
        y = cy + rng.uniform(-r, r)
        s = rng.uniform(0.05, 0.09)
        a = rng.uniform(0, math.pi)
        ca, sa = math.cos(a) * s / 2, math.sin(a) * s / 2
        z = 0.008
        i0 = len(verts)
        verts.append((x - ca, y - sa, z))
        verts.append((x + sa, y + ca, z))
        verts.append((x + ca * 1.7, y + sa * 1.7, z))
        verts.append((x - sa * 1.7, y - ca * 1.7, z))
        faces.append((i0, i0 + 1, i0 + 2, i0 + 3))
        faces.append((i0 + 3, i0 + 2, i0 + 1, i0))
    if verts:
        C.new_obj(f"Litter{cx:.1f}_{cy:.1f}", verts, faces, material, col)


def make_stream(col):
    """Thin arcing ribbon of water from the spout stone into the pond."""
    p0 = (4.66, 0.94, 0.30)
    p1 = (4.30, 0.82, 0.06)
    n, width = 8, 0.065
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dl = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / dl, dx / dl
    verts, faces = [], []
    for i in range(n + 1):
        t = i / n
        x = p0[0] + dx * t
        y = p0[1] + dy * t
        z = p0[2] + (p1[2] - p0[2]) * t - 0.045 * math.sin(math.pi * t)
        mx, my = x - nx * width / 2, y - ny * width / 2
        px, py = x + nx * width / 2, y + ny * width / 2
        verts.append((mx, my, z))
        verts.append((px, py, z))
    for i in range(n):
        a = i * 2
        b = i * 2 + 1
        c = (i + 1) * 2 + 1
        d = (i + 1) * 2
        faces.append((a, b, c, d))
        faces.append((d, c, b, a))
    C.new_obj("Stream1", verts, faces, "PondWater", col)


def build(col):
    # pond in the SE part of the main courtyard
    make_pond(col, 3.1, 0.5, 1.65, 1.2, seed=7)
    make_rockery(col, 4.35, 1.35, seed=11, scale=0.95)
    # small spout stone feeding the pond from the rockery side
    C.box("SpoutStone", (0.5, 0.24, 0.18), (4.7, 0.95, 0.34), "PathStone", col, rot=(0, -0.18, 0.35))

    # pines (kept clear of porches, walls and roof edges)
    make_pine(col, -3.5, 0.3, h=3.0, seed=5)
    make_pine(col, 7.35, -5.1, h=2.6, seed=21)
    make_pine(col, -7.4, -5.3, h=2.9, seed=31)
    # bamboo clumps (kept off building footprints)
    make_bamboo_clump(col, -4.35, -2.95, n=8, seed=9)
    make_bamboo_clump(col, 6.6, 4.6, n=6, seed=14)
    make_bamboo_clump(col, -1.6, -5.4, n=5, seed=22)
    # stone lanterns
    make_lantern(col, 1.55, -1.5)
    make_lantern(col, 4.75, -0.85, h=0.9)
    make_lantern(col, -1.9, 2.7)
    # paths — main axis runs gatehouse → main hall; branches fork off it
    make_path(col, [(1.5, -3.05), (1.5, -1.9), (1.45, -0.75), (1.5, 0.45), (1.35, 1.42)],
              width=0.6, seed=36)
    make_path(col, [(1.5, -2.55), (0.9, -1.6), (0.85, -0.5), (0.85, 0.85)], width=0.5, seed=13)
    make_path(col, [(1.5, -2.7), (0.2, -3.0), (-1.2, -2.85), (-2.6, -2.9), (-3.6, -2.6)],
              width=0.45, seed=33)
    # diagonal stepping stones through the moon gate toward the pond
    make_path(col, [(5.6, -4.8), (5.2, -4.15), (5.0, -3.6), (4.6, -2.8), (4.2, -1.7), (3.85, -0.7)],
              width=0.45, seed=27)
    # plantings along walls (inside the wall face)
    make_planting_strip(col, -8.0, -5.65, -3.9, -5.65, seed=17)
    make_planting_strip(col, -8.0, 5.6, -5.6, 5.6, seed=18)
    make_planting_strip(col, 5.5, 6.1, 8.0, 6.1, seed=19)
    # lily pads
    rng = random.Random(41)
    for i in range(6):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.9)
        C.cyl(f"Lily{i}", rng.uniform(0.10, 0.17), 0.015,
              (3.1 + math.cos(a) * d, 0.5 + math.sin(a) * d * 0.7, 0.065),
              "LeafGreen", col, seg=10)
    # water arc from the spout into the pond
    make_stream(col)
    # grass: wall-edge beds, courtyard corners, sparse tufts on open paving edges
    make_grass(col, -5.2, -4.6, 0.9, 26, 51)
    make_grass(col, -2.6, -5.6, 0.8, 22, 52)
    make_grass(col, -7.2, -4.2, 0.8, 20, 53, material="MossGreen")
    make_grass(col, 6.4, -6.0, 0.5, 18, 54)
    make_grass(col, 8.0, -4.6, 0.6, 16, 55, material="MossGreen")
    make_grass(col, 6.9, 5.3, 0.6, 18, 56)
    make_grass(col, -6.9, 4.9, 0.6, 16, 57, material="MossGreen")
    make_grass(col, 4.9, 3.75, 0.35, 8, 58)
    make_grass(col, -4.9, 3.75, 0.35, 8, 59)
    make_grass(col, -4.9, -3.75, 0.4, 8, 60)
    make_grass(col, 4.9, -4.15, 0.3, 6, 61)
    make_grass(col, 3.4, 2.3, 0.35, 8, 62)
    make_grass(col, -3.4, 2.3, 0.35, 8, 63)
    # fallen leaves under the pines and by the moon wall
    make_leaf_litter(col, -3.5, 0.3, 0.85, 24, 71)
    make_leaf_litter(col, 7.35, -5.1, 0.8, 22, 72)
    make_leaf_litter(col, -7.4, -5.3, 0.8, 22, 73)
    make_leaf_litter(col, 5.0, -3.3, 0.55, 10, 74)

    # ---- surrounding landscape (outside the enclosure walls) ----
    make_terrain(col)
    # jittered grid fill across the whole meadow; near ring is hand-placed below
    rngg = random.Random(150)
    for gy in (-28, -23, -18, -13, -8, -3, 2, 7, 12, 17, 22, 27):
        for gx in range(-39, 40, 5):
            x = gx + rngg.uniform(-1.6, 1.6)
            y = gy + rngg.uniform(-1.6, 1.6)
            if abs(x) < 11.0 and abs(y) < 9.0:
                continue                       # compound + near ring: hand-placed
            if -1.5 < x < 4.5 and y < -5.5:
                continue                       # south entry corridor / road
            pick = rngg.random()
            z = terrain_z(x, y) - 0.02
            if pick < 0.62:
                make_pine_far(col, x, y, rngg.uniform(2.4, 4.4), seed=200 + gx * 71 + gy, z0=z)
            elif pick < 0.86:
                make_bush_far(col, x, y, rngg.uniform(0.8, 1.5), seed=300 + gx * 53 + gy, z0=z)
            elif pick < 0.94:
                r = rngg.uniform(0.12, 0.30)
                C.sphere(f"RockeryG{gx}_{gy}", r, (x, y, z + r * 0.3), "RockGray", col,
                         seg=7, ring=5, scale=(1.15, 0.95, 0.7))
            else:
                make_stump(col, x, y, seed=400 + gx * 37 + gy, z0=z)
    # scattered pines; keep the south entry corridor (x -0.5..3.5, y < -6.75) clear
    outside_pines = [
        (-12.5, -1.5, 3.4, 61), (-11.5, 4.5, 2.8, 62), (-13.5, -5.5, 3.0, 63),
        (11.5, 3.5, 3.2, 64), (12.5, -2.5, 2.7, 65), (10.5, -6.5, 3.0, 66),
        (-7.5, 9.2, 3.1, 67), (4.5, 9.5, 2.6, 68), (11.0, 8.0, 3.3, 69),
        (-11.0, 9.0, 2.9, 70), (7.8, -9.0, 2.9, 71), (-6.2, -9.4, 2.7, 72),
        (-14.0, -8.0, 3.3, 73), (-8.5, -11.0, 2.8, 74), (-1.5, -11.0, 2.6, 75),
        (5.5, -11.5, 3.0, 76), (14.0, -4.0, 3.2, 77), (15.0, 2.0, 2.9, 78),
        (13.0, 7.5, 3.4, 79), (9.0, 11.0, 2.7, 80), (3.0, 12.0, 3.1, 81),
        (-4.0, 11.0, 2.6, 82), (-9.0, 12.0, 3.0, 83), (-14.0, 6.0, 2.8, 84),
    ]
    for x, y, h, s in outside_pines:
        make_pine(col, x, y, h=h, seed=s, z0=terrain_z(x, y) - 0.02)
    # boulder groups tucked between the trees
    for x, y, s, sc in [(-10.6, -7.6, 81, 1.2), (9.8, -7.9, 82, 1.1), (-9.8, 7.6, 83, 1.3),
                        (8.6, 7.3, 84, 1.0), (12.2, 5.6, 85, 1.25), (-12.4, 2.2, 86, 1.1),
                        (3.9, -9.1, 87, 0.9)]:
        make_rockery(col, x, y, seed=s, scale=sc, z0=terrain_z(x, y) - 0.02)
    # single weathered stones scattered across the meadow
    for i, (x, y) in enumerate([(-10.8, -8.2), (-4.8, -9.6), (7.0, -9.0), (10.6, -8.6),
                                (13.0, -2.0), (13.6, 4.0), (10.6, 7.4), (5.6, 10.8),
                                (-1.8, 10.6), (-6.4, 11.2), (-12.2, 7.6), (-13.8, -0.5)]):
        r = 0.10 + (i % 3) * 0.045
        st = C.sphere(f"RockeryScat{i}", r, (x, y, terrain_z(x, y) + r * 0.35), "RockGray", col,
                      seg=7, ring=5, scale=(1.0 + (i % 3) * 0.18, 0.9 + ((i + 1) % 3) * 0.14, 0.72))
        st.rotation_euler = (0.05 * (i % 3 - 1), 0.04 * (i % 2), 0.4 * i)
    # bushes: inside walls + across the meadow, two flanking the entry road
    for x, y, s, sc in [(-5.7, -5.2, 101, 1.1), (-6.4, 4.4, 102, 1.0), (5.5, -5.6, 103, 1.15),
                        (-7.6, 4.6, 104, 0.9)]:
        make_bush(col, x, y, s=sc, seed=s)
    for x, y, s, sc in [(-9.5, -8.5, 111, 1.2), (-5.5, -9.2, 112, 1.0), (6.0, -9.5, 113, 1.1),
                        (9.5, -9.2, 114, 1.0), (12.0, -6.5, 115, 1.2), (13.2, 0.5, 116, 1.1),
                        (11.8, 6.2, 117, 1.2), (7.5, 10.2, 118, 1.0), (1.0, 9.8, 119, 1.0),
                        (-5.0, 10.2, 120, 1.1), (-10.5, 10.5, 121, 1.0), (-13.5, 3.5, 122, 1.0),
                        (-13.0, -4.0, 123, 1.1), (5.0, -8.3, 124, 0.9), (-1.4, -7.3, 125, 0.8),
                        (4.4, -7.4, 126, 0.8)]:
        make_bush(col, x, y, s=sc, seed=s, z0=terrain_z(x, y) - 0.02)
    # the road leaving the gatehouse to the south, following the terrain
    make_path(col, [(1.5, -6.7), (1.3, -8.0), (1.6, -9.4), (1.4, -10.8), (1.6, -12.0)],
              width=0.6, seed=35, thick=0.09, zfn=terrain_z)
    # meadow grass near the trees and walls
    for x, y, r, n, s in [(-11.2, -3.2, 1.0, 24, 91), (11.0, 0.5, 1.0, 22, 92),
                          (-8.3, 7.8, 0.9, 20, 93), (6.8, 8.3, 0.9, 20, 94),
                          (-3.5, -8.6, 0.8, 16, 95), (5.9, -8.2, 0.7, 14, 96),
                          (-13.0, -6.0, 1.0, 22, 97), (-9.0, -10.2, 0.9, 18, 98),
                          (8.0, -10.6, 0.9, 18, 99), (13.5, -2.5, 1.0, 20, 100),
                          (12.5, 4.2, 0.9, 18, 105), (9.5, 9.2, 0.9, 18, 106),
                          (-2.0, 9.6, 0.9, 18, 107), (-6.0, -9.8, 0.8, 14, 108)]:
        make_grass(col, x, y, r, n, s, z0=terrain_z(x, y) - 0.015)
