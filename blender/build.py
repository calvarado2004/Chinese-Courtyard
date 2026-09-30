"""Entry point: blender -b -P blender/build.py -- --stage N [--no-render]

Builds stages cumulatively, exports GLBs, renders preview PNGs to check/."""
import bpy
import sys
import os
import shutil
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender"))

from lib import common as C  # noqa: E402
from lib import architecture as arch  # noqa: E402
from lib import garden as garden  # noqa: E402
from lib import interior as interior  # noqa: E402
from lib import critters as critters  # noqa: E402

MODELS = os.path.join(ROOT, "models")
CHECK = os.path.join(ROOT, "check")


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    stage, render = 1, True
    i = 0
    while i < len(argv):
        if argv[i] == "--stage":
            stage = int(argv[i + 1]); i += 2
        elif argv[i] == "--no-render":
            render = False; i += 1
        else:
            i += 1
    return stage, render


def export_glb(filename, objects):
    col_objs = set(objects)
    for ob in bpy.data.objects:
        ob.select_set(ob in col_objs)
    bpy.context.view_layer.objects.active = objects[0]
    path = os.path.join(MODELS, filename)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format='GLB',
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_apply=True,
    )
    # mirror into web/models so the static server tree is self-contained
    web_models = os.path.join(ROOT, "web", "models")
    os.makedirs(web_models, exist_ok=True)
    shutil.copy2(path, os.path.join(web_models, filename))


def setup_preview_world():
    world = bpy.data.worlds.new("preview")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.55, 0.58, 0.62, 1.0)
    bg.inputs[1].default_value = 0.8
    sun = bpy.data.lights.new("sun", 'SUN')
    sun.energy = 3.5
    sun_ob = bpy.data.objects.new("sun", sun)
    sun_ob.rotation_euler = (math.radians(50), 0, math.radians(-35))
    bpy.context.scene.collection.objects.link(sun_ob)
    fill = bpy.data.lights.new("fill", 'SUN')
    fill.energy = 0.8
    fill_ob = bpy.data.objects.new("fill", fill)
    fill_ob.rotation_euler = (math.radians(35), math.radians(140), 0)
    bpy.context.scene.collection.objects.link(fill_ob)


def render_views(tag, hide_roofs=False):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 40
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 760
    scene.render.film_transparent = False

    cam_data = bpy.data.cameras.new("checkcam")
    cam = bpy.data.objects.new("checkcam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    scene.camera = cam

    views = [
        ("iso", (16.5, -14.0, 12.0), (0, 0.5, 1.0), 50),
        ("top", (0, 0, 34.0), (0, 0, 0), 0),  # ortho below
        ("courtyard", (-4.5, -5.5, 3.2), (1.5, 1.5, 1.6), 60),
        ("moongate", (5.8, -6.35, 1.7), (4.5, -1.6, 0.8), 42),
        ("entry", (1.5, -8.6, 1.8), (1.5, -1.5, 1.0), 55),
    ]
    if hide_roofs:
        for ob in list(bpy.data.objects):
            if "Roof" in ob.name or ob.name.endswith(("Fin+1", "Fin-1")) or "_ridge" in ob.name or "_fascia" in ob.name:
                ob.hide_render = True
                ob.hide_viewport = True
    for name, loc, target, lens in views:
        cam.location = loc
        direction = [target[i] - loc[i] for i in range(3)]
        cam.rotation_euler = direction_to_euler(direction)
        if name == "top":
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = 21.0
            cam.rotation_euler = (0, 0, 0)
        else:
            cam_data.type = 'PERSP'
            cam_data.lens = lens
        scene.render.filepath = os.path.join(CHECK, f"{tag}_{name}.png")
        bpy.ops.render.render(write_still=True)
    for ob in list(bpy.data.objects):
        if ob.name == "checkcam":
            bpy.data.objects.remove(ob, do_unlink=True)


def direction_to_euler(d):
    import mathutils
    v = mathutils.Vector(d).normalized()
    return v.to_track_quat('-Z', 'Y').to_euler()


def main():
    stage, do_render = parse_args()
    C.reset_scene()
    col = C.get_col("Courtyard")
    arch.build(col)
    if stage >= 2:
        garden.build(col)
    if stage >= 3:
        interior.build(col)
    if stage >= 5:
        critters.build(C.get_col("Critters"))

    # categorize for export by prefix
    GARDEN_PREFIX = ("Pond", "Rockery", "Pine", "Bamboo", "Lantern", "Path", "Lily",
                     "StepStone", "Spout", "Stream", "MossPatch", "Grass", "Litter",
                     "Terrain", "Bush", "Stump")
    INTERIOR_PREFIX = ("Furn_",)
    arch_objs = [o for o in col.objects if not o.name.startswith(GARDEN_PREFIX + INTERIOR_PREFIX)]
    garden_objs = [o for o in col.objects if o.name.startswith(GARDEN_PREFIX)]
    interior_objs = [o for o in col.objects if o.name.startswith(INTERIOR_PREFIX)]

    export_glb("architecture.glb", arch_objs)
    if garden_objs:
        export_glb("garden.glb", garden_objs)
    if interior_objs:
        export_glb("interior.glb", interior_objs)
    if stage >= 5:
        crit_col = bpy.data.collections.get("Critters")
        for animal in ("Koi", "Frog", "Dragonfly", "Cat", "Sparrow"):
            objs = [o for o in crit_col.objects if o.name.startswith(animal)]
            export_glb(f"critter_{animal.lower()}.glb", objs)
    print(f"[build] stage {stage}: {len(arch_objs)} arch / {len(garden_objs)} garden / "
          f"{len(interior_objs)} interior objects exported")

    if do_render:
        setup_preview_world()
        render_views(f"stage{stage}", hide_roofs=(stage >= 3))


main()
