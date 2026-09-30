"""Shared helpers for the courtyard generator (Blender 5.x, background mode)."""
import bpy
import math
import random
from mathutils import Vector

# ---------------------------------------------------------------- scene


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def get_col(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


# ---------------------------------------------------------------- materials

PALETTE = {
    "WallWhite":    ((0.898, 0.878, 0.827), 0.95, 0.0, None, 0.0),
    "WallCap":      ((0.176, 0.180, 0.196), 0.85, 0.0, None, 0.0),
    "RoofTile":     ((0.118, 0.133, 0.161), 0.62, 0.0, None, 0.0),
    "RidgeCap":     ((0.078, 0.086, 0.102), 0.55, 0.0, None, 0.0),
    "WoodDark":     ((0.219, 0.145, 0.094), 0.72, 0.0, None, 0.0),
    "WoodWarm":     ((0.478, 0.322, 0.196), 0.68, 0.0, None, 0.0),
    "StoneGray":    ((0.533, 0.525, 0.502), 0.92, 0.0, None, 0.0),
    "RockGray":     ((0.412, 0.412, 0.396), 0.95, 0.0, None, 0.0),
    "PathStone":    ((0.588, 0.576, 0.545), 0.94, 0.0, None, 0.0),
    "GroundPaving": ((0.702, 0.686, 0.639), 0.95, 0.0, None, 0.0),
    "SoilDark":     ((0.243, 0.212, 0.165), 0.98, 0.0, None, 0.0),
    "LeafPine":     ((0.157, 0.286, 0.180), 0.90, 0.0, None, 0.0),
    "LeafBamboo":   ((0.294, 0.443, 0.231), 0.90, 0.0, None, 0.0),
    "LeafGreen":    ((0.310, 0.412, 0.220), 0.90, 0.0, None, 0.0),
    "LeafFall":     ((0.556, 0.373, 0.176), 0.90, 0.0, None, 0.0),
    "TerrainEarth": ((0.352, 0.382, 0.262), 1.00, 0.0, None, 0.0),
    "PondDepth":    ((0.094, 0.145, 0.137), 0.85, 0.0, None, 0.0),
    "PondWater":    ((0.278, 0.475, 0.478), 0.15, 0.05, None, 0.0),
    "PaperWarm":    ((0.929, 0.878, 0.769), 0.90, 0.0, (1.0, 0.82, 0.55), 0.0),
    "FabricRed":    ((0.541, 0.192, 0.157), 0.80, 0.0, None, 0.0),
    "FabricIndigo": ((0.161, 0.220, 0.365), 0.85, 0.0, None, 0.0),
    "CeramicWhite": ((0.882, 0.878, 0.859), 0.25, 0.0, None, 0.0),
    "MetalBrass":   ((0.722, 0.569, 0.290), 0.35, 1.0, None, 0.0),
    "LanternGlow":  ((0.980, 0.780, 0.420), 0.60, 0.0, (1.0, 0.66, 0.30), 0.0),
    "FurCat":       ((0.522, 0.427, 0.333), 0.92, 0.0, None, 0.0),
    "FurCatLight":  ((0.870, 0.843, 0.780), 0.92, 0.0, None, 0.0),
    "KoiOrange":    ((0.898, 0.435, 0.129), 0.35, 0.0, None, 0.0),
    "KoiWhite":     ((0.929, 0.910, 0.870), 0.35, 0.0, None, 0.0),
    "KoiRed":       ((0.784, 0.204, 0.145), 0.35, 0.0, None, 0.0),
    "FrogGreen":    ((0.271, 0.435, 0.180), 0.75, 0.0, None, 0.0),
    "SparrowBrown": ((0.443, 0.341, 0.227), 0.90, 0.0, None, 0.0),
    "WingInsect":   ((0.800, 0.878, 0.929), 0.25, 0.0, None, 0.0, 0.55),
    "MossGreen":    ((0.286, 0.373, 0.204), 0.95, 0.0, None, 0.0),
}


def mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    spec = PALETTE[name]
    color, rough, metal, emit, emit_str = spec[0], spec[1], spec[2], spec[3], spec[4]
    alpha = spec[5] if len(spec) > 5 else 1.0
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_str
    if alpha < 1.0:
        try:
            bsdf.inputs["Alpha"].default_value = alpha
        except KeyError:
            pass
    return m


# ---------------------------------------------------------------- primitives


def new_obj(name, verts, faces, material, col, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    me.update()
    ob = bpy.data.objects.new(name, me)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if material is not None:
        ob.data.materials.append(material if isinstance(material, bpy.types.Material) else mat(material))
    col.objects.link(ob)
    return ob


def place(ob, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    return ob


def box(name, size, loc, material, col, rot=(0, 0, 0)):
    sx, sy, sz = size
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
         (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return place(new_obj(name, v, f, material, col), loc, rot)


def cyl(name, r, h, loc, material, col, seg=14, rot=(0, 0, 0), base=True, r_top=None):
    r_top = r if r_top is None else r_top
    z0 = 0.0 if base else -h / 2
    v, f = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        v.append((r * math.cos(a), r * math.sin(a), z0))
    for i in range(seg):
        a = 2 * math.pi * i / seg
        v.append((r_top * math.cos(a), r_top * math.sin(a), z0 + h))
    f.append(tuple(range(seg - 1, -1, -1)))
    f.append(tuple(range(seg, 2 * seg)))
    for i in range(seg):
        j = (i + 1) % seg
        f.append((i, j, seg + j, seg + i))
    return place(new_obj(name, v, f, material, col), loc, rot)


def sphere(name, r, loc, material, col, seg=12, ring=8, scale=(1, 1, 1), smooth=False):
    v, f = [], []
    for j in range(ring + 1):
        phi = math.pi * j / ring
        for i in range(seg):
            th = 2 * math.pi * i / seg
            v.append((r * math.sin(phi) * math.cos(th),
                      r * math.sin(phi) * math.sin(th),
                      r * math.cos(phi)))
    for j in range(ring):
        for i in range(seg):
            a = j * seg + i
            b = j * seg + (i + 1) % seg
            c = (j + 1) * seg + (i + 1) % seg
            d = (j + 1) * seg + i
            if j == 0:
                f.append((a, c, d))
            elif j == ring - 1:
                f.append((a, b, d))
            else:
                f.append((a, b, c, d))
    ob = new_obj(name, v, f, material, col, smooth=smooth)
    place(ob, loc, scale=scale)
    return ob


def torus(name, R, r, loc, material, col, seg=40, sides=10, rot=(0, 0, 0)):
    v, f = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        for k in range(sides):
            b = 2 * math.pi * k / sides
            rr = R + r * math.cos(b)
            v.append((rr * ca, rr * sa, r * math.sin(b)))
    for i in range(seg):
        i2 = (i + 1) % seg
        for k in range(sides):
            k2 = (k + 1) % sides
            a = i * sides + k
            b = i2 * sides + k
            c = i2 * sides + k2
            d = i * sides + k2
            f.append((a, b, c, d))
    return place(new_obj(name, v, f, material, col), loc, rot)


# ---------------------------------------------------------------- modifiers


def apply_modifier(ob, mod_name):
    with bpy.context.temp_override(object=ob, active_object=ob,
                                   selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod_name)


def boolean_diff(target, cutter):
    md = target.modifiers.new("bool", 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.solver = 'EXACT'
    md.object = cutter
    apply_modifier(target, md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def solidify(ob, thickness, offset=-1.0):
    md = ob.modifiers.new("solid", 'SOLIDIFY')
    md.thickness = thickness
    md.offset = offset
    apply_modifier(ob, md.name)


# ---------------------------------------------------------------- uv


def uv_planar_top(ob, scale=0.5):
    me = ob.data
    uvl = me.uv_layers.new(name="UVMap")
    i = 0
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[i].uv = (co.x / scale, co.y / scale)
            i += 1


# ---------------------------------------------------------------- misc


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def make_roof(name, length, span, ridge_h, eave_h, col, material="RoofTile",
              corner_lift=0.24, thick=0.07, seg_l=16, seg_s=14, axis='x',
              span_lo=None, span_hi=None):
    """Chinese-style roof: concave profile with lifted eave corners.

    Ridge runs along `axis` (length), slopes fall across `span`.
    span_lo/span_hi: centre-to-eave distance on each side of the span axis
    (default span/2); a shorter side lets one slope die into a wall (wings)."""
    lo = span / 2 if span_lo is None else span_lo
    hi = span / 2 if span_hi is None else span_hi
    verts, faces = [], []
    hl, hs = length / 2, lo + hi
    for i in range(seg_l + 1):
        u = -hl + length * i / seg_l
        un = abs(u) / hl
        for j in range(seg_s + 1):
            s = -lo + hs * j / seg_s
            t = abs(s) / (lo if s < 0 else hi)
            z = ridge_h - (ridge_h - eave_h) * (t ** 1.4)
            lift = corner_lift * (t ** 3) * (0.30 + 0.70 * smoothstep(0.45, 1.0, un))
            if axis == 'x':
                verts.append((u, s, z + lift))
            else:
                verts.append((s, u, z + lift))
    for i in range(seg_l):
        for j in range(seg_s):
            a = i * (seg_s + 1) + j
            b = (i + 1) * (seg_s + 1) + j
            c = (i + 1) * (seg_s + 1) + j + 1
            d = i * (seg_s + 1) + j + 1
            faces.append((a, b, c, d) if axis == 'x' else (a, d, c, b))
    ob = new_obj(name, verts, faces, mat(material), col)
    solidify(ob, thick, offset=-1.0)
    uv_planar_top(ob, scale=0.55)
    return ob


def make_roof_tiles(name, length, span, ridge_h, eave_h, col, corner_lift=0.24,
                    axis='x', span_lo=None, span_hi=None, tile_w=0.24,
                    course=0.32, crown=0.042, base=0.010, arc_seg=4):
    """Pan-tile field (筒瓦) laid just above the make_roof surface.

    Half-round tile courses run down-slope in columns across the ridge
    direction; course seams are staggered column to column. One mesh per
    roof, named *_RoofTiles so the roof-hide filters catch it."""
    lo = span / 2 if span_lo is None else span_lo
    hi = span / 2 if span_hi is None else span_hi
    hl = length / 2
    nc = max(3, round(length / tile_w))
    wu = length / nc
    verts, faces = [], []

    def zsurf(u, s):
        t = abs(s) / (lo if s < 0 else hi)
        z = ridge_h - (ridge_h - eave_h) * (t ** 1.4)
        lift = corner_lift * (t ** 3) * (0.30 + 0.70 * smoothstep(0.45, 1.0, abs(u) / hl))
        return z + lift

    def emit_course(c, s0, s1, cap_lo, cap_hi):
        u0 = -hl + c * wu
        i0 = len(verts)
        for s in (s0, s1):
            for k in range(arc_seg + 1):
                u = u0 + wu * k / arc_seg
                z = zsurf(u, s) + base + crown * math.sin(math.pi * k / arc_seg)
                verts.append((u, s, z) if axis == 'x' else (s, u, z))
        b0 = i0 + arc_seg + 1
        for k in range(arc_seg):
            if axis == 'x':
                faces.append((i0 + k, i0 + k + 1, b0 + k + 1, b0 + k))
            else:
                faces.append((i0 + k, b0 + k, b0 + k + 1, i0 + k + 1))
        a2, a1, a0 = i0 + 2, i0 + 1, i0
        c2, c1, c0 = b0 + 2, b0 + 1, b0
        if axis == 'x':
            if cap_lo:
                faces.append((a2, a0, a1))    # s0 end cap, normal -s
            if cap_hi:
                faces.append((c2, c1, c0))    # s1 end cap, normal +s
        else:
            if cap_lo:
                faces.append((a2, a1, a0))    # s0 end cap, normal -s
            if cap_hi:
                faces.append((c2, c0, c1))    # s1 end cap, normal +s

    for c in range(nc):
        off = (c % 2) * (course / 2)
        n = max(1, int(math.ceil((lo + hi - off) / course - 1e-6)))
        sb = [-lo + off + k * course for k in range(n + 1)]
        sb = [max(-lo, min(hi, v)) for v in sb]
        sb[0], sb[-1] = -lo, hi
        for k in range(len(sb) - 1):
            if sb[k + 1] - sb[k] > 1e-4:
                emit_course(c, sb[k], sb[k + 1], k == 0, k == len(sb) - 2)
    ob = new_obj(name, verts, faces, mat("RoofTile"), col)
    uv_planar_top(ob, scale=0.55)
    return ob


def ridge_cap(name, length, ridge_h, col, loc=(0, 0, 0), axis='x'):
    parts = []
    if axis == 'x':
        parts.append(box(name + "_Cap", (length + 0.30, 0.40, 0.16), (loc[0], loc[1], ridge_h + 0.06), "RidgeCap", col))
        for sgn in (-1, 1):
            fin = box(f"{name}_Fin{sgn:+d}", (0.20, 0.38, 0.34),
                      (loc[0] + sgn * (length / 2 + 0.02), loc[1], ridge_h + 0.16), "RidgeCap", col)
            fin.rotation_euler = (0, sgn * 0.18, 0)
            parts.append(fin)
    else:
        parts.append(box(name + "_Cap", (0.40, length + 0.30, 0.16), (loc[0], loc[1], ridge_h + 0.06), "RidgeCap", col))
        for sgn in (-1, 1):
            fin = box(f"{name}_Fin{sgn:+d}", (0.38, 0.20, 0.34),
                      (loc[0], loc[1] + sgn * (length / 2 + 0.02), ridge_h + 0.16), "RidgeCap", col)
            fin.rotation_euler = (sgn * 0.18, 0, 0)
            parts.append(fin)
    return parts
