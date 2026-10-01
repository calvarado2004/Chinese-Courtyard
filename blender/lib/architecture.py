"""Architecture: halls, wings, gatehouse, enclosure walls, moon-gate wall."""
import bpy
import math
from . import common as C


def place_group(parts, loc, rot, name, col):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0.1
    col.objects.link(empty)
    for p in parts:
        p.parent = empty
    empty.location = loc
    empty.rotation_euler = rot
    return empty


def lattice_window(name, w, h, col, loc, rot=(0, 0, 0), cols=4, rows=5, paper=True, paper_side=1):
    """Wood-framed lattice window. paper_side: +1/-1 local Y for the paper backing."""
    parts = []
    t, depth = 0.06, 0.045
    parts.append(C.box(f"{name}_frameB", (w, depth, t), (0, 0, -h / 2 + t / 2), "WoodDark", col))
    parts.append(C.box(f"{name}_frameT", (w, depth, t), (0, 0, h / 2 - t / 2), "WoodDark", col))
    parts.append(C.box(f"{name}_frameL", (t, depth, h), (-w / 2 + t / 2, 0, 0), "WoodDark", col))
    parts.append(C.box(f"{name}_frameR", (t, depth, h), (w / 2 - t / 2, 0, 0), "WoodDark", col))
    for i in range(1, cols):
        x = -w / 2 + w * i / cols
        parts.append(C.box(f"{name}_muntV{i}", (0.032, depth * 0.7, h - 2 * t), (x, 0, 0), "WoodDark", col))
    for j in range(1, rows):
        z = -h / 2 + h * j / rows
        parts.append(C.box(f"{name}_muntH{j}", (w - 2 * t, depth * 0.7, 0.032), (0, 0, z), "WoodDark", col))
    if paper:
        parts.append(C.box(f"{name}_paper", (w - 0.02, 0.012, h - 0.02), (0, paper_side * depth, 0), "PaperWarm", col))
    return place_group(parts, loc, rot, name, col)


def _wall_skirt(name, col, w, d, x, y, z0, h=0.95):
    """Grey brick base course (下碱), a hair proud of the white wall."""
    C.box(name, (w + 0.012, d + 0.012, h), (x, y, z0 + h / 2), "WallBrick", col)


def _gable_pane(name, col, roof_axis, plane_c, center, a0, a1,
                plinth, wall_h, ridge, eave_h, lift, un, span_lo, span_hi):
    """Gable wall whose top edge follows the roof's concave profile, so the
    pane meets the roof skin with no crescent gap (a straight triangle leaves
    a curved sliver of daylight under a t^1.4 roof)."""
    lo = span_lo if span_lo is not None else span_hi
    hi = span_hi if span_hi is not None else span_hi
    top = plinth + wall_h
    n = 9
    verts = []

    def pt(s, z):
        return (plane_c, center + s, z) if roof_axis == 'x' else (center + s, plane_c, z)

    verts.append(pt(a0, top))
    verts.append(pt(a1, top))
    for k in range(n, -1, -1):   # top edge from a1 back to a0, through the ridge
        s = a0 + (a1 - a0) * k / n
        t = abs(s) / (lo if s < 0 else hi)
        z = ridge - (ridge - eave_h) * (t ** 1.4) + lift * (t ** 3) * (0.30 + 0.70 * C.smoothstep(0.45, 1.0, un))
        verts.append(pt(s, z))
    faces = [(0, k, k + 1) for k in range(1, len(verts) - 1)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(C.mat("WallWhite"))
    col.objects.link(ob)
    C.solidify(ob, 0.14, offset=0.0)
    C.uv_box(ob)


def make_building(name, col, cx, cy, w, d, wall_h=2.55, ridge_h=5.3, bays=3,
                  plinth=0.35, overhang=0.55, door_bay=None, windows=True,
                  side_door=None, door_w=1.5, door_h=2.1, roof_axis='x', roof_lift=0.24,
                  steps=True, rear_door=False):
    """Courtyard building: stone plinth, wood columns, white infill walls,
    lattice windows, curved roof with lifted eave corners.

    Front (-Y) may hold a door (door_bay). side_door=-1/+1 puts a door and
    two windows on the courtyard-facing gable wall (wings)."""
    hw, hd = w / 2, d / 2
    wall_t = 0.14
    # plinth + steps
    C.box(f"{name}_plinth", (w + 0.36, d + 0.36, plinth), (cx, cy, plinth / 2), "StoneGray", col)
    if steps:
        for k in range(3):
            h = plinth * (3 - k) / 3
            y = cy - hd - 0.16 - 0.30 * (k + 0.5)
            C.box(f"{name}_step{k}", (2.1, 0.30, h), (cx, y, h / 2), "StoneGray", col)

    xs = [cx - hw + w * i / bays for i in range(bays + 1)]
    for row_y in (cy - hd + 0.16, cy + hd - 0.16):
        for i, x in enumerate(xs):
            C.cyl(f"{name}_col{row_y:.1f}_{i}", 0.11, wall_h - 0.05, (x, row_y, plinth), "WoodDark", col)

    def wall_segment(tag, x0, x1, wy, z0, z1, material="WallWhite"):
        C.box(f"{name}_{tag}", (x1 - x0, wall_t, z1 - z0),
              ((x0 + x1) / 2, wy, plinth + (z0 + z1) / 2), material, col)

    for side in (-1, 1):
        wy = cy + side * (hd - wall_t / 2)
        for i in range(bays):
            x0, x1 = xs[i] + 0.14, xs[i + 1] - 0.14
            bw = x1 - x0
            is_front = side == -1 and door_bay is not None and i == door_bay
            is_rear = side == 1 and rear_door and door_bay is not None and i == door_bay
            if is_front or is_rear:
                seg = bw - door_w
                if seg > 0.05:
                    wall_segment(f"wA{side}_{i}", x0, x0 + seg / 2, wy, 0, wall_h)
                    wall_segment(f"wB{side}_{i}", x1 - seg / 2, x1, wy, 0, wall_h)
                    _wall_skirt(f"{name}_skirtA{side}_{i}", col, seg / 2, wall_t,
                                (x0 + x0 + seg / 2) / 2, wy, plinth)
                    _wall_skirt(f"{name}_skirtB{side}_{i}", col, seg / 2, wall_t,
                                (x1 - seg / 2 + x1) / 2, wy, plinth)
                C.box(f"{name}_lintel{side}_{i}", (door_w + 0.1, wall_t, wall_h - door_h),
                      ((x0 + x1) / 2, wy, plinth + door_h + (wall_h - door_h) / 2), "WoodDark", col)
                leaf_y = wy - side * 0.10
                for sgn in (-1, 1):
                    C.box(f"{name}_door{side}{sgn}", (door_w / 2 - 0.03, 0.05, door_h - 0.06),
                          (cx + sgn * (door_w / 2 + 0.02), leaf_y, plinth + (door_h - 0.06) / 2),
                          "WoodDark", col)
                if is_rear:
                    C.box(f"{name}_rearstep", (2.1, 0.30, plinth), (cx, cy + hd + 0.15, plinth / 2), "StoneGray", col)
            elif side == -1 and windows and door_bay is not None:
                skirt_h, win_h = 0.42, 1.55
                wall_segment(f"skirt{side}_{i}", x0, x1, wy, 0, skirt_h, material="WallBrick")
                wall_segment(f"top{side}_{i}", x0, x1, wy, skirt_h + win_h, wall_h)
                lattice_window(f"{name}_win{side}_{i}", bw - 0.1, win_h, col,
                               ((x0 + x1) / 2, wy, plinth + skirt_h + win_h / 2))
            else:
                wall_segment(f"w{side}_{i}", x0, x1, wy, 0, wall_h)
                _wall_skirt(f"{name}_bskirt{side}_{i}", col, x1 - x0, wall_t,
                            (x0 + x1) / 2, wy, plinth)

    # roof geometry (also used by the gable panes so profiles match exactly)
    L = d + 2 * overhang if roof_axis == 'y' else w
    S = w + 2 * overhang if roof_axis == 'y' else d + 2 * overhang
    span_lo = span_hi = None
    if roof_axis == 'y' and side_door is not None:
        if side_door < 0:
            span_lo, span_hi = w / 2, S / 2
        else:
            span_lo, span_hi = S / 2, w / 2
    eave_h = plinth + wall_h + 0.15
    ridge = plinth + ridge_h

    # gable-end walls; wings get a door + windows on the courtyard side
    for side in (-1, 1):
        sx = cx + side * (hw - wall_t / 2)
        if side_door is not None and side == side_door:
            segs = [(-hd + 0.15, -hd + 0.75), (-hd + 0.75, -0.75), (-0.75, 0.75),
                    (0.75, hd - 0.75), (hd - 0.75, hd - 0.15)]
            kinds = ["wall", "win", "door", "win", "wall"]
            for (a, b), kind in zip(segs, kinds):
                yc = cy + (a + b) / 2
                length = b - a
                if kind == "wall":
                    C.box(f"{name}_gwall{a:.1f}", (wall_t, length, wall_h), (sx, yc, plinth + wall_h / 2), "WallWhite", col)
                    _wall_skirt(f"{name}_gbskirt{a:.1f}", col, wall_t, length, sx, yc, plinth)
                elif kind == "door":
                    C.box(f"{name}_gdoorT", (wall_t, length, wall_h - door_h), (sx, yc, plinth + door_h + (wall_h - door_h) / 2), "WallWhite", col)
                    for sgn in (-1, 1):
                        C.box(f"{name}_gdoor{sgn}", (0.05, door_w / 2 - 0.03, door_h - 0.06),
                              (sx + side * 0.12, yc + sgn * (door_w / 2 + 0.02), plinth + (door_h - 0.06) / 2),
                              "WoodDark", col)
                else:
                    skirt_h, win_h = 0.42, 1.55
                    C.box(f"{name}_gskirt{a:.1f}", (wall_t, length, skirt_h), (sx, yc, plinth + skirt_h / 2), "WallBrick", col)
                    C.box(f"{name}_gtop{a:.1f}", (wall_t, length, wall_h - skirt_h - win_h), (sx, yc, plinth + skirt_h + win_h + (wall_h - skirt_h - win_h) / 2), "WallWhite", col)
                    lattice_window(f"{name}_gwin{a:.1f}", length - 0.06, win_h, col,
                                   (sx, yc, plinth + skirt_h + win_h / 2), rot=(0, 0, math.pi / 2),
                                   paper_side=side)
        else:
            C.box(f"{name}_sidewall{side}", (wall_t, d - 0.34, wall_h), (sx, cy, plinth + wall_h / 2), "WallWhite", col)
            _wall_skirt(f"{name}_sskirt{side}", col, wall_t, d - 0.34, sx, cy, plinth)
        # gable infill follows the roof profile — a straight triangle leaves a
        # crescent gap under the concave t^1.4 roof curve
        if roof_axis == 'x':
            _gable_pane(f"{name}_gable{side}", col, 'x', sx, cy,
                        -(hd - 0.2), hd - 0.2, plinth, wall_h, ridge, eave_h,
                        roof_lift, abs(sx - cx) / (L / 2), S / 2, S / 2)
            _wall_skirt(f"{name}_panskirt{side}", col, wall_t, 2 * (hd - 0.2),
                        sx, cy, plinth)
        else:
            ey = cy + side * (hd - wall_t / 2)
            _gable_pane(f"{name}_gable{side}", col, 'y', ey, cx,
                        -(hw - 0.2), hw - 0.2, plinth, wall_h, ridge, eave_h,
                        roof_lift, abs(ey - cy) / (L / 2), span_lo, span_hi)
            _wall_skirt(f"{name}_panskirt{side}", col, 2 * (hw - 0.2), wall_t,
                        cx, ey, plinth)

    # roof + ridge; tiles are a separate corrugated field just above the surface
    # x-ridge roofs end flush with the gable walls (硬山) so the hall cannot
    # overrun the wings; wings pull the courtyard-side eave flush to the hall wall
    roof = C.make_roof(f"{name}_Roof", L, S, ridge, eave_h, col, corner_lift=roof_lift,
                       axis=roof_axis, span_lo=span_lo, span_hi=span_hi)
    tiles = C.make_roof_tiles(f"{name}_RoofTiles", L, S, ridge, eave_h, col,
                              corner_lift=roof_lift, axis=roof_axis,
                              span_lo=span_lo, span_hi=span_hi)
    roof.location = (cx, cy, 0)
    tiles.location = (cx, cy, 0)
    C.ridge_cap(f"{name}_ridge", L, ridge, col, loc=(cx, cy, 0), axis=roof_axis)
    for side in (-1, 1):
        if roof_axis == 'y':
            dist = (span_lo if side < 0 else span_hi) or S / 2
            C.box(f"{name}_fascia{side}", (0.07, L + 0.1, 0.13),
                  (cx + side * (dist - 0.035), cy, eave_h - 0.07), "RidgeCap", col)
        else:
            C.box(f"{name}_fascia{side}", (L + 0.1, 0.07, 0.13),
                  (cx, cy + side * (S / 2 - 0.035), eave_h - 0.07), "RidgeCap", col)


def enclosure_wall(col):
    W, D, T, H = 18.0, 13.5, 0.4, 2.6
    DH = 2.3  # entry opening height, aligned with the gatehouse door
    segs = [("N", (0, D / 2 - T / 2), (W, T), None),
            ("W", (-W / 2 + T / 2, 0), (T, D - 2 * T), None),
            ("E", (W / 2 - T / 2, 0), (T, D - 2 * T), None)]
    for tag, (x, y), (sx, sy), _ in segs:
        C.box(f"WallPerim{tag}", (sx, sy, H), (x, y, H / 2), "WallWhite", col)
        C.box(f"WallPerim{tag}Cap", (sx + 0.12, sy + 0.12, 0.09), (x, y, H + 0.045), "WallCap", col)
        _wall_skirt(f"WallPerim{tag}Skirt", col, sx, sy, x, y, 0.0)
    # south wall with a 1.9 m entry gap aligned to the gatehouse door (x 0.55..2.45)
    y = -D / 2 + T / 2
    parts = [((-W / 2, 0.55), "S1"), ((2.45, W / 2), "S2")]
    for (a, b), tag in parts:
        C.box(f"WallPerim{tag}", (b - a, T, H), ((a + b) / 2, y, H / 2), "WallWhite", col)
        C.box(f"WallPerim{tag}Cap", (b - a + 0.12, T + 0.12, 0.09), ((a + b) / 2, y, H + 0.045), "WallCap", col)
        _wall_skirt(f"WallPerim{tag}Skirt", col, b - a, T, (a + b) / 2, y, 0.0)
    C.box("WallPerimSHeader", (1.9, T, H - DH), (1.5, y, DH + (H - DH) / 2), "WallWhite", col)
    C.box("WallPerimSHeaderCap", (1.9 + 0.12, T + 0.12, 0.09), (1.5, y, H + 0.045), "WallCap", col)


def moon_gate_wall(col):
    """Garden wall running E-W at y=-3.6, gate aligned to frame the pond."""
    x0, x1 = 3.85, 8.8
    y = -3.6
    gx = 5.0
    T, H, R = 0.28, 2.1, 0.72
    wall = C.box("WallMoon", (x1 - x0, T, H), ((x0 + x1) / 2, y, H / 2), "WallWhite", col)
    cutter = C.cyl("moonCutter", R, T + 0.4, (gx, y, R), None, col, seg=40, rot=(math.pi / 2, 0, 0), base=False)
    C.boolean_diff(wall, cutter)
    # trim band proud of both wall faces around the opening
    C.torus("MoonTrim", R + 0.06, 0.17, (gx, y, R), "WallCap", col, rot=(math.pi / 2, 0, 0))
    C.box("WallMoonCap", (x1 - x0 + 0.1, T + 0.14, 0.08), ((x0 + x1) / 2, y, H + 0.04), "WallCap", col)
    # brick skirt stops clear of the moon-gate opening
    _wall_skirt("WallMoonSkirtL", col, (gx - R - 0.08) - x0, T, (x0 + gx - R - 0.08) / 2, y, 0.0)
    _wall_skirt("WallMoonSkirtR", col, x1 - (gx + R + 0.08), T, (gx + R + 0.08 + x1) / 2, y, 0.0)
    lattice_window("MoonWallWin", 0.78, 0.78, col, (7.3, y, 1.35), cols=3, rows=3, paper=False)


def gatehouse(col):
    make_building("Gate", col, cx=1.5, cy=-4.85, w=4.6, d=3.0, wall_h=2.7, ridge_h=4.0,
                  bays=1, plinth=0.18, overhang=0.5, door_bay=0, windows=False,
                  door_w=1.9, door_h=2.3, roof_lift=0.20, steps=False, rear_door=True)


def build(col):
    enclosure_wall(col)
    make_building("MainHall", col, cx=0.0, cy=4.15, w=10.0, d=4.4, wall_h=2.85, ridge_h=5.5,
                  bays=3, door_bay=1, windows=True, door_w=1.7, door_h=2.2)
    make_building("EastWing", col, cx=6.8, cy=0.0, w=3.6, d=6.4, wall_h=2.55, ridge_h=4.9,
                  bays=2, windows=False, side_door=-1, roof_axis='y', roof_lift=0.22,
                  steps=False)
    make_building("WestWing", col, cx=-6.8, cy=0.0, w=3.6, d=6.4, wall_h=2.55, ridge_h=4.9,
                  bays=2, windows=False, side_door=1, roof_axis='y', roof_lift=0.22,
                  steps=False)
    gatehouse(col)
    moon_gate_wall(col)
    ground = C.box("Ground", (18.0, 13.5, 0.04), (0, 0, -0.02), "GroundPaving", col)
    C.uv_planar_top(ground, scale=1.1)
