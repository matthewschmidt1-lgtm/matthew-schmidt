"""Render the home page header: "The Dance Floor".

Symbols, not words:
  checkerboard dance floor   strategy and movement on one surface (Nash)
  two pieces, two spotlights  partly shared, partly conflicting interests (Schelling)
  teal glow where light overlaps  value that only exists together (Nalebuff)
  curve of dance steps        moves answered by moves (Axelrod)
  receding doorways           the same meeting again and again; the glow beyond is walking away (Aumann)
  dice in the foreground      you never know everything (Duke)

Run:
  /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/render_hero.py -- "$PWD" [--samples N]
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ROOT = argv[0] if argv else os.getcwd()
SAMPLES = int(argv[argv.index('--samples') + 1]) if '--samples' in argv else 160
LAYER = argv[argv.index('--layer') + 1] if '--layer' in argv else 'bg'
OUT = os.path.join(ROOT, 'hero-' + LAYER + '.png')
W, H = 1200, 514


def lin(h):
    h = h.lstrip('#')
    return tuple(((int(h[i:i + 2], 16) / 255) / 12.92 if int(h[i:i + 2], 16) / 255 <= 0.04045 else (((int(h[i:i + 2], 16) / 255) + 0.055) / 1.055) ** 2.4) for i in (0, 2, 4)) + (1.0,)


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = lin(color)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if coat and 'Coat Weight' in p.inputs:
        p.inputs['Coat Weight'].default_value = coat
    if emit:
        p.inputs['Emission Color'].default_value = lin(emit)
        p.inputs['Emission Strength'].default_value = strength
    return m


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def mesh_from(name, bm, mats, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = link(bpy.data.objects.new(name, me))
    for m in (mats if isinstance(mats, list) else [mats]):
        ob.data.materials.append(m)
    return ob


def lathe(name, profile, m, loc, segs=64):
    """Revolve a (radius, z) profile around Z: the shape of a chess piece."""
    bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        ring = [bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in [i * 2 * math.pi / segs for i in range(segs)]]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(segs):
            bm.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    ob = mesh_from(name, bm, m, smooth=True)
    ob.location = loc
    return ob


def box(name, c, s, m, bevel=0.0):
    bm = bmesh.new()
    v = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.scale(bm, vec=s, verts=v)
    ob = mesh_from(name, bm, m)
    ob.location = c
    if bevel:
        mod = ob.modifiers.new('b', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
    return ob


def disc(name, c, r, m, h=0.004):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=r, radius2=r, depth=h)
    ob = mesh_from(name, bm, m, smooth=True)
    ob.location = c
    return ob


def ring(name, c, r, w, m):
    bm = bmesh.new()
    segs = 96
    outer = [bm.verts.new((math.cos(a) * r, math.sin(a) * r, 0)) for a in [i * 2 * math.pi / segs for i in range(segs)]]
    inner = [bm.verts.new((math.cos(a) * (r - w), math.sin(a) * (r - w), 0)) for a in [i * 2 * math.pi / segs for i in range(segs)]]
    for i in range(segs):
        bm.faces.new((outer[i], outer[(i + 1) % segs], inner[(i + 1) % segs], inner[i]))
    ob = mesh_from(name, bm, m)
    ob.location = c
    return ob


# ─────────────────────────────── scene

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = W, H
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print('CPU render:', e)
sc.view_settings.view_transform = 'AgX'
try:
    sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass
sc.render.image_settings.file_format = 'WEBP'
sc.render.image_settings.quality = 82
sc.render.image_settings.color_mode = 'RGB'

world = bpy.data.worlds.new('w')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#0b0e11')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25
sc.world = world

# Checkerboard dance floor: one mesh, two materials, glossy.
ivory_tile = mat('tile-a', '#cfc8b8', 0.22, coat=0.4)
dark_tile = mat('tile-b', '#1d2a2c', 0.18, coat=0.5)
bm = bmesh.new()
N = 40
for ix in range(-N // 2, N // 2):
    for iy in range(-8, 36):
        x0, y0 = ix * 1.0, iy * 1.0
        vs = [bm.verts.new((x0, y0, 0)), bm.verts.new((x0 + 1, y0, 0)), bm.verts.new((x0 + 1, y0 + 1, 0)), bm.verts.new((x0, y0 + 1, 0))]
        f = bm.faces.new(vs)
        f.material_index = (ix + iy) % 2
floor = mesh_from('floor', bm, [ivory_tile, dark_tile])
floor.location = (-0.5, 0, 0)

# The two pieces: same shape, opposite colours, facing each other.
profile = [(0.36, 0.0), (0.36, 0.06), (0.30, 0.10), (0.28, 0.16), (0.20, 0.22), (0.15, 0.32), (0.12, 0.62), (0.11, 0.80),
           (0.19, 0.84), (0.19, 0.88), (0.10, 0.92), (0.08, 0.96), (0.14, 1.02), (0.17, 1.10), (0.17, 1.16), (0.14, 1.24), (0.08, 1.29), (0.0, 1.31)]
ivory = mat('ivory', '#ece4d2', 0.16, coat=1.0)
ebony = mat('ebony', '#1a1d21', 0.12, coat=1.0)
def smooth_profile(pts, n=6):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t * t + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t ** 3) for d in range(2)))
    out.append(pts[-1])
    return [(max(r, 0.0), z) for (r, z) in out]
profile = smooth_profile(profile)
a = lathe('piece-ivory', profile, ivory, (-0.15, 1.6, 0), segs=128)
b = lathe('piece-ebony', profile, ebony, (1.25, 1.6, 0), segs=128)
# A slight lean toward each other: the dance.
a.rotation_euler = (0, math.radians(4), 0)
b.rotation_euler = (0, math.radians(-4), 0)

# Two spotlights whose pools overlap between the pieces.
def spot(name, loc, target, energy, color, size_deg, blend=0.35):
    ld = bpy.data.lights.new(name, 'SPOT')
    ld.energy = energy
    ld.color = lin(color)[:3]
    ld.spot_size = math.radians(size_deg)
    ld.spot_blend = blend
    ld.shadow_soft_size = 0.15
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


spot('spot-a', (-1.1, 0.9, 6.5), (-0.1, 1.6, 0), 2600, '#ffe7c4', 26)
spot('spot-b', (2.2, 0.9, 6.5), (1.2, 1.6, 0), 2600, '#ffe7c4', 26)
spot('rim', (0.55, 7.5, 3.2), (0.55, 1.6, 0.8), 900, '#9fe6dd', 30, 0.6)

# The shared ground: a thin teal ring inlaid where the pools overlap.
teal = mat('teal', '#0b7a87', 0.3, emit='#3fd0c4', strength=4.0)
ring('focal', (0.55, 1.6, 0.003), 0.42, 0.03, teal)
glow = mat('glow', '#0b7a87', 0.6, emit='#2bb7ad', strength=0.6)
disc('focal-fill', (0.55, 1.6, 0.002), 0.39, glow)

# Dance steps: a soft S-curve of marks from the foreground to the pieces.
step = mat('step', '#cfeee9', 0.5, emit='#7fd8cf', strength=0.9)
for i in range(9):
    t = i / 8
    x = -2.4 + t * 2.6 + math.sin(t * math.pi * 1.6) * 0.55
    y = -2.6 + t * 3.6
    side = 0.11 if i % 2 else -0.11
    d = disc(f'step{i}', (x + side, y, 0.003), 0.085, step)
    d.scale = (0.6, 1.55, 1)
    h = disc(f'heel{i}', (x + side, y - 0.17, 0.003), 0.05, step)
    d.rotation_euler = (0, 0, math.radians(-25 + t * 30))

# Receding doorways: the same meeting, again and again.
frame = mat('frame', '#2a3437', 0.6)
for i in range(7):
    y = 6.0 + i * 3.6
    w, h = 2.4, 3.6
    for x in (0.55 - w / 2, 0.55 + w / 2):
        box(f'post{i}{x}', (x, y, h / 2), (0.22, 0.22, h), frame)
    box(f'lintel{i}', (0.55, y, h + 0.11), (w + 0.22, 0.22, 0.22), frame)
for i in range(7):
    y = 6.0 + i * 3.6
    ld = bpy.data.lights.new(f'door{i}', 'AREA')
    ld.energy = 220 * (0.82 ** i)
    ld.color = lin('#9fe6dd')[:3]
    ld.size = 2.0
    o = link(bpy.data.objects.new(f'door{i}', ld))
    o.location = (0.55, y - 0.4, 3.4)
# The exit is only light: a warm glow blooming through the haze at the end of the corridor,
# with a dark back wall, so there is no hard bright shape to pull the eye.
box('exit', (0.55, 6.0 + 7 * 3.6 + 1.5, 1.8), (2.3, 0.05, 3.6), mat('exit', '#1d2527', 0.8))
ld = bpy.data.lights.new('exit-glow', 'POINT')
ld.energy = 140
ld.color = lin('#e9c79a')[:3]
ld.shadow_soft_size = 1.2
eg = link(bpy.data.objects.new('exit-glow', ld))
eg.location = (0.55, 6.0 + 7 * 3.6 - 0.8, 1.9)

# Dice at rest in the foreground.
die = mat('die', '#f2efe8', 0.25, coat=0.5)
pip = mat('pip', '#14171a', 0.4)


def dice(name, c, rz, top, front):
    s = 0.39
    ob = box(name, c, (s, s, s), die, bevel=0.05)
    ob.rotation_euler = (0, 0, rz)
    layouts = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, 1), (-1, 1), (1, -1)],
               5: [(-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)], 6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]}
    for i, (u, v) in enumerate(layouts[top]):
        p = disc(f'{name}-t{i}', (u * 0.085, v * 0.085, s / 2 + 0.001), 0.03, pip)
        p.parent = ob
    for i, (u, v) in enumerate(layouts[front]):
        p = disc(f'{name}-f{i}', (u * 0.085, -s / 2 - 0.001, v * 0.085), 0.03, pip)
        p.rotation_euler = (math.radians(90), 0, 0)
        p.parent = ob
    return ob


dice('die-a', (-1.25, -0.45, 0.195), math.radians(22), 5, 3)
dice('die-b', (-0.68, -0.12, 0.195), math.radians(-14), 2, 6)
spot('dice-light', (-2.0, -1.6, 2.6), (-1.0, -0.3, 0.1), 260, '#ffe7c4', 30, 0.8)

# Haze, so the light has a shape.
fog = mat('fog', '#ffffff')
fog.node_tree.nodes.remove(fog.node_tree.nodes['Principled BSDF'])
vol = fog.node_tree.nodes.new('ShaderNodeVolumePrincipled')
vol.inputs['Density'].default_value = 0.022
vol.inputs['Anisotropy'].default_value = 0.35
fog.node_tree.links.new(vol.outputs[0], fog.node_tree.nodes['Material Output'].inputs['Volume'])
box('haze', (0.5, 12, 4), (30, 34, 8.2), fog)

# Camera: low, close to the floor, looking up the corridor.
cd = bpy.data.cameras.new('cam')
cd.lens = 29.5
cd.sensor_width = 36
cd.dof.use_dof = True
cd.dof.focus_distance = 7.2
cd.dof.aperture_fstop = 4.0
cam = link(bpy.data.objects.new('cam', cd))
cam.location = (-1.2, -5.6, 1.0)
cam.rotation_euler = (Vector((-1.15, 3.0, 1.15)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam

sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
pieces = {bpy.data.objects['piece-ivory'], bpy.data.objects['piece-ebony']}
if LAYER == 'bg':
    for o in pieces: o.hide_render = True
else:
    sc.render.film_transparent = True
    bpy.data.lights['spot-a'].energy = 1700
    bpy.data.lights['spot-b'].energy = 1700
    bpy.data.lights['rim'].energy = 2600
    spot('rim-2', (-1.6, 6.5, 2.2), (0.55, 1.6, 0.7), 1400, '#9fe6dd', 34, 0.7)
    for o in bpy.data.objects:
        if o.type in ('MESH',) and o not in pieces: o.hide_render = True
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('hero rendered', OUT)
