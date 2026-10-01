"""Small animals: koi, frog, dragonfly, cat, sparrow — exported as individual GLBs.

Critters face -Y in Blender, which becomes +Z (the lookAt direction) after glTF export.
Part names drive life.js: Koi_Tail, Cat_HeadPivot, Sparrow_HeadPivot, Dragonfly_Wing0..3.
"""
import math
import bpy
from . import common as C


def _fin(name, col, material, length, height, loc, rot=(0, 0, 0)):
    """Flat triangular panel in the XZ plane, pivot at origin, tip toward -Y."""
    v = [(0, 0, 0), (0, -length, height * 0.25), (0, -length * 0.85, -height)]
    f = [(0, 1, 2), (0, 2, 1)]
    ob = C.new_obj(name, v, f, material, col)
    return C.place(ob, loc, rot)


def build_koi(col):
    name = "Koi"
    # forward-heavy spindle: fat front body, tapered rear, distinct head
    C.sphere(f"{name}_Body", 0.09, (0, -0.02, 0), "KoiOrange", col, seg=12, ring=8,
             scale=(0.52, 1.05, 0.66), smooth=True)
    C.cyl(f"{name}_Rear", 0.055, 0.15, (0, 0.07, 0.0), "KoiOrange", col, seg=9,
          r_top=0.026, rot=(math.pi / 2, 0, 0), base=False)
    C.sphere(f"{name}_Head", 0.055, (0, -0.085, 0.005), "KoiOrange", col, seg=10, ring=7,
             scale=(0.74, 0.8, 0.62), smooth=True)
    # forked caudal fin: one mesh, pivot at its root (life.js swings it on Y)
    v = [(0, 0, 0), (0, 0.16, 0.055), (0, 0.105, 0.0), (0, 0.16, -0.055)]
    f = [(0, 1, 2), (0, 2, 3), (0, 3, 1)]
    tail = C.new_obj(f"{name}_Tail", v, f, "KoiOrange", col)
    C.place(tail, (0, 0.16, 0.0))
    _fin(f"{name}_FinL", col, "KoiOrange", 0.07, 0.035, (-0.05, -0.045, -0.015), rot=(0.5, 0.7, 0))
    _fin(f"{name}_FinR", col, "KoiOrange", 0.07, 0.035, (0.05, -0.045, -0.015), rot=(0.5, -0.7, 0))
    _fin(f"{name}_Dorsal", col, "KoiOrange", 0.07, 0.038, (0, 0.02, 0.05), rot=(-1.15, 0, 0))
    _fin(f"{name}_Anal", col, "KoiOrange", 0.05, 0.028, (0, 0.10, -0.028), rot=(1.0, 0, 0))
    C.sphere(f"{name}_EyeL", 0.012, (-0.037, -0.112, 0.02), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_EyeR", 0.012, (0.037, -0.112, 0.02), "WoodDark", col, seg=6, ring=4)


def build_frog(col):
    name = "Frog"
    C.sphere(f"{name}_Body", 0.055, (0, 0.005, 0.03), "FrogGreen", col, seg=10, ring=7,
             scale=(1.0, 1.15, 0.66), smooth=True)
    C.sphere(f"{name}_Head", 0.040, (0, -0.055, 0.055), "FrogGreen", col, seg=9, ring=6,
             scale=(1.05, 0.95, 0.72), smooth=True)
    C.sphere(f"{name}_EyeL", 0.017, (-0.024, -0.075, 0.084), "FrogGreen", col, seg=7, ring=5)
    C.sphere(f"{name}_EyeR", 0.017, (0.024, -0.075, 0.084), "FrogGreen", col, seg=7, ring=5)
    C.sphere(f"{name}_PupilL", 0.008, (-0.024, -0.088, 0.088), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_PupilR", 0.008, (0.024, -0.088, 0.088), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_NostrilL", 0.004, (-0.012, -0.092, 0.064), "WoodDark", col, seg=5, ring=4)
    C.sphere(f"{name}_NostrilR", 0.004, (0.012, -0.092, 0.064), "WoodDark", col, seg=5, ring=4)
    # folded hind legs: haunch -> knee -> shin -> webbed foot
    for sgn, tag in ((-1, "L"), (1, "R")):
        C.sphere(f"{name}_Haunch{tag}", 0.032, (sgn * 0.05, 0.05, 0.032), "FrogGreen", col,
                 seg=7, ring=5, scale=(0.85, 1.25, 1.0), smooth=True)
        C.cyl(f"{name}_Knee{tag}", 0.014, 0.05, (sgn * 0.052, 0.028, 0.022), "FrogGreen", col,
              seg=6, rot=(0.5, 0, 0))
        C.cyl(f"{name}_Shin{tag}", 0.010, 0.05, (sgn * 0.05, -0.005, 0.012), "FrogGreen", col,
              seg=6, rot=(1.15, 0, 0))
        C.sphere(f"{name}_Foot{tag}", 0.02, (sgn * 0.052, -0.038, 0.006), "FrogGreen", col,
                 seg=6, ring=4, scale=(0.55, 1.9, 0.4))
        # small front arms
        C.cyl(f"{name}_Arm{tag}", 0.008, 0.045, (sgn * 0.034, -0.048, 0.024), "FrogGreen", col,
              seg=5, rot=(0.25, 0, 0))
        C.sphere(f"{name}_Hand{tag}", 0.011, (sgn * 0.038, -0.056, 0.004), "FrogGreen", col,
                 seg=6, ring=4, scale=(0.8, 1.3, 0.6))


def build_dragonfly(col):
    name = "Dragonfly"
    C.cyl(f"{name}_Thorax", 0.011, 0.05, (0, -0.005, 0), "SparrowBrown", col, seg=7, base=False,
          rot=(math.pi / 2, 0, 0))
    # segmented abdomen trailing behind
    for i in range(3):
        C.cyl(f"{name}_Segment{i}", 0.006 - i * 0.0008, 0.03, (0, 0.048 + i * 0.03, 0),
              "SparrowBrown", col, seg=6, rot=(math.pi / 2, 0, 0), base=False)
    C.sphere(f"{name}_Head", 0.013, (0, -0.035, 0), "SparrowBrown", col, seg=7, ring=5)
    C.sphere(f"{name}_EyeL", 0.009, (-0.009, -0.041, 0.003), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_EyeR", 0.009, (0.009, -0.041, 0.003), "WoodDark", col, seg=6, ring=4)
    # long slim wings with rounded trailing edge (hinged at the thorax)
    for i, (sx, dy) in enumerate([(-1, -0.012), (-1, 0.012), (1, -0.012), (1, 0.012)]):
        w = C.box(f"{name}_Wing{i}", (0.095, 0.024, 0.002), (0, 0, 0), "WingInsect", col)
        for v in w.data.vertices:
            v.co.x += sx * 0.0475
            if v.co.x * sx > 0.06:
                v.co.z = 0.0
        w.data.update()
        C.place(w, (sx * 0.006, dy, 0.012))


def build_cat(col):
    name = "Cat"
    C.sphere(f"{name}_Body", 0.115, (0, 0.02, 0.115), "FurCat", col, seg=10, ring=8,
             scale=(0.72, 1.0, 0.85), smooth=True)
    C.sphere(f"{name}_Chest", 0.085, (0, -0.065, 0.105), "FurCatLight", col, seg=9, ring=7,
             scale=(0.8, 0.9, 0.9), smooth=True)
    # head group pivot at the neck so life.js can glance the whole head
    before = set(o.name for o in col.objects)
    C.sphere(f"{name}_Head", 0.062, (0, 0, 0), "FurCat", col, seg=9, ring=7, smooth=True)
    for sgn, tag in ((-1, "L"), (1, "R")):
        C.cyl(f"{name}_Ear{tag}", 0.022, 0.045, (sgn * 0.03, -0.02, 0.042), "FurCat", col,
              seg=6, r_top=0.006, rot=(0.25 * sgn, 0, 0))
    C.sphere(f"{name}_Muzzle", 0.026, (0, -0.05, -0.015), "FurCatLight", col, seg=8, ring=6,
             scale=(1.0, 0.8, 0.7), smooth=True)
    grp = [o for o in col.objects if o.name not in before]
    pivot = bpy.data.objects.new(f"{name}_HeadPivot", None)
    pivot.empty_display_size = 0.03
    col.objects.link(pivot)
    pivot.location = (0, -0.115, 0.21)
    for p in grp:
        p.parent = pivot
    C.cyl(f"{name}_LegFL", 0.02, 0.11, (-0.045, -0.075, 0.0), "FurCat", col, seg=7)
    C.cyl(f"{name}_LegFR", 0.02, 0.11, (0.045, -0.075, 0.0), "FurCat", col, seg=7)
    C.cyl(f"{name}_PawL", 0.021, 0.03, (-0.045, -0.085, 0.0), "FurCatLight", col, seg=7,
          rot=(math.pi / 2, 0, 0), base=False)
    C.cyl(f"{name}_PawR", 0.021, 0.03, (0.045, -0.085, 0.0), "FurCatLight", col, seg=7,
          rot=(math.pi / 2, 0, 0), base=False)
    C.cyl(f"{name}_LegBL", 0.021, 0.105, (-0.05, 0.085, 0.005), "FurCat", col, seg=7)
    C.cyl(f"{name}_LegBR", 0.021, 0.105, (0.05, 0.085, 0.005), "FurCat", col, seg=7)
    C.cyl(f"{name}_PawBL", 0.022, 0.03, (-0.05, 0.095, 0.005), "FurCatLight", col, seg=7,
          rot=(math.pi / 2, 0, 0), base=False)
    C.cyl(f"{name}_PawBR", 0.022, 0.03, (0.05, 0.095, 0.005), "FurCatLight", col, seg=7,
          rot=(math.pi / 2, 0, 0), base=False)
    C.cyl(f"{name}_Tail1", 0.016, 0.09, (0, 0.125, 0.06), "FurCat", col, seg=7, r_top=0.013, rot=(0.9, 0, 0))
    C.cyl(f"{name}_Tail2", 0.013, 0.08, (0, 0.164, 0.128), "FurCat", col, seg=7, r_top=0.011, rot=(1.15, 0, 0))
    C.cyl(f"{name}_Tail3", 0.011, 0.07, (0, 0.168, 0.2), "FurCat", col, seg=7, r_top=0.009, rot=(1.45, 0, 0))
    C.sphere(f"{name}_HaunchL", 0.055, (-0.062, 0.065, 0.085), "FurCat", col, seg=8, ring=6,
             scale=(0.75, 1.0, 1.0), smooth=True)
    C.sphere(f"{name}_HaunchR", 0.055, (0.062, 0.065, 0.085), "FurCat", col, seg=8, ring=6,
             scale=(0.75, 1.0, 1.0), smooth=True)


def build_sparrow(col):
    name = "Sparrow"
    C.sphere(f"{name}_Body", 0.045, (0, 0, 0.045), "SparrowBrown", col, seg=9, ring=7,
             scale=(0.8, 1.15, 0.9), smooth=True)
    C.sphere(f"{name}_Belly", 0.033, (0, -0.008, 0.03), "FurCatLight", col, seg=8, ring=6,
             scale=(0.75, 1.0, 0.8), smooth=True)
    # head pivot so life.js can peck
    before = set(o.name for o in col.objects)
    C.sphere(f"{name}_Head", 0.03, (0, 0, 0), "SparrowBrown", col, seg=8, ring=6, smooth=True)
    C.cyl(f"{name}_Beak", 0.006, 0.018, (0, -0.028, -0.007), "WoodDark", col, seg=6, rot=(math.pi / 2, 0, 0), r_top=0.002)
    C.sphere(f"{name}_EyeL", 0.006, (-0.021, -0.017, 0.011), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_EyeR", 0.006, (0.021, -0.017, 0.011), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_Cap", 0.028, (0, 0.004, 0.012), "WoodDark", col, seg=8, ring=5,
             scale=(0.95, 1.0, 0.55), smooth=True)
    grp = [o for o in col.objects if o.name not in before]
    pivot = bpy.data.objects.new(f"{name}_HeadPivot", None)
    pivot.empty_display_size = 0.03
    col.objects.link(pivot)
    pivot.location = (0, -0.042, 0.075)
    for p in grp:
        p.parent = pivot
    C.box(f"{name}_TailC", (0.016, 0.052, 0.004), (0, 0.064, 0.048), "SparrowBrown", col, rot=(0.45, 0, 0))
    for sgn in (-1, 1):
        C.box(f"{name}_TailF{sgn}", (0.007, 0.04, 0.003),
              (sgn * 0.007, 0.082, 0.036), "SparrowBrown", col, rot=(0.55, 0, sgn * 0.12))
    for i, sx in enumerate((-1, 1)):
        w = C.box(f"{name}_Wing{i}", (0.032, 0.058, 0.004), (0, 0, 0), "SparrowBrown", col)
        for v in w.data.vertices:
            v.co.x += sx * 0.016
            v.co.y -= 0.004
        w.data.update()
        C.place(w, (sx * 0.028, 0.004, 0.062), rot=(0, sx * 0.18, 0))
    C.cyl(f"{name}_LegL", 0.0035, 0.03, (-0.012, -0.005, 0.008), "WoodWarm", col, seg=5)
    C.cyl(f"{name}_LegR", 0.0035, 0.03, (0.012, -0.005, 0.008), "WoodWarm", col, seg=5)


def build(col):
    build_koi(col)
    build_frog(col)
    build_dragonfly(col)
    build_cat(col)
    build_sparrow(col)
