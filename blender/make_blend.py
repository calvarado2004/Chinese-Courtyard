"""Generate per-animal .blend working files for hand-tweaking in Blender:

    blender -b -P blender/make_blend.py

Each file contains the critter (objects named <Animal>_*) in a "Critters"
collection plus reference helpers (RefGround, RefCamera, RefSun, RefFill)
and a framed camera, so the animal is centred and lit the moment the file
opens. Export edits back into the app with blender/export_blend.py.
"""
import bpy
import sys
import os
import math
import mathutils

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender"))

from lib import common as C  # noqa: E402
from lib import critters as critters  # noqa: E402

OUT = os.path.join(ROOT, "blends")
os.makedirs(OUT, exist_ok=True)

ANIMALS = [
    ("koi", critters.build_koi),
    ("frog", critters.build_frog),
    ("dragonfly", critters.build_dragonfly),
    ("cat", critters.build_cat),
    ("sparrow", critters.build_sparrow),
]


def direction_to_euler(d):
    v = mathutils.Vector(d).normalized()
    return v.to_track_quat('-Z', 'Y').to_euler()


for tag, builder in ANIMALS:
    C.reset_scene()
    col = C.get_col("Critters")
    builder(col)
    bpy.context.view_layer.update()   # matrices must be fresh before bbox reads

    # reference helpers live OUTSIDE the Critters collection so exports ignore them
    root = bpy.context.scene.collection
    C.box("RefGround", (8, 8, 0.02), (0, 0, -0.012), "StoneGray", root)

    objs = list(col.objects)
    pts = [o.matrix_world @ mathutils.Vector(c) for o in objs for c in o.bound_box]
    mn = mathutils.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mathutils.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (mn + mx) / 2
    r = max((mx - mn).length / 2, 0.05)

    cam_data = bpy.data.cameras.new("RefCamera")
    cam = bpy.data.objects.new("RefCamera", cam_data)
    root.objects.link(cam)
    cam.location = center + mathutils.Vector((1.0, -1.35, 0.75)).normalized() * (r * 3.4)
    cam.rotation_euler = direction_to_euler(center - mathutils.Vector(cam.location))
    cam_data.lens = 50

    sun = bpy.data.lights.new("RefSun", 'SUN')
    sun.energy = 3.5
    sun_ob = bpy.data.objects.new("RefSun", sun)
    root.objects.link(sun_ob)
    sun_ob.rotation_euler = (math.radians(50), 0, math.radians(-35))

    fill = bpy.data.lights.new("RefFill", 'SUN')
    fill.energy = 0.8
    fill_ob = bpy.data.objects.new("RefFill", fill)
    root.objects.link(fill_ob)
    fill_ob.rotation_euler = (math.radians(35), math.radians(140), 0)

    world = bpy.data.worlds.new("RefWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.55, 0.58, 0.62, 1.0)
    bg.inputs[1].default_value = 0.8

    scene = bpy.context.scene
    scene.camera = cam
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 800

    path = os.path.join(OUT, f"{tag}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    print(f"[blend] {path}: {len(objs)} critter objects, radius {r:.2f} m")
