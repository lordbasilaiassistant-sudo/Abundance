"""Abundance - the 3D pass.

Run headless:
  blender -b --factory-startup -P scene.py -- --start 1 --end 2160 --out <dir>

Builds a field of 44,000 points of light (one instance per point, brightness
driven per-point per-frame), three resource monoliths that dissolve into rain,
and the camera moves. Renders PNG frames only - all typography is composited
afterwards by type_pass.py, so text can be re-cut without re-rendering.

Nothing here is a generated image: every pixel comes from authored geometry,
which is the same standard the site holds itself to.
"""
import bpy, bmesh, math, os, sys, json, random
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
sys.path.insert(0, HERE)
import timeline as T  # noqa: E402

# ----------------------------------------------------------------- args ------
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    if name in argv:
        return argv[argv.index(name) + 1]
    return default


START = int(arg("--start", 1))
END = int(arg("--end", T.END))
OUT = os.path.abspath(arg("--out", os.path.join(HERE, "render")))
PROBE = "--probe" in argv
SAMPLES = int(arg("--samples", 48))
PCT = int(arg("--pct", 100))
FRAMES = [int(x) for x in arg("--frames", "").split(",") if x.strip()]

os.makedirs(OUT, exist_ok=True)

with open(os.path.join(HERE, "film_facts.json"), encoding="utf-8") as fh:
    FACTS = json.load(fh)

# --------------------------------------------------------------- palette ----
BG_TOP = (0.031, 0.043, 0.063)
BG_BOT = (0.008, 0.011, 0.018)
POINT_WARM = (1.000, 0.906, 0.780)
HUES = {d["key"]: tuple(d["hue"]) for d in FACTS["divisions"]}

N_POINTS = 44000
FIELD_R = 62.0
N_RAIN = 9000

rng = np.random.default_rng(20260907)


# ============================================================ scene reset ====
def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.node_groups,
                 bpy.data.objects, bpy.data.cameras):
        for item in list(coll):
            try:
                coll.remove(item)
            except Exception:
                pass


# ============================================================== helpers ======
def new_mesh_object(name, coords):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(c) for c in coords], [], [])
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def ensure_attr(me, name, dtype="FLOAT", domain="POINT"):
    if name not in me.attributes:
        me.attributes.new(name=name, type=dtype, domain=domain)
    return me.attributes[name]


def write_positions(ob, pos):
    """pos: (N,3) float array."""
    ob.data.vertices.foreach_set("co", pos.astype(np.float32).ravel())
    ob.data.update()


def write_float_attr(ob, name, vals):
    a = ensure_attr(ob.data, name)
    a.data.foreach_set("value", vals.astype(np.float32).ravel())


# ================================================== point material ===========
def make_point_material(name, colour, boost=1.0):
    """Emission whose strength is read per-instance from the `glow` attribute."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_type = "INSTANCER"
    attr.attribute_name = "glow"
    attr.location = (-800, 0)

    # glow drives strength non-linearly so faint points stay faint
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.6
    pw.location = (-600, 0)
    nt.links.new(attr.outputs["Fac"], pw.inputs[0])

    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 3.6 * boost
    mul.location = (-420, 0)
    nt.links.new(pw.outputs[0], mul.inputs[0])

    # warm shift: brighter points run slightly whiter
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-620, -240)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (colour[0] * 0.72, colour[1] * 0.62,
                                         colour[2] * 0.55, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (colour[0], colour[1], colour[2], 1)
    nt.links.new(attr.outputs["Fac"], ramp.inputs["Fac"])

    em = nt.nodes.new("ShaderNodeEmission")
    em.location = (-200, 0)
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(mul.outputs[0], em.inputs["Strength"])

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (0, 0)
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return mat


# ============================================ geometry-nodes instancer ======
def add_point_instancer(ob, mat, base_radius=0.055):
    """Instance a small icosphere on every vertex, scaled by the `psize`
    attribute. Point-domain attributes (incl. `glow`) propagate to the instance
    domain, which the shader reads via an INSTANCER Attribute node."""
    ng = bpy.data.node_groups.new(ob.name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT",
                            socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT",
                            socket_type="NodeSocketGeometry")
    n = ng.nodes
    gin = n.new("NodeGroupInput"); gin.location = (-700, 0)
    gout = n.new("NodeGroupOutput"); gout.location = (500, 0)

    ico = n.new("GeometryNodeMeshIcoSphere")
    ico.location = (-500, -220)
    ico.inputs["Subdivisions"].default_value = 2
    ico.inputs["Radius"].default_value = base_radius

    named = n.new("GeometryNodeInputNamedAttribute")
    named.data_type = "FLOAT"
    named.inputs["Name"].default_value = "psize"
    named.location = (-500, -420)

    inst = n.new("GeometryNodeInstanceOnPoints")
    inst.location = (-180, 0)
    ng.links.new(gin.outputs[0], inst.inputs["Points"])
    ng.links.new(ico.outputs["Mesh"], inst.inputs["Instance"])
    ng.links.new(named.outputs[0], inst.inputs["Scale"])

    setm = n.new("GeometryNodeSetMaterial")
    setm.location = (150, 0)
    setm.inputs["Material"].default_value = mat
    ng.links.new(inst.outputs[0], setm.inputs["Geometry"])
    ng.links.new(setm.outputs[0], gout.inputs[0])

    m = ob.modifiers.new(ob.name + "_gn", "NODES")
    m.node_group = ng
    return ng


# ================================================================ world ======
def build_world():
    world = bpy.data.worlds.new("W")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.location = (-900, 0)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-720, 0)
    nt.links.new(geo.outputs["Incoming"], sep.inputs[0])
    # view-ray Z (-1 down .. +1 up) -> 0..1 so the gradient is a real sky
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.location = (-560, 0)
    mr.inputs["From Min"].default_value = -0.45
    mr.inputs["From Max"].default_value = 0.55
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])

    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (-380, 0)
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*BG_BOT, 1)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (*BG_TOP, 1)
    e = cr.elements.new(0.30)
    e.color = (0.050, 0.070, 0.094, 1)      # horizon lift
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])

    bg = nt.nodes.new("ShaderNodeBackground"); bg.location = (-120, 0)
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputWorld"); out.location = (60, 0)
    nt.links.new(bg.outputs[0], out.inputs["Surface"])


def build_backdrop():
    """A large plane far behind the field carrying a soft vertical gradient and
    a horizon bloom, so the frame has atmosphere instead of flat black."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 190, 40))
    ob = bpy.context.object
    ob.name = "backdrop"
    ob.scale = (330, 150, 1)
    ob.rotation_euler = (math.radians(90), 0, 0)

    mat = bpy.data.materials.new("backdrop")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexCoord"); tex.location = (-900, 0)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-720, 0)
    nt.links.new(tex.outputs["Generated"], sep.inputs[0])

    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (-540, 0)
    cr = ramp.color_ramp
    cr.elements[0].position = 0.02
    cr.elements[0].color = (*BG_BOT, 1)
    cr.elements[1].position = 0.62
    cr.elements[1].color = (*BG_TOP, 1)
    e = cr.elements.new(0.30)
    e.color = (0.055, 0.078, 0.105, 1)   # horizon lift
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])

    em = nt.nodes.new("ShaderNodeEmission"); em.location = (-260, 0)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (0, 0)
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(mat)
    return ob


# ================================================================ field ======
def phyllotaxis(n, radius):
    i = np.arange(n)
    ga = math.pi * (3.0 - math.sqrt(5.0))
    r = radius * np.sqrt((i + 0.5) / n)
    th = i * ga
    # jitter breaks the visible spiral so it reads organic, not generated
    r = r + rng.normal(0, radius * 0.008, n)
    th = th + rng.normal(0, 0.035, n)
    x = r * np.cos(th)
    y = r * np.sin(th)
    z = -0.055 * np.power(np.abs(r), 1.32) + rng.normal(0, 0.10, n)
    return np.stack([x, y, z], axis=1), r


def build_field():
    pos, rad = phyllotaxis(N_POINTS, FIELD_R)
    ob = new_mesh_object("field", pos)
    mat = make_point_material("m_point", POINT_WARM, boost=1.0)
    add_point_instancer(ob, mat, base_radius=0.055)

    psize = (0.55 + rng.random(N_POINTS) * 0.85).astype(np.float32)
    # far points a touch larger so the horizon does not dissolve
    psize *= (1.0 + 0.5 * (rad / FIELD_R))
    write_float_attr(ob, "psize", psize)
    ensure_attr(ob.data, "glow")
    return ob, pos, rad, psize


def build_rain():
    ob = new_mesh_object("rain", np.zeros((N_RAIN, 3)))
    mat = make_point_material("m_rain", (1.0, 1.0, 1.0), boost=1.35)
    add_point_instancer(ob, mat, base_radius=0.060)
    psize = (0.42 + rng.random(N_RAIN) * 0.55).astype(np.float32)
    write_float_attr(ob, "psize", psize)
    ensure_attr(ob.data, "glow")
    return ob, psize


def build_monolith():
    """A tall slab that descends over the field, then breaks into rain."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 24, 34))
    ob = bpy.context.object
    ob.name = "monolith"
    ob.scale = (7.0, 7.0, 20.0)

    mat = bpy.data.materials.new("m_monolith")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    # emissive body, alpha-blended so it reads as contained light, not a solid
    em = nt.nodes.new("ShaderNodeEmission"); em.location = (-400, 120)
    em.inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
    em.inputs["Strength"].default_value = 1.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.location = (-400, -80)
    fres = nt.nodes.new("ShaderNodeFresnel"); fres.location = (-600, -220)
    fres.inputs["IOR"].default_value = 1.30
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.location = (-160, 0)
    nt.links.new(fres.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (60, 0)
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    mat.blend_method = "BLEND"
    mat.show_transparent_back = False
    ob.data.materials.append(mat)
    ob.hide_render = True
    return ob, mat, em


def build_edges(monolith):
    """Crisp emissive edges on the slab - the detail that stops it reading flat."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 24, 34))
    ob = bpy.context.object
    ob.name = "monolith_edges"
    ob.scale = monolith.scale
    w = ob.modifiers.new("wire", "WIREFRAME")
    w.thickness = 0.022
    w.use_relative_offset = True

    mat = bpy.data.materials.new("m_edges")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 6.0
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(mat)
    ob.hide_render = True
    return ob, em


# =============================================================== camera ======
def build_camera():
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 40
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 2.4
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    tgt = bpy.data.objects.new("cam_target", None)
    bpy.context.scene.collection.objects.link(tgt)
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    cam_data.dof.focus_object = tgt
    return cam, tgt


# ============================================================ compositor =====
def build_compositor():
    scn = bpy.context.scene
    scn.use_nodes = True
    nt = scn.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers"); rl.location = (-900, 0)

    fog = nt.nodes.new("CompositorNodeGlare"); fog.location = (-660, 0)
    fog.glare_type = "FOG_GLOW"
    fog.quality = "HIGH"
    fog.threshold = 0.72
    fog.size = 8
    fog.mix = -0.62
    nt.links.new(rl.outputs["Image"], fog.inputs["Image"])

    streak = nt.nodes.new("CompositorNodeGlare"); streak.location = (-440, 0)
    streak.glare_type = "STREAKS"
    streak.quality = "HIGH"
    streak.threshold = 0.90
    streak.streaks = 6
    streak.angle_offset = math.radians(12)
    streak.fade = 0.88
    streak.mix = -0.90          # very light - a hint of anamorphic, not a flare show
    nt.links.new(fog.outputs["Image"], streak.inputs["Image"])

    # subtle vignette
    ell = nt.nodes.new("CompositorNodeEllipseMask"); ell.location = (-660, -320)
    ell.width, ell.height = 0.98, 1.02
    blur = nt.nodes.new("CompositorNodeBlur"); blur.location = (-480, -320)
    blur.filter_type = "FAST_GAUSS"   # a 300px true gauss dominated frame cost
    blur.size_x, blur.size_y = 300, 300
    blur.use_relative = False
    nt.links.new(ell.outputs["Mask"], blur.inputs["Image"])

    vmix = nt.nodes.new("CompositorNodeMixRGB"); vmix.location = (-240, -160)
    vmix.blend_type = "MULTIPLY"
    vmix.inputs["Fac"].default_value = 0.42
    nt.links.new(streak.outputs["Image"], vmix.inputs[1])
    nt.links.new(blur.outputs["Image"], vmix.inputs[2])

    comp = nt.nodes.new("CompositorNodeComposite"); comp.location = (60, 0)
    nt.links.new(vmix.outputs["Image"], comp.inputs["Image"])


# ============================================================== render =======
def build_render():
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_EEVEE_NEXT"
    scn.render.resolution_x, scn.render.resolution_y = T.W, T.H
    scn.render.resolution_percentage = PCT
    scn.render.fps = T.FPS
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGB"
    scn.render.image_settings.compression = 25
    scn.render.film_transparent = False
    ee = scn.eevee
    ee.taa_render_samples = SAMPLES
    for attr, val in (("use_raytracing", False), ("use_shadows", False),
                      ("use_volumetric_shadows", False)):
        if hasattr(ee, attr):
            setattr(ee, attr, val)
    scn.view_settings.view_transform = "AgX"
    scn.view_settings.look = "AgX - Medium High Contrast"


# ======================================================== animation ==========
class Film:
    def __init__(self):
        self.field, self.fpos, self.frad, self.fpsize = build_field()
        self.rain, self.rain_psize = build_rain()
        self.mono, self.mono_mat, self.mono_em = build_monolith()
        self.edges, self.edge_em = build_edges(self.mono)
        self.cam, self.tgt = build_camera()

        n = N_POINTS
        # per-point randomness reused every frame (never re-drawn, so no flicker)
        self.ph = rng.random(n) * math.tau
        self.rank = rng.random(n)
        self.ang = np.arctan2(self.fpos[:, 1], self.fpos[:, 0])
        self.seed_idx = int(np.argmin(self.frad))   # the one light we open on

        # act 3: which points keep their light when it concentrates
        cx, cy = FIELD_R * 0.46, FIELD_R * 0.30
        d = np.hypot(self.fpos[:, 0] - cx, self.fpos[:, 1] - cy)
        self.keep = np.clip(1.0 - (d / (FIELD_R * 0.30)), 0, 1) ** 1.5

        # rain
        self.rain_x = rng.normal(0, 5.4, N_RAIN)
        self.rain_y = 24 + rng.normal(0, 5.4, N_RAIN)
        self.rain_delay = rng.random(N_RAIN)
        self.rain_speed = 0.85 + rng.random(N_RAIN) * 0.5
        self.rain_land = -0.055 * np.power(
            np.hypot(self.rain_x, self.rain_y), 1.32)

    # ------------------------------------------------------------ glow ------
    def field_glow(self, f):
        n = N_POINTS
        g = np.zeros(n, dtype=np.float32)
        r = self.frad

        # --- ACT 1: one light, then ignition spreading outward --------------
        if f <= T.A1[1]:
            seed = T.hold(f, 1, 200, 40, 0)
            g[self.seed_idx] += seed                     # exactly one point
            front = T.ease_out_quint(T.span(f, 96, 330)) * (FIELD_R * 1.22)
            reach = np.clip((front - r) / 9.0, 0, 1)
            base = 0.30 + 0.52 * self.rank
            g = np.maximum(g, reach * base)
            # a slow breath so the field is never static
            g *= 0.90 + 0.10 * np.sin(f * 0.021 + self.ph)
            return np.clip(g, 0, 1.6)

        base = 0.30 + 0.52 * self.rank
        g = base * (0.90 + 0.10 * np.sin(f * 0.021 + self.ph))

        # --- ACT 2: each beat lifts the field as the resource lands ---------
        for b in T.BEATS:
            if b["start"] <= f <= b["end"] + 40:
                land = T.ease_out_cubic(T.span(f, b["start"] + 108, b["end"] - 10))
                decay = 1.0 - T.ease_in_quad(T.span(f, b["end"], b["end"] + 40))
                g += 0.55 * land * decay * (0.6 + 0.4 * self.rank)

        # --- ACT 3: the light does not spread - it concentrates -------------
        if f >= T.A3[0]:
            t = T.ease_in_out_cubic(T.span(f, T.A3[0] + 30, T.A3[0] + 190))
            conc = self.keep * 1.70 + 0.30
            g = g * (1 - t) + (g * conc) * t

        # --- ACT 4: quiet field, a few points re-igniting (the commits) -----
        # Blend toward a calm absolute level. Multiplying the act-3 state here
        # compounds the concentration and drives the whole field to near zero.
        if f >= T.A4[0]:
            t = T.ease_in_out_cubic(T.span(f, T.A4[0], T.A4[0] + 70))
            calm = ((0.36 + 0.26 * self.rank)
                    * (0.92 + 0.08 * np.sin(f * 0.019 + self.ph)))
            g = g * (1 - t) + calm * t
            k = int(T.span(f, T.A4[0] + 80, T.A4[1] - 30) * 46)   # 46 commits
            if k > 0:
                idx = (np.arange(n) % 46) < k
                pulse = 0.55 + 0.45 * np.sin(f * 0.10 + self.ph)
                g = np.where(idx & (self.rank > 0.9955),
                             g + 1.30 * pulse, g)

        # --- ACT 5: the field lights evenly ---------------------------------
        if f >= T.A5[0]:
            t = T.ease_in_out_cubic(T.span(f, T.A5[0], T.A5[0] + 150))
            even = (0.62 + 0.30 * self.rank) * (0.94 + 0.06 * np.sin(f * 0.018 + self.ph))
            g = g * (1 - t) + even * t

        return np.clip(g, 0, 1.8)

    # ------------------------------------------------------------ rain ------
    def update_rain(self, f):
        beat = None
        for b in T.BEATS:
            if b["start"] - 10 <= f <= b["end"]:
                beat = b
                break
        if beat is None:
            z = np.zeros(N_RAIN, dtype=np.float32)
            write_float_attr(self.rain, "glow", z)
            write_float_attr(self.rain, "psize", z)   # else they sit there as black spheres
            self.rain.data.update()
            self.rain.hide_render = True
            return
        self.rain.hide_render = False

        # rain runs from the slab breaking to the field lighting
        t0, t1 = beat["start"] + 84, beat["start"] + 176
        t = T.span(f, t0, t1)
        prog = np.clip((t - self.rain_delay * 0.42) * self.rain_speed * 1.9, 0, 1)
        top = 34.0
        z = top + (self.rain_land - top) * T.ease_in_quad(prog)
        pos = np.stack([self.rain_x, self.rain_y, z], axis=1)
        write_positions(self.rain, pos)

        alive = ((prog > 0.001) & (prog < 0.999)).astype(np.float32)
        fade = np.sin(np.clip(prog, 0, 1) * math.pi) ** 0.5
        gl = (alive * fade * 1.25).astype(np.float32)
        write_float_attr(self.rain, "glow", gl)
        write_float_attr(self.rain, "psize",
                         self.rain_psize * np.clip(gl, 0, 1))
        self.rain.data.update()

    # -------------------------------------------------------- monolith ------
    def update_monolith(self, f):
        beat = None
        for b in T.BEATS:
            if b["start"] - 20 <= f <= b["end"]:
                beat = b
                break
        if beat is None:
            self.mono.hide_render = True
            self.edges.hide_render = True
            return
        self.mono.hide_render = False
        self.edges.hide_render = False

        hue = HUES[beat["key"]]
        self.mono_em.inputs["Color"].default_value = (*hue, 1)
        self.edge_em.inputs["Color"].default_value = (*hue, 1)

        # descend, hold, then collapse as it breaks into rain
        drop = T.ease_out_cubic(T.span(f, beat["start"], beat["start"] + 76))
        z = 84 - 64 * drop
        collapse = T.ease_in_out_cubic(T.span(f, beat["start"] + 84, beat["start"] + 150))
        h = 20.0 * (1.0 - 0.97 * collapse)
        appear = T.hold(f, beat["start"], beat["start"] + 152, 26, 30)

        for ob in (self.mono, self.edges):
            ob.location = (0, 24, z)
            ob.scale = (7.0, 7.0, max(h, 0.02))
        self.mono_em.inputs["Strength"].default_value = 2.6 * appear
        self.edge_em.inputs["Strength"].default_value = 7.5 * appear
        if appear < 0.012:
            # a fully faded slab is still opaque geometry - it reads as a black box
            self.mono.hide_render = True
            self.edges.hide_render = True

    # ---------------------------------------------------------- camera ------
    def update_camera(self, f):
        """Five distinct setups with real cuts between them - not one endless dolly.

        Framed against the actual field: a disc of radius 62 whose dome falls to
        about z = -12 at the rim. The camera has to stand outside that to read it.
        """
        fstop = 2.8
        if f <= T.A1[1]:
            # start tight on the single seed point, then retreat until the whole
            # field is in frame. Long lens to short: the reveal is the shot.
            t = T.ease_in_out_cubic(T.span(f, 30, 410))
            pos = Vector((0, -7.0 - 81.0 * t, 1.4 + 26.0 * t))
            tgt = Vector((0, 0, 0.3 - 2.6 * t))
            self.cam.data.lens = 82 - 46 * t
            fstop = 2.2 + 6.0 * t          # shallow on the seed, deep on the field
        elif f <= T.A2[1]:
            # outside the rim looking back at the slab standing over the field;
            # alternate sides per beat so the three divisions are not one shot
            b = [x for x in T.BEATS if x["start"] <= f <= x["end"]]
            b = b[0] if b else T.BEATS[-1]
            t = T.ease_in_out_cubic(T.span(f, b["start"], b["end"]))
            side = -1.0 if T.BEATS.index(b) % 2 == 0 else 1.0
            pos = Vector((side * (25 - 7 * t), -60 + 6 * t, 12 + 5 * t))
            tgt = Vector((0, 14, 17 - 13 * t))   # tilt down as the slab collapses
            self.cam.data.lens = 38
            fstop = 5.6
        elif f <= T.A3[1]:
            # high and cold: the uneven shape is only legible from above
            t = T.ease_in_out_cubic(T.span(f, T.A3[0], T.A3[1]))
            pos = Vector((-14 + 30 * t, -74 - 4 * t, 54 + 14 * t))
            tgt = Vector((6 + 10 * t, 2, -3))
            self.cam.data.lens = 40
            fstop = 8.0
        elif f <= T.A4[1]:
            # intimate: down among the points, shallow, so one light is a subject
            t = T.ease_in_out_cubic(T.span(f, T.A4[0], T.A4[1]))
            pos = Vector((20 - 7 * t, -52 - 4 * t, 31 + 5 * t))
            tgt = Vector((0, 4, -2.0))
            self.cam.data.lens = 46
            fstop = 2.0
        else:
            # settle wide and still for the close
            t = T.ease_out_quint(T.span(f, T.A5[0], T.A5[1]))
            pos = Vector((0, -88 - 16 * t, 54 + 18 * t))
            tgt = Vector((0, 2, -5.0))
            self.cam.data.lens = 33 - 2 * t
            fstop = 7.0

        self.cam.location = pos
        self.tgt.location = tgt
        self.cam.data.dof.aperture_fstop = fstop

    # ------------------------------------------------------------ tick ------
    def presence(self, f):
        """Floor under a point's size. Zero at the open, so the very first shot
        is one light in real emptiness rather than a crowd of dark spheres."""
        return 0.30 * T.ease_in_out_cubic(T.span(f, 150, 330))

    def tick(self, f):
        g = self.field_glow(f)
        fl = self.presence(f)
        write_float_attr(self.field, "glow", g)
        write_float_attr(self.field, "psize",
                         self.fpsize * (fl + (1.0 - fl) * np.clip(g, 0, 1)))
        self.field.data.update()
        self.update_rain(f)
        self.update_monolith(f)
        self.update_camera(f)


# ================================================================= main ======
def main():
    wipe()
    build_world()
    build_render()
    film = Film()
    build_compositor()

    scn = bpy.context.scene
    scn.frame_start, scn.frame_end = 1, T.END

    if PROBE:
        # prove the per-instance glow attribute actually reaches the shader:
        # left half dark, right half bright. If the halves match, it is broken.
        g = (film.fpos[:, 0] > 0).astype(np.float32) * 1.2
        write_float_attr(film.field, "glow", g)
        film.field.data.update()
        film.update_camera(300)
        film.mono.hide_render = True
        film.edges.hide_render = True
        scn.render.filepath = os.path.join(OUT, "probe_glow.png")
        bpy.ops.render.render(write_still=True)
        print("PROBE_WROTE", scn.render.filepath)
        return

    todo = FRAMES if FRAMES else range(START, END + 1)
    for f in todo:
        scn.frame_set(f)
        film.tick(f)
        scn.render.filepath = os.path.join(OUT, "f_%05d.png" % f)
        bpy.ops.render.render(write_still=True)
        if f % 25 == 0 or f == START:
            print("FRAME %d/%d" % (f, END), flush=True)
    print("RENDER_DONE", START, END)


main()
