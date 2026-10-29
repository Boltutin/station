"""
Fixed Generator for Railway Passenger Station Pavilion 3D Model (.glb).
Corrects all geometry orientations using explicit cylinder segments.
Ensures zero floating meshes, solid ramp wedge, and compliant polygon count (5k-50k).
"""

import os
import sys
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
import pygltflib

def create_box(extents, translation=[0, 0, 0], material=None):
    mesh = trimesh.creation.box(extents=extents)
    mesh.unmerge_vertices()
    mesh.apply_translation(translation)
    if material:
        mesh.visual.material = material
    return mesh

def create_segment_cylinder(radius, pt_start, pt_end, sections=16, material=None):
    """Creates a cylinder precisely between pt_start and pt_end"""
    mesh = trimesh.creation.cylinder(radius=radius, segment=[pt_start, pt_end], sections=sections)
    if material:
        mesh.visual.material = material
    return mesh

def create_pyramid_stud(bottom_w=0.032, top_w=0.016, h=0.007):
    """
    Creates a truncated 4-sided pyramid tactile stud (warning point stud / точечный риф)
    compliant with GOST R 52875-2018 for tactile warning fields before stairs and ramps.
    """
    bw = bottom_w / 2.0
    tw = top_w / 2.0
    verts = np.array([
        [-bw, 0.0, -bw], [+bw, 0.0, -bw], [+bw, 0.0, +bw], [-bw, 0.0, +bw],
        [-tw, h, -tw], [+tw, h, -tw], [+tw, h, +tw], [-tw, h, +tw],
    ])
    faces = np.array([
        [0, 3, 2], [0, 2, 1],  # Bottom
        [4, 5, 6], [4, 6, 7],  # Top
        [0, 1, 5], [0, 5, 4],  # Front
        [1, 2, 6], [1, 6, 5],  # Right
        [2, 3, 7], [2, 7, 6],  # Back
        [3, 0, 4], [3, 4, 7],  # Left
    ])
    m = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    m.unmerge_vertices()
    return m

def create_trapezoid_rib(length, h, bottom_w, top_w):
    """
    Creates a longitudinal trapezoidal tactile rib with beveled sloped sides
    compliant with GOST R 52875-2018 for high visual depth and cast shadow.
    """
    x0 = -length / 2.0
    x1 = length / 2.0
    bw = bottom_w
    tw = top_w
    
    verts = np.array([
        [x0, 0.0, -bw / 2.0],
        [x0, 0.0, +bw / 2.0],
        [x0, h, +tw / 2.0],
        [x0, h, -tw / 2.0],
        [x1, 0.0, -bw / 2.0],
        [x1, 0.0, +bw / 2.0],
        [x1, h, +tw / 2.0],
        [x1, h, -tw / 2.0],
    ])
    faces = np.array([
        [0, 4, 5], [0, 5, 1],  # Bottom
        [3, 2, 6], [3, 6, 7],  # Top ridge
        [0, 3, 7], [0, 7, 4],  # -Z sloped bevel
        [1, 5, 6], [1, 6, 2],  # +Z sloped bevel
        [0, 1, 2], [0, 2, 3],  # -X cap
        [4, 7, 6], [4, 6, 5]   # +X cap
    ])
    m = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    m.unmerge_vertices()
    return m

def create_sh3_sleeper(length=2.7, base_w=0.28, top_w=0.21, h_center=0.18, h_end=0.10, bevel_len=0.22):
    """
    Parametric generator for Russian prestressed concrete sleeper Type Sh-3 (ГОСТ Р 54747-2011).
    Features authentic beveled/tapered ends and trapezoidal cross-section.
    """
    z0 = -length / 2.0
    z1 = z0 + bevel_len
    z2 = length / 2.0 - bevel_len
    z3 = length / 2.0

    sections_z = [z0, z1, z2, z3]
    sections_h = [h_end, h_center, h_center, h_end]
    sections_top_w = [top_w * 0.9, top_w, top_w, top_w * 0.9]

    vertices = []
    for z, h, tw in zip(sections_z, sections_h, sections_top_w):
        vertices.append([-base_w/2, 0.0, z])
        vertices.append([+base_w/2, 0.0, z])
        vertices.append([+tw/2, h, z])
        vertices.append([-tw/2, h, z])

    vertices = np.array(vertices, dtype=np.float32)

    faces = []
    for s in range(3):
        i0 = s * 4
        i1 = (s + 1) * 4
        faces.append([i0+0, i1+0, i1+1])
        faces.append([i0+0, i1+1, i0+1])
        faces.append([i0+1, i1+1, i1+2])
        faces.append([i0+1, i1+2, i0+2])
        faces.append([i0+2, i1+2, i1+3])
        faces.append([i0+2, i1+3, i0+3])
        faces.append([i0+3, i1+3, i1+0])
        faces.append([i0+3, i1+0, i0+0])

    faces.append([0, 2, 1])
    faces.append([0, 3, 2])
    faces.append([12, 13, 14])
    faces.append([12, 14, 15])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    mesh.unmerge_vertices()
    return mesh

def build_station_scene():
    scene = trimesh.Scene()

    # =========================================================================
    # MATERIALS DEFINITION (PBR Principled BSDF Standard - RZD Specification)
    # =========================================================================
    # Platform pavement: medium-tone grey asphalt deck
    mat_concrete = PBRMaterial(
        name='Mat_Concrete_Platform',
        baseColorFactor=[0.38, 0.40, 0.43, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.88
    )
    # Platform perimeter border & foundation plinth: dark granite curb (high contrast)
    mat_curb = PBRMaterial(
        name='Mat_Curb_Border',
        baseColorFactor=[0.18, 0.19, 0.21, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.92
    )
    # Warning tactile base tile (recessed groove color - deeper golden ochre)
    mat_tactile_base = PBRMaterial(
        name='Mat_Tactile_Base',
        baseColorFactor=[0.82, 0.60, 0.02, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.88
    )
    # Raised tactile directional ribs (bright traffic yellow with subtle sheen)
    mat_tactile = PBRMaterial(
        name='Mat_Tactile_Yellow',
        baseColorFactor=[0.98, 0.82, 0.02, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.38
    )
    # Structural steel frame & roof fascia: RZD anthracite powder coating (dark matte)
    mat_steel_frame = PBRMaterial(
        name='Mat_Steel_Anthracite',
        baseColorFactor=[0.14, 0.16, 0.18, 1.0],
        metallicFactor=0.05,
        roughnessFactor=0.65
    )
    # Pavilion roof canopy top sheet: medium graphite composite
    mat_roof = PBRMaterial(
        name='Mat_Roof_Canopy',
        baseColorFactor=[0.32, 0.35, 0.38, 1.0],
        metallicFactor=0.08,
        roughnessFactor=0.72
    )
    # Glazing: clear tempered architectural triplex glass
    mat_glass = PBRMaterial(
        name='Mat_Tempered_Glass',
        baseColorFactor=[0.85, 0.92, 0.96, 0.22],
        metallicFactor=0.02,
        roughnessFactor=0.12
    )
    # Wooden bench slats: treated oak / larch with protective semi-matte finish
    mat_wood = PBRMaterial(
        name='Mat_Bench_Wood',
        baseColorFactor=[0.60, 0.36, 0.16, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.75
    )
    # Track ballast: crushed granite gravel (dark grey-brown with brake dust patina)
    mat_ballast = PBRMaterial(
        name='Mat_Track_Ballast',
        baseColorFactor=[0.18, 0.17, 0.16, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.98
    )
    # Sleepers: prestressed reinforced concrete Sh-3 (weathered structural concrete grey)
    mat_sleepers = PBRMaterial(
        name='Mat_Reinforced_Sleepers',
        baseColorFactor=[0.50, 0.52, 0.55, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.92
    )
    # Rail fastenings KB-65: cast iron baseplates & bolts with oil/oxidation patina
    mat_fasteners = PBRMaterial(
        name='Mat_Rail_Fasteners_KB65',
        baseColorFactor=[0.14, 0.13, 0.13, 1.0],
        metallicFactor=0.25,
        roughnessFactor=0.75
    )
    # Rail body (web and foot): natural dark oxidized steel / rust patina
    mat_rail_body = PBRMaterial(
        name='Mat_Rail_Oxidized',
        baseColorFactor=[0.34, 0.23, 0.16, 1.0],
        metallicFactor=0.15,
        roughnessFactor=0.85
    )
    # Rail head: wheel-polished steel running surface (soft metallic sheen, non-specular)
    mat_rails = PBRMaterial(
        name='Mat_Polished_Rails_P65',
        baseColorFactor=[0.68, 0.70, 0.74, 1.0],
        metallicFactor=0.75,
        roughnessFactor=0.38
    )
    # LED schedule display matrix
    mat_led_board = PBRMaterial(
        name='Mat_LED_Display',
        baseColorFactor=[0.96, 0.52, 0.05, 1.0],
        emissiveFactor=[0.90, 0.48, 0.05],
        metallicFactor=0.0,
        roughnessFactor=0.50
    )
    # LED street luminaire fixture
    mat_lamp_luminaire = PBRMaterial(
        name='Mat_LED_Luminaire',
        baseColorFactor=[0.95, 0.98, 1.0, 1.0],
        emissiveFactor=[0.90, 0.95, 1.0],
        metallicFactor=0.0,
        roughnessFactor=0.20
    )
    # Corporate RZD Red: RAL 3020 Traffic Red
    mat_rzd_red = PBRMaterial(
        name='Mat_RZD_Corporate_Red',
        baseColorFactor=[0.86, 0.10, 0.10, 1.0],
        metallicFactor=0.05,
        roughnessFactor=0.60
    )
    # Navigation sign white enamel
    mat_sign_white = PBRMaterial(
        name='Mat_Sign_Enamel_White',
        baseColorFactor=[0.94, 0.94, 0.95, 1.0],
        metallicFactor=0.02,
        roughnessFactor=0.50
    )

    meshes_to_add = []

    # =========================================================================
    # 1. PLATFORM BASE & ACCESS RAMP
    # =========================================================================
    plat_len = 14.0
    plat_wid = 3.4
    plat_h = 0.85
    plat_z_start = 1.0
    plat_z_end = 4.4
    plat_z_center = (plat_z_start + plat_z_end) / 2.0  # 2.7

    curb_wid = 0.20
    curb_front_z = plat_z_start + curb_wid / 2.0  # 1.10
    curb_back_z = plat_z_end - curb_wid / 2.0    # 4.30

    # Front granite curb along track edge (Z in [1.0, 1.20])
    curb_front = create_box(
        extents=[plat_len, plat_h, curb_wid],
        translation=[0.0, plat_h / 2.0, curb_front_z],
        material=mat_curb
    )
    # Rear granite curb border (Z in [4.20, 4.40])
    curb_back = create_box(
        extents=[plat_len, plat_h, curb_wid],
        translation=[0.0, plat_h / 2.0, curb_back_z],
        material=mat_curb
    )
    curb_combined = trimesh.util.concatenate([curb_front, curb_back])
    curb_combined.visual.material = mat_curb
    meshes_to_add.append(('Platform_Curb', curb_combined))

    # Main platform body (asphalt deck between curbs: Z in [1.20, 4.20], width = 3.00m)
    asphalt_wid = plat_wid - 2.0 * curb_wid  # 3.00m
    asphalt_z_center = (plat_z_start + plat_z_end) / 2.0  # 2.70
    platform_mesh = create_box(
        extents=[plat_len, plat_h, asphalt_wid],
        translation=[0.0, plat_h / 2.0, asphalt_z_center],
        material=mat_concrete
    )
    meshes_to_add.append(('Platform_Base', platform_mesh))

    # Warning Tactile Safety Strip (Yellow with deep longitudinal ribbed grooves by GOST R 52875)
    tactile_z = 1.0 + 0.65
    tactile_base = create_box(
        extents=[plat_len, 0.015, 0.36],
        translation=[0.0, plat_h + 0.0075, tactile_z],
        material=mat_tactile_base
    )
    meshes_to_add.append(('Tactile_Safety_Base', tactile_base))

    # 4 pronounced trapezoidal raised ribs with 55° beveled facets for clear 3D grooves and highlights
    rib_meshes = []
    for offset_z in [-0.12, -0.04, 0.04, 0.12]:
        rib = create_trapezoid_rib(length=plat_len, h=0.016, bottom_w=0.048, top_w=0.024)
        rib.apply_translation([0.0, plat_h + 0.015, tactile_z + offset_z])
        rib_meshes.append(rib)
    ribs_mesh = trimesh.util.concatenate(rib_meshes)
    ribs_mesh.visual.material = mat_tactile
    meshes_to_add.append(('Tactile_Ribs', ribs_mesh))

    # Accessible Ramp: Solid watertight triangular prism
    # Slopes from X = -7.0 (Y = 0.85) down to X = -11.0 (Y = 0.0)
    ramp_verts = np.array([
        [-7.0, 0.0, plat_z_start],    # 0: back bottom front-Z
        [-7.0, plat_h, plat_z_start],  # 1: back top front-Z
        [-11.0, 0.0, plat_z_start],   # 2: tip bottom front-Z
        [-7.0, 0.0, plat_z_end],      # 3: back bottom back-Z
        [-7.0, plat_h, plat_z_end],    # 4: back top back-Z
        [-11.0, 0.0, plat_z_end],     # 5: tip bottom back-Z
    ])
    ramp_faces = np.array([
        [0, 2, 1],             # Front Z cap
        [3, 4, 5],             # Back Z cap
        [1, 2, 5], [1, 5, 4],  # Slanted top surface
        [0, 3, 5], [0, 5, 2],  # Bottom base
        [0, 1, 4], [0, 4, 3],  # Vertical face abutting platform
    ])
    ramp_mesh = trimesh.Trimesh(vertices=ramp_verts, faces=ramp_faces, process=True)
    ramp_mesh.unmerge_vertices()
    ramp_mesh.visual.material = mat_concrete
    meshes_to_add.append(('Ramp_Slope', ramp_mesh))

    # Warning tactile warning field before ramp (ТНУ-2 по ГОСТ Р 52875 с точечными рифами)
    ramp_tactile_base = create_box(
        extents=[0.30, 0.012, plat_wid - 0.20],
        translation=[-6.85, plat_h + 0.006, plat_z_center],
        material=mat_tactile_base
    )
    meshes_to_add.append(('Ramp_Tactile_Warning_Base', ramp_tactile_base))

    # Grid of truncated pyramid tactile warning studs on ramp field
    ramp_stud_parts = []
    for sx in np.linspace(-6.95, -6.75, 3):
        for sz in np.linspace(plat_z_start + 0.25, plat_z_end - 0.25, 18):
            st = create_pyramid_stud()
            st.apply_translation([sx, plat_h + 0.012, sz])
            ramp_stud_parts.append(st)
    ramp_studs_mesh = trimesh.util.concatenate(ramp_stud_parts)
    ramp_studs_mesh.visual.material = mat_tactile
    meshes_to_add.append(('Ramp_Tactile_Studs', ramp_studs_mesh))

    # Safety wheel curbs along ramp slope (колесоотбойные бортики по СП 59.13330)
    slope_len = np.sqrt(4.0**2 + plat_h**2)
    slope_angle = np.arctan2(plat_h, 4.0)
    R_slope = trimesh.transformations.rotation_matrix(slope_angle, [0, 0, 1])

    curb_slope_front = trimesh.creation.box([slope_len, 0.06, 0.06])
    curb_slope_front.apply_transform(R_slope)
    curb_slope_front.apply_translation([-9.0, plat_h / 2.0 + 0.03, plat_z_start + 0.03])
    curb_slope_front.unmerge_vertices()

    curb_slope_back = trimesh.creation.box([slope_len, 0.06, 0.06])
    curb_slope_back.apply_transform(R_slope)
    curb_slope_back.apply_translation([-9.0, plat_h / 2.0 + 0.03, plat_z_end - 0.03])
    curb_slope_back.unmerge_vertices()

    ramp_curbs = trimesh.util.concatenate([curb_slope_front, curb_slope_back])
    ramp_curbs.visual.material = mat_curb
    meshes_to_add.append(('Ramp_Safety_Curbs', ramp_curbs))

    # Ramp Handrails (Двойные поручни на высотах 0.7м и 0.9м с вертикальными стойками)
    handrail_parts = []
    for side_z in [plat_z_start + 0.08, plat_z_end - 0.08]:
        # Top continuous rail (height 0.90m above slope)
        rail_top = create_segment_cylinder(
            radius=0.022,
            pt_start=[-7.0, plat_h + 0.90, side_z],
            pt_end=[-11.0, 0.0 + 0.90, side_z],
            sections=16
        )
        # Middle continuous rail (height 0.70m above slope)
        rail_mid = create_segment_cylinder(
            radius=0.020,
            pt_start=[-7.0, plat_h + 0.70, side_z],
            pt_end=[-11.0, 0.0 + 0.70, side_z],
            sections=16
        )
        handrail_parts.extend([rail_top, rail_mid])

        # 5 vertical stanchion posts along slope (post radius 0.018 < rail radius 0.022, ends inside rail tube)
        for rx in np.linspace(-7.0, -11.0, 5):
            curr_y = plat_h * (1.0 - (abs(rx) - 7.0) / 4.0)
            post = create_segment_cylinder(
                radius=0.018,
                pt_start=[rx, curr_y, side_z],
                pt_end=[rx, curr_y + 0.892, side_z],
                sections=16
            )
            handrail_parts.append(post)

    combined_handrails = trimesh.util.concatenate(handrail_parts)
    combined_handrails.visual.material = mat_steel_frame
    meshes_to_add.append(('Ramp_Handrails', combined_handrails))

    # =========================================================================
    # 1.1 PASSENGER STAIRCASE ACCESS (Торцевой лестничный сход по СП 225 / СП 59)
    # =========================================================================
    # Staircase located at opposite end: X from +7.0 to +8.5 m
    # 5 steps: step rise h = 0.17m (170 mm), tread depth d = 0.30m (300 mm)
    # Normative compliance: СП 59.13330.2020 п. 5.1.12, СП 225.1326000.2014 п. 5.3.3.16
    stair_steps = []
    stair_contrast_strips = []
    num_steps = 4  # 4 intermediate stepped blocks leading down to ground
    step_depth = 0.30
    step_rise = plat_h / 5.0  # 0.17 m

    # Tactile warning field on platform before stairs (ТНУ-2 по ГОСТ Р 52875 с точечными рифами)
    stair_tactile_base = create_box(
        extents=[0.50, 0.012, plat_wid - 0.20],
        translation=[6.65, plat_h + 0.006, plat_z_center],
        material=mat_tactile_base
    )
    meshes_to_add.append(('Stairs_Tactile_Warning_Base', stair_tactile_base))

    # Grid of truncated pyramid tactile warning studs on stair field
    stair_stud_parts = []
    for sx in np.linspace(6.45, 6.85, 4):
        for sz in np.linspace(plat_z_start + 0.25, plat_z_end - 0.25, 18):
            st = create_pyramid_stud()
            st.apply_translation([sx, plat_h + 0.012, sz])
            stair_stud_parts.append(st)
    stair_studs_mesh = trimesh.util.concatenate(stair_stud_parts)
    stair_studs_mesh.visual.material = mat_tactile
    meshes_to_add.append(('Stairs_Tactile_Studs', stair_studs_mesh))

    # Steps geometry
    for i in range(num_steps):
        s_x_start = 7.0 + i * step_depth
        s_x_center = s_x_start + step_depth / 2.0
        s_y_top = plat_h - (i + 1) * step_rise
        s_height = s_y_top
        step_box = create_box(
            extents=[step_depth, s_height, plat_wid],
            translation=[s_x_center, s_height / 2.0, plat_z_center],
            material=mat_concrete
        )
        stair_steps.append(step_box)

        # Contrast anti-slip strip on FRONT NOSE of each step (СП 59.13330 п. 5.1.12)
        strip = create_box(
            extents=[0.05, 0.008, plat_wid - 0.10],
            translation=[s_x_start + step_depth - 0.035, s_y_top + 0.004, plat_z_center],
            material=mat_tactile
        )
        stair_contrast_strips.append(strip)

    # Contrast anti-slip strip on top platform departure nose (X = 7.0)
    plat_top_strip = create_box(
        extents=[0.05, 0.008, plat_wid - 0.10],
        translation=[7.0 - 0.035, plat_h + 0.004, plat_z_center],
        material=mat_tactile
    )
    stair_contrast_strips.append(plat_top_strip)

    # Landing pad at base of stairs (Y = 0.04)
    stair_landing = create_box(
        extents=[0.40, 0.04, plat_wid],
        translation=[7.0 + num_steps * step_depth + 0.20, 0.02, plat_z_center],
        material=mat_concrete
    )
    stair_steps.append(stair_landing)

    steps_mesh = trimesh.util.concatenate(stair_steps)
    steps_mesh.visual.material = mat_concrete
    meshes_to_add.append(('Stairs_Steps', steps_mesh))
    strips_mesh = trimesh.util.concatenate(stair_contrast_strips)
    strips_mesh.visual.material = mat_tactile
    meshes_to_add.append(('Stairs_Contrast_Strips', strips_mesh))

    # Dual stainless steel handrails for stairs (высоты 0.7м и 0.9м с выносом 0.3м по СП 59)
    stair_handrail_parts = []
    for side_z in [plat_z_start + 0.08, plat_z_end - 0.08]:
        # Top inclined rail (0.90m above step slope)
        rail_top_slope = create_segment_cylinder(
            radius=0.022,
            pt_start=[7.0, plat_h + 0.90, side_z],
            pt_end=[8.2, step_rise + 0.90, side_z],
            sections=16
        )
        # Top horizontal extension (300 mm at top landing)
        rail_top_ext_hi = create_segment_cylinder(
            radius=0.022,
            pt_start=[6.7, plat_h + 0.90, side_z],
            pt_end=[7.0, plat_h + 0.90, side_z],
            sections=16
        )
        # Bottom horizontal extension (300 mm at bottom landing)
        rail_top_ext_lo = create_segment_cylinder(
            radius=0.022,
            pt_start=[8.2, step_rise + 0.90, side_z],
            pt_end=[8.5, step_rise + 0.90, side_z],
            sections=16
        )

        # Mid rail (0.70m above step slope)
        rail_mid_slope = create_segment_cylinder(
            radius=0.020,
            pt_start=[7.0, plat_h + 0.70, side_z],
            pt_end=[8.2, step_rise + 0.70, side_z],
            sections=16
        )
        rail_mid_ext_hi = create_segment_cylinder(
            radius=0.020,
            pt_start=[6.7, plat_h + 0.70, side_z],
            pt_end=[7.0, plat_h + 0.70, side_z],
            sections=16
        )
        rail_mid_ext_lo = create_segment_cylinder(
            radius=0.020,
            pt_start=[8.2, step_rise + 0.70, side_z],
            pt_end=[8.5, step_rise + 0.70, side_z],
            sections=16
        )

        stair_handrail_parts.extend([
            rail_top_slope, rail_top_ext_hi, rail_top_ext_lo,
            rail_mid_slope, rail_mid_ext_hi, rail_mid_ext_lo
        ])

        # Vertical support posts (стойки - radius 0.018 < rail radius 0.022, ends inside top rail tube)
        post_xs = [6.7, 7.0, 7.4, 7.8, 8.2, 8.5]
        for px in post_xs:
            if px <= 7.0:
                base_y = plat_h
                rail_top_cy = plat_h + 0.90
            elif px >= 8.2:
                base_y = 0.0
                rail_top_cy = step_rise + 0.90
            else:
                base_y = plat_h - (px - 7.0) / 1.2 * (plat_h - step_rise)
                rail_top_cy = base_y + 0.90
            top_y = rail_top_cy - 0.008
            post = create_segment_cylinder(
                radius=0.018,
                pt_start=[px, base_y, side_z],
                pt_end=[px, top_y, side_z],
                sections=16
            )
            stair_handrail_parts.append(post)

    combined_stair_handrails = trimesh.util.concatenate(stair_handrail_parts)
    combined_stair_handrails.visual.material = mat_steel_frame
    meshes_to_add.append(('Stairs_Handrails', combined_stair_handrails))

    # =========================================================================
    # 2. RAILWAY TRACK STRUCTURE (Ballast, Sleepers, Rails P65, Fasteners)
    # =========================================================================
    track_len = 22.0
    ballast_mesh = create_box(
        extents=[track_len, 0.40, 3.4],
        translation=[0.0, 0.20, -0.7],
        material=mat_ballast
    )
    ballast_top = create_box(
        extents=[track_len, 0.08, 2.9],
        translation=[0.0, 0.44, -0.7],
        material=mat_ballast
    )
    ballast_mesh = trimesh.util.concatenate([ballast_mesh, ballast_top])
    ballast_mesh.visual.material = mat_ballast
    meshes_to_add.append(('Track_Ballast', ballast_mesh))

    # Sleepers (Шпалы железобетонные типа Ш-1)
    sleeper_parts = []
    fastener_parts = []
    sleeper_spacing = 0.8
    num_sleepers = int(track_len / sleeper_spacing)
    sleeper_xs = np.linspace(-track_len / 2.0 + 0.5, track_len / 2.0 - 0.5, num_sleepers)

    rail_left_z = -0.7 - 0.76   # -1.46 (Russian 1520 mm gauge)
    rail_right_z = -0.7 + 0.76  # +0.06
    rail_base_y = 0.48 + 0.18   # 0.66 (sleeper top)

    for sx in sleeper_xs:
        sl = create_sh3_sleeper(length=2.7, base_w=0.28, top_w=0.21, h_center=0.18, h_end=0.10, bevel_len=0.22)
        sl.apply_translation([sx, 0.48, -0.7])
        sleeper_parts.append(sl)

        # Baseplates & KB-65 fasteners with vertical bolt caps
        for rz in [rail_left_z, rail_right_z]:
            plate = create_box(extents=[0.28, 0.03, 0.20], translation=[sx, rail_base_y + 0.015, rz])
            b1 = create_segment_cylinder(radius=0.018, pt_start=[sx - 0.08, rail_base_y + 0.03, rz], pt_end=[sx - 0.08, rail_base_y + 0.06, rz], sections=12)
            b2 = create_segment_cylinder(radius=0.018, pt_start=[sx + 0.08, rail_base_y + 0.03, rz], pt_end=[sx + 0.08, rail_base_y + 0.06, rz], sections=12)
            fastener_parts.extend([plate, b1, b2])

    combined_sleepers = trimesh.util.concatenate(sleeper_parts)
    combined_sleepers.visual.material = mat_sleepers
    meshes_to_add.append(('Track_Sleepers', combined_sleepers))

    combined_fasteners = trimesh.util.concatenate(fastener_parts)
    combined_fasteners.visual.material = mat_fasteners
    meshes_to_add.append(('Track_Fasteners_KB65', combined_fasteners))

    # Rails P65: foot + web (oxidized patina), head (polished running surface)
    rail_body_parts = []
    rail_head_parts = []
    for rz in [rail_left_z, rail_right_z]:
        foot = create_box(extents=[track_len, 0.025, 0.15], translation=[0.0, rail_base_y + 0.03 + 0.012, rz])
        web = create_box(extents=[track_len, 0.105, 0.02], translation=[0.0, rail_base_y + 0.03 + 0.025 + 0.052, rz])
        head = create_box(extents=[track_len, 0.045, 0.075], translation=[0.0, rail_base_y + 0.03 + 0.13 + 0.022, rz])
        rail_body_parts.extend([foot, web])
        rail_head_parts.append(head)

    combined_rail_body = trimesh.util.concatenate(rail_body_parts)
    combined_rail_body.visual.material = mat_rail_body
    meshes_to_add.append(('Track_Rails_P65_Body', combined_rail_body))

    combined_rail_heads = trimesh.util.concatenate(rail_head_parts)
    combined_rail_heads.visual.material = mat_rails
    meshes_to_add.append(('Track_Rails_P65_Head', combined_rail_heads))

    # =========================================================================
    # 3. PASSENGER WAITING PAVILION (Steel Frame, Canopy, Glass Walls, Bench)
    # =========================================================================
    pav_len = 5.8
    pav_wid = 1.9
    pav_h = 2.7
    pav_base_y = plat_h
    pav_center_x = 0.0
    pav_center_z = 2.9

    frame_parts = []
    col_xs = [-pav_len/2.0 + 0.2, 0.0, pav_len/2.0 - 0.2]
    col_zs = [pav_center_z - pav_wid/2.0 + 0.15, pav_center_z + pav_wid/2.0 - 0.15]

    # Columns (6 upright steel columns terminating cleanly flush under the horizontal beams)
    col_h = pav_h - 0.12
    for cx in col_xs:
        for cz in col_zs:
            col = create_box(extents=[0.10, col_h, 0.10], translation=[cx, pav_base_y + col_h / 2.0, cz])
            frame_parts.append(col)

    # Perimeter horizontal roof beams
    beam_front = create_box(extents=[pav_len, 0.12, 0.10], translation=[pav_center_x, pav_base_y + pav_h - 0.06, col_zs[0]])
    beam_back = create_box(extents=[pav_len, 0.12, 0.10], translation=[pav_center_x, pav_base_y + pav_h - 0.06, col_zs[1]])
    beam_left = create_box(extents=[0.10, 0.12, pav_wid], translation=[col_xs[0], pav_base_y + pav_h - 0.06, pav_center_z])
    beam_mid = create_box(extents=[0.10, 0.12, pav_wid], translation=[col_xs[1], pav_base_y + pav_h - 0.06, pav_center_z])
    beam_right = create_box(extents=[0.10, 0.12, pav_wid], translation=[col_xs[2], pav_base_y + pav_h - 0.06, pav_center_z])
    frame_parts.extend([beam_front, beam_back, beam_left, beam_mid, beam_right])

    combined_frame = trimesh.util.concatenate(frame_parts)
    combined_frame.visual.material = mat_steel_frame
    meshes_to_add.append(('Pavilion_Steel_Frame', combined_frame))

    # Overhanging Canopy Roof with prominent perimeter fascia border
    roof_w = pav_len + 0.8  # 6.6m
    roof_d = pav_wid + 0.8  # 2.7m
    roof_h = 0.08
    roof_y = pav_base_y + pav_h + 0.06

    # 1. Top roof panel (Mat_Roof_Canopy - medium graphite composite)
    roof_panel = create_box(
        extents=[roof_w, roof_h, roof_d],
        translation=[pav_center_x, roof_y, pav_center_z],
        material=mat_roof
    )
    meshes_to_add.append(('Pavilion_Roof', roof_panel))

    # 2. Perimeter Fascia Trim (Mat_Steel_Anthracite - dark steel cornice framing roof)
    fascia_h = 0.16
    f_thick = 0.04
    # Front fascia (facing tracks - solves arrow in user image 2!)
    f_front = create_box(
        extents=[roof_w + 2 * f_thick, fascia_h, f_thick],
        translation=[pav_center_x, roof_y, pav_center_z - roof_d / 2.0 - f_thick / 2.0],
        material=mat_steel_frame
    )
    # Rear fascia
    f_back = create_box(
        extents=[roof_w + 2 * f_thick, fascia_h, f_thick],
        translation=[pav_center_x, roof_y, pav_center_z + roof_d / 2.0 + f_thick / 2.0],
        material=mat_steel_frame
    )
    # Left and right side fascias
    f_left = create_box(
        extents=[f_thick, fascia_h, roof_d],
        translation=[pav_center_x - roof_w / 2.0 - f_thick / 2.0, roof_y, pav_center_z],
        material=mat_steel_frame
    )
    f_right = create_box(
        extents=[f_thick, fascia_h, roof_d],
        translation=[pav_center_x + roof_w / 2.0 + f_thick / 2.0, roof_y, pav_center_z],
        material=mat_steel_frame
    )
    fascia_mesh = trimesh.util.concatenate([f_front, f_back, f_left, f_right])
    fascia_mesh.visual.material = mat_steel_frame
    meshes_to_add.append(('Pavilion_Roof_Fascia', fascia_mesh))

    # Tempered Glazing Walls (Back wind screen + left/right side screens)
    glass_parts = []
    back_z = col_zs[1]
    g_back1 = create_box(extents=[col_xs[1] - col_xs[0] - 0.12, pav_h - 0.4, 0.018],
                         translation=[(col_xs[0] + col_xs[1]) / 2.0, pav_base_y + (pav_h - 0.4) / 2.0 + 0.2, back_z])
    g_back2 = create_box(extents=[col_xs[2] - col_xs[1] - 0.12, pav_h - 0.4, 0.018],
                         translation=[(col_xs[1] + col_xs[2]) / 2.0, pav_base_y + (pav_h - 0.4) / 2.0 + 0.2, back_z])
    g_left = create_box(extents=[0.018, pav_h - 0.4, col_zs[1] - col_zs[0] - 0.12],
                        translation=[col_xs[0], pav_base_y + (pav_h - 0.4) / 2.0 + 0.2, pav_center_z])
    g_right = create_box(extents=[0.018, pav_h - 0.4, col_zs[1] - col_zs[0] - 0.12],
                         translation=[col_xs[2], pav_base_y + (pav_h - 0.4) / 2.0 + 0.2, pav_center_z])
    glass_parts.extend([g_back1, g_back2, g_left, g_right])

    combined_glass = trimesh.util.concatenate(glass_parts)
    combined_glass.visual.material = mat_glass
    meshes_to_add.append(('Pavilion_Glazing', combined_glass))

    # Waiting Bench (Ergonomic wooden seat + backrest on steel legs)
    bench_len = 3.6
    bench_z = col_zs[1] - 0.42
    bench_wood_parts = []
    bench_steel_parts = []

    # 4 seat wooden slats
    for pi in range(4):
        slat = create_box(extents=[bench_len, 0.03, 0.08],
                          translation=[pav_center_x, pav_base_y + 0.45, bench_z - 0.15 + pi * 0.10])
        bench_wood_parts.append(slat)

    # 2 ergonomic backrest wooden slats (mounted cleanly on the FRONT of the steel backrest struts)
    b_slat1 = create_box(extents=[bench_len, 0.09, 0.028],
                         translation=[pav_center_x, pav_base_y + 0.58, bench_z + 0.165])
    b_slat2 = create_box(extents=[bench_len, 0.09, 0.028],
                         translation=[pav_center_x, pav_base_y + 0.70, bench_z + 0.190])
    bench_wood_parts.extend([b_slat1, b_slat2])

    # Steel support frames: legs, seat beams, rear-supporting backrest struts and integrated armrests
    for lx in [-bench_len / 2.0 + 0.3, 0.0, bench_len / 2.0 - 0.3]:
        # Floor base plate
        leg_base = create_box(extents=[0.08, 0.02, 0.44], translation=[lx, pav_base_y + 0.01, bench_z])
        # Vertical leg to seat
        leg_v = create_box(extents=[0.06, 0.42, 0.06], translation=[lx, pav_base_y + 0.21, bench_z - 0.04])
        # Horizontal seat support rail under slats
        seat_rail = create_box(extents=[0.05, 0.04, 0.40], translation=[lx, pav_base_y + 0.42, bench_z])
        # Backrest upright strut: positioned STRICTLY BEHIND wooden slats (supporting wood from the rear)
        back_strut = create_box(extents=[0.045, 0.38, 0.04], translation=[lx, pav_base_y + 0.61, bench_z + 0.215])
        bench_steel_parts.extend([leg_base, leg_v, seat_rail, back_strut])

    # End armrests on outer legs
    for lx in [-bench_len / 2.0 + 0.3, bench_len / 2.0 - 0.3]:
        arm_post = create_box(extents=[0.035, 0.16, 0.035], translation=[lx, pav_base_y + 0.44 + 0.08, bench_z - 0.16])
        arm_top = create_box(extents=[0.035, 0.035, 0.30], translation=[lx, pav_base_y + 0.44 + 0.16, bench_z - 0.01])
        bench_steel_parts.extend([arm_post, arm_top])

    combined_bench_wood = trimesh.util.concatenate(bench_wood_parts)
    combined_bench_wood.visual.material = mat_wood
    meshes_to_add.append(('Bench_Wood', combined_bench_wood))

    combined_bench_steel = trimesh.util.concatenate(bench_steel_parts)
    combined_bench_steel.visual.material = mat_steel_frame
    meshes_to_add.append(('Bench_Steel', combined_bench_steel))

    # Waste Receptacle (Урна) - Standing upright on platform
    bin_x = pav_len / 2.0 + 0.5
    bin_z = col_zs[1] - 0.3
    bin_body = create_segment_cylinder(
        radius=0.18,
        pt_start=[bin_x, pav_base_y, bin_z],
        pt_end=[bin_x, pav_base_y + 0.72, bin_z],
        sections=20,
        material=mat_steel_frame
    )
    bin_hood = create_segment_cylinder(
        radius=0.20,
        pt_start=[bin_x, pav_base_y + 0.72, bin_z],
        pt_end=[bin_x, pav_base_y + 0.78, bin_z],
        sections=20,
        material=mat_steel_frame
    )
    bin_mesh = trimesh.util.concatenate([bin_body, bin_hood])
    bin_mesh.visual.material = mat_steel_frame
    meshes_to_add.append(('Waste_Bin', bin_mesh))

    # =========================================================================
    # 4. ELECTRONIC LED INFORMATION BOARD (Табло расписания)
    # =========================================================================
    board_w = 2.4
    board_h = 0.50
    board_d = 0.12
    # Mount suspended flush under the front beam (beam bottom is at Y = 3.43)
    board_y = pav_base_y + pav_h - 0.45  # Y = 3.10 (bottom at 2.85m -> 2.00m headroom)
    board_z = col_zs[0]

    # Steel hanger brackets connecting board top (Y=3.35) into front beam (Y=3.43..3.51)
    # Height 0.16m, centered at Y=3.43, top is at Y=3.51 (well below roof ceiling Y=3.57)
    b_mount1 = create_box(extents=[0.05, 0.16, 0.05], translation=[-0.8, 3.43, board_z])
    b_mount2 = create_box(extents=[0.05, 0.16, 0.05], translation=[+0.8, 3.43, board_z])
    board_casing = create_box(extents=[board_w, board_h, board_d], translation=[0.0, board_y, board_z], material=mat_steel_frame)
    led_face = create_box(extents=[board_w - 0.08, board_h - 0.08, 0.01], translation=[0.0, board_y, board_z - board_d/2.0 - 0.005], material=mat_led_board)
    housing_mesh = trimesh.util.concatenate([board_casing, b_mount1, b_mount2])
    housing_mesh.visual.material = mat_steel_frame
    meshes_to_add.append(('Info_Board_Housing', housing_mesh))
    meshes_to_add.append(('Info_Board_Display', led_face))

    # =========================================================================
    # 5. MODERN LED LIGHTING POLE (Светодиодная опора освещения)
    # =========================================================================
    pole_x = 4.8
    pole_z = 3.8
    pole_top_y = plat_h + 4.5  # 5.35m

    # Vertical mast from platform floor to top
    pole_mast = create_segment_cylinder(
        radius=0.07,
        pt_start=[pole_x, plat_h, pole_z],
        pt_end=[pole_x, pole_top_y, pole_z],
        sections=20,
        material=mat_steel_frame
    )
    # Horizontal cantilever boom arm reaching toward platform center (along -Z)
    pole_arm = create_segment_cylinder(
        radius=0.045,
        pt_start=[pole_x, pole_top_y, pole_z],
        pt_end=[pole_x, pole_top_y, pole_z - 1.2],
        sections=16,
        material=mat_steel_frame
    )
    # Luminaire fixture box attached to arm end
    luminaire = create_box(
        extents=[0.24, 0.08, 0.44],
        translation=[pole_x, pole_top_y - 0.06, pole_z - 1.2],
        material=mat_steel_frame
    )
    # Bottom LED lens
    lens = create_box(
        extents=[0.20, 0.015, 0.38],
        translation=[pole_x, pole_top_y - 0.105, pole_z - 1.2],
        material=mat_lamp_luminaire
    )
    pole_mesh = trimesh.util.concatenate([pole_mast, pole_arm, luminaire])
    pole_mesh.visual.material = mat_steel_frame
    meshes_to_add.append(('Lighting_Pole', pole_mesh))
    meshes_to_add.append(('Lighting_Luminaire', lens))

    # =========================================================================
    # 6. PLATFORM REAR GUARDRAILS (Защитное леерное ограждение по СП 59 / СП 225)
    # =========================================================================
    # High-elevation barrier (height 1.10m above platform) along open rear edge (Z = 4.32m)
    # Covers left gap (X from -7.0 to -2.9m) and right gap (X from +2.9 to +7.0m)
    guardrail_parts = []
    guardrail_sections = [
        (-7.0, -2.9, np.linspace(-7.0, -2.9, 5)),
        (2.9, 7.0, np.linspace(2.9, 7.0, 5))
    ]
    for x_start, x_end, post_xs in guardrail_sections:
        # Top handrail at Y = plat_h + 1.10m (1.95m)
        r_top = create_segment_cylinder(
            radius=0.022,
            pt_start=[x_start, plat_h + 1.10, 4.32],
            pt_end=[x_end, plat_h + 1.10, 4.32],
            sections=16
        )
        # Intermediate rail at Y = plat_h + 0.60m (1.45m)
        r_mid = create_segment_cylinder(
            radius=0.018,
            pt_start=[x_start, plat_h + 0.60, 4.32],
            pt_end=[x_end, plat_h + 0.60, 4.32],
            sections=16
        )
        # Lower kick-plate rail at Y = plat_h + 0.15m (1.00m)
        r_bot = create_segment_cylinder(
            radius=0.016,
            pt_start=[x_start, plat_h + 0.15, 4.32],
            pt_end=[x_end, plat_h + 0.15, 4.32],
            sections=16
        )
        guardrail_parts.extend([r_top, r_mid, r_bot])

        # Vertical posts along section (radius 0.018 < top rail radius 0.022, ends inside rail tube)
        for px in post_xs:
            post = create_segment_cylinder(
                radius=0.018,
                pt_start=[px, plat_h, 4.32],
                pt_end=[px, plat_h + 1.10 - 0.008, 4.32],
                sections=16
            )
            guardrail_parts.append(post)

    combined_guardrails = trimesh.util.concatenate(guardrail_parts)
    combined_guardrails.visual.material = mat_steel_frame
    meshes_to_add.append(('Platform_Rear_Guardrails', combined_guardrails))



    # =========================================================================
    # 8. RZD CORPORATE STATION NAME SIGN («о.п. ДВГУПС»)
    # Double-sided sign with flush corporate red block and white name plaque
    # =========================================================================
    sign_posts = []
    for sx in [-5.1, -3.9]:
        sp = create_box(extents=[0.08, 2.6, 0.08], translation=[sx, plat_h + 1.3, 4.15])
        sign_posts.append(sp)

    sign_y = plat_h + 2.05
    sign_frame = create_box(extents=[1.50, 0.50, 0.06], translation=[-4.5, sign_y, 4.15])
    sign_core = create_box(extents=[1.38, 0.38, 0.04], translation=[-4.5, sign_y, 4.15])
    sign_steel = trimesh.util.concatenate(sign_posts + [sign_frame, sign_core])
    sign_steel.visual.material = mat_steel_frame
    meshes_to_add.append(('Station_Sign_Frame', sign_steel))

    # Sign face plates: height strictly 0.38m for both red and white elements (flush fit with 0.06m frame border)
    # Front face (facing tracks / platform at Z = 4.15 - 0.022)
    red_front = create_box(extents=[0.20, 0.38, 0.012], translation=[-5.09, sign_y, 4.15 - 0.022])
    white_front = create_box(extents=[1.16, 0.38, 0.012], translation=[-4.41, sign_y, 4.15 - 0.022])

    # Rear face (facing platform approach at Z = 4.15 + 0.022)
    red_back = create_box(extents=[0.20, 0.38, 0.012], translation=[-3.91, sign_y, 4.15 + 0.022])
    white_back = create_box(extents=[1.16, 0.38, 0.012], translation=[-4.59, sign_y, 4.15 + 0.022])

    sign_red = trimesh.util.concatenate([red_front, red_back])
    sign_red.visual.material = mat_rzd_red
    meshes_to_add.append(('Station_Sign_RZD_Red', sign_red))

    sign_white = trimesh.util.concatenate([white_front, white_back])
    sign_white.visual.material = mat_sign_white
    meshes_to_add.append(('Station_Sign_Plaque', sign_white))

    # =========================================================================
    # 9. RZD EMERGENCY CALL TERMINAL (Колонна экстренной связи «Инфо-SOS»)
    # =========================================================================
    sos_base = create_box(extents=[0.36, 0.04, 0.26], translation=[3.8, plat_h + 0.02, 3.8])
    sos_body = create_box(extents=[0.30, 2.20, 0.20], translation=[3.8, plat_h + 1.10, 3.8])
    sos_intercom = create_box(extents=[0.20, 0.15, 0.02], translation=[3.8, plat_h + 1.70, 3.8 - 0.105])
    sos_steel = trimesh.util.concatenate([sos_base, sos_body, sos_intercom])
    sos_steel.visual.material = mat_steel_frame
    meshes_to_add.append(('SOS_Terminal_Body', sos_steel))

    # Corporate red wrap band on SOS terminal
    sos_red = create_box(extents=[0.305, 0.60, 0.205], translation=[3.8, plat_h + 1.65, 3.8])
    sos_red.visual.material = mat_rzd_red
    meshes_to_add.append(('SOS_Terminal_Red_Band', sos_red))

    # Cylindrical emergency beacon on top of SOS column
    beacon_base = create_segment_cylinder(
        radius=0.065,
        pt_start=[3.8, plat_h + 2.20, 3.8],
        pt_end=[3.8, plat_h + 2.22, 3.8],
        sections=16
    )
    beacon_lens = create_segment_cylinder(
        radius=0.055,
        pt_start=[3.8, plat_h + 2.22, 3.8],
        pt_end=[3.8, plat_h + 2.30, 3.8],
        sections=16
    )
    beacon_mesh = trimesh.util.concatenate([beacon_base, beacon_lens])
    beacon_mesh.visual.material = mat_led_board
    meshes_to_add.append(('SOS_Terminal_Beacon', beacon_mesh))

    # SOS Call push button
    sos_button = create_box(extents=[0.08, 0.08, 0.03], translation=[3.8, plat_h + 1.45, 3.8 - 0.105])
    sos_button.visual.material = mat_tactile
    meshes_to_add.append(('SOS_Terminal_Button', sos_button))

    # =========================================================================
    # ADD ALL GEOMETRIES TO SCENE
    # =========================================================================
    total_triangles = 0
    for name, m in meshes_to_add:
        total_triangles += len(m.faces)
        scene.add_geometry(m, node_name=name)

    print(f'Total meshes: {len(meshes_to_add)}, Triangles: {total_triangles}')
    return scene, total_triangles

def export_and_patch(scene, out_path):
    glb_data = scene.export(file_type='glb', include_normals=True)
    with open(out_path, 'wb') as f:
        f.write(glb_data)

    # Patch glass material in glTF to BLEND mode
    gltf = pygltflib.GLTF2().load(out_path)
    for m in gltf.materials:
        m.doubleSided = True
        if 'Glass' in m.name:
            m.alphaMode = 'BLEND'
            print(f'Patched {m.name} -> alphaMode=BLEND, doubleSided=True')
        else:
            print(f'Patched {m.name} -> doubleSided=True')
    gltf.save(out_path)
    print(f'Successfully exported and patched {out_path}')

if __name__ == '__main__':
    scene, count = build_station_scene()
    SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJ_DIR = os.path.dirname(SCRIPTS_DIR)
    p1 = os.path.join(PROJ_DIR, 'station_pavilion.glb')
    p2 = os.path.join(PROJ_DIR, 'webxr_app', 'models', 'station_pavilion.glb')

    export_and_patch(scene, p1)
    export_and_patch(scene, p2)
