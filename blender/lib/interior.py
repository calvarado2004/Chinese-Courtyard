"""Interior furniture: living room (main hall), tea room (east wing), bedroom (west wing)."""
import math
import bpy
from . import common as C


def _legs(name, col, x, y, w, d, h, mat="WoodWarm", z0=0.0):
    hw, hd = w / 2 - 0.04, d / 2 - 0.04
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.box(f"{name}_leg{sx}{sy}", (0.06, 0.06, h),
                  (x + sx * hw, y + sy * hd, z0 + h / 2), mat, col)


def table(name, col, x, y, w, d, h, top_t=0.05, mat="WoodWarm", floor=0.0):
    """h = tabletop surface height (absolute). Legs span floor..h-top_t."""
    C.box(f"{name}_top", (w, d, top_t), (x, y, h - top_t / 2), mat, col)
    _legs(name, col, x, y, w, d, h - top_t - floor, mat, z0=floor)


def armchair(name, col, x, y, rot, mat="WoodWarm", floor=0.0):
    """Simplified round-back chair facing +Y, then rotated by `rot` around Z.
    Parts are relative to the floor; the group empty carries the floor height."""
    before = set(o.name for o in col.objects)
    C.box(f"{name}_seat", (0.52, 0.5, 0.07), (0, 0, 0.46), mat, col)
    C.cyl(f"{name}_back", 0.30, 0.09, (0, 0.06, 0.78), mat, col, seg=10, rot=(math.pi / 2, 0, 0), base=False)
    C.box(f"{name}_backfill", (0.5, 0.05, 0.30), (0, 0.22, 0.72), mat, col)
    _legs(name, col, 0, 0, 0.5, 0.46, 0.44, mat)
    grp = [o for o in col.objects if o.name not in before]
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0.1
    col.objects.link(empty)
    for p in grp:
        p.parent = empty
    empty.location = (x, y, floor)
    empty.rotation_euler = (0, 0, rot)
    return empty


def cushion(name, col, x, y, mat="FabricRed", floor=0.0):
    return C.sphere(name, 0.19, (x, y, floor + 0.086), mat, col, seg=10, ring=6, scale=(1.0, 1.0, 0.45))


def teaset(name, col, x, y, z=0.87):
    C.sphere(f"{name}_pot", 0.055, (x, y, z + 0.04), "CeramicWhite", col, seg=10, ring=7, scale=(1.0, 1.0, 0.72))
    C.cyl(f"{name}_spout", 0.014, 0.07, (x + 0.055, y, z + 0.06), "CeramicWhite", col, seg=6, rot=(0, math.pi / 2, 0))
    C.torus(f"{name}_handle", 0.035, 0.011, (x - 0.062, y, z + 0.04), "CeramicWhite", col, rot=(0, math.pi / 2, 0))
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.5
        C.cyl(f"{name}_cup{i}", 0.022, 0.024, (x + 0.19 * math.cos(a), y + 0.19 * math.sin(a), z),
              "CeramicWhite", col, seg=8)


def build(col):
    # ---------------- living room (main hall, floor z=0.35) ----------------
    z = 0.35
    for i, (dx, rot) in enumerate([(-1.32, 0.28), (-0.44, 0.10), (0.44, -0.10), (1.32, -0.28)]):
        C.box(f"Furn_Screen{i}f", (0.88, 0.05, 1.75), (dx, 5.82 + abs(rot), z + 0.875), "WoodDark", col, rot=(0, -rot, 0))
        C.box(f"Furn_Screen{i}p", (0.80, 0.02, 1.55), (dx, 5.82 + abs(rot) - 0.04, z + 0.875), "FabricIndigo", col, rot=(0, -rot, 0))
    table("Furn_AltarTable", col, 0, 5.35, 2.3, 0.5, z + 0.92, floor=z)
    C.cyl("Furn_VaseNeck", 0.05, 0.16, (-0.6, 5.35, z + 1.06), "CeramicWhite", col, seg=10, r_top=0.07)
    C.sphere("Furn_VaseBody", 0.10, (-0.6, 5.35, z + 1.0), "CeramicWhite", col, seg=10, ring=7, scale=(1.0, 1.0, 0.9))
    armchair("Furn_ChairL", col, -1.05, 4.55, 0.35, floor=z)
    armchair("Furn_ChairR", col, 1.05, 4.55, -0.35, floor=z)
    table("Furn_TeaTable", col, 0, 4.55, 0.85, 0.75, z + 0.72, floor=z)
    teaset("Furn_Tea", col, 0, 4.55, z=z + 0.72)
    C.box("Furn_Cabinet", (0.5, 1.6, 1.15), (4.55, 4.1, z + 0.575), "WoodWarm", col)
    C.box("Furn_CabinetDoor", (0.03, 1.5, 1.0), (4.28, 4.1, z + 0.55), "WoodDark", col)
    C.box("Furn_Mat", (2.6, 1.6, 0.03), (0, 4.6, z + 0.015), "FabricRed", col)

    # ---------------- tea room (east wing, floor z=0.35) ----------------
    tx, ty = 6.8, -0.2
    C.cyl("Furn_TeaTableTop", 0.52, 0.05, (tx, ty, z + 0.58), "WoodWarm", col, seg=14, base=False)
    _legs("Furn_TeaTable", col, tx, ty, 0.8, 0.8, 0.555, z0=z)
    teaset("Furn_TeaSet", col, tx, ty, z=z + 0.605)
    for i, (dx, dy, m) in enumerate([(-0.85, 0, "FabricRed"), (0.85, 0, "FabricIndigo"),
                                     (0, -0.85, "FabricRed"), (0, 0.85, "FabricIndigo")]):
        cushion(f"Furn_TeaCushion{i}", col, tx + dx, ty + dy, m, floor=z)
    C.box("Furn_Shelf", (1.4, 0.24, 0.04), (7.6, 2.94, z + 1.35), "WoodWarm", col)
    C.box("Furn_Shelf2", (1.4, 0.24, 0.04), (7.6, 2.94, z + 1.0), "WoodWarm", col)
    for i in range(3):
        C.cyl(f"Furn_Jar{i}", 0.055, 0.16, (7.2 + i * 0.4, 2.94, z + 1.02), "CeramicWhite", col, seg=9)
    C.box("Furn_Scroll", (0.02, 0.45, 1.15), (8.45, 0.9, z + 1.55), "PaperWarm", col)
    C.cyl("Furn_ScrollRod", 0.02, 0.5, (8.44, 0.9, z + 2.15), "WoodDark", col, seg=8, rot=(math.pi / 2, 0, 0), base=False)
    C.cyl("Furn_Pot", 0.14, 0.22, (8.2, -2.5, z), "CeramicWhite", col, seg=10)
    for i in range(4):
        a = 2 * math.pi * i / 4
        C.cyl(f"Furn_PotStem{i}", 0.012, 1.1, (8.2 + 0.05 * math.cos(a), -2.5 + 0.05 * math.sin(a), z + 0.2),
              "LeafBamboo", col, seg=5, r_top=0.009, rot=(0.04 * (i - 1.5), 0.03 * (i - 1), 0))
        for k in range(2):
            C.sphere(f"Furn_PotLeaf{i}_{k}", 0.10, (8.2 + 0.05 * math.cos(a) + (k - 0.5) * 0.1,
                     -2.5 + 0.05 * math.sin(a) + (k - 0.5) * 0.08, z + 1.15 - k * 0.25),
                     "LeafBamboo", col, seg=6, ring=4, scale=(1.3, 0.5, 0.3))

    # ---------------- bedroom (west wing, floor z=0.35) ----------------
    bx, by = -7.0, 1.9
    C.box("Furn_BedBase", (1.5, 2.1, 0.26), (bx, by, z + 0.13), "WoodWarm", col)
    C.box("Furn_BedMattress", (1.36, 1.96, 0.14), (bx, by, z + 0.33), "FabricIndigo", col)
    C.box("Furn_BedPillow", (0.42, 0.62, 0.09), (bx - 0.35, by + 0.6, z + 0.44), "FabricRed", col)
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.cyl(f"Furn_BedPost{sx}{sy}", 0.035, 1.35, (bx + sx * 0.68, by + sy * 0.98, z + 0.26), "WoodWarm", col, seg=7)
    for sy in (-1, 1):
        C.box(f"Furn_BedRailY{sy}", (1.44, 0.045, 0.05), (bx, by + sy * 0.98, z + 1.58), "WoodWarm", col)
    C.box("Furn_BedRailXL", (0.045, 2.0, 0.05), (bx - 0.68, by, z + 1.58), "WoodWarm", col)
    C.box("Furn_BedRailXR", (0.045, 2.0, 0.05), (bx + 0.68, by, z + 1.58), "WoodWarm", col)
    C.box("Furn_Wardrobe", (0.55, 1.5, 1.4), (-8.18, 0.4, z + 0.7), "WoodWarm", col)
    C.box("Furn_WardrobeDoor", (0.03, 1.4, 1.25), (-7.89, 0.4, z + 0.68), "WoodDark", col)
    C.cyl("Furn_LampPole", 0.025, 1.15, (-5.6, -1.9, z), "WoodDark", col, seg=7)
    C.cyl("Furn_LampBase", 0.13, 0.04, (-5.6, -1.9, z + 0.02), "WoodDark", col, seg=10)
    C.cyl("Furn_LampShade", 0.11, 0.24, (-5.6, -1.9, z + 1.02), "PaperWarm", col, seg=10, r_top=0.13)
    C.box("Furn_BedScreen0", (0.7, 0.04, 1.3), (-6.1, -1.0, z + 0.65), "WoodDark", col, rot=(0, 0.2, 0.5))
    C.box("Furn_BedScreen1", (0.7, 0.04, 1.3), (-6.6, -1.4, z + 0.65), "WoodDark", col, rot=(0, -0.2, 0.5))
    C.cyl("Furn_Stool", 0.19, 0.36, (-6.4, 0.2, z), "WoodWarm", col, seg=10)
