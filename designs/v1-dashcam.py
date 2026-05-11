"""
Pi 5 + AI HAT Dashcam Enclosure -- V1
Dual Camera (Front + Rear) -- Car Mount Design

Designed for: Raspberry Pi 5 + AI HAT+ (Hailo-8L)
Cameras: 2x Raspberry Pi Camera Module v3 (integrated mounts)
GPS: u-blox NEO-6M/7M/8M module (25x25mm standard)
Features: Snap-fit closure, 30mm fan, status LED, power button access
Print material: PETG recommended (heat + vibration resistant)

Rewritten from OpenJSCAD to CadQuery (Python).
Loadable by cadquery-server via show_object().
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Raspberry Pi 5 ---
PI_W = 85.6            # board length
PI_D = 56.5            # board width
PI_PCB_H = 1.6         # PCB thickness
PI_MOUNT_HOLE = 2.7    # M2.5 mounting holes (diameter)

# Pi 5 mounting hole positions (from bottom-left corner of PCB)
PI_HOLES = [
    (3.5, 3.5),
    (61.5, 3.5),
    (3.5, 52.5),
    (61.5, 52.5),
]

# --- AI HAT+ ---
HAT_H = 5.5            # HAT PCB + components height
STACKING_H = 16        # stacking header height between Pi and HAT

# --- Camera Module v3 ---
CAM_W = 25             # camera board width
CAM_D = 24             # camera board depth
CAM_H = 11.5           # camera module total height
LENS_DIA = 8           # lens barrel diameter
LENS_PROTRUSION = 5    # how far the lens sticks out
CAM_MOUNT_HOLE = 2.0   # M2 camera mount screw diameter
CAM_HOLE_SPACING_W = 21    # horizontal hole center-to-center
CAM_HOLE_SPACING_H = 12.5  # vertical hole center-to-center

# --- GPS Module (u-blox NEO standard) ---
GPS_W = 25
GPS_D = 25
GPS_H = 4
GPS_MOUNT_HOLE = 3.0   # M3

# --- 30mm Fan ---
FAN_SIZE = 30
FAN_H = 10
FAN_MOUNT_HOLE = 3.2   # M3
FAN_HOLE_SPACING = 24  # center-to-center distance between mount holes

# --- Case construction ---
WALL = 2.5             # wall thickness (thicker for car vibration)
CORNER_R = 3           # fillet radius on outer edges
TOL = 0.4              # fit tolerance

# Internal stack height:
# standoffs(5) + Pi PCB(1.6) + under-board(3.5) + cooler(15) +
# stacking header(16) + HAT(5.5) + clearance(3)
INTERNAL_H = 50

# Internal cavity dimensions
INT_W = PI_W + TOL * 2
INT_D = PI_D + TOL * 2

# Camera housing that protrudes from case
CAM_HOUSING_W = CAM_W + WALL * 2 + 4   # ~33mm wide
CAM_HOUSING_H = CAM_D + WALL * 2 + 4   # ~32mm tall
CAM_HOUSING_DEPTH = CAM_H + WALL + 4   # ~18mm deep — sticks out from case
CAM_ANGLE = 15         # degrees downward tilt for road view

# External dimensions (main box only — camera housings protrude separately)
EXT_W = INT_W + WALL * 2
EXT_D = INT_D + WALL * 2
EXT_H = INTERNAL_H + WALL * 2
SPLIT_H = EXT_H / 2   # case splits in half horizontally

# --- Snap-fit tabs ---
SNAP_W = 12
SNAP_H = 3
SNAP_DEPTH = 1.5
SNAP_POSITIONS = [-25, 0, 25]  # X positions along each long side

# --- Windshield mount ---
MOUNT_W = 50
MOUNT_D = 35
MOUNT_H = 4
MOUNT_SLOT_W = 30
MOUNT_SLOT_D = 4

# --- Indicators and buttons ---
LED_DIA = 3            # recording LED diameter
PWR_BTN_DIA = 7        # power button hole diameter
STATUS_LED_W = 8       # status LED window width
STATUS_LED_H = 3       # status LED window height

# --- Cable routing ---
CABLE_CHAN_W = 10
CABLE_CHAN_H = 8

# --- microSD ---
SD_SLOT_W = 14
SD_SLOT_H = 3

# --- Ventilation grid parameters ---
VENT_SLOT_W = 2
VENT_SLOT_L = 5
VENT_GAP = 3.5
VENT_ROWS = 6

# --- Quarter-twenty threaded insert ---
QUARTER_TWENTY_DIA = 6.2  # hole for press-fit 1/4-20 insert

# --- Standoff dimensions ---
STANDOFF_H = 5         # height of Pi mounting standoffs
STANDOFF_OUTER_R = 3   # outer radius of standoff posts


# =============================================================================
# HELPER: Ventilation grid as a cuttable solid
# =============================================================================

def make_vent_grid(count_x, count_y, slot_w, slot_l, gap_x, gap_y, depth):
    """
    Create a grid of rectangular slots suitable for boolean subtraction.
    Returns a single CadQuery solid centered at the origin.
    """
    result = None
    start_x = -(count_x * (slot_w + gap_x) - gap_x) / 2
    start_y = -(count_y * (slot_l + gap_y) - gap_y) / 2

    for i in range(count_x):
        for j in range(count_y):
            cx = start_x + i * (slot_w + gap_x) + slot_w / 2
            cy = start_y + j * (slot_l + gap_y) + slot_l / 2
            slot = (
                cq.Workplane("XY")
                .center(cx, cy)
                .box(slot_w, slot_l, depth + 2, centered=True)
            )
            if result is None:
                result = slot
            else:
                result = result.union(slot)
    return result


# =============================================================================
# CAMERA HOUSING (protruding from front/rear face)
# =============================================================================

def build_camera_housing(side="front"):
    """
    Build a protruding camera housing that attaches to the case face.
    The housing tilts 15deg downward and has:
    - Camera module cavity
    - Lens aperture hole
    - M2 screw holes for camera board
    - CSI ribbon cable slot at the base
    """
    # Outer housing block
    housing = (
        cq.Workplane("XY")
        .box(CAM_HOUSING_W, CAM_HOUSING_DEPTH, CAM_HOUSING_H, centered=True)
    )
    # Fillet vertical edges for a cleaner look
    housing = housing.edges("|Z").fillet(2)

    # Camera module cavity (inside the housing)
    cam_cavity = (
        cq.Workplane("XY")
        .box(CAM_W + TOL * 2, CAM_H + TOL, CAM_D + TOL * 2, centered=True)
    )
    housing = housing.cut(cam_cavity)

    # Lens aperture through the outer face
    lens_hole = (
        cq.Workplane("XZ")
        .workplane(offset=CAM_HOUSING_DEPTH / 2)
        .circle(LENS_DIA / 2 + 1.5)
        .extrude(WALL * 2)
    )
    housing = housing.cut(lens_hole)

    # M2 screw holes for camera board mounting (4 corners)
    for dx in [-CAM_HOLE_SPACING_W / 2, CAM_HOLE_SPACING_W / 2]:
        for dz in [-CAM_HOLE_SPACING_H / 2, CAM_HOLE_SPACING_H / 2]:
            m2_hole = (
                cq.Workplane("XZ")
                .center(dx, dz)
                .workplane(offset=-(CAM_HOUSING_DEPTH / 2))
                .circle(CAM_MOUNT_HOLE / 2)
                .extrude(-(CAM_HOUSING_DEPTH))
            )
            housing = housing.cut(m2_hole)

    # CSI ribbon cable slot at the back of the housing
    ribbon_slot = (
        cq.Workplane("XZ")
        .workplane(offset=-(CAM_HOUSING_DEPTH / 2))
        .rect(17, 3)
        .extrude(-(WALL * 2))
    )
    housing = housing.cut(ribbon_slot)

    # --- Position and angle the housing ---
    # Tilt downward by CAM_ANGLE degrees
    housing = housing.rotateAboutCenter((1, 0, 0), -CAM_ANGLE)

    if side == "front":
        # Attach to front face (+Y), centered vertically at mid-height
        housing = housing.translate((
            0,
            EXT_D / 2 + CAM_HOUSING_DEPTH / 2 - 2,  # protrude from front face
            SPLIT_H / 2 - 2   # vertically centered in bottom half
        ))
    else:
        # Rear camera: rotate 180deg around Z then position on -Y face
        housing = housing.rotateAboutCenter((0, 0, 1), 180)
        housing = housing.translate((
            0,
            -(EXT_D / 2 + CAM_HOUSING_DEPTH / 2 - 2),
            SPLIT_H / 2 - 2
        ))

    return housing


# =============================================================================
# BOTTOM HALF
# =============================================================================

def build_bottom_half():
    """
    Bottom half of the snap-fit enclosure.
    Contains: Pi mounting posts, USB-C / microSD / power button / LED cutouts,
    side ventilation, snap-fit ledge rim, and CSI ribbon cable passthrough
    slots in front/rear walls.
    Camera housings are added as separate protruding parts.
    """

    # --- Outer shell (rounded box, bottom half height) ---
    outer = (
        cq.Workplane("XY")
        .box(EXT_W, EXT_D, SPLIT_H, centered=True)
    )
    outer = outer.edges("|Z").fillet(CORNER_R)

    # --- Inner cavity ---
    cavity = (
        cq.Workplane("XY")
        .center(0, 0)
        .workplane(offset=WALL - SPLIT_H / 2)
        .box(INT_W, INT_D, SPLIT_H, centered=[True, True, False])
    )
    bottom = outer.cut(cavity)

    # -------------------------------------------------------------------------
    # CSI RIBBON CABLE PASSTHROUGH (slots in front and rear walls)
    # -------------------------------------------------------------------------

    # Front wall CSI slot
    csi_front = (
        cq.Workplane("XY")
        .center(12, EXT_D / 2)
        .workplane(offset=WALL + 2 - SPLIT_H / 2)
        .box(17, WALL * 3, 3, centered=True)
    )
    bottom = bottom.cut(csi_front)

    # Rear wall CSI slot
    csi_rear = (
        cq.Workplane("XY")
        .center(-12, -(EXT_D / 2))
        .workplane(offset=WALL + 2 - SPLIT_H / 2)
        .box(17, WALL * 3, 3, centered=True)
    )
    bottom = bottom.cut(csi_rear)

    # -------------------------------------------------------------------------
    # PORT CUTOUTS
    # -------------------------------------------------------------------------

    # USB-C power port (left side wall)
    usbc = (
        cq.Workplane("XY")
        .center(-(EXT_W / 2), 15)
        .workplane(offset=WALL + 4 - SPLIT_H / 2)
        .box(WALL * 3, 12, 7, centered=True)
    )
    bottom = bottom.cut(usbc)

    # Cable routing channel
    cable_chan = (
        cq.Workplane("XY")
        .center(-(EXT_W / 2), 15)
        .workplane(offset=WALL + 10 - SPLIT_H / 2)
        .box(WALL * 3, CABLE_CHAN_W, CABLE_CHAN_H, centered=True)
    )
    bottom = bottom.cut(cable_chan)

    # microSD card slot access (right side)
    sd_slot = (
        cq.Workplane("XY")
        .center(EXT_W / 2, -20)
        .workplane(offset=WALL + 2 - SPLIT_H / 2)
        .box(WALL * 3, SD_SLOT_W, SD_SLOT_H, centered=True)
    )
    bottom = bottom.cut(sd_slot)

    # -------------------------------------------------------------------------
    # BUTTON AND LED CUTOUTS
    # -------------------------------------------------------------------------

    # Power button access (rear face)
    pwr_btn = (
        cq.Workplane("XZ")
        .center(35, WALL + 8 - SPLIT_H / 2)
        .workplane(offset=-(EXT_D / 2))
        .circle(PWR_BTN_DIA / 2)
        .extrude(-(WALL * 3))
    )
    bottom = bottom.cut(pwr_btn)

    # Status LED window (rear face)
    status_led = (
        cq.Workplane("XY")
        .center(30, -(EXT_D / 2))
        .workplane(offset=WALL + 4 - SPLIT_H / 2)
        .box(STATUS_LED_W, WALL * 3, STATUS_LED_H, centered=True)
    )
    bottom = bottom.cut(status_led)

    # Recording indicator LED (front face)
    rec_led = (
        cq.Workplane("XZ")
        .center(15, 10 - SPLIT_H / 2)
        .workplane(offset=EXT_D / 2)
        .circle(LED_DIA / 2)
        .extrude(WALL * 3)
    )
    bottom = bottom.cut(rec_led)

    # -------------------------------------------------------------------------
    # SIDE VENTILATION GRIDS
    # -------------------------------------------------------------------------

    vent_grid = make_vent_grid(1, VENT_ROWS, VENT_SLOT_W, VENT_SLOT_L, 0, VENT_GAP, WALL)

    left_vents = vent_grid.translate((-(EXT_W / 2), 0, -2))
    left_vents = left_vents.rotateAboutCenter((0, 1, 0), 90)
    bottom = bottom.cut(left_vents)

    right_vents = vent_grid.translate((EXT_W / 2, 0, -2))
    right_vents = right_vents.rotateAboutCenter((0, 1, 0), 90)
    bottom = bottom.cut(right_vents)

    # -------------------------------------------------------------------------
    # Pi 5 MOUNTING POSTS (5mm standoffs from floor)
    # -------------------------------------------------------------------------

    for hx, hy in PI_HOLES:
        px = hx - INT_W / 2 + TOL
        py = hy - INT_D / 2 + TOL
        pz = -(SPLIT_H / 2) + WALL

        standoff = (
            cq.Workplane("XY")
            .center(px, py)
            .workplane(offset=pz)
            .circle(STANDOFF_OUTER_R)
            .extrude(STANDOFF_H)
        )
        screw_hole = (
            cq.Workplane("XY")
            .center(px, py)
            .workplane(offset=pz - 0.5)
            .circle(PI_MOUNT_HOLE / 2)
            .extrude(STANDOFF_H + 1)
        )
        post = standoff.cut(screw_hole)
        bottom = bottom.union(post)

    # -------------------------------------------------------------------------
    # SNAP-FIT LEDGE (rim for top half to sit on)
    # -------------------------------------------------------------------------

    snap_ledge_outer = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 - 2)
        .box(INT_W + 2, INT_D + 2, 2, centered=[True, True, False])
    )
    snap_ledge_inner = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 - 2.5)
        .box(INT_W - 2, INT_D - 2, 3, centered=[True, True, False])
    )
    snap_ledge = snap_ledge_outer.cut(snap_ledge_inner)
    bottom = bottom.union(snap_ledge)

    # -------------------------------------------------------------------------
    # PROTRUDING CAMERA HOUSINGS (front + rear)
    # -------------------------------------------------------------------------

    front_cam = build_camera_housing("front")
    rear_cam = build_camera_housing("rear")
    bottom = bottom.union(front_cam)
    bottom = bottom.union(rear_cam)

    # Move bottom half so its base sits at Z=0 (build plate)
    bottom = bottom.translate((0, 0, SPLIT_H / 2))

    return bottom


# =============================================================================
# TOP HALF (LID)
# =============================================================================

def build_top_half():
    """
    Top half / lid of the snap-fit enclosure.
    Contains: 30mm fan mount with screw holes, GPS module recess with thinned
    antenna window, snap-fit inner rim + tabs, windshield mount tab with
    adhesive slot, and 1/4-20 threaded insert hole.
    """

    # --- Outer shell ---
    outer = (
        cq.Workplane("XY")
        .box(EXT_W, EXT_D, SPLIT_H, centered=True)
    )
    outer = outer.edges("|Z").fillet(CORNER_R)

    # --- Inner cavity (hollowed from below, leaving WALL on top) ---
    cavity = (
        cq.Workplane("XY")
        .center(0, 0)
        .workplane(offset=SPLIT_H / 2 - WALL)
        .box(INT_W, INT_D, SPLIT_H, centered=[True, True, False])
        .translate((0, 0, -(SPLIT_H)))
    )
    top = outer.cut(cavity)

    # -------------------------------------------------------------------------
    # 30mm FAN MOUNT (centered on top, directly over AI HAT)
    # -------------------------------------------------------------------------

    # Main fan intake hole
    fan_hole = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2)
        .circle(FAN_SIZE / 2 - 2)
        .extrude(-(WALL * 3))
    )
    top = top.cut(fan_hole)

    # Fan M3 screw holes
    for fx in [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2]:
        for fy in [-FAN_HOLE_SPACING / 2, FAN_HOLE_SPACING / 2]:
            screw = (
                cq.Workplane("XY")
                .center(fx, fy)
                .workplane(offset=SPLIT_H / 2)
                .circle(FAN_MOUNT_HOLE / 2)
                .extrude(-(WALL * 3))
            )
            top = top.cut(screw)

    # Fan intake ventilation grid around the fan opening
    fan_vent_grid = make_vent_grid(4, 4, 2, 3, 4, 4, WALL)
    fan_vents = fan_vent_grid.translate((0, 0, SPLIT_H / 2))
    top = top.cut(fan_vents)

    # -------------------------------------------------------------------------
    # GPS MODULE RECESS (top surface, offset from fan)
    # -------------------------------------------------------------------------

    gps_recess = (
        cq.Workplane("XY")
        .center(-(EXT_W / 4), 0)
        .workplane(offset=SPLIT_H / 2 - GPS_H / 2)
        .box(GPS_W + TOL * 2, GPS_D + TOL * 2, GPS_H + 1, centered=True)
    )
    top = top.cut(gps_recess)

    # Thinned antenna window
    gps_window = (
        cq.Workplane("XY")
        .center(-(EXT_W / 4), 0)
        .workplane(offset=SPLIT_H / 2)
        .box(GPS_W - 4, GPS_D - 4, WALL, centered=True)
    )
    top = top.cut(gps_window)

    # GPS M3 mount holes
    for gx in [-(GPS_W / 2 - 2), (GPS_W / 2 - 2)]:
        for gy in [-(GPS_D / 2 - 2), (GPS_D / 2 - 2)]:
            gps_hole = (
                cq.Workplane("XY")
                .center(gx - EXT_W / 4, gy)
                .workplane(offset=SPLIT_H / 2 - GPS_H)
                .circle(GPS_MOUNT_HOLE / 2)
                .extrude(GPS_H + WALL + 2)
            )
            top = top.cut(gps_hole)

    # -------------------------------------------------------------------------
    # SNAP-FIT INNER RIM + TABS
    # -------------------------------------------------------------------------

    snap_rim_outer = (
        cq.Workplane("XY")
        .workplane(offset=-(SPLIT_H / 2) + 1)
        .box(INT_W, INT_D, 2.5, centered=True)
    )
    snap_rim_inner = (
        cq.Workplane("XY")
        .workplane(offset=-(SPLIT_H / 2) + 1)
        .box(INT_W - 3, INT_D - 3, 3.5, centered=True)
    )
    snap_rim = snap_rim_outer.cut(snap_rim_inner)
    top = top.union(snap_rim)

    for xpos in SNAP_POSITIONS:
        tab_front = (
            cq.Workplane("XY")
            .center(xpos, INT_D / 2)
            .workplane(offset=-(SPLIT_H / 2) + 1)
            .box(SNAP_W, SNAP_DEPTH, SNAP_H, centered=True)
        )
        top = top.union(tab_front)

        tab_rear = (
            cq.Workplane("XY")
            .center(xpos, -(INT_D / 2))
            .workplane(offset=-(SPLIT_H / 2) + 1)
            .box(SNAP_W, SNAP_DEPTH, SNAP_H, centered=True)
        )
        top = top.union(tab_rear)

    # -------------------------------------------------------------------------
    # WINDSHIELD MOUNT TAB (on top surface)
    # -------------------------------------------------------------------------

    mount_base = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 - 0.5)
        .box(MOUNT_W, MOUNT_D, MOUNT_H, centered=[True, True, False])
    )
    mount_base = mount_base.edges("|Z").fillet(2)
    top = top.union(mount_base)

    # Adhesive pad / suction cup slot
    mount_slot = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2 + MOUNT_H / 2 - 0.5)
        .box(MOUNT_SLOT_W, MOUNT_SLOT_D, MOUNT_H + 2, centered=True)
    )
    top = top.cut(mount_slot)

    # 1/4-20 threaded insert hole
    quarter_twenty = (
        cq.Workplane("XY")
        .workplane(offset=SPLIT_H / 2)
        .circle(QUARTER_TWENTY_DIA / 2)
        .extrude(-(MOUNT_H + WALL + 2))
    )
    top = top.cut(quarter_twenty)

    # Position top half above bottom for assembly preview
    top = top.translate((0, 0, SPLIT_H + SPLIT_H / 2 + 0.5))

    return top


# =============================================================================
# BUILD AND DISPLAY
# =============================================================================

bottom_half = build_bottom_half()
top_half = build_top_half()

show_object(bottom_half, name="bottom_half", options={"color": (0.15, 0.15, 0.15, 0.9)})
show_object(top_half, name="top_half", options={"color": (0.25, 0.25, 0.25, 0.85)})
