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
    C.sphere(f"{name}_Body", 0.09, (0, 0, 0), "KoiOrange", col, seg=10, ring=7,
             scale=(0.55, 1.55, 0.72), smooth=True)
    _fin(f"{name}_Tail", col, "KoiOrange", 0.13, 0.055, (0, 0.135, 0.005), rot=(math.pi, 0, 0))
    _fin(f"{name}_FinL", col, "KoiOrange", 0.06, 0.03, (-0.045, -0.03, -0.02), rot=(0, 0.9, 0))
    _fin(f"{name}_FinR", col, "KoiOrange", 0.06, 0.03, (0.045, -0.03, -0.02), rot=(0, -0.9, 0))
    _fin(f"{name}_Dorsal", col, "KoiOrange", 0.05, 0.028, (0, 0.01, 0.055), rot=(-1.1, 0, 0))
    C.sphere(f"{name}_EyeL", 0.011, (-0.032, -0.095, 0.02), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_EyeR", 0.011, (0.032, -0.095, 0.02), "WoodDark", col, seg=6, ring=4)


def build_frog(col):
    name = "Frog"
    C.sphere(f"{name}_Body", 0.055, (0, 0, 0.028), "FrogGreen", col, seg=10, ring=7,
             scale=(1.0, 1.15, 0.72), smooth=True)
    C.sphere(f"{name}_Head", 0.038, (0, -0.045, 0.052), "FrogGreen", col, seg=9, ring=6,
             scale=(1.0, 0.9, 0.8), smooth=True)
    C.sphere(f"{name}_EyeL", 0.016, (-0.022, -0.062, 0.075), "FrogGreen", col, seg=7, ring=5)
    C.sphere(f"{name}_EyeR", 0.016, (0.022, -0.062, 0.075), "FrogGreen", col, seg=7, ring=5)
    C.sphere(f"{name}_PupilL", 0.007, (-0.022, -0.072, 0.078), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_PupilR", 0.007, (0.022, -0.072, 0.078), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_HaunchL", 0.028, (-0.045, 0.045, 0.03), "FrogGreen", col, seg=7, ring=5, scale=(0.8, 1.2, 0.9))
    C.sphere(f"{name}_HaunchR", 0.028, (0.045, 0.045, 0.03), "FrogGreen", col, seg=7, ring=5, scale=(0.8, 1.2, 0.9))
    C.sphere(f"{name}_FootL", 0.02, (-0.05, -0.02, 0.008), "FrogGreen", col, seg=6, ring=4, scale=(0.6, 1.6, 0.5))
    C.sphere(f"{name}_FootR", 0.02, (0.05, -0.02, 0.008), "FrogGreen", col, seg=6, ring=4, scale=(0.6, 1.6, 0.5))


def build_dragonfly(col):
    name = "Dragonfly"
    C.cyl(f"{name}_Body", 0.008, 0.055, (0, 0, 0), "SparrowBrown", col, seg=7, base=False,
          rot=(math.pi / 2, 0, 0))
    C.cyl(f"{name}_Tail", 0.005, 0.06, (0, 0.055, 0), "SparrowBrown", col, seg=6,
          rot=(math.pi / 2, 0, 0))
    C.sphere(f"{name}_Head", 0.012, (0, -0.03, 0), "SparrowBrown", col, seg=7, ring=5)
    C.sphere(f"{name}_EyeL", 0.008, (-0.008, -0.036, 0.002), "WoodDark", col, seg=6, ring=4)
    C.sphere(f"{name}_EyeR", 0.008, (0.008, -0.036, 0.002), "WoodDark", col, seg=6, ring=4)
    for i, (sx, dy) in enumerate([(-1, -0.012), (-1, 0.012), (1, -0.012), (1, 0.012)]):
        w = C.box(f"{name}_Wing{i}", (0.075, 0.028, 0.002), (0, 0, 0), "WingInsect", col)
        for v in w.data.vertices:
            v.co.x += sx * 0.0375
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
    C.cyl(f"{name}_Beak", 0.006, 0.018, (0, -0.028, -0.007), "WoodDark", col, seg=6, rot=(math.pi / 2, 0, 0))
    grp = [o for o in col.objects if o.name not in before]
    pivot = bpy.data.objects.new(f"{name}_HeadPivot", None)
    pivot.empty_display_size = 0.03
    col.objects.link(pivot)
    pivot.location = (0, -0.042, 0.075)
    for p in grp:
        p.parent = pivot
    C.box(f"{name}_Tail", (0.016, 0.05, 0.004), (0, 0.062, 0.048), "SparrowBrown", col, rot=(0.45, 0, 0))
    for i, sx in enumerate((-1, 1)):
        w = C.box(f"{name}_Wing{i}", (0.03, 0.05, 0.004), (0, 0, 0), "SparrowBrown", col)
        for v in w.data.vertices:
            v.co.x += sx * 0.015
        w.data.update()
        C.place(w, (sx * 0.026, 0, 0.062))
    C.cyl(f"{name}_LegL", 0.0035, 0.03, (-0.012, -0.005, 0.008), "WoodWarm", col, seg=5)
    C.cyl(f"{name}_LegR", 0.0035, 0.03, (0.012, -0.005, 0.008), "WoodWarm", col, seg=5)


def build(col):
    build_koi(col)
    build_frog(col)
    build_dragonfly(col)
    build_cat(col)
    build_sparrow(col)
